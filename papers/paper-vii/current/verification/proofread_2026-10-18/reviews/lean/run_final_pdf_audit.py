#!/usr/bin/env python3
"""Temporary, read-only release QA; no Lean execution or release-tree writes."""
from pathlib import Path
import collections
import hashlib
import json
import shutil
import subprocess
import sys

import fitz
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
RELEASE = HERE.parents[1] / "output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18"
SOURCE = RELEASE / "source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot"
GUIDE = RELEASE / "editable/lean_guide"
STAGE = HERE / "final_pdf_stage"
PREVIOUS = HERE / "pre_binder_pdf_stage_2026-10-18/Paper_VII_Lean_Guide_Final.pdf"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if STAGE.exists():
        raise SystemExit(f"Refusing to replace existing QA stage: {STAGE}")
    STAGE.mkdir()
    for name in ("verify_pdf.py", "render_review_details.py", "Paper_VII_Lean_Guide_Final.pdf", "Paper_VII_Lean_Guide_Final.log"):
        shutil.copy2(GUIDE / name, STAGE / name)
    for name in ("generated", "excerpts"):
        shutil.copytree(GUIDE / name, STAGE / name)
    commands = [
        [sys.executable, "-B", str(STAGE / "verify_pdf.py"), "--source", str(SOURCE)],
        [sys.executable, "-B", str(STAGE / "render_review_details.py")],
    ]
    for cmd in commands:
        log = STAGE / (Path(cmd[2]).stem + "_stdout.txt")
        with log.open("w") as stream:
            subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, check=True)
    pdf = STAGE / "Paper_VII_Lean_Guide_Final.pdf"
    doc, old = fitz.open(pdf), fitz.open(PREVIOUS)
    reader = PdfReader(pdf)
    destinations = reader.named_destinations
    out = STAGE / "qa/individual"
    out.mkdir()
    renders, links, bad_rects, bad_targets, missing, mismatched = [], [], [], [], [], []
    glyphs = {"U+0357": 0, "U+FFFD": 0}
    for number, page in enumerate(doc, 1):
        png = out / f"page_{number:03d}.png"
        pix = page.get_pixmap(dpi=120, alpha=False)
        pix.save(png)
        text = page.get_text()
        record = {
            "page": number,
            "path": str(png),
            "bytes": png.stat().st_size,
            "image_sha256": sha(png.read_bytes()),
            "pixel_sha256": sha(pix.samples),
            "text_sha256": sha(text.encode()),
        }
        if number <= len(old):
            old_pix = old[number - 1].get_pixmap(dpi=120, alpha=False)
            record["pixels_identical_to_pre_binder"] = (pix.width, pix.height, pix.samples) == (old_pix.width, old_pix.height, old_pix.samples)
            record["text_identical_to_pre_binder"] = text == old[number - 1].get_text()
        else:
            record["pixels_identical_to_pre_binder"] = False
            record["text_identical_to_pre_binder"] = False
        renders.append(record)
        glyphs["U+0357"] += text.count("\u0357")
        glyphs["U+FFFD"] += text.count("\ufffd")
        for link in page.get_links():
            row = {"source_page": number, "kind": link["kind"], "source_rect": list(link["from"]), "named_destination": link.get("nameddest"), "target_page": link.get("page", -1) + 1}
            if "to" in link:
                row["target_point"] = list(link["to"])
            links.append(row)
            if not (page.rect + (-.5, -.5, .5, .5)).contains(link["from"]):
                bad_rects.append(row)
            if link["kind"] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                target = link.get("page", -1)
                if not 0 <= target < len(doc):
                    bad_targets.append(row)
                elif "to" in link and not (doc[target].rect + (-.5, -.5, .5, .5)).contains(link["to"]):
                    bad_targets.append(row)
                name = link.get("nameddest")
                if name and name not in destinations:
                    missing.append(row)
                elif name and reader.get_destination_page_number(destinations[name]) != target:
                    mismatched.append(row)
    data = {
        "pdf": str(pdf),
        "pdf_sha256": sha(pdf.read_bytes()),
        "bytes": pdf.stat().st_size,
        "pages": len(doc),
        "pre_binder_pdf": str(PREVIOUS),
        "pre_binder_pdf_sha256": sha(PREVIOUS.read_bytes()),
        "individual_renders": renders,
        "render_dpi": 120,
        "unchanged_pages": [x["page"] for x in renders if x["pixels_identical_to_pre_binder"] and x["text_identical_to_pre_binder"]],
        "pages_requiring_visual_review": [x["page"] for x in renders if not (x["pixels_identical_to_pre_binder"] and x["text_identical_to_pre_binder"])],
        "glyph_counts": glyphs,
        "link_kinds": dict(collections.Counter(x["kind"] for x in links)),
        "total_links": len(links),
        "named_destination_inventory": len(destinations),
        "outline_entries": len(doc.get_toc()),
        "out_of_page_link_rects": bad_rects,
        "invalid_target_pages_or_points": bad_targets,
        "missing_named_destinations": missing,
        "cross_reader_target_mismatch": mismatched,
        "links": links,
        "fresh_kernel_execution": False,
        "visual_review_status": "PENDING_MANUAL_INSPECTION_OF_CHANGED_PAGES",
    }
    data["automated_status"] = "PASS" if not (any(glyphs.values()) or bad_rects or bad_targets or missing or mismatched) else "FAIL"
    (STAGE / "qa/final_render_geometry_and_comparison.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({k: v for k, v in data.items() if k not in ("individual_renders", "links", "unchanged_pages")}, indent=2))
    if data["automated_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
