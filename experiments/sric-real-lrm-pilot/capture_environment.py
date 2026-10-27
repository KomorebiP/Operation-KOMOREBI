from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def package_version(name: str):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="environment.json")
    args = parser.parse_args()
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {
            name: package_version(name)
            for name in ["torch", "transformers", "datasets", "numpy", "huggingface_hub", "pytest"]
        },
    }
    try:
        import torch
        report["torch"] = {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda,
            "device_count": torch.cuda.device_count(),
            "devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
        }
    except Exception as exc:
        report["torch_error"] = repr(exc)
    try:
        report["nvidia_smi"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip().splitlines()
    except Exception:
        report["nvidia_smi"] = None
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ENVIRONMENT_REPORT={Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
