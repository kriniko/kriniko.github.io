#!/usr/bin/env python3
"""Generate social-only posts: memes, hooks, quotes, short jokes for Facebook."""

import json
import os
import random
import sys
from datetime import date
from pathlib import Path
from google import genai

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = REPO_ROOT / "content" / "topics-history.json"
SOCIAL_HISTORY_FILE = REPO_ROOT / "content" / "social-history.json"
CONTENT_DIR = REPO_ROOT / "content" / "article"

POST_TYPES = [
    {
        "type": "meme_text",
        "prompt": """Напиши КРАТЪК мийм текст (2-4 реда) за българската бюрокрация.
Формат: setup → punchline. Кратко, остро, споделяемо.
Примери за стил:
- "Отиваш в общината за 5 минути. Излизаш след 5 часа. С грешен документ."
- "Гише 7: Отворено от 10 до 10:05. Обедна почивка от 10:05 до 17:00."
- "— Трябва ми печат.\n— Печатът е на почивка.\n— А кога се връща?\n— Когато реши."
Върни САМО текста на мийма, нищо друго.""",
    },
    {
        "type": "bureaucratic_quote",
        "prompt": """Измисли ФАЛШИВ цитат от измислен български бюрократ. Трябва да звучи абсолютно автентично.
Формат:
"Цитатът тук" — Име Фамилия, Длъжност

Примери:
"Системата работи перфектно. Просто не е включена." — Инж. Сървъров, Началник ИТ отдел, МВР
"Ние сме отворени за граждани всеки ден. Просто не за тези граждани." — Г-жа Затворкова, Гише 12

Върни САМО цитата с автора, нищо друго.""",
    },
    {
        "type": "would_you_rather",
        "prompt": """Създай забавна "По-скоро бихте..." анкета свързана с българската бюрокрация.
Двата варианта трябва да са еднакво ужасяващи.
Формат:
По-скоро бихте:
A) вариант 1
B) вариант 2

Пример:
По-скоро бихте:
A) Чакали 6 часа на опашка в НАП
B) Попълнили формуляр 385-Б три пъти ръчно

Върни САМО анкетата, нищо друго.""",
    },
    {
        "type": "fun_fact",
        "prompt": """Измисли ФАЛШИВА но правдоподобна статистика за българската бюрокрация.
Трябва да звучи като истинска статистика, но да е абсурдна.
Формат: "Знаехте ли, че..." + фактът.

Примери:
"Знаехте ли, че средностатистическият българин прекарва 47 дни от живота си в чакане пред гишета? Това е повече, отколкото прекарва в отпуск."
"Знаехте ли, че в България има повече формуляри, отколкото граждани? При последното преброяване формулярите отказаха да бъдат преброени."

Върни САМО факта, нищо друго.""",
    },
    {
        "type": "old_article_hook",
        "prompt": """На базата на тази статия, напиши кратък закачлив Facebook пост (2-3 изречения),
който да привлече хората да я прочетат. Използвай различен ъгъл от оригиналния тийзър.
Може да е въпрос, провокация, или "а вие опитвали ли сте..."
Завърши с {{link}}

Върни САМО текста на поста, нищо друго.""",
    },
    {
        "type": "this_or_that",
        "prompt": """Създай кратък "Кое е по-лошо?" пост за българската бюрокрация.
Два абсурдни бюрократични сценария, единият малко по-лош от другия.
Формат кратък, споделяем, с емоджи.

Върни САМО текста, нищо друго.""",
    },
]


def load_social_history():
    if SOCIAL_HISTORY_FILE.exists():
        return json.loads(SOCIAL_HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_social_history(history):
    SOCIAL_HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_articles():
    """Load all published articles for old_article_hook posts."""
    articles = []
    for f in CONTENT_DIR.glob("*.md"):
        if f.name == "_index.md":
            continue
        text = f.read_text(encoding="utf-8")
        # Extract title and slug
        title_match = None
        for line in text.splitlines():
            if line.startswith("title:"):
                title_match = line.split(":", 1)[1].strip().strip('"')
                break
        slug = f.stem
        articles.append({"title": title_match or slug, "slug": slug})
    return articles


def generate_social_post(client, social_history):
    """Generate a social-only post."""
    # Pick post type, avoid repeating the same type consecutively
    recent_types = [h["type"] for h in social_history[-5:]]
    available = [p for p in POST_TYPES if p["type"] not in recent_types[-2:]]
    if not available:
        available = POST_TYPES
    post_type = random.choice(available)

    prompt = post_type["prompt"]

    # For old_article_hook, pick a random old article and include its context
    article_context = None
    if post_type["type"] == "old_article_hook":
        articles = load_articles()
        if articles:
            article = random.choice(articles)
            article_file = CONTENT_DIR / f"{article['slug']}.md"
            article_text = article_file.read_text(encoding="utf-8")
            # Get first 500 chars of content (after frontmatter)
            parts = article_text.split("---", 2)
            body = parts[2][:500] if len(parts) > 2 else ""
            prompt += f"\n\nСТАТИЯ: {article['title']}\nОТКЪС: {body}"
            article_context = {
                "slug": article["slug"],
                "title": article["title"],
                "url": f"https://gisheto.com/article/{article['slug']}/",
                "image_url": f"https://gisheto.com/images/{article['slug']}.jpeg",
            }

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = response.text.strip()

    # Add hashtags if not present
    if "#" not in text:
        text += "\n\n#гише #бюрокрация #България #сатира"

    # Replace link placeholder
    if article_context and "{link}" in text:
        text = text.replace("{link}", article_context["url"])

    return {
        "type": post_type["type"],
        "text": text,
        "article": article_context,
    }


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    social_history = load_social_history()

    post = generate_social_post(client, social_history)
    print(f"Type: {post['type']}")
    print(f"Text: {post['text'][:200]}...")

    # Save to output for Buffer posting
    output = {
        "type": post["type"],
        "text": post["text"],
    }
    if post.get("article"):
        output["article_url"] = post["article"]["url"]
        output["image_url"] = post["article"]["image_url"]

    output_file = REPO_ROOT / "scripts" / "social-output.json"
    output_file.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Update history
    social_history.append({
        "type": post["type"],
        "date": date.today().isoformat(),
        "preview": post["text"][:100],
    })
    # Keep last 50 entries
    social_history = social_history[-50:]
    save_social_history(social_history)

    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
