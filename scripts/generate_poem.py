#!/usr/bin/env python3
"""Generate a weekly satirical poem about Bulgarian bureaucracy."""

import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from google import genai
from google.genai import types

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "article"
IMAGES_DIR = REPO_ROOT / "static" / "images"
QUEUE_FILE = REPO_ROOT / "content" / "topics-queue.txt"
HISTORY_FILE = REPO_ROOT / "content" / "topics-history.json"

MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30  # seconds
REVIEW_THRESHOLD = 7
MAX_REWRITES = 2


def call_gemini(client, prompt, system=None):
    """Call Gemini with retry logic and model fallback."""
    contents = prompt
    if system:
        contents = f"{system}\n\n{prompt}"

    for model in MODELS:
        for attempt in range(MAX_API_RETRIES):
            try:
                response = client.models.generate_content(model=model, contents=contents)
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                is_overloaded = any(k in err_str for k in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]) or "overloaded" in err_str.lower()
                if is_overloaded and attempt < MAX_API_RETRIES - 1:
                    print(f"  {model} attempt {attempt + 1} failed (503). Retrying in {API_RETRY_DELAY}s...")
                    time.sleep(API_RETRY_DELAY)
                elif is_overloaded:
                    print(f"  {model} exhausted retries. Trying fallback model...")
                    break  # try next model
                else:
                    raise  # non-503 error, don't retry

    raise RuntimeError("All models and retries exhausted")

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

REVIEW_PROMPT_TEMPLATE = """Ти си литературен редактор специализиран в българска сатира.
Оценяваш фейлетони по следните критерии:
- Сатира: остра ли е иронията, ескалира ли абсурдът?
- Език: естествен ли е българският, има ли частици и текстура?
- Оригиналност: свеж ли е ъгълът, различен ли е от предишни теми?

Оцени този фейлетон:

ЗАГЛАВИЕ: {title}

ТЕКСТ:
{poem_body}

Върни САМО валиден JSON, без markdown форматиране:
{{
  "score": <1-10>,
  "satire": "<кратка оценка>",
  "language": "<кратка оценка>",
  "originality": "<кратка оценка>",
  "verdict": "<publish или rewrite>",
  "feedback": "<null ако publish, конкретни инструкции за подобрение ако rewrite>"
}}"""


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
    result = call_gemini(client, f"""Избери ЕДНА конкретна тема за сатиричен фейлетон за българската бюрокрация.

Темата трябва да е конкретна ситуация (не просто институция), например:
- "Как се получава удостоверение за наследници когато наследниците са в чужбина"
- "Опашката пред КАТ в петък следобед"
- "Как се сменя доставчик на ток без да изгубиш ума си"

НЕ избирай теми подобни на вече използваните: {json.dumps(used_topics, ensure_ascii=False)}

Институции за вдъхновение: {', '.join(INSTITUTIONS)}

Върни САМО темата, нищо друго. Една тема, един ред.""")
    return result.strip('"')


def generate_poem(client, topic, history, feedback=None):
    used_topics = [h["topic"] for h in history]
    prompt = f"""{STYLE_PROMPT}

ВЕЧЕ ИЗПОЛЗВАНИ ТЕМИ (НЕ повтаряй): {json.dumps(used_topics, ensure_ascii=False)}

ТЕМА: {topic}

Напиши фейлетона. Започни с заглавие на първия ред (без кавички, без "Заглавие:").
После празен ред и текста."""

    if feedback:
        prompt += f"\n\nОБРАТНА ВРЪЗКА ОТ РЕДАКТОР (вземи предвид): {feedback}"

    return call_gemini(client, prompt)


def review_and_score(client, title, poem_body, topic, history):
    """Review a poem draft. Returns dict with title, poem_body, score."""
    best = {"title": title, "poem_body": poem_body, "score": 0}

    for attempt in range(1 + MAX_REWRITES):
        review_prompt = REVIEW_PROMPT_TEMPLATE.format(title=title, poem_body=poem_body)

        review_text = call_gemini(client, review_prompt)

        # Extract JSON from possible markdown code block
        if "```" in review_text:
            match = re.search(r"```(?:json)?\s*(.*?)```", review_text, re.DOTALL)
            if match:
                review_text = match.group(1)

        try:
            review = json.loads(review_text)
        except json.JSONDecodeError:
            print(f"  Review attempt {attempt + 1}: JSON parse error, treating as pass")
            best = {"title": title, "poem_body": poem_body, "score": 7}
            break

        score = review["score"]
        print(f"  Review attempt {attempt + 1}: score={score}, verdict={review['verdict']}")

        if score > best["score"]:
            best = {"title": title, "poem_body": poem_body, "score": score}

        if review["verdict"] == "publish" or score >= REVIEW_THRESHOLD:
            best = {"title": title, "poem_body": poem_body, "score": score}
            break

        if attempt < MAX_REWRITES:
            print(f"  Rewriting with feedback: {review['feedback']}")
            rewrite_full = generate_poem(client, topic, history, feedback=review["feedback"])
            lines = rewrite_full.split("\n", 1)
            title = lines[0].strip().strip("#").strip()
            poem_body = lines[1].strip() if len(lines) > 1 else rewrite_full

    return best


def generate_metadata(client, title, poem_text):
    text = call_gemini(client, f"""За тази българска сатирична статия, генерирай метаданни в JSON формат:

ЗАГЛАВИЕ: {title}
ТЕКСТ (първи 200 символа): {poem_text[:200]}

Върни САМО валиден JSON обект:
{{
  "description": "кратко описание до 160 символа на български",
  "slug": "slug-na-latinica-bez-specialni-znaci",
  "image_alt": "описание на илюстрация на български",
  "image_prompt": "Detailed English prompt for an illustration in the style of Bulgarian animator Donyo Donev (Доньо Донев) — flat 2D cartoon, hand-drawn ink lines, limited muted earth-tone palette (ochre, faded red, cream, charcoal), exaggerated long noses, big ears, droopy eyes, thin spindly limbs, retro 1970s socialist-era look, slightly absurd and melancholic atmosphere, simple geometric backgrounds. Illustrate this specific story. NO TEXT, NO SIGNATURES, NO ARTIST NAMES, NO WATERMARKS, NO LETTERS anywhere on the image. Do not write 'Donyo Donev' or any name. Pure illustration only.",
  "keywords": ["ключова1", "ключова2", "ключова3"],
  "teaser": "кратък тийзър за Facebook пост — 2-3 изречения, закачливи, с линк placeholder {{link}}"
}}""")
    # Extract JSON from possible markdown code block
    if "```" in text:
        text = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL).group(1)
    return json.loads(text)


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


def create_gemini_image(client, slug, image_prompt):
    """Generate Donyo Donev style cover via Gemini 2.5 Flash Image.

    Returns True on success, False on failure (caller falls back to placeholder).
    """
    if not image_prompt:
        return False

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9"),
                candidate_count=1,
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(part.inline_data.data))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                dest = IMAGES_DIR / f"{slug}.jpeg"
                img.save(dest, "JPEG", quality=92)
                print(f"Gemini image saved: {dest}")
                return True

        print("Gemini returned no image part")
        return False

    except Exception as exc:  # pylint: disable=broad-except
        print(f"Gemini image error ({type(exc).__name__}): {exc}")
        return False


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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
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
    reviewed = review_and_score(client, title, poem_body, topic, history)
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

    # 6. Create cover image via Gemini (Donyo Donev style), falling back to placeholder
    if not create_gemini_image(client, slug, metadata.get("image_prompt", "")):
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
