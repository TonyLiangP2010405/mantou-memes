import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1] / "memes" / "mantou_duel"


def test_hundred_reviewed_sources_and_crop_assets_are_distinct():
    templates = json.loads((ROOT / "templates.json").read_text(encoding="utf-8"))
    assert len(templates) == 100
    assert len({t["source_sha256"] for t in templates}) == 100
    assert len({t["name"] for t in templates}) == 100
    pictures = set()
    for template in templates:
        assert template["caption"].startswith("{name}，")
        x0, y0, x1, y1 = template["crop"]
        width, height = template["source_size"]
        assert 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
        path = ROOT / "images" / template["asset"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == template["asset_sha256"]
        with Image.open(path) as image:
            assert image.size == (x1 - x0, y1 - y0)
            assert template["animated"] == (getattr(image, "n_frames", 1) > 1)
            pictures.add(
                hashlib.sha256(
                    ImageOps.contain(image.convert("RGB"), (128, 128)).tobytes()
                ).hexdigest()
            )
    # Count the pictures before captions: changing words on one base cannot pass.
    assert len(pictures) == 100


def test_each_new_template_personalizes_the_output(new_meme):
    first = new_meme(texts=["群友甲"]).getvalue()
    second = new_meme(texts=["群友乙"]).getvalue()
    assert first != second
    with Image.open(BytesIO(first)) as image:
        assert image.size == (512, 512)
        assert len(first) < 2_000_000
        for index in range(getattr(image, "n_frames", 1)):
            image.seek(index)
            image.load()
        # Captions must fit in their bottom panel, including the first/last letters.
        for box in [(0, 390, 16, 512), (496, 390, 512, 512)]:
            margin = image.convert("RGB").crop(box)
            assert (
                ImageChops.difference(margin, Image.new("RGB", margin.size, "white")).getbbox()
                is None
            )
