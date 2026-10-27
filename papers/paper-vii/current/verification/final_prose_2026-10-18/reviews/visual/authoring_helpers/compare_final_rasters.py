from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageChops, ImageDraw
import fitz

BASE = Path("/workspace/scratch/be33f0b6c391")
QA = BASE / "tmp/p7_final_visual_prose"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


atlas_rows = []
for p in range(118, 160):
    old = Image.open(QA / f"atlas_candidate3/poppler/page-{p}.png").convert("RGB")
    new = Image.open(QA / f"atlas_candidate4/poppler/page-{p}.png").convert("RGB")
    assert old.size == new.size
    box = ImageChops.difference(old, new).getbbox()
    assert box is None, ("Unexpected final atlas change", p, box)
    atlas_rows.append({"physical_page": p, "entire_page_pixels_identical": True,
                       "pixel_sha256": hashlib.sha256(new.tobytes()).hexdigest()})
write(QA / "atlas_candidate4/RASTER_COMPARISON.json", {
    "status": "PASS",
    "pdf_sha256": sha(BASE / "tmp/p7_final_candidate_4/Paper_VII_Traditional_Final.pdf"),
    "compared_to_sha256": sha(BASE / "tmp/p7_final_candidate_3/Paper_VII_Traditional_Final.pdf"),
    "dpi": 120,
    "all_42_pages_including_headers_and_footers_pixel_identical": True,
    "pages": atlas_rows,
})

old_pdf = fitz.open(BASE / "tmp/p7_final_candidate_3/Paper_VII_Visual_Guide_Final.pdf")
new_pdf = fitz.open(BASE / "tmp/p7_final_candidate_4/Paper_VII_Visual_Guide_Final.pdf")
guide_rows = []
changed_locators = []


def locator(doc, physical):
    blocks = [x for x in doc[physical - 1].get_text("blocks") if x[4].startswith("Traditional p")]
    assert len(blocks) == 1
    x0, y0, x1, y1 = blocks[0][:4]
    rect = [math.floor(x0 * 5 / 3) - 3, math.floor(y0 * 5 / 3) - 3,
            math.ceil(x1 * 5 / 3) + 3, math.ceil(y1 * 5 / 3) + 3]
    return rect, blocks[0][4].strip()


for p in range(1, 43):
    old = Image.open(QA / f"guide_candidate3/poppler/page-{p:02}.png").convert("RGB")
    new = Image.open(QA / f"guide_candidate4/poppler/page-{p:02}.png").convert("RGB")
    assert old.size == new.size
    diff = ImageChops.difference(old, new)
    box = diff.getbbox()
    row = {"physical_page": p, "visual_page": p - 2 if p >= 3 else None,
           "entire_page_pixels_identical": box is None, "whole_diff_bbox": box,
           "pixel_sha256": hashlib.sha256(new.tobytes()).hexdigest()}
    if p >= 3:
        masks = []
        for doc in [old_pdf, new_pdf]:
            rect, line = locator(doc, p)
            masks.append(rect)
            diff.paste((0, 0, 0), rect)
        row["locator_mask_rectangles"] = masks
        row["final_locator_text"] = locator(new_pdf, p)[1]
        if box is not None:
            changed_locators.append((p, new, locator(new_pdf, p)))
    row["pixels_outside_precise_locator_rectangles_identical"] = diff.getbbox() is None
    assert diff.getbbox() is None, ("Unexpected final guide body change", p, diff.getbbox())
    guide_rows.append(row)

for offset in range(0, len(changed_locators), 20):
    batch = changed_locators[offset:offset + 20]
    sheet = Image.new("RGB", (980, 45 * len(batch)), "white")
    draw = ImageDraw.Draw(sheet)
    for j, (p, pic, (rect, line)) in enumerate(batch):
        draw.text((5, j * 45 + 8), f"V{p - 2}", fill="black")
        sheet.paste(pic.crop((95, rect[1], 930, rect[3])), (55, j * 45 + 8))
    sheet.save(QA / f"guide_candidate4/changed_locator_sheet_{offset // 20 + 1}.png")

write(QA / "guide_candidate4/RASTER_COMPARISON.json", {
    "status": "PASS",
    "pdf_sha256": sha(BASE / "tmp/p7_final_candidate_4/Paper_VII_Visual_Guide_Final.pdf"),
    "compared_to_sha256": sha(BASE / "tmp/p7_final_candidate_3/Paper_VII_Visual_Guide_Final.pdf"),
    "dpi": 120,
    "all_42_pages_pixel_identical_outside_precise_locator_rectangles": True,
    "changed_locator_physical_pages": [r[0] for r in changed_locators],
    "changed_locator_visual_pages": [r[0] - 2 for r in changed_locators],
    "pages": guide_rows,
})
print(json.dumps({
    "atlas": "All 42 entire page rasters are identical to candidate 3.",
    "guide": "All 42 page rasters are identical outside exact locator rectangles.",
    "guide_changed_locator_visual_pages": [r[0] - 2 for r in changed_locators],
    "guide_entire_page_identical_count": sum(r["entire_page_pixels_identical"] for r in guide_rows),
}))
