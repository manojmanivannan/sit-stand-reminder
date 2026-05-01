"""Asset loading and caching."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


def get_bundle_dir() -> str:
    """Return the directory where bundled assets are stored."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    # In development, assets live at the project root (one level above this package)
    return str(Path(__file__).parent.parent)



def get_asset_path(name: str, subdir: str, ext: str = "") -> str | None:
    """Return the full path to an asset if it exists."""
    bundle = Path(get_bundle_dir())
    path = bundle / subdir / f"{name}{ext}"
    if path.exists():
        return str(path)
    return None


@lru_cache(maxsize=8)
def load_image(name: str, size: tuple[int, int]) -> "Image.Image" | None:
    """Load and resize an image, returning a PIL Image."""
    from PIL import Image as PILImage

    path = get_asset_path(name, "images", ".png")
    if not path:
        return None
    try:
        img = PILImage.open(path).convert("RGBA")
        img = img.resize(size, PILImage.Resampling.LANCZOS)
        return img
    except Exception:
        return None
