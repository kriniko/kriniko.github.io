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


def test_parse_scores_with_chatter_prefix():
    raw = 'Ето оценките: [{"laugh":7,"share":6},{"laugh":4,"share":4},{"laugh":9,"share":8}]'
    out = parse_scores(raw)
    assert out is not None
    assert len(out) == 3
    assert out[2]["laugh"] == 9


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
