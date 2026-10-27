"""Reproduce structural checks and raster comparisons for the release PDFs."""
from pathlib import Path
import hashlib
import json
import re
import fitz

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {"monograph": "Monograph", "lean": "Lean_Guide", "visual": "Visual_Guide"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


structural, comparisons = {}, {}
for key, name in BOOKS.items():
    path = ROOT / f"build/final_03/{key}/Komorebi_Space_{name}.pdf"
    parent = ROOT / f"parent_books/Komorebi_Space_{name}_v1.13.0.pdf"
    initial = ROOT / f"build/final_01/{key}/Komorebi_Space_{name}.pdf"
    doc, old, first = fitz.open(path), fitz.open(parent), fitz.open(initial)
    invalid_links, outside = [], []
    for page_no, page in enumerate(doc, 1):
        for link in page.get_links():
            if link.get("kind") == fitz.LINK_GOTO and not 0 <= link.get("page", -1) < len(doc):
                invalid_links.append({"page": page_no, "link": str(link)})
        for block in page.get_text("blocks"):
            rect = fitz.Rect(block[:4])
            if rect.x0 < -0.5 or rect.y0 < -0.5 or rect.x1 > page.rect.width + 0.5 or rect.y1 > page.rect.height + 0.5:
                outside.append({"page": page_no, "rectangle": list(rect)})
    (ROOT / f"build/rendered_final/{key}_text.txt").write_text("\n\f\n".join(p.get_text() for p in doc))
    logs = list((ROOT / f"build/final_03/{key}").glob("*.log"))
    findings = []
    for log in logs:
        for line in log.read_text(errors="replace").splitlines():
            if re.search(r"Overfull|Underfull|undefined|multiply defined|Missing character|LaTeX Warning|Package .* Warning", line):
                findings.append({"log": log.name, "line": line})
    structural[key] = {"file": str(path.relative_to(ROOT)), "pages": len(doc), "sha256": digest(path),
                       "invalid_internal_links": invalid_links, "text_blocks_outside_page": outside,
                       "latex_findings": findings, "metadata": doc.metadata}
    identical, changed, same_as_initial = [], [], []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=72)
        if i < len(old) and pix.samples == old[i].get_pixmap(dpi=72).samples:
            identical.append(i + 1)
        else:
            changed.append(i + 1)
        if i < len(first) and pix.samples == first[i].get_pixmap(dpi=72).samples:
            same_as_initial.append(i + 1)
    comparisons[key] = {"parent_pages": len(old), "new_pages": len(doc), "final_sha256": digest(path),
                        "parent_sha256": digest(parent), "raster_comparison_dpi": 72,
                        "unchanged_pages": identical, "changed_or_new_pages": changed,
                        "pages_identical_to_initial_reviewed_render": same_as_initial}
    assert not invalid_links and not outside and not findings, structural[key]

for filename, data in [("PDF_STRUCTURAL_CHECKS.json", structural), ("PDF_PAGE_COMPARISON.json", comparisons)]:
    (ROOT / "records" / filename).write_text(json.dumps(data, indent=2) + "\n")
print(json.dumps({k: {"pages": v["pages"], "sha256": v["sha256"], "unchanged_parent_pages": len(comparisons[k]["unchanged_pages"]),
                        "identical_to_initial_reviewed_render": len(comparisons[k]["pages_identical_to_initial_reviewed_render"])}
                  for k, v in structural.items()}, indent=2))
