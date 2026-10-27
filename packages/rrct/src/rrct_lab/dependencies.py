from __future__ import annotations

import importlib.util
import platform
import sys
from typing import Any


def available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def doctor() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": None,
        "torch": None,
        "matplotlib": None,
        "pytest": None,
        "cuda_available": False,
        "cuda_device_count": 0,
    }
    import numpy

    payload["numpy"] = numpy.__version__
    if available("torch"):
        import torch

        payload["torch"] = torch.__version__
        payload["cuda_available"] = bool(torch.cuda.is_available())
        payload["cuda_device_count"] = int(torch.cuda.device_count()) if torch.cuda.is_available() else 0
    if available("matplotlib"):
        import matplotlib

        payload["matplotlib"] = matplotlib.__version__
    if available("pytest"):
        import pytest

        payload["pytest"] = pytest.__version__
    return payload
