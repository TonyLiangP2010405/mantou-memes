import hashlib
import importlib.util
import json
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from meme_generator.exception import ImageNumberMismatch, TextNumberMismatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "memes/mantou_actions"
TEMPLATES = json.loads((ASSETS / "templates.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location(
    "avatar_test_runtime", ROOT / "memes/_mantou_avatar.py"
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_five_hundred_distinct_source_backed_image_only_actions(memes):
    registered = {m.key: m for m in memes}
    previous = json.loads((ROOT / "memes/mantou_duel/templates.json").read_text(encoding="utf-8"))
    old_hashes = {r["source_sha256"] for r in previous}
    assert len(TEMPLATES) == 500
    assert len({r["source_sha256"] for r in TEMPLATES}) == 500
    assert len({r["asset_sha256"] for r in TEMPLATES}) == 500
    assert {r["source_sha256"] for r in TEMPLATES}.isdisjoint(old_hashes)
    for number, item in enumerate(TEMPLATES, 1):
        assert item["key"] == f"mantou_action_{number:03}"
        meme = registered[item["key"]]
        assert (meme.params_type.min_images, meme.params_type.max_images) == (1, 1)
        assert (meme.params_type.min_texts, meme.params_type.max_texts) == (0, 0)
        assert item["source_commit"] in item["source_url"]
        assert item["review_status"] == "retained source and composite frames visually inspected"
        asset = ASSETS / "images" / item["asset"]
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == item["asset_sha256"]
        with Image.open(asset) as image:
            assert list(image.size) == item["asset_size"]
            assert image.n_frames == len(item["frame_faces"])
            assert item["faces"] == item["frame_faces"][0]
            assert len(item["source_sample_indices"]) == image.n_frames
            if item["animated"]:
                assert image.format == "GIF" and 2 <= image.n_frames <= 12
                # The source itself must contain genuine multi-frame material.
                assert item["source_frames"] > 3
                image.seek(image.n_frames - 1)
                image.load()
            else:
                assert image.format == "PNG" and image.n_frames == 1
            for faces in item["frame_faces"]:
                for face in faces:
                    x0, y0, x1, y1 = face["box"]
                    assert 0 <= x0 < x1 <= image.width
                    assert 0 <= y0 < y1 <= image.height
                    assert -90 <= face["angle"] <= 90
                    for x, y in face.get("outline", []):
                        assert -1 <= x <= image.width + 1
                        assert -1 <= y <= image.height + 1


def test_detected_eyes_nose_and_mouth_are_actually_covered():
    # These are facial landmark positions, not the centre of the replacement
    # rectangle: shifting or shrinking an otherwise valid box must fail here.
    color = (25, 143, 238)
    avatar = SimpleNamespace(image=Image.new("RGB", (180, 180), color))
    checked = 0
    for item in TEMPLATES:
        with Image.open(ASSETS / "images" / item["asset"]) as source:
            for index, faces in enumerate(item["frame_faces"]):
                source.seek(index)
                points = [point for face in faces for point in face.get("feature_points", [])]
                if not points:
                    continue
                image = runtime.frame(source, [avatar], faces)
                scale = min(496 / source.width, 496 / source.height)
                width, height = round(source.width * scale), round(source.height * scale)
                left, top = (512 - width) // 2, (512 - height) // 2
                for x, y in points:
                    if not (1 < x < source.width - 1 and 1 < y < source.height - 1):
                        continue
                    px, py = (
                        round(x * width / source.width) + left,
                        round(y * height / source.height) + top,
                    )
                    actual = image.getpixel((px, py))
                    assert max(abs(a - b) for a, b in zip(actual, color)) <= 20, (
                        item["key"],
                        index,
                        (x, y),
                        actual,
                    )
                    checked += 1
    assert checked > 1000


@pytest.mark.parametrize(
    ("number", "points"),
    [
        (5, [(15, 15), (35, 15), (26, 24)]),
        (6, [(38, 44), (62, 43), (50, 55)]),
        (7, [(15, 16), (33, 16), (24, 27)]),
        (309, [(21, 19), (41, 19), (32, 26)]),
        (343, [(20, 29), (41, 29), (30, 35)]),
        (357, [(18, 25), (38, 26), (28, 34)]),
        (407, [(19, 23), (39, 23), (29, 32)]),
    ],
)
def test_cartoon_source_eye_and_mouth_landmarks(number, points):
    # Read from the original artwork on a pixel grid, independently of its mask.
    item = TEMPLATES[number - 1]
    color = (25, 143, 238)
    avatar = SimpleNamespace(image=Image.new("RGB", (100, 100), color))
    with Image.open(ASSETS / "images" / item["asset"]) as source:
        image = runtime.frame(source, [avatar], item["faces"])
        scale = min(496 / source.width, 496 / source.height)
        width, height = round(source.width * scale), round(source.height * scale)
        left, top = (512 - width) // 2, (512 - height) // 2
        for x, y in points:
            px, py = round(x * width / source.width) + left, round(y * height / source.height) + top
            assert image.getpixel((px, py)) == color


def test_outline_mask_keeps_foreground_and_covers_head_corners():
    source = Image.new("RGB", (100, 100), "white")
    source.paste("black", (10, 10, 90, 90))
    source.paste("red", (65, 55, 90, 70))
    face = {
        "box": [10, 10, 90, 90],
        "outline": [[10, 10], [90, 10], [90, 90], [10, 90]],
        "preserve": [[[65, 55], [90, 55], [90, 70], [65, 70]]],
        "angle": 25,
    }
    avatar = SimpleNamespace(image=Image.new("RGB", (100, 100), "blue"))
    image = runtime.frame(source, [avatar], [face])
    assert image.getpixel((90, 90)) == (0, 0, 255)
    assert image.getpixel((380, 310)) == (255, 0, 0)
    assert image.getpixel((20, 20)) == (255, 255, 255)


def test_wide_action_head_maps_the_whole_square_avatar_before_masking():
    source = Image.new("RGB", (100, 100), "white")
    avatar = Image.new("RGB", (80, 80), "blue")
    avatar.paste("red", (0, 70, 80, 80))
    face = {
        "box": [10, 20, 90, 60],
        "outline": [[10, 20], [90, 20], [90, 60], [10, 60]],
        "fit": "square",
    }
    image = runtime.frame(source, [SimpleNamespace(image=avatar)], [face])
    # A direct fit to the wide rectangle would crop away this bottom band.
    assert image.getpixel((256, 290)) == (255, 0, 0)
    assert image.getpixel((256, 140)) == (0, 0, 255)


def test_action_parameters_reject_text_and_extra_images(memes):
    image = BytesIO()
    Image.new("RGB", (64, 64), "blue").save(image, "PNG")
    data = image.getvalue()
    for key in ("mantou_action_001", "mantou_action_500"):
        meme = next(m for m in memes if m.key == key)
        with pytest.raises(TextNumberMismatch):
            meme(images=[data], texts=["不应绘制"])
        with pytest.raises(ImageNumberMismatch):
            meme(images=[data, data])
