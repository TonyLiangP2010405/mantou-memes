"""Original, offline templates for MemeCrafters/meme-generator 0.1.x."""

import math
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache, partial
from io import BytesIO
from pathlib import Path

from meme_generator import add_meme
from PIL import Image, ImageDraw, ImageFont, ImageOps

INK = "#252124"
FONT_PATH = Path(__file__).with_name("NotoSansSC.ttf")
SIZE = 512


@dataclass(frozen=True)
class Template:
    key: str
    name: str
    images: int
    theme: str
    animated: bool = False


TEMPLATES = (
    Template("battery", "社交电量", 1, "情绪"),
    Template("overheat", "正在红温", 1, "情绪", True),
    Template("loading", "脑子加载中", 1, "抽象", True),
    Template("offline", "本人已下线", 1, "摆烂"),
    Template("work", "摸鱼工牌", 1, "打工"),
    Template("salary", "精神工资条", 0, "打工"),
    Template("receipt", "已读乱回小票", 0, "群聊"),
    Template("praise", "夸夸奖状", 1, "夸夸"),
    Template("grass", "头上长草", 1, "抽象"),
    Template("question", "满头问号", 1, "疑惑"),
    Template("capybara", "水豚泡汤", 1, "动物"),
    Template("cat", "猫猫探头", 1, "动物"),
    Template("bun", "蒸笼认领", 1, "馒头"),
    Template("peach", "今日桃气", 1, "桃子"),
    Template("support", "双人应援", 2, "互动"),
    Template("charge", "给你充电", 2, "互动"),
    Template("duel", "菜鸡对决", 2, "游戏"),
    Template("melon", "吃瓜席位", 1, "围观"),
    Template("sleep", "关机睡觉", 1, "晚安"),
    Template("schedule", "今日摆烂计划", 0, "摆烂"),
)


@lru_cache(maxsize=32)
def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def label(canvas, text, xy, size=40, fill=INK, width=460):
    """Fit one line, including long nicknames, within a known area."""
    text = " ".join(str(text).split())
    if len(text) > 40:
        text = text[:39] + "…"
    draw = ImageDraw.Draw(canvas)
    while size > 16 and draw.textlength(text, font=font(size)) > width:
        size -= 2
    while draw.textlength(text, font=font(size)) > width and len(text) > 1:
        text = text[:-2] + "…"
    draw.text(xy, text, font=font(size), fill=fill, anchor="mm", stroke_width=1)


def avatar(canvas, image, xy, diameter=210, gray=False, tint=None):
    source = image.image.convert("RGBA")
    source = ImageOps.fit(source, (diameter, diameter), method=Image.Resampling.LANCZOS)
    if gray:
        source = ImageOps.grayscale(source).convert("RGBA")
    if tint:
        source = Image.blend(source, Image.new("RGBA", source.size, tint), 0.38)
    mask = Image.new("L", source.size)
    ImageDraw.Draw(mask).ellipse((4, 4, diameter - 4, diameter - 4), fill=255)
    x, y = xy
    ImageDraw.Draw(canvas).ellipse((x - 3, y - 3, x + diameter + 3, y + diameter + 3), fill=INK)
    canvas.paste(source, xy, mask)


def star(draw, xy, radius, color):
    x, y = xy
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
    draw.polygon(points, fill=color)


def scene(key, images, text, tick=0):
    colors = {
        "battery": "#e7efdc",
        "overheat": "#ffe8d5",
        "loading": "#e3e8fa",
        "offline": "#dddde1",
        "work": "#eef0db",
        "salary": "#fff4da",
        "receipt": "#efe9dc",
        "praise": "#fff0cb",
        "grass": "#d8edcb",
        "question": "#f1e1fc",
        "capybara": "#e3d6bd",
        "cat": "#fbe4c8",
        "bun": "#fceacb",
        "peach": "#ffdfdd",
        "support": "#ffe0eb",
        "charge": "#deeee3",
        "duel": "#2e2948",
        "melon": "#e3f0cc",
        "sleep": "#252b4a",
        "schedule": "#eee9fa",
    }
    canvas = Image.new("RGB", (SIZE, SIZE), colors[key])
    d = ImageDraw.Draw(canvas)

    if key == "battery":
        label(canvas, "社交电量只剩", (256, 58), 40)
        d.rounded_rectangle((56, 132, 432, 343), 22, fill="#fafcf4", outline=INK, width=7)
        d.rectangle((432, 196, 453, 272), fill=INK)
        d.rounded_rectangle((68, 144, 111, 331), 12, fill="#ec6552")
        avatar(canvas, images[0], (165, 153), 168, gray=True)
        label(canvas, "1%", (256, 394), 64, "#d65343")
        label(canvas, "有事请给我发红包", (256, 463), 28)
    elif key == "overheat":
        for i in range(12):
            x = i * 47 - 20
            h = 85 + (i * 31 + tick * 23) % 130
            d.polygon([(x, 420), (x + 28, 420 - h), (x + 62, 420)], fill="#ff9650")
        avatar(canvas, images[0], (131, 130), 250, tint="#ff4433")
        label(canvas, "正在红温", (256 + (tick % 2) * 5, 66), 62, "#c82a24")
        label(canvas, "冷却系统已罢工", (256, 461), 36)
        label(canvas, f"{96 + tick % 4}°C", (414, 144), 28, "#c82a24", 150)
    elif key == "loading":
        avatar(canvas, images[0], (146, 124), 220, gray=True)
        d.arc((125, 103, 387, 365), tick * 45, tick * 45 + 240, fill="#6954bc", width=12)
        label(canvas, "脑子加载中", (256, 56), 49)
        d.rounded_rectangle((66, 399, 446, 426), 12, fill="#c5c5dc")
        d.rounded_rectangle((66, 399, 66 + 38 * (tick + 1), 426), 12, fill="#6954bc")
        label(canvas, "请勿催促，越催越卡", (256, 468), 29)
    elif key == "offline":
        avatar(canvas, images[0], (136, 89), 240, gray=True)
        d.line((108, 332, 404, 91), fill="#eb615b", width=18)
        label(canvas, "本人已下线", (256, 394), 54)
        label(canvas, "回复靠缘分", (256, 461), 30)
    elif key == "work":
        d.rounded_rectangle((65, 56, 447, 468), 24, fill="#fffdf7", outline=INK, width=5)
        d.rounded_rectangle((209, 35, 303, 80), 10, fill=INK)
        label(canvas, "群聊摸鱼部", (256, 113), 36)
        avatar(canvas, images[0], (166, 157), 180)
        label(canvas, "首席摸鱼官", (256, 387), 41)
        label(canvas, "在岗状态：灵魂出走", (256, 439), 23)
    elif key == "salary":
        label(canvas, "精神工资条", (256, 61), 52)
        label(canvas, text, (256, 117), 30)
        rows = [
            ("基本情绪", "+ 100"),
            ("上班消耗", "- 99"),
            ("群聊回血", "+ 1"),
            ("实发能量", "2 格"),
        ]
        for i, (name, value) in enumerate(rows):
            y = 191 + i * 67
            d.line((44, y + 33, 468, y + 33), fill="#c9b994", width=2)
            label(canvas, name, (151, y), 29, width=210)
            label(canvas, value, (367, y), 31, width=170)
        label(canvas, "已到账：一点点快乐", (256, 475), 26)
    elif key == "receipt":
        d.rectangle((70, 23, 442, 488), fill="#fffcf1")
        for x in range(70, 442, 20):
            d.polygon([(x, 488), (x + 10, 475), (x + 20, 488)], fill=colors[key])
        label(canvas, "群聊结算小票", (256, 69), 36, width=340)
        label(canvas, text, (256, 121), 28, width=320)
        for i, line in enumerate(
            [
                "消息已读              × 1",
                "脑子理解              × 0",
                "认真回复              × 0",
                "哈哈哈哈              × 99",
            ]
        ):
            label(canvas, line, (256, 190 + i * 45), 25, width=328)
        d.line((93, 357, 419, 357), fill=INK, width=3)
        label(canvas, "合计：已读乱回", (256, 400), 33, width=330)
        for i in range(60):
            x = 111 + i * 5
            if i % 7 in (0, 1, 3, 6):
                d.rectangle((x, 440, x + 2, 462), fill=INK)
    elif key == "praise":
        d.rectangle((18, 18, 494, 494), outline="#bd8634", width=8)
        d.rectangle((31, 31, 481, 481), outline="#bd8634", width=2)
        label(canvas, "夸 夸 奖 状", (256, 80), 52)
        avatar(canvas, images[0], (158, 137), 196)
        for x in (84, 428):
            star(d, (x, 234), 34, "#e6ac32")
        label(canvas, "你怎么这么会啊", (256, 385), 42)
        label(canvas, "群聊特别贡献奖", (256, 449), 26, "#986929")
    elif key == "grass":
        avatar(canvas, images[0], (126, 168), 260)
        for x, h in [(220, 105), (258, 133), (290, 92)]:
            d.line((256, 180, x, h), fill="#397a40", width=10)
            d.ellipse((x - 29, h - 17, x + 6, h + 4), fill="#579b4d")
            d.ellipse((x, h - 24, x + 33, h - 3), fill="#6cab4a")
        label(canvas, "沉默，但长草", (256, 465), 42)
    elif key == "question":
        avatar(canvas, images[0], (146, 160), 220)
        for x, y, size in [(70, 163, 82), (180, 82, 96), (340, 83, 87), (438, 190, 100)]:
            label(canvas, "?", (x, y), size, "#8053a0", 100)
        label(canvas, "你要不要听听", (256, 422), 39)
        label(canvas, "你在说什么", (256, 473), 39)
    elif key == "capybara":
        d.ellipse((44, 279, 468, 444), fill="#9fc5b4", outline=INK, width=5)
        d.rounded_rectangle((130, 139, 383, 370), 80, fill="#ae855d", outline=INK, width=5)
        d.ellipse((137, 120, 190, 174), fill="#ae855d", outline=INK, width=4)
        d.ellipse((324, 120, 377, 174), fill="#ae855d", outline=INK, width=4)
        avatar(canvas, images[0], (167, 175), 178)
        d.ellipse((222, 88, 290, 151), fill="#f1a039", outline=INK, width=3)
        d.ellipse((254, 76, 287, 96), fill="#658148")
        for x in (99, 381):
            d.arc((x, 204, x + 29, 277), 70, 270, fill="#fff8e9", width=6)
        label(canvas, "问题不大", (256, 41), 43)
        label(canvas, "先泡个汤再说", (256, 471), 38)
    elif key == "cat":
        d.polygon([(115, 214), (123, 76), (229, 168)], fill="#dba467", outline=INK, width=5)
        d.polygon([(283, 168), (389, 76), (398, 214)], fill="#dba467", outline=INK, width=5)
        avatar(canvas, images[0], (126, 133), 260)
        for side in (-1, 1):
            for y in (258, 281, 304):
                x = 256 + side * 130
                d.line((x, y, x + side * 52, y - 12), fill=INK, width=4)
        d.rectangle((0, 367, 512, 512), fill="#bd8c60")
        d.line((0, 367, 512, 367), fill=INK, width=5)
        for x in (128, 319):
            d.rounded_rectangle((x, 342, x + 66, 399), 20, fill="#f1d0a0", outline=INK, width=4)
        label(canvas, "让我看看谁在摸鱼", (256, 451), 36)
    elif key == "bun":
        d.ellipse((42, 247, 470, 449), fill="#c79557", outline=INK, width=5)
        d.ellipse((42, 235, 470, 396), fill="#e6bc81", outline=INK, width=5)
        avatar(canvas, images[0], (141, 142), 230)
        for x in (105, 243, 381):
            d.arc((x, 52, x + 32, 139), 65, 270, fill="#ba9c7a", width=6)
        label(canvas, "出锅啦！", (256, 47), 43)
        label(canvas, "这只馒头有人认领吗", (256, 472), 36)
    elif key == "peach":
        d.ellipse((65, 120, 306, 386), fill="#f49ba9", outline="#b75b6b", width=5)
        d.ellipse((205, 120, 446, 386), fill="#f49ba9", outline="#b75b6b", width=5)
        d.polygon([(112, 282), (256, 420), (400, 282)], fill="#f49ba9")
        d.ellipse((256, 60, 369, 116), fill="#7f9d62")
        avatar(canvas, images[0], (157, 177), 198)
        label(canvas, "今日桃气超标", (256, 462), 45)
        label(canvas, "+ 100%", (256, 144), 29, "#a13752")
    elif key in {"support", "charge", "duel"}:
        dark = key == "duel"
        color = "#fff7dc" if dark else INK
        title = {"support": "今天也站你这边", "charge": "给你充一点电", "duel": "菜 鸡 对 决"}[key]
        label(canvas, title, (256, 65), 45, color)
        avatar(canvas, images[0], (31, 164), 182)
        avatar(canvas, images[1], (299, 164), 182)
        if key == "support":
            d.polygon(
                [
                    (245, 211),
                    (228, 195),
                    (212, 211),
                    (215, 230),
                    (256, 269),
                    (297, 230),
                    (300, 211),
                    (284, 195),
                    (267, 211),
                    (256, 226),
                ],
                fill="#de6286",
            )
            footer = "你负责闪闪发光"
        elif key == "charge":
            d.line((214, 255, 299, 255), fill="#5a9b6d", width=12)
            d.polygon(
                [
                    (247, 218),
                    (235, 263),
                    (255, 263),
                    (245, 295),
                    (280, 247),
                    (258, 247),
                    (270, 218),
                ],
                fill="#e8b64d",
            )
            footer = "累了就靠一会儿"
        else:
            label(canvas, "VS", (256, 247), 46, "#ffc857", 78)
            footer = "主打一个势均力敌"
        label(canvas, footer, (256, 420), 37, color)
        label(canvas, "馒头 × 群友", (256, 475), 23, color)
    elif key == "melon":
        avatar(canvas, images[0], (143, 91), 226)
        d.pieslice((67, 192, 445, 432), 0, 180, fill="#4a9a5e", outline=INK, width=4)
        d.pieslice((85, 202, 427, 410), 0, 180, fill="#ed766d")
        for x, y in [(161, 335), (223, 365), (282, 365), (352, 335)]:
            d.ellipse((x, y, x + 8, y + 15), fill=INK)
        label(canvas, "吃瓜专座", (256, 42), 46)
        label(canvas, "我先坐下，你们继续", (256, 473), 32)
    elif key == "sleep":
        for x, y in [(51, 63), (432, 100), (363, 41), (81, 300), (459, 336)]:
            star(d, (x, y), 10, "#f5dc8e")
        avatar(canvas, images[0], (141, 123), 230, gray=True)
        d.rounded_rectangle((69, 300, 443, 426), 24, fill="#8a91bb")
        d.line((69, 328, 443, 328), fill="#c0c5df", width=5)
        label(canvas, "Z z z", (343, 92), 36, "#f5dc8e", 150)
        label(canvas, "今日营业结束", (256, 468), 42, "#f9eacb")
    elif key == "schedule":
        label(canvas, "今日摆烂计划", (256, 66), 48)
        label(canvas, text, (256, 121), 29)
        for i, line in enumerate(["上午：缓缓", "中午：吃点", "下午：再缓缓", "晚上：明天一定"]):
            y = 196 + i * 73
            d.rounded_rectangle((47, y - 20, 83, y + 16), 6, outline="#7b6c98", width=3)
            d.line((54, y - 3, 63, y + 7, 77, y - 11), fill="#7b6c98", width=4)
            label(canvas, line, (283, y), 33, width=345)
    return canvas


def render(template, images, texts, args):
    text = texts[0] if texts else "群友"
    output = BytesIO()
    if template.animated:
        frames = [scene(template.key, images, text, tick) for tick in range(8)]
        frames[0].save(
            output,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=130,
            loop=0,
            disposal=2,
        )
    else:
        scene(template.key, images, text).save(output, format="PNG")
    output.seek(0)
    return output


for template in TEMPLATES:
    add_meme(
        "mantou_" + template.key,
        partial(render, template),
        min_images=template.images,
        max_images=template.images,
        min_texts=0 if template.images else 1,
        max_texts=0 if template.images else 1,
        default_texts=[] if template.images else ["群友"],
        keywords=["馒头" + template.name],
        tags={"mantou-memes", template.theme, "动图" if template.animated else "静态"},
        date_created=datetime(2026, 10, 23),
        date_modified=datetime(2026, 10, 23),
    )
