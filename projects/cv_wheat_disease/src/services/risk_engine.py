"""
Risk Engine — 三级风险预警引擎

根据病害类别 (class_id) 和置信度 (confidence) 输出 green/yellow/red 风险等级。
风险规则来源于项目交接文档，对接"病害识别—知识解释—风险预警—产业决策"四层闭环。
"""


def evaluate_risk(class_id: str, confidence: float) -> dict:
    """
    根据分类结果和置信度评估风险等级。

    规则优先级（从高到低）：
    1. 任何类别 confidence < 0.45 → yellow（低置信度拦截）
    2. healthy 且 confidence >= 0.70 → green
    3. fusarium 且 confidence >= 0.60 → red
    4. 其他病害 且 confidence >= 0.60 → yellow
    5. 病害 confidence < 0.60 → yellow（结果不确定）

    Returns:
        dict with keys: risk_level, risk_label, risk_reason, confidence_band
    """
    confidence_band = _get_confidence_band(confidence)

    if confidence < 0.45:
        return {
            "risk_level": "yellow",
            "risk_label": "低置信度",
            "risk_reason": "识别置信度过低，无法形成稳定结论，建议重新上传清晰图片或人工复核。",
            "confidence_band": confidence_band,
        }

    if class_id == "healthy" and confidence >= 0.70:
        return {
            "risk_level": "green",
            "risk_label": "低风险",
            "risk_reason": "识别结果为健康叶片，未见明显病害特征，建议常规监测与正常收储。",
            "confidence_band": confidence_band,
        }

    if class_id == "healthy" and confidence < 0.70:
        return {
            "risk_level": "yellow",
            "risk_label": "待确认",
            "risk_reason": "健康判定置信度偏低，建议补充采样或人工复核确认。",
            "confidence_band": confidence_band,
        }

    if class_id == "fusarium" and confidence >= 0.60:
        return {
            "risk_level": "red",
            "risk_label": "高风险",
            "risk_reason": "识别结果疑似小麦赤霉病，存在潜在 DON 毒素风险，建议重点检测并关注 GB 2761-2017 限定值，不建议未经检测直接进入加工流程。",
            "confidence_band": confidence_band,
        }

    if class_id in ("stripe_rust", "leaf_rust", "powdery_mildew") and confidence >= 0.60:
        return {
            "risk_level": "yellow",
            "risk_label": "中风险",
            "risk_reason": "识别结果显示存在病害特征，可能影响产量和品质，建议加强田间防治、分级收获或抽样复检。",
            "confidence_band": confidence_band,
        }

    if confidence < 0.60:
        return {
            "risk_level": "yellow",
            "risk_label": "结果不确定",
            "risk_reason": "识别置信度不足，结果可能不准确，建议重新拍摄清晰图片或人工复核。",
            "confidence_band": confidence_band,
        }

    return {
        "risk_level": "yellow",
        "risk_label": "待评估",
        "risk_reason": "未匹配到明确风险规则，建议人工复核。",
        "confidence_band": confidence_band,
    }


def _get_confidence_band(confidence: float) -> str:
    """将置信度映射为语义分段"""
    if confidence >= 0.85:
        return "high"
    if confidence >= 0.60:
        return "medium"
    if confidence >= 0.45:
        return "low"
    return "very_low"
