"""Avatar compositing shared by the source-backed template collections."""

from io import BytesIO

from PIL import Image, ImageDraw, ImageOps


def frame(source, avatars, faces):
    canvas = Image.new("RGB", (512, 512), "white")
    source = source.convert("RGBA")
    resample = Image.Resampling.NEAREST if min(source.size) < 96 else Image.Resampling.LANCZOS
    base = ImageOps.contain(source, (496, 496), method=resample)
    left, top = (512 - base.width) // 2, (512 - base.height) // 2
    canvas.paste(base, (left, top), base)
    sx, sy = base.width / source.width, base.height / source.height
    for number, face in enumerate(faces):
        avatar = avatars[face.get("image", number)]
        x0, y0, x1, y1 = face["box"]
        x0, x1 = round(x0 * sx) + left, round(x1 * sx) + left
        y0, y1 = round(y0 * sy) + top, round(y1 * sy) + top
        size = (x1 - x0, y1 - y0)
        target = avatar.image.convert("RGBA")
        if face.get("angle", 0) or face.get("fit") == "square":
            # Rotate inside a square before mapping its inscribed circle to the
            # oval. Expanding a rotated rectangle and fitting it leaves white
            # triangles inside the face mask, especially in the rolling GIF.
            side = max(size)
            target = ImageOps.fit(target, (side, side), method=Image.Resampling.LANCZOS)
            if face.get("angle", 0):
                target = target.rotate(
                    face["angle"],
                    resample=Image.Resampling.BICUBIC,
                    fillcolor=target.getpixel((0, 0)) if face.get("outline") else None,
                )
            target = target.resize(size, Image.Resampling.LANCZOS)
        else:
            target = ImageOps.fit(target, size, method=Image.Resampling.LANCZOS)
        opaque = Image.new("RGB", size, "white")
        opaque.paste(target, (0, 0), target)
        mask = Image.new("L", (size[0] * 3, size[1] * 3))
        draw = ImageDraw.Draw(mask)
        if face.get("outline"):
            draw.polygon(
                [
                    (round((x * sx + left - x0) * 3), round((y * sy + top - y0) * 3))
                    for x, y in face["outline"]
                ],
                fill=255,
            )
        else:
            draw.ellipse((0, 0, mask.width - 1, mask.height - 1), fill=255)
        # Source coordinates keep foreground props registered as the image scales.
        for polygon in face.get("preserve", []):
            draw.polygon(
                [
                    (round((x * sx + left - x0) * 3), round((y * sy + top - y0) * 3))
                    for x, y in polygon
                ],
                fill=0,
            )
        mask = mask.resize(size, Image.Resampling.LANCZOS)
        canvas.paste(opaque, (x0, y0), mask)
    return canvas


def render(template, images, texts, args, *, root):
    output = BytesIO()
    with Image.open(root / "images" / template["asset"]) as source:
        if not template["animated"]:
            frame(source, images, template["faces"]).save(output, "PNG")
        else:
            frames, durations = [], []
            for i in range(source.n_frames):
                source.seek(i)
                faces = template.get("frame_faces", [template["faces"]] * source.n_frames)[i]
                frames.append(frame(source, images, faces))
                durations.append(source.info.get("duration", 100))
            if template.get("palette"):
                frames = [image.quantize(colors=template["palette"]) for image in frames]
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
