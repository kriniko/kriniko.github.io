import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from PIL import Image

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
