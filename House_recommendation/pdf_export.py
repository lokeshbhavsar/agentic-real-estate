"""Generate a PDF brochure — one property per page — from recommended_properties.csv."""

import os
import urllib.request
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from House_recommendation.viewer import load_properties

DIR = Path(__file__).resolve().parent
DEFAULT_CSV = DIR / "recommended_properties.csv"
DEFAULT_PDF = DIR / "recommended_properties.pdf"

# colours similar to property_viewer.html
BG = colors.HexColor("#1a2234")
ACCENT = colors.HexColor("#f59e0b")
MINT = colors.HexColor("#34d399")
TEXT = colors.HexColor("#f1f5f9")
MUTED = colors.HexColor("#64748b")
LIGHT = colors.HexColor("#f8fafc")


def _download_image(url: str, timeout: int = 8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return ImageReader(BytesIO(data))
    except Exception:
        return None


def _wrap_text(c, text, x, y, max_width, line_height, font, size):
    c.setFont(font, size)
    words = str(text).split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    for i, ln in enumerate(lines):
        c.setFillColor(TEXT if font == "Helvetica" else MUTED)
        c.drawString(x, y - i * line_height, ln)
    return y - len(lines) * line_height


def _draw_stat_box(c, x, y, w, h, label, value):
    c.setFillColor(BG)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + w / 2, y + h - 22, str(value))
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawCentredString(x + w / 2, y + 8, label.upper())


def _draw_property_page(c, prop, index, total, width, height):
    margin = 36
    content_w = width - 2 * margin

    # page background
    c.setFillColor(LIGHT)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # header band
    c.setFillColor(BG)
    c.rect(0, height - 52, width, 52, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height - 32, "Recommended Properties")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 32, f"Property {index + 1} of {total}")

    y = height - 68

    # image area
    img_h = 195
    img_reader = None
    if prop.get("images"):
        img_reader = _download_image(prop["images"][0])

    c.setFillColor(BG)
    c.roundRect(margin, y - img_h, content_w, img_h, 12, fill=1, stroke=0)

    if img_reader:
        c.drawImage(
            img_reader,
            margin + 4,
            y - img_h + 4,
            width=content_w - 8,
            height=img_h - 8,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
    else:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 28)
        c.drawCentredString(margin + content_w / 2, y - img_h / 2 - 8, "🏠")

    # similarity badge
    badge = f"{prop['similarity'] * 100:.1f}% match"
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 9)
    badge_w = c.stringWidth(badge, "Helvetica-Bold", 9) + 20
    c.roundRect(margin + content_w - badge_w - 8, y - 28, badge_w, 20, 10, fill=1, stroke=0)
    c.setFillColor(BG)
    c.drawString(margin + content_w - badge_w + 2, y - 22, badge)

    y -= img_h + 18

    # price (highlight)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(margin, y, str(prop["price"]))
    y -= 28

    # heading
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 13)
    y = _wrap_text(c, prop["heading"], margin, y, content_w, 16, "Helvetica-Bold", 13) - 6

    # location
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    location = f"{prop['locality']}, {prop['city']}"
    c.drawString(margin, y, location)
    y -= 22

    # stat boxes — row 1
    box_w = (content_w - 16) / 3
    row1 = [
        ("Config", prop["bhk"]),
        ("Area", prop["area"]),
        ("Floor", f"{prop['floor']}/{prop['total_floors']}" if prop.get("floor") is not None else "—"),
    ]
    for i, (label, val) in enumerate(row1):
        _draw_stat_box(c, margin + i * (box_w + 8), y - 42, box_w, 42, label, val)
    y -= 54

    # stat boxes — row 2
    row2 = [
        ("Bath", prop.get("bathrooms", "—")),
        ("Balcony", prop.get("balconies", "—")),
        ("Landmarks", prop.get("landmarks", "—")),
    ]
    for i, (label, val) in enumerate(row2):
        _draw_stat_box(c, margin + i * (box_w + 8), y - 42, box_w, 42, label, val)
    y -= 54

    # tags
    if prop.get("tags"):
        tag_x = margin
        c.setFont("Helvetica", 8)
        for tag in prop["tags"][:6]:
            tag = str(tag)
            tw = c.stringWidth(tag, "Helvetica", 8) + 14
            if tag_x + tw > width - margin:
                break
            c.setFillColor(colors.HexColor("#fef3c7"))
            c.roundRect(tag_x, y - 14, tw, 16, 8, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#b45309"))
            c.drawString(tag_x + 7, y - 10, tag)
            tag_x += tw + 6
        y -= 26

    # description
    c.setFillColor(ACCENT)
    c.rect(margin, y - 2, 3, 60, fill=1, stroke=0)
    y = _wrap_text(
        c,
        prop.get("description") or "No description available.",
        margin + 12,
        y,
        content_w - 12,
        12,
        "Helvetica",
        9,
    ) - 10

    # footer
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(margin, 72, width - margin, 72)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, 52, str(prop.get("society", "—")))
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(margin, 38, str(prop.get("type", "—")))
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, 52, f"Agent: {prop.get('contact', '—')}")
    c.setFillColor(MUTED)
    c.drawRightString(width - margin, 38, str(prop.get("dealer", "—")))


def generate_pdf(csv_path=None, pdf_path=None) -> str:
    csv_path = Path(csv_path or DEFAULT_CSV)
    pdf_path = Path(pdf_path or DEFAULT_PDF)

    properties = load_properties(csv_path)
    if not properties:
        raise ValueError("No properties found in CSV.")

    width, height = A4
    c = canvas.Canvas(str(pdf_path), pagesize=A4)

    for i, prop in enumerate(properties):
        _draw_property_page(c, prop, i, len(properties), width, height)
        c.showPage()

    c.save()
    return str(pdf_path)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(DIR.parent))
    path = generate_pdf()
    print(f"PDF saved: {path}")
