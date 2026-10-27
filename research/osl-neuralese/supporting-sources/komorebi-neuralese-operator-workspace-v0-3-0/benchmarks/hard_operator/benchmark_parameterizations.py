"""Development-only timing/trainability comparison for hard operator maps.

This script is intentionally separate from the frozen experiment runner.  It
prints JSON to stdout and does not write checkpoints or evaluation artifacts.
Run from the v0.3 package root with its ``src`` directory on ``PYTHONPATH``.
"""

from __future__ import annotations

import argparse
import json
import time

import torch

from komorebi_neuralese.hard_operator import HardMetricOperatorRNN
from komorebi_neuralese.closure import deep_accuracy_stability, operator_geometry_metrics
from komorebi_neuralese.train import TrainConfig, train_arm


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("qr", "matrix_exp", "cayley", "polar"), required=True)
    parser.add_argument("--seed", type=int, default=779)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=8e-4)
    parser.add_argument("--operator-init-std", type=float, default=0.08)
    parser.add_argument("--composition-weight", type=float, default=0.3)
    parser.add_argument("--examples", type=int, default=128)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--eval-seed", type=int, default=9002)
    return parser


def main() -> None:
    args = _parser().parse_args()
    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    model = HardMetricOperatorRNN(parameterization=args.backend)
    torch.nn.init.normal_(model.operator_encoder.weight, std=args.operator_init_std)
    config = TrainConfig(
        model_name="linear_hyper_hard_metric",
        regime="metric",
        seed=args.seed,
        steps=args.steps,
        batch_size=args.batch_size,
        train_max_length=4,
        max_eval_length=128,
        learning_rate=args.learning_rate,
        weight_decay=1e-6,
        grad_clip=1.0,
        metric_isometry_weight=0.0,
        composition_weight=args.composition_weight,
        composition_min_length=2,
        composition_max_length=4,
        device="cpu",
    )
    started = time.perf_counter()
    trained = train_arm(model, config)
    train_wall = time.perf_counter() - started
    stability = deep_accuracy_stability(
        trained.model,
        family="d4",
        depths=(8, 32, 64, 128),
        examples_per_depth=args.examples,
        batch_size=args.examples,
        seed=args.eval_seed,
        device="cpu",
        coordinate_split="dev",
        neighbor_offsets=(0,),
    )
    c8 = deep_accuracy_stability(
        trained.model,
        family="c8",
        depths=(64,),
        examples_per_depth=args.examples,
        batch_size=args.examples,
        seed=args.eval_seed + 1,
        device="cpu",
        coordinate_split="dev",
        neighbor_offsets=(0,),
    )
    geometry = operator_geometry_metrics(
        trained.model,
        family="d4",
        examples=args.examples,
        batch_size=args.examples,
        seed=args.eval_seed + 2,
        device="cpu",
        coordinate_split="dev",
    )
    by_depth = stability["by_depth"]
    record = {
        "development_only": True,
        "backend": args.backend,
        "seed": args.seed,
        "steps": args.steps,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "operator_init_std": args.operator_init_std,
        "composition_weight": args.composition_weight,
        "examples": args.examples,
        "train_seconds": train_wall,
        "final_loss": trained.final_loss,
        "parameter_count": trained.parameter_count,
        "d4_accuracy": {depth: by_depth[depth]["endpoint_accuracy"] for depth in ("8", "32", "64", "128")},
        "d4_g_endpoint_ratio_128": by_depth["128"]["g_endpoint_ratio"],
        "c8_accuracy_64": c8["by_depth"]["64"]["endpoint_accuracy"],
        "isometry_defect_p95": geometry["aggregate"]["normalized_g_isometry_defect_p95"],
        "whitened_minimum_singular_value": geometry["aggregate"]["whitened_minimum_singular_value"],
        "whitened_maximum_singular_value": geometry["aggregate"]["whitened_maximum_singular_value"],
        "metric_condition_number": geometry["metric"]["condition_number"],
        "trajectory": trained.trajectory,
    }
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
