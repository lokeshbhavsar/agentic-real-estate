#!/usr/bin/env python3
"""Generate a simple project overview PDF for demo / audience."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

OUTPUT = Path(__file__).resolve().parent / "HPA_Project_Overview.pdf"

ACCENT = colors.HexColor("#2563eb")
DARK = colors.HexColor("#0f172a")
BODY = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748b")
LIGHT_BG = colors.HexColor("#f1f5f9")


def wrap(c, text, x, y, width, size=10, font="Helvetica", leading=14):
    c.setFont(font, size)
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)
    return y - len(lines) * leading


def section_title(c, title, x, y, width):
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, title)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(x, y - 4, x + width, y - 4)
    return y - 22


def bullet(c, text, x, y, width, size=10):
    c.setFillColor(BODY)
    c.setFont("Helvetica", size)
    c.drawString(x, y, "•")
    return wrap(c, text, x + 12, y, width - 12, size=size, leading=14) - 4


def new_page_if_needed(c, y, min_y=2.5 * cm):
    if y < min_y:
        c.showPage()
        return A4[1] - 2 * cm
    return y


def build_pdf(path: Path = OUTPUT):
    w, h = A4
    margin = 2 * cm
    width = w - 2 * margin
    c = canvas.Canvas(str(path), pagesize=A4)

    # ---- Cover ----
    c.setFillColor(DARK)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(margin, h - 4 * cm, "HPA Project")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#94a3b8"))
    wrap(
        c,
        "House Price Prediction, Property Recommendation & Blockchain Agent",
        margin,
        h - 5.2 * cm,
        width,
        size=14,
        font="Helvetica",
        leading=18,
    )
    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 11)
    c.drawString(margin, 3 * cm, "Demo overview — simple explanation for audience")

    c.showPage()

    # ---- Page 2: Big picture ----
    y = h - 2 * cm
    y = section_title(c, "What is this project?", margin, y, width)
    y = wrap(
        c,
        "This project combines real estate data, two machine learning models, blockchain "
        "operations, and an AI agent. You can talk to the agent in plain English — it figures "
        "out what you want and runs the right function (tool) for you.",
        margin,
        y,
        width,
        size=11,
        leading=16,
    ) - 16

    y = section_title(c, "Data we start with", margin, y, width)
    y = bullet(
        c,
        "Raw property data from Gurgaon (10,000+ listings) with details like bedrooms, "
        "bathrooms, area, location, photos, price, society name, and more.",
        margin,
        y,
        width,
    )
    y = bullet(
        c,
        "We clean and prepare this data before training — for example: filter sale listings, "
        "convert property type to numbers, extract sector and GPS coordinates.",
        margin,
        y,
        width,
    )

    y = new_page_if_needed(c, y)

    # ---- ML Model 1 ----
    y = section_title(c, "Model 1 — Price Prediction (XGBoost)", margin, y, width)
    y = wrap(
        c,
        "Goal: Given property features, predict an approximate price (MAX_PRICE).",
        margin,
        y,
        width,
        size=11,
        leading=15,
    ) - 8

    c.setFillColor(LIGHT_BG)
    c.roundRect(margin, y - 95, width, 100, 6, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 10, y - 14, "14 input features (example):")
    features = (
        "Bedrooms, Bathrooms, Balconies, Facing, Age, Carpet sqft, Super built-up sqft, "
        "Property type (4 categories), Sector number, Latitude, Longitude"
    )
    wrap(c, features, margin + 10, y - 28, width - 20, size=9, leading=12)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 10, y - 58, "Target: MAX_PRICE")
    c.setFont("Helvetica", 9)
    c.drawString(margin + 10, y - 72, "Model: XGBRegressor — saved as property_price_model.pkl")
    c.drawString(margin + 10, y - 86, "Accuracy: R² ≈ 0.91  |  Error (MAE) ≈ ± ₹31.8 Lac")
    y -= 115

    y = bullet(
        c,
        "The model learns which features matter most (e.g. area and location often weigh heavily).",
        margin,
        y,
        width,
    )
    y = bullet(
        c,
        "At runtime: pass 14 comma-separated numbers → get predicted price instantly.",
        margin,
        y,
        width,
    )

    y = new_page_if_needed(c, y)

    # ---- ML Model 2 ----
    y = section_title(c, "Model 2 — Similar Property Recommendation (KNN)", margin, y, width)
    y = wrap(
        c,
        "Goal: Find properties in our database that are most similar to what the user wants.",
        margin,
        y,
        width,
        size=11,
        leading=15,
    ) - 8

    y = bullet(c, "Uses K-Nearest Neighbors with Euclidean distance on the same 14 features.", margin, y, width)
    y = bullet(c, "Location (latitude/longitude) is weighted more heavily so nearby areas rank higher.", margin, y, width)
    y = bullet(c, "Returns the top 15 closest matches with a similarity score.", margin, y, width)
    y = bullet(c, "Output: recommended_properties.csv + recommended_properties.pdf (one page per property).", margin, y, width)
    y = bullet(c, "Interactive web viewer (viewer.py) to browse results with photos and details.", margin, y, width)

    y = new_page_if_needed(c, y)

    # ---- Web3 ----
    y = section_title(c, "Blockchain — Read & Write (Web3)", margin, y, width)
    y = wrap(
        c,
        "Reusable functions connect to a smart contract on BSC testnet:",
        margin,
        y,
        width,
        size=11,
        leading=15,
    ) - 8

    y = bullet(c, "balanceOf — check token balance for any wallet address (read).", margin, y, width)
    y = bullet(c, "allowance — check how much a spender is allowed to use (read).", margin, y, width)
    y = bullet(c, "transferFrom — move tokens from one address to another (write / transaction).", margin, y, width)
    y = wrap(
        c,
        "In a demo story: transfer can represent buying or paying for a property on-chain.",
        margin,
        y - 4,
        width,
        size=10,
        font="Helvetica-Oblique",
        leading=14,
    ) - 12

    y = new_page_if_needed(c, y)

    # ---- Agent ----
    y = section_title(c, "The AI Agent — how it ties everything together", margin, y, width)
    y = wrap(
        c,
        "An agent is a loop: LLM (Gemini) + tools (Python functions) + memory.",
        margin,
        y,
        width,
        size=11,
        leading=15,
    ) - 10

    c.setFillColor(LIGHT_BG)
    c.roundRect(margin, y - 72, width, 78, 6, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 10, y - 14, "How the agent thinks (ReAct pattern):")
    steps = [
        "1. Thought — understand what the user wants",
        "2. Action — pick a tool (predict price, recommend, balance, transfer…)",
        "3. Observation — read the tool result",
        "4. Final Answer — reply in plain language",
    ]
    sy = y - 28
    for s in steps:
        c.setFont("Helvetica", 9)
        c.drawString(margin + 10, sy, s)
        sy -= 14
    y -= 90

    y = bullet(c, "Each tool has a description — the LLM reads it and picks the best match.", margin, y, width)
    y = bullet(c, "You can ask in natural language: “predict price for…”, “suggest similar properties…”, “what is my balance…”", margin, y, width)
    y = bullet(c, "General questions work too — the LLM can answer without calling a tool.", margin, y, width)

    y = new_page_if_needed(c, y)

    # ---- Demo flow ----
    y = section_title(c, "Suggested demo flow", margin, y, width)
    demos = [
        "1. Ask agent to predict price — paste 14 feature values.",
        "2. Ask agent to recommend similar properties — same features → CSV + PDF.",
        "3. Open viewer.py or share the PDF brochure with the audience.",
        "4. Show blockchain read: balance / allowance for a wallet.",
        "5. Show blockchain write: transfer tokens (property purchase story).",
    ]
    for d in demos:
        y = bullet(c, d, margin, y, width)

    y = new_page_if_needed(c, y)

    # ---- Future ----
    y = section_title(c, "Scope for improvement", margin, y, width)
    improvements = [
        "Improve prediction accuracy with more data and tuning.",
        "Better agent memory for longer, smarter conversations.",
        "Add RAG — analyze locality scores, living quality, and facilities before final answer.",
        "Auto-invest agent — monitor news, invest in properties, flag scams.",
    ]
    for item in improvements:
        y = bullet(c, item, margin, y, width)

    y = new_page_if_needed(c, y)

    # ---- Project structure ----
    y = section_title(c, "Project folders (quick map)", margin, y, width)
    folders = [
        "House_prediction_model/ — training notebook, predict.py, saved XGB model",
        "House_recommendation/ — KNN notebook, CSV/PDF output, viewer, recommendation.pkl",
        "ContractOperations/ — Web3 read/write (rw.py)",
        "AGENT/ — agent.py + tool.py (LLM + all tools)",
    ]
    for f in folders:
        y = bullet(c, f, margin, y, width, size=9)

    # Footer on last page
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(w / 2, 1.5 * cm, "HPA — House · Prediction · Agent  |  Demo document")

    c.save()
    return str(path)


if __name__ == "__main__":
    out = build_pdf()
    print(f"Demo PDF saved: {out}")
