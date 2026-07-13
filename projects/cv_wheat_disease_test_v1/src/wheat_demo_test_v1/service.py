from __future__ import annotations

import hashlib
import io
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image, UnidentifiedImageError


CONTRACT_VERSION = "test-v1"
ALLOWED_CLASS_IDS = (
    "healthy",
    "stripe_rust",
    "leaf_rust",
    "powdery_mildew",
    "fusarium",
)
ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/bmp",
    "image/tiff",
}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
MIN_FILE_SIZE = 100
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024
DEFAULT_MAX_IMAGE_PIXELS = 20_000_000
FORMAT_EXTENSIONS = {
    "PNG": {".png"},
    "JPEG": {".jpg", ".jpeg"},
    "WEBP": {".webp"},
    "BMP": {".bmp"},
    "TIFF": {".tif", ".tiff"},
}
FORMAT_CONTENT_TYPES = {
    "PNG": {"image/png"},
    "JPEG": {"image/jpeg"},
    "WEBP": {"image/webp"},
    "BMP": {"image/bmp"},
    "TIFF": {"image/tiff"},
}
DISCLAIMER = (
    "本结果仅用于演示 API、风险与知识合同，不是真实视觉诊断；"
    "涉及农作物病害或食品安全时，必须由专业人员和实验室检测复核。"
)
DEFAULT_KNOWLEDGE_PATH = (
    Path(__file__).resolve().parents[3]
    / "cv_wheat_disease"
    / "src"
    / "knowledge"
    / "wheat_diseases.json"
)


class InputValidationError(ValueError):
    """Raised before prediction when the uploaded object violates the input contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ModelUnavailableError(RuntimeError):
    """A real provider may raise this when required model resources are unavailable."""


class ProviderExecutionError(RuntimeError):
    """Raised when an injected real provider cannot return a trustworthy result."""


class ProviderContractError(RuntimeError):
    """Raised when a provider returns a result that cannot be trusted."""


@dataclass(frozen=True)
class Prediction:
    class_id: str
    confidence: float
    mode: str


class Predictor(Protocol):
    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        """Return one contract-compliant prediction."""


class DemoPredictor:
    """Deterministic mock provider; it never claims to inspect disease features."""

    _keywords = (
        ("赤霉病", "fusarium"),
        ("赤霉", "fusarium"),
        ("条锈病", "stripe_rust"),
        ("条锈", "stripe_rust"),
        ("叶锈病", "leaf_rust"),
        ("叶锈", "leaf_rust"),
        ("白粉病", "powdery_mildew"),
        ("白粉", "powdery_mildew"),
        ("healthy", "healthy"),
        ("normal", "healthy"),
        ("健康", "healthy"),
        ("fusarium", "fusarium"),
        ("mildew", "powdery_mildew"),
        ("rust", "stripe_rust"),
    )
    _confidence_ranges = {
        "healthy": (0.72, 0.88),
        "stripe_rust": (0.68, 0.86),
        "leaf_rust": (0.68, 0.86),
        "powdery_mildew": (0.68, 0.86),
        "fusarium": (0.72, 0.90),
    }

    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        normalized_name = filename.casefold()
        class_id = next(
            (class_name for keyword, class_name in self._keywords if keyword.casefold() in normalized_name),
            None,
        )
        digest = hashlib.sha256(image_bytes[:4096] + normalized_name.encode("utf-8")).digest()
        if class_id is None:
            class_id = ALLOWED_CLASS_IDS[int.from_bytes(digest[:4], "big") % len(ALLOWED_CLASS_IDS)]
        low, high = self._confidence_ranges[class_id]
        fraction = int.from_bytes(digest[4:8], "big") / 0xFFFFFFFF
        confidence = round(low + (high - low) * fraction, 3)
        return Prediction(class_id=class_id, confidence=confidence, mode="demo_mock")


class PredictionService:
    """Side-effect-free application service with an explicit provider boundary."""

    def __init__(
        self,
        model_predictor: Predictor | None = None,
        *,
        knowledge_path: str | Path = DEFAULT_KNOWLEDGE_PATH,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        max_image_pixels: int = DEFAULT_MAX_IMAGE_PIXELS,
    ) -> None:
        if max_file_size < MIN_FILE_SIZE:
            raise ValueError("max_file_size must be at least MIN_FILE_SIZE")
        if max_image_pixels < 1:
            raise ValueError("max_image_pixels must be positive")
        self.model_predictor = model_predictor
        self.demo_predictor = DemoPredictor()
        self.knowledge_path = Path(knowledge_path)
        self.max_file_size = max_file_size
        self.max_image_pixels = max_image_pixels
        self._knowledge_cache: dict[str, object] | None = None

    def predict(self, image_bytes: bytes, filename: str, content_type: str | None) -> dict[str, object]:
        self.validate_input(image_bytes, filename, content_type)
        fallback_reason: str | None = None

        if self.model_predictor is None:
            prediction = self.demo_predictor.predict(image_bytes, filename)
            fallback_reason = "real_model_not_configured"
        else:
            try:
                prediction = self.model_predictor.predict(image_bytes, filename)
            except ModelUnavailableError as exc:
                raise ProviderExecutionError("real model provider is unavailable") from exc
            except Exception as exc:
                raise ProviderExecutionError("real model provider failed") from exc

        self._validate_prediction(prediction)
        risk = evaluate_risk(prediction.class_id, prediction.confidence, prediction.mode)
        knowledge = self._knowledge_for(prediction.class_id)
        return {
            "success": True,
            "contract_version": CONTRACT_VERSION,
            "mode": prediction.mode,
            "fallback_reason": fallback_reason,
            "prediction": {
                "class_id": prediction.class_id,
                "class_name": knowledge.get("class_name", prediction.class_id),
                "confidence": prediction.confidence,
            },
            "risk": risk,
            "knowledge": {
                "symptoms": knowledge.get("symptoms", []),
                "causes": knowledge.get("causes", []),
                "prevention": knowledge.get("prevention", []),
                "decision_advice": knowledge.get("decision_advice", {}),
            },
            "disclaimer": DISCLAIMER,
        }

    def validate_input(self, image_bytes: bytes, filename: str, content_type: str | None) -> None:
        if not isinstance(image_bytes, bytes):
            raise InputValidationError("invalid_bytes", "image_bytes must be bytes")
        if len(image_bytes) < MIN_FILE_SIZE:
            raise InputValidationError("file_too_small", "图片为空或过小")
        if len(image_bytes) > self.max_file_size:
            raise InputValidationError("file_too_large", "图片超过允许的大小上限")
        if not filename or not filename.strip():
            raise InputValidationError("missing_filename", "缺少文件名")

        extension = Path(filename).suffix.casefold()
        normalized_type = (content_type or "").split(";", 1)[0].strip().casefold()
        if extension not in ALLOWED_EXTENSIONS:
            raise InputValidationError("unsupported_type", "文件扩展名不在支持列表中")
        if normalized_type and normalized_type not in ALLOWED_CONTENT_TYPES:
            raise InputValidationError("unsupported_type", "仅支持常见图片格式")

        detected_format = _verify_image_bytes(image_bytes, self.max_image_pixels)
        if extension not in FORMAT_EXTENSIONS[detected_format]:
            raise InputValidationError("type_mismatch", "文件扩展名与图片实际格式不一致")
        if normalized_type and normalized_type not in FORMAT_CONTENT_TYPES[detected_format]:
            raise InputValidationError("type_mismatch", "MIME 类型与图片实际格式不一致")

    def _validate_prediction(self, prediction: Prediction) -> None:
        if not isinstance(prediction, Prediction):
            raise ProviderContractError("provider must return Prediction")
        if prediction.class_id not in ALLOWED_CLASS_IDS:
            raise ProviderContractError(f"unknown class_id: {prediction.class_id}")
        if not isinstance(prediction.confidence, (int, float)) or isinstance(prediction.confidence, bool):
            raise ProviderContractError("confidence must be numeric")
        if not 0.0 <= float(prediction.confidence) <= 1.0:
            raise ProviderContractError("confidence must be between zero and one")
        if prediction.mode not in {"model", "demo_mock"}:
            raise ProviderContractError(f"unsupported prediction mode: {prediction.mode}")

    def _knowledge_for(self, class_id: str) -> dict[str, object]:
        if self._knowledge_cache is None:
            try:
                raw = json.loads(self.knowledge_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ProviderContractError(f"knowledge source is unavailable: {exc}") from exc
            if not isinstance(raw, dict):
                raise ProviderContractError("knowledge source must be a JSON object")
            self._knowledge_cache = raw
        entry = self._knowledge_cache.get(class_id)
        if not isinstance(entry, dict):
            raise ProviderContractError(f"knowledge is missing for class_id: {class_id}")
        return entry


def _verify_image_bytes(image_bytes: bytes, max_image_pixels: int) -> str:
    """Decode a bounded image and return its normalized container format."""

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(image_bytes)) as image:
                detected_format = (image.format or "").upper()
                if detected_format not in FORMAT_EXTENSIONS:
                    raise InputValidationError("unsupported_type", "图片实际格式不在支持列表中")
                width, height = image.size
                if width < 1 or height < 1:
                    raise InputValidationError("invalid_image", "图片尺寸无效")
                if width * height > max_image_pixels:
                    raise InputValidationError("image_too_large", "图片像素数量超过允许上限")
                image.verify()

            # Pillow documents verify() as a structural check. Reopen and load the
            # pixels so truncated or corrupt compressed payloads also fail.
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.load()
    except InputValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
    ) as exc:
        raise InputValidationError("invalid_image", "文件不是可完整解码的受支持图片") from exc

    return detected_format


def evaluate_risk(class_id: str, confidence: float, mode: str) -> dict[str, str]:
    result_label = "模拟结果" if mode == "demo_mock" else "模型结果"
    if confidence < 0.45:
        return {
            "risk_level": "yellow",
            "risk_label": "低置信度",
            "risk_reason": f"{result_label}置信度较低，建议重新上传并由专业人员复核。",
        }
    if class_id == "healthy" and confidence >= 0.70:
        return {
            "risk_level": "green",
            "risk_label": "低风险演示",
            "risk_reason": f"{result_label}为健康；该结果不构成真实诊断。",
        }
    if class_id == "fusarium" and confidence >= 0.60:
        return {
            "risk_level": "red",
            "risk_label": "高关注演示",
            "risk_reason": f"{result_label}进入高关注分支，必须由专业人员和实验室检测复核。",
        }
    return {
        "risk_level": "yellow",
        "risk_label": "需复核演示",
        "risk_reason": f"{result_label}进入复核分支，不可直接用于农业或食品安全决策。",
    }
