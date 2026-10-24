"""Run: python tools/generate_previews.py (no network or user config changes)."""

import json
import math
from io import BytesIO
from pathlib import Path

from isolated_backend import load_backend
from PIL import Image, ImageDraw, ImageFont, ImageSequence

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
    memes = sorted(
        backend.get_memes(),
        key=lambda m: (
            2
            if m.key.startswith("mantou_action_")
            else 0
            if m.key.startswith("mantou_duel_")
            else 1,
            m.key,
        ),
    )
    if len(memes) != 620:
        raise RuntimeError(f"Expected 620 templates, got {len(memes)}")
    avatars = [example_avatar("#8cbbb2"), example_avatar("#f4bd9b", True)]
    output = ROOT / "previews"
    output.mkdir(exist_ok=True)
    sheets = [
        Image.new("RGB", (1280, 5 * 300), "#f4f1e9") for _ in range(math.ceil(len(memes) / 20))
    ]
    font = ImageFont.truetype(str(ROOT / "memes/mantou/NotoSansSC.ttf"), 20)
    rows = []
    for index, meme in enumerate(memes):
        count = meme.params_type.min_images
        images = avatars[1:] if count == 1 else avatars[:count]
        data = meme(images=images, texts=[] if count else ["馒头群友"]).getvalue()
        image = Image.open(BytesIO(data))
        suffix = ".gif" if image.format == "GIF" else ".png"
        path = output / (meme.key + suffix)
        if meme.key.startswith("mantou_action_"):
            if suffix == ".gif":
                frames, durations = [], []
                for frame in ImageSequence.Iterator(image):
                    durations.append(frame.info.get("duration", 100))
                    frames.append(frame.convert("RGB").resize((192, 192)).quantize(colors=128))
                frames[0].save(
                    path,
                    "GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0,
                    disposal=2,
                )
                image.seek(0)
            else:
                image.resize((192, 192)).save(path, "PNG")
        else:
            path.write_bytes(data)
        sheet = sheets[index // 20]
        slot = index % 20
        x, y = (slot % 4) * 320, (slot // 4) * 300
        sheet.paste(image.convert("RGB").resize((256, 256)), (x + 32, y))
        ImageDraw.Draw(sheet).text(
            (x + 160, y + 275), meme.keywords[0], font=font, fill="#252124", anchor="mm"
        )
        input_name = f"{count} 张头像" if count else "1 段文字"
        rows.append(
            f"| {meme.keywords[0]} / `{meme.key}` | {input_name} | ![{meme.key}]({path.relative_to(ROOT).as_posix()}) |"
        )
    for i, sheet in enumerate(sheets, 1):
        sheet.save(output / f"overview-{i:02d}.jpg", quality=90)
    sheets[0].save(output / "overview.jpg", quality=90)
    links = " · ".join(
        f"[预览 {i}](previews/overview-{i:02d}.jpg)" for i in range(1, len(sheets) + 1)
    )
    table = "| 模板 | 输入 | 预览 |\n|---|---|---|\n"
    sections = []
    for i in range(0, len(rows), 20):
        sections.append(f"## 第 {i // 20 + 1} 页\n\n" + table + "\n".join(rows[i : i + 20]))
    (ROOT / "CATALOG.md").write_text(
        "# 620 个模板预览\n\n" + links + "\n\n" + "\n\n".join(sections) + "\n", encoding="utf-8"
    )
    (ROOT / "DUEL_CATALOG.md").write_text(
        "# 新增 100 个换头像模板\n\n98 个单头像、2 个双头像模板，均使用不同网络底图裁切制作，不接受文字输入，不叠加昵称或文案。\n\n"
        + " · ".join(f"[预览 {i}](previews/overview-{i:02d}.jpg)" for i in range(1, 6))
        + "\n\n"
        + "\n\n".join(sections[:5])
        + "\n",
        encoding="utf-8",
    )
    definitions = json.loads(
        (ROOT / "memes/mantou_duel/templates.json").read_text(encoding="utf-8")
    )
    actions = json.loads((ROOT / "memes/mantou_actions/templates.json").read_text(encoding="utf-8"))
    animated = sum(item["animated"] for item in actions)
    (ROOT / "ACTIONS_CATALOG.md").write_text(
        f"# 新增 500 个换头像模板\n\n{animated} 个循环 GIF、{500 - animated} 个 PNG。每个模板只接受 1 张头像，不接受文字输入。\n\n"
        + " · ".join(
            f"[预览 {i}](previews/overview-{i:02d}.jpg)" for i in range(7, len(sheets) + 1)
        )
        + "\n\n"
        + "\n\n".join(sections[6:])
        + "\n",
        encoding="utf-8",
    )
    sources = [
        "# 网络底图来源与裁切记录",
        "",
        "本批素材来自 [ChineseBQB](https://github.com/zhaoolee/ChineseBQB) 的公开图集。代码与本项目新增文案采用 MIT；网络底图权利仍归相应原作者，不因本项目代码许可证而变更。采集库未逐张提供独立授权信息，本项目不将这些底图标记为原创或 MIT 素材。",
        "",
        "链接固定到上游提交，像素裁切矩形为 `[左, 上, 右, 下]`。原图旧字幕通过裁切或清理文字区域去除；头像区域、旋转角度、逐帧位置、源图和裁切图 SHA256 分别记录在 `memes/mantou_duel/templates.json` 与 `memes/mantou_actions/templates.json` 中。运行时不绘制文字。原 100 个模板最多保留 16 帧，新 500 个模板最多保留 12 帧，等间隔采样时合并原帧时长。仅字幕或水印闪动的素材不计入动作 GIF。",
        "",
        "| 模板 | 原图 | 原始尺寸 | 裁切矩形 |",
        "|---|---|---|---|",
    ]
    for item in definitions + actions:
        sources.append(
            f"| `{item['key']}` {item['name']} | [来源]({item['source_url']}) | {item['source_size']} | {item['crop']} |"
        )
    (ROOT / "ASSET_SOURCES.md").write_text("\n".join(sources) + "\n", encoding="utf-8")
    print(
        f"Generated {len(memes)} previews, {len(sheets)} contact sheets, catalogs and source records"
    )


if __name__ == "__main__":
    main()
