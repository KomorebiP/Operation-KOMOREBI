"""Render reader PDFs and collect proportionate layout checks for inspection."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import shutil
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
QA = ROOT.parent / "tmp" / "pdfs" / "catalan_qa"
QA.mkdir(parents=True, exist_ok=True)
checks = json.loads((QA / 'layout_checks.json').read_text()) if (QA / 'layout_checks.json').exists() else {}
parser = argparse.ArgumentParser()
parser.add_argument("--only", nargs="+", choices=["paper", "visual"])
args = parser.parse_args()
for project in (args.only if args.only else ["paper", "visual"]):
    original_pdf = ROOT / project / "main.pdf"
    target = QA / project
    target.mkdir(exist_ok=True)
    pdf = target / 'snapshot.pdf'
    shutil.copyfile(original_pdf, pdf)
    snapshot_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
    doc = fitz.open(pdf)
    for old in list(target.glob("page-*.png")) + list(target.glob("contact-*.jpg")):
        old.unlink()
    renderer = '/usr/bin/pdftoppm' if Path('/usr/bin/pdftoppm').exists() else 'pdftoppm'
    subprocess.run([renderer, "-png", "-r", "150", str(pdf), str(target / "page")], check=True)
    page_files = sorted(target.glob("page-*.png"))
    text = "\n".join(page.get_text() for page in doc)
    outside = []
    for i, page in enumerate(doc, 1):
        for word in page.get_text("words"):
            x0, y0, x1, y1, token = word[:5]
            if x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width + 0.5 or y1 > page.rect.height + 0.5:
                outside.append({"page": i, "token": token, "bbox": [x0, y0, x1, y1]})
    log = (ROOT / project / "main.log").read_text(errors="replace")
    warnings = [line for line in log.splitlines() if re.search(r"Overfull|undefined|LaTeX Error|Missing character|destination with the same identifier", line)]
    for batch in range(math.ceil(len(page_files) / 9)):
        landscape = doc[0].rect.width > doc[0].rect.height
        row_height = 310 if landscape else 600
        sheet = Image.new("RGB", (1200, row_height * 3 + 10), "#E8EBEB")
        draw = ImageDraw.Draw(sheet)
        for pos, png in enumerate(page_files[batch * 9: batch * 9 + 9]):
            tile = Image.open(png).convert("RGB")
            tile.thumbnail((380, 269 if landscape else 553))
            x = (pos % 3) * 400 + (400 - tile.width) // 2
            y = (pos // 3) * row_height + 28
            sheet.paste(tile, (x, y))
            draw.text((x, y - 18), f"{project.title()} / page {batch * 9 + pos + 1}", fill="#243138")
        sheet.save(target / f"contact-{batch + 1:02d}.jpg", quality=92)
    checks[project] = {
        "pages": len(doc),
        "word_count_extracted": len(text.split()),
        "page_size_points": [doc[0].rect.width, doc[0].rect.height],
        "outside_page_words": outside,
        "tex_warnings_to_resolve": warnings,
        "replacement_characters": text.count("\ufffd"),
        "unresolved_placeholders": bool(re.search(r"\bTODO\b|Figure pending|PLACEHOLDER", text)),
        "rendered_pages": len(page_files),
        "pdf_sha256": snapshot_hash,
        "original_unchanged_during_render": hashlib.sha256(original_pdf.read_bytes()).hexdigest() == snapshot_hash,
        "renderer": renderer,
        "manual_visual_review": "pending",
    }
(QA / "layout_checks.json").write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
