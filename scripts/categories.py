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
