#!/usr/bin/env python3
"""Launch interactive property viewer for recommended_properties.csv."""

import ast
import json
import math
import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

DIR = Path(__file__).resolve().parent
DEFAULT_CSV = DIR / "recommended_properties.csv"
HTML_FILE = DIR / "property_viewer.html"
PORT = 8765


def _safe(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value


def _parse_list(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (ValueError, SyntaxError):
        return [part.strip() for part in text.split(",") if part.strip()]


def _format_price(row):
    price = _safe(row.get("PRICE"))
    if price:
        return str(price)
    max_price = _safe(row.get("MAX_PRICE"))
    if max_price is None:
        return "Price on request"
    if max_price >= 1_00_00_000:
        return f"₹ {max_price / 1_00_00_000:.2f} Cr"
    if max_price >= 1_00_000:
        return f"₹ {max_price / 1_00_000:.2f} Lac"
    return f"₹ {max_price:,.0f}"


def load_properties(csv_path: Path) -> list[dict]:
    df = pd.read_csv(csv_path)
    properties = []

    for _, row in df.iterrows():
        images = _parse_list(row.get("PROPERTY_IMAGES"))
        if not images:
            photo = _safe(row.get("MEDIUM_PHOTO_URL")) or _safe(row.get("PHOTO_URL"))
            if photo:
                images = [photo]

        tags = _parse_list(row.get("TOP_USPS")) + _parse_list(row.get("SECONDARY_TAGS"))
        tags = [str(t) for t in tags if t]

        desc = _safe(row.get("DESCRIPTION")) or ""
        if len(desc) > 320:
            desc = desc[:317] + "..."

        bedrooms = _safe(row.get("BEDROOM_NUM"))
        bathrooms = _safe(row.get("BATHROOM_NUM"))
        bhk = f"{int(bedrooms)} BHK" if bedrooms and not math.isnan(float(bedrooms)) else "—"

        properties.append({
            "id": _safe(row.get("PROP_ID")),
            "heading": _safe(row.get("PROP_HEADING")) or _safe(row.get("PROP_NAME")) or "Property",
            "name": _safe(row.get("PROP_NAME")) or "—",
            "locality": _safe(row.get("LOCALITY")) or "—",
            "city": _safe(row.get("CITY")) or "—",
            "type": _safe(row.get("PROPERTY_TYPE")) or "—",
            "price": _format_price(row),
            "area": _safe(row.get("AREA")) or "—",
            "bhk": bhk,
            "bedrooms": _safe(row.get("BEDROOM_NUM")),
            "bathrooms": _safe(row.get("BATHROOM_NUM")),
            "balconies": _safe(row.get("BALCONY_NUM")),
            "floor": _safe(row.get("FLOOR_NUM")),
            "total_floors": _safe(row.get("TOTAL_FLOOR")),
            "society": _safe(row.get("SOCIETY_NAME")) or _safe(row.get("BUILDING_NAME")) or "—",
            "description": desc,
            "similarity": round(float(row.get("SIMILARITY_SCORE", 0) or 0), 3),
            "contact": _safe(row.get("CONTACT_NAME")) or "—",
            "dealer": _safe(row.get("CONTACT_COMPANY_NAME")) or "—",
            "landmarks": _safe(row.get("TOTAL_LANDMARK_COUNT")),
            "images": images,
            "tags": tags[:8],
        })

    return properties


def make_handler(properties: list[dict]):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIR), **kwargs)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/properties":
                payload = json.dumps(properties).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            super().do_GET()

        def log_message(self, format, *args):
            try:
                msg = str(args[0]) if args else ""
            except Exception:
                msg = ""
            if "/api/" not in msg and "favicon" not in msg:
                super().log_message(format, *args)

    return Handler


def main():
    csv_path = Path(os.environ.get("PROPERTY_CSV", DEFAULT_CSV))
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if not HTML_FILE.exists():
        raise FileNotFoundError(f"HTML not found: {HTML_FILE}")

    properties = load_properties(csv_path)
    server = HTTPServer(("127.0.0.1", PORT), make_handler(properties))
    url = f"http://127.0.0.1:{PORT}/property_viewer.html"

    print(f"Loaded {len(properties)} properties from {csv_path.name}")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop")

    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
