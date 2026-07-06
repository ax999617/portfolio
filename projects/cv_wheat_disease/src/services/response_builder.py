"""
Response Builder — 统一 JSON 响应构建器

将推理结果、风险评估、知识库信息合并为前端可直接消费的标准 JSON。
所有 /predict 响应均通过本模块组装，保证字段一致性和免责声明。
"""

import json
import os

_KNOWLEDGE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "knowledge", "wheat_diseases.json"
)

_knowledge_cache: dict | None = None

DISCLAIMER = (
    "本系统结果仅用于源头风险预警和辅助决策，不替代实验室检测或专业农技诊断。"
    "由于现场光照、样本洁净度等物理因素干扰，AI 识别存在一定概率误差。"
    "对于涉及食品安全的高风险样本，请务必以实验室化学定量检测结果为准。"
)


def _load_knowledge() -> dict:
    global _knowledge_cache
    if _knowledge_cache is not None:
        return _knowledge_cache
    abs_path = os.path.normpath(_KNOWLEDGE_PATH)
    with open(abs_path, "r", encoding="utf-8") as f:
        _knowledge_cache = json.load(f)
    return _knowledge_cache


def _get_disease_knowledge(class_id: str) -> dict:
    """从知识库获取指定病害的详细信息"""
    kb = _load_knowledge()
    entry = kb.get(class_id, {})
    return {
        "symptoms": entry.get("symptoms", []),
        "causes": entry.get("causes", []),
        "confusable": entry.get("confusable", []),
        "prevention": entry.get("prevention", []),
        "industry_note": entry.get("industry_note", ""),
        "decision_advice": entry.get("decision_advice", {
            "farmer": "",
            "storage": "",
            "processing": "",
        }),
        "expert_analysis": entry.get("expert_analysis", ""),
    }


def build_predict_response(
    inference_result: dict,
    risk_result: dict,
) -> dict:
    """
    构建统一的 /predict 响应。

    Args:
        inference_result: 来自 demo_rule_engine 或 model_inference 的结果
            {"class_id": str, "confidence": float, "mode": str}
        risk_result: 来自 risk_engine.evaluate_risk 的结果
            {"risk_level": str, "risk_label": str, "risk_reason": str, "confidence_band": str}

    Returns:
        完整的 JSON 可序列化 dict
    """
    class_id = inference_result.get("class_id", "healthy")
    confidence = inference_result.get("confidence", 0.0)
    mode = inference_result.get("mode", "demo_rule_engine")

    kb = _load_knowledge()
    entry = kb.get(class_id, {})
    class_name = entry.get("class_name", class_id)

    knowledge = _get_disease_knowledge(class_id)

    return {
        "success": True,
        "mode": mode,
        "prediction": {
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence,
        },
        "risk": {
            "risk_level": risk_result.get("risk_level", "yellow"),
            "risk_label": risk_result.get("risk_label", "待评估"),
            "risk_reason": risk_result.get("risk_reason", ""),
            "confidence_band": risk_result.get("confidence_band", "medium"),
        },
        "knowledge": knowledge,
        "disclaimer": DISCLAIMER,
    }


def build_error_response(error_type: str, message: str) -> dict:
    """构建错误响应"""
    return {
        "success": False,
        "mode": "error",
        "error": {
            "type": error_type,
            "message": message,
        },
        "disclaimer": DISCLAIMER,
    }
