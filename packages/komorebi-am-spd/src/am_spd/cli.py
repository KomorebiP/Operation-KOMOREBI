from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from . import __version__, atlas
from .api import AMSpdConfig, config_from_mapping, reconstruct, resume_model
from .batch import run_batch
from .benchmark import BUILTIN_CASES, METHODS, run_builtin_benchmark
from .components import compare_baselines, complete_with_pixels
from .io import load_image, save_image
from .model import SCHEMA_VERSION, AMSpdModel
from .reference import PAPER_CASES, reproduce_paper
from .tiled import (
    TILED_SCHEMA_VERSION,
    TiledAMSpdModel,
    TiledConfig,
    compare_model_archives,
    load_model_archive,
    resume_tiled_model,
    tiled_reconstruct,
)
from .tuning import auto_tune, tuning_candidates
from .verification import run_full_verification, run_smoke_verification


def _apply_config_overrides(args: argparse.Namespace, base: AMSpdConfig) -> AMSpdConfig:
    values = {
        "method": getattr(args, "method", None) or base.method,
        "packet_budget": getattr(args, "packet_budget", None),
        "singular_budget": getattr(args, "singular_budget", None),
        "parameter_budget": getattr(args, "parameter_budget", None),
        "tree_depth": getattr(args, "tree_depth", None),
        "max_rank": getattr(args, "max_rank", None),
        "max_actions": getattr(args, "max_actions", None),
        "max_regions": getattr(args, "max_regions", None),
        "random_seed": getattr(args, "seed", None),
        "complexity_weight": getattr(args, "complexity_weight", None),
        "max_candidates_per_iteration": getattr(args, "max_candidates", None),
        "residual_refresh": getattr(args, "residual_refresh", None),
        "quadtree_refine_every": getattr(args, "quadtree_refine_every", None),
        "tolerance": getattr(args, "tolerance", None),
    }
    reopen = getattr(args, "reopen_fractions", None)
    if reopen:
        values["reopen_fractions"] = tuple(reopen)
    return replace(base, **{key: value for key, value in values.items() if value is not None})


def _config(args: argparse.Namespace, base: AMSpdConfig | None = None) -> AMSpdConfig:
    if base is None:
        method = getattr(args, "method", None) or "portfolio"
        preset = getattr(args, "preset", None) or "quick"
        base = AMSpdConfig.quick(method) if preset == "quick" else AMSpdConfig.paper_scale(method)
    elif getattr(args, "preset", None):
        method = getattr(args, "method", None) or base.method
        base = AMSpdConfig.quick(method) if args.preset == "quick" else AMSpdConfig.paper_scale(method)
    return _apply_config_overrides(args, base)


def _add_reconstruction_options(
    parser: argparse.ArgumentParser,
    *,
    optional_method: bool = False,
    optional_preset: bool = False,
) -> None:
    parser.add_argument(
        "--preset",
        choices=("quick", "paper-scale", "paper"),
        default=None if optional_preset else "quick",
    )
    parser.add_argument(
        "--method",
        choices=("core", "spd", "tree", "portfolio"),
        default=None if optional_method else "portfolio",
    )
    parser.add_argument("--packet-budget", type=int)
    parser.add_argument("--singular-budget", type=int)
    parser.add_argument("--parameter-budget", type=int)
    parser.add_argument("--tree-depth", type=int)
    parser.add_argument("--max-rank", type=int)
    parser.add_argument("--max-actions", type=int)
    parser.add_argument("--max-regions", type=int)
    parser.add_argument("--reopen-fractions", type=float, nargs="+")
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument("--complexity-weight", type=float)
    parser.add_argument("--residual-refresh", type=int)
    parser.add_argument("--quadtree-refine-every", type=int)
    parser.add_argument("--tolerance", type=float)
    parser.add_argument("--seed", type=int)


def _add_model_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--residual-storage", choices=("dense", "sparse", "none"), default="sparse")
    parser.add_argument("--residual-threshold", type=float, default=0.0)
    parser.add_argument("--include-input", action="store_true")
    parser.add_argument("--omit-atoms", action="store_true")
    parser.add_argument("--omit-directions", action="store_true")


def _add_tiled_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tile-size", type=int, default=128)
    parser.add_argument("--overlap", type=int, default=16)
    parser.add_argument("--blend", choices=("cosine", "linear", "uniform"), default="cosine")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--omit-tile-models", action="store_true")


def _tiled_config(args: argparse.Namespace) -> TiledConfig:
    return TiledConfig(
        tile_size=args.tile_size,
        overlap=args.overlap,
        blend=args.blend,
        workers=args.workers,
    )


def _write_array_or_image(path: Path, value: np.ndarray) -> Path:
    if path.suffix.lower() == ".npy":
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, value, allow_pickle=False)
        return path
    return save_image(path, value)


def _save_model(
    result: Any,
    path: Path,
    args: argparse.Namespace,
    provenance: dict[str, Any],
    *,
    include_input: bool | None = None,
) -> Path:
    return result.save_model(
        path,
        residual_storage=args.residual_storage,
        residual_threshold=args.residual_threshold,
        include_input=args.include_input if include_input is None else include_input,
        include_atoms=not args.omit_atoms,
        include_directions=not args.omit_directions,
        provenance=provenance,
    )


def _write_outputs(
    result: Any,
    output: Path,
    archive: Path | None,
    summary: Path | None,
    model: Path | None = None,
    model_args: argparse.Namespace | None = None,
) -> dict[str, Any]:
    image_path = save_image(output, result.bounded_reconstruction())
    archive_path = archive or output.with_suffix(".npz")
    summary_path = summary or output.with_suffix(".json")
    result.save_archive(archive_path)
    summary_path.write_text(json.dumps(result.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    model_path = None
    if model is not None:
        if model_args is None:
            raise ValueError("model options are required when writing a model")
        model_path = _save_model(result, model, model_args, {"mode": "reconstruct-cli"})
    payload = {
        "image": str(image_path),
        "archive": str(archive_path),
        "summary": str(summary_path),
        "model": str(model_path) if model_path is not None else None,
        **result.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def command_reconstruct(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    result = reconstruct(image, _config(args))
    _write_outputs(result, args.output, args.archive, args.summary, args.model, args)
    return 0


def command_decompose(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    result = reconstruct(image, _config(args))
    model_path = _save_model(result, args.model, args, {"mode": "decompose-cli", "input": str(args.input)})
    preview_path = save_image(args.preview, result.bounded_reconstruction()) if args.preview is not None else None
    model = AMSpdModel.load(model_path)
    payload = {
        "model": str(model_path),
        "preview": str(preview_path) if preview_path is not None else None,
        "model_summary": model.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_resume(args: argparse.Namespace) -> int:
    source = load_model_archive(args.source_model)
    base = config_from_mapping(source.config)
    settings = _config(args, base=base)

    if isinstance(source, TiledAMSpdModel):
        result = resume_tiled_model(
            source,
            additional_packets=args.additional_packets,
            target_packet_budget=args.target_packet_budget,
            method=settings.method,
            config=settings,
            workers=args.workers,
        )
        model_path = result.save_model(
            args.output_model,
            residual_storage=args.residual_storage,
            residual_threshold=args.residual_threshold,
            include_input=args.include_input or source.input_image is not None,
            include_tile_models=not args.omit_tile_models,
            include_atoms=not args.omit_atoms,
            include_directions=not args.omit_directions,
            provenance={
                "mode": "resume-tiled-cli",
                "source_model": str(args.source_model),
                "source_model_schema": source.schema_version,
                "resume_state_quality": source.resume_state_quality,
            },
        )
        source_format = "tiled"
    else:
        result = resume_model(
            source,
            settings,
            additional_packets=args.additional_packets,
            target_packet_budget=args.target_packet_budget,
        )
        model_path = _save_model(
            result,
            args.output_model,
            args,
            {
                "mode": "resume-cli",
                "source_model": str(args.source_model),
                "source_model_schema": source.schema_version,
                "resume_state_quality": source.resume_state_quality,
            },
            include_input=args.include_input or source.input_image is not None,
        )
        source_format = "single"

    preview = save_image(args.preview, result.bounded_reconstruction()) if args.preview is not None else None
    summary_path = None
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(result.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary_path = args.summary
    payload = {
        "source_model": str(args.source_model),
        "source_format": source_format,
        "output_model": str(model_path),
        "preview": str(preview) if preview is not None else None,
        "summary_file": str(summary_path) if summary_path is not None else None,
        "source_resume_state_quality": source.resume_state_quality,
        "result": result.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_tiled(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    result = tiled_reconstruct(image, _config(args), _tiled_config(args))
    model_path = result.save_model(
        args.model,
        residual_storage=args.residual_storage,
        residual_threshold=args.residual_threshold,
        include_input=args.include_input,
        include_tile_models=not args.omit_tile_models,
        include_atoms=not args.omit_atoms,
        include_directions=not args.omit_directions,
        provenance={"mode": "tiled-cli", "input": str(args.input)},
    )
    preview = save_image(args.preview, result.bounded_reconstruction()) if args.preview is not None else None
    summary_path = None
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(result.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary_path = args.summary
    payload = {
        "model": str(model_path),
        "preview": str(preview) if preview is not None else None,
        "summary_file": str(summary_path) if summary_path is not None else None,
        "result": result.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_decode(args: argparse.Namespace) -> int:
    if args.mode == "exact" and args.output.suffix.lower() != ".npy":
        raise ValueError("exact decode requires a .npy output; use --mode bounded for an 8-bit display preview")
    model = load_model_archive(args.model)
    value = model.decode(args.mode)
    output = _write_array_or_image(args.output, value)
    payload = {"model": str(args.model), "mode": args.mode, "output": str(output), "summary": model.summary()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_convert_archive(args: argparse.Namespace) -> int:
    model = AMSpdModel.from_legacy_archive(
        args.archive,
        residual_storage=args.residual_storage,
        residual_threshold=args.residual_threshold,
    )
    destination = model.save(args.model)
    payload = {"source_archive": str(args.archive), "model": str(destination), "verification": model.verify()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    model = load_model_archive(args.model)
    payload: dict[str, Any] = {"summary": model.summary(), "verification": model.verify()}
    if isinstance(model, AMSpdModel):
        if args.packets:
            payload["packets"] = model.packet_table()
        if args.trees:
            payload["trees"] = model.tree_table()
            payload["exact_frontier"] = model.exact_frontier
        if args.trials:
            payload["portfolio_trials"] = model.portfolio_trials
            payload["replacement_blocks"] = model.replacement_blocks
        if args.search:
            payload["search_state"] = model.search_state
    elif isinstance(model, TiledAMSpdModel):
        payload["tiles"] = model.tile_table()
        if args.packets or args.trees or args.trials:
            payload["embedded_tiles"] = [tile.summary() for tile in model.tile_models]
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    payload = compare_model_archives(args.models)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


def command_complete(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    result = reconstruct(image, _config(args))
    closure = complete_with_pixels(result, threshold=args.residual_threshold)
    model_path = result.save_model(
        args.model,
        residual_storage="sparse",
        residual_threshold=args.residual_threshold,
        include_input=args.include_input,
        include_atoms=not args.omit_atoms,
        include_directions=not args.omit_directions,
        provenance={
            "mode": "pixel-coordinate-completion",
            "pixel_packet_count": closure.pixel_packet_count,
            "scalar_coefficient_count": closure.scalar_coefficient_count,
        },
    )
    preview_path = _write_array_or_image(args.preview, closure.decode()) if args.preview is not None else None
    payload = {
        "model": str(model_path),
        "preview": str(preview_path) if preview_path is not None else None,
        "pixel_packet_count": closure.pixel_packet_count,
        "scalar_coefficient_count": closure.scalar_coefficient_count,
        "identity_error": closure.identity_error(image),
        "base_summary": result.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_tune(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    first_method = args.methods[0]
    base = (
        AMSpdConfig.paper_scale(first_method)
        if args.preset in {"paper-scale", "paper"}
        else AMSpdConfig.quick(first_method)
    )
    base = _apply_config_overrides(args, base)
    candidates = tuning_candidates(
        base,
        methods=args.methods,
        packet_budgets=args.packet_budgets,
        singular_budgets=args.singular_budgets,
        tree_depths=args.tree_depths,
        max_ranks=args.max_ranks,
    )
    tuned = auto_tune(
        image,
        candidates,
        objective=args.objective,
        rate_weight=args.rate_weight,
        target_rmse=args.target_rmse,
        max_parameters=args.max_parameters,
    )
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    report_path = tuned.save_report(destination / "tuning.json")
    csv_path = tuned.save_csv(destination / "tuning.csv")
    preview_path = save_image(args.preview or destination / "best-reconstruction.png", tuned.best_result.bounded_reconstruction())
    model_path = None
    if args.model is not None or args.save_model:
        model_path = _save_model(
            tuned.best_result,
            args.model or destination / "best.amspd",
            args,
            {
                "mode": "automatic-budget-selection",
                "objective": args.objective,
                "candidate_count": len(tuned.records),
            },
        )
    payload = {
        "report": str(report_path),
        "csv": str(csv_path),
        "preview": str(preview_path),
        "model": str(model_path) if model_path is not None else None,
        **tuned.summary(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_batch(args: argparse.Namespace) -> int:
    settings = _config(args)
    tiled_config = None
    if args.force_tiled or args.tiled_above is not None:
        tiled_config = TiledConfig(
            tile_size=args.tile_size,
            overlap=args.overlap,
            blend=args.blend,
            workers=args.tile_workers,
        )
    result = run_batch(
        args.source,
        args.output_dir,
        settings,
        recursive=not args.no_recursive,
        workers=args.workers,
        save_models=args.save_models,
        include_input_in_models=args.include_input,
        residual_storage=args.residual_storage,
        tile_config=tiled_config,
        tiled_above=None if args.force_tiled else args.tiled_above,
        save_tile_models=args.embed_tile_models,
        skip_existing=args.skip_existing,
        fail_fast=args.fail_fast,
    )
    print(json.dumps(result.summary(), indent=2, sort_keys=True))
    return 0 if result.passed else 1


def command_demo(args: argparse.Namespace) -> int:
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    image = atlas.synthetic_geometry(args.size)
    save_image(destination / "input.png", image)
    result = reconstruct(image, _config(args))
    _write_outputs(
        result,
        destination / "reconstruction.png",
        destination / "reconstruction.npz",
        destination / "summary.json",
        destination / "reconstruction.amspd" if args.save_model else None,
        args,
    )
    residual = np.abs(result.archive_residual)
    scale = max(float(residual.max()), 1e-15)
    save_image(destination / "residual_magnitude.png", residual / scale)
    return 0


def command_baselines(args: argparse.Namespace) -> int:
    image = load_image(args.input)
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    results = compare_baselines(
        image,
        coefficient_budget=args.coefficient_budget,
        svd_rank=args.svd_rank,
        quadtree_leaves=args.quadtree_leaves,
        tv_weight=args.tv_weight,
    )
    payload: dict[str, Any] = {}
    for name, result in results.items():
        path = save_image(destination / f"{name}.png", atlas.bounded_synthesis(result.reconstruction))
        payload[name] = {"image": str(path), "budget": result.budget, "notes": result.notes, "metrics": result.metrics}
    (destination / "baselines.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_benchmark(args: argparse.Namespace) -> int:
    report = run_builtin_benchmark(
        args.output_dir,
        cases=args.cases,
        methods=args.methods,
        preset=args.preset,
        size=args.size,
        save_models=args.save_models,
        include_input_in_models=args.include_input,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def command_reproduce_paper(args: argparse.Namespace) -> int:
    if args.list_cases:
        print(json.dumps({"paper_cases": PAPER_CASES}, indent=2))
        return 0
    report = reproduce_paper(
        args.output_dir,
        cases=args.cases,
        strict_reference=args.strict_reference,
        include_input=args.include_input,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_reference_matches"] or not args.strict_reference else 1


def command_verify(args: argparse.Namespace) -> int:
    report = run_full_verification(paper_case=args.paper_case) if args.full else run_smoke_verification()
    print(report.to_json())
    return 0 if report.passed else 1


def command_info(_: argparse.Namespace) -> int:
    payload = {
        "package": "komorebi-am-spd",
        "version": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "model_formats": {
            "single": {"name": "komorebi-am-spd-model", "schema_version": SCHEMA_VERSION},
            "tiled": {"name": "komorebi-am-spd-tiled-model", "schema_version": TILED_SCHEMA_VERSION},
        },
        "commands": [
            "reconstruct",
            "decompose",
            "resume",
            "tiled",
            "tune",
            "batch",
            "decode",
            "convert-archive",
            "inspect",
            "compare",
            "complete",
            "baselines",
            "benchmark",
            "reproduce-paper",
            "demo",
            "verify",
            "info",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="am-spd", description="Adaptive Multiscale Singular Packet Decomposition")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reconstruct_parser = subparsers.add_parser("reconstruct", help="reconstruct an image file")
    reconstruct_parser.add_argument("input", type=Path)
    reconstruct_parser.add_argument("output", type=Path)
    reconstruct_parser.add_argument("--archive", type=Path)
    reconstruct_parser.add_argument("--summary", type=Path)
    reconstruct_parser.add_argument("--model", type=Path)
    _add_reconstruction_options(reconstruct_parser)
    _add_model_options(reconstruct_parser)
    reconstruct_parser.set_defaults(handler=command_reconstruct)

    decompose_parser = subparsers.add_parser("decompose", help="fit AM-SPD and write a portable .amspd model")
    decompose_parser.add_argument("input", type=Path)
    decompose_parser.add_argument("model", type=Path)
    decompose_parser.add_argument("--preview", type=Path)
    _add_reconstruction_options(decompose_parser)
    _add_model_options(decompose_parser)
    decompose_parser.set_defaults(handler=command_decompose)

    resume_parser = subparsers.add_parser("resume", help="continue a saved packet search")
    resume_parser.add_argument("source_model", type=Path)
    resume_parser.add_argument("output_model", type=Path)
    resume_parser.add_argument("--additional-packets", type=int, default=8)
    resume_parser.add_argument("--target-packet-budget", type=int)
    resume_parser.add_argument("--preview", type=Path)
    resume_parser.add_argument("--summary", type=Path)
    resume_parser.add_argument("--workers", type=int, default=1, help="workers for tiled-model continuation")
    resume_parser.add_argument("--omit-tile-models", action="store_true", help="do not embed resumable tile checkpoints")
    _add_reconstruction_options(resume_parser, optional_method=True, optional_preset=True)
    _add_model_options(resume_parser)
    resume_parser.set_defaults(handler=command_resume)

    tiled_parser = subparsers.add_parser("tiled", help="reconstruct a large image with overlap-blended AM-SPD tiles")
    tiled_parser.add_argument("input", type=Path)
    tiled_parser.add_argument("model", type=Path)
    tiled_parser.add_argument("--preview", type=Path)
    tiled_parser.add_argument("--summary", type=Path)
    _add_reconstruction_options(tiled_parser)
    _add_model_options(tiled_parser)
    _add_tiled_options(tiled_parser)
    tiled_parser.set_defaults(handler=command_tiled)

    decode_parser = subparsers.add_parser("decode", help="decode a saved .amspd or .amspdt model")
    decode_parser.add_argument("model", type=Path)
    decode_parser.add_argument("output", type=Path)
    decode_parser.add_argument("--mode", choices=("raw", "bounded", "exact"), default="bounded")
    decode_parser.set_defaults(handler=command_decode)

    convert_parser = subparsers.add_parser("convert-archive", help="convert a version 0.1.x reconstruction .npz archive")
    convert_parser.add_argument("archive", type=Path)
    convert_parser.add_argument("model", type=Path)
    convert_parser.add_argument("--residual-storage", choices=("dense", "sparse", "none"), default="sparse")
    convert_parser.add_argument("--residual-threshold", type=float, default=0.0)
    convert_parser.set_defaults(handler=command_convert_archive)

    inspect_parser = subparsers.add_parser("inspect", help="inspect a saved .amspd or .amspdt model")
    inspect_parser.add_argument("model", type=Path)
    inspect_parser.add_argument("--packets", action="store_true")
    inspect_parser.add_argument("--trees", action="store_true")
    inspect_parser.add_argument("--trials", action="store_true")
    inspect_parser.add_argument("--search", action="store_true")
    inspect_parser.add_argument("--output", type=Path)
    inspect_parser.set_defaults(handler=command_inspect)

    compare_parser = subparsers.add_parser("compare", help="compare two or more AM-SPD model archives")
    compare_parser.add_argument("models", type=Path, nargs="+")
    compare_parser.add_argument("--output", type=Path)
    compare_parser.set_defaults(handler=command_compare)

    complete_parser = subparsers.add_parser("complete", help="store exact finite pixel-coordinate residual closure")
    complete_parser.add_argument("input", type=Path)
    complete_parser.add_argument("model", type=Path)
    complete_parser.add_argument("--preview", type=Path)
    _add_reconstruction_options(complete_parser)
    _add_model_options(complete_parser)
    complete_parser.set_defaults(handler=command_complete, residual_storage="sparse")

    tune_parser = subparsers.add_parser("tune", help="select an AM-SPD method and finite budget from a declared grid")
    tune_parser.add_argument("input", type=Path)
    tune_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_tuning"))
    tune_parser.add_argument("--methods", choices=("core", "spd", "tree", "portfolio"), nargs="+", default=["core", "spd", "tree", "portfolio"])
    tune_parser.add_argument("--packet-budgets", type=int, nargs="+", default=[8, 12, 16])
    tune_parser.add_argument("--singular-budgets", type=int, nargs="+")
    tune_parser.add_argument("--tree-depths", type=int, nargs="+")
    tune_parser.add_argument("--max-ranks", type=int, nargs="+")
    tune_parser.add_argument("--objective", choices=("rate-distortion", "ssim-rate", "rmse", "target-rmse"), default="rate-distortion")
    tune_parser.add_argument("--rate-weight", type=float, default=0.01)
    tune_parser.add_argument("--target-rmse", type=float)
    tune_parser.add_argument("--max-parameters", type=int)
    tune_parser.add_argument("--preset", choices=("quick", "paper-scale", "paper"), default="quick")
    tune_parser.add_argument("--preview", type=Path)
    tune_parser.add_argument("--model", type=Path)
    tune_parser.add_argument("--save-model", action="store_true")
    tune_parser.add_argument("--seed", type=int)
    tune_parser.add_argument("--max-candidates", type=int)
    tune_parser.add_argument("--complexity-weight", type=float)
    tune_parser.add_argument("--residual-refresh", type=int)
    tune_parser.add_argument("--quadtree-refine-every", type=int)
    tune_parser.add_argument("--tolerance", type=float)
    tune_parser.add_argument("--max-actions", type=int)
    tune_parser.add_argument("--max-regions", type=int)
    tune_parser.add_argument("--reopen-fractions", type=float, nargs="+")
    _add_model_options(tune_parser)
    tune_parser.set_defaults(handler=command_tune)

    batch_parser = subparsers.add_parser("batch", help="process an image file or directory tree with resumable manifests")
    batch_parser.add_argument("source", type=Path)
    batch_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_batch"))
    batch_parser.add_argument("--no-recursive", action="store_true")
    batch_parser.add_argument("--workers", type=int, default=1)
    batch_parser.add_argument("--save-models", action="store_true")
    batch_parser.add_argument("--include-input", action="store_true")
    batch_parser.add_argument("--residual-storage", choices=("dense", "sparse", "none"), default="sparse")
    batch_parser.add_argument("--skip-existing", action="store_true")
    batch_parser.add_argument("--fail-fast", action="store_true")
    batch_parser.add_argument("--force-tiled", action="store_true")
    batch_parser.add_argument("--tiled-above", type=int)
    batch_parser.add_argument("--tile-size", type=int, default=128)
    batch_parser.add_argument("--overlap", type=int, default=16)
    batch_parser.add_argument("--blend", choices=("cosine", "linear", "uniform"), default="cosine")
    batch_parser.add_argument("--tile-workers", type=int, default=1)
    batch_parser.add_argument("--embed-tile-models", action="store_true")
    _add_reconstruction_options(batch_parser)
    batch_parser.set_defaults(handler=command_batch)

    baselines_parser = subparsers.add_parser("baselines", help="run Fourier, DCT, SVD, quadtree, and TV baselines")
    baselines_parser.add_argument("input", type=Path)
    baselines_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_baselines"))
    baselines_parser.add_argument("--coefficient-budget", type=int, default=64)
    baselines_parser.add_argument("--svd-rank", type=int, default=4)
    baselines_parser.add_argument("--quadtree-leaves", type=int, default=32)
    baselines_parser.add_argument("--tv-weight", type=float, default=0.07)
    baselines_parser.set_defaults(handler=command_baselines)

    benchmark_parser = subparsers.add_parser("benchmark", help="run the built-in finite image benchmark")
    benchmark_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_benchmark"))
    benchmark_parser.add_argument("--cases", choices=BUILTIN_CASES, nargs="+")
    benchmark_parser.add_argument("--methods", choices=METHODS, nargs="+")
    benchmark_parser.add_argument("--preset", choices=("quick", "paper-scale", "paper"), default="quick")
    benchmark_parser.add_argument("--size", type=int, default=24)
    benchmark_parser.add_argument("--save-models", action="store_true")
    benchmark_parser.add_argument("--include-input", action="store_true")
    benchmark_parser.set_defaults(handler=command_benchmark)

    reproduce_parser = subparsers.add_parser(
        "reproduce-paper",
        help="replay the published four-case benchmark from bundled packet histories",
    )
    reproduce_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_paper_reproduction"))
    reproduce_parser.add_argument("--cases", choices=PAPER_CASES, nargs="+")
    reproduce_parser.add_argument("--strict-reference", action="store_true")
    reproduce_parser.add_argument("--include-input", action="store_true")
    reproduce_parser.add_argument("--list-cases", action="store_true")
    reproduce_parser.set_defaults(handler=command_reproduce_paper)

    demo_parser = subparsers.add_parser("demo", help="run a synthetic geometry example")
    demo_parser.add_argument("--output-dir", type=Path, default=Path("am_spd_demo"))
    demo_parser.add_argument("--size", type=int, default=32)
    demo_parser.add_argument("--save-model", action="store_true")
    _add_reconstruction_options(demo_parser)
    _add_model_options(demo_parser)
    demo_parser.set_defaults(handler=command_demo)

    verify_parser = subparsers.add_parser("verify", help="run package verification")
    verify_parser.add_argument("--full", action="store_true", help="exercise every public package feature")
    verify_parser.add_argument("--paper-case", choices=PAPER_CASES, help="also run one exact paper replay")
    verify_parser.set_defaults(handler=command_verify)

    info_parser = subparsers.add_parser("info", help="show package and runtime information")
    info_parser.set_defaults(handler=command_info)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (FileNotFoundError, ValueError, RuntimeError, OSError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
