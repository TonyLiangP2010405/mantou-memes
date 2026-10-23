import hashlib
import json
from io import BytesIO
from pathlib import Path

import pytest
from meme_generator.exception import TextNumberMismatch
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1] / "memes" / "mantou_duel"
TEMPLATES = {t["key"]: t for t in json.loads((ROOT / "templates.json").read_text(encoding="utf-8"))}


def picture(color):
    output = BytesIO()
    Image.new("RGB", (160, 210), color).save(output, "PNG")
    return output.getvalue()


def test_hundred_sources_are_distinct_and_faces_are_inside_the_crops():
    assert len(TEMPLATES) == 100
    assert len({t["source_sha256"] for t in TEMPLATES.values()}) == 100
    assert len({t["name"] for t in TEMPLATES.values()}) == 100
    pictures = set()
    for template in TEMPLATES.values():
        assert "caption" not in template
        x0, y0, x1, y1 = template["crop"]
        width, height = template["source_size"]
        assert 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
        path = ROOT / "images" / template["asset"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == template["asset_sha256"]
        with Image.open(path) as image:
            assert image.size == (x1 - x0, y1 - y0)
            assert template["animated"] == (getattr(image, "n_frames", 1) > 1)
            face_sets = template.get("frame_faces", [template["faces"]])
            if "frame_faces" in template:
                assert len(face_sets) == image.n_frames
            for faces in face_sets:
                assert len(faces) == template["images"]
                for face in faces:
                    a, b, c, d = face["box"]
                    assert 0 <= a < c <= image.width and 0 <= b < d <= image.height, template["key"]
            pictures.add(
                hashlib.sha256(
                    ImageOps.contain(image.convert("RGB"), (128, 128)).tobytes()
                ).hexdigest()
            )
    assert len(pictures) == 100


def test_each_new_template_replaces_its_faces_and_rejects_text(new_meme):
    template = TEMPLATES[new_meme.key]
    count = template["images"]
    params = new_meme.params_type
    assert params.min_images == params.max_images == count
    assert params.min_texts == params.max_texts == 0
    red, blue = picture("red"), picture("blue")
    first = new_meme(images=[red] * count).getvalue()
    with Image.open(ROOT / "images" / template["asset"]) as base:
        contained = ImageOps.contain(base, (496, 496))
        sx, sy = contained.width / base.width, contained.height / base.height
        left, top = (512 - contained.width) // 2, (512 - contained.height) // 2
    for target in range(count):
        inputs = [red] * count
        inputs[target] = blue
        changed = new_meme(images=inputs).getvalue()
        assert first != changed
        with Image.open(BytesIO(changed)) as image:
            assert image.size == (512, 512) and len(changed) < 2_000_000
            for index in range(image.n_frames):
                image.seek(index)
                frame = image.convert("RGB")
                faces = template.get("frame_faces", [template["faces"]] * image.n_frames)[index]
                for number, face in enumerate(faces):
                    x0, y0, x1, y1 = face["box"]
                    x = round((x0 + x1) * sx / 2) + left
                    y = round((y0 + y1) * sy / 2) + top
                    color = frame.getpixel((x, y))
                    assert color[2 if number == target else 0] > 200, (
                        new_meme.key,
                        index,
                        number,
                        color,
                    )
    with pytest.raises(TextNumberMismatch):
        new_meme(images=[red] * count, texts=["不接受文字"])
