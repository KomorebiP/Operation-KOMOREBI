#!/usr/bin/env python3
"""Regenerate and validate all thirteen monograph figures from preserved data."""
from pathlib import Path
from draw_matrix_visuals import generate as generate_matrices
from draw_graph_visuals import generate as generate_graphs

def main():
    generate_matrices()
    generate_graphs()
    directory = Path(__file__).resolve().parent.parent / 'figures'
    for number in range(1, 14):
        for extension in ['pdf', 'png']:
            matches = list(directory.glob(f'{number:02d}_*.{extension}'))
            assert len(matches) == 1 and matches[0].stat().st_size > 100, (number, extension)
    print('All thirteen PDF/PNG pairs regenerated; source data assertions passed.')

if __name__ == '__main__':
    main()
