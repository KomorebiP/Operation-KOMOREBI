from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from PIL import Image

Array = NDArray[np.float64]


def load_image(path: str | Path) -> Array:
    """Load a normalized raster, preserving alpha and 16-bit grayscale.

    Floating-point ``.npy`` sources must already lie in ``[0, 1]``. Pillow
    formats use their declared integer depth, never observed min/max values.
    """
    from .atlas import ensure_image

    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".npy":
        return ensure_image(np.load(source, allow_pickle=False))
    with Image.open(source) as image:
        if image.mode in {"1", "L", "F"} or image.mode.startswith("I;16"):
            value = np.asarray(image)
        elif image.mode == "I":
            raw = np.asarray(image)
            if image.format != "PNG" or np.any(raw < 0) or np.any(raw > 65535):
                raise ValueError("signed integer image files require explicit normalization; use a normalized .npy raster")
            value = raw.astype(np.uint16)
        elif image.mode in {"RGBA", "LA"} or "transparency" in image.info:
            value = np.asarray(image.convert("RGBA"))
        else:
            value = np.asarray(image.convert("RGB"))
    return ensure_image(value)


def save_image(path: str | Path, image: Array) -> Path:
    """Save an 8-bit display preview, with explicit clipping and quantization.

    Use ``numpy.save(..., allow_pickle=False)`` for exact floating-point data.
    """
    destination = Path(path)
    value = np.asarray(image, dtype=np.float64)
    if value.ndim == 2:
        value = value[..., None]
    if value.ndim != 3 or value.shape[2] not in {1, 3, 4}:
        raise ValueError("image must have 1, 3, or 4 channels")
    if not all(value.shape) or not np.isfinite(value).all():
        raise ValueError("image must be nonempty and contain only finite values")
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = np.rint(np.clip(value, 0.0, 1.0) * 255.0).astype(np.uint8)
    if encoded.shape[2] == 1:
        output = Image.fromarray(encoded[..., 0])
    elif encoded.shape[2] == 3:
        output = Image.fromarray(encoded)
    else:
        output = Image.fromarray(encoded)
    output.save(destination)
    return destination
