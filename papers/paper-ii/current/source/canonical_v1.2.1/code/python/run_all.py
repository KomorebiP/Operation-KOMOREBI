from __future__ import annotations

import argparse
from pathlib import Path

from seed_refinement.experiments import run_experiments, write_numerical_summary
from seed_refinement.release_validation import compare_generated_records
from seed_refinement.visuals import make_visuals

PYTHON_ROOT = Path(__file__).resolve().parent
RELEASE_ROOT = PYTHON_ROOT.parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate Paper II numerical records and figure pairs."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=RELEASE_ROOT,
        help="root receiving results/ and paper/figures/",
    )
    parser.add_argument(
        "--compare-release-root",
        type=Path,
        help="semantically compare regenerated records with a frozen release",
    )
    arguments = parser.parse_args()

    output_root = arguments.output_root.resolve()
    results = run_experiments(output_root / "results" / "numerical_results.json")
    write_numerical_summary(results, output_root / "results" / "numerical_summary.csv")
    figures = make_visuals(output_root / "paper" / "figures")
    if len(figures) != 13 or len(set(figures)) != 13:
        raise RuntimeError(f"expected 13 unique figure stems, generated {len(figures)}")

    if arguments.compare_release_root is not None:
        frozen_root = arguments.compare_release_root.resolve()
        compare_generated_records(output_root, frozen_root)
        frozen_stems = {
            path.stem
            for path in (frozen_root / "paper" / "figures").glob("*.png")
        }
        if frozen_stems != set(figures):
            raise AssertionError(
                f"frozen figure stems differ: {frozen_stems ^ set(figures)}"
            )
        for stem in figures:
            for suffix in (".png", ".pdf"):
                generated = output_root / "paper" / "figures" / f"{stem}{suffix}"
                frozen = frozen_root / "paper" / "figures" / f"{stem}{suffix}"
                if not generated.is_file() or not frozen.is_file():
                    raise AssertionError(f"missing figure artifact for {stem}{suffix}")
        print("frozen numerical record comparison: PASS (9/9 summary rows)")

    print(f"generated {len(figures)} figure pairs")
    print(f"transfer-zeta walk coefficient match: {results['path_zeta']['match']}")


if __name__ == "__main__":
    main()
