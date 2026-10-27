"""Read-only PDF raster comparison for the final Lean guide review.

Writes a page-by-page comparison and renders each changed page for inspection.
It neither changes nor builds the supplied PDFs or their source files.
"""

import argparse
import hashlib
import json
from pathlib import Path

import fitz


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dpi", type=int, default=120)
    args = parser.parse_args()
    predecessor = args.predecessor.resolve(strict=True)
    candidate = args.candidate.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    old = fitz.open(predecessor)
    new = fitz.open(candidate)
    if len(old) != len(new):
        raise SystemExit(f"Page counts differ: predecessor={len(old)}, candidate={len(new)}")
    matrix = fitz.Matrix(args.dpi / 72, args.dpi / 72)
    records = []
    for index in range(len(new)):
        old_page, new_page = old[index], new[index]
        a = old_page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        b = new_page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        same = (a.width, a.height, a.samples) == (b.width, b.height, b.samples)
        if not same:
            b.save(output / f"page_{index + 1:03d}.png")
        records.append({
            "physical_page": index + 1,
            "raster_byte_identical": same,
            "text_identical": old_page.get_text() == new_page.get_text(),
            "raster_sha256": hashlib.sha256(b.samples).hexdigest(),
            "raster_size": [b.width, b.height],
        })
    report = {
        "candidate_path": str(candidate),
        "candidate_sha256": digest(candidate),
        "predecessor_path": str(predecessor),
        "predecessor_sha256": digest(predecessor),
        "dpi": args.dpi,
        "pages": len(new),
        "raster_equal_pages": [r["physical_page"] for r in records if r["raster_byte_identical"]],
        "changed_raster_pages": [r["physical_page"] for r in records if not r["raster_byte_identical"]],
        "changed_text_pages": [r["physical_page"] for r in records if not r["text_identical"]],
        "page_records": records,
    }
    target = output / "RASTER_DELTA.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "report": str(target),
        "candidate_sha256": report["candidate_sha256"],
        "pages": report["pages"],
        "raster_equal_page_count": len(report["raster_equal_pages"]),
        "changed_raster_pages": report["changed_raster_pages"],
        "changed_text_pages": report["changed_text_pages"],
    }, indent=2))


if __name__ == "__main__":
    main()
