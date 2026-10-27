"""Launch the frozen engine with fresh workers instead of inheriting checkpoints.

This changes process startup only. Compiler code, budgets and checkpoint bindings
remain those of engine.py. Author: Komorebi P.
"""
import argparse
import multiprocessing
from pathlib import Path
import engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--challenges', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--include-new', action='store_true')
    args = parser.parse_args()
    multiprocessing.set_start_method('spawn')
    engine.scan(engine.read(args.challenges), args.output, args.workers, args.include_new)


if __name__ == '__main__':
    main()
