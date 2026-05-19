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
