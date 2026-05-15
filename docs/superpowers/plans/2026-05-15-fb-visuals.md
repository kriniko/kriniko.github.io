# Facebook Post Visuals + Categories + Humor Quality — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every Facebook post gets a category-appropriate visual (meme/infographic/illustration/GIF) and passes a best-of-3 humor quality check before publishing.

**Architecture:** New `categories.py` maps the 27 existing templates into 4 categories (memes, did_you_know, absurdi, reactions), each with a fixed visual treatment. New `visuals.py` builds the visual via Pollinations + PIL (memes/infographic/illustration) or Tenor API (GIF). Refactored `generate_social.py` picks category round-robin, generates 3 text variants in one Gemini call, scores them via a judge Gemini call, picks the best, generates the visual, and writes `social-output.json`. `post_to_buffer.py` is unchanged.

**Tech Stack:** Python 3.12, Pillow, requests, google-genai, Pollinations.ai (image gen), Tenor v2 API (GIF search), Buffer GraphQL API (publish).

**Spec:** `docs/superpowers/specs/2026-05-14-fb-visuals-design.md`

---

## File Structure

**Created:**
- `scripts/categories.py` — category + template mapping; round-robin picker
- `scripts/visuals.py` — `make_meme`, `make_infographic`, `make_illustration`, `fetch_gif`
- `scripts/fonts/DejaVuSans-Bold.ttf` — bundled Cyrillic-capable font for PIL overlay
- `scripts/judge.py` — best-of-3 generator + judge model wrapper
- `scripts/social-output.json` — already exists, schema unchanged (`text`, `image_url`)
- `tests/test_categories.py` — pure-function unit tests
- `tests/test_judge.py` — judge response parsing tests

**Modified:**
- `scripts/generate_social.py` — replaced control flow (kept POST_TEMPLATES, dropped random pick + single-prompt path)
- `scripts/requirements.txt` — add `pytest` (Pillow + requests already present)
- `.github/workflows/social-post.yml` — add TENOR_API_KEY env, expand `git add` to include `static/images/social/`

**New repo secret (manual step before first run):**
- `TENOR_API_KEY` — added by user via GitHub repo settings → Secrets → Actions

---

## Task 1: Bootstrap tests directory + pytest

**Files:**
- Create: `tests/__init__.py`
- Modify: `scripts/requirements.txt`

- [ ] **Step 1: Create empty test package**

```bash
mkdir -p ~/kriniko.github.io/tests
touch ~/kriniko.github.io/tests/__init__.py
```

- [ ] **Step 2: Add pytest to requirements**

Append to `scripts/requirements.txt`:

```
pytest>=8.0.0
```

- [ ] **Step 3: Install + verify**

```bash
cd ~/kriniko.github.io && pip install -r scripts/requirements.txt && pytest --version
```
Expected: prints pytest version.

- [ ] **Step 4: Commit**

```bash
git add tests/__init__.py scripts/requirements.txt
git commit -m "test: bootstrap pytest"
```

---

## Task 2: Category mapping module (categories.py)

**Files:**
- Create: `scripts/categories.py`
- Test: `tests/test_categories.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_categories.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from categories import CATEGORIES, pick_category, pick_template


def test_four_categories_exist():
    assert set(CATEGORIES.keys()) == {"memes", "did_you_know", "absurdi", "reactions"}


def test_each_category_has_required_fields():
    for key, cat in CATEGORIES.items():
        assert cat["name"]
        assert cat["emoji"]
        assert cat["visual_type"] in {"meme", "infographic", "illustration", "gif"}
        assert len(cat["templates"]) >= 3


def test_all_27_templates_covered():
    all_templates = set()
    for cat in CATEGORIES.values():
        all_templates.update(cat["templates"])
    assert len(all_templates) == 27


def test_no_template_in_two_categories():
    seen = []
    for cat in CATEGORIES.values():
        seen.extend(cat["templates"])
    assert len(seen) == len(set(seen))


def test_pick_category_round_robin_after_recent():
    history = [{"category": "memes"}, {"category": "did_you_know"}, {"category": "absurdi"}]
    picked = pick_category(history)
    assert picked == "reactions"


def test_pick_category_handles_empty_history():
    picked = pick_category([])
    assert picked in CATEGORIES


def test_pick_template_avoids_recent():
    history = [{"type": "meme_text"}, {"type": "weekend_meme"}]
    picked = pick_template("memes", history)
    assert picked not in {"meme_text", "weekend_meme"}
    assert picked in CATEGORIES["memes"]["templates"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/kriniko.github.io && pytest tests/test_categories.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'categories'`.

- [ ] **Step 3: Write implementation**

Create `scripts/categories.py`:

```python
"""Category + template mapping for Facebook social posts.

Each of 27 existing templates in generate_social.py is mapped to one of 4
categories. Categories drive visual type. Picker is round-robin across
categories and avoids recent templates within a category.
"""

import random

CATEGORIES = {
    "memes": {
        "name": "Мемета",
        "emoji": "🧠",
        "visual_type": "meme",
        "templates": [
            "meme_text",
            "weekend_meme",
            "before_after",
            "share_if",
            "pro_tip",
            "bureaucrat_quote",
        ],
    },
    "did_you_know": {
        "name": "Знаете ли че",
        "emoji": "💡",
        "visual_type": "infographic",
        "templates": [
            "did_you_know_real",
            "satirical_fact",
            "historical_bureaucracy",
            "bureaucracy_bingo",
        ],
    },
    "absurdi": {
        "name": "Абсурди",
        "emoji": "🤪",
        "visual_type": "illustration",
        "templates": [
            "current_absurdity",
            "comparison",
            "personification",
            "educational_satire",
            "survival_guide",
            "caption_this",
            "behind_the_scenes",
            "old_article_hook",
        ],
    },
    "reactions": {
        "name": "Реакции",
        "emoji": "🎬",
        "visual_type": "gif",
        "templates": [
            "interactive_poll",
            "engaging_question",
            "tag_a_friend",
            "this_or_that",
            "finish_the_sentence",
            "theme_song",
            "user_stories",
            "weekend_humor",
            "monthly_reflection",
        ],
    },
}


def pick_category(history):
    """Round-robin across categories. Avoid the last 3 used."""
    recent = [h.get("category") for h in history[-3:] if h.get("category")]
    available = [k for k in CATEGORIES if k not in recent]
    if not available:
        available = list(CATEGORIES)
    return random.choice(available)


def pick_template(category_key, history):
    """Random template from `category_key`, avoiding the last 6 in history."""
    recent_types = [h.get("type") for h in history[-6:]]
    available = [t for t in CATEGORIES[category_key]["templates"] if t not in recent_types]
    if not available:
        available = CATEGORIES[category_key]["templates"]
    return random.choice(available)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd ~/kriniko.github.io && pytest tests/test_categories.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/categories.py tests/test_categories.py
git commit -m "feat: categories module mapping 27 templates to 4 categories"
```

---

## Task 3: Bundle Cyrillic font for PIL overlay

**Files:**
- Create: `scripts/fonts/DejaVuSans-Bold.ttf` (binary, downloaded)

- [ ] **Step 1: Create directory + download font**

```bash
mkdir -p ~/kriniko.github.io/scripts/fonts
curl -L -o ~/kriniko.github.io/scripts/fonts/DejaVuSans-Bold.ttf \
  https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans-Bold.ttf
```

- [ ] **Step 2: Verify font loads with Pillow**

```bash
cd ~/kriniko.github.io && python3 -c "
from PIL import ImageFont
font = ImageFont.truetype('scripts/fonts/DejaVuSans-Bold.ttf', 64)
print('OK', font.getlength('БЮРОКРАЦИЯ'))
"
```
Expected: prints `OK` followed by a positive number.

- [ ] **Step 3: Commit**

```bash
git add scripts/fonts/DejaVuSans-Bold.ttf
git commit -m "chore: bundle DejaVuSans-Bold for Cyrillic meme overlay"
```

---

## Task 4: Visuals module — make_illustration (simplest path)

**Files:**
- Create: `scripts/visuals.py`
- Test: `tests/test_visuals.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_visuals.py`:

```python
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import visuals


def test_pollinations_url_includes_style_anchor():
    url = visuals.pollinations_url("a tired clerk at a window")
    assert "image.pollinations.ai" in url
    assert "Donyo+Donev" in url or "donyo-donev" in url.lower()


def test_make_illustration_writes_jpg(tmp_path):
    fake_jpeg = b"\xff\xd8\xff" + b"x" * 1000
    with patch("visuals.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=fake_jpeg)
        out = visuals.make_illustration("scene", out_dir=tmp_path, slug="test")
    assert out.exists()
    assert out.suffix == ".jpg"
    assert out.read_bytes().startswith(b"\xff\xd8\xff")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'visuals'`.

- [ ] **Step 3: Implement minimum to pass**

Create `scripts/visuals.py`:

```python
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
    encoded = urllib.parse.quote(full)
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -v
```
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/visuals.py tests/test_visuals.py
git commit -m "feat: visuals.make_illustration + Pollinations url builder"
```

---

## Task 5: Visuals module — make_meme (overlay logic)

**Files:**
- Modify: `scripts/visuals.py`
- Modify: `tests/test_visuals.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visuals.py`:

```python
def test_make_meme_writes_jpg_with_text(tmp_path):
    from io import BytesIO
    img = Image.new("RGB", (1080, 1080), "white")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    fake_jpeg = buf.getvalue()
    with patch("visuals.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=fake_jpeg)
        out = visuals.make_meme(
            top_text="КОГАТО",
            bottom_text="СИСТЕМАТА НЕ РАБОТИ",
            scene_prompt="frustrated clerk",
            out_dir=tmp_path,
            slug="meme-test",
        )
    assert out.exists()
    assert out.suffix == ".jpg"


def test_wrap_text_short_stays_one_line():
    lines = visuals._wrap_text("КРАТЪК", max_width_chars=20)
    assert lines == ["КРАТЪК"]


def test_wrap_text_long_breaks():
    long = "ТОВА Е МНОГО ДЪЛЪГ ТЕКСТ КОЙТО ТРЯБВА ДА СЕ ПРЕЛОМИ НА НЯКОЛКО РЕДА"
    lines = visuals._wrap_text(long, max_width_chars=20)
    assert len(lines) >= 2
    for line in lines:
        assert len(line) <= 24
```

Add to top of file:

```python
from PIL import Image
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py::test_make_meme_writes_jpg_with_text -v
```
Expected: FAIL — `AttributeError: module 'visuals' has no attribute 'make_meme'`.

- [ ] **Step 3: Implement make_meme + _wrap_text**

Append to `scripts/visuals.py`:

```python
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
```

- [ ] **Step 4: Run tests**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -v
```
Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/visuals.py tests/test_visuals.py
git commit -m "feat: visuals.make_meme with Impact-style Cyrillic overlay"
```

---

## Task 6: Visuals module — make_infographic

**Files:**
- Modify: `scripts/visuals.py`
- Modify: `tests/test_visuals.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visuals.py`:

```python
def test_make_infographic_writes_jpg(tmp_path):
    from io import BytesIO
    img = Image.new("RGB", (1080, 1080), "white")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    fake_jpeg = buf.getvalue()
    with patch("visuals.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=fake_jpeg)
        out = visuals.make_infographic(
            headline="ЗНАЕТЕ ЛИ ЧЕ",
            body="България има над 260 различни услуги изискващи лично присъствие.",
            scene_prompt="bureaucracy desk",
            out_dir=tmp_path,
            slug="info-test",
        )
    assert out.exists()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py::test_make_infographic_writes_jpg -v
```
Expected: FAIL — `AttributeError`.

- [ ] **Step 3: Implement make_infographic**

Append to `scripts/visuals.py`:

```python
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
```

- [ ] **Step 4: Run tests**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/visuals.py tests/test_visuals.py
git commit -m "feat: visuals.make_infographic for did-you-know posts"
```

---

## Task 7: Visuals module — fetch_gif (Tenor)

**Files:**
- Modify: `scripts/visuals.py`
- Modify: `tests/test_visuals.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visuals.py`:

```python
def test_fetch_gif_returns_url():
    fake_resp = {
        "results": [
            {"media_formats": {"gif": {"url": "https://media.tenor.com/abc.gif"}}}
        ]
    }
    with patch("visuals.requests.get") as mock_get, \
         patch.dict("os.environ", {"TENOR_API_KEY": "k"}):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: fake_resp)
        url = visuals.fetch_gif("frustrated office")
    assert url == "https://media.tenor.com/abc.gif"


def test_fetch_gif_empty_falls_back_to_simpler_keyword():
    empty = {"results": []}
    hit = {"results": [{"media_formats": {"gif": {"url": "https://media.tenor.com/x.gif"}}}]}
    with patch("visuals.requests.get") as mock_get, \
         patch.dict("os.environ", {"TENOR_API_KEY": "k"}):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: empty),
            MagicMock(status_code=200, json=lambda: hit),
        ]
        url = visuals.fetch_gif("very specific phrase that does not exist")
    assert url == "https://media.tenor.com/x.gif"


def test_fetch_gif_no_results_raises():
    empty = {"results": []}
    with patch("visuals.requests.get") as mock_get, \
         patch.dict("os.environ", {"TENOR_API_KEY": "k"}):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: empty)
        try:
            visuals.fetch_gif("xxx")
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -k gif -v
```
Expected: 3 FAILs — `AttributeError: ... fetch_gif`.

- [ ] **Step 3: Implement fetch_gif**

Append to `scripts/visuals.py`:

```python
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
```

- [ ] **Step 4: Run tests**

```bash
cd ~/kriniko.github.io && pytest tests/test_visuals.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/visuals.py tests/test_visuals.py
git commit -m "feat: visuals.fetch_gif via Tenor v2 with keyword fallback"
```

---

## Task 8: Judge module — best-of-3 generation + scoring

**Files:**
- Create: `scripts/judge.py`
- Test: `tests/test_judge.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_judge.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from judge import parse_variants, parse_scores, pick_best


def test_parse_variants_three_blocks():
    raw = "First post text.\n---\nSecond post text.\n---\nThird post text."
    out = parse_variants(raw)
    assert out == ["First post text.", "Second post text.", "Third post text."]


def test_parse_variants_strips_numbering():
    raw = "1. First\n---\n2. Second\n---\n3. Third"
    out = parse_variants(raw)
    assert out == ["First", "Second", "Third"]


def test_parse_variants_two_blocks_pads_to_three():
    raw = "Only one.\n---\nOnly two."
    out = parse_variants(raw)
    assert len(out) == 3
    assert out[2] == out[0] or out[2] == out[1]


def test_parse_scores_valid_json():
    raw = '[{"laugh":7,"share":6},{"laugh":4,"share":4},{"laugh":9,"share":8}]'
    out = parse_scores(raw)
    assert out == [{"laugh": 7, "share": 6}, {"laugh": 4, "share": 4}, {"laugh": 9, "share": 8}]


def test_parse_scores_with_markdown_fence():
    raw = '```json\n[{"laugh":7,"share":6},{"laugh":4,"share":4},{"laugh":9,"share":8}]\n```'
    out = parse_scores(raw)
    assert len(out) == 3


def test_parse_scores_malformed_returns_none():
    assert parse_scores("not json at all") is None


def test_pick_best_returns_highest_sum():
    variants = ["a", "b", "c"]
    scores = [{"laugh": 5, "share": 5}, {"laugh": 9, "share": 8}, {"laugh": 6, "share": 6}]
    best, total = pick_best(variants, scores)
    assert best == "b"
    assert total == 17


def test_pick_best_no_scores_returns_first():
    variants = ["a", "b", "c"]
    best, total = pick_best(variants, None)
    assert best == "a"
    assert total == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/kriniko.github.io && pytest tests/test_judge.py -v
```
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement judge**

Create `scripts/judge.py`:

```python
"""Best-of-3 generation + judge scoring for social posts.

Two pure-function parsers (variant splitter, score parser) and one selector.
The Gemini calls themselves live in generate_social.py; this module isolates
the format handling so it's testable without network.
"""

import json
import re

GENERATION_PREAMBLE = """Ти си български сатирик. Целта ти: пост който кара читателя ДА СЕ ИЗСМЕЕ ТИХО НА ТЕЛЕФОНА В ОФИСА.
Не общи фрази, а специфични. Ползвай:
- Конкретни институции: НАП, КАТ, БДЖ, ЕОН/ЧЕЗ, общината, "областна"
- Конкретни моменти: "елате утре", "системата не работи", "не съм оторизирана", "този прозорец не работи", "обедна почивка от 10:05 до 17:00"
- Конкретни абсурди: печат върху печат, формуляр в 3 копия, час за след 3 месеца, гише 7
- Конкретни хора: "леля на гише 3", "охранителят който не знае нищо"

Избягвай: "Опа, бюрокрация!", "Браво на администрацията!", общи философски заключения.
Бъди КОНКРЕТЕН. Образът да е виден. Шегата да е остра.

Сега, ето задачата:
{task}

ВЪРНИ 3 ВАРИАНТА разделени с ред "---". Без номерация. Без обяснения. Само трите поста."""

JUDGE_PROMPT = """Ти си строг редактор на сатиричен портал. Имаш 3 варианта на Facebook пост.
Оцени всеки 1-10 по два критерия:
- laugh: реално ли е смешно (1=не, 10=ще се смея на глас)
- share: бих ли го споделил с приятел (1=не, 10=веднага)

Бъди строг. Средното не е 7 — средното е 4.

Варианти:
1. {v1}
2. {v2}
3. {v3}

Върни САМО JSON масив: [{{"laugh":N,"share":N}},{{"laugh":N,"share":N}},{{"laugh":N,"share":N}}]"""

REGEN_NOTE = "\n\nПредишните варианти бяха слаби. Бъди по-конкретен и по-остър."

THRESHOLD = 14


def parse_variants(raw):
    blocks = [b.strip() for b in raw.split("---") if b.strip()]
    cleaned = [re.sub(r"^\s*\d+[\.\)]\s*", "", b) for b in blocks]
    while len(cleaned) < 3 and cleaned:
        cleaned.append(cleaned[-1])
    return cleaned[:3]


def parse_scores(raw):
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, flags=re.S)
    payload = fence.group(1) if fence else raw
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, list) or len(data) != 3:
        return None
    for entry in data:
        if not isinstance(entry, dict) or "laugh" not in entry or "share" not in entry:
            return None
    return data


def pick_best(variants, scores):
    if not scores:
        return variants[0], 0
    totals = [s["laugh"] + s["share"] for s in scores]
    best_idx = totals.index(max(totals))
    return variants[best_idx], totals[best_idx]
```

- [ ] **Step 4: Run tests**

```bash
cd ~/kriniko.github.io && pytest tests/test_judge.py -v
```
Expected: 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/judge.py tests/test_judge.py
git commit -m "feat: judge module - variant parsing + score parsing + best picker"
```

---

## Task 9: Refactor generate_social.py — wire categories + judge + visuals

**Files:**
- Modify: `scripts/generate_social.py`

- [ ] **Step 1: Read existing file**

```bash
cd ~/kriniko.github.io && wc -l scripts/generate_social.py
```
Expected: ~477 lines. Keep `POST_TEMPLATES` and history helpers; replace flow.

- [ ] **Step 2: Rewrite main pipeline**

Replace the body of `scripts/generate_social.py` with:

```python
#!/usr/bin/env python3
"""Generate one Facebook post per run.

Flow:
  1. pick category (round-robin) + template (avoid recent)
  2. Gemini: 3 text variants
  3. Gemini: judge scores -> pick best (regen once if max < THRESHOLD)
  4. Gemini: 1-sentence English scene prompt for visual
  5. dispatch visual by category.visual_type
  6. write social-output.json with {text, image_url}
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import date
from pathlib import Path

from google import genai

from categories import CATEGORIES, pick_category, pick_template
from judge import (
    GENERATION_PREAMBLE,
    JUDGE_PROMPT,
    REGEN_NOTE,
    THRESHOLD,
    parse_scores,
    parse_variants,
    pick_best,
)
import visuals

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30
SOCIAL_HISTORY_FILE = REPO_ROOT / "content" / "social-history.json"
CONTENT_DIR = REPO_ROOT / "content" / "article"
SITE_BASE_URL = "https://gisheto.com"

# Keep existing POST_TEMPLATES dict here (unchanged) — copy from previous version.
# (The 27 entries with type/name/prompt/hashtags remain identical.)
POST_TEMPLATES = [
    # ... (paste existing 27 entries unchanged)
]


def load_history():
    if SOCIAL_HISTORY_FILE.exists():
        return json.loads(SOCIAL_HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    SOCIAL_HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def gemini_call(client, prompt):
    """Single Gemini call with retry + model fallback."""
    for model in MODELS:
        for attempt in range(MAX_API_RETRIES):
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                return resp.text.strip()
            except Exception as e:
                err = str(e)
                overloaded = any(
                    k in err for k in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]
                )
                if overloaded and attempt < MAX_API_RETRIES - 1:
                    print(f"  {model} attempt {attempt + 1} overloaded, retry in {API_RETRY_DELAY}s")
                    time.sleep(API_RETRY_DELAY)
                elif overloaded:
                    print(f"  {model} exhausted, trying fallback")
                    break
                else:
                    raise
    raise RuntimeError("All models exhausted")


def find_template(template_type):
    for t in POST_TEMPLATES:
        if t["type"] == template_type:
            return t
    raise KeyError(template_type)


def generate_variants(client, template, regen=False):
    task = template["prompt"]
    full = GENERATION_PREAMBLE.format(task=task) + (REGEN_NOTE if regen else "")
    raw = gemini_call(client, full)
    return parse_variants(raw)


def score_variants(client, variants):
    prompt = JUDGE_PROMPT.format(v1=variants[0], v2=variants[1], v3=variants[2])
    raw = gemini_call(client, prompt)
    return parse_scores(raw)


def build_scene_prompt(client, post_text):
    """1-sentence English visual description used as Pollinations/Tenor input."""
    prompt = f"""You will be given a Bulgarian satirical Facebook post about bureaucracy.
Return ONE short English sentence (max 15 words) describing a visual scene for it.
No commentary. No labels. Just the sentence.

Post:
{post_text}"""
    return gemini_call(client, prompt).strip().strip('".')


def slugify_for_file(template_type):
    today = date.today().isoformat()
    return f"{today}-{template_type}"


def make_visual(category_key, template_type, chosen_text, scene_prompt):
    """Dispatch by category visual_type. Returns (image_url, local_path_or_none)."""
    visual_type = CATEGORIES[category_key]["visual_type"]
    slug = slugify_for_file(template_type)

    if visual_type == "gif":
        try:
            url = visuals.fetch_gif(scene_prompt)
            return url, None
        except RuntimeError as e:
            print(f"  GIF fetch failed ({e}); falling back to illustration")
            path = visuals.make_illustration(scene_prompt, slug=slug)
            return f"{SITE_BASE_URL}/images/social/{path.name}", path

    if visual_type == "meme":
        top, bottom = split_meme_text(chosen_text)
        path = visuals.make_meme(top, bottom, scene_prompt, slug=slug)
    elif visual_type == "infographic":
        headline, body = split_infographic_text(chosen_text)
        path = visuals.make_infographic(headline, body, scene_prompt, slug=slug)
    else:
        path = visuals.make_illustration(scene_prompt, slug=slug)

    return f"{SITE_BASE_URL}/images/social/{path.name}", path


def split_meme_text(text):
    """Crude split: first line up, rest down. If single line, put it all bottom."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    lines = [l for l in lines if not l.startswith("#")]
    if not lines:
        return "", text
    if len(lines) == 1:
        return "", lines[0]
    return lines[0], " ".join(lines[1:])


def split_infographic_text(text):
    """First line headline, rest body."""
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        return "ЗНАЕТЕ ЛИ", text
    return lines[0], " ".join(lines[1:]) if len(lines) > 1 else lines[0]


def run(dry_run=False):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    history = load_history()
    category_key = pick_category(history)
    template_type = pick_template(category_key, history)
    template = find_template(template_type)

    print(f"Category: {category_key}  Template: {template_type}")

    variants = generate_variants(client, template)
    scores = score_variants(client, variants)
    best_text, total = pick_best(variants, scores)
    print(f"  best score: {total}")

    if total < THRESHOLD:
        print("  below threshold, regenerating once")
        variants = generate_variants(client, template, regen=True)
        scores = score_variants(client, variants)
        best_text, total = pick_best(variants, scores)
        print(f"  regen score: {total}")

    hashtags = template.get("hashtags", "#гише #бюрокрация")
    if "#" not in best_text:
        best_text = f"{best_text}\n\n{hashtags}"

    scene_prompt = build_scene_prompt(client, best_text)
    print(f"  scene: {scene_prompt}")

    image_url, local_path = make_visual(category_key, template_type, best_text, scene_prompt)
    print(f"  visual: {image_url}")

    output = {
        "type": template_type,
        "category": category_key,
        "text": best_text,
        "image_url": image_url,
    }
    out_file = REPO_ROOT / "scripts" / "social-output.json"
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    history.append({
        "type": template_type,
        "category": category_key,
        "date": date.today().isoformat(),
        "score": total,
        "preview": best_text[:100],
    })
    history = history[-50:]
    save_history(history)
    print(f"output: {out_file}")
    if dry_run:
        print("DRY RUN: skipping Buffer step (post_to_buffer.py not invoked here anyway)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```

**Important:** preserve the existing `POST_TEMPLATES` list (27 entries) — copy it verbatim from the old `generate_social.py` into the spot marked `# ... (paste existing 27 entries unchanged)`. Use `git show HEAD:scripts/generate_social.py` if needed to retrieve.

- [ ] **Step 3: Copy POST_TEMPLATES from old file into new file**

```bash
cd ~/kriniko.github.io && python3 -c "
import re
old = open('scripts/generate_social.py').read()
m = re.search(r'POST_TEMPLATES = \[(.*?)\n\]\n', old, flags=re.S)
print(m.group(0))
" > /tmp/templates.txt
```
Then open `/tmp/templates.txt`, copy the content, and replace the placeholder block in the new file with the full list.

- [ ] **Step 4: Syntax check**

```bash
cd ~/kriniko.github.io && python3 -c "import ast; ast.parse(open('scripts/generate_social.py').read()); print('OK')"
```
Expected: `OK`.

- [ ] **Step 5: Run linter / import check**

```bash
cd ~/kriniko.github.io && python3 -c "
import sys; sys.path.insert(0, 'scripts')
import generate_social
print('import OK, templates:', len(generate_social.POST_TEMPLATES))
"
```
Expected: `import OK, templates: 27`.

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_social.py
git commit -m "feat: wire categories + judge + visuals into generate_social pipeline"
```

---

## Task 10: Update workflow yml — TENOR_API_KEY + image commit path

**Files:**
- Modify: `.github/workflows/social-post.yml`

- [ ] **Step 1: Add TENOR_API_KEY to generate step**

Find the "Generate social post" step in `.github/workflows/social-post.yml` and add `TENOR_API_KEY`:

```yaml
      - name: Generate social post
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINIAPI }}
          TENOR_API_KEY: ${{ secrets.TENOR_API_KEY }}
        run: python scripts/generate_social.py
```

- [ ] **Step 2: Expand git add to include social images**

In the "Commit social history" step, replace:

```yaml
          git add content/social-history.json
```

with:

```yaml
          git add content/social-history.json static/images/social/
```

- [ ] **Step 3: Sanity check yaml**

```bash
cd ~/kriniko.github.io && python3 -c "
import yaml; print(yaml.safe_load(open('.github/workflows/social-post.yml')))" | head -5
```
Expected: parses without exception.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/social-post.yml
git commit -m "ci: pass TENOR_API_KEY + commit generated social images"
```

---

## Task 11: Add TENOR_API_KEY repo secret (manual)

**Files:** none

- [ ] **Step 1: User adds secret**

The user creates a Tenor v2 API key at https://developers.google.com/tenor/guides/quickstart and adds it as a repo secret named `TENOR_API_KEY` via GitHub repo settings → Secrets → Actions → New repository secret.

Verify via API:

```bash
TOKEN="<the existing GHP from Kliuchove.txt>"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/kriniko/kriniko.github.io/actions/secrets" \
  | python3 -m json.tool | grep TENOR_API_KEY
```
Expected: shows `TENOR_API_KEY` in the secrets list.

If user does not have a Tenor key yet, the `reactions` category will fall back to `make_illustration` via the error path in `make_visual()`, so other categories continue to work.

---

## Task 12: End-to-end dry-run

**Files:** none

- [ ] **Step 1: Run dry-run locally with real API keys**

```bash
cd ~/kriniko.github.io
export GEMINI_API_KEY=$(grep -i "gemini" /mnt/c/Users/kristina.nikolova/Downloads/Kliuchove.txt | head -1 | awk '{print $NF}')
export TENOR_API_KEY=$(grep -i "tenor" /mnt/c/Users/kristina.nikolova/Downloads/Kliuchove.txt | head -1 | awk '{print $NF}')
python3 scripts/generate_social.py --dry-run
```
Expected: prints `Category: ...`, `Template: ...`, `best score: ...`, `scene: ...`, `visual: https://gisheto.com/images/social/...jpg`, and writes both `scripts/social-output.json` + a JPG under `static/images/social/`.

- [ ] **Step 2: Inspect output**

```bash
cd ~/kriniko.github.io && cat scripts/social-output.json
ls -la static/images/social/
```
Expected: JSON with text + image_url; one new JPG.

- [ ] **Step 3: Manually open the JPG**

```bash
explorer.exe $(wslpath -w $(ls -t static/images/social/*.jpg | head -1))
```
Expected: image opens in Windows. User confirms it looks like the right category (meme/infographic/illustration).

- [ ] **Step 4: Clean up dry-run artifacts**

```bash
cd ~/kriniko.github.io && rm scripts/social-output.json
# Keep the JPG: it's a real generated asset and will be committed by the workflow on next run.
git status --short
```

---

## Task 13: Push + manual workflow trigger

**Files:** none

- [ ] **Step 1: Push all committed work**

```bash
cd ~/kriniko.github.io && git push https://kriniko:<GHP_FROM_KLIUCHOVE>@github.com/kriniko/kriniko.github.io.git main
```
Expected: push succeeds.

- [ ] **Step 2: Trigger social-post workflow**

```bash
TOKEN="<GHP_FROM_KLIUCHOVE>"
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/kriniko/kriniko.github.io/actions/workflows/social-post.yml/dispatches" \
  -d '{"ref":"main"}' -w "HTTP %{http_code}\n"
```
Expected: `HTTP 204`.

- [ ] **Step 3: Watch the run**

```bash
sleep 60
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/kriniko/kriniko.github.io/actions/runs?per_page=3" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['conclusion'] or r['status'], r['name'], r['html_url']) for r in d['workflow_runs']]"
```
Expected: `Social Media Post` run completes `success`.

- [ ] **Step 4: Verify Facebook post**

User opens the Facebook page Гише ∞ and confirms the new post has the visual attached (image or GIF). If not, capture the workflow logs and the published Buffer post; do not claim done.

---

## Task 14: Document for next-time runner

**Files:**
- Modify: `README.md` (only if it exists and documents the social pipeline)

- [ ] **Step 1: Check README**

```bash
cd ~/kriniko.github.io && grep -n "social" README.md 2>/dev/null || echo "no README mention"
```

- [ ] **Step 2: If README mentions social pipeline, add categories section**

Insert under existing social docs:

```markdown
### Social Post Categories

Each post falls into one of 4 categories with a fixed visual treatment:
- 🧠 МЕМЕТА — illustration + Impact-style Cyrillic overlay
- 💡 ЗНАЕТЕ ЛИ ЧЕ — illustration + boxed infographic text
- 🤪 АБСУРДИ — clean Доньо Донев illustration
- 🎬 РЕАКЦИИ — GIF from Tenor

Pipeline generates 3 text variants, scores them with a judge model, publishes the best (regenerates once if all below 14/20).

Required secrets: `GEMINIAPI`, `BUFFERAPI`, `BUFFER_FACEBOOK_CHANNEL_ID`, `GHP`, `TENOR_API_KEY`.
```

- [ ] **Step 3: Commit (only if README modified)**

```bash
git add README.md
git commit -m "docs: README section on social post categories + visuals"
```
