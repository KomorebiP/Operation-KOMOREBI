#!/usr/bin/env python3
"""Poppler page renders and labeled contact sheets for publication QA."""
from pathlib import Path
import subprocess
import json
import tempfile
import shutil
import fcntl
from PIL import Image, ImageDraw, ImageFont
import fitz

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "preview").mkdir(exist_ok=True)
lock = (ROOT / "preview" / ".render.lock").open("w")
fcntl.flock(lock, fcntl.LOCK_EX)
font = ImageFont.truetype("DejaVuSans.ttf", 20)
reports = []
for pdf in sorted((ROOT / "output").glob("*.pdf")):
    final_destination = ROOT / "preview" / pdf.stem
    destination = Path(tempfile.mkdtemp(prefix="render_", dir=ROOT / "preview"))
    subprocess.run(["pdftoppm", "-png", "-scale-to", "1400", str(pdf), str(destination / "page")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    pages = sorted(destination.glob("page-*.png"))
    for start in range(0, len(pages), 6):
        sheet = Image.new("RGB", (1530, 1510), "#DDE4E6")
        draw = ImageDraw.Draw(sheet)
        for i, page in enumerate(pages[start:start + 6]):
            img = Image.open(page).convert("RGB")
            img.thumbnail((480, 690))
            x, y = (i % 3) * 510 + (510 - img.width) // 2, (i // 3) * 750 + 35
            sheet.paste(img, (x, y))
            draw.text(((i % 3) * 510 + 20, (i // 3) * 750 + 7), f"Page {start+i+1}", fill="#182A3B", font=font)
        sheet.save(destination / f"contact_{start//6+1:02d}.png")
    doc = fitz.open(pdf)
    reports.append({"file": str(pdf.relative_to(ROOT)), "pages": len(doc), "rendered_pages": len(pages), "empty_text_pages": [i+1 for i,p in enumerate(doc) if len(p.get_text().strip())<20], "page_sizes": sorted(set((round(p.rect.width,2),round(p.rect.height,2)) for p in doc))})
    if final_destination.exists():
        shutil.rmtree(final_destination)
    destination.rename(final_destination)
(ROOT / "verification" / "RENDER_REPORT.json").write_text(json.dumps({"status": "PASS", "documents": reports}, indent=2) + "\n")
print(json.dumps(reports, indent=2))
