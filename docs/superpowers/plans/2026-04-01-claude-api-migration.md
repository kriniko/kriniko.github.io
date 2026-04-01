# Claude API Migration + Quality Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Gemini with Claude API in the poem generation pipeline and add a quality review step that scores drafts and rewrites low-quality ones before publishing.

**Architecture:** The script keeps its current flow (pick topic, generate poem, generate metadata, create article, placeholder image, update history) but swaps the Gemini SDK for the Anthropic SDK, uses Opus for creative writing and Sonnet for utility tasks, and inserts a new review_and_score step between generation and metadata that can trigger up to 2 rewrites.

**Tech Stack:** Python 3.12, `anthropic` SDK, Hugo, GitHub Actions

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `scripts/requirements.txt` | Modify | Swap google-genai for anthropic |
| `scripts/generate_poem.py` | Rewrite | Full Claude API migration + review step |
| `scripts/tests/test_generate_poem.py` | Create | Unit tests for the rewritten script |
| `.github/workflows/generate-poem.yml` | Modify | Swap GEMINI_API_KEY for ANTHROPIC_API_KEY |

---

### Task 1: Update requirements.txt

**Files:**
- Modify: `scripts/requirements.txt`

- [ ] **Step 1: Replace google-genai with anthropic**

Replace the contents of `scripts/requirements.txt` with:

```
anthropic>=0.40.0
requests>=2.31.0
Pillow>=10.0.0
```

- [ ] **Step 2: Verify install works**

Run: `cd /home/kristinanikolova/kriniko.github.io && pip install -r scripts/requirements.txt`
Expected: All packages install successfully, `anthropic` is available.

- [ ] **Step 3: Commit**

```bash
git add scripts/requirements.txt
git commit -m "chore: swap google-genai for anthropic SDK

Preparing for Claude API migration in poem generation pipeline."
```

---

### Task 2: Write tests for call_claude helper

**Files:**
- Create: `scripts/tests/__init__.py`
- Create: `scripts/tests/test_generate_poem.py`

- [ ] **Step 1: Create test directory and init file**

Create `scripts/tests/__init__.py` as an empty file.

- [ ] **Step 2: Write failing test for call_claude**

Create `scripts/tests/test_generate_poem.py`:

```python
"""Tests for generate_poem.py Claude API integration."""

import json
from unittest.mock import MagicMock, patch

import pytest


def make_mock_response(text):
    """Create a mock Anthropic API response."""
    mock_block = MagicMock()
    mock_block.text = text
    mock_resp = MagicMock()
    mock_resp.content = [mock_block]
    return mock_resp


class TestCallClaude:
    """Tests for the call_claude helper function."""

    @patch("generate_poem.anthropic")
    def test_call_claude_returns_text(self, mock_anthropic_mod):
        from generate_poem import call_claude

        mock_client = MagicMock()
        mock_anthropic_mod.Anthropic.return_value = mock_client
        mock_client.messages.create.return_value = make_mock_response("Hello world")

        # call_claude takes a pre-built client, model, system prompt, user prompt
        result = call_claude(mock_client, "claude-sonnet-4-6", "system", "user prompt")

        assert result == "Hello world"
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"
        assert call_kwargs["system"] == "system"
        assert call_kwargs["messages"] == [{"role": "user", "content": "user prompt"}]

    @patch("generate_poem.anthropic")
    @patch("generate_poem.time.sleep")
    def test_call_claude_retries_on_api_error(self, mock_sleep, mock_anthropic_mod):
        from generate_poem import call_claude
        import anthropic as real_anthropic

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            real_anthropic.APIError(
                message="server error",
                request=MagicMock(),
                body=None,
            ),
            make_mock_response("retry worked"),
        ]

        result = call_claude(mock_client, "claude-sonnet-4-6", "system", "prompt")

        assert result == "retry worked"
        assert mock_client.messages.create.call_count == 2
        mock_sleep.assert_called_once_with(5)

    @patch("generate_poem.anthropic")
    @patch("generate_poem.time.sleep")
    def test_call_claude_raises_after_two_failures(self, mock_sleep, mock_anthropic_mod):
        from generate_poem import call_claude
        import anthropic as real_anthropic

        mock_client = MagicMock()
        err = real_anthropic.APIError(
            message="server error",
            request=MagicMock(),
            body=None,
        )
        mock_client.messages.create.side_effect = [err, err]

        with pytest.raises(real_anthropic.APIError):
            call_claude(mock_client, "claude-sonnet-4-6", "system", "prompt")

        assert mock_client.messages.create.call_count == 2
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/kristinanikolova/kriniko.github.io && PYTHONPATH=scripts pytest scripts/tests/test_generate_poem.py::TestCallClaude -v`
Expected: FAIL — `generate_poem` has no `call_claude` function yet.

---

### Task 3: Write tests for review_and_score

**Files:**
- Modify: `scripts/tests/test_generate_poem.py`

- [ ] **Step 1: Add review_and_score tests**

Append to `scripts/tests/test_generate_poem.py`:

```python
class TestReviewAndScore:
    """Tests for the review_and_score quality gate."""

    @patch("generate_poem.call_claude")
    def test_publish_verdict_returns_poem_unchanged(self, mock_call):
        from generate_poem import review_and_score

        review_json = json.dumps({
            "score": 8,
            "satire": "good",
            "language": "good",
            "originality": "good",
            "verdict": "publish",
            "feedback": None,
        })
        mock_call.return_value = review_json

        client = MagicMock()
        result = review_and_score(client, "Заглавие", "Тялото на поемата", "тема")

        assert result["poem_body"] == "Тялото на поемата"
        assert result["title"] == "Заглавие"
        assert result["score"] == 8

    @patch("generate_poem.generate_poem")
    @patch("generate_poem.call_claude")
    def test_rewrite_verdict_triggers_regeneration(self, mock_call, mock_gen):
        from generate_poem import review_and_score

        rewrite_review = json.dumps({
            "score": 4,
            "satire": "weak",
            "language": "ok",
            "originality": "repetitive",
            "verdict": "rewrite",
            "feedback": "Needs sharper satire and better escalation",
        })
        publish_review = json.dumps({
            "score": 8,
            "satire": "strong",
            "language": "good",
            "originality": "fresh",
            "verdict": "publish",
            "feedback": None,
        })
        mock_call.side_effect = [rewrite_review, publish_review]
        mock_gen.return_value = "Ново заглавие\n\nПодобрено тяло"

        client = MagicMock()
        result = review_and_score(client, "Заглавие", "Слабо тяло", "тема")

        assert result["title"] == "Ново заглавие"
        assert result["poem_body"] == "Подобрено тяло"
        assert result["score"] == 8
        mock_gen.assert_called_once()
        # Verify feedback was passed to generate_poem
        gen_kwargs = mock_gen.call_args
        assert "Needs sharper satire" in str(gen_kwargs)

    @patch("generate_poem.generate_poem")
    @patch("generate_poem.call_claude")
    def test_max_retries_uses_best_version(self, mock_call, mock_gen):
        from generate_poem import review_and_score

        low_review = json.dumps({
            "score": 3,
            "satire": "weak",
            "language": "ok",
            "originality": "weak",
            "verdict": "rewrite",
            "feedback": "Needs work",
        })
        medium_review = json.dumps({
            "score": 5,
            "satire": "ok",
            "language": "ok",
            "originality": "ok",
            "verdict": "rewrite",
            "feedback": "Still needs work",
        })
        mock_call.side_effect = [low_review, medium_review]
        mock_gen.return_value = "Второ заглавие\n\nВторо тяло"

        client = MagicMock()
        result = review_and_score(client, "Първо заглавие", "Първо тяло", "тема")

        # Should use the version with score 5 (the rewrite), not score 3
        assert result["score"] == 5
        assert result["title"] == "Второ заглавие"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/kristinanikolova/kriniko.github.io && PYTHONPATH=scripts pytest scripts/tests/test_generate_poem.py::TestReviewAndScore -v`
Expected: FAIL — `generate_poem` has no `review_and_score` function yet.

---

### Task 4: Rewrite generate_poem.py with Claude API + review step

**Files:**
- Modify: `scripts/generate_poem.py` (full rewrite)

- [ ] **Step 1: Write the complete rewritten generate_poem.py**

Replace the entire contents of `scripts/generate_poem.py` with:

```python
#!/usr/bin/env python3
"""Generate a weekly satirical poem about Bulgarian bureaucracy using Claude API."""

import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "article"
IMAGES_DIR = REPO_ROOT / "static" / "images"
QUEUE_FILE = REPO_ROOT / "content" / "topics-queue.txt"
HISTORY_FILE = REPO_ROOT / "content" / "topics-history.json"

MODEL_CREATIVE = "claude-opus-4-6"
MODEL_UTILITY = "claude-sonnet-4-6"
MAX_TOKENS_CREATIVE = 4096
MAX_TOKENS_UTILITY = 2048
REVIEW_THRESHOLD = 7
MAX_REWRITES = 2

INSTITUTIONS = [
    "НАП", "НОИ", "КАТ", "ТЕЛК", "община", "митница", "нотариус",
    "кадастър", "ДНСК", "МВР", "ГРАО", "Агенция по вписванията",
    "пощи", "ЧСИ", "ДКС", "БАБХ", "РЗИ", "РИОСВ", "НСИ",
    "Бюро по труда", "Социални грижи", "КЕВР", "КЗП", "патентно ведомство",
    "БНБ", "КФН", "Гаранционен фонд", "ВиК", "Топлофикация",
    "ЧЕЗ", "EVN", "Енерго-Про", "БДЖ", "градски транспорт",
]

STYLE_PROMPT = """Ти си български сатиричен писател в традицията на Иво Сиромахов, Еленко Еленков и стила "Евала бе, митница".

СТИЛ:
- Горчива ирония маскирана като небрежно наблюдение
- Документален абсурдизъм — описвай реални процедури толкова детайлно, че абсурдът става очевиден
- Измислени имена на персонажи, които намекват за съдбата им (като министър Технологиев, Живко Живев, Г-жа Забавлева)
- Български частици и текстура (бе, ба, де, евала, Българска работа)
- Ескалиращ абсурд — започва правдоподобно, завършва невъзможно
- Понякога тъжно под комедията — "мани, мани, то голямо чудо стана"
- Смесица от диалог и разказ
- Самоиронично национално чувство за хумор — подигравка с обич, не с презрение
- Техно-бюрократичен абсурд (системи които съществуват на хартия, но отказват да работят)

ФОРМАТ: Фейлетон от 300-600 думи. НЕ повтаряй теми или имена от предишни статии."""

REVIEW_SYSTEM = """Ти си литературен редактор специализиран в българска сатира. 
Оценяваш фейлетони по следните критерии:
- Сатира: остра ли е иронията, ескалира ли абсурдът?
- Език: естествен ли е българският, има ли частици и текстура?
- Оригиналност: свеж ли е ъгълът, различен ли е от предишни теми?

Върни САМО валиден JSON, без markdown форматиране."""


def call_claude(client, model, system, prompt, max_tokens=None):
    """Call Claude API with retry logic. Returns response text."""
    if max_tokens is None:
        max_tokens = MAX_TOKENS_CREATIVE if model == MODEL_CREATIVE else MAX_TOKENS_UTILITY

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except anthropic.APIError as e:
            if attempt == 0:
                print(f"API error (attempt 1): {e}. Retrying in 5s...")
                time.sleep(5)
            else:
                raise


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def pick_topic(client, history):
    # Check queue first
    if QUEUE_FILE.exists():
        lines = [
            l.strip()
            for l in QUEUE_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        if lines:
            topic = lines[0]
            remaining = "\n".join(lines[1:]) if len(lines) > 1 else ""
            QUEUE_FILE.write_text(
                "# Добави теми тук — по една на ред\n" + remaining + "\n",
                encoding="utf-8",
            )
            return topic

    # AI picks a topic
    used_topics = [h["topic"] for h in history]
    prompt = f"""Избери ЕДНА конкретна тема за сатиричен фейлетон за българската бюрокрация.

Темата трябва да е конкретна ситуация (не просто институция), например:
- "Как се получава удостоверение за наследници когато наследниците са в чужбина"
- "Опашката пред КАТ в петък следобед"
- "Как се сменя доставчик на ток без да изгубиш ума си"

НЕ избирай теми подобни на вече използваните: {json.dumps(used_topics, ensure_ascii=False)}

Институции за вдъхновение: {', '.join(INSTITUTIONS)}

Върни САМО темата, нищо друго. Една тема, един ред."""

    result = call_claude(client, MODEL_UTILITY, "Ти си помощник за избор на теми.", prompt)
    return result.strip().strip('"')


def generate_poem(client, topic, history, feedback=None):
    used_topics = [h["topic"] for h in history]
    prompt = f"""ВЕЧЕ ИЗПОЛЗВАНИ ТЕМИ (НЕ повтаряй): {json.dumps(used_topics, ensure_ascii=False)}

ТЕМА: {topic}

Напиши фейлетона. Започни с заглавие на първия ред (без кавички, без "Заглавие:").
После празен ред и текста."""

    if feedback:
        prompt += f"\n\nОБРАТНА ВРЪЗКА ОТ РЕДАКТОР (вземи предвид): {feedback}"

    return call_claude(client, MODEL_CREATIVE, STYLE_PROMPT, prompt)


def review_and_score(client, title, poem_body, topic):
    """Review a poem draft. Returns dict with title, poem_body, score."""
    best = {"title": title, "poem_body": poem_body, "score": 0}

    for attempt in range(1 + MAX_REWRITES):
        review_prompt = f"""Оцени този фейлетон:

ЗАГЛАВИЕ: {title}

ТЕКСТ:
{poem_body}

Върни САМО валиден JSON:
{{
  "score": <1-10>,
  "satire": "<кратка оценка>",
  "language": "<кратка оценка>",
  "originality": "<кратка оценка>",
  "verdict": "<publish или rewrite>",
  "feedback": "<null ако publish, конкретни инструкции за подобрение ако rewrite>"
}}"""

        review_text = call_claude(client, MODEL_CREATIVE, REVIEW_SYSTEM, review_prompt)
        # Extract JSON from possible markdown code block
        clean = review_text.strip()
        if "```" in clean:
            match = re.search(r"```(?:json)?\s*(.*?)```", clean, re.DOTALL)
            if match:
                clean = match.group(1)
        review = json.loads(clean)

        score = review["score"]
        print(f"  Review attempt {attempt + 1}: score={score}, verdict={review['verdict']}")

        if score > best["score"]:
            best = {"title": title, "poem_body": poem_body, "score": score}

        if review["verdict"] == "publish" or score >= REVIEW_THRESHOLD:
            best = {"title": title, "poem_body": poem_body, "score": score}
            break

        if attempt < MAX_REWRITES:
            print(f"  Rewriting with feedback: {review['feedback']}")
            # Pass empty history to avoid re-fetching — topic is already chosen
            rewrite_full = generate_poem(client, topic, [], feedback=review["feedback"])
            lines = rewrite_full.split("\n", 1)
            title = lines[0].strip().strip("#").strip()
            poem_body = lines[1].strip() if len(lines) > 1 else rewrite_full

    return best


def generate_metadata(client, title, poem_text):
    prompt = f"""За тази българска сатирична статия, генерирай метаданни в JSON формат:

ЗАГЛАВИЕ: {title}
ТЕКСТ (първи 200 символа): {poem_text[:200]}

Върни САМО валиден JSON обект:
{{
  "description": "кратко описание до 160 символа на български",
  "slug": "slug-na-latinica-bez-specialni-znaci",
  "image_alt": "описание на илюстрация на български",
  "image_prompt": "Detailed English prompt for black-and-white ink cartoon illustration in minimalist satirical style with bold lines and exaggerated figures, illustrating this specific story. No signatures or artist names anywhere on the image. Any text in the image must be in Bulgarian.",
  "keywords": ["ключова1", "ключова2", "ключова3"],
  "teaser": "кратък тийзър за Facebook пост — 2-3 изречения, закачливи, с линк placeholder {{link}}"
}}"""

    for attempt in range(2):
        text = call_claude(client, MODEL_UTILITY, "Генерирай метаданни за статия. Върни САМО валиден JSON.", prompt)
        text = text.strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if attempt == 0:
                print(f"JSON parse error on metadata, retrying...")
                prompt += "\n\nВАЖНО: Върни САМО валиден JSON без markdown форматиране."
            else:
                raise


def create_article(title, poem_body, metadata, today):
    slug = metadata["slug"]
    md_content = f"""---
title: "{title}"
date: {today.isoformat()}
description: "{metadata['description']}"
draft: false
featured_image: "/images/{slug}.jpeg"
image_alt: "{metadata['image_alt']}"
keywords:
"""
    for kw in metadata["keywords"]:
        md_content += f"  - {kw}\n"
    md_content += f"---\n\n{poem_body}\n"

    filepath = CONTENT_DIR / f"{slug}.md"
    filepath.write_text(md_content, encoding="utf-8")
    return slug, filepath


def create_placeholder_image(slug, title):
    """Create a styled placeholder image."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 900
    img = Image.new("RGB", (width, height), "#f5f5f0")
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([20, 20, width - 20, height - 20], outline="#2d2d2d", width=3)

    # Draw decorative lines
    for y in range(100, 800, 120):
        draw.line([(60, y), (width - 60, y)], fill="#e0e0d8", width=1)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Center the site name
    draw.text((width // 2, 200), "Гише ∞", fill="#2d2d2d", font=font_large, anchor="mm")

    # Draw a simple counter/window shape
    cx, cy = width // 2, height // 2
    draw.rectangle([cx - 150, cy - 80, cx + 150, cy + 80], outline="#2d2d2d", width=3)
    draw.line([(cx - 150, cy - 30), (cx + 150, cy - 30)], fill="#2d2d2d", width=2)
    draw.text((cx, cy + 30), "ЗАТВОРЕНО", fill="#8b0000", font=font_small, anchor="mm")

    # Bottom text
    draw.text(
        (width // 2, height - 100),
        "gisheto.com",
        fill="#666666",
        font=font_small,
        anchor="mm",
    )

    img.save(IMAGES_DIR / f"{slug}.jpeg", "JPEG", quality=90)
    print(f"Image: {IMAGES_DIR / slug}.jpeg")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    history = load_history()
    today = date.today()

    # 1. Pick topic
    topic = pick_topic(client, history)
    print(f"Topic: {topic}")

    # 2. Generate poem
    poem_full = generate_poem(client, topic, history)
    lines = poem_full.split("\n", 1)
    title = lines[0].strip().strip("#").strip()
    poem_body = lines[1].strip() if len(lines) > 1 else poem_full
    print(f"Title: {title}")

    # 3. Review and score (may rewrite up to 2 times)
    print("Reviewing...")
    reviewed = review_and_score(client, title, poem_body, topic)
    title = reviewed["title"]
    poem_body = reviewed["poem_body"]
    print(f"Final score: {reviewed['score']}")

    # 4. Generate metadata
    metadata = generate_metadata(client, title, poem_body)
    slug = metadata["slug"]
    print(f"Slug: {slug}")

    # 5. Create article file
    slug, filepath = create_article(title, poem_body, metadata, today)
    print(f"Article: {filepath}")

    # 6. Create placeholder image
    create_placeholder_image(slug, title)

    # 7. Update history
    history.append({"topic": topic, "slug": slug, "date": today.isoformat()})
    save_history(history)

    # 8. Output for next steps
    output = {
        "slug": slug,
        "title": title,
        "teaser": metadata.get("teaser", ""),
        "image_prompt": metadata.get("image_prompt", ""),
        "article_url": f"https://gisheto.com/article/{slug}/",
        "image_url": f"https://gisheto.com/images/{slug}.jpeg",
    }
    output_file = REPO_ROOT / "scripts" / "output.json"
    output_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Output: {output_file}")

    return output


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run all tests**

Run: `cd /home/kristinanikolova/kriniko.github.io && PYTHONPATH=scripts pytest scripts/tests/test_generate_poem.py -v`
Expected: All tests in TestCallClaude and TestReviewAndScore pass.

- [ ] **Step 3: Commit**

```bash
git add scripts/generate_poem.py
git commit -m "feat: migrate generate_poem.py from Gemini to Claude API

- Use Opus for creative writing and review, Sonnet for topic/metadata
- Add review_and_score quality gate with score threshold and max 2 rewrites
- Add call_claude helper with retry logic
- Update image prompt: no signatures/artist names, Bulgarian text only
- Same output format and file structure"
```

---

### Task 5: Update GitHub Actions workflow

**Files:**
- Modify: `.github/workflows/generate-poem.yml:38-40`

- [ ] **Step 1: Replace GEMINI_API_KEY with ANTHROPIC_API_KEY**

In `.github/workflows/generate-poem.yml`, replace:

```yaml
      - name: Generate poem
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/generate_poem.py
```

with:

```yaml
      - name: Generate poem
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/generate_poem.py
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/generate-poem.yml
git commit -m "chore: use ANTHROPIC_API_KEY in poem generation workflow"
```

---

### Task 6: Add ANTHROPIC_API_KEY to GitHub Secrets

This is a manual step — cannot be done via code.

- [ ] **Step 1: Remind user to add secret**

The user needs to go to https://github.com/kriniko/kriniko.github.io/settings/secrets/actions and add:
- Name: `ANTHROPIC_API_KEY`
- Value: their Anthropic API key

- [ ] **Step 2: Optionally remove GEMINI_API_KEY**

If Gemini is no longer needed (after social post migration), the old secret can be removed. Keep it for now since `generate_social.py` still uses it.

---

### Task 7: End-to-end dry run

- [ ] **Step 1: Run the script locally with a test topic**

Run:
```bash
cd /home/kristinanikolova/kriniko.github.io
ANTHROPIC_API_KEY=<key> python scripts/generate_poem.py
```

Expected output:
```
Topic: <a specific bureaucratic scenario>
Title: <Bulgarian title>
Reviewing...
  Review attempt 1: score=<N>, verdict=<publish|rewrite>
Final score: <N>
Slug: <latin-slug>
Article: <path to .md file>
Image: <path to .jpeg file>
Output: <path to output.json>
```

- [ ] **Step 2: Verify generated article**

Check that:
- `content/article/<slug>.md` exists with proper frontmatter
- `static/images/<slug>.jpeg` exists
- `scripts/output.json` has correct URLs
- `content/topics-history.json` has the new entry

- [ ] **Step 3: Clean up test output**

Remove the test article and image:
```bash
rm content/article/<slug>.md static/images/<slug>.jpeg scripts/output.json
```
Restore topics-history.json to its original state:
```bash
git checkout content/topics-history.json
```

- [ ] **Step 4: Final commit of test files**

```bash
git add scripts/tests/
git commit -m "test: add unit tests for Claude API poem generation"
```
