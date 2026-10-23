"""Reproduce the reviewed crops; downloads occur only when explicitly running this tool."""

import argparse
import hashlib
import json
import ssl
import tempfile
import urllib.request
from pathlib import Path

import certifi
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "memes" / "mantou_duel"


def prepare(cache, offline=False):
    templates = json.loads((ROOT / "templates.json").read_text(encoding="utf-8"))
    images = ROOT / "images"
    images.mkdir(exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    for template in templates:
        path = cache / template["source_sha256"]
        if not path.is_file():
            if offline:
                raise FileNotFoundError(path)
            with urllib.request.urlopen(
                template["source_url"],
                timeout=30,
                context=ssl.create_default_context(cafile=certifi.where()),
            ) as response:
                path.write_bytes(response.read())
        if hashlib.sha256(path.read_bytes()).hexdigest() != template["source_sha256"]:
            raise ValueError(f"Source checksum mismatch: {template['key']}")
        with Image.open(path) as source:
            frames, durations = [], []
            for i in range(getattr(source, "n_frames", 1)):
                source.seek(i)
                crop = source.convert("RGBA").crop(template["crop"])
                background = Image.new("RGB", crop.size, "white")
                background.paste(crop, (0, 0), crop)
                frames.append(background)
                durations.append(max(20, source.info.get("duration", 100)))
            template["source_frames"] = getattr(source, "n_frames", 1)
        output = images / template["asset"]
        if template["animated"]:
            count = min(16, len(frames))
            indices = [i * len(frames) // count for i in range(count)]
            stops = indices[1:] + [len(frames)]
            frames[indices[0]].save(
                output,
                "GIF",
                save_all=True,
                append_images=[frames[i] for i in indices[1:]],
                duration=[sum(durations[start:end]) for start, end in zip(indices, stops)],
                loop=0,
                disposal=2,
            )
        else:
            frames[0].save(output, "PNG")
        template["asset_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    (ROOT / "templates.json").write_text(
        json.dumps(templates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Prepared {len(templates)} reviewed crops")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    prepare(args.cache_dir or Path(tempfile.mkdtemp(prefix="mantou-source-")), args.offline)
