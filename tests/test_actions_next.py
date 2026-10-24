import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "memes/mantou_actions_next"
TEMPLATES = json.loads((ASSETS / "templates.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location(
    "avatar_test_runtime", ROOT / "memes/_mantou_avatar.py"
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_five_hundred_distinct_source_backed_image_only_actions(memes):
    registered = {m.key: m for m in memes}
    previous = json.loads((ROOT / "memes/mantou_duel/templates.json").read_text(encoding="utf-8"))
    previous += json.loads(
        (ROOT / "memes/mantou_actions/templates.json").read_text(encoding="utf-8")
    )
    old_hashes = {r["source_sha256"] for r in previous}
    assert len(TEMPLATES) == 500
    assert len({r["source_sha256"] for r in TEMPLATES}) == 500
    assert len({r["asset_sha256"] for r in TEMPLATES}) == 500
    assert {r["source_sha256"] for r in TEMPLATES}.isdisjoint(old_hashes)
    for number, item in enumerate(TEMPLATES, 501):
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
                    assert -180 <= face["angle"] <= 180
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


def test_independently_reviewed_cartoon_and_animal_source_landmarks():
    color = (25, 143, 238)
    avatar = SimpleNamespace(image=Image.new("RGB", (180, 180), color))
    checked = 0
    for item in TEMPLATES:
        points = item.get("qa_source_landmarks", [])
        if not points:
            continue
        with Image.open(ASSETS / "images" / item["asset"]) as source:
            image = runtime.frame(source, [avatar], item["faces"])
            scale = min(496 / source.width, 496 / source.height)
            width, height = round(source.width * scale), round(source.height * scale)
            left, top = (512 - width) // 2, (512 - height) // 2
            for x, y in points:
                px, py = (
                    round(x * width / source.width) + left,
                    round(y * height / source.height) + top,
                )
                actual = image.getpixel((px, py))
                assert max(abs(a - b) for a, b in zip(actual, color)) <= 25, (
                    item["key"],
                    item["source_id"],
                    (x, y),
                    actual,
                )
                checked += 1
    assert checked >= 80


def test_foreground_desk_and_rail_stay_in_front_of_avatar_in_every_frame():
    avatar = SimpleNamespace(image=Image.new("RGB", (180, 180), "blue"))
    for source_id, point in [(443, (160, 235)), (479, (113, 85)), (7043, (104, 159))]:
        item = next(t for t in TEMPLATES if t["source_id"] == source_id)
        with Image.open(ASSETS / "images" / item["asset"]) as source:
            for index, faces in enumerate(item["frame_faces"]):
                source.seek(index)
                scale = min(496 / source.width, 496 / source.height)
                width, height = round(source.width * scale), round(source.height * scale)
                left, top = (512 - width) // 2, (512 - height) // 2
                px, py = (
                    round(point[0] * width / source.width) + left,
                    round(point[1] * height / source.height) + top,
                )
                actual = runtime.frame(source, [avatar], faces).getpixel((px, py))
                original = runtime.frame(source, [], []).getpixel((px, py))
                assert actual == original, (item["key"], index)
