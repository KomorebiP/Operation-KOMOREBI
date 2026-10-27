#!/usr/bin/env python3
"""Regenerate four inherited Paper V heatmaps with readable annotations.

Run from anywhere with Python 3.10+, NumPy and Matplotlib installed. The
unaltered plotting blocks and numerical modules are read from the bundled
historical source tree. Only annotation colors, the FIR annotation font size,
and the transfer-block title's line break change. No historical file is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1791504000")
sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
COMPANION = PACKAGE / "source/complete/original_snapshot/companion"
CORE = COMPANION / "projector_signal/visuals.py"
EXTENSION = PACKAGE / "source/annals/figure_source/generate_figures.py"
SOURCE_PINS = {
    "core": "01bde54156c8cc24a2e9eb5be44e5684a788da91f15b4e21e0482971e40ebce2",
    "extension": "b89a7563dc3afbf60cfded97327541d6268028153a1cd3c27ecd5b188ee27b25",
}
JOBS = (
    (CORE, 2, "core_figures/02_filter_transfer_matrix.pdf"),
    (CORE, 14, "core_figures/14_nonlinear_phase_coupling.pdf"),
    (EXTENSION, 2, "extension_figures/02_transfer_blocks.pdf"),
    (EXTENSION, 8, "extension_figures/08_overlap_matrix.pdf"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_block(path: Path, number: int) -> str:
    """Read the numbered plot block without executing any other plot."""
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^\s*# {number}\. [^\n]*\n", source)
    if match is None:
        raise RuntimeError(f"Plot block {number} missing from {path}")
    rest = source[match.end():]
    next_block = re.search(r"(?m)^\s*# \d+\. ", rest)
    block = rest[: next_block.start()] if next_block else rest
    if path == CORE:
        # The core plotting blocks occur inside make_figures.
        import textwrap
        block = textwrap.dedent(block)
    return block


def snapshot(fig: plt.Figure) -> dict:
    ax = fig.axes[0]
    image = ax.images[0]
    array = np.asarray(image.get_array())
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "matrix": array.tolist(),
        "matrix_sha256": hashlib.sha256(array.tobytes()).hexdigest(),
        "clim": list(image.get_clim()),
        "extent": list(image.get_extent()),
        "xlim": list(ax.get_xlim()),
        "ylim": list(ax.get_ylim()),
        "xticks": ax.get_xticks().tolist(),
        "yticks": ax.get_yticks().tolist(),
        "xtick_labels": [t.get_text() for t in ax.get_xticklabels()],
        "ytick_labels": [t.get_text() for t in ax.get_yticklabels()],
        "cell_labels": [t.get_text() for t in ax.texts],
        "cell_positions": [list(t.get_position()) for t in ax.texts],
        "xlabel": ax.get_xlabel(),
        "ylabel": ax.get_ylabel(),
        "colorbar_label": fig.axes[1].get_ylabel(),
    }


def relative_luminance(rgb: tuple) -> float:
    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return sum(w * linear(float(c)) for w, c in zip((0.2126, 0.7152, 0.0722), rgb[:3]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=HERE)
    parser.add_argument("--report", type=Path, default=HERE / "FIGURE_READABILITY_REPORT.json")
    args = parser.parse_args()
    for key, path in (("core", CORE), ("extension", EXTENSION)):
        if sha256(path) != SOURCE_PINS[key]:
            raise RuntimeError(f"Historical plotting source hash changed: {path}")
    sys.path.insert(0, str(COMPANION))
    from projector_signal.nonlinear import coefficient_packets
    records = []

    for source, number, destination in JOBS:
        saved = []

        def save_figure(fig: plt.Figure) -> None:
            ax = fig.axes[0]
            image = ax.images[0]
            before = snapshot(fig)
            title_before = ax.get_title()
            array = np.asarray(image.get_array())
            contrasts = []
            for text in ax.texts:
                x, y = text.get_position()
                rgba = image.cmap(image.norm(array[int(round(y)), int(round(x))]))
                luminance = relative_luminance(rgba)
                black = (luminance + 0.05) / 0.05
                white = 1.05 / (luminance + 0.05)
                color = "white" if white > black else "black"
                text.set_color(color)
                if destination == "core_figures/02_filter_transfer_matrix.pdf":
                    text.set_fontsize(9)
                contrasts.append({"label": text.get_text(), "color": color,
                                  "contrast_ratio": max(black, white),
                                  "font_size": text.get_fontsize()})
            if destination == "extension_figures/02_transfer_blocks.pdf":
                ax.set_title("Absolute tap weight\nin four phase transfer blocks", pad=12)
            after = snapshot(fig)
            if before != after:
                raise RuntimeError(f"Numerical model or labels changed in {destination}")
            # The extension's original save() used tight_layout; preserve that
            # behavior after the presentation changes. Core blocks did not.
            if source == EXTENSION:
                fig.tight_layout()
            out = args.output_root / destination
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out, format="pdf", bbox_inches="tight")
            records.append({
                "path": destination, "sha256": sha256(out),
                "source": str(source.relative_to(PACKAGE)),
                "source_sha256": sha256(source), "source_plot_number": number,
                "presentation_changes": ["contrast-aware annotation color"]
                    + (["cell annotation font size 7pt to 9pt"] if number == 2 and source == CORE else [])
                    + (["title line break and title padding"] if number == 2 and source == EXTENSION else []),
                "title_before": title_before, "title_after": ax.get_title(),
                "numerical_data_axes_and_labels_unchanged": before == after,
                "model": before, "annotations": contrasts,
                "minimum_annotation_contrast_ratio": min(c["contrast_ratio"] for c in contrasts),
            })
            saved.append(out)
            plt.close(fig)

        def core_save(fig: plt.Figure, root: Path, stem: str) -> list[str]:
            save_figure(fig)
            return [str(saved[-1])]

        def extension_save(name: str) -> None:
            save_figure(plt.gcf())

        namespace = {"np": np, "plt": plt, "generated": [],
                     "figure_dir": args.output_root,
                     "_save": core_save, "save": extension_save,
                     "coefficient_packets": coefficient_packets,
                     "__package__": "projector_signal"}
        exec(compile(selected_block(source, number), str(source), "exec"), namespace)
        if len(saved) != 1:
            raise RuntimeError(f"Expected one plot for {destination}, got {len(saved)}")

    report = {"status": "PASS", "edition_date": "2026-10-09",
              "scope": "Presentation-only regeneration of four inherited 2D heatmaps",
              "source_models_unchanged": True, "historical_sources_written": False,
              "original_plotting_blocks_executed": True,
              "generator": {"path": "editable/traditional/generate_readable_heatmaps.py",
                            "sha256": sha256(Path(__file__).resolve())},
              "dependencies": {"python": sys.version.split()[0],
                               "numpy": np.__version__, "matplotlib": matplotlib.__version__},
              "figures": records}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "figures": len(records),
                      "report": str(args.report)}))


if __name__ == "__main__":
    main()
