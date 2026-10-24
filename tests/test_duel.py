import hashlib
import json
import math
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
                    for polygon in face.get("preserve", []):
                        assert len(polygon) >= 3
                        assert all(
                            0 <= x <= image.width and 0 <= y <= image.height for x, y in polygon
                        ), template["key"]
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


# Pixel landmarks were read from the source pictures, independently of face boxes.
# These catch shifted boxes that would pass a test sampling only their own centres.
@pytest.mark.parametrize(
    "number,index,covered,unchanged",
    [
        (15, 0, [(340, 171), (425, 192), (382, 287)], [(349, 448)]),
        (34, 0, [(137, 34), (174, 36), (153, 84)], [(153, 125)]),
        (45, 0, [(75, 85), (103, 90), (82, 126), (329, 80), (356, 85), (341, 123)], []),
        (48, 0, [(46, 28), (56, 29), (48, 38), (132, 27), (140, 29), (135, 38)], [(139, 70)]),
        (51, 0, [(22, 24), (43, 24), (33, 32)], [(57, 28)]),
        (56, 0, [(140, 178), (279, 180), (232, 247)], [(246, 292)]),
        (58, 0, [(165, 80), (261, 80), (211, 120)], [(217, 226)]),
        (63, 0, [(155, 176), (272, 179), (231, 236)], [(201, 333)]),
        (65, 0, [(145, 177), (279, 178), (225, 250)], [(200, 130)]),
        (66, 0, [(142, 179), (278, 179), (225, 235)], [(210, 350)]),
        (67, 0, [(144, 176), (279, 175), (218, 225)], [(210, 350)]),
        (69, 0, [(124, 95), (195, 98), (167, 118)], [(135, 100)]),
        (74, 0, [(13, 30), (33, 30), (23, 21)], [(24, 4)]),
        (77, 0, [(807, 241), (816, 334)], [(600, 100)]),
        (83, 0, [(49, 30), (56, 32), (54, 40)], [(35, 10)]),
        (84, 0, [(97, 80), (112, 78), (107, 99)], [(108, 130)]),
        (86, 0, [(132, 164), (245, 138), (216, 196), (213, 272)], [(328, 185)]),
        (88, 0, [(399, 219), (438, 229), (433, 272)], [(401, 162)]),
        (97, 1, [(154, 130), (171, 141)], [(184, 186)]),
        (98, 4, [(190, 128), (116, 159)], [(154, 241)]),
        (98, 5, [(156, 194), (160, 235)], [(27, 90)]),
        (99, 0, [(112, 108), (130, 116), (120, 142)], [(66, 95)]),
    ],
)
def test_source_face_features_are_replaced_and_props_stay_visible(
    memes, number, index, covered, unchanged
):
    key = f"mantou_duel_{number:03}"
    template = TEMPLATES[key]
    meme = next(m for m in memes if m.key == key)
    with Image.open(ROOT / "images" / template["asset"]) as source:
        source.seek(index)
        resample = Image.Resampling.NEAREST if min(source.size) < 96 else Image.Resampling.LANCZOS
        base = ImageOps.contain(source.convert("RGBA"), (496, 496), method=resample)
        left, top = (512 - base.width) // 2, (512 - base.height) // 2
        sx, sy = base.width / source.width, base.height / source.height
        baseline = Image.new("RGB", (512, 512), "white")
        baseline.paste(base, (left, top), base)
    result = meme(images=[picture("blue")] * template["images"]).getvalue()
    with Image.open(BytesIO(result)) as output:
        output.seek(index)
        rendered = output.convert("RGB")
        for x, y in covered:
            pixel = (round(x * sx) + left, round(y * sy) + top)
            r, g, b = rendered.getpixel(pixel)
            assert b > 220 and r < 35 and g < 35, (key, index, (x, y), (r, g, b))
        for x, y in unchanged:
            pixel = (round(x * sx) + left, round(y * sy) + top)
            actual, expected = rendered.getpixel(pixel), baseline.getpixel(pixel)
            assert max(abs(a - b) for a, b in zip(actual, expected)) < 35, (
                key,
                index,
                (x, y),
                actual,
                expected,
            )


def test_rotating_avatar_fills_the_whole_face_without_white_triangles(memes):
    template = TEMPLATES["mantou_duel_097"]
    meme = next(m for m in memes if m.key == template["key"])
    with Image.open(ROOT / "images" / template["asset"]) as source:
        contained = ImageOps.contain(source, (496, 496))
        sx, sy = contained.width / source.width, contained.height / source.height
        left, top = (512 - contained.width) // 2, (512 - contained.height) // 2
    with Image.open(BytesIO(meme(images=[picture("blue")]).getvalue())) as output:
        for index, faces in enumerate(template["frame_faces"]):
            output.seek(index)
            rendered = output.convert("RGB")
            x0, y0, x1, y1 = faces[0]["box"]
            for step in range(32):
                angle = step * math.tau / 32
                x = (x0 + x1) / 2 + (x1 - x0) * 0.42 * math.cos(angle)
                y = (y0 + y1) / 2 + (y1 - y0) * 0.42 * math.sin(angle)
                color = rendered.getpixel((round(x * sx) + left, round(y * sy) + top))
                assert color[2] > 220 and max(color[:2]) < 35, (index, step, color)
