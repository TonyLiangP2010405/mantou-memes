import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.isolated_backend import load_backend

backend = load_backend()
backend.load_memes(Path(__file__).resolve().parents[1] / "memes")


@pytest.fixture(scope="session")
def memes():
    return sorted(backend.get_memes(), key=lambda meme: meme.key)
