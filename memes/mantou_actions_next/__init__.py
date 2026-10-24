"""Five hundred additional source-backed, image-only avatar action templates."""

import importlib.util
import json
from datetime import datetime
from functools import partial
from pathlib import Path

from meme_generator import add_meme

ROOT = Path(__file__).parent
TEMPLATES = json.loads((ROOT / "templates.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location(
    "mantou_avatar_runtime", ROOT.parent / "_mantou_avatar.py"
)
avatar_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(avatar_runtime)

for template in TEMPLATES:
    add_meme(
        template["key"],
        partial(avatar_runtime.render, template, root=ROOT),
        min_images=1,
        max_images=1,
        min_texts=0,
        max_texts=0,
        keywords=template["keywords"],
        tags={
            "mantou-memes",
            "换头像",
            "动作模板",
            template["family"],
            "动图" if template["animated"] else "静态",
        },
        date_created=datetime(2026, 10, 24),
        date_modified=datetime(2026, 10, 24),
    )
