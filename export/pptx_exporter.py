"""Turn slide JSON into a polished, readable academic PowerPoint."""
import json
import re
from io import BytesIO
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

NAVY = RGBColor(19, 35, 62)
BLUE = RGBColor(43, 103, 194)
TEAL = RGBColor(35, 171, 165)
INK = RGBColor(38, 50, 67)
MUTED = RGBColor(105, 119, 137)
PALE = RGBColor(242, 246, 251)
WHITE = RGBColor(255, 255, 255)


def parse_slides(content: str) -> list[dict]:
    """Parse common LLM JSON shapes, including fenced or surrounding prose."""
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        a, b = text.find("["), text.rfind("]")
        if a >= 0 and b > a:
            try: data = json.loads(text[a:b + 1])
            except json.JSONDecodeError: pass
        elif start >= 0 and end > start:
            try: data = json.loads(text[start:end + 1])
            except json.JSONDecodeError: pass
    if isinstance(data, dict):
        data = data.get("slides", data.get("presentation", []))
    if not isinstance(data, list):
        raise ValueError("The slide response was not a slide list. Please regenerate it.")
    slides = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "Key points").strip()
        raw = item.get("bullets", item.get("content", item.get("points", [])))
        if isinstance(raw, str): raw = [line.strip(" •-*\t") for line in raw.splitlines() if line.strip()]
        bullets = [str(value).strip() for value in raw if str(value).strip()] if isinstance(raw, list) else []
        slides.append({"title": title, "bullets": bullets[:6], "citation": str(item.get("citation", "")).strip()})
    if not slides:
        raise ValueError("No usable slides were returned. Please regenerate the presentation.")
    return slides


def slides_to_markdown(slides: list[dict]) -> str:
    blocks = []
    for i, slide in enumerate(slides, 1):
        points = "\n".join(f"- {point}" for point in slide["bullets"])
        citation = f"\n\n_Source: {slide['citation']}_" if slide.get("citation") else ""
        blocks.append(f"## {i}. {slide['title']}\n\n{points}{citation}")
    return "# Paper Presentation\n\n" + "\n\n".join(blocks)


def _text(slide, x, y, w, h, value, size, color, bold=False, font="Aptos"):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear(); frame.word_wrap = True
    frame.margin_left = Inches(0.02); frame.margin_right = Inches(0.02)
    frame.margin_top = Inches(0.01); frame.margin_bottom = Inches(0.01)
    p = frame.paragraphs[0]
    p.text = value
    p.font.name = font; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
    return box


def _background(slide, color):
    fill = slide.background.fill
    fill.solid(); fill.fore_color.rgb = color


def create_pptx(content: str, paper_name: str = "Research Paper") -> bytes:
    slides = parse_slides(content)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    count = len(slides)
    for idx, item in enumerate(slides):
        slide = prs.slides.add_slide(blank)
        is_cover = idx == 0
        _background(slide, NAVY if is_cover else PALE)
        if is_cover:
            # Accent rail and restrained title composition.
            rail = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(.22), Inches(7.5))
            rail.fill.solid(); rail.fill.fore_color.rgb = TEAL; rail.line.fill.background()
            _text(slide, Inches(.95), Inches(1.15), Inches(10.8), Inches(.38), "PAPERPILOT  /  RESEARCH BRIEF", 13, TEAL, True)
            _text(slide, Inches(.95), Inches(2.0), Inches(11.0), Inches(1.65), item["title"], 34, WHITE, True)
            _text(slide, Inches(.98), Inches(3.85), Inches(10.4), Inches(.8), paper_name, 17, RGBColor(201, 215, 234))
            if item["bullets"]:
                _text(slide, Inches(.98), Inches(5.15), Inches(10.8), Inches(.9), "  ·  ".join(item["bullets"][:2]), 16, WHITE)
            _text(slide, Inches(.98), Inches(6.9), Inches(10), Inches(.28), "SOURCE-GROUNDED ACADEMIC PRESENTATION", 9, RGBColor(155, 177, 204), True)
        else:
            # Header, section number, spacious content panel and page footer.
            _text(slide, Inches(.65), Inches(.34), Inches(2.4), Inches(.28), f"PAPERPILOT   /   {idx:02d}", 9, BLUE, True)
            _text(slide, Inches(.65), Inches(.83), Inches(11.9), Inches(.74), item["title"], 27, NAVY, True)
            rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.65), Inches(1.66), Inches(12.0), Inches(.035))
            rule.fill.solid(); rule.fill.fore_color.rgb = TEAL; rule.line.fill.background()
            panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(.65), Inches(1.98), Inches(12.0), Inches(4.72))
            panel.fill.solid(); panel.fill.fore_color.rgb = WHITE; panel.line.color.rgb = RGBColor(226, 233, 242)
            panel.text_frame.clear()
            bullets = item["bullets"] or ["No slide points were provided."]
            y = 2.18
            step = .70 if len(bullets) >= 6 else .82
            font_size = 15 if len(bullets) >= 6 else 17
            for bullet_no, bullet in enumerate(bullets[:6]):
                dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.02), Inches(y + .12), Inches(.13), Inches(.13))
                dot.fill.solid(); dot.fill.fore_color.rgb = TEAL if bullet_no == 0 else BLUE; dot.line.fill.background()
                _text(slide, Inches(1.38), Inches(y), Inches(10.65), Inches(step - .04), bullet, font_size, INK)
                y += step
            if item.get("citation"):
                _text(slide, Inches(.7), Inches(6.82), Inches(9.8), Inches(.27), f"SOURCE  {item['citation']}", 9, MUTED)
            _text(slide, Inches(11.25), Inches(6.82), Inches(1.4), Inches(.27), f"{idx + 1}  /  {count}", 9, MUTED)
    output = BytesIO(); prs.save(output)
    return output.getvalue()
