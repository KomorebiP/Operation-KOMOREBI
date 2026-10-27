"""Command-line interface for the RRCT research prototype."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Sequence

import numpy as np

from . import __version__
from .agent import RRCTAgent
from .causal_exclusion import (
    V05_BOOTSTRAP_RESAMPLES,
    V05_BOOTSTRAP_SEED,
    V05_VALIDATION_SEEDS,
    run_causal_exclusion,
)
from .calibrated_intention_experiment import (
    V08_BOOTSTRAP_RESAMPLES,
    V08_BOOTSTRAP_SEED,
    V08_DEVELOPMENT_SEEDS,
    run_calibrated_intention_experiment,
)
from .environment import DelayedBindingEnvironment
from .endogenous_intention_experiment import (
    V07_DEVELOPMENT_SEEDS,
    run_endogenous_intention_experiment,
)
from .experiments import (
    DEFAULT_PREDICTOR_DOSES,
    DEFAULT_HYSTERESIS_GAINS,
    DEFAULT_LOCAL_DYNAMICS_GAINS,
    DEFAULT_PHASE_GAINS,
    DEFAULT_SURFACE_GAINS,
    DEFAULT_SWEEP_SEEDS,
    SELF_MODEL_CONDITIONS,
    V03_BOOTSTRAP_RESAMPLES,
    V03_VALIDATION_SEEDS,
    V04_BOOTSTRAP_RESAMPLES,
    V04_BOOTSTRAP_SEED,
    V04_VALIDATION_SEEDS,
    intervention_diagnostics,
    run_experiment,
    run_gain_surface,
    run_hysteresis_sweep,
    run_local_dynamics,
    run_path_decomposition,
    run_phase_sweep,
    run_predictor_mediation,
    run_seed_sweep,
)
from .predictor_dose import run_predictor_dose
from .self_access_experiment import (
    V06_DEVELOPMENT_BOOTSTRAP_RESAMPLES,
    V06_DEVELOPMENT_BOOTSTRAP_SEED,
    V06_DEVELOPMENT_SEEDS,
    run_self_access_experiment,
)
from .projectors import NestedOrthogonalProjectors


def _integer_token(value: str) -> tuple[int, ...]:
    try:
        parsed = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be comma-separated integers") from exc
    if not parsed:
        raise argparse.ArgumentTypeError("a seed token must not be empty")
    return parsed


def _float_token(value: str) -> tuple[float, ...]:
    try:
        parsed = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("gains must be comma-separated numbers") from exc
    if not parsed:
        raise argparse.ArgumentTypeError("a gain token must not be empty")
    return parsed


def _string_token(value: str) -> tuple[str, ...]:
    parsed = tuple(item.strip() for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("a condition token must not be empty")
    return parsed


def _flatten_tokens(values: Sequence[Sequence[object]]) -> tuple[object, ...]:
    return tuple(item for token in values for item in token)


def _verify() -> dict[str, object]:
    projector = NestedOrthogonalProjectors(12, ranks=(3, 6, 9, 12), seed=13)
    projector_audit = projector.validate(atol=1e-10)
    environment = DelayedBindingEnvironment(delay=3, noise=0.0, seed=19)
    episode = environment.sample()

    first = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=23)
    second = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=23)
    first_trace = np.asarray([first.step(x).feature_vector() for x in episode.observations])
    second_trace = np.asarray([second.step(x).feature_vector() for x in episode.observations])
    deterministic = bool(np.array_equal(first_trace, second_trace))

    full_intervention = intervention_diagnostics(seed=29, horizon=6)
    blocked_intervention = intervention_diagnostics(
        seed=29, ablations=("broadcast",), horizon=6
    )
    broadcast_blocked = bool(
        full_intervention.broadcast > blocked_intervention.broadcast
        and blocked_intervention.broadcast == 0.0
    )

    with tempfile.TemporaryDirectory(prefix="rrct_verify_") as directory:
        smoke = run_experiment(
            directory,
            seed=31,
            train_episode_count=16,
            test_episode_count=8,
            make_figures=False,
        )
        artifacts_exist = all(
            (Path(directory) / name).is_file()
            for name in ("summary.json", "ablations.csv")
        )

    checks = {
        "projector_filtration": bool(projector_audit["valid"]),
        "deterministic_replay": deterministic,
        "workspace_intervention_propagates": full_intervention.broadcast > 0.0,
        "broadcast_ablation_blocks_intervention": broadcast_blocked,
        "smoke_experiment_completed": len(smoke["results"]) == 8,
        "smoke_artifacts_created": artifacts_exist,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "version": __version__,
        "checks": checks,
        "projector_worst_error": projector_audit["worst_error"],
    }


def _inspect(seed: int) -> dict[str, object]:
    environment = DelayedBindingEnvironment(delay=4, noise=0.0, seed=seed + 1)
    episode = environment.sample()
    agent = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=seed)
    steps: list[dict[str, object]] = []
    for observation in episode.observations:
        result = agent.step(observation, source="inspect")
        steps.append(
            {
                "time": result.time,
                "resolution_level": result.resolution_level,
                "next_resolution_level": result.next_resolution_level,
                "selected_specialists": list(result.selected_specialists),
                "workspace_norm": float(np.linalg.norm(result.workspace)),
                "self_state_norm": float(np.linalg.norm(result.self_state)),
                "memory_size": agent.memory.size,
                "prediction_error_norm": result.error_norm,
            }
        )
    return {
        "version": __version__,
        "seed": seed,
        "latent_factors": {
            "context": episode.context,
            "object": episode.object_cue,
            "actuator": episode.actuator_map,
        },
        "steps": steps,
        "interpretation_boundary": (
            "This trace exposes causal architecture state. It is not a report "
            "of subjective experience."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rrct",
        description="Recursive Resolution Closure nonvalenced research prototype",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("verify", help="run deterministic internal verification")

    demo = subparsers.add_parser("demo", help="run matched ablations and diagnostics")
    demo.add_argument("--output", type=Path, default=Path("results_v0.4"))
    demo.add_argument("--seed", type=int, default=17)
    demo.add_argument("--train-episodes", type=int, default=256)
    demo.add_argument("--test-episodes", type=int, default=128)
    demo.add_argument("--no-figures", action="store_true")

    inspect = subparsers.add_parser("inspect", help="print one transparent causal trace")
    inspect.add_argument("--seed", type=int, default=17)

    seed_sweep = subparsers.add_parser(
        "seed-sweep",
        help="run fixed thresholds over every prespecified seed and self-model control",
    )
    seed_sweep.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.2_seed_sweep"),
        help="artifact directory (default: validation/v0.2_seed_sweep)",
    )
    seed_sweep.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(DEFAULT_SWEEP_SEEDS,),
        metavar="SEED[,SEED...]",
        help="comma- or space-separated seeds (default: 17,23,31,47)",
    )
    seed_sweep.add_argument(
        "--train-episodes", type=int, default=128, help="training episodes per run"
    )
    seed_sweep.add_argument(
        "--test-episodes", type=int, default=64, help="held-out episodes per run"
    )

    phase_sweep = subparsers.add_parser(
        "phase-sweep",
        help=(
            "sweep a shared recurrent and explicit closure gain without "
            "retuning thresholds"
        ),
    )
    phase_sweep.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.2_phase_sweep"),
        help="artifact directory (default: validation/v0.2_phase_sweep)",
    )
    phase_sweep.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(DEFAULT_SWEEP_SEEDS,),
        metavar="SEED[,SEED...]",
        help="comma- or space-separated seeds (default: 17,23,31,47)",
    )
    phase_sweep.add_argument(
        "--gains",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_PHASE_GAINS,),
        metavar="GAIN[,GAIN...]",
        help=(
            "shared recurrent/explicit-closure grid "
            "(default: 0,0.2,0.4,0.6,0.8,1.0,1.2)"
        ),
    )
    phase_sweep.add_argument(
        "--train-episodes", type=int, default=64, help="training episodes per run"
    )
    phase_sweep.add_argument(
        "--test-episodes", type=int, default=32, help="held-out episodes per run"
    )
    phase_sweep.add_argument(
        "--conditions",
        type=_string_token,
        nargs="+",
        default=(SELF_MODEL_CONDITIONS,),
        metavar="CONDITION[,CONDITION...]",
        help="self-model conditions (default: all three v0.2 controls)",
    )
    phase_sweep.add_argument(
        "--matched-predictor",
        action="store_true",
        help=(
            "train one standard-gain predictor snapshot per seed and hold it "
            "fixed across every gain (v0.3 dense-scan protocol)"
        ),
    )

    gain_surface = subparsers.add_parser(
        "gain-surface",
        help="map independent recurrent and explicit closure gains",
    )
    gain_surface.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.3_gain_surface"),
    )
    gain_surface.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V03_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    gain_surface.add_argument(
        "--recurrent-gains",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_SURFACE_GAINS,),
        metavar="GAIN[,GAIN...]",
    )
    gain_surface.add_argument(
        "--closure-gains",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_SURFACE_GAINS,),
        metavar="GAIN[,GAIN...]",
        help="explicit prior self/action feedback gain grid",
    )
    gain_surface.add_argument(
        "--conditions",
        type=_string_token,
        nargs="+",
        default=(("trained_self_model",),),
        metavar="CONDITION[,CONDITION...]",
    )
    gain_surface.add_argument("--train-episodes", type=int, default=32)
    gain_surface.add_argument("--test-episodes", type=int, default=16)
    gain_surface.add_argument(
        "--bootstrap-resamples", type=int, default=V03_BOOTSTRAP_RESAMPLES
    )

    hysteresis = subparsers.add_parser(
        "hysteresis-sweep",
        help=(
            "run matched joint recurrent/explicit-closure ramps as a "
            "path-dependence proxy"
        ),
    )
    hysteresis.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.3_hysteresis"),
    )
    hysteresis.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V03_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    hysteresis.add_argument(
        "--gains",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_HYSTERESIS_GAINS,),
        metavar="GAIN[,GAIN...]",
    )
    hysteresis.add_argument("--train-episodes", type=int, default=64)
    hysteresis.add_argument("--settle-cycles", type=int, default=8)
    hysteresis.add_argument("--measurement-cycles", type=int, default=4)
    hysteresis.add_argument("--drive-period", type=int, default=8)
    hysteresis.add_argument("--persistence-horizon", type=int, default=12)
    hysteresis.add_argument(
        "--bootstrap-resamples", type=int, default=V03_BOOTSTRAP_RESAMPLES
    )

    mediation = subparsers.add_parser(
        "predictor-mediation",
        help="compare trained, frozen, shuffled, and disabled predictor controls",
    )
    mediation.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.3_predictor_mediation"),
    )
    mediation.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V03_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    mediation.add_argument("--train-episodes", type=int, default=128)
    mediation.add_argument("--test-episodes", type=int, default=64)
    mediation.add_argument(
        "--bootstrap-resamples", type=int, default=V03_BOOTSTRAP_RESAMPLES
    )

    path_decomposition = subparsers.add_parser(
        "path-decomposition",
        help="run the matched 2x2x2 recurrence/self/action path factorial",
    )
    path_decomposition.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.4_path_decomposition"),
    )
    path_decomposition.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V04_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    path_decomposition.add_argument(
        "--recurrent-gains",
        type=_float_token,
        nargs="+",
        default=((0.0, 1.0),),
        metavar="GAIN[,GAIN...]",
    )
    path_decomposition.add_argument(
        "--self-feedback-gains",
        type=_float_token,
        nargs="+",
        default=((0.0, 1.0),),
        metavar="GAIN[,GAIN...]",
    )
    path_decomposition.add_argument(
        "--action-feedback-gains",
        type=_float_token,
        nargs="+",
        default=((0.0, 1.0),),
        metavar="GAIN[,GAIN...]",
    )
    path_decomposition.add_argument("--closure-gain", type=float, default=1.0)
    path_decomposition.add_argument("--train-episodes", type=int, default=64)
    path_decomposition.add_argument("--test-episodes", type=int, default=32)
    path_decomposition.add_argument("--train-delay", type=int, default=5)
    path_decomposition.add_argument("--test-delay", type=int, default=7)
    path_decomposition.add_argument(
        "--horizon",
        "--intervention-horizon",
        dest="intervention_horizon",
        type=int,
        default=12,
    )
    path_decomposition.add_argument(
        "--bootstrap-resamples", type=int, default=V04_BOOTSTRAP_RESAMPLES
    )
    path_decomposition.add_argument(
        "--bootstrap-seed", type=int, default=V04_BOOTSTRAP_SEED
    )

    local_dynamics = subparsers.add_parser(
        "local-dynamics",
        help="retain piecewise local transition Jacobians across recurrence gains",
    )
    local_dynamics.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.4_local_dynamics"),
    )
    local_dynamics.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V04_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    local_dynamics.add_argument(
        "--gains",
        "--recurrent-gains",
        dest="recurrent_gains",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_LOCAL_DYNAMICS_GAINS,),
        metavar="GAIN[,GAIN...]",
    )
    local_dynamics.add_argument("--closure-gain", type=float, default=1.0)
    local_dynamics.add_argument("--self-feedback-gain", type=float, default=1.0)
    local_dynamics.add_argument("--action-feedback-gain", type=float, default=1.0)
    local_dynamics.add_argument("--train-episodes", type=int, default=32)
    local_dynamics.add_argument("--train-delay", type=int, default=5)
    local_dynamics.add_argument("--test-delay", type=int, default=7)
    local_dynamics.add_argument("--warmup-episodes", type=int, default=1)
    local_dynamics.add_argument(
        "--epsilon",
        "--finite-difference-epsilon",
        dest="epsilon",
        type=float,
        default=1e-5,
    )
    local_dynamics.add_argument(
        "--horizon",
        "--intervention-horizon",
        "--persistence-horizon",
        dest="intervention_horizon",
        type=int,
        default=12,
    )
    local_dynamics.add_argument(
        "--bootstrap-resamples", type=int, default=V04_BOOTSTRAP_RESAMPLES
    )
    local_dynamics.add_argument(
        "--bootstrap-seed", type=int, default=V04_BOOTSTRAP_SEED
    )

    predictor_dose = subparsers.add_parser(
        "predictor-dose",
        help="test a spectrum-preserving predictor-organization dose",
    )
    predictor_dose.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.4_predictor_dose"),
    )
    predictor_dose.add_argument(
        "--seeds",
        type=_integer_token,
        nargs="+",
        default=(V04_VALIDATION_SEEDS,),
        metavar="SEED[,SEED...]",
    )
    predictor_dose.add_argument(
        "--doses",
        type=_float_token,
        nargs="+",
        default=(DEFAULT_PREDICTOR_DOSES,),
        metavar="DOSE[,DOSE...]",
    )
    predictor_dose.add_argument("--recurrent-gain", type=float, default=1.0)
    predictor_dose.add_argument("--closure-gain", type=float, default=1.0)
    predictor_dose.add_argument("--self-feedback-gain", type=float, default=1.0)
    predictor_dose.add_argument("--action-feedback-gain", type=float, default=1.0)
    predictor_dose.add_argument("--train-episodes", type=int, default=128)
    predictor_dose.add_argument("--test-episodes", type=int, default=64)
    predictor_dose.add_argument("--train-delay", type=int, default=5)
    predictor_dose.add_argument("--test-delay", type=int, default=7)
    predictor_dose.add_argument(
        "--horizon",
        "--intervention-horizon",
        "--persistence-horizon",
        dest="intervention_horizon",
        type=int,
        default=12,
    )
    predictor_dose.add_argument(
        "--bootstrap-resamples", type=int, default=V04_BOOTSTRAP_RESAMPLES
    )
    predictor_dose.add_argument(
        "--bootstrap-seed", type=int, default=V04_BOOTSTRAP_SEED
    )

    causal = subparsers.add_parser(
        "causal-exclusion",
        help="test hidden-intervention equivalence under exact baseline output replay",
    )
    causal.add_argument("--output", type=Path, default=Path("validation/v0.5_causal_exclusion"))
    causal.add_argument("--seeds", type=_integer_token, nargs="+", default=(V05_VALIDATION_SEEDS,))
    causal.add_argument("--train-episodes", type=int, default=128)
    causal.add_argument("--train-delay", type=int, default=5)
    causal.add_argument("--test-delay", type=int, default=7)
    causal.add_argument("--magnitude", type=float, default=0.35)
    causal.add_argument("--horizon", type=int, default=12)
    causal.add_argument("--bootstrap-resamples", type=int, default=V05_BOOTSTRAP_RESAMPLES)
    causal.add_argument("--bootstrap-seed", type=int, default=V05_BOOTSTRAP_SEED)

    self_access = subparsers.add_parser(
        "self-access-dev",
        help="run the nonconfirmatory prospective self-access control benchmark",
    )
    self_access.add_argument("--output", type=Path, default=Path("validation/v0.6_self_access_development"))
    self_access.add_argument("--seeds", type=_integer_token, nargs="+", default=(V06_DEVELOPMENT_SEEDS,))
    self_access.add_argument("--train-episodes", type=int, default=128)
    self_access.add_argument("--probes", type=int, default=8)
    self_access.add_argument("--train-delay", type=int, default=5)
    self_access.add_argument("--test-delay", type=int, default=7)
    self_access.add_argument("--future-horizon", type=int, default=4)
    self_access.add_argument("--directions", type=int, default=4)
    self_access.add_argument("--magnitude", type=float, default=0.35)
    self_access.add_argument("--bootstrap-resamples", type=int, default=V06_DEVELOPMENT_BOOTSTRAP_RESAMPLES)
    self_access.add_argument("--bootstrap-seed", type=int, default=V06_DEVELOPMENT_BOOTSTRAP_SEED)

    endogenous = subparsers.add_parser(
        "endogenous-intention-dev",
        help="run the development-only endogenous self-regulation benchmark",
    )
    endogenous.add_argument("--output", type=Path, default=Path("validation/v0.7_endogenous_intention_development"))
    endogenous.add_argument("--seeds", type=_integer_token, nargs="+", default=(V07_DEVELOPMENT_SEEDS,))
    endogenous.add_argument("--train-episodes", type=int, default=64)
    endogenous.add_argument("--probes", type=int, default=8)
    endogenous.add_argument("--horizon", type=int, default=4)
    endogenous.add_argument("--query-budget", type=int, default=4)
    endogenous.add_argument("--magnitude", type=float, default=0.35)
    endogenous.add_argument("--bootstrap-resamples", type=int, default=2000)
    endogenous.add_argument("--bootstrap-seed", type=int, default=20260824)

    calibrated = subparsers.add_parser(
        "calibrated-intention-dev",
        help="run the development-only learned-forecast by calibration benchmark",
    )
    calibrated.add_argument(
        "--output",
        type=Path,
        default=Path("validation/v0.8_calibrated_intention_development"),
    )
    calibrated.add_argument(
        "--seeds", type=_integer_token, nargs="+", default=(V08_DEVELOPMENT_SEEDS,)
    )
    calibrated.add_argument("--train-episodes", type=int, default=64)
    calibrated.add_argument("--calibration-episodes", type=int, default=32)
    calibrated.add_argument("--evaluation-episodes", type=int, default=32)
    calibrated.add_argument("--train-delay", type=int, default=5)
    calibrated.add_argument("--test-delay", type=int, default=7)
    calibrated.add_argument("--horizon", type=int, default=4)
    calibrated.add_argument("--query-budget", type=int, default=4)
    calibrated.add_argument("--magnitude", type=float, default=0.35)
    calibrated.add_argument("--calibration-alpha", type=float, default=0.05)
    calibrated.add_argument("--calibration-min-samples", type=int, default=19)
    calibrated.add_argument(
        "--bootstrap-resamples", type=int, default=V08_BOOTSTRAP_RESAMPLES
    )
    calibrated.add_argument("--bootstrap-seed", type=int, default=V08_BOOTSTRAP_SEED)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "verify":
        result = _verify()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1
    if args.command == "demo":
        result = run_experiment(
            args.output,
            seed=args.seed,
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            make_figures=not args.no_figures,
        )
        concise = {
            "status": result["status"],
            "output": str(args.output.resolve()),
            "full_signature": result["results"][0]["signature"],
            "targeted_losses": result["targeted_losses"],
            "artifacts": result["artifacts"],
            "interpretation_boundary": result["interpretation_boundary"],
        }
        print(json.dumps(concise, indent=2, sort_keys=True))
        return 0
    if args.command == "inspect":
        print(json.dumps(_inspect(args.seed), indent=2, sort_keys=True))
        return 0
    if args.command == "seed-sweep":
        result = run_seed_sweep(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
        )
        concise = {
            "status": result["status"],
            "experiment": result["experiment"],
            "output": str(args.output.resolve()),
            "run_count": len(result["runs"]),
            "parameters": result["parameters"],
            "threshold_policy": result["threshold_policy"],
            "artifacts": result["artifacts"],
            "interpretation_boundary": result["interpretation_boundary"],
        }
        print(json.dumps(concise, indent=2, sort_keys=True))
        return 0
    if args.command == "phase-sweep":
        result = run_phase_sweep(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            gains=tuple(float(value) for value in _flatten_tokens(args.gains)),
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            conditions=tuple(str(value) for value in _flatten_tokens(args.conditions)),
            matched_predictor=args.matched_predictor,
        )
        concise = {
            "status": result["status"],
            "experiment": result["experiment"],
            "output": str(args.output.resolve()),
            "run_count": len(result["runs"]),
            "parameters": result["parameters"],
            "threshold_policy": result["threshold_policy"],
            "artifacts": result["artifacts"],
            "interpretation_boundary": result["interpretation_boundary"],
        }
        print(json.dumps(concise, indent=2, sort_keys=True))
        return 0
    if args.command == "gain-surface":
        result = run_gain_surface(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            recurrent_gains=tuple(
                float(value) for value in _flatten_tokens(args.recurrent_gains)
            ),
            closure_gains=tuple(
                float(value) for value in _flatten_tokens(args.closure_gains)
            ),
            conditions=tuple(
                str(value) for value in _flatten_tokens(args.conditions)
            ),
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "hysteresis-sweep":
        result = run_hysteresis_sweep(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            gains=tuple(float(value) for value in _flatten_tokens(args.gains)),
            train_episode_count=args.train_episodes,
            settle_cycles=args.settle_cycles,
            measurement_cycles=args.measurement_cycles,
            drive_period=args.drive_period,
            persistence_horizon=args.persistence_horizon,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "predictor-mediation":
        result = run_predictor_mediation(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "path-decomposition":
        result = run_path_decomposition(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            recurrent_gains=tuple(
                float(value) for value in _flatten_tokens(args.recurrent_gains)
            ),
            self_feedback_gains=tuple(
                float(value) for value in _flatten_tokens(args.self_feedback_gains)
            ),
            action_feedback_gains=tuple(
                float(value) for value in _flatten_tokens(args.action_feedback_gains)
            ),
            closure_gain=args.closure_gain,
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            intervention_horizon=args.intervention_horizon,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "local-dynamics":
        result = run_local_dynamics(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            recurrent_gains=tuple(
                float(value) for value in _flatten_tokens(args.recurrent_gains)
            ),
            closure_gain=args.closure_gain,
            self_feedback_gain=args.self_feedback_gain,
            action_feedback_gain=args.action_feedback_gain,
            train_episode_count=args.train_episodes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            warmup_episode_count=args.warmup_episodes,
            epsilon=args.epsilon,
            intervention_horizon=args.intervention_horizon,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "predictor-dose":
        result = run_predictor_dose(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            doses=tuple(float(value) for value in _flatten_tokens(args.doses)),
            recurrent_gain=args.recurrent_gain,
            closure_gain=args.closure_gain,
            self_feedback_gain=args.self_feedback_gain,
            action_feedback_gain=args.action_feedback_gain,
            train_episode_count=args.train_episodes,
            test_episode_count=args.test_episodes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            intervention_horizon=args.intervention_horizon,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "experiment": result["experiment"],
                    "output": str(args.output.resolve()),
                    "run_count": len(result["runs"]),
                    "parameters": result["parameters"],
                    "artifacts": result["artifacts"],
                    "interpretation_boundary": result["interpretation_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "causal-exclusion":
        result = run_causal_exclusion(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            magnitude=args.magnitude,
            horizon=args.horizon,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(json.dumps({
            "status": result["status"],
            "experiment": result["experiment"],
            "output": str(args.output.resolve()),
            "gates": result["gates"],
            "warranted_claim": result["warranted_claim"],
            "interpretation_boundary": result["interpretation_boundary"],
        }, indent=2, sort_keys=True))
        return 0
    if args.command == "self-access-dev":
        result = run_self_access_experiment(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            probe_count=args.probes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            future_horizon=args.future_horizon,
            direction_count=args.directions,
            candidate_magnitude=args.magnitude,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(json.dumps({
            "status": result["status"], "output": str(args.output.resolve()),
            "row_count": result["row_count"],
            "confirmatory_claim_allowed": result["confirmatory_claim_allowed"],
            "interpretation_boundary": result["interpretation_boundary"],
        }, indent=2, sort_keys=True))
        return 0
    if args.command == "endogenous-intention-dev":
        result = run_endogenous_intention_experiment(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            probe_count=args.probes,
            horizon=args.horizon,
            query_budget=args.query_budget,
            candidate_magnitude=args.magnitude,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(json.dumps({
            "status": result["status"],
            "output": str(args.output.resolve()),
            "confirmatory_claim_allowed": result["confirmatory_claim_allowed"],
            "metrics": result["metrics"],
            "interpretation_boundary": result["interpretation_boundary"],
        }, indent=2, sort_keys=True))
        return 0
    if args.command == "calibrated-intention-dev":
        result = run_calibrated_intention_experiment(
            args.output,
            seeds=tuple(int(value) for value in _flatten_tokens(args.seeds)),
            train_episode_count=args.train_episodes,
            calibration_episode_count=args.calibration_episodes,
            evaluation_episode_count=args.evaluation_episodes,
            train_delay=args.train_delay,
            test_delay=args.test_delay,
            horizon=args.horizon,
            query_budget=args.query_budget,
            candidate_magnitude=args.magnitude,
            calibration_alpha=args.calibration_alpha,
            calibration_min_samples=args.calibration_min_samples,
            bootstrap_resamples=args.bootstrap_resamples,
            bootstrap_seed=args.bootstrap_seed,
        )
        print(json.dumps({
            "status": result["status"],
            "output": str(args.output.resolve()),
            "confirmatory_claim_allowed": result["confirmatory_claim_allowed"],
            "contrasts": result["contrasts"],
            "interpretation_boundary": result["interpretation_boundary"],
        }, indent=2, sort_keys=True))
        return 0
    raise RuntimeError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
