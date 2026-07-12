"""
pdf_export.py — Generates a resume/portfolio-summary PDF using ReportLab.

ReportLab is pure-Python and pip-installable everywhere (unlike WeasyPrint,
which needs system-level Cairo/Pango libraries), so this keeps deployment
simple while still giving a genuine "Export to PDF" feature.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)

from projects_data import PROJECTS, CATEGORY_LABELS


def build_resume_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
        title="Ravi Der - Resume",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], textColor=colors.HexColor("#0a0a1a"))
    heading_style = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], textColor=colors.HexColor("#7b00ff"),
                                    spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("BodyCustom", parent=styles["BodyText"], leading=15)

    story = []
    story.append(Paragraph("Ravi Der", title_style))
    story.append(Paragraph("AI / Machine Learning &amp; Python Developer", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("About", heading_style))
    story.append(Paragraph(
        "B.Tech in Information Technology, currently pursuing an M.Tech in Artificial "
        "Intelligence, Machine Learning and Data Science. Based in Mandvi, District "
        "Bhavnagar, India. Builder of 20+ AI/ML, data analysis and Python/Django projects, "
        "with 3 completed internships.", body_style))

    story.append(Paragraph("Core Skills", heading_style))
    skills_table_data = [
        ["Backend", "Python, FastAPI, MySQL, REST APIs, JWT Auth"],
        ["AI / ML", "Scikit-Learn, Pandas, NumPy, Matplotlib, Feature Engineering"],
        ["Frontend", "HTML5, CSS3, JavaScript (ES6+), Bootstrap 5"],
        ["DevOps", "Git, GitHub Actions, CLI/Bash, Docker (containerization)"],
    ]
    t = Table(skills_table_data, colWidths=[100, 360])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#00a3ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(t)

    story.append(Paragraph("Selected Projects", heading_style))
    by_category = {}
    for p in PROJECTS:
        by_category.setdefault(p["category"], []).append(p)

    for cat, items in by_category.items():
        story.append(Paragraph(f"<b>{CATEGORY_LABELS.get(cat, cat)}</b>", body_style))
        bullets = [
            ListItem(Paragraph(f"{p['title']} — {', '.join(p['tags'])}", body_style))
            for p in items
        ]
        story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=14))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Contact", heading_style))
    story.append(Paragraph(
        "Full project details, live demos and contact form available at the "
        "portfolio website. GitHub: github.com/derravi", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
