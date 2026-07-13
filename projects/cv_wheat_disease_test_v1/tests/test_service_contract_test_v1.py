from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wheat_demo_test_v1.service import (  # noqa: E402
    InputValidationError,
    ModelUnavailableError,
    Prediction,
    PredictionService,
    ProviderContractError,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"test-v1" * 20


class StaticModel:
    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        return Prediction("fusarium", 0.91, "model")


class UnavailableModel:
    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        raise ModelUnavailableError("weights are not configured")


class BrokenModel:
    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        raise RuntimeError("provider crashed")


class InvalidContractModel:
    def predict(self, image_bytes: bytes, filename: str) -> Prediction:
        return Prediction("unknown_class", 1.2, "model")


class ServiceContractTests(unittest.TestCase):
    def test_demo_is_deterministic_and_explicit(self) -> None:
        service = PredictionService()
        first = service.predict(PNG_BYTES, "sample.png", "image/png")
        second = service.predict(PNG_BYTES, "sample.png", "image/png")
        self.assertEqual(first, second)
        self.assertEqual(first["mode"], "demo_mock")
        self.assertEqual(first["fallback_reason"], "real_model_not_configured")

    def test_filename_keyword_is_only_a_mock_selector(self) -> None:
        result = PredictionService().predict(PNG_BYTES, "健康_sample.png", "image/png")
        self.assertEqual(result["prediction"]["class_id"], "healthy")
        self.assertEqual(result["risk"]["risk_level"], "green")
        self.assertIn("不是真实视觉诊断", result["disclaimer"])

    def test_empty_or_too_small_input_fails_before_provider(self) -> None:
        with self.assertRaises(InputValidationError) as context:
            PredictionService().predict(b"", "empty.png", "image/png")
        self.assertEqual(context.exception.code, "file_too_small")

    def test_invalid_signature_is_rejected(self) -> None:
        with self.assertRaises(InputValidationError) as context:
            PredictionService().predict(b"not-an-image" * 20, "fake.png", "image/png")
        self.assertEqual(context.exception.code, "invalid_signature")

    def test_size_limit_is_enforced(self) -> None:
        service = PredictionService(max_file_size=120)
        with self.assertRaises(InputValidationError) as context:
            service.predict(PNG_BYTES, "large.png", "image/png")
        self.assertEqual(context.exception.code, "file_too_large")

    def test_real_provider_result_is_used_when_valid(self) -> None:
        result = PredictionService(model_predictor=StaticModel()).predict(
            PNG_BYTES, "sample.png", "image/png"
        )
        self.assertEqual(result["mode"], "model")
        self.assertIsNone(result["fallback_reason"])
        self.assertEqual(result["risk"]["risk_level"], "red")

    def test_unavailable_provider_falls_back_with_reason(self) -> None:
        result = PredictionService(model_predictor=UnavailableModel()).predict(
            PNG_BYTES, "sample.png", "image/png"
        )
        self.assertEqual(result["mode"], "demo_mock")
        self.assertEqual(result["fallback_reason"], "real_model_unavailable")

    def test_unexpected_provider_failure_is_visible(self) -> None:
        result = PredictionService(model_predictor=BrokenModel()).predict(
            PNG_BYTES, "sample.png", "image/png"
        )
        self.assertEqual(result["mode"], "demo_mock")
        self.assertEqual(result["fallback_reason"], "real_model_failed")

    def test_invalid_provider_contract_fails_closed(self) -> None:
        with self.assertRaises(ProviderContractError):
            PredictionService(model_predictor=InvalidContractModel()).predict(
                PNG_BYTES, "sample.png", "image/png"
            )


if __name__ == "__main__":
    unittest.main()
