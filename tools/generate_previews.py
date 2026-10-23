"""Run: python tools/generate_previews.py (no network or user config changes)."""

from io import BytesIO
from pathlib import Path

from isolated_backend import load_backend
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def example_avatar(color, ears=False):
    image = Image.new("RGB", (300, 300), color)
    draw = ImageDraw.Draw(image)
    if ears:
        draw.polygon([(64, 118), (50, 30), (125, 80)], fill="#fff1d5", outline="#453b37")
        draw.polygon([(175, 80), (250, 30), (236, 118)], fill="#fff1d5", outline="#453b37")
    draw.ellipse((48, 60, 252, 265), fill="#fff1d5", outline="#453b37", width=5)
    for x in (107, 185):
        draw.ellipse((x, 143, x + 10, 156), fill="#453b37")
    draw.arc((130, 153, 170, 190), 0, 180, fill="#453b37", width=4)
    for x in (78, 202):
        draw.ellipse((x, 171, x + 23, 185), fill="#e9aaa1")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def main():
    backend = load_backend()
    backend.load_memes(ROOT / "memes")
    memes = backend.get_memes()
    if len(memes) != 20:
        raise RuntimeError(f"Expected 20 templates, got {len(memes)}")
    avatars = [example_avatar("#8cbbb2"), example_avatar("#f4bd9b", True)]
    output = ROOT / "previews"
    output.mkdir(exist_ok=True)
    sheet = Image.new("RGB", (1280, 5 * 300), "#f4f1e9")
    font = ImageFont.truetype(str(ROOT / "memes/mantou/NotoSansSC.ttf"), 20)
    rows = ["| 模板 | 输入 | 预览 |", "|---|---|---|"]
    for index, meme in enumerate(memes):
        count = meme.params_type.min_images
        images = avatars[1:] if count == 1 else avatars[:count]
        data = meme(images=images, texts=[] if count else ["馒头群友"]).getvalue()
        image = Image.open(BytesIO(data))
        suffix = ".gif" if image.format == "GIF" else ".png"
        path = output / (meme.key + suffix)
        path.write_bytes(data)
        x, y = (index % 4) * 320, (index // 4) * 300
        sheet.paste(image.convert("RGB").resize((256, 256)), (x + 32, y))
        ImageDraw.Draw(sheet).text(
            (x + 160, y + 275), meme.keywords[0], font=font, fill="#252124", anchor="mm"
        )
        input_name = f"{count} 张头像" if count else "1 段文字"
        rows.append(
            f"| {meme.keywords[0]} / `{meme.key}` | {input_name} | ![{meme.key}]({path.relative_to(ROOT).as_posix()}) |"
        )
    sheet.save(output / "overview.jpg", quality=90)
    (ROOT / "CATALOG.md").write_text("# 模板预览\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"Generated {len(memes)} previews and overview.jpg")


if __name__ == "__main__":
    main()
