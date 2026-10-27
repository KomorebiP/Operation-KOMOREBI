#!/usr/bin/env python3
"""Resolve and record externally installed fonts. No downloads or installation."""
from pathlib import Path
import hashlib
import shutil
import subprocess

BASE = ["P052-Roman.otf", "P052-Bold.otf", "P052-Italic.otf", "P052-BoldItalic.otf",
        "NimbusSans-Regular.otf", "NimbusSans-Bold.otf", "NimbusSans-Italic.otf", "NimbusSans-BoldItalic.otf",
        "lmmono10-regular.otf", "lmmono10-italic.otf", "latinmodern-math.otf"]
CODE = ["DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf", "DejaVuSansMono-Oblique.ttf", "DejaVuSansMono-BoldOblique.ttf"]

def resolve_fonts(include_code=False):
    if shutil.which("kpsewhich") is None:
        raise SystemExit("kpsewhich is required to resolve the documented external fonts. No dependencies are installed automatically.")
    records = []
    for name in BASE + (CODE if include_code else []):
        run = subprocess.run(["kpsewhich", name], text=True, capture_output=True, timeout=20)
        lines = run.stdout.strip().splitlines()
        path = Path(lines[0]) if lines else None
        if run.returncode or path is None or not path.is_file():
            raise SystemExit("Required external font unavailable: " + name + ". See FONT_DEPENDENCIES.txt. No fallback font was substituted.")
        records.append({"file": name, "resolved_path": str(path.resolve()), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"schema": "komorebi.paper-vi.external-fonts/1", "policy": "External system fonts; no font binaries are bundled or installed by this builder.", "fonts": records}

def stage_fonts(stage, record):
    target = Path(stage) / "fonts"
    target.mkdir(parents=True, exist_ok=True)
    for item in record["fonts"]:
        destination = target / item["file"]
        shutil.copyfile(item["resolved_path"], destination)
        if hashlib.sha256(destination.read_bytes()).hexdigest() != item["sha256"]:
            raise SystemExit("Font changed during staging: " + item["file"])
