#!/usr/bin/env python3
"""Render the accepted publication verification-scope diagram.

This script changes only the diagram of verification scope. It performs no
scientific computation and does not constitute verification of a theorem.
"""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publication-root", type=Path, required=True)
    parser.add_argument("--accepted-proof-record", type=Path, required=True)
    args = parser.parse_args()
    # Requiring an actual record prevents accidental publication from an unrun draft.
    acceptance = json.loads(args.accepted_proof_record.read_text())
    if acceptance.get("status") not in {"PASS_SCOPED_CENTERED_EXTENSION"}:
        raise ValueError("The supplied formal acceptance record does not pass")
    root = args.publication_root.resolve()
    out = root / "source/monographs/figures"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "pdf.fonttype": 42, "ps.fonttype": 42,
                         "savefig.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(10.1, 5.25))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ink, pale = "#18394A", "#EEF3F4"

    def heading(y, text, color):
        ax.text(.014, y, text, ha="left", va="center", fontsize=11.4,
                fontweight="bold", color=color)

    def box(x, y, w, h, text, color, size=11.1):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.009,rounding_size=0.012",
                     facecolor=pale, edgecolor=color, linewidth=1.15))
        ax.text(x+w/2, y+h/2, text, ha="center", va="center",
                fontsize=size, color=ink, linespacing=1.35)

    heading(.962, "FORMAL SOURCE COVERAGE", "#078A98")
    box(.014, .724, .472, .182,
        "Unitary dynamics, maximal domain\nand strong Schrödinger equation", "#078A98")
    box(.514, .724, .472, .182,
        "Centered graph and resolvent limits\nand third-moment error bounds", "#078A98")
    heading(.638, "WRITTEN MATHEMATICAL IDENTIFICATION", "#173F5A")
    box(.014, .409, .972, .174,
        "Spectral-functional-calculus identification\nSeparate formal API linkage remains open", "#173F5A")
    heading(.319, "SEPARATE PHYSICAL COMPARISONS", "#AD6C2E")
    box(.014, .075, .472, .180,
        "Sampled spatial grids\nand background coupling", "#AD6C2E")
    box(.514, .075, .472, .180,
        "Dynamical fields\nand controlled production", "#AD6C2E")
    outputs = []
    for ext in ("pdf", "png"):
        p = out / f"12_frontier.{ext}"
        fig.savefig(p, dpi=190, bbox_inches="tight", pad_inches=.12,
                    metadata={"Creator": "Komorebi Physics publication source"}
                    if ext == "pdf" else None)
        outputs.append({"path": str(p.relative_to(root)),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    plt.close(fig)
    record = {"scope": "Verification diagram only, no scientific data changed.",
              "acceptance_record_sha256": hashlib.sha256(args.accepted_proof_record.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "outputs": outputs}
    (root / "audit/current_scope_figure.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
