#!/usr/bin/env python3
"""Run target-token residual/Jacobian probes on an existing local causal LM."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Sequence

from rrct_lab.adapters.hf_local import (
    load_local_causal_lm,
    probe_target_token_vjps,
    validate_local_model_path,
)
from rrct_lab.exceptions import DependencyError


def _load_prompt_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        raise ValueError("prompts must be an existing JSON or JSONL file")
    records: Any
    if path.suffix.lower() == ".jsonl":
        records = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL at line {line_number}") from error
    else:
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("prompts file is not valid JSON") from error
        if isinstance(records, dict) and "prompts" in records:
            records = records["prompts"]
        elif isinstance(records, (str, dict)):
            records = [records]
    if not isinstance(records, list) or not records:
        raise ValueError("prompts file must contain a nonempty list")
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if isinstance(record, str):
            item = {"id": str(index), "prompt": record}
        elif isinstance(record, dict):
            item = dict(record)
            item.setdefault("id", str(index))
        else:
            raise ValueError(f"prompt record {index} must be a string or object")
        if not isinstance(item.get("prompt"), str) or not item["prompt"]:
            raise ValueError(f"prompt record {index} has no nonempty prompt")
        normalized.append(item)
    return normalized


def _safe_output_path(output: Path, *, model_path: Path, prompts_path: Path) -> Path:
    target = output.expanduser().resolve(strict=False)
    if target.exists() and target.is_dir():
        raise ValueError("output must be a JSON file, not a directory")
    if target == prompts_path.resolve(strict=True):
        raise ValueError("output must not overwrite the prompts file")
    if model_path.is_file() and target == model_path:
        raise ValueError("output must not overwrite the local model file")
    if model_path.is_dir() and (target == model_path or model_path in target.parents):
        raise ValueError("output must be outside the local model directory")
    return target


def _record_targets(record: dict[str, Any], defaults: Sequence[int]) -> list[int]:
    values = record.get("target_token_ids", defaults)
    if isinstance(values, int) and not isinstance(values, bool):
        values = [values]
    if not isinstance(values, list) or not values:
        raise ValueError(
            f"prompt record {record['id']} needs target_token_ids or "
            "--target-token-id"
        )
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError(f"prompt record {record['id']} has invalid target_token_ids")
    return values


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Probe an existing local causal LM without training, downloads, "
            "remote code, or network access."
        )
    )
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--prompts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--layer", type=int, default=-1)
    parser.add_argument("--residual-token", type=int, default=-1)
    parser.add_argument("--prediction-token", type=int, default=-1)
    parser.add_argument("--target-token-id", type=int, action="append", default=[])
    parser.add_argument("--max-length", type=int)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--dtype", choices=("float32", "float16", "bfloat16"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        model_path = validate_local_model_path(args.model)
        prompts_path = args.prompts.expanduser().resolve(strict=True)
        records = _load_prompt_records(prompts_path)
        output_path = _safe_output_path(
            args.output, model_path=model_path, prompts_path=prompts_path
        )
        bundle = load_local_causal_lm(
            model_path, device=args.device, dtype=args.dtype
        )
        probes: list[dict[str, Any]] = []
        for record in records:
            result = probe_target_token_vjps(
                bundle,
                record["prompt"],
                _record_targets(record, args.target_token_id),
                layer_index=int(record.get("layer_index", args.layer)),
                residual_token_index=int(
                    record.get("residual_token_index", args.residual_token)
                ),
                prediction_token_index=int(
                    record.get("prediction_token_index", args.prediction_token)
                ),
                max_length=args.max_length,
            )
            result["prompt_id"] = str(record["id"])
            probes.append(result)
        payload = {
            "schema": "rrct_lab.local_jspace_probe_collection.v1",
            "status": "completed",
            "adapter": bundle.metadata(),
            "probe_count": len(probes),
            "probes": probes,
            "local_files_only": True,
            "trust_remote_code": False,
            "training": False,
            "network_access": False,
        }
        _atomic_write_json(output_path, payload)
    except (DependencyError, OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

