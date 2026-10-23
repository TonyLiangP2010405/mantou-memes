from io import BytesIO

import pytest
from meme_generator.exception import ImageNumberMismatch, OpenImageFailed, TextNumberMismatch
from PIL import Image, ImageDraw


def picture(color, format="PNG", mode="RGB", size=(320, 240)):
    image = Image.new(mode, size, color)
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 30, 110, 110), fill="white")
    output = BytesIO()
    image.save(output, format=format)
    return output.getvalue()


def test_all_templates_registered_and_compatible(memes):
    assert len(memes) == 120
    assert len({m.key for m in memes}) == 120
    assert sum(m.key.startswith("mantou_duel_") for m in memes) == 100
    for meme in memes:
        p = meme.params_type
        assert p.min_images == p.max_images in (0, 1, 2)
        assert (p.min_texts, p.max_texts) == ((0, 0) if p.min_images else (1, 1))
        assert meme.key.startswith("mantou_")
        assert "mantou-memes" in meme.tags
        assert meme.keywords


@pytest.mark.parametrize("kind", ["standard", "transparent", "portrait", "tiny", "jpeg"])
def test_real_backend_renders_every_template(memes, kind):
    samples = {
        "standard": lambda: picture("#68b9bd"),
        "transparent": lambda: picture((120, 30, 80, 0), mode="RGBA"),
        "portrait": lambda: picture("#df9866", size=(160, 720)),
        "tiny": lambda: picture("#a4bc59", size=(1, 1)),
        "jpeg": lambda: picture("#d5a3bc", format="JPEG"),
    }
    for meme in memes:
        if kind != "standard" and not meme.params_type.min_images:
            continue
        result = meme(
            images=[samples[kind]() for _ in range(meme.params_type.min_images)],
            texts=["馒头群友"] if meme.params_type.min_texts else [],
            args={},
        )
        data = result.getvalue()
        assert len(data) < 2_000_000, meme.key
        with Image.open(BytesIO(data)) as image:
            assert image.size == (512, 512), meme.key
            if "动图" in meme.tags:
                assert image.format == "GIF" and 2 <= image.n_frames <= 16
                assert image.info["loop"] == 0
                image.seek(image.n_frames - 1)
                image.load()
            else:
                assert image.format == "PNG" and image.n_frames == 1
                image.load()


def test_double_templates_preserve_input_order(memes):
    for meme in [
        m for m in memes if m.params_type.min_images == 2 and not m.key.startswith("mantou_duel_")
    ]:
        red, blue = picture("red"), picture("blue")
        output = meme(images=[red, blue])
        image = Image.open(output).convert("RGB")
        assert image.getpixel((122, 300))[0] > 200
        assert image.getpixel((390, 300))[2] > 200


@pytest.mark.parametrize("text", ["", "我是一个很长的群昵称" * 50, "hello\nworld\t你好", "😀🐱​"])
def test_text_inputs_do_not_overflow_or_crash(memes, text):
    for meme in [m for m in memes if m.params_type.min_images == 0]:
        with Image.open(meme(texts=[text])) as image:
            image.load()
            assert image.size == (512, 512)


def test_bad_inputs_are_rejected_by_upstream(memes):
    single = next(m for m in memes if m.params_type.min_images == 1)
    with pytest.raises(ImageNumberMismatch):
        single(images=[])
    with pytest.raises(OpenImageFailed):
        single(images=[b"broken"])
    text = next(m for m in memes if m.params_type.min_texts == 1)
    with pytest.raises(TextNumberMismatch):
        text(texts=[])
