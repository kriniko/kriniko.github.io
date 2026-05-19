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
