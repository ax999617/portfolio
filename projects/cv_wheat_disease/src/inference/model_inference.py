"""
Model Inference — 真实模型推理入口（未来由 Codex 实现）

当前状态：未接入真实模型权重，所有调用安全降级到 demo_rule_engine。

后续接入步骤：
1. 准备训练好的 EfficientNet-B0 / MobileNet-V2 权重文件 (.pth)
2. 在本模块中加载模型、实现图像预处理和推理
3. 将 INFERENCE_MODE 设为 "model" 即可启用
4. /predict API 返回结构保持不变，前端无需改动
"""

import os
from inference.demo_rule_engine import predict_image_demo


def _try_real_model_inference(image_bytes: bytes, filename: str | None = None) -> dict | None:
    """
    尝试使用真实模型进行推理。

    当前未实现——返回 None 表示模型不可用，触发 fallback。
    后续 Codex 在此处实现：
      - 加载 .pth 权重
      - 图像预处理（resize, normalize）
      - 模型前向推理
      - 返回 {"class_id": ..., "confidence": ..., "mode": "model"}
    """
    return None


def predict_image(image_bytes: bytes, filename: str | None = None) -> dict:
    """
    统一推理入口。

    根据 INFERENCE_MODE 环境变量决定调用路径：
    - "model": 尝试真实模型，失败则 fallback
    - "demo" (默认): 直接使用演示规则引擎

    Args:
        image_bytes: 图片二进制数据
        filename: 可选的原始文件名

    Returns:
        dict with keys: class_id, confidence, mode
    """
    mode = os.environ.get("INFERENCE_MODE", "demo").strip().lower()
    if mode == "model":
        result = _try_real_model_inference(image_bytes, filename)
        if result is not None:
            return result

    return predict_image_demo(image_bytes, filename)
