from __future__ import annotations

import argparse
import json
from pathlib import Path

import generate_chunks
import write_results
import write_table_chunks
from proof_atlas.foundation_figures import generate_foundation_figures


def _validate_figure_inventory(root: Path) -> None:
    pdfs = sorted((root / "figures").glob("[0-9][0-9]_*.pdf"))
    pngs = sorted((root / "figures").glob("[0-9][0-9]_*.png"))
    if len(pdfs) != 61 or len(pngs) != 61:
        raise RuntimeError(f"expected 61 figure pairs, found {len(pdfs)} PDF and {len(pngs)} PNG")
    if [p.stem for p in pdfs] != [p.stem for p in pngs]:
        raise RuntimeError("PDF and PNG figure stems differ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="regenerate the retained 38 domain figures and all tables in addition to the new foundational layer",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent

    print("table:foundation", flush=True)
    write_table_chunks.foundation_table()

    if args.full:
        table_functions = [
            write_table_chunks.linear_table,
            write_table_chunks.signal_table,
            write_table_chunks.bayes_table,
            write_table_chunks.arithmetic_table,
            write_table_chunks.physics_table,
            write_table_chunks.nonlinear_table,
        ]
        for fn in table_functions:
            print(f"table:{fn.__name__}", flush=True)
            fn()
        for index in range(12):
            print(f"figures:chunk{index}", flush=True)
            getattr(generate_chunks, f"chunk{index}")()

    print("figures:foundations", flush=True)
    generate_foundation_figures(root)
    _validate_figure_inventory(root)

    print("results", flush=True)
    write_results.main(recompute=args.full)
    results = json.loads((root / "results" / "results.json").read_text(encoding="utf-8"))
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
