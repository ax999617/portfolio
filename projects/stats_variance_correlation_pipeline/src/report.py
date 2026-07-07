from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _paragraph(text: str, style_name: str = "BodyText"):
    styles = getSampleStyleSheet()
    return Paragraph(text, styles[style_name])


def _asset_rows(package_summary: dict[str, object]) -> list[list[str]]:
    rows = [["Asset", "Type", "Role", "Output"]]
    for asset in package_summary["outputs"]:
        rows.append(
            [
                str(asset["asset_id"]),
                str(asset["asset_type"]),
                str(asset["role"]),
                Path(str(asset["output_original"])).name,
            ]
        )
    return rows


def build_package_report(
    output_pdf: Path,
    package_summary: dict[str, object],
    optional_analysis: dict[str, object] | None = None,
) -> Path:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=landscape(A4),
        leftMargin=0.45 * inch,
        rightMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Stats Variance Correlation Pipeline", styles["Title"]),
        Spacer(1, 0.12 * inch),
        _paragraph("Source-derived statistical asset package. Frozen historical results are preserved; ANOVA, CLD, and source data are not recomputed."),
        Spacer(1, 0.16 * inch),
        _paragraph("Full local source paths are preserved in source_asset_inventory.md and asset_package_summary.json."),
        Spacer(1, 0.12 * inch),
    ]

    table = Table(_asset_rows(package_summary), hAlign="LEFT", colWidths=[1.8 * inch, 0.9 * inch, 2.1 * inch, 2.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9edf3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.extend([table, Spacer(1, 0.18 * inch)])

    if optional_analysis:
        story.extend(
            [
                _paragraph("Optional analysis output was generated for a new user-supplied table.", "Heading2"),
                _paragraph(", ".join(str(path) for path in optional_analysis.get("outputs", []))),
                Spacer(1, 0.14 * inch),
            ]
        )

    preview_paths = [
        Path(str(asset["output_preview"]))
        for asset in package_summary["outputs"]
        if asset.get("output_preview")
    ]
    for preview in preview_paths:
        if not preview.exists():
            continue
        story.append(_paragraph(preview.name, "Heading2"))
        image = Image(str(preview))
        max_width = 9.7 * inch
        max_height = 5.0 * inch
        scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
        image.drawWidth = image.imageWidth * scale
        image.drawHeight = image.imageHeight * scale
        story.extend([image, Spacer(1, 0.16 * inch)])

    doc.build(story)
    return output_pdf
