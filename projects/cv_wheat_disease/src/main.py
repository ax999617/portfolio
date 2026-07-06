import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import io
import math
import random
import datetime
from typing import Any, Optional

from qw import mock_patent_inference, PATENT_ID
from inference.model_inference import predict_image
from services.risk_engine import evaluate_risk
from services.response_builder import build_predict_response, build_error_response

API_DESCRIPTION = """
This is a demo MVP for wheat disease recognition and risk warning. It demonstrates the flow of disease recognition, knowledge explanation, risk warning, and decision advice for portfolio and competition presentation.

当前为演示型 MVP，用于展示“病害识别—知识解释—风险预警—决策建议”流程，适合作品集与竞赛答辩展示。

Demo Rule Engine does not perform real AI diagnosis. The output is for auxiliary risk warning only and does not replace laboratory testing or professional agricultural diagnosis.

Demo Rule Engine 不进行真实 AI 诊断，输出仅用于辅助预警，不替代实验室检测或农技诊断。
"""

API_GUIDE_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Wheat Disease API Guide</title>
  <style>
    body { font-family: Arial, "Microsoft YaHei", sans-serif; margin: 0; color: #172033; background: #f7f9fc; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 20px 48px; }
    header { margin-bottom: 24px; }
    h1 { margin: 0 0 8px; font-size: 28px; }
    h2 { margin-top: 28px; font-size: 20px; }
    p, li { line-height: 1.7; }
    button { margin-right: 8px; padding: 8px 14px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; cursor: pointer; }
    button.active { background: #1f6feb; border-color: #1f6feb; color: white; }
    section { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 20px; margin: 14px 0; }
    code { background: #eef2f7; padding: 2px 5px; border-radius: 4px; }
    .lang { display: none; }
    .lang.active { display: block; }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Wheat Disease API — 小麦病害智能识别与预警系统</h1>
      <button id="btn-zh" class="active" onclick="setLang('zh')">中文</button>
      <button id="btn-en" onclick="setLang('en')">English</button>
    </header>

    <div id="zh" class="lang active">
      <section>
        <h2>项目概览</h2>
        <p>这是一个演示型 MVP，用于展示小麦病害识别、知识解释、风险预警与决策建议的闭环流程。</p>
      </section>
      <section>
        <h2>接口列表</h2>
        <ul>
          <li><code>POST /predict</code>：标准化病害识别演示接口。</li>
          <li><code>GET /v1/health</code>：系统状态检查。</li>
          <li><code>POST /v1/analyze</code>：旧版瓦片级分析接口。</li>
          <li><code>POST /v1/upload</code>：旧版上传兼容接口。</li>
          <li><code>POST /v1/report/pdf</code>：PDF 报告生成接口。</li>
        </ul>
      </section>
      <section>
        <h2>Demo 边界</h2>
        <p>当前使用 Demo Rule Engine，不进行真实 AI 诊断。未来真实模型应接入 <code>inference/model_inference.py</code>，并保持 <code>/predict</code> 返回结构不变。</p>
      </section>
      <section>
        <h2>免责声明</h2>
        <p>系统输出仅用于辅助预警和演示展示，不替代实验室检测或专业农技诊断。</p>
      </section>
    </div>

    <div id="en" class="lang">
      <section>
        <h2>Project Overview</h2>
        <p>This is a demo MVP for wheat disease recognition, knowledge explanation, risk warning, and decision advice.</p>
      </section>
      <section>
        <h2>API List</h2>
        <ul>
          <li><code>POST /predict</code>: standardized demo prediction endpoint.</li>
          <li><code>GET /v1/health</code>: system health check.</li>
          <li><code>POST /v1/analyze</code>: legacy tile-level analysis endpoint.</li>
          <li><code>POST /v1/upload</code>: legacy upload compatibility endpoint.</li>
          <li><code>POST /v1/report/pdf</code>: PDF report generation endpoint.</li>
        </ul>
      </section>
      <section>
        <h2>Demo Boundary</h2>
        <p>The current Demo Rule Engine does not perform real AI diagnosis. A future model should be integrated through <code>inference/model_inference.py</code> while keeping the <code>/predict</code> response schema stable.</p>
      </section>
      <section>
        <h2>Disclaimer</h2>
        <p>The output is for auxiliary risk warning and demo presentation only. It does not replace laboratory testing or professional agricultural diagnosis.</p>
      </section>
    </div>
  </main>
  <script>
    function setLang(lang) {
      document.getElementById("zh").classList.toggle("active", lang === "zh");
      document.getElementById("en").classList.toggle("active", lang === "en");
      document.getElementById("btn-zh").classList.toggle("active", lang === "zh");
      document.getElementById("btn-en").classList.toggle("active", lang === "en");
    }
  </script>
</body>
</html>
"""

app = FastAPI(
    title="Wheat Disease API — 小麦病害智能识别与预警系统",
    description=API_DESCRIPTION,
    version="0.1.0-demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static-file mount helper ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _mount(url_path: str, rel_or_abs: str, name: str, html: bool = False) -> None:
    """Mount a StaticFiles directory. Skips if path does not exist."""
    abs_path = (
        rel_or_abs
        if os.path.isabs(rel_or_abs)
        else os.path.abspath(os.path.join(BASE_DIR, rel_or_abs))
    )
    if os.path.exists(abs_path):
        app.mount(url_path, StaticFiles(directory=abs_path, html=html), name=name)
        print(f"[static] {url_path}  →  {abs_path}")
    else:
        print(f"[WARNING] Static mount skipped — path not found: {abs_path}  (url: {url_path})")


def _resolve(rel_or_abs: str) -> str:
    return (
        rel_or_abs
        if os.path.isabs(rel_or_abs)
        else os.path.abspath(os.path.join(BASE_DIR, rel_or_abs))
    )


# ── Static mounts ─────────────────────────────────────────────────────────────
UI_DIST_DIR = _resolve("../前端/openlime-main/dist")
if os.path.exists(UI_DIST_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIST_DIR, html=True), name="ui")
    print(f"[static] /ui  →  {UI_DIST_DIR}")
else:
    print(f"[WARNING] Static mount skipped — path not found: {UI_DIST_DIR}  (url: /ui)")

_ASSET_DIR = "../前端/素材文件"
_mount("/assets",    _ASSET_DIR, "assets_ascii")
_mount("/素材文件",  _ASSET_DIR, "assets_cn")

_CORPUS_DIR = "../语料文件"
_mount("/corpus",    _CORPUS_DIR, "corpus_ascii")
_mount("/语料文件",  _CORPUS_DIR, "corpus_cn")

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
_mount("/outputs", OUTPUT_DIR, "outputs")


@app.get(
    "/ui",
    tags=["Frontend / 前端页面"],
    summary="Open frontend page / 打开前端页面",
    description=(
        "Serves the built frontend entry page when the dist directory is available.\n\n"
        "当 dist 目录存在时，返回已构建的前端入口页面。"
    ),
)
@app.get(
    "/ui/",
    tags=["Frontend / 前端页面"],
    summary="Open frontend page / 打开前端页面",
    description=(
        "Serves the built frontend entry page when the dist directory is available.\n\n"
        "当 dist 目录存在时，返回已构建的前端入口页面。"
    ),
    include_in_schema=False,
)
def ui_index():
    index_path = os.path.join(UI_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"code": 404, "msg": "ui index.html not found"}


@app.get(
    "/api-guide",
    response_class=HTMLResponse,
    tags=["System / 系统状态"],
    summary="API guide / 接口说明页",
    description=(
        "Provides a lightweight bilingual guide for the demo API, boundaries, and disclaimer.\n\n"
        "提供轻量中英文接口说明页，介绍演示 API、Demo 边界与免责声明。"
    ),
)
def api_guide():
    return HTMLResponse(API_GUIDE_HTML)


@app.get("/v1/debug/static")
def debug_static():
    def _probe(rel: str):
        abs_path = os.path.abspath(os.path.join(BASE_DIR, rel))
        exists = os.path.exists(abs_path)
        listing = []
        if exists and os.path.isdir(abs_path):
            try:
                listing = sorted(os.listdir(abs_path))[:40]
            except Exception as e:
                listing = [f"<listdir error: {e}>"]
        return {"path": abs_path, "exists": exists, "entries": listing}

    return {
        "assets":  _probe(_ASSET_DIR),
        "corpus":  _probe(_CORPUS_DIR),
        "ui":      _probe("../前端/openlime-main/dist"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# NEW: /predict — 标准化病害识别 API（P0 核心接口）
# ══════════════════════════════════════════════════════════════════════════════

@app.post(
    "/predict",
    tags=["Prediction / 病害识别"],
    summary="Predict wheat disease / 小麦病害识别",
    description=(
        "Accepts an uploaded wheat image and returns a standardized demo prediction, risk level, knowledge explanation, and decision advice. The current mode is Demo Rule Engine, not real AI diagnosis.\n\n"
        "接收上传的小麦图片，返回标准化演示识别结果、风险等级、知识解释与决策建议。当前模式为 Demo Rule Engine，不进行真实 AI 诊断。"
    ),
)
async def predict(file: UploadFile = File(...)):
    """
    标准化病害识别接口。

    接收小麦叶片图像，返回：
    - 病害分类结果与置信度
    - 风险等级（green/yellow/red）
    - 知识库解释（症状、诱因、防治建议）
    - 产业决策建议（农户、收储、加工）

    当前模式：demo_rule_engine（演示规则引擎）
    """
    if not file or not file.filename:
        return build_error_response("missing_file", "请上传图片文件")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".gif"):
            return build_error_response("invalid_format", "仅支持图片格式（JPG/PNG/BMP/WebP）")

    try:
        image_bytes = await file.read()
    except Exception:
        return build_error_response("read_error", "图片读取失败，请重试")

    if not image_bytes or len(image_bytes) < 100:
        return build_error_response("empty_file", "图片文件为空或过小")

    inference_result = predict_image(image_bytes, file.filename)
    risk_result = evaluate_risk(
        inference_result["class_id"],
        inference_result["confidence"],
    )
    response = build_predict_response(inference_result, risk_result)
    return response


@app.get(
    "/v1/health",
    tags=["System / 系统状态"],
    summary="Health check / 系统健康检查",
    description=(
        "Returns basic service status, patent identifier, and current inference mode for demo verification.\n\n"
        "返回基础服务状态、专利号标识与当前推理模式，用于演示环境检查。"
    ),
)
def health():
    return {"ok": True, "patent": PATENT_ID, "inference_mode": os.environ.get("INFERENCE_MODE", "demo")}


# ══════════════════════════════════════════════════════════════════════════════
# LEGACY: 以下接口保留以兼容前端旧逻辑，标记为 deprecated
# ══════════════════════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    x: int = 0
    y: int = 0
    tile_size: int = 256


def to_json_compatible(value: Any):
    try:
        import numpy as np
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except Exception:
        pass
    if isinstance(value, dict):
        return {str(k): to_json_compatible(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json_compatible(v) for v in value]
    if hasattr(value, "__dict__"):
        return to_json_compatible(vars(value))
    return value


@app.post(
    "/v1/analyze",
    tags=["Legacy Analysis / 旧版分析接口"],
    summary="Legacy tile analysis / 旧版瓦片分析",
    description=(
        "Legacy OpenLIME tile-level analysis endpoint. It returns simulated patent-structure data for compatibility and visualization.\n\n"
        "旧版 OpenLIME 瓦片级分析接口，返回专利结构 stub 的模拟数据，用于兼容与可视化展示。"
    ),
)
def analyze(req: AnalyzeRequest):
    """[Legacy] 瓦片级分析接口，供 OpenLIME 前端调用"""
    result = mock_patent_inference(req.x, req.y, req.tile_size)
    clean_result = jsonable_encoder(to_json_compatible(result))
    return {"code": 0, "data": clean_result}


@app.post("/analyze")
def analyze_compat(req: AnalyzeRequest):
    """[Legacy] 兼容旧路径"""
    result = mock_patent_inference(req.x, req.y, req.tile_size)
    clean_result = jsonable_encoder(to_json_compatible(result))
    return {"code": 0, "data": clean_result}


# ── [Legacy] Demo-mode: filename-keyword → disease script ─────────────────────
# 以下逻辑已被 /predict + demo_rule_engine 替代，保留仅为兼容 /v1/upload 旧调用

_DEMO_SCRIPTS = [
    ("赤霉病", {
        "diseaseName": "小麦赤霉病",
        "confidence": 0.95,
        "toxinRiskLabel": "高关注",
        "gbRiskHint": "疑似存在 DON 风险，建议重点关注 GB 2761-2017 限定值风险。",
        "trendSeries": [48, 62, 74, 86, 92],
        "blurred": False,
    }),
    ("条锈病", {
        "diseaseName": "条锈病",
        "confidence": 0.88,
        "toxinRiskLabel": "中关注",
        "gbRiskHint": "当前以病害风险预警为主，建议结合批次抽检关注 GB 2761-2017 限定值风险。",
        "trendSeries": [22, 30, 45, 58, 51],
        "blurred": False,
    }),
    ("白粉病", {
        "diseaseName": "白粉病",
        "confidence": 0.84,
        "toxinRiskLabel": "中关注",
        "gbRiskHint": "当前以病害风险预警为主，建议结合批次抽检关注 GB 2761-2017 限定值风险。",
        "trendSeries": [18, 24, 36, 43, 47],
        "blurred": False,
    }),
    ("叶锈病", {
        "diseaseName": "小麦叶锈病",
        "confidence": 0.86,
        "toxinRiskLabel": "中关注",
        "gbRiskHint": "当前以病害风险预警为主，建议结合批次抽检关注 GB 2761-2017 限定值风险。",
        "trendSeries": [20, 32, 44, 50, 46],
        "blurred": False,
    }),
    ("健康", {
        "diseaseName": "健康叶片",
        "confidence": 0.91,
        "toxinRiskLabel": "低关注",
        "gbRiskHint": "当前未见明显高风险视觉征象，仍建议维持常规批次抽检。",
        "trendSeries": [10, 12, 15, 13, 12],
        "blurred": False,
    }),
]

_DEFAULT_SCRIPT = {
    "diseaseName": "未识别",
    "confidence": 0.28,
    "toxinRiskLabel": "待评估",
    "gbRiskHint": "样本模糊或无法匹配已知病害特征，建议重新拍摄或补充高质量样本。",
    "trendSeries": [10, 10, 10, 10, 10],
    "blurred": True,
}


def _match_disease_by_filename(filename: str) -> dict:
    """[Deprecated] 被 inference/demo_rule_engine.py 替代"""
    for keyword, script in _DEMO_SCRIPTS:
        if keyword in filename:
            return script
    return _DEFAULT_SCRIPT


def _generate_disease_map(disease_name: str, tile_size: int = 256) -> list:
    step = 16
    nodes = []
    for iy in range(0, tile_size, step):
        for ix in range(0, tile_size, step):
            cx = ix + step // 2
            cy = iy + step // 2
            dist = math.sqrt((cx - tile_size * 0.55) ** 2 + (cy - tile_size * 0.45) ** 2)
            proximity = 1 - min(1, dist / (tile_size * 0.45))
            level = 0
            conf = 0.3 + random.random() * 0.4

            if disease_name == "小麦赤霉病":
                if proximity > 0.5 and random.random() < 0.7:
                    level = 2
                elif proximity > 0.25 and random.random() < 0.5:
                    level = 1
                conf = 0.7 + random.random() * 0.25
            elif disease_name == "条锈病":
                stripe = math.sin(cy / tile_size * math.pi * 6)
                if stripe > 0.3 and random.random() < 0.55:
                    level = 1
                elif stripe > 0.5 and random.random() < 0.3:
                    level = 2
                conf = 0.6 + random.random() * 0.3
            elif disease_name == "小麦叶锈病":
                if random.random() < 0.35 and proximity > 0.25:
                    level = 1
                if random.random() < 0.18 and proximity > 0.35:
                    level = 2
                conf = 0.58 + random.random() * 0.32
            elif disease_name == "白粉病":
                if random.random() < 0.25 and proximity > 0.2:
                    level = 1
                if random.random() < 0.12 and proximity > 0.3:
                    level = 2
                conf = 0.55 + random.random() * 0.35
            else:
                if random.random() < 0.04:
                    level = 1
                conf = 0.3 + random.random() * 0.2

            nodes.append({"x": cx, "y": cy, "level": level, "confidence": round(conf, 3)})
    return nodes


@app.post(
    "/v1/upload",
    tags=["Legacy Upload / 旧版上传接口"],
    summary="Legacy upload demo / 旧版上传演示",
    description=(
        "Legacy upload endpoint kept for frontend fallback. It uses demo filename matching and simulated heatmap data.\n\n"
        "为前端 fallback 保留的旧版上传接口，使用演示文件名匹配与模拟热力图数据。"
    ),
)
async def upload_sample(file: UploadFile = File(...)):
    """[Legacy] 前端旧上传接口，保留兼容"""
    filename = file.filename or ""
    script = _match_disease_by_filename(filename)
    tile_size = 256
    disease_map = _generate_disease_map(script["diseaseName"], tile_size)

    return {
        "code": 0,
        "data": {
            **script,
            "sourceFile": filename,
            "disease_map": disease_map,
            "tile": {"x": 0, "y": 0, "size": tile_size},
        },
    }


# ── PDF Report Generation ─────────────────────────────────────────────────────

SYSTEM_VERSION = "HeTong AI v2.1"


class PDFReportRequest(BaseModel):
    sample_code: str = "WHT-0000"
    time_text: str = ""
    file_name: str = "未命名样本"
    disease_name: str = "未识别"
    confidence: float = 0.0
    risk_level: str = "待识别"
    toxin_risk_label: str = "待评估"
    gb_risk_hint: str = ""
    expert_analysis: str = ""
    prevention: str = ""
    decision_action: str = ""
    storage_advice: str = ""
    processing_advice: str = ""


def _register_cn_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        ("msyh",   "C:/Windows/Fonts/msyh.ttc"),
        ("msyhbd", "C:/Windows/Fonts/msyhbd.ttc"),
        ("simhei", "C:/Windows/Fonts/simhei.ttf"),
        ("simsun", "C:/Windows/Fonts/simsun.ttc"),
    ]
    registered = {}
    for name, path in candidates:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = True
        except Exception:
            pass

    body = "msyh" if "msyh" in registered else ("simhei" if "simhei" in registered else "Helvetica")
    bold = "msyhbd" if "msyhbd" in registered else body
    return body, bold


def _create_pdf(data: PDFReportRequest) -> io.BytesIO:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    cn, cn_b = _register_cn_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            leftMargin=20 * mm, rightMargin=20 * mm)

    sTitle   = ParagraphStyle("T", fontName=cn_b, fontSize=18, leading=26, alignment=TA_CENTER, spaceAfter=2 * mm)
    sSub     = ParagraphStyle("Sub", fontName=cn, fontSize=10, leading=14, alignment=TA_CENTER,
                              textColor=colors.HexColor("#64748b"), spaceAfter=5 * mm)
    sSec     = ParagraphStyle("Sec", fontName=cn_b, fontSize=13, leading=18, spaceBefore=6 * mm,
                              spaceAfter=3 * mm, textColor=colors.HexColor("#1a365d"))
    sBody    = ParagraphStyle("Body", fontName=cn, fontSize=10, leading=16, spaceAfter=2 * mm)
    sBodyB   = ParagraphStyle("BodyB", fontName=cn_b, fontSize=10, leading=16, spaceAfter=2 * mm)
    sDiscl   = ParagraphStyle("Disc", fontName=cn, fontSize=8, leading=12,
                              textColor=colors.HexColor("#666666"), spaceBefore=4 * mm)
    sFoot    = ParagraphStyle("Foot", fontName=cn, fontSize=8, leading=12, alignment=TA_CENTER,
                              textColor=colors.grey)

    LBL = ParagraphStyle("LBL", fontName=cn_b, fontSize=10, leading=15, textColor=colors.HexColor("#475569"))
    VAL = ParagraphStyle("VAL", fontName=cn, fontSize=10, leading=15)

    time_text = data.time_text or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _tbl(rows, lw=38, vw=130):
        t = Table(
            [[Paragraph(r[0], LBL), Paragraph(str(r[1]), VAL)] for r in rows],
            colWidths=[lw * mm, vw * mm],
        )
        t.setStyle(TableStyle([
            ("GRID",       (0, 0), (-1, -1), 0.45, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (0, -1),  colors.HexColor("#f1f5f9")),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        return t

    el = []

    el.append(Paragraph("小麦病害智能识别与预警检测报告", sTitle))
    el.append(Paragraph("WHEAT DISEASE INTELLIGENCE DETECTION REPORT", sSub))
    el.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1")))
    el.append(Spacer(1, 3 * mm))

    el.append(Paragraph("一、基本信息", sSec))
    el.append(_tbl([
        ("报告编号",   data.sample_code),
        ("检测时间",   time_text),
        ("来源文件",   data.file_name),
        ("系统版本",   SYSTEM_VERSION),
        ("专利号",     PATENT_ID),
        ("检测环境",   "标准光照 / 实验室参考条件"),
    ]))

    el.append(Paragraph("二、辅助预警结果", sSec))
    el.append(_tbl([
        ("演示分析结果", data.disease_name),
        ("病害置信度",   f"{data.confidence * 100:.1f}%"),
        ("辅助风险等级", data.risk_level),
        ("疑似 DON 评估", data.toxin_risk_label),
        ("标准风险提示", data.gb_risk_hint or "建议关注 GB 2761-2017 限定值风险"),
        ("处置决策",     data.decision_action or "待生成"),
    ]))

    el.append(Paragraph("三、专家形态学分析", sSec))
    el.append(Paragraph(data.expert_analysis or "暂无足够的形态学证据支持病害判别，请补充高质量样本。", sBody))

    el.append(Paragraph("四、处置建议", sSec))
    el.append(Paragraph("4.1 综合结论", sBodyB))
    el.append(Paragraph(data.prevention or "请继续采样并复核图像质量。", sBody))
    el.append(Paragraph("4.2 收储端建议", sBodyB))
    el.append(Paragraph(data.storage_advice or "收储端建议待补充。", sBody))
    el.append(Paragraph("4.3 加工端建议", sBodyB))
    el.append(Paragraph(data.processing_advice or "加工端建议待补充。", sBody))
    el.append(Paragraph("4.4 物理防治方案", sBodyB))
    el.append(Paragraph(
        "采用强力风选与比重去石协同剔除病斑粒，配合低温烘干将水分控制在 12.5% 以下安全水分标准；"
        "收获前视病情进行适时抢收，减少田间二次侵染损失。", sBody))
    el.append(Paragraph("4.5 化学防治方案", sBodyB))
    el.append(Paragraph(
        "拔节至扬花期喷施戊唑醇、氰烯菌酯或丙硫菌唑等登记杀菌剂，间隔 7-10 天连续施药 2-3 次；"
        "连续阴雨天气适当加密施药间隔，注意药剂轮换以延缓抗药性。", sBody))

    el.append(Paragraph("五、检测依据与法规参考", sSec))
    refs = [
        "GB 2761-2017《食品安全国家标准 食品中真菌毒素限量》——脱氧雪腐镰刀菌烯醇（DON）限量 1000 μg/kg",
        "GB/T 17892-1999《优质小麦 强筋小麦》",
        f"专利 {PATENT_ID} —— 基于区域图卷积网络与大核注意力融合的高光谱作物病害识别方法",
        "NY/T 1464.34-2010《农药田间药效试验准则》",
        "DB 34/T 2285-2015《小麦赤霉病综合防控技术规程》",
    ]
    for ref in refs:
        el.append(Paragraph(f"• {ref}", sBody))

    el.append(Paragraph("六、演示系统参数声明", sSec))
    el.append(_tbl([
        ("模型状态",   f"专利模型结构 stub / 演示规则流程 (Patent {PATENT_ID})"),
        ("预处理说明", "演示用高光谱 SLIC 超像素分割参数说明，当前不代表真实生产推理"),
        ("运行框架",   "PyTorch 结构 stub + FastAPI 演示服务"),
        ("输入规格",   "演示瓦片参数说明，真实模型接入后需重新校准"),
        ("分类类别",   "演示类别说明，当前不替代实验室检测或农技诊断"),
        ("融合策略",   "结构 stub 展示，不表示真实模型已完成训练或验证"),
    ], lw=35, vw=133))

    el.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceBefore=6 * mm))
    el.append(Paragraph(
        "【免责声明】本报告由禾瞳 AI 辅助决策系统自动生成，当前结果为演示/辅助预警结果，仅供参考，不作为法定检测依据。"
        "由于现场光照、样本洁净度等物理因素干扰，演示识别存在一定概率误差，且不替代实验室检测或农技诊断。"
        "对于赤霉病等涉及食品安全的高风险样本，请务必以实验室化学定量检测（GB 5009.111）结果为准，"
        "本系统不承担因误报导致的直接经济损失。", sDiscl))
    el.append(Spacer(1, 4 * mm))
    el.append(Paragraph(
        f"禾瞳科技 (HeTong Tech) · {SYSTEM_VERSION} · 报告生成时间：{time_text}", sFoot))

    doc.build(el)
    buf.seek(0)
    return buf


@app.post(
    "/v1/report/pdf",
    tags=["Report / 报告生成"],
    summary="Generate PDF report / 生成 PDF 报告",
    description=(
        "Generates a PDF report from submitted analysis fields. The report is for demo and auxiliary warning only.\n\n"
        "根据提交的分析字段生成 PDF 报告。报告仅用于演示与辅助预警，不替代实验室检测或农技诊断。"
    ),
)
def generate_pdf_report(req: PDFReportRequest):
    buf = _create_pdf(req)
    safe_code = "".join(c for c in req.sample_code if c.isalnum() or c in "-_")
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="wheat_report_{safe_code}.pdf"',
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
