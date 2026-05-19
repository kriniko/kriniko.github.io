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
