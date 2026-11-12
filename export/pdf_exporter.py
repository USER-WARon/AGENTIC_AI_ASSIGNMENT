"""Create clean, text-selectable PDFs for PaperPilot written outputs."""
from html import escape
from io import BytesIO
import os
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

NAVY = colors.HexColor("#13233E")
BLUE = colors.HexColor("#2B67C2")
TEAL = colors.HexColor("#23ABA5")
INK = colors.HexColor("#263243")
MUTED = colors.HexColor("#697789")
_FONT_READY = False


def _register_font():
    global _FONT_READY
    if _FONT_READY:
        return
    candidates = [
        ("PaperPilot", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        ("PaperPilot", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for name, regular, bold in candidates:
        if os.path.exists(regular):
            pdfmetrics.registerFont(TTFont(name, regular))
            if os.path.exists(bold):
                pdfmetrics.registerFont(TTFont(name + "-Bold", bold))
                pdfmetrics.registerFontFamily(name, normal=name, bold=name + "-Bold", italic=name, boldItalic=name + "-Bold")
            _FONT_READY = True
            return


def create_text_pdf(title: str, content: str, paper_name: str = "Research Paper") -> bytes:
    """Render simple Markdown as a selectable, styled PDF with page footer."""
    _register_font()
    font = "PaperPilot" if _FONT_READY else "Helvetica"
    bold_font = "PaperPilot-Bold" if _FONT_READY else "Helvetica-Bold"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PPTitle", parent=styles["Title"], fontName=bold_font, fontSize=22, leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8))
    styles.add(ParagraphStyle(name="PPH2", parent=styles["Heading2"], fontName=bold_font, fontSize=14, leading=18, textColor=BLUE, spaceBefore=13, spaceAfter=5, keepWithNext=True))
    styles.add(ParagraphStyle(name="PPH3", parent=styles["Heading3"], fontName=bold_font, fontSize=11, leading=15, textColor=NAVY, spaceBefore=9, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="PPBody", parent=styles["BodyText"], fontName=font, fontSize=10, leading=15, textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(name="PPBullet", parent=styles["BodyText"], fontName=font, fontSize=10, leading=14, textColor=INK, leftIndent=16, firstLineIndent=-10, spaceAfter=4))
    styles.add(ParagraphStyle(name="PPMeta", parent=styles["BodyText"], fontName=font, fontSize=9, leading=12, textColor=MUTED, spaceAfter=10))
    story = [Paragraph(escape(title), styles["PPTitle"]), Paragraph(escape(paper_name), styles["PPMeta"]), HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=12)]
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 3)); continue
        if line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), styles["PPH3"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), styles["PPH2"]))
        elif line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["PPH2"]))
        elif re.match(r"^[-*]\s+", line):
            body = escape(re.sub(r"^[-*]\s+", "", line))
            story.append(Paragraph("• " + body, styles["PPBullet"]))
        elif re.match(r"^\d+[.)]\s+", line):
            body = escape(line)
            story.append(Paragraph(body, styles["PPBullet"]))
        else:
            body = escape(line).replace("**", "")
            story.append(Paragraph(body, styles["PPBody"]))
    output = BytesIO()
    def page_decor(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E2E9F2")); canvas.line(.65 * inch, .55 * inch, 7.85 * inch, .55 * inch)
        canvas.setFont(font, 8); canvas.setFillColor(MUTED)
        canvas.drawString(.65 * inch, .36 * inch, "PaperPilot AI  |  Source-grounded study notes")
        canvas.drawRightString(7.85 * inch, .36 * inch, f"{doc.page}")
        canvas.restoreState()
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=.68*inch, leftMargin=.68*inch, topMargin=.65*inch, bottomMargin=.75*inch, title=title, author="PaperPilot AI")
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    return output.getvalue()
