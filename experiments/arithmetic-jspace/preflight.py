from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=["cuda", "cpu"], required=True)
    args = parser.parse_args()
    try:
        import torch
    except ImportError as error:
        print(f"PREFLIGHT=FAIL: PyTorch is not installed: {error}")
        return 2
    if args.device == "cuda" and not torch.cuda.is_available():
        print("PREFLIGHT=FAIL: CUDA requested but torch.cuda.is_available() is False")
        return 3
    try:
        import numpy
    except ImportError as error:
        print(f"PREFLIGHT=FAIL: NumPy is not installed: {error}")
        return 4
    result = {
        "python": platform.python_version(),
        "python_executable": os.path.realpath(os.sys.executable),
        "python_prefix": os.sys.prefix,
        "numpy": numpy.__version__,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "device": args.device,
    }
    try:
        result["transformers"] = importlib.metadata.version("transformers")
    except importlib.metadata.PackageNotFoundError:
        result["transformers"] = "not-installed-not-required"
    if args.device == "cuda":
        properties = torch.cuda.get_device_properties(0)
        result["gpu"] = properties.name
        result["gpu_vram_gb"] = round(properties.total_memory / 1073741824, 3)
    print("PREFLIGHT=PASS")
    print("RUNTIME=" + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
