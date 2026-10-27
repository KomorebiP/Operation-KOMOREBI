"""Input contracts shared by exact numerical routines (no silent coercion)."""
from __future__ import annotations
from numbers import Integral
import numpy as np


def integer(value: object, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer >= {minimum}")
    result = int(value)
    if result < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return result


def real_array(value: object, name: str, *, ndim: int, empty: bool = False) -> np.ndarray:
    raw = np.asarray(value)
    if raw.ndim != ndim or (not empty and (raw.size == 0 or 0 in raw.shape)):
        raise ValueError(f"{name} must be a {'nonempty ' if not empty else ''}{ndim}-dimensional array")
    if raw.dtype.kind not in "biuf":
        raise ValueError(f"{name} must contain real numeric values, not {raw.dtype}")
    # float64 cannot promise exact conversion of arbitrary large integer data.
    if raw.dtype.kind in "iu" and raw.size:
        if int(raw.min()) < -(2**53) or int(raw.max()) > 2**53:
            raise ValueError(f"{name} integers must lie in [-2**53, 2**53] for lossless float64 conversion")
    result = np.asarray(raw, dtype=np.float64)
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def shape2(value: object) -> tuple[int, int]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError("shape must contain two positive integers")
    return integer(value[0], "height", minimum=1), integer(value[1], "width", minimum=1)


def dyadic_depth(shape: tuple[int, ...]) -> int:
    depth = 0
    while all(size % 2 == 0 for size in shape):
        shape = tuple(size // 2 for size in shape)
        depth += 1
    return depth


def readonly(value: object, dtype=None) -> np.ndarray:
    array = np.array(value, dtype=dtype, copy=True)
    array.setflags(write=False)
    return array
