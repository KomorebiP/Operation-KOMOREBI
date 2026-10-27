from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from .examples import (
    AnalyticExpressionSystem,
    DyadicLimitSystem,
    IntegerWalkSystem,
    PolynomialDeformationSystem,
    fibonacci_numbers,
)
from .extended_examples import (
    AffineShapeSystem,
    CongruenceLiftSystem,
    GaussianFamilySystem,
    GraphDeformationSystem,
    MatrixDeformationSystem,
    QubitGateSystem,
    SequenceTransformSystem,
    path_graph,
    triangle_seed,
)
from .experiments import run_all
from .forest import PerturbationForest
from .model import ExplorationConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="generative-deformation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-all", help="run all reference experiments")
    run_parser.add_argument("--base", default=".")

    explore_parser = subparsers.add_parser("explore", help="explore a built-in deformation system")
    explore_parser.add_argument(
        "--example",
        choices=[
            "walk", "dyadic", "polynomial", "analytic", "sequence",
            "gaussian", "qubit", "matrix", "shape", "graph",
            "adic-simple", "adic-singular",
        ],
        required=True,
    )
    explore_parser.add_argument("--depth", type=int, default=4)
    explore_parser.add_argument("--max-paths", type=int, default=5000)
    explore_parser.add_argument("--out", default="exploration_output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run-all":
        summary = run_all(Path(args.base))
        print(json.dumps(summary, indent=2))
        return 0

    x = sp.Symbol("x")
    if args.example == "walk":
        system, seeds = IntegerWalkSystem(), [0]
    elif args.example == "dyadic":
        system, seeds = DyadicLimitSystem(), [Fraction(0)]
    elif args.example == "polynomial":
        system, seeds = PolynomialDeformationSystem(x), [x**2 + 1]
    elif args.example == "analytic":
        system, seeds = AnalyticExpressionSystem(x), [sp.cosh(x)]
    elif args.example == "sequence":
        system, seeds = SequenceTransformSystem(length=8), [tuple(fibonacci_numbers(8))]
    elif args.example == "gaussian":
        system, seeds = GaussianFamilySystem(), [(Fraction(0), Fraction(1))]
    elif args.example == "qubit":
        system, seeds = QubitGateSystem(), [(0, 0, 1)]
    elif args.example == "matrix":
        system, seeds = MatrixDeformationSystem(), [((1, 1), (0, 1))]
    elif args.example == "shape":
        system, seeds = AffineShapeSystem(), [triangle_seed()]
    elif args.example == "graph":
        system, seeds = GraphDeformationSystem(node_cap=6), [path_graph(3)]
    elif args.example == "adic-simple":
        system = CongruenceLiftSystem(3, "square_one", depth_cap=max(2, args.depth + 1))
        seeds = system.residual_seeds()
    else:
        system = CongruenceLiftSystem(2, "square_zero", depth_cap=max(2, args.depth + 1))
        seeds = system.residual_seeds()
    forest = PerturbationForest(system, seeds).explore(
        ExplorationConfig(max_depth=args.depth, max_paths=args.max_paths)
    )
    forest.export(args.out)
    print(json.dumps(forest.summary(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
