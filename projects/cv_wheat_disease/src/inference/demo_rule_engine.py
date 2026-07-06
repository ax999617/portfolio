"""
Demo Rule Engine — 演示规则引擎

当前系统处于 MVP 演示阶段，使用文件名关键词匹配或随机选择来模拟病害分类。
本模块不进行任何真实图像识别，仅用于系统流程验证和前端联调。

后续由 Codex 接入 EfficientNet-B0 / MobileNet-V2 真实模型后，
本模块将被 model_inference.py 替代，但保留作为 fallback。
"""

import random
import hashlib

VALID_CLASSES = ["healthy", "stripe_rust", "leaf_rust", "powdery_mildew", "fusarium"]

_FILENAME_KEYWORDS = [
    ("赤霉", "fusarium"),
    ("赤霉病", "fusarium"),
    ("条锈", "stripe_rust"),
    ("条锈病", "stripe_rust"),
    ("叶锈", "leaf_rust"),
    ("叶锈病", "leaf_rust"),
    ("白粉", "powdery_mildew"),
    ("白粉病", "powdery_mildew"),
    ("健康", "healthy"),
    ("normal", "healthy"),
    ("healthy", "healthy"),
    ("rust", "stripe_rust"),
    ("mildew", "powdery_mildew"),
    ("fusarium", "fusarium"),
    ("scab", "fusarium"),
]

_CONFIDENCE_RANGES = {
    "healthy": (0.82, 0.95),
    "stripe_rust": (0.78, 0.93),
    "leaf_rust": (0.75, 0.91),
    "powdery_mildew": (0.76, 0.92),
    "fusarium": (0.85, 0.97),
}


def _match_by_filename(filename: str) -> str | None:
    """尝试从文件名中提取病害关键词进行匹配"""
    if not filename:
        return None
    lower = filename.lower()
    for keyword, class_id in _FILENAME_KEYWORDS:
        if keyword in filename or keyword in lower:
            return class_id
    return None


def _stable_random_class(image_bytes: bytes) -> str:
    """基于图片内容哈希的稳定随机分类（同一张图片总是返回相同结果）"""
    if image_bytes:
        digest = hashlib.md5(image_bytes[:4096]).hexdigest()
        index = int(digest[:8], 16) % len(VALID_CLASSES)
        return VALID_CLASSES[index]
    return random.choice(VALID_CLASSES)


def _generate_confidence(class_id: str, seed_bytes: bytes | None = None) -> float:
    """生成该类别对应范围内的置信度"""
    lo, hi = _CONFIDENCE_RANGES.get(class_id, (0.70, 0.90))
    if seed_bytes:
        digest = hashlib.md5(seed_bytes[:4096]).hexdigest()
        frac = int(digest[8:16], 16) / 0xFFFFFFFF
        return round(lo + frac * (hi - lo), 3)
    return round(random.uniform(lo, hi), 3)


def predict_image_demo(image_bytes: bytes, filename: str | None = None) -> dict:
    """
    演示规则引擎入口。

    Args:
        image_bytes: 图片二进制数据（当前 demo 模式下不做真实图像分析）
        filename: 可选的原始文件名，用于关键词匹配

    Returns:
        dict with keys: class_id, confidence, mode
    """
    class_id = None

    if filename:
        class_id = _match_by_filename(filename)

    if class_id is None:
        class_id = _stable_random_class(image_bytes)

    confidence = _generate_confidence(class_id, image_bytes)

    return {
        "class_id": class_id,
        "confidence": confidence,
        "mode": "demo_rule_engine",
    }
