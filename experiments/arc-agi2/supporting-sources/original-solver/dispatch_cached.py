"""Read plain or compressed census data and call the unchanged dispatcher.
Author: Komorebi P.
"""
import argparse
from pathlib import Path
import engine
import solver
import storage


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--challenges', type=Path, required=True)
    parser.add_argument('--census', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--policy', choices=solver.POLICIES, default=solver.PRIMARY)
    args = parser.parse_args()
    result = solver.dispatch(engine.read(args.challenges), storage.read(args.census), args.policy)
    engine.write(args.output, result)
