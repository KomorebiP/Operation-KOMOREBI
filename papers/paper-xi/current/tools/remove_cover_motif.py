#!/usr/bin/env python3
"""Remove the five known Paper XI research-reader cover motifs and audit the edit.

This release-1.1 presentation repair changes only the final S (stroke) operator
of each of 17 exact cubic paths per cover to n (end path without painting).
It does not paint rectangles, redact, flatten, rasterize, reflow, or add text.
The historical mathematical version labels and all other page content remain.

Requires Python 3, PyMuPDF, NumPy and Pillow. Reproduce from the unmodified
research PDFs, whose SHA-256 hashes are pinned below:

  python tools/remove_cover_motif.py --source-dir ORIGINAL_PDFS

By default the two results replace publication/pdfs/<original filename>, the
receipt is evidence/release_1_1/COVER_MOTIF_REMOVAL.json, and visual evidence is
evidence/release_1_1/cover_motifs/. Existing source and destination directories
may be the same: source bytes are captured before any replacement. Each output
is validated before atomic replacement. The script refuses modified inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone

import fitz
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "Paper_XI_Conjecture66_Progress_v0.4.0.pdf": {
        "sha256": "cc613949a95c9d149c5ff9786ef5d53b77b4711f7a65350c68cc7ed3b030b39d",
        "page_count": 77, "covers": [1, 3, 36, 55],
    },
    "Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf": {
        "sha256": "7ea0746b5eb1c33ced22d4a4186108fc81add7e58a9ee00f9ae08d4d1c73b457",
        "page_count": 36, "covers": [1],
    },
}
PATHS = tuple(tuple(map(float, line.split())) for line in """
506.16644 26.07971 369.36514 18.8792 524.16557 -53.12173 495.36566 -153.92259
498.96591 8.07948 471.60521 12.39935 408.96475 41.19926 448.56548 28.23964
498.96591 8.07948 520.5664 2.31927 565.20662 -34.40187 536.4067 -17.12126
489.60544 -9.20111 462.24474 -4.88124 399.6043 23.91867 439.20502 10.95905
489.60544 -9.20111 511.20593 -14.9613 555.84615 -51.68248 527.04623 -34.40187
480.24498 -26.48172 452.88428 -22.16185 390.24382 6.63806 429.84454 -6.32155
480.24498 -26.48172 501.84547 -32.24191 546.48569 -68.96309 517.68576 -51.68248
470.8845 -43.76233 443.5238 -39.44246 380.88336 -10.64253 420.48409 -23.60216
470.8845 -43.76233 492.485 -49.52252 537.12521 -86.24368 508.3253 -68.96309
461.52405 -61.04292 434.16335 -56.72305 371.52289 -27.92314 411.12361 -40.88277
461.52405 -61.04292 483.12454 -66.80313 527.76476 -103.52429 498.96483 -86.24368
452.16357 -78.32353 424.80287 -74.00366 362.16243 -45.20375 401.76315 -58.16338
452.16357 -78.32353 473.76407 -84.08372 518.40428 -120.8049 489.60437 -103.52429
442.80312 -95.60414 415.44241 -91.28427 352.80196 -62.48434 392.40268 -75.44397
442.80312 -95.60414 464.40361 -101.36433 509.04382 -138.08551 480.2439 -120.8049
433.44264 -112.88475 406.08194 -108.56488 343.4415 -79.76495 383.04222 -92.72458
433.44264 -112.88475 455.04314 -118.64494 499.68335 -155.3661 470.88344 -138.08551
""".strip().splitlines())
NUMBER = rb"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
CURVE = re.compile(rb"(?<![\w.])(" + NUMBER + rb")\s+(" + NUMBER +
                   rb")\s+m\s+(" + NUMBER + rb")\s+(" + NUMBER +
                   rb")\s+(" + NUMBER + rb")\s+(" + NUMBER +
                   rb")\s+(" + NUMBER + rb")\s+(" + NUMBER +
                   rb")\s+c\s+(S)(?!\w)")


def require(test, message):
    if not test:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, fitz.Rect, fitz.Point, fitz.Quad)):
        return [canonical(v) for v in value]
    if isinstance(value, bytes):
        return {"bytes_sha256": digest(value), "length": len(value)}
    return value


def hash_value(value):
    return digest(json.dumps(canonical(value), sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode())


def drawings(page):
    # Display-list sequence numbers decrease when a paint operation disappears;
    # the drawing geometry, style, order and all other fields must be identical.
    return [canonical({k: v for k, v in d.items() if k != "seqno"})
            for d in page.get_drawings()]


def snapshot(page):
    return {
        "page": page.number + 1,
        "geometry_sha256": hash_value([page.mediabox, page.cropbox, page.trimbox,
                                       page.bleedbox, page.artbox, page.rotation,
                                       page.get_label()]),
        "text_sha256": digest(page.get_text().encode()),
        "text_layout_sha256": hash_value(page.get_text("rawdict")),
        "links_sha256": hash_value(page.get_links()),
        "link_count": len(page.get_links()),
        "images_sha256": hash_value(page.get_images(full=True)),
        "annotations_sha256": hash_value([
            [a.xref, a.type, a.rect, a.info, a.flags, a.colors, a.opacity]
            for a in page.annots() or []
        ]),
        "contents_xrefs": page.get_contents(),
    }


def validate_cover_drawings(page):
    ds = page.get_drawings()
    require(len(ds) == 20, f"Unexpected cover drawing count on page {page.number + 1}")
    curves = ds[2:19]
    for i, (drawing, raw) in enumerate(zip(curves, PATHS)):
        expected = np.asarray(raw).reshape(4, 2) * [1, -1] + [59.041, 72.879]
        require(drawing["type"] == "s" and len(drawing["items"]) == 1
                and drawing["items"][0][0] == "c", "Unexpected motif path type")
        points = np.array([list(p) for p in drawing["items"][0][1:]])
        require(np.max(np.abs(points - expected)) < .001, "Motif transform differs")
        require(abs(drawing["width"] - (.79701 if i == 0 else .69739)) < .00001,
                "Unexpected motif stroke width")
        expected_color = (.690, .769, .742) if i == 0 else (.739, .806, .783)
        require(max(abs(a - b) for a, b in zip(drawing["color"], expected_color)) < .001,
                "Unexpected motif stroke color")
        require(drawing.get("fill") is None and not drawing["closePath"],
                "Unexpected motif fill or closure")
    return curves


def stroke_containment(pixel_x, pixel_y, curves, scale):
    """Bound all changed pixel centers by the original vector strokes.

    This mask is independent of the difference image: it is derived solely from
    the original cubic control points and stroke widths. Cubics are sampled into
    512 line segments; the standard sup|B''|/(8*N^2) interpolation bound is added.
    A one-pixel allowance covers raster antialiasing and pixel-center sampling.
    """
    points = np.column_stack(((pixel_x + .5) / scale, (pixel_y + .5) / scale))
    excess = np.full(len(points), np.inf)
    max_error = 0.0
    n = 512
    t = np.linspace(0, 1, n + 1)[:, None]
    for d in curves:
        p = np.asarray([list(v) for v in d["items"][0][1:]])
        bez = (1-t)**3*p[0] + 3*(1-t)**2*t*p[1] + 3*(1-t)*t**2*p[2] + t**3*p[3]
        err = max(np.linalg.norm(6*(p[2]-2*p[1]+p[0])),
                  np.linalg.norm(6*(p[3]-2*p[2]+p[1]))) / (8*n*n)
        max_error = max(max_error, float(err))
        width = d["width"] / 2
        padding = width + 1 / scale + err
        low, high = bez.min(axis=0) - padding, bez.max(axis=0) + padding
        candidates = np.flatnonzero(np.all((points >= low) & (points <= high), axis=1))
        start, vectors = bez[:-1], np.diff(bez, axis=0)
        lengths = (vectors*vectors).sum(axis=1)
        for batch in np.array_split(candidates, max(1, math.ceil(len(candidates)/512))):
            if not len(batch):
                continue
            delta = points[batch, None, :] - start[None, :, :]
            projection = np.clip((delta*vectors).sum(axis=2)/lengths, 0, 1)
            distances = np.linalg.norm(delta - projection[:, :, None]*vectors, axis=2)
            local = distances.min(axis=1) - width - err
            excess[batch] = np.minimum(excess[batch], local)
    maximum = float(excess.max()) if len(excess) else 0.0
    return {
        "method": "distance to original cubic strokes; 512-segment interpolation with analytic error bound",
        "antialias_allowance_pixels": 1,
        "antialias_allowance_points": 1 / scale,
        "maximum_interpolation_error_points": max_error,
        "maximum_changed_pixel_excess_beyond_stroke_points": maximum,
        "all_changed_pixels_within_original_strokes_plus_allowance": maximum <= 1 / scale,
    }


def relative(path, root):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def process(name, spec, args):
    source, target = args.source_dir / name, args.target_dir / name
    original = source.read_bytes()
    require(digest(original) == spec["sha256"], f"Refusing unrecognized source: {source}")
    before = fitz.open(stream=original, filetype="pdf")
    require(len(before) == spec["page_count"], "Page count differs from pinned input")
    patches, cover_curves, scan = {}, {}, []
    for page in before:
        found = []
        for xref in page.get_contents():
            raw = before.xref_stream(xref)
            matches = [m for m in CURVE.finditer(raw)
                       if tuple(float(v) for v in m.groups()[:8]) in PATHS]
            if matches:
                require(tuple(tuple(float(v) for v in m.groups()[:8]) for m in matches) == PATHS,
                        "Partial, repeated or reordered motif match")
                require(matches[-1].end() < raw.find(b"BT"),
                        "Known cover motif is not before the first text object")
                require(xref not in patches, "Shared motif stream requires separate review")
                changed = bytearray(raw)
                offsets = [m.start(9) for m in matches]
                for offset in offsets:
                    changed[offset] = ord("n")
                changed = bytes(changed)
                require([i for i, (a, b) in enumerate(zip(raw, changed)) if a != b] == offsets,
                        "A byte outside the selected stroke operators changed")
                patches[xref] = (raw, changed, offsets)
                found.append({"xref": xref, "operators_changed": len(offsets),
                              "decoded_stream_byte_offsets": offsets,
                              "decoded_stream_sha256_before": digest(raw),
                              "decoded_stream_sha256_after": digest(changed),
                              "decoded_stream_length_unchanged": len(raw) == len(changed)})
        if found:
            cover_curves[page.number] = validate_cover_drawings(page)
        scan.append({"page": page.number + 1, "matched_streams": found})
    require([p+1 for p in cover_curves] == spec["covers"], "Cover page inventory differs")
    require(len(patches) == len(spec["covers"]), "Unexpected matching stream count")
    snapshots = [snapshot(page) for page in before]

    args.target_dir.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.stem}_", suffix=".pdf", dir=args.target_dir)
    os.close(fd)
    temporary = Path(temp_name)
    try:
        temporary.write_bytes(original)
        edit = fitz.open(temporary)
        require(edit.can_save_incrementally(), "Incremental preservation unavailable")
        for xref, (_, changed, _) in patches.items():
            edit.update_stream(xref, changed)
        edit.save(temporary, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP, no_new_id=True)
        edit.close()
        output = temporary.read_bytes()
        require(output.startswith(original), "Incremental output does not preserve original bytes")
        after = fitz.open(temporary)
        require(len(after) == len(before), "Page count changed")
        require(after.metadata == before.metadata, "Document metadata changed")
        require(canonical(after.get_toc(simple=False)) == canonical(before.get_toc(simple=False)),
                "Document outline changed")
        require(after.get_page_labels() == before.get_page_labels(), "Page labels changed")
        invariant_pages = []
        for a, b, snap in zip(before, after, snapshots):
            require(snapshot(b) == snap, f"Text, links, geometry or resources changed on page {a.number+1}")
            expected = drawings(a)
            if a.number in cover_curves:
                expected = expected[:2] + expected[19:]
            require(drawings(b) == expected, f"Other drawings changed on page {a.number+1}")
            invariant_pages.append({**snap, "all_page_invariants_equal": True,
                                    "other_drawings_equal": True})
        for xref in range(1, before.xref_length()):
            if xref in patches:
                require(after.xref_stream(xref) == patches[xref][1], "Edited stream differs from exact patch")
            else:
                require(after.xref_object(xref) == before.xref_object(xref),
                        f"Unrelated PDF object changed: {xref}")
                if before.xref_is_stream(xref):
                    require(after.xref_stream_raw(xref) == before.xref_stream_raw(xref),
                            f"Unrelated encoded stream changed: {xref}")

        render_rows = []
        args.render_dir.mkdir(parents=True, exist_ok=True)
        for a, b in zip(before, after):
            scale = 2  # Every complete page is checked at 144 dpi.
            p0 = a.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            p1 = b.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            require((p0.width, p0.height, p0.n) == (p1.width, p1.height, p1.n), "Raster dimensions changed")
            arr0 = np.frombuffer(p0.samples, np.uint8).reshape(p0.height, p0.width, p0.n)
            arr1 = np.frombuffer(p1.samples, np.uint8).reshape(p1.height, p1.width, p1.n)
            diff = np.any(arr0 != arr1, axis=2)
            yy, xx = np.nonzero(diff)
            row = {"page": a.number + 1, "dpi": 144,
                   "before_pixel_sha256": digest(p0.samples),
                   "after_pixel_sha256": digest(p1.samples),
                   "changed_pixel_count": int(diff.sum())}
            if a.number not in cover_curves:
                require(not diff.any(), f"Unexpected raster difference on page {a.number+1}")
                row["pixels_identical"] = True
            else:
                require(diff.any(), "Matched cover did not change visually")
                containment = stroke_containment(xx, yy, cover_curves[a.number], scale)
                require(containment["all_changed_pixels_within_original_strokes_plus_allowance"],
                        f"Raster difference escapes original strokes on page {a.number+1}")
                row.update({"difference_bbox_pixels": [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)],
                            "difference_bbox_pdf_points": [float(xx.min()/scale), float(yy.min()/scale),
                                                           float((xx.max()+1)/scale), float((yy.max()+1)/scale)],
                            "stroke_containment": containment})
                stem = f"{Path(name).stem}_page_{a.number+1:03d}"
                files = {}
                for suffix, pix in [("before", p0), ("after", p1)]:
                    path = args.render_dir / f"{stem}_{suffix}.png"
                    pix.save(path)
                    files[suffix] = relative(path, ROOT)
                delta_path = args.render_dir / f"{stem}_difference.png"
                delta = np.full(arr0.shape, 255, dtype=np.uint8)
                delta[diff] = [188, 44, 66]
                Image.fromarray(delta).save(delta_path)
                files["difference"] = relative(delta_path, ROOT)
                crop = fitz.Rect(392, 20, 612, 245)
                for suffix, page in [("before", a), ("after", b)]:
                    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=crop, alpha=False)
                    path = args.render_dir / f"{stem}_local_{suffix}.png"
                    pix.save(path)
                    files[f"local_{suffix}"] = relative(path, ROOT)
                row["local_render_dpi"] = 288
                row["local_render_clip_pdf_points"] = list(crop)
                row["visual_evidence"] = files
            render_rows.append(row)
        after.close()
        before.close()
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()

    return {
        "filename": name,
        "source_sha256": digest(original), "output_sha256": digest(output),
        "source_bytes": len(original), "output_bytes": len(output),
        "page_count_before": spec["page_count"], "page_count_after": spec["page_count"],
        "cover_pages": spec["covers"], "motif_count": len(cover_curves),
        "stroke_operators_changed": sum(len(p[2]) for p in patches.values()),
        "page_scan": scan,
        "invariants": {
            "original_pdf_bytes_preserved_as_incremental_prefix": True,
            "only_matched_decoded_stream_bytes_changed": True,
            "all_unrelated_existing_pdf_objects_unchanged": True,
            "all_unrelated_encoded_stream_bytes_unchanged": True,
            "page_count_geometry_labels_text_layout_links_images_annotations_unchanged": True,
            "all_other_drawings_unchanged": True,
            "metadata_and_outline_unchanged": True,
            "no_rectangle_painting_redaction_rasterization_or_flattening": True,
        },
        "page_invariants": invariant_pages,
        "render_comparison": render_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--target-dir", type=Path, default=ROOT / "publication/pdfs")
    parser.add_argument("--receipt", type=Path, default=ROOT / "evidence/release_1_1/COVER_MOTIF_REMOVAL.json")
    parser.add_argument("--render-dir", type=Path, default=ROOT / "evidence/release_1_1/cover_motifs")
    args = parser.parse_args()
    for key in ("source_dir", "target_dir", "receipt", "render_dir"):
        setattr(args, key, getattr(args, key).resolve())
    # Validate both inputs before beginning the first output.
    for name, spec in SPECS.items():
        require(digest((args.source_dir / name).read_bytes()) == spec["sha256"],
                f"Refusing input other than the original historical binary: {name}")
    receipt = {
        "schema": "paper-xi-cover-motif-removal-v1",
        "release": "1.1", "mathematical_version_labels": "preserved",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "tools": {"python": sys.version.split()[0], "pymupdf": fitz.VersionBind,
                  "numpy": np.__version__, "pillow": Image.__version__},
        "method": "Exact seventeen-cubic cover-path signature; change only S to n; incremental PDF save",
        "path_signature_raw_coordinates": PATHS,
        "coordinate_convention": "PDF-space evidence bounds use PyMuPDF top-left origin in points",
        "full_page_render_dpi": 144, "local_render_dpi": 288,
        "visual_inspection": {"status": "awaiting independent visual review"},
        "documents": [],
    }
    for name, spec in SPECS.items():
        result = process(name, spec, args)
        receipt["documents"].append(result)
        print(json.dumps({"filename": name, "pages": spec["page_count"],
                          "covers": spec["covers"], "strokes_removed": result["stroke_operators_changed"],
                          "output_sha256": result["output_sha256"]}), flush=True)
    receipt["all_automated_invariants_passed"] = True
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    print(f"Receipt: {args.receipt}", flush=True)


if __name__ == "__main__":
    main()
