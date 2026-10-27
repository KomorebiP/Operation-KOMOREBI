"""Render the 34 inherited mathematical figures and contact sheets for QA."""
from pathlib import Path
import json
import hashlib
import fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QA = ROOT / "verification/figure_qa"
QA.mkdir(parents=True, exist_ok=True)
paths = sorted((HERE / "core_figures").glob("*.pdf")) + sorted((HERE / "extension_figures").glob("*.pdf"))
assert len(paths) == 34
inventory = []
for index, path in enumerate(paths, 1):
    document = fitz.open(path)
    assert len(document) == 1, path
    page = document[0]
    name = f"{index:02d}_{path.stem}.png"
    page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(QA / name)
    spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block for line in block["lines"] for span in line["spans"]]
    outside = [span["text"] for span in spans if not page.rect.contains(fitz.Rect(span["bbox"]))]
    original_dir = ROOT / ("source/complete/original_snapshot/manuscript/figures" if path.parent.name == "core_figures" else "source/strengthened/figures")
    inventory.append({
        "index": index, "path": str(path.relative_to(ROOT)),
        "before_sha256": hashlib.sha256((original_dir / path.name).read_bytes()).hexdigest(),
        "after_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "render": str((QA / name).relative_to(ROOT)),
        "width_pt": page.rect.width, "height_pt": page.rect.height,
        "minimum_extracted_font_pt": min((span["size"] for span in spans), default=None),
        "out_of_page_text": outside,
    })
for sheet, start in enumerate(range(0, len(paths), 12), 1):
    canvas = Image.new("RGB", (1800, 1900), "#d9d9d9")
    draw = ImageDraw.Draw(canvas)
    for cell, item in enumerate(inventory[start:start + 12]):
        x = (cell % 3) * 600
        y = (cell // 3) * 475
        picture = Image.open(ROOT / item["render"])
        picture.thumbnail((585, 435))
        canvas.paste(picture, (x + (600 - picture.width) // 2, y + 28 + (435 - picture.height) // 2))
        draw.text((x + 10, y + 6), f"{item['index']:02d} {Path(item['path']).name}", fill="black")
    canvas.save(QA / f"contact_{sheet:02d}.png")
(QA / "final_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
print(json.dumps({"figures": len(paths), "contacts": 3, "out_of_page_text": sum(bool(item["out_of_page_text"]) for item in inventory)}))
