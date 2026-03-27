#!/usr/bin/env python3
"""Generate a weekly satirical poem about Bulgarian bureaucracy."""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from google import genai

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "article"
IMAGES_DIR = REPO_ROOT / "static" / "images"
QUEUE_FILE = REPO_ROOT / "content" / "topics-queue.txt"
HISTORY_FILE = REPO_ROOT / "content" / "topics-history.json"

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
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Избери ЕДНА конкретна тема за сатиричен фейлетон за българската бюрокрация.

Темата трябва да е конкретна ситуация (не просто институция), например:
- "Как се получава удостоверение за наследници когато наследниците са в чужбина"
- "Опашката пред КАТ в петък следобед"
- "Как се сменя доставчик на ток без да изгубиш ума си"

НЕ избирай теми подобни на вече използваните: {json.dumps(used_topics, ensure_ascii=False)}

Институции за вдъхновение: {', '.join(INSTITUTIONS)}

Върни САМО темата, нищо друго. Една тема, един ред.""",
    )
    return response.text.strip().strip('"')

def generate_poem(client, topic, history):
    used_topics = [h["topic"] for h in history]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""{STYLE_PROMPT}

ВЕЧЕ ИЗПОЛЗВАНИ ТЕМИ (НЕ повтаряй): {json.dumps(used_topics, ensure_ascii=False)}

ТЕМА: {topic}

Напиши фейлетона. Започни с заглавие на първия ред (без кавички, без "Заглавие:").
После празен ред и текста.""",
    )
    return response.text.strip()

def generate_metadata(client, title, poem_text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""За тази българска сатирична статия, генерирай метаданни в JSON формат:

ЗАГЛАВИЕ: {title}
ТЕКСТ (първи 200 символа): {poem_text[:200]}

Върни САМО валиден JSON обект:
{{
  "description": "кратко описание до 160 символа на български",
  "slug": "slug-na-latinica-bez-specialni-znaci",
  "image_alt": "описание на илюстрация на български",
  "image_prompt": "Detailed English prompt for Donio Donev style black-and-white ink cartoon illustrating this specific story. Minimalist bold lines, exaggerated figures, satirical political cartoon. Any text in the image must be in Bulgarian.",
  "keywords": ["ключова1", "ключова2", "ключова3"],
  "teaser": "кратък тийзър за Facebook пост — 2-3 изречения, закачливи, с линк placeholder {{link}}"
}}""",
    )
    text = response.text.strip()
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

    # 3. Generate metadata
    metadata = generate_metadata(client, title, poem_body)
    slug = metadata["slug"]
    print(f"Slug: {slug}")

    # 4. Create article file
    slug, filepath = create_article(title, poem_body, metadata, today)
    print(f"Article: {filepath}")

    # 5. Create placeholder image (Canva/Imagen not available in CI)
    # The image will be a simple styled placeholder
    # In production, upgrade Gemini for Imagen or add Canva API
    create_placeholder_image(slug, title)

    # 6. Update history
    history.append({"topic": topic, "slug": slug, "date": today.isoformat()})
    save_history(history)

    # 7. Output for next steps
    output = {
        "slug": slug,
        "title": title,
        "teaser": metadata.get("teaser", ""),
        "image_prompt": metadata.get("image_prompt", ""),
        "article_url": f"https://gisheto.com/article/{slug}/",
        "image_url": f"https://gisheto.com/images/{slug}.jpeg",
    }
    # Write outputs for the workflow
    output_file = REPO_ROOT / "scripts" / "output.json"
    output_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Output: {output_file}")

    return output

def create_placeholder_image(slug, title):
    """Create a styled placeholder image when Canva/Imagen is not available."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 900
    img = Image.new("RGB", (width, height), "#f5f5f0")
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([20, 20, width - 20, height - 20], outline="#2d2d2d", width=3)

    # Draw decorative lines (Donev-inspired)
    for y in range(100, 800, 120):
        draw.line([(60, y), (width - 60, y)], fill="#e0e0d8", width=1)

    # "Гише ∞" branding
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

if __name__ == "__main__":
    main()
