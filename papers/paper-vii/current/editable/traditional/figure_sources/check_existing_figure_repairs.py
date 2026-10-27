"""Replay and audit the four presentation repairs against retained sources.

Checks plotted models and inherited labels, not a general theorem. All original
source files are read without generating Python bytecode in their directories.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import fitz
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRADITIONAL = HERE.parent
QA = ROOT / "verification/monograph_figure_qa"
CORE = ROOT / "source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_companion"
STRONG = ROOT / "source/strengthened/PSC_Paper_VII_Strengthened_Annals_Edition_Final"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    original = load(STRONG / "verification/generate_figures.py", "original_strengthened_figures")
    repaired = load(HERE / "repair_existing_figures.py", "repaired_existing_figures")
    old_figures, new_figures = {}, {}
    original.save = lambda fig, name: old_figures.update({name: fig})
    repaired.save = lambda fig, name, out: new_figures.update({name: fig})
    original.symmetry_packets()
    original.kato_transport()
    original.boundary_ladder()
    models = {"core/02_bell_seed_probabilities.pdf": repaired.bell(Path("unused")),
              "strengthened/03_symmetry_selection.pdf": repaired.symmetry(Path("unused")),
              "strengthened/06_kato_transport.pdf": repaired.kato(Path("unused")),
              "strengthened/16_continuum_boundary.pdf": repaired.boundary(Path("unused"))}
    checks = []

    def require(name: str, condition: bool, details=None):
        checks.append({"check": name, "passed": bool(condition), "details": details})
        if not condition:
            raise AssertionError(name)

    # Bell model comes from the exact inherited circuit implementation.
    sys.path.insert(0, str(CORE))
    from projector_quantum_calculus.circuits import bell_circuit
    old_probabilities = np.abs(bell_circuit()[2]) ** 2
    require("Bell probabilities identical to inherited circuit", np.array_equal(
        old_probabilities, models["core/02_bell_seed_probabilities.pdf"]["probabilities"]),
        old_probabilities.tolist())

    old_ax = old_figures["03_symmetry_selection.pdf"].axes[0]
    old_transfers = [[int(patch._posA_posB[0][0]), int(patch._posA_posB[1][0])]
                     for patch in old_ax.patches if isinstance(patch, original.FancyArrowPatch)]
    require("Four original cyclic transfers retained", old_transfers ==
            models["strengthened/03_symmetry_selection.pdf"]["transitions"], old_transfers)
    old_path = np.stack(old_figures["06_kato_transport.pdf"].axes[0].lines[0].get_data_3d(), axis=1)
    new_path = np.stack(new_figures["strengthened/06_kato_transport.pdf"].axes[0].lines[0].get_data_3d(), axis=1)
    require("Bloch coordinates identical for all 150 samples", np.array_equal(old_path, new_path),
            {"samples": len(old_path), "coordinates_sha256": hashlib.sha256(old_path.tobytes()).hexdigest()})
    old_mesh = old_figures["06_kato_transport.pdf"].axes[0].collections[0]._segments3d
    new_mesh = new_figures["strengthened/06_kato_transport.pdf"].axes[0].collections[0]._segments3d
    require("Sphere wireframe segments identical", len(old_mesh) == len(new_mesh) and all(
        np.array_equal(a, b) for a, b in zip(old_mesh, new_mesh)), {"segments": len(old_mesh)})
    require("Genuine 3D axes retained", new_figures["strengthened/06_kato_transport.pdf"].axes[0].name == "3d")
    old_labels = [text.get_text() for text in old_figures["16_continuum_boundary.pdf"].axes[0].texts[:-1]]
    new_labels = [text.get_text() for text in new_figures["strengthened/16_continuum_boundary.pdf"].axes[0].texts[:-1]]
    require("All seven boundary labels retained in order", old_labels == new_labels, old_labels)
    old_warning = old_figures["16_continuum_boundary.pdf"].axes[0].texts[-1].get_text()
    new_warning = new_figures["strengthened/16_continuum_boundary.pdf"].axes[0].texts[-1].get_text()
    require("Conditional proof-boundary warning retained", old_warning == new_warning, old_warning)
    for fig in [*old_figures.values(), *new_figures.values()]:
        plt.close(fig)

    # Run the actual packaged generator from an unrelated working directory.
    replay_records = []
    with tempfile.TemporaryDirectory(prefix="paper-vii-figure-replay-") as temporary:
        replay = Path(temporary) / "assets"
        process = subprocess.run([sys.executable, str(HERE / "repair_existing_figures.py"),
                                  "--output-directory", str(replay)], cwd=temporary,
                                 capture_output=True, text=True, check=True)
        (QA / "isolated_replay_stdout.txt").write_text(process.stdout)
        (QA / "isolated_replay_stderr.txt").write_text(process.stderr)
        for name in models:
            actual = TRADITIONAL / "assets" / name
            replayed = replay / name
            matched = digest(actual) == digest(replayed)
            require(f"Deterministic isolated PDF replay: {name}", matched)
            replay_records.append({"path": str(actual.relative_to(ROOT)),
                                   "sha256": digest(actual), "replay_sha256": digest(replayed),
                                   "binary_identical": matched})

    inventory = json.loads((QA / "original_inventory.json").read_text())
    by_path = {record["path"]: record for record in inventory}
    assets = sorted((TRADITIONAL / "assets").glob("*/*.pdf"))
    require("Exactly 35 inherited assets reviewed", len(assets) == 35 and len(inventory) == 35)
    records = []
    for asset in assets:
        local = asset.relative_to(TRADITIONAL / "assets").as_posix()
        inherited = (CORE / "figures" if asset.parent.name == "core" else STRONG / "figures") / asset.name
        old = by_path[str(asset.relative_to(ROOT))]
        require(f"Retrieved baseline agrees with retained original: {local}", digest(inherited) == old["sha256"])
        spans_outside, missing_glyphs = [], []
        with fitz.open(asset) as doc:
            require(f"One-page PDF: {local}", len(doc) == 1)
            embedded_raster_image_count = len(doc[0].get_images())
            page = doc[0]
            width, height = page.rect.width, page.rect.height
            unchanged_aspect = abs(width - old["width_pt"]) < 0.001 and abs(height - old["height_pt"]) < 0.001
            require(f"Original page dimensions retained: {local}", unchanged_aspect)
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        if x0 < -0.3 or y0 < -0.3 or x1 > width + 0.3 or y1 > height + 0.3:
                            spans_outside.append(span["text"])
                        if "\ufffd" in span["text"]:
                            missing_glyphs.append(span["text"])
            require(f"All extracted text spans contained: {local}", not spans_outside, spans_outside)
            require(f"No replacement characters: {local}", not missing_glyphs, missing_glyphs)
        changed = local in models
        require(f"Asset alteration matches recorded repair decision: {local}",
                (digest(asset) != old["sha256"]) if changed else (digest(asset) == old["sha256"]))
        records.append({"path": str(asset.relative_to(ROOT)), "original_source": str(inherited.relative_to(ROOT)),
                        "input_sha256": old["sha256"], "output_sha256": digest(asset),
                        "status": "PASS", "decision": "presentation_repair" if changed else "unchanged",
                        "page_size_pt": [width, height], "original_page_size_pt": [old["width_pt"], old["height_pt"]],
                        "page_dimensions_preserved": unchanged_aspect,
                        "vector_only_pdf": embedded_raster_image_count == 0,
                        "embedded_raster_image_count": embedded_raster_image_count,
                        "text_spans_outside_page": spans_outside,
                        "replacement_characters": missing_glyphs,
                        "mathematical_scope": models[local]["scope"] if changed else "Inherited figure model and labels preserved byte-for-byte.",
                        "presentation_change": {"core/02_bell_seed_probabilities.pdf": "ASCII closing angle replaced by a correctly typeset ket; same bar probabilities.",
                                                "strengthened/03_symmetry_selection.pdf": "Same four cyclic arrows routed between packet circles, with separate labels.",
                                                "strengthened/06_kato_transport.pdf": "Tick count reduced; axes given equal aspect; title wrapped; 3D axis labels contained.",
                                                "strengthened/16_continuum_boundary.pdf": "Stair boxes separated; arrows point from each stage to the next; final box contained."}.get(local)})

    pins = []
    for path in [HERE / "repair_existing_figures.py", Path(__file__),
                 STRONG / "verification/generate_figures.py", CORE / "projector_quantum_calculus/visuals.py",
                 CORE / "projector_quantum_calculus/circuits.py", HERE / "render_figure_review.py",
                 HERE / "README.md", HERE / "upstream/generate_strengthened_figures.py",
                 HERE / "upstream/core_visuals.py"]:
        pins.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path)})
    report = {"schema": "komorebi.monograph.figure_review.v1", "paper": "VII", "status": "PASS",
              "reviewed_original_count": 35, "repaired_count": 4, "unchanged_byte_identical_count": 31,
              "ai_images_used": False,
              "figure_encoding": {"vector_only": sum(r["vector_only_pdf"] for r in records),
                                  "hybrid_with_inherited_raster_heatmap": sum(not r["vector_only_pdf"] for r in records)},
              "resolved_validation_events": [{"kind": "review-script assumption",
                                               "failure": "Initial checker asserted no embedded images for every inherited figure; core/03 contains an original Matplotlib imshow heatmap.",
                                               "resolution": "Checker now records actual PDF encoding and only requires a single PDF page. Inherited raster heatmaps remain byte-identical; all four repairs are vector-only.",
                                               "mathematical_model_changed": False}],
              "manual_visual_review": {
                  "all_original_contact_sheets_reviewed": True,
                  "all_current_contact_sheets_reviewed": True,
                  "current_contact_sheets": [str(p.relative_to(ROOT)) for p in sorted(QA.glob("current_contact_*.png"))],
                  "current_render_scale": 2.0,
                  "contact_sheet_render_scale": 1.7,
                  "original_contact_sheets": [str(p.relative_to(ROOT)) for p in sorted(QA.glob("original_contact_*.png"))],
                  "original_fullsize_inspected": ["strengthened/03_symmetry_selection", "strengthened/06_kato_transport",
                                                  "strengthened/14_continuum_tower", "strengthened/15_constraint_obstruction",
                                                  "strengthened/16_continuum_boundary"],
                  "all_four_repaired_fullsize_images_reviewed": True,
                  "repaired_render_scale": 2.0,
                  "current_visible_defects": [],
                  "limitation": "Text-bound checks supplement visual inspection; no general theorem is established by figure or model replay."},
              "model_checks": checks, "models": models, "isolated_replay": replay_records,
              "source_pins": pins, "figures": records,
              "scope": "Presentation-only review of the 35 inherited traditional assets. Three new pedagogical figures are separately owned and checked."}
    (ROOT / "verification/monograph_figure_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "figures": 35, "repairs": 4, "unchanged": 31,
                      "checks": len(checks), "deterministic_replay": 4}))


if __name__ == "__main__":
    main()
