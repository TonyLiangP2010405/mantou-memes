import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from meme_generator.exception import ImageNumberMismatch, TextNumberMismatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "memes/mantou_groups"
TEMPLATES = json.loads((ASSETS / "templates.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location(
    "group_avatar_runtime", ROOT / "memes/_mantou_avatar.py"
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
COLORS = [
    (36, 146, 237),
    (247, 149, 40),
    (72, 186, 99),
    (172, 113, 217),
    (223, 87, 157),
    (166, 169, 34),
    (54, 191, 200),
    (219, 98, 96),
    (140, 113, 84),
    (96, 107, 201),
]
AVATARS = [SimpleNamespace(image=Image.new("RGB", (160, 160), color)) for color in COLORS]


def test_five_hundred_new_distinct_dual_and_group_templates(memes):
    registered = {m.key: m for m in memes}
    old = []
    for module in ["mantou_duel", "mantou_actions", "mantou_actions_next"]:
        old.extend(
            json.loads((ROOT / "memes" / module / "templates.json").read_text(encoding="utf-8"))
        )
    assert len(TEMPLATES) == 500
    for field in ["source_sha256", "asset_sha256", "composite_sequence_sha256"]:
        assert len({r[field] for r in TEMPLATES}) == 500, field
    assert {r["source_sha256"] for r in TEMPLATES}.isdisjoint({r["source_sha256"] for r in old})
    assert sum(r["animated"] for r in TEMPLATES) > 400
    assert sum(r["images"] > 2 for r in TEMPLATES) >= 100
    for number, item in enumerate(TEMPLATES, 1):
        assert item["key"] == f"mantou_group_{number:03}"
        assert 2 <= item["images"] <= 10
        params = registered[item["key"]].params_type
        assert params.min_images == params.max_images == item["images"]
        assert params.min_texts == params.max_texts == 0
        assert item["source_commit"] in item["source_url"]
        asset = ASSETS / "images" / item["asset"]
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == item["asset_sha256"]
        with Image.open(asset) as image:
            assert list(image.size) == item["asset_size"]
            assert image.n_frames == len(item["frame_faces"]) == len(item["source_sample_indices"])
            assert item["faces"] == item["frame_faces"][0]
            assert image.format == ("GIF" if item["animated"] else "PNG")
            if item["animated"]:
                assert item["source_frames"] >= 2 and 2 <= image.n_frames <= 16
                assert item["composite_distinct_frames"] >= 2
                assert item["motion_fraction"] >= 0.001
            first_order = [f["image"] for f in item["faces"]]
            assert sorted(first_order) == list(range(item["images"]))
            for faces in item["frame_faces"]:
                assert [f["image"] for f in faces] == first_order
                for face in faces:
                    x0, y0, x1, y1 = face["box"]
                    assert 0 <= x0 < x1 <= image.width
                    assert 0 <= y0 < y1 <= image.height
                    assert -180 <= face["angle"] <= 180


def test_reviewed_source_features_receive_the_correct_actor_avatar():
    checked = 0
    for item in TEMPLATES:
        if not item.get("qa_source_features"):
            continue
        with Image.open(ASSETS / "images" / item["asset"]) as source:
            for frame_id, points in item["qa_source_features"].items():
                source.seek(int(frame_id))
                result = runtime.frame(source, AVATARS, item["frame_faces"][int(frame_id)])
                scale = min(496 / source.width, 496 / source.height)
                w, h = round(source.width * scale), round(source.height * scale)
                left, top = (512 - w) // 2, (512 - h) // 2
                for actor, x, y in points:
                    actual = result.getpixel(
                        (round(x * w / source.width) + left, round(y * h / source.height) + top)
                    )
                    assert max(abs(a - b) for a, b in zip(actual, COLORS[actor])) <= 25, (
                        item["source_id"],
                        frame_id,
                        actor,
                        x,
                        y,
                    )
                    checked += 1
    assert checked >= 90


def test_group_templates_reject_text_and_incorrect_avatar_counts(memes):
    registered = {m.key: m for m in memes}
    for item in TEMPLATES:
        with pytest.raises(TextNumberMismatch):
            registered[item["key"]](images=[b"unused"] * item["images"], texts=["不加文字"])
    for count in [2, 3, 10]:
        item = next(r for r in TEMPLATES if r["images"] == count)
        for incorrect in [count - 1, count + 1]:
            with pytest.raises(ImageNumberMismatch):
                registered[item["key"]](images=[b"unused"] * incorrect)
