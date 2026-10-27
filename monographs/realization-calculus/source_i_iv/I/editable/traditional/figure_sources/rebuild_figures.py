#!/usr/bin/env python3
"""Rebuild the ten main-text figures with their original mathematical data."""
from pathlib import Path
import draw_diagrams
import draw_numeric
import draw_ranks
import draw_shift

def main():
    draw_diagrams.main()
    numeric = draw_numeric.generate()
    draw_ranks.generate()
    draw_shift.draw_shift()
    transport = numeric["coordinate_transport"]
    assert transport["max_idempotence_residual"] < 1e-11
    assert transport["max_annihilation_residual"] < 1e-11
    figures = Path(__file__).resolve().parent.parent / "figures"
    stems = sorted(p.stem for p in figures.glob("[0-9][0-9]_*.pdf"))
    assert len(stems) == 10
    assert all((figures / (s+".png")).is_file() for s in stems)
    print("Rebuilt all ten main-text figures. Figure data checks passed.")

if __name__ == "__main__":
    main()
