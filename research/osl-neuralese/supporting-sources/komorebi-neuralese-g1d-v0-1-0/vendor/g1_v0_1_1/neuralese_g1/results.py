from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .config import config_digest, load_config, validate_config
from .gates import adjudicate
from .integrity import verify_package_manifest
from .tasks import ANSWER_CUE, QUERY_TYPES, find_query_derangement, make_split, split_digest


REQUIRED_FILES = (
    "resolved_config.json",
    "preflight.json",
    "training.jsonl",
    "checkpoint.pt",
    "evaluation.json",
    "predictions.jsonl",
    "gates.json",
    "run_summary.json",
)
MODES = ("recurrent", "zero", "shuffle", "no_feedback")
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path.name}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"invalid JSONL object in {path.name}:{line_number}")
        records.append(value)
    return records


def _close(left: float, right: float) -> bool:
    return math.isfinite(left) and math.isfinite(right) and abs(left - right) <= 1e-12


def _state_dict_hash(state: dict[str, Any], torch: Any) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        if not torch.is_tensor(tensor):
            raise RuntimeError(f"checkpoint workspace value is not a tensor: {name}")
        if not bool(torch.isfinite(tensor.detach()).all().item()):
            raise RuntimeError(f"checkpoint workspace tensor is nonfinite: {name}")
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(str(tensor.dtype).encode("ascii"))
        value = tensor.detach().cpu().contiguous()
        if value.dtype == torch.bfloat16:
            value = value.view(torch.uint16)
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def _regenerate_splits(config: dict[str, Any]) -> dict[str, list[Any]]:
    task = config["task"]
    common = {"seed": int(config["seed"]), "states": int(task["states"])}
    result = {
        "train": make_split(
            **common,
            split="train",
            base_problems=int(task["train_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "validation": make_split(
            **common,
            split="validation",
            base_problems=int(task["validation_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "test_iid": make_split(
            **common,
            split="test_iid",
            base_problems=int(task["test_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "test_ood_depth": make_split(
            **common,
            split="test_ood_depth",
            base_problems=int(task["ood_base_problems"]),
            chain_min=int(task["ood_chain_min"]),
            chain_max=int(task["ood_chain_max"]),
        ),
    }
    import random

    random.Random(int(config["seed"]) + 91).shuffle(result["train"])
    return result


def verify_run_directory(
    path: str | Path, *, require_checkpoint_validation: bool = True
) -> dict[str, Any]:
    package_verification = verify_package_manifest(PACKAGE_ROOT)
    root = Path(path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"run directory not found: {root}")
    missing = [name for name in REQUIRED_FILES if not (root / name).is_file()]
    if missing:
        raise RuntimeError(f"run artifacts are missing: {missing}")
    if (root / "checkpoint.pt").stat().st_size <= 0:
        raise RuntimeError("checkpoint.pt is empty")

    config = _read_json(root / "resolved_config.json")
    stored_digest = config.get("config_digest")
    unsigned_config = dict(config)
    unsigned_config.pop("config_digest", None)
    validate_config(unsigned_config)
    if stored_digest != config_digest(unsigned_config):
        raise RuntimeError("resolved config digest mismatch")
    canonical_overrides = (
        {"seed": config["seed"]} if config["profile"] == "pilot" else {}
    )
    canonical_config = load_config(
        PACKAGE_ROOT / "configs" / f"{config['profile']}.json", canonical_overrides
    )
    canonical_claim_eligible = config == canonical_config

    preflight = _read_json(root / "preflight.json")
    if preflight.get("schema") != "komorebi.neuralese.g1.preflight.v1":
        raise RuntimeError("preflight schema mismatch")
    if preflight.get("status") != "PASS":
        raise RuntimeError("preflight did not pass")
    if preflight.get("config_digest") != stored_digest:
        raise RuntimeError("preflight config digest mismatch")
    if preflight.get("seed") != config.get("seed"):
        raise RuntimeError("preflight seed mismatch")
    if preflight.get("canonical_claim_eligible") is not canonical_claim_eligible:
        raise RuntimeError("preflight canonical-status mismatch")
    if preflight.get("package_manifest_sha256") != package_verification[
        "manifest_sha256"
    ]:
        raise RuntimeError("preflight package manifest hash mismatch")
    expected_identity = {
        "model_type": str(config["model"]["expected_model_type"]),
        "architecture": str(config["model"]["expected_architecture"]),
        "hidden_size": int(config["model"]["expected_hidden_size"]),
        "layers": int(config["model"]["expected_layers"]),
    }
    if preflight.get("expected_model_identity") != expected_identity:
        raise RuntimeError("preflight expected model identity does not match config")
    if preflight.get("model_identity") != expected_identity:
        raise RuntimeError("preflight model identity did not match the registered model")
    model_fingerprint = preflight.get("model")
    if not isinstance(model_fingerprint, dict) or set(model_fingerprint) != {
        "path",
        "files",
        "metadata_sha256",
    }:
        raise RuntimeError("preflight model fingerprint is malformed")
    model_files = model_fingerprint["files"]
    if not isinstance(model_fingerprint["path"], str) or not model_fingerprint["path"]:
        raise RuntimeError("preflight model path is malformed")
    if not isinstance(model_files, list) or not model_files:
        raise RuntimeError("preflight model file inventory is empty")
    observed_model_names: set[str] = set()
    for entry in model_files:
        if not isinstance(entry, dict) or set(entry) != {"name", "size", "sha256"}:
            raise RuntimeError("preflight model file entry is malformed")
        name = entry["name"]
        size = entry["size"]
        digest = entry["sha256"]
        if (
            not isinstance(name, str)
            or not name
            or "/" in name
            or "\\" in name
            or name in observed_model_names
        ):
            raise RuntimeError("preflight model filename is invalid or duplicated")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise RuntimeError(f"preflight model file size is invalid: {name}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.lower()
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise RuntimeError(f"preflight model file hash is invalid: {name}")
        observed_model_names.add(name)
    if "config.json" not in observed_model_names or not any(
        name.endswith((".safetensors", ".bin")) for name in observed_model_names
    ):
        raise RuntimeError("preflight model inventory lacks config or weights")
    reproduced_model_digest = hashlib.sha256(
        json.dumps(model_files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if model_fingerprint["metadata_sha256"] != reproduced_model_digest:
        raise RuntimeError("preflight model inventory digest mismatch")
    expected_scaler_enabled = (
        config["model"]["device"] == "cuda"
        and config["model"]["dtype"] == "float16"
    )
    if preflight.get("gradient_scaler_enabled") is not expected_scaler_enabled:
        raise RuntimeError("preflight gradient-scaler mode does not match config")
    if not _close(
        float(
            preflight.get(
                "gradient_scaler_registered_initial_scale", float("nan")
            )
        ),
        float(config["training"]["loss_scale_initial"]),
    ):
        raise RuntimeError("preflight registered loss scale does not match config")
    start_scale = float(preflight.get("gradient_scaler_start_scale", float("nan")))
    if not math.isfinite(start_scale) or start_scale <= 0.0:
        raise RuntimeError("preflight gradient-scaler start scale is invalid")
    if preflight.get("resumed") is False:
        expected_start_scale = (
            float(config["training"]["loss_scale_initial"])
            if expected_scaler_enabled
            else 1.0
        )
        if not _close(start_scale, expected_start_scale):
            raise RuntimeError("fresh-run gradient-scaler start scale mismatch")
    overlap_counts = preflight.get("compute_prompt_overlap_counts", {})
    if not overlap_counts or any(int(value) != 0 for value in overlap_counts.values()):
        raise RuntimeError("preflight split-overlap audit failed")
    regenerated = _regenerate_splits(config)
    prompt_sets = {
        key: {example.compute_prompt for example in rows}
        for key, rows in regenerated.items()
    }
    expected_overlap_counts: dict[str, int] = {}
    split_names = tuple(prompt_sets)
    for left_index, left in enumerate(split_names):
        for right in split_names[left_index + 1 :]:
            expected_overlap_counts[f"{left}__{right}"] = len(
                prompt_sets[left] & prompt_sets[right]
            )
    if overlap_counts != expected_overlap_counts:
        raise RuntimeError("preflight split-overlap counts do not reproduce")
    regenerated_counts = {key: len(value) for key, value in regenerated.items()}
    regenerated_digests = {key: split_digest(value) for key, value in regenerated.items()}
    if preflight.get("split_counts") != regenerated_counts:
        raise RuntimeError("preflight split counts do not reproduce")
    if preflight.get("split_digests") != regenerated_digests:
        raise RuntimeError("preflight split digests do not reproduce")
    target_token_map = preflight.get("single_token_targets")
    expected_target_texts = {
        example.target_text for rows in regenerated.values() for example in rows
    }
    if (
        not isinstance(target_token_map, dict)
        or set(target_token_map) != expected_target_texts
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in target_token_map.values()
        )
        or len(set(int(value) for value in target_token_map.values()))
        != len(target_token_map)
    ):
        raise RuntimeError("preflight target-token map is incomplete or non-unique")
    expected_pair_count = len(
        {
            (example.query_prompt, example.target_text)
            for rows in regenerated.values()
            for example in rows
        }
    )
    expected_token_contract = {
        "schema": "komorebi.neuralese.g1.answer_token_contract.v1",
        "status": "PASS",
        "answer_cue": ANSWER_CUE,
        "target_count": len(target_token_map),
        "prompt_target_pair_count": expected_pair_count,
    }
    if preflight.get("answer_token_contract") != expected_token_contract:
        raise RuntimeError("preflight answer-token boundary contract mismatch")

    training = _read_jsonl(root / "training.jsonl")
    if not training:
        raise RuntimeError("training telemetry is empty")
    steps = [record.get("step") for record in training]
    if any(isinstance(step, bool) or not isinstance(step, int) for step in steps):
        raise RuntimeError("training telemetry contains an invalid step")
    if any(left >= right for left, right in zip(steps, steps[1:])):
        raise RuntimeError("training telemetry steps are not strictly increasing")
    if steps[0] != 1 or steps[-1] != config["training"]["steps"]:
        raise RuntimeError("training telemetry does not span the configured run")
    previous_overflow_retries = -1
    previous_attempts = -1
    for record in training:
        if not math.isfinite(float(record.get("loss", float("nan")))):
            raise RuntimeError("training telemetry contains a nonfinite loss")
        if not math.isfinite(float(record.get("gradient_norm", float("nan")))):
            raise RuntimeError("training telemetry contains a nonfinite gradient")
        loss_scale = float(record.get("loss_scale", float("nan")))
        retries_before = record.get("overflow_retries_before_step")
        retries_total = record.get("overflow_retries_total")
        attempts_total = record.get("optimizer_attempts_total")
        if not math.isfinite(loss_scale) or loss_scale <= 0.0:
            raise RuntimeError("training telemetry contains an invalid loss scale")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in (retries_before, retries_total, attempts_total)
        ):
            raise RuntimeError("training telemetry contains invalid overflow counters")
        if retries_before > config["training"]["max_overflow_retries"]:
            raise RuntimeError("training telemetry exceeds the overflow retry bound")
        if retries_total < retries_before or retries_total < previous_overflow_retries:
            raise RuntimeError("training overflow counters are inconsistent")
        if attempts_total != record["step"] + retries_total:
            raise RuntimeError("training optimizer-attempt counter is inconsistent")
        if attempts_total <= previous_attempts:
            raise RuntimeError("training optimizer-attempt counter is not increasing")
        if not expected_scaler_enabled and (
            retries_before != 0 or retries_total != 0 or not _close(loss_scale, 1.0)
        ):
            raise RuntimeError("disabled gradient scaler reported overflow activity")
        previous_overflow_retries = retries_total
        previous_attempts = attempts_total

    evaluation = _read_json(root / "evaluation.json")
    if evaluation.get("schema") != "komorebi.neuralese.g1.evaluation.v1":
        raise RuntimeError("evaluation schema mismatch")
    predictions = _read_jsonl(root / "predictions.jsonl")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in predictions:
        split = str(record.get("split"))
        mode = str(record.get("mode"))
        if split not in ("test_iid", "test_ood_depth") or mode not in MODES:
            raise RuntimeError("prediction contains an unregistered split or mode")
        if bool(record.get("correct")) != (
            int(record["predicted_token_id"]) == int(record["target_token_id"])
        ):
            raise RuntimeError("prediction correctness flag is inconsistent")
        grouped[(split, mode)].append(record)

    expected_counts = {
        "test_iid": int(config["task"]["test_base_problems"]) * len(QUERY_TYPES),
        "test_ood_depth": int(config["task"]["ood_base_problems"]) * len(QUERY_TYPES),
    }
    expected_examples = {
        split: {example.example_id: example for example in regenerated[split]}
        for split in ("test_iid", "test_ood_depth")
    }
    for split, evaluation_key in (
        ("test_iid", "iid"),
        ("test_ood_depth", "ood"),
    ):
        expected_ids: set[str] | None = None
        expected_target_ids: dict[str, int] | None = None
        registered_rows = regenerated[split]
        registered_donors = find_query_derangement(registered_rows)
        if registered_donors is None:
            raise RuntimeError(f"registered derangement cannot be reproduced for {split}")
        donor_by_id = {
            row.example_id: registered_rows[registered_donors[index]]
            for index, row in enumerate(registered_rows)
        }
        for mode in MODES:
            records = grouped[(split, mode)]
            if len(records) != expected_counts[split]:
                raise RuntimeError(f"prediction count mismatch for {split}/{mode}")
            identifiers = {str(record["example_id"]) for record in records}
            if len(identifiers) != len(records):
                raise RuntimeError(f"duplicate prediction IDs for {split}/{mode}")
            if identifiers != set(expected_examples[split]):
                raise RuntimeError(f"prediction IDs do not match regenerated {split}")
            for record in records:
                expected = expected_examples[split][str(record["example_id"])]
                if (
                    record.get("query_type") != expected.query_type
                    or int(record.get("applications")) != expected.applications
                    or int(record.get("final_state")) != expected.final_state
                    or int(record.get("target_token_id"))
                    != int(target_token_map[expected.target_text])
                ):
                    raise RuntimeError(
                        f"prediction metadata mismatch for {record['example_id']}"
                    )
            if expected_ids is None:
                expected_ids = identifiers
            elif identifiers != expected_ids:
                raise RuntimeError(f"prediction ID mismatch across modes for {split}")
            local_target_ids = {
                str(record["example_id"]): int(record["target_token_id"])
                for record in records
            }
            if expected_target_ids is None:
                expected_target_ids = local_target_ids
            elif local_target_ids != expected_target_ids:
                raise RuntimeError(f"target token IDs differ across modes for {split}")
            if mode == "shuffle":
                observed_donors = {
                    str(record["donor_example_id"]) for record in records
                }
                if observed_donors != identifiers:
                    raise RuntimeError(f"shuffle donors are not bijective for {split}")
                for record in records:
                    expected_donor = donor_by_id[str(record["example_id"])]
                    if (
                        record.get("donor_example_id") != expected_donor.example_id
                        or int(record.get("donor_final_state"))
                        != expected_donor.final_state
                    ):
                        raise RuntimeError(
                            f"shuffle donor mismatch for {record['example_id']}"
                        )
            summary = evaluation[evaluation_key][mode]
            observed_accuracy = sum(bool(record["correct"]) for record in records) / len(
                records
            )
            if summary.get("count") != len(records) or not _close(
                float(summary.get("accuracy", float("nan"))), observed_accuracy
            ):
                raise RuntimeError(f"accuracy summary mismatch for {split}/{mode}")
            for query_type in QUERY_TYPES:
                family = [
                    record for record in records if record.get("query_type") == query_type
                ]
                if not family:
                    raise RuntimeError(f"missing query family {query_type} for {split}/{mode}")
                family_accuracy = sum(bool(record["correct"]) for record in family) / len(
                    family
                )
                if not _close(
                    float(summary["accuracy_by_query"][query_type]), family_accuracy
                ):
                    raise RuntimeError(
                        f"query accuracy mismatch for {split}/{mode}/{query_type}"
                    )
                target_counts: dict[int, int] = defaultdict(int)
                for record in family:
                    target_counts[int(record["target_token_id"])] += 1
                majority = max(target_counts.values()) / sum(target_counts.values())
                if not _close(
                    float(summary["majority_baseline_by_query"][query_type]), majority
                ):
                    raise RuntimeError(
                        f"majority baseline mismatch for {split}/{mode}/{query_type}"
                    )
        derangement = evaluation[evaluation_key].get("state_derangement", {})
        if (
            derangement.get("rows") != expected_counts[split]
            or derangement.get("bijection") is not True
            or derangement.get("same_query_family") is not True
            or derangement.get("fixed_state_matches") != 0
            or derangement.get("answer_compatible_matches") != 0
        ):
            raise RuntimeError(f"invalid shuffle audit for {split}")

    gates = _read_json(root / "gates.json")
    if gates.get("schema") != "komorebi.neuralese.g1.gates.v1":
        raise RuntimeError("gate schema mismatch")
    summary = _read_json(root / "run_summary.json")
    if summary.get("schema") != "komorebi.neuralese.g1.run_summary.v1":
        raise RuntimeError("run summary schema mismatch")
    if summary.get("status") != gates.get("claim"):
        raise RuntimeError("run summary and gate claim disagree")
    if summary.get("profile") != config.get("profile") or summary.get("seed") != config.get(
        "seed"
    ):
        raise RuntimeError("run summary identity mismatch")
    if summary.get("gates") != gates:
        raise RuntimeError("embedded and standalone gates disagree")
    training_summary = summary.get("training", {})
    if (
        training_summary.get("logged_records") != len(training)
        or not _close(float(training_summary.get("first_logged_loss", float("nan"))), float(training[0]["loss"]))
        or not _close(float(training_summary.get("last_logged_loss", float("nan"))), float(training[-1]["loss"]))
        or not _close(
            float(training_summary.get("maximum_gradient_norm", float("nan"))),
            max(float(record["gradient_norm"]) for record in training),
        )
        or training_summary.get("overflow_retries_total")
        != training[-1]["overflow_retries_total"]
    ):
        raise RuntimeError("run summary training telemetry mismatch")
    expected_summary_metrics = {
        "iid_recurrent_accuracy": evaluation["iid"]["recurrent"]["accuracy"],
        "iid_zero_accuracy": evaluation["iid"]["zero"]["accuracy"],
        "iid_shuffle_accuracy": evaluation["iid"]["shuffle"]["accuracy"],
        "iid_no_feedback_accuracy": evaluation["iid"]["no_feedback"]["accuracy"],
        "ood_recurrent_accuracy": evaluation["ood"]["recurrent"]["accuracy"],
    }
    if any(
        not _close(float(summary.get("evaluation", {}).get(key, float("nan"))), float(value))
        for key, value in expected_summary_metrics.items()
    ):
        raise RuntimeError("run summary evaluation mismatch")
    if config["model"]["strict_backbone_hash"]:
        before = summary.get("backbone_hash_before")
        after = summary.get("backbone_hash_after")
        if not isinstance(before, str) or len(before) != 64 or before != after:
            raise RuntimeError("strict backbone hash invariant failed")

    if require_checkpoint_validation:
        try:
            import torch
        except ImportError as error:
            raise RuntimeError("PyTorch is required for checkpoint verification") from error
        checkpoint = torch.load(
            root / "checkpoint.pt", map_location="cpu", weights_only=True
        )
        if checkpoint.get("schema") != "komorebi.neuralese.g1.checkpoint.v3":
            raise RuntimeError("checkpoint schema mismatch")
        if checkpoint.get("config_digest") != stored_digest:
            raise RuntimeError("checkpoint config digest mismatch")
        if checkpoint.get("model_fingerprint") != preflight.get("model"):
            raise RuntimeError("checkpoint model fingerprint mismatch")
        if checkpoint.get("package_manifest_sha256") != preflight.get(
            "package_manifest_sha256"
        ):
            raise RuntimeError("checkpoint package manifest mismatch")
        if checkpoint.get("split_digests") != regenerated_digests:
            raise RuntimeError("checkpoint split digest mismatch")
        if checkpoint.get("completed_steps") != config["training"]["steps"]:
            raise RuntimeError("checkpoint completed-step mismatch")
        if checkpoint.get("latest_record") != training[-1]:
            raise RuntimeError("checkpoint and final training telemetry disagree")
        if not isinstance(checkpoint.get("optimizer_state"), dict):
            raise RuntimeError("checkpoint optimizer state is missing")
        if not isinstance(checkpoint.get("scaler_state"), dict):
            raise RuntimeError("checkpoint gradient-scaler state is missing")
        scaler_enabled = bool(checkpoint["scaler_state"])
        if preflight.get("gradient_scaler_enabled") is not scaler_enabled:
            raise RuntimeError("checkpoint gradient-scaler mode mismatch")
        if scaler_enabled:
            checkpoint_scale = float(
                checkpoint["scaler_state"].get("scale", float("nan"))
            )
            if not _close(checkpoint_scale, float(training[-1]["loss_scale"])):
                raise RuntimeError("checkpoint gradient-scaler scale mismatch")
        rng_state = checkpoint.get("rng_state")
        if not isinstance(rng_state, dict) or set(rng_state) != {
            "python",
            "numpy",
            "torch_cpu",
            "torch_cuda",
        }:
            raise RuntimeError("checkpoint RNG state is incomplete")
        final_workspace_hash = _state_dict_hash(checkpoint["workspace_state"], torch)
        initial_workspace_hash = checkpoint.get("initial_workspace_hash")
        if (
            initial_workspace_hash != summary["training"]["workspace_hash_before"]
            or final_workspace_hash != summary["training"]["workspace_hash_after"]
        ):
            raise RuntimeError("checkpoint workspace hash mismatch")
        if checkpoint.get("backbone_hash_before") != preflight.get(
            "backbone_hash_before"
        ):
            raise RuntimeError("checkpoint pretraining backbone hash mismatch")
        state_norms = [
            float(value)
            for record in training
            for value in record.get("trace", {}).get("state_mean_norm_by_step", [])
        ]
        injection_norms = [
            float(value)
            for record in training
            for value in record.get("trace", {}).get("injection_mean_norm_by_step", [])
        ]
        gradient_norms = [float(record["gradient_norm"]) for record in training]
        engineering_values = {
            "local_model_loaded": bool(preflight.get("model"))
            and preflight.get("model_identity") == preflight.get("expected_model_identity"),
            "single_token_targets": bool(preflight.get("single_token_targets")),
            "answer_token_boundary": preflight.get("answer_token_contract")
            == expected_token_contract,
            "backbone_frozen": preflight.get("backbone_frozen") is True
            and (
                not config["model"]["strict_backbone_hash"]
                or summary.get("backbone_hash_before")
                == summary.get("backbone_hash_after")
            ),
            "optimizer_excludes_backbone": preflight.get("optimizer_excludes_backbone")
            is True
            and preflight.get("optimizer_matches_workspace") is True,
            "finite_loss": all(math.isfinite(float(record["loss"])) for record in training),
            "nonzero_finite_gradient": bool(gradient_norms)
            and all(math.isfinite(value) for value in gradient_norms)
            and max(gradient_norms) > 0.0,
            "nonzero_finite_parameter_delta": isinstance(initial_workspace_hash, str)
            and len(initial_workspace_hash) == 64
            and initial_workspace_hash != final_workspace_hash,
            "nonzero_finite_state": bool(state_norms)
            and bool(injection_norms)
            and all(math.isfinite(value) for value in state_norms + injection_norms)
            and max(state_norms) > 0.0
            and max(injection_norms) > 0.0,
            "artifacts_complete": True,
            "canonical_scientific_profile": preflight.get("canonical_claim_eligible")
            is True
            and canonical_claim_eligible,
        }
    else:
        engineering_values = {
            str(item["name"]): item.get("value")
            for item in gates.get("engineering", {}).get("gates", [])
        }
        engineering_values["canonical_scientific_profile"] = preflight.get(
            "canonical_claim_eligible"
        ) is True and canonical_claim_eligible
    recomputed_gates = adjudicate(config, engineering_values, evaluation)
    if recomputed_gates != gates:
        raise RuntimeError("gate adjudication is not reproducible from primary artifacts")

    return {
        "schema": "komorebi.neuralese.g1.run_verification.v1",
        "status": "PASS",
        "profile": config["profile"],
        "seed": config["seed"],
        "claim": gates["claim"],
        "training_records": len(training),
        "prediction_records": len(predictions),
        "config_digest": stored_digest,
        "model_metadata_sha256": preflight["model"]["metadata_sha256"],
        "package_manifest_sha256": preflight["package_manifest_sha256"],
        "checkpoint_validated": require_checkpoint_validation,
    }
