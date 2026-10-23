"""Keep preview/test runs out of the user's meme-generator configuration."""

import importlib.util
import sys
import tempfile
from pathlib import Path


def load_backend():
    if "meme_generator" in sys.modules:
        raise RuntimeError("Call load_backend before importing meme_generator")
    package = importlib.util.find_spec("meme_generator")
    if package is None:
        raise RuntimeError("Install requirements-dev.txt first")
    path = Path(package.origin).with_name("dirs.py")
    spec = importlib.util.spec_from_file_location("meme_generator.dirs", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    root = Path(tempfile.mkdtemp(prefix="mantou-memes-"))
    for field, folder in [
        ("BASE_CACHE_DIR", "cache"),
        ("BASE_CONFIG_DIR", "config"),
        ("BASE_DATA_DIR", "data"),
    ]:
        setattr(module, field, root / folder)
    config = module.get_config_file("config.toml")
    config.write_text("[meme]\nload_builtin_memes = false\n", encoding="utf-8")
    import meme_generator

    return meme_generator
