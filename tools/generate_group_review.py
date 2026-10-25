"""Render centered source/composite comparisons and every retained group GIF frame."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "memes/mantou_groups"
OUTPUT = ROOT / "previews/review-groups"
COLORS = [
    "#2492ed",
    "#f79528",
    "#48ba63",
    "#ac71d9",
    "#df579d",
    "#a6a922",
    "#36bfc8",
    "#db6260",
    "#8c7154",
    "#606bc9",
]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    templates = json.loads((ASSETS / "templates.json").read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location(
        "group_review_runtime", ROOT / "memes/_mantou_avatar.py"
    )
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    avatars = [SimpleNamespace(image=Image.new("RGB", (160, 160), color)) for color in COLORS]
    font = ImageFont.truetype(str(ROOT / "memes/mantou/NotoSansSC.ttf"), 15)
    for base in range(0, len(templates), 20):
        sheet = Image.new("RGB", (1600, 1200), "#ddd")
        for j, item in enumerate(templates[base : base + 20]):
            with Image.open(ASSETS / "images" / item["asset"]) as source:
                x, y = j % 4 * 400, j // 4 * 240
                sheet.paste(runtime.frame(source, [], []).resize((192, 192)), (x, y))
                sheet.paste(
                    runtime.frame(source, avatars, item["faces"]).resize((192, 192)), (x + 200, y)
                )
                ImageDraw.Draw(sheet).text(
                    (x + 3, y + 196),
                    f"{item['keywords'][0]} {item['images']}人 源{item['source_id']}",
                    font=font,
                    fill="black",
                )
        sheet.save(OUTPUT / f"faces-{base // 20 + 1:02}.jpg", quality=88)
    animated = [item for item in templates if item["animated"]]
    for base in range(0, len(animated), 10):
        sheet = Image.new("RGB", (1700, 1180), "#ddd")
        for j, item in enumerate(animated[base : base + 10]):
            y = j * 118
            with Image.open(ASSETS / "images" / item["asset"]) as source:
                sheet.paste(runtime.frame(source, [], []).resize((96, 96)), (0, y))
                ImageDraw.Draw(sheet).text(
                    (2, y + 97), item["keywords"][0], font=font, fill="black"
                )
                for k, faces in enumerate(item["frame_faces"]):
                    source.seek(k)
                    sheet.paste(
                        runtime.frame(source, avatars, faces).resize((96, 96)), (100 + k * 100, y)
                    )
                    ImageDraw.Draw(sheet).text(
                        (102 + k * 100, y + 97), str(k), font=font, fill="black"
                    )
        sheet.save(OUTPUT / f"motion-{base // 10 + 1:02}.jpg", quality=88)
    print(f"Group review: {len(templates)} templates, {len(animated)} GIFs")


if __name__ == "__main__":
    main()
