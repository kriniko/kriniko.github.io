"""Visual generation for social posts.

Four entry points by category visual_type:
  meme        -> make_meme(top, bottom, scene)         -> Path
  infographic -> make_infographic(headline, body, scene)-> Path
  illustration-> make_illustration(scene)              -> Path
  gif         -> fetch_gif(keywords)                   -> str (URL)
"""

import os
import re
import time
import urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
SOCIAL_IMG_DIR = REPO_ROOT / "static" / "images" / "social"
FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"
POLLINATIONS_STYLE = (
    "black and white ink illustration in the style of Donyo Donev, "
    "minimalist line art, single red accent color, bulgarian satire"
)

TENOR_BASE = "https://tenor.googleapis.com/v2/search"

MAX_FETCH_RETRIES = 3
FETCH_RETRY_DELAY = 10


def _slugify(text):
    s = re.sub(r"[^a-zA-Z0-9-]+", "-", text.lower())
    return s.strip("-")[:60] or "post"


def pollinations_url(scene_prompt, width=1080, height=1080):
    full = f"{scene_prompt}, {POLLINATIONS_STYLE}"
    encoded = urllib.parse.quote_plus(full)
    return (
        f"{POLLINATIONS_BASE}{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux"
    )


def _fetch_with_retry(url):
    last_err = None
    for attempt in range(MAX_FETCH_RETRIES):
        try:
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200:
                return resp.content
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            last_err = str(e)
        if attempt < MAX_FETCH_RETRIES - 1:
            time.sleep(FETCH_RETRY_DELAY)
    raise RuntimeError(f"Fetch failed after {MAX_FETCH_RETRIES} retries: {last_err}")


def make_illustration(scene_prompt, out_dir=None, slug=None):
    """Plain Pollinations illustration, no overlay. Returns Path."""
    out_dir = Path(out_dir) if out_dir else SOCIAL_IMG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slug or _slugify(scene_prompt)
    url = pollinations_url(scene_prompt)
    data = _fetch_with_retry(url)
    out_path = out_dir / f"{slug}.jpg"
    out_path.write_bytes(data)
    return out_path


def _wrap_text(text, max_width_chars=20):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) <= max_width_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines or [text]


def _draw_impact_text(draw, text, image_w, y_start, font_size, position):
    """Draw Cyrillic Impact-style centered text with black stroke.

    position: 'top' (y_start = 40) or 'bottom' (y_start = image_h - lines*lh - 40).
    """
    font = ImageFont.truetype(str(FONT_PATH), font_size)
    lines = _wrap_text(text.upper(), max_width_chars=20)
    line_height = int(font_size * 1.15)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        line_w = bbox[2] - bbox[0]
        x = (image_w - line_w) // 2
        y = y_start + i * line_height
        draw.text(
            (x, y), line, font=font, fill="white",
            stroke_width=4, stroke_fill="black",
        )
    return len(lines) * line_height


def make_meme(top_text, bottom_text, scene_prompt, out_dir=None, slug=None):
    """Pollinations illustration + Impact-style top/bottom Cyrillic overlay."""
    out_dir = Path(out_dir) if out_dir else SOCIAL_IMG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slug or _slugify(top_text + "-" + bottom_text)
    url = pollinations_url(scene_prompt)
    from io import BytesIO
    data = _fetch_with_retry(url)
    img = Image.open(BytesIO(data)).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font_size = int(w * 0.06)
    if top_text:
        _draw_impact_text(draw, top_text, w, 40, font_size, "top")
    if bottom_text:
        bottom_lines = _wrap_text(bottom_text.upper(), max_width_chars=20)
        line_height = int(font_size * 1.15)
        y_start = h - len(bottom_lines) * line_height - 40
        _draw_impact_text(draw, bottom_text, w, y_start, font_size, "bottom")
    out_path = out_dir / f"{slug}.jpg"
    img.save(out_path, format="JPEG", quality=90)
    return out_path


def make_infographic(headline, body, scene_prompt, out_dir=None, slug=None):
    """Pollinations illustration + white bordered text block bottom-third."""
    out_dir = Path(out_dir) if out_dir else SOCIAL_IMG_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slug or _slugify(headline)
    url = pollinations_url(scene_prompt)
    from io import BytesIO
    data = _fetch_with_retry(url)
    img = Image.open(BytesIO(data)).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    block_h = int(h * 0.42)
    block_y = h - block_h
    draw.rectangle([(0, block_y), (w, h)], fill="white")
    draw.rectangle(
        [(20, block_y + 20), (w - 20, h - 20)],
        outline="black", width=6,
    )

    headline_font = ImageFont.truetype(str(FONT_PATH), int(w * 0.055))
    body_font = ImageFont.truetype(str(FONT_PATH), int(w * 0.038))

    pad = 60
    cur_y = block_y + 40
    bbox = draw.textbbox((0, 0), headline.upper(), font=headline_font)
    line_w = bbox[2] - bbox[0]
    draw.text(((w - line_w) // 2, cur_y), headline.upper(), font=headline_font, fill="black")
    cur_y += (bbox[3] - bbox[1]) + 30

    body_lines = _wrap_text(body, max_width_chars=36)
    line_h = int(w * 0.052)
    for line in body_lines:
        bb = draw.textbbox((0, 0), line, font=body_font)
        lw = bb[2] - bb[0]
        draw.text(((w - lw) // 2, cur_y), line, font=body_font, fill="black")
        cur_y += line_h

    out_path = out_dir / f"{slug}.jpg"
    img.save(out_path, format="JPEG", quality=90)
    return out_path


def fetch_gif(keywords):
    """Search Tenor for a GIF matching `keywords` (English). Returns direct URL.

    If first search returns no results, retry with the first word only.
    Raises RuntimeError if still empty or API key missing.
    """
    api_key = os.environ.get("TENOR_API_KEY")
    if not api_key:
        raise RuntimeError("TENOR_API_KEY not set")

    def _search(q):
        resp = requests.get(
            TENOR_BASE,
            params={
                "q": q,
                "key": api_key,
                "client_key": "gisheto",
                "limit": 10,
                "media_filter": "gif",
                "contentfilter": "medium",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    results = _search(keywords)
    if not results:
        simpler = keywords.split()[0] if keywords.split() else keywords
        if simpler != keywords:
            results = _search(simpler)
    if not results:
        raise RuntimeError(f"Tenor: no GIF for '{keywords}'")

    return results[0]["media_formats"]["gif"]["url"]
