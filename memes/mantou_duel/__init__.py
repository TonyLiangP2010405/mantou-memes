"""Cropped internet reaction images with personalized, replaceable captions."""

import json
from datetime import datetime
from functools import lru_cache, partial
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).parent
FONT = ROOT.parent / "mantou" / "NotoSansSC.ttf"
TEMPLATES = json.loads((ROOT / "templates.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=24)
def font(size):
    return ImageFont.truetype(str(FONT), size)


def frame(source, caption):
    canvas = Image.new("RGB", (512, 512), "white")
    source = source.convert("RGBA")
    resample = Image.Resampling.NEAREST if min(source.size) < 96 else Image.Resampling.LANCZOS
    source = ImageOps.contain(source, (480, 366), method=resample)
    canvas.paste(source, ((512 - source.width) // 2, (380 - source.height) // 2), source)
    lines = caption.splitlines()
    draw = ImageDraw.Draw(canvas)
    size = 36
    while size > 16 and max(draw.textlength(line, font=font(size)) for line in lines) > 462:
        size -= 2
    for i, line in enumerate(lines):
        draw.text(
            (256, 442 + (i - (len(lines) - 1) / 2) * (size + 12)),
            line,
            font=font(size),
            fill="#161616",
            anchor="mm",
            stroke_width=1,
        )
    return canvas


def render(template, images, texts, args):
    name = " ".join(texts[0].split()) or "群友"
    if len(name) > 20:
        name = name[:19] + "…"
    caption = template["caption"].replace("{name}，", name + "，\n")
    output = BytesIO()
    with Image.open(ROOT / "images" / template["asset"]) as source:
        if not template["animated"]:
            frame(source, caption).save(output, "PNG")
        else:
            frames, durations = [], []
            for i in range(source.n_frames):
                source.seek(i)
                frames.append(frame(source, caption))
                durations.append(source.info.get("duration", 100))
            frames[0].save(
                output,
                "GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                disposal=2,
            )
    output.seek(0)
    return output


for template in TEMPLATES:
    add_meme(
        template["key"],
        partial(render, template),
        min_images=0,
        max_images=0,
        min_texts=1,
        max_texts=1,
        default_texts=["群友"],
        keywords=["馒头对线" + template["name"]],
        tags={
            "mantou-memes",
            "对线",
            template["category"],
            "动图" if template["animated"] else "静态",
        },
        date_created=datetime(2026, 10, 23),
        date_modified=datetime(2026, 10, 23),
    )
