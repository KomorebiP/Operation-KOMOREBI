from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .byte_tokenizer import ByteTokenizer


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
RUN_SENTINEL = ".arithmetic_workspace_run"
RUN_SENTINEL_CONTENT = "arithmetic-workspace-owned-run-v1\n"
SCHEMA_VERSION = "4.0"
LEGACY_EVENT_SAMPLER_MANIFEST_SHA256 = (
    "7855d6d6495f9a28062479174ac80a5a7591d300f639b26ba5b31745b9ff5344"
)
HOTFIX_MIGRATION_SCHEMA = "arithmetic-workspace-package-hotfix-migration-v1"
HOTFIX_MIGRATION_FILE = "package_hotfix_migration.json"
REQUIRED_TOP_LEVEL = {
    "experiment",
    "model",
    "data",
    "arms",
    "training",
    "evaluation",
    "competence_gates",
    "space",
    "causal",
    "seeds",
}
REQUIRED_ARMS = {"correct", "no_carry", "pseudo_fst", "deranged"}
CLAIM_STAGES = (
    "competence",
    "representation",
    "necessity",
    "patch_and_rescue",
    "mediation",
    "shared_access",
    "math_specificity",
)
IMPLEMENTED_SPACE_CONSUMERS = (
    "digit_log_mass",
    "eos_log_probability",
    "minus_log_probability",
    "output_entropy",
    "top_log_probability",
    "sealed_vocab_projection_0",
    "sealed_vocab_projection_1",
    "sealed_vocab_projection_2",
    "sealed_vocab_projection_3",
)
IMPLEMENTED_SPACE_CONTROLS = ("pca", "random", "complement")
IMPLEMENTED_CAUSAL_TESTS = (
    "candidate_coordinate_ablation",
    "clean_to_corrupt_coordinate_patch",
    "independent_upstream_residual_transplant",
    "coordinate_rescue_after_upstream_transplant",
)


def _atomic_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def _append_jsonl(value: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(dict(value), ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def _positive_integer(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1):
        qualifier = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{label} must be a {qualifier} integer")
    return value


def validate_profile(value: Mapping[str, Any], profile_name: str = "custom") -> dict[str, Any]:
    """Validate the cross-module contract without rejecting documented extensions."""

    if not isinstance(value, Mapping):
        raise ValueError("profile root must be an object")
    missing = REQUIRED_TOP_LEVEL - set(value)
    if missing:
        raise ValueError(f"profile is missing required sections: {sorted(missing)}")
    resolved = copy.deepcopy(dict(value))
    if not isinstance(profile_name, str) or not profile_name.strip():
        raise ValueError("profile name must be a nonempty string")

    experiment = resolved["experiment"]
    if isinstance(experiment, str):
        if not experiment.strip():
            raise ValueError("experiment must be nonempty")
        resolved["experiment"] = {"name": experiment}
    elif not isinstance(experiment, dict) or not isinstance(experiment.get("name"), str):
        raise ValueError("experiment must be a string or an object with a name")
    experiment = resolved["experiment"]
    required_experiment_flags = {
        "paired_initialization": True,
        "paired_prompt_order": True,
        "sealed_evaluation": True,
        "fail_closed": True,
    }
    for key, expected in required_experiment_flags.items():
        if experiment.get(key, expected) is not expected:
            raise ValueError(f"experiment.{key} must be {expected!r}")
    if list(
        experiment.get(
            "paired_prompt_order_scope", ["correct", "pseudo_fst", "deranged"]
        )
    ) != ["correct", "pseudo_fst", "deranged"]:
        raise ValueError(
            "experiment.paired_prompt_order_scope must be correct,pseudo_fst,deranged"
        )

    for section in (
        "model",
        "data",
        "training",
        "evaluation",
        "competence_gates",
        "space",
        "causal",
    ):
        if not isinstance(resolved[section], dict):
            raise ValueError(f"{section} must be an object")

    model = resolved["model"]
    for key in ("vocab_size", "d_model", "n_layers", "n_heads", "max_seq_len"):
        if key in model:
            _positive_integer(model[key], f"model.{key}")
    if model.get("vocab_size", 260) != 260:
        raise ValueError("model.vocab_size must equal the byte tokenizer vocabulary size 260")
    if "d_model" in model and "n_heads" in model and model["d_model"] % model["n_heads"]:
        raise ValueError("model.d_model must be divisible by model.n_heads")

    data = resolved["data"]
    if data.get("mode", "deterministic_online") != "deterministic_online":
        raise ValueError("data.mode must be deterministic_online")
    operations = data.get("operations", ["add", "sub"])
    if list(operations) != ["add", "sub"]:
        raise ValueError("v0.4 requires the fixed balanced add/sub operation cycle")
    required_data_flags = {
        "answer_only": True,
        "family_disjoint": True,
        "fresh_counter_addressed_stream": True,
        "same_prompts_across_label_arms": True,
        "same_order_across_label_arms": True,
    }
    for key, expected in required_data_flags.items():
        if data.get(key, expected) is not expected:
            raise ValueError(f"data.{key} must be {expected!r}")
    if data.get("collision_audited", False) is not False:
        raise ValueError("v0.4 does not implement a global collision audit")
    paired_arms = data.get(
        "label_paired_arms", ["correct", "pseudo_fst", "deranged"]
    )
    if list(paired_arms) != ["correct", "pseudo_fst", "deranged"]:
        raise ValueError(
            "data.label_paired_arms must be correct,pseudo_fst,deranged"
        )

    arms = resolved["arms"]
    if not isinstance(arms, list) or not arms:
        raise ValueError("arms must be a nonempty array")
    names: list[str] = []
    normalized_arms: list[dict[str, Any]] = []
    for index, arm in enumerate(arms):
        if not isinstance(arm, dict):
            raise ValueError(f"arms[{index}] must be an object")
        name = arm.get("name")
        rule = arm.get("target_rule")
        if not isinstance(name, str) or not name:
            raise ValueError(f"arms[{index}].name must be nonempty")
        if not isinstance(rule, str) or not rule:
            raise ValueError(f"arms[{index}].target_rule must be nonempty")
        if type(arm.get("enabled", True)) is not bool:
            raise ValueError(f"arms[{index}].enabled must be boolean")
        names.append(name)
        normalized_arms.append(copy.deepcopy(arm))
    if len(names) != len(set(names)):
        raise ValueError("arm names must be unique")
    enabled_names = {
        arm["name"] for arm in normalized_arms if bool(arm.get("enabled", True))
    }
    absent = REQUIRED_ARMS - enabled_names
    if absent:
        raise ValueError(f"the four mandatory enabled arms are required: missing {sorted(absent)}")
    resolved["arms"] = normalized_arms
    expected_target_rules = {
        "correct": "exact_arithmetic",
        "no_carry": "no_transfer_subset_exact",
        "pseudo_fst": "seeded_finite_state_transducer",
        "deranged": "seeded_random_value_derangement",
    }
    for arm in normalized_arms:
        expected = expected_target_rules.get(arm["name"])
        if expected is not None and arm["target_rule"] != expected:
            raise ValueError(
                f"arms.{arm['name']}.target_rule must equal {expected}"
            )

    training = resolved["training"]
    if str(training.get("optimizer", "adamw")).lower() != "adamw":
        raise ValueError("training.optimizer must be adamw")
    max_steps = training.get("max_steps", training.get("steps"))
    if max_steps is None:
        raise ValueError("training.max_steps is required")
    _positive_integer(max_steps, "training.max_steps")
    progress_every = training.get("progress_every_steps", 100)
    _positive_integer(progress_every, "training.progress_every_steps")
    if progress_every != 100:
        raise ValueError("training.progress_every_steps must be 100 for auditable telemetry")
    training["max_steps"] = max_steps
    training["progress_every_steps"] = 100
    if "checkpoint_steps" in training:
        checkpoints = training["checkpoint_steps"]
        if not isinstance(checkpoints, list) or any(type(step) is not int for step in checkpoints):
            raise ValueError("training.checkpoint_steps must be an integer array")
        if checkpoints != sorted(set(checkpoints)):
            raise ValueError("training.checkpoint_steps must be unique and increasing")
        if any(step < 0 or step > max_steps for step in checkpoints):
            raise ValueError("training checkpoint lies outside [0,max_steps]")

    seeds = resolved["seeds"]
    if not isinstance(seeds, (list, dict)):
        raise ValueError("seeds must be an array or object")
    _resolve_seeds(seeds, None)

    gates = resolved["competence_gates"]
    if gates.get("apply_to_arm", "correct") != "correct":
        raise ValueError("competence_gates.apply_to_arm must be correct")
    for key, threshold in _flatten_numeric_thresholds(gates):
        number = _finite_number(threshold, f"competence_gates.{key}")
        if (key.endswith("_min") or "minimum" in key) and not 0.0 <= number <= 1.0:
            raise ValueError(f"competence threshold {key} must lie in [0,1]")

    space = resolved["space"]
    if space.get("method", "balanced_controllability_observability") != (
        "balanced_controllability_observability"
    ):
        raise ValueError("space.method must be balanced_controllability_observability")
    if space.get(
        "controllability_source", "empirical_upstream_residual_perturbations"
    ) != "empirical_upstream_residual_perturbations":
        raise ValueError(
            "space.controllability_source must be empirical_upstream_residual_perturbations"
        )
    if "consumers" in space and tuple(space["consumers"]) != IMPLEMENTED_SPACE_CONSUMERS:
        raise ValueError("space.consumers must exactly match the implemented target-free consumers")
    if "controls" in space and tuple(space["controls"]) != IMPLEMENTED_SPACE_CONTROLS:
        raise ValueError("space.controls must exactly match pca,random,complement")
    if int(space.get("random_output_consumers", 4)) != 4:
        raise ValueError("space.random_output_consumers must equal four")
    if "rank" in space:
        _positive_integer(space["rank"], "space.rank")
    if "candidate_ranks" in space:
        ranks = space["candidate_ranks"]
        if not isinstance(ranks, list) or not ranks or any(type(rank) is not int or rank <= 0 for rank in ranks):
            raise ValueError("space.candidate_ranks must be a nonempty positive-integer array")

    causal = resolved["causal"]
    if "controls" in causal:
        controls = causal["controls"]
        if not isinstance(controls, list) or tuple(controls) != (
            "candidate",
            *IMPLEMENTED_SPACE_CONTROLS,
        ):
            raise ValueError(
                "causal.controls must exactly match candidate,pca,random,complement"
            )
    if "tests" in causal and tuple(causal["tests"]) != IMPLEMENTED_CAUSAL_TESTS:
        raise ValueError("causal.tests must exactly match the implemented v0.4 assays")
    if list(causal.get("matched_pairs", ["carry", "borrow"])) != ["carry", "borrow"]:
        raise ValueError("causal.matched_pairs must be carry,borrow")
    if causal.get("intervention_position", "pre_answer") != "pre_answer":
        raise ValueError("causal.intervention_position must be pre_answer")
    for key in ("require_free_generation", "require_directional_donor_effect"):
        if causal.get(key, True) is not True:
            raise ValueError(f"causal.{key} must be true")
    causal["require_free_generation"] = True
    causal["require_directional_donor_effect"] = True
    causal_count = int(
        causal.get(
            "pairs",
            causal.get("examples", resolved["evaluation"].get("causal_items", 128)),
        )
    )
    _positive_integer(causal_count, "causal pair count")
    for key in (
        "minimum_baseline_qualified_pairs",
        "minimum_directional_rescue_pairs",
    ):
        minimum = _positive_integer(causal.get(key, 1), f"causal.{key}")
        if minimum > causal_count:
            raise ValueError(f"causal.{key} cannot exceed the causal pair count")
        causal[key] = minimum

    seeds_section = resolved["seeds"]
    if isinstance(seeds_section, Mapping) and seeds_section.get(
        "cli_seed_overrides", True
    ) is not True:
        raise ValueError("seeds.cli_seed_overrides must be true")
    claim_policy = resolved.get("claim_policy", {})
    if isinstance(claim_policy, Mapping):
        if claim_policy.get("allow_jspace_claim", False) is not False:
            raise ValueError("v0.4 profiles must set allow_jspace_claim=false")
        for key in (
            "require_all_competence_gates",
            "require_all_causal_gates",
        ):
            if claim_policy.get(key, True) is not True:
                raise ValueError(f"claim_policy.{key} must be true")

    resolved["profile"] = profile_name
    resolved["schema_version"] = str(resolved.get("schema_version", SCHEMA_VERSION))
    return resolved


def _flatten_numeric_thresholds(value: Mapping[str, Any], prefix: str = "") -> Iterable[tuple[str, Any]]:
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(child, Mapping):
            yield from _flatten_numeric_thresholds(child, path)
        elif isinstance(child, (int, float)) and not isinstance(child, bool):
            yield path, child


def _integer_seed_list(value: Any, label: str) -> list[int]:
    if value is None:
        return []
    if type(value) is int:
        value = [value]
    if not isinstance(value, (list, tuple)) or any(type(seed) is not int or seed < 0 for seed in value):
        raise ValueError(f"{label} must contain nonnegative integer seeds")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicate seeds")
    return list(value)


def _resolve_seeds(
    value: list[Any] | dict[str, Any], override: int | None
) -> tuple[list[int], set[int], int]:
    if override is not None:
        if type(override) is not int or override < 0:
            raise ValueError("seed override must be a nonnegative integer")
    if isinstance(value, list):
        configured = _integer_seed_list(value, "seeds")
        confirmatory = set(configured)
        required = len(configured)
    else:
        development = _integer_seed_list(
            value.get("development", value.get("exploration", [])), "seeds.development"
        )
        confirmation = _integer_seed_list(
            value.get("confirmatory", value.get("confirmation", value.get("values", []))),
            "seeds.confirmatory",
        )
        configured = development + [seed for seed in confirmation if seed not in development]
        if not configured and "base" in value:
            base = _positive_integer(value["base"], "seeds.base", allow_zero=True)
            count = _positive_integer(value.get("count", 1), "seeds.count")
            configured = [base + index for index in range(count)]
            confirmation = configured.copy()
        required = value.get(
            "minimum_confirmatory",
            value.get("required_confirmatory", value.get("confirmatory_required", 3)),
        )
        required = _positive_integer(required, "seeds.minimum_confirmatory")
        confirmatory = set(confirmation)
    if not configured:
        raise ValueError("at least one seed must be configured")
    if override is not None:
        return [override], ({override} if override in confirmatory else set()), required
    return configured, confirmatory, required


@dataclass(frozen=True)
class Components:
    provider_factory: Callable[..., Any]
    train_arm: Callable[..., dict[str, Any]]
    evaluate_free_generation: Callable[..., dict[str, Any]]
    competence_report: Callable[..., dict[str, Any]]
    load_research_checkpoint: Callable[..., Any]
    balanced_config_type: type
    discover_balanced_space: Callable[..., Any]
    run_causal_assay: Callable[..., dict[str, Any]]
    resolve_device: Callable[[str], Any]
    runtime_information: Callable[[Any], dict[str, Any]]


def _load_components() -> Components:
    # Delayed imports keep profile validation and --dry-run usable on machines that
    # have not installed PyTorch yet, and avoid import-order coupling between modules.
    from .balanced_space import BalancedSpaceConfig, discover_balanced_space
    from .causal_workspace import run_causal_assay
    from .trainer import resolve_device, runtime_information
    from .workspace_data import WorkspaceDataProvider
    from .workspace_trainer import (
        competence_report,
        evaluate_free_generation,
        load_research_checkpoint,
        train_arm,
    )

    return Components(
        provider_factory=WorkspaceDataProvider,
        train_arm=train_arm,
        evaluate_free_generation=evaluate_free_generation,
        competence_report=competence_report,
        load_research_checkpoint=load_research_checkpoint,
        balanced_config_type=BalancedSpaceConfig,
        discover_balanced_space=discover_balanced_space,
        run_causal_assay=run_causal_assay,
        resolve_device=resolve_device,
        runtime_information=runtime_information,
    )


def _supported_call(function: Callable[..., Any], **kwargs: Any) -> Any:
    """Call a component with the named portion of the evolving v0.4 contract."""

    signature = inspect.signature(function)
    accepts_extra = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    selected = kwargs if accepts_extra else {
        name: value for name, value in kwargs.items() if name in signature.parameters
    }
    missing = [
        name
        for name, parameter in signature.parameters.items()
        if parameter.default is inspect.Parameter.empty
        and parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
        and name not in selected
    ]
    if missing:
        raise TypeError(
            f"component {getattr(function, '__name__', function)!r} requires unsupported "
            f"arguments: {missing}"
        )
    return function(**selected)


def _construct_config(config_type: type, value: Mapping[str, Any]) -> Any:
    if hasattr(config_type, "from_mapping"):
        return config_type.from_mapping(value)
    signature = inspect.signature(config_type)
    accepts_extra = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    selected = dict(value) if accepts_extra else {
        name: child for name, child in value.items() if name in signature.parameters
    }
    return config_type(**selected)


def _prepare_run(output: Path, resolved: Mapping[str, Any]) -> None:
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        sentinel = output / RUN_SENTINEL
        if not sentinel.is_file() or sentinel.read_text(encoding="utf-8") != RUN_SENTINEL_CONTENT:
            raise ValueError(f"refusing to use a non-owned nonempty run directory: {output}")
        existing = output / "resolved_experiment.json"
        if not existing.is_file():
            raise ValueError("existing run configuration differs; select a new output directory")
        existing_resolved = _load_json(existing)
        if _canonical_json(existing_resolved) != _canonical_json(resolved):
            existing_without_manifest = dict(existing_resolved)
            current_without_manifest = dict(resolved)
            source_manifest = existing_without_manifest.pop(
                "package_manifest_sha256", None
            )
            target_manifest = current_without_manifest.pop(
                "package_manifest_sha256", None
            )
            manifest_path = PACKAGE_ROOT / "PACKAGE_MANIFEST.sha256"
            current_manifest = (
                _sha256_file(manifest_path) if manifest_path.is_file() else None
            )
            manifest_only_hotfix = bool(
                source_manifest == LEGACY_EVENT_SAMPLER_MANIFEST_SHA256
                and isinstance(target_manifest, str)
                and target_manifest != source_manifest
                and target_manifest == current_manifest
                and existing_resolved.get("profile") == "carry_discovery"
                and resolved.get("profile") == "carry_discovery"
                and _canonical_json(existing_without_manifest)
                == _canonical_json(current_without_manifest)
            )
            if not manifest_only_hotfix:
                raise ValueError(
                    "existing run configuration differs; select a new output directory"
                )
            migration = {
                "schema_version": HOTFIX_MIGRATION_SCHEMA,
                "migration": "v0.4.0_event_sampler_generation_hotfix",
                "profile": "carry_discovery",
                "source_package_manifest_sha256": source_manifest,
                "target_package_manifest_sha256": target_manifest,
                "resolved_configuration_unchanged_except_package_manifest": True,
                "existing_training_state_preserved": True,
            }
            migration_path = output / HOTFIX_MIGRATION_FILE
            if migration_path.is_file():
                if _canonical_json(_load_json(migration_path)) != _canonical_json(
                    migration
                ):
                    raise ValueError(
                        "existing package hotfix migration provenance conflicts with "
                        "this package"
                    )
            else:
                _atomic_json(migration, migration_path)
            print(
                "PACKAGE_HOTFIX_RESUME=PASS "
                f"SOURCE_MANIFEST={source_manifest} TARGET_MANIFEST={target_manifest}",
                flush=True,
            )
    else:
        output.mkdir(parents=True, exist_ok=True)
        (output / RUN_SENTINEL).write_text(
            RUN_SENTINEL_CONTENT, encoding="utf-8", newline="\n"
        )
        _atomic_json(dict(resolved), output / "resolved_experiment.json")
    for directory in ("training", "behavior", "geometry", "causal"):
        (output / directory).mkdir(parents=True, exist_ok=True)


def _discovery_lock_requirements() -> tuple[Path, str, set[int], int]:
    profile_path = PACKAGE_ROOT / "configs" / "carry_discovery.json"
    if not profile_path.is_file():
        raise FileNotFoundError(
            f"bundled discovery profile is missing: {profile_path}"
        )
    profile = validate_profile(_load_json(profile_path), "carry_discovery")
    configured_seeds, _, _ = _resolve_seeds(profile["seeds"], None)
    raw_seeds = profile["seeds"]
    if not isinstance(raw_seeds, Mapping):
        raise ValueError("carry_discovery seeds must be an object")
    required_support = raw_seeds.get("minimum_lock_support")
    if (
        type(required_support) is not int
        or required_support < 1
        or required_support > len(configured_seeds)
    ):
        raise ValueError(
            "carry_discovery seeds.minimum_lock_support must be between 1 and "
            "the number of configured exploration seeds"
        )
    return (
        profile_path,
        _sha256_file(profile_path),
        set(configured_seeds),
        required_support,
    )


def _read_analysis_lock(path: str | Path) -> tuple[dict[str, Any], str]:
    lock_path = Path(path).resolve()
    if not lock_path.is_file():
        raise FileNotFoundError(f"confirmatory analysis lock is missing: {lock_path}")
    value = _load_json(lock_path)
    if value.get("schema_version") != "arithmetic-workspace-analysis-lock-v1":
        raise ValueError("analysis lock has an unsupported or missing schema_version")
    if value.get("source_profile") != "carry_discovery":
        raise ValueError("analysis lock source_profile must be carry_discovery")
    discovery_profile_path, expected_profile_sha256, expected_seeds, required_support = (
        _discovery_lock_requirements()
    )
    if value.get("source_profile_configuration_sha256") != expected_profile_sha256:
        raise ValueError(
            "analysis lock is stale or does not match the bundled carry_discovery profile"
        )
    selection = value.get("selection")
    if not isinstance(selection, Mapping):
        raise ValueError("analysis lock must contain a selection object")
    for key in ("source_layer", "upstream_layer", "rank"):
        _positive_integer(
            selection.get(key),
            f"analysis lock selection.{key}",
            allow_zero=key == "upstream_layer",
        )
    if int(selection["upstream_layer"]) >= int(selection["source_layer"]):
        raise ValueError("analysis lock requires upstream_layer < source_layer")
    expected_rule = "modal_seed_selection_then_mean_target_blind_score"
    if selection.get("selection_rule") != expected_rule:
        raise ValueError(f"analysis lock selection_rule must be {expected_rule}")
    supporting = selection.get("supporting_seed_count")
    if type(supporting) is not int or supporting < required_support:
        raise ValueError(
            "analysis lock has insufficient independent discovery-seed support: "
            f"required {required_support}, observed {supporting!r}"
        )
    per_seed = value.get("per_seed_target_blind_selections")
    if not isinstance(per_seed, list) or len(per_seed) < required_support:
        raise ValueError("analysis lock is missing its per-seed target-blind selections")
    seed_ids = [
        row.get("seed") for row in per_seed if isinstance(row, Mapping)
    ]
    if (
        len(seed_ids) != len(per_seed)
        or any(type(seed) is not int for seed in seed_ids)
        or len(set(seed_ids)) != len(seed_ids)
        or set(seed_ids) != expected_seeds
    ):
        raise ValueError(
            "analysis lock per-seed selections do not match the bundled discovery seeds"
        )
    selected_key = (
        int(selection["source_layer"]),
        int(selection["upstream_layer"]),
        int(selection["rank"]),
    )
    discovery_profile = validate_profile(
        _load_json(discovery_profile_path), "carry_discovery"
    )
    allowed_layers = sorted(
        set(int(value) for value in discovery_profile["space"].get("layers", []))
    )
    allowed_ranks = set(
        int(value)
        for value in discovery_profile["space"].get(
            "rank_sweep", [discovery_profile["space"].get("rank")]
        )
    )
    source_layer, upstream_layer, selected_rank = selected_key
    earlier_layers = [value for value in allowed_layers if value < source_layer]
    expected_upstream = max(earlier_layers) if earlier_layers else max(
        0, source_layer - 2
    )
    if (
        source_layer not in allowed_layers
        or upstream_layer != expected_upstream
        or selected_rank not in allowed_ranks
    ):
        raise ValueError(
            "analysis lock selection is outside the bundled discovery layer/rank sweep"
        )
    matching_support = sum(
        (
            int(row.get("source_layer", -1)),
            int(row.get("upstream_layer", -1)),
            int(row.get("rank", -1)),
        )
        == selected_key
        for row in per_seed
        if isinstance(row, Mapping)
    )
    if matching_support != supporting or matching_support < required_support:
        raise ValueError(
            "analysis lock supporting_seed_count is inconsistent with per-seed selections"
        )
    for row in per_seed:
        score = row.get("heldout_causal_prediction_fraction")
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(float(score))
            or not 0.0 <= float(score) <= 1.0
        ):
            raise ValueError(
                "analysis lock contains an invalid heldout causal-prediction score"
            )
    locked_policy = value.get("locked_claim_policy")
    if not isinstance(locked_policy, Mapping) or locked_policy.get(
        "allow_jspace_claim"
    ) is not False:
        raise ValueError("analysis lock must preserve the candidate-only claim policy")
    if value.get("immutable_after_confirmation_begins") is not True:
        raise ValueError("analysis lock must be marked immutable for confirmation")
    return value, _sha256_file(lock_path)


def _write_discovery_lock(
    *,
    output: Path,
    resolved: Mapping[str, Any],
    seed_results: Mapping[str, Mapping[str, Any]],
    telemetry: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    lock_path = output / "workspace_lock.json"

    def reject(reason: str) -> None:
        if telemetry is not None:
            telemetry.update(
                {"written": False, "path": str(lock_path), "reason": reason}
            )

    _, expected_profile_sha256, expected_seeds, required_support = (
        _discovery_lock_requirements()
    )
    if (
        resolved.get("profile") != "carry_discovery"
        or resolved.get("profile_configuration_sha256")
        != expected_profile_sha256
    ):
        reject("profile_provenance_does_not_match_bundled_carry_discovery")
        return None
    selections: list[dict[str, Any]] = []
    for seed, result in seed_results.items():
        geometry = result.get("geometry")
        if not isinstance(geometry, Mapping):
            continue
        if "correct" in geometry and isinstance(geometry["correct"], Mapping):
            geometry = geometry["correct"]
        if not _representation_pass(geometry, _claim_policy(resolved)):
            continue
        candidate = geometry.get("candidate")
        if not isinstance(candidate, Mapping):
            continue
        selections.append(
            {
                "seed": int(seed),
                "source_layer": int(candidate.get("source_layer", -1)),
                "upstream_layer": int(candidate.get("upstream_layer", -1)),
                "rank": int(candidate.get("rank", -1)),
                "heldout_causal_prediction_fraction": float(
                    geometry.get("target_blind_layer_selection_score", float("-inf"))
                ),
            }
        )
    valid = [
        row
        for row in selections
        if row["source_layer"] > row["upstream_layer"] >= 0 and row["rank"] > 0
    ]
    if not valid:
        reject("no_seed_passed_the_registered_representation_gate")
        return None
    if {int(row["seed"]) for row in valid} != expected_seeds:
        reject("missing_or_unexpected_discovery_seed_selection")
        return None
    # Pre-register the modal target-blind selection; deterministic ties favor
    # the tuple with the best mean held-out causal-prediction fraction.
    grouped: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    for row in valid:
        key = (row["source_layer"], row["upstream_layer"], row["rank"])
        grouped.setdefault(key, []).append(row)
    chosen_key, chosen_rows = max(
        grouped.items(),
        key=lambda item: (
            len(item[1]),
            sum(row["heldout_causal_prediction_fraction"] for row in item[1])
            / len(item[1]),
            -item[0][0],
            -item[0][2],
        ),
    )
    if len(chosen_rows) < required_support:
        reject(
            "modal_selection_support_below_minimum:"
            f"{len(chosen_rows)}<{required_support}"
        )
        return None
    lock = {
        "schema_version": "arithmetic-workspace-analysis-lock-v1",
        "source_profile": resolved["profile"],
        "source_profile_configuration_sha256": resolved[
            "profile_configuration_sha256"
        ],
        "selection": {
            "source_layer": chosen_key[0],
            "upstream_layer": chosen_key[1],
            "rank": chosen_key[2],
            "selection_rule": "modal_seed_selection_then_mean_target_blind_score",
            "supporting_seed_count": len(chosen_rows),
        },
        "per_seed_target_blind_selections": valid,
        "locked_claim_policy": dict(resolved.get("claim_policy", {})),
        "immutable_after_confirmation_begins": True,
    }
    _atomic_json(lock, lock_path)
    if telemetry is not None:
        telemetry.update(
            {
                "written": True,
                "path": str(lock_path),
                "reason": "modal_selection_met_registered_minimum_support",
            }
        )
    return lock


def _progress(output: Path, event: str, **values: Any) -> None:
    row = {"event": event, "time_unix": time.time(), **values}
    _append_jsonl(row, output / "progress.jsonl")


def _enabled_arms(resolved: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(arm) for arm in resolved["arms"] if bool(arm.get("enabled", True))]


def _evaluation_panels(resolved: Mapping[str, Any]) -> list[dict[str, Any]]:
    evaluation = resolved["evaluation"]
    raw = evaluation.get("panels", evaluation.get("splits"))
    panels: list[dict[str, Any]] = []
    if isinstance(raw, Mapping):
        for name, child in raw.items():
            if isinstance(child, int):
                child = {"count": child}
            if not isinstance(child, Mapping):
                raise ValueError(f"evaluation panel {name} must be an object")
            panels.append({"name": str(name), **dict(child)})
    elif isinstance(raw, list):
        for child in raw:
            if isinstance(child, str):
                panels.append({"name": child, "split": child})
            elif isinstance(child, Mapping):
                panels.append(dict(child))
            else:
                raise ValueError("evaluation.panels entries must be strings or objects")
    elif raw is not None:
        raise ValueError("evaluation.panels must be an object or array")
    if not panels:
        count = int(evaluation.get("examples_per_panel", evaluation.get("eval_samples", 256)))
        panels = [
            {"name": "iid", "split": "test_iid", "count": count},
            {"name": "ood_plus1", "split": "test_ood_plus1", "count": count},
            {"name": "ood_plus2", "split": "test_ood_plus2", "count": count},
        ]
    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, panel in enumerate(panels):
        name = panel.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"evaluation panel {index} requires a unique name")
        names.add(name)
        count = int(
            panel.get(
                "count",
                evaluation.get(
                    "examples_per_panel", evaluation.get("full_items", 256)
                ),
            )
        )
        if count <= 0:
            raise ValueError(f"evaluation panel {name} has a nonpositive count")
        normalized.append(
            {
                **panel,
                "name": name,
                "split": str(panel.get("split", name)),
                "count": count,
            }
        )
    return normalized


def _final_checkpoint(summary: Mapping[str, Any], arm_output: Path, max_steps: int) -> Path:
    for key in ("final_checkpoint", "final_checkpoint_path", "checkpoint_path"):
        value = summary.get(key)
        if isinstance(value, str) and value:
            path = Path(value)
            return path if path.is_absolute() else (arm_output / path).resolve()
    return arm_output / "checkpoints" / f"model_step_{max_steps:06d}.pt"


def _load_model(components: Components, checkpoint: Path, device: Any) -> tuple[Any, dict[str, Any]]:
    loaded = _supported_call(
        components.load_research_checkpoint,
        checkpoint=checkpoint,
        checkpoint_path=checkpoint,
        device=device,
    )
    if isinstance(loaded, tuple) and len(loaded) == 2:
        model, payload = loaded
        return model, dict(payload) if isinstance(payload, Mapping) else {}
    return loaded, {}


def _evaluate_arm_behavior(
    *,
    components: Components,
    resolved: Mapping[str, Any],
    provider: Any,
    arm: str,
    model: Any,
    seed: int,
    device: Any,
    output: Path,
) -> dict[str, Any]:
    tokenizer = ByteTokenizer()
    evaluation_config = resolved["evaluation"]
    panels: dict[str, Any] = {}
    skipped_panels: list[dict[str, Any]] = []
    for panel in _evaluation_panels(resolved):
        stage = panel.get("stage")
        structures = (
            stage.get("structure_cycle", [])
            if isinstance(stage, Mapping)
            else []
        )
        transfer_panel = bool(
            {str(value) for value in structures} & {"event", "chain"}
        ) or any(
            label in panel["name"].lower() for label in ("carry", "borrow", "transfer")
        )
        data_arm = (
            "correct"
            if arm == "no_carry"
            and transfer_panel
            and "no_transfer" not in panel["name"].lower()
            else arm
        )
        examples = provider.fixed_eval(
            data_arm,
            panel["split"],
            panel["count"],
            stage=panel.get("stage"),
        )
        report = _supported_call(
            components.evaluate_free_generation,
            model=model,
            examples=examples,
            tokenizer=tokenizer,
            device=device,
            max_new_tokens=int(
                evaluation_config.get(
                    "max_new_tokens",
                    evaluation_config.get("generation_max_new_tokens", 32),
                )
            ),
            batch_size=int(
                evaluation_config.get(
                    "batch_size", evaluation_config.get("full_batch_size", 64)
                )
            ),
            retain_items=bool(evaluation_config.get("retain_items", False)),
        )
        panels[panel["name"]] = {
            "definition": panel,
            "evaluation_target_arm": data_arm,
            "input_expression_fingerprint": hashlib.sha256(
                _canonical_json(
                    [
                        {
                            "pair_id": str(getattr(example, "pair_id", "")),
                            "prompt": str(getattr(example, "prompt", "")),
                        }
                        for example in examples
                    ]
                ).encode("utf-8")
            ).hexdigest(),
            "report": report,
        }
        exact = _extract_exact(report)
        print(
            f"BEHAVIOR SEED={seed} ARM={arm} PANEL={panel['name']} "
            f"EXACT={exact:.6f} STATUS=PASS",
            flush=True,
        )

    gates = _gate_for_arm(resolved["competence_gates"], arm)
    evaluations = {name: child["report"] for name, child in panels.items()}
    competence = _supported_call(
        components.competence_report,
        evaluations=evaluations,
        gates=gates,
        gate_name="probe_requires" if arm == "correct" else f"{arm}_requires",
    )
    if not isinstance(competence, Mapping):
        raise TypeError("competence_report must return an object")
    result = {
        "status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "arm": arm,
        "panels": panels,
        "skipped_panels": skipped_panels,
        "competence": dict(competence),
        "probe_competence": dict(competence),
        "claim_competence": {
            "status": "INCOMPLETE",
            "ready": False,
            "reason": "claim gate is computed only after paired control evaluation",
        },
    }
    _atomic_json(result, output)
    return result


def _refresh_claim_competence(
    *,
    components: Components,
    resolved: Mapping[str, Any],
    behavior: dict[str, dict[str, Any]],
) -> None:
    correct = behavior["correct"]
    deranged = behavior["deranged"]
    evaluations = {
        name: value["report"]
        for name, value in correct["panels"].items()
        if isinstance(value, Mapping) and isinstance(value.get("report"), Mapping)
    }
    margins: list[float] = []
    for name, correct_panel in correct["panels"].items():
        deranged_panel = deranged["panels"].get(name)
        if not isinstance(correct_panel, Mapping) or not isinstance(deranged_panel, Mapping):
            continue
        correct_report = correct_panel.get("report")
        deranged_report = deranged_panel.get("report")
        if not isinstance(correct_report, Mapping) or not isinstance(deranged_report, Mapping):
            continue
        correct_exact = _extract_exact(correct_report)
        deranged_oracle = deranged_report.get("arithmetic_oracle_exact_match")
        if isinstance(deranged_oracle, (int, float)) and not isinstance(deranged_oracle, bool):
            margins.append(correct_exact - float(deranged_oracle))
    if margins:
        evaluations["control_margin"] = min(margins)
    claim = _supported_call(
        components.competence_report,
        evaluations=evaluations,
        gates=resolved["competence_gates"],
        gate_name="claim_requires",
    )
    if not isinstance(claim, Mapping):
        raise TypeError("claim competence report must be an object")
    correct["claim_competence"] = dict(claim)
    correct["control_margin"] = min(margins) if margins else None


def _gate_for_arm(gates: Mapping[str, Any], arm: str) -> dict[str, Any]:
    for key in (arm, f"{arm}_requires"):
        value = gates.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    for key in ("probe_requires", "primary", "correct"):
        value = gates.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    # A nested gate schema with no applicable arm is not a numeric threshold
    # map. Return an explicit permissive engineering gate rather than passing
    # dictionaries into the trainer's threshold parser.
    if any(isinstance(value, Mapping) for value in gates.values()):
        return {"iid_exact": 0.0, "malformed_max": 1.0}
    return dict(gates)


def _extract_exact(report: Mapping[str, Any]) -> float:
    for key in (
        "answer_exact_match",
        "exact_match",
        "exact_accuracy",
        "accuracy",
        "rate",
    ):
        value = report.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    generation = report.get("generation")
    if isinstance(generation, Mapping):
        return _extract_exact(generation)
    return 0.0


def _gate_pass(report: Mapping[str, Any]) -> bool:
    for key in ("pass", "passed", "gate_pass", "all_pass", "ready"):
        if key in report:
            return bool(report[key])
    status = report.get("status")
    return isinstance(status, str) and status.upper() == "PASS"


def _prefixes(examples: Sequence[Any], tokenizer: ByteTokenizer) -> list[list[int]]:
    return [tokenizer.prefix(str(example.prompt)) for example in examples]


def _space_counts(space_config: Mapping[str, Any]) -> tuple[int, int]:
    discovery = int(
        space_config.get(
            "discovery_examples",
            space_config.get("train_examples", space_config.get("fit_items", 256)),
        )
    )
    selection = int(
        space_config.get(
            "selection_examples",
            space_config.get(
                "heldout_examples", space_config.get("holdout_items", 128)
            ),
        )
    )
    if discovery <= 0 or selection <= 0:
        raise ValueError("space discovery and selection example counts must be positive")
    return discovery, selection


def _balanced_mapping(
    space_config: Mapping[str, Any], source_layer: int, upstream_layer: int, seed: int
) -> dict[str, Any]:
    candidate_ranks = space_config.get(
        "candidate_ranks",
        space_config.get("rank_sweep", [int(space_config.get("rank", 8))]),
    )
    return {
        **dict(space_config),
        "source_layer": int(source_layer),
        "upstream_layer": int(upstream_layer),
        "candidate_ranks": tuple(int(value) for value in candidate_ranks),
        "perturbations_per_prompt": int(
            space_config.get(
                "perturbations_per_prompt",
                space_config.get("perturbations_per_item", 4),
            )
        ),
        "ridge": float(
            space_config.get("ridge", space_config.get("whitening_ridge", 1e-4))
        ),
        "prediction_fraction_threshold": float(
            space_config.get(
                "prediction_fraction_threshold",
                space_config.get("minimum_heldout_causal_prediction", 0.80),
            )
        ),
        "random_output_consumers": int(
            space_config.get("random_output_consumers", 4)
        ),
        "seed": int(seed + source_layer * 1009 + upstream_layer * 9176),
        "token_position": -1,
    }


def _balanced_score(summary: Mapping[str, Any]) -> float:
    metadata = summary.get("metadata")
    if not isinstance(metadata, Mapping):
        return float("-inf")
    selected = metadata.get("selected_rank", summary.get("rank"))
    table = metadata.get("rank_selection", [])
    if isinstance(table, list):
        for row in table:
            if isinstance(row, Mapping) and row.get("rank") == selected:
                value = row.get("heldout_causal_prediction_fraction")
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    return float(value)
    return float("-inf")


def _run_geometry(
    *,
    components: Components,
    resolved: Mapping[str, Any],
    provider: Any,
    model: Any,
    seed: int,
    arm: str,
    device: Any,
    output: Path,
) -> tuple[Any, dict[str, Any]]:
    tokenizer = ByteTokenizer()
    space_config = resolved["space"]
    discovery_count, selection_count = _space_counts(space_config)
    discovery_split = str(space_config.get("discovery_split", "space_discovery"))
    selection_split = str(space_config.get("selection_split", "space_selection"))
    discovery_examples = provider.fixed_eval(arm, discovery_split, discovery_count)
    selection_examples = provider.fixed_eval(arm, selection_split, selection_count)
    output.parent.mkdir(parents=True, exist_ok=True)
    layers = [int(value) for value in space_config.get("layers", [])]
    if "source_layer" in space_config:
        layers = [int(space_config["source_layer"])]
    if not layers:
        layers = [max(1, int(resolved["model"]["n_layers"]) - 2)]
    locked = space_config.get("locked_selection")
    if isinstance(locked, Mapping):
        layers = [int(locked["source_layer"])]
    candidates: list[tuple[float, int, Any, dict[str, Any], Path]] = []
    discovery_prefixes = _prefixes(discovery_examples, tokenizer)
    selection_prefixes = _prefixes(selection_examples, tokenizer)
    model_layers = int(resolved["model"]["n_layers"])
    for source_layer in sorted(set(layers)):
        if not 1 <= source_layer < model_layers:
            continue
        if isinstance(locked, Mapping):
            upstream_layer = int(locked["upstream_layer"])
        else:
            earlier = [value for value in layers if 0 <= value < source_layer]
            upstream_layer = max(earlier) if earlier else max(0, source_layer - 2)
        mapped = _balanced_mapping(space_config, source_layer, upstream_layer, seed)
        if isinstance(locked, Mapping) and "rank" in locked:
            mapped["candidate_ranks"] = (int(locked["rank"]),)
        configuration = _construct_config(components.balanced_config_type, mapped)
        print(
            f"BALANCED_SPACE_START SEED={seed} ARM={arm} "
            f"SOURCE_LAYER={source_layer} UPSTREAM_LAYER={upstream_layer} "
            f"FIT_ITEMS={discovery_count} SELECTION_ITEMS={selection_count}",
            flush=True,
        )
        candidate = _supported_call(
            components.discover_balanced_space,
            model=model,
            discovery_prefixes=discovery_prefixes,
            selection_prefixes=selection_prefixes,
            config=configuration,
            device=device,
        )
        if not hasattr(candidate, "save"):
            raise TypeError("discover_balanced_space must return an object with save(path)")
        candidate_file = output.parent / f"candidate_layer_{source_layer:02d}.pt"
        candidate.save(candidate_file)
        candidate_summary = candidate.summary() if hasattr(candidate, "summary") else {}
        if not isinstance(candidate_summary, Mapping):
            raise TypeError("BalancedSpace.summary() must return an object")
        candidates.append(
            (
                _balanced_score(candidate_summary),
                source_layer,
                candidate,
                dict(candidate_summary),
                candidate_file,
            )
        )
    if not candidates:
        raise ValueError("space.layers contains no valid source layer")
    # Selection is target blind: the held-out response diagnostics contain no
    # answers. Ties choose the earlier layer and then the smaller rank.
    score, _, space, summary, source_file = max(
        candidates,
        key=lambda row: (row[0], -row[1], -int(row[3].get("rank", 10**9))),
    )
    space_file = output.with_suffix(".pt")
    space.save(space_file)
    report = {
        "status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "arm": arm,
        "candidate_file": str(space_file),
        "candidate": dict(summary),
        "source_candidate_file": str(source_file),
        "target_blind_layer_selection_score": score,
        "layer_candidates": [
            {
                "source_layer": source_layer,
                "heldout_causal_prediction_fraction": candidate_score,
                "artifact": str(candidate_file),
                "summary": candidate_summary,
            }
            for candidate_score, source_layer, _, candidate_summary, candidate_file in candidates
        ],
        "discovery_target_blind": True,
        "completion_or_answer_labels_used": False,
    }
    _atomic_json(report, output.with_suffix(".json"))
    print(
        f"BALANCED_SPACE SEED={seed} ARM={arm} STATUS=PASS "
        f"RANK={getattr(space, 'rank', report['candidate'].get('rank', 'unknown'))}",
        flush=True,
    )
    return space, report


def _metadata_dict(example: Any) -> dict[str, Any]:
    metadata = getattr(example, "metadata", {})
    if hasattr(metadata, "to_dict"):
        metadata = metadata.to_dict()
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def _causal_pairs(
    examples: Sequence[Any], count: int, tokenizer: ByteTokenizer
) -> tuple[list[Any], list[Any]]:
    """Make deterministic donor/recipient pairs matched on operation and token shape."""

    groups: dict[tuple[Any, ...], list[Any]] = {}
    for example in examples:
        key = (
            getattr(example, "operation", None),
            len(tokenizer.prefix(str(example.prompt))),
            len(tokenizer.encode(str(example.answer))),
        )
        groups.setdefault(key, []).append(example)
    clean: list[Any] = []
    corrupt: list[Any] = []
    for key in sorted(groups, key=repr):
        group = sorted(groups[key], key=lambda child: str(getattr(child, "pair_id", "")))
        if len(group) < 2:
            continue
        # Prefer a structural mismatch so a successful patch has a falsifiable target.
        for left_index in range(0, len(group) - 1, 2):
            left, right = group[left_index], group[left_index + 1]
            if str(left.answer) == str(right.answer):
                continue
            left_meta, right_meta = _metadata_dict(left), _metadata_dict(right)
            if left_meta == right_meta and len(group) > left_index + 2:
                right = group[left_index + 2]
            clean.append(left)
            corrupt.append(right)
            if len(clean) >= count:
                return clean, corrupt
    return clean, corrupt


def _run_causal(
    *,
    components: Components,
    resolved: Mapping[str, Any],
    provider: Any,
    model: Any,
    space: Any,
    seed: int,
    arm: str,
    device: Any,
    output: Path,
) -> dict[str, Any]:
    tokenizer = ByteTokenizer()
    causal_config = resolved["causal"]
    count = int(
        causal_config.get(
            "pairs",
            causal_config.get(
                "examples", resolved["evaluation"].get("causal_items", 128)
            ),
        )
    )
    pool_multiplier = int(causal_config.get("pair_pool_multiplier", 6))
    if count <= 0 or pool_multiplier < 2:
        raise ValueError("causal pair count must be positive and pool multiplier at least two")
    split = str(causal_config.get("split", "causal_sealed"))
    semantically_matched = False
    counterfactual_metadata: list[dict[str, Any]] = []
    if hasattr(provider, "counterfactual_pairs"):
        provided_pairs = provider.counterfactual_pairs(arm, split, count)
        clean = [
            pair.clean if hasattr(pair, "clean") else pair[0]
            for pair in provided_pairs
        ]
        corrupt = [
            pair.corrupt if hasattr(pair, "corrupt") else pair[1]
            for pair in provided_pairs
        ]
        for index, pair in enumerate(provided_pairs):
            if hasattr(pair, "to_dict"):
                value = pair.to_dict()
                if isinstance(value, Mapping):
                    counterfactual_metadata.append(dict(value))
                    continue
            counterfactual_metadata.append(
                {
                    "pair_index": index,
                    "pair_id": getattr(pair, "pair_id", None),
                    "event_type": getattr(pair, "event_type", None),
                    "event_column": getattr(pair, "event_column", None),
                    "expected_affected_digits": getattr(
                        pair, "expected_affected_digits", None
                    ),
                    "expected_unaffected_digits": getattr(
                        pair, "expected_unaffected_digits", None
                    ),
                }
            )
        semantically_matched = True
    else:
        pool = provider.fixed_eval(arm, split, count * pool_multiplier)
        clean, corrupt = _causal_pairs(pool, count, tokenizer)
    minimum = int(causal_config.get("minimum_pairs", min(count, 16)))
    if len(clean) < minimum:
        raise RuntimeError(
            f"only {len(clean)} matched causal pairs were available; minimum is {minimum}"
        )
    configured_controls = tuple(
        str(value)
        for value in causal_config.get(
            "controls", ["candidate", "pca", "random", "complement"]
        )
    )
    # The candidate is always evaluated by run_causal_assay; its ``controls``
    # argument names only the rank-matched alternatives stored on the space.
    controls = tuple(value for value in configured_controls if value != "candidate")
    print(
        f"CAUSAL_ASSAY_START SEED={seed} ARM={arm} PAIRS={len(clean)} "
        f"SPACES={','.join(configured_controls)}",
        flush=True,
    )
    report = _supported_call(
        components.run_causal_assay,
        model=model,
        clean_prefixes=_prefixes(clean, tokenizer),
        corrupt_prefixes=_prefixes(corrupt, tokenizer),
        clean_expected=[str(example.completion) for example in clean],
        corrupt_expected=[str(example.completion) for example in corrupt],
        space=space,
        tokenizer=tokenizer,
        device=device,
        max_new_tokens=int(
            causal_config.get(
                "max_new_tokens",
                resolved["evaluation"].get("generation_max_new_tokens", 32),
            )
        ),
        controls=controls,
        require_directional_donor_effect=bool(
            causal_config.get("require_directional_donor_effect", True)
        ),
        minimum_baseline_qualified_pairs=int(
            causal_config.get("minimum_baseline_qualified_pairs", 1)
        ),
        minimum_directional_rescue_pairs=int(
            causal_config.get("minimum_directional_rescue_pairs", 1)
        ),
    )
    if not isinstance(report, Mapping):
        raise TypeError("run_causal_assay must return an object")
    result = {
        **dict(report),
        "status": "PASS",
        "schema_version": str(report.get("schema_version", SCHEMA_VERSION)),
        "seed": seed,
        "arm": arm,
        "sealed_evaluation": True,
        "discovery_examples_reused": False,
        "matched_pairs_requested": count,
        "matched_pairs_used": len(clean),
        "controls_required": list(configured_controls),
        "semantically_matched_counterfactual_pairs": semantically_matched,
        "pairing_claim_eligible": semantically_matched,
        "counterfactual_pair_metadata": counterfactual_metadata,
    }
    _annotate_directional_digits(result, counterfactual_metadata)
    _atomic_json(result, output)
    print(
        f"CAUSAL_ASSAY SEED={seed} ARM={arm} PAIRS={len(clean)} STATUS=PASS",
        flush=True,
    )
    return result


def _right_indexed_digit(text: str, position: int) -> str | None:
    digits = str(text).strip().lstrip("-")
    index = len(digits) - 1 - int(position)
    return digits[index] if 0 <= index < len(digits) else None


def _signed_digit_shape(text: str) -> tuple[bool, int] | None:
    """Return sign and digit width for a canonical signed decimal string."""

    value = str(text).strip()
    if not re.fullmatch(r"-?[0-9]+", value):
        return None
    return value.startswith("-"), len(value.lstrip("-"))


def _positions_match(output: str, target: str, positions: Sequence[int]) -> bool:
    return all(
        _right_indexed_digit(output, position)
        == _right_indexed_digit(target, position)
        for position in positions
    )


def _annotate_directional_digits(
    report: dict[str, Any], metadata: Sequence[Mapping[str, Any]]
) -> None:
    spaces = report.get("spaces")
    if not isinstance(spaces, Mapping) or not metadata:
        return
    for section in spaces.values():
        if not isinstance(section, dict):
            continue
        patch = section.get("clean_to_corrupt_patch")
        if not isinstance(patch, dict):
            continue
        items = patch.get("directional_items")
        if not isinstance(items, list):
            continue
        annotated = 0
        qualified = 0
        affected_matches = 0
        unaffected_preserved = 0
        both = 0
        for index, item in enumerate(items):
            if not isinstance(item, dict) or index >= len(metadata):
                continue
            pair = metadata[index]
            affected = [int(value) for value in pair.get("expected_affected_digits", [])]
            unaffected = [int(value) for value in pair.get("expected_unaffected_digits", [])]
            output_text = str(item.get("output", ""))
            clean_target = str(item.get("clean_expected", ""))
            corrupt_target = str(item.get("corrupt_expected", ""))
            output_shape = _signed_digit_shape(output_text)
            clean_shape = _signed_digit_shape(clean_target)
            corrupt_shape = _signed_digit_shape(corrupt_target)
            directional_output_valid = bool(
                item.get("output_well_formed", False)
                and output_shape is not None
                and output_shape == clean_shape == corrupt_shape
            )
            affected_ok = directional_output_valid and bool(affected) and _positions_match(
                output_text, clean_target, affected
            )
            unaffected_ok = directional_output_valid and (
                (not unaffected)
                or _positions_match(output_text, corrupt_target, unaffected)
            )
            item["counterfactual_pair_id"] = pair.get("pair_id")
            item["event_type"] = pair.get("event_type")
            item["event_column"] = pair.get("event_column")
            item["directional_output_valid"] = directional_output_valid
            item["affected_digits_match_clean_donor"] = affected_ok
            item["unaffected_digits_preserve_recipient"] = unaffected_ok
            annotated += 1
            if not bool(item.get("baseline_qualified", False)):
                continue
            qualified += 1
            affected_matches += int(affected_ok)
            unaffected_preserved += int(unaffected_ok)
            both += int(affected_ok and unaffected_ok)
        patch["directional_digit_audit"] = {
            "items": annotated,
            "qualified_denominator_count": qualified,
            "affected_digits_match_clean_donor_rate": affected_matches
            / max(1, qualified),
            "unaffected_digits_preserve_recipient_rate": unaffected_preserved
            / max(1, qualified),
            "joint_predicted_direction_count": both,
            "joint_predicted_direction_rate": (
                None if qualified == 0 else both / qualified
            ),
            "claim_eligible": qualified > 0,
        }


def _as_rate(mapping: Mapping[str, Any], keys: Sequence[str]) -> float | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _control_section(report: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    for container_name in ("spaces", "controls", "interventions", "results"):
        container = report.get(container_name)
        if isinstance(container, Mapping) and isinstance(container.get(name), Mapping):
            return container[name]
    value = report.get(name)
    return value if isinstance(value, Mapping) else {}


def _intervention_metric(section: Mapping[str, Any], kind: str) -> float | None:
    section_key = {
        "patch": "clean_to_corrupt_patch",
        "rescue": "coordinate_rescue",
    }.get(kind, kind)
    value = section.get(section_key)
    if not isinstance(value, Mapping):
        return None
    primary = value.get("primary_estimand")
    if isinstance(primary, Mapping):
        if not bool(primary.get("claim_eligible", False)):
            return None
        denominator = primary.get("qualified_denominator_count")
        registered_minimum = primary.get("registered_minimum_qualified_pairs")
        if (
            not isinstance(denominator, int)
            or isinstance(denominator, bool)
            or not isinstance(registered_minimum, int)
            or isinstance(registered_minimum, bool)
            or denominator < registered_minimum
        ):
            return None
        primary_key = {
            "ablation": "qualified_loss_rate",
            "patch": "qualified_clean_conversion_rate",
            "rescue": "qualified_rescue_rate",
        }.get(kind)
        if primary_key is not None:
            return _as_rate(primary, (primary_key,))
    if kind == "ablation":
        direct = _as_rate(
            value,
            ("exact_drop", "accuracy_drop", "baseline_correct_lost", "effect"),
        )
        if direct is not None:
            return direct
        before = _as_rate(value, ("baseline_exact", "before_exact", "clean_exact"))
        after = _as_rate(value, ("exact_rate", "after_exact", "ablated_exact"))
        return None if before is None or after is None else before - after
    if kind == "patch":
        return _as_rate(
            value,
            (
                "baseline_error_rescued",
                "flip_rate",
                "target_flip_rate",
                "exact",
                "effect",
            ),
        )
    if kind == "rescue":
        return _as_rate(
            value,
            (
                "upstream_corruption_error_rescued",
                "baseline_error_rescued",
                "rescue_rate",
                "restoration_rate",
                "effect",
            ),
        )
    return _as_rate(value, ("rate", "effect"))


def _representation_pass(geometry: Mapping[str, Any], policy: Mapping[str, Any]) -> bool:
    candidate = geometry.get("candidate")
    if not isinstance(candidate, Mapping):
        return False
    for key in ("gate_pass", "representation_pass", "selection_pass"):
        if key in candidate:
            return bool(candidate[key])
    metadata = candidate.get("metadata")
    if not isinstance(metadata, Mapping):
        metadata = candidate
    selected = metadata.get("selected_rank", candidate.get("rank"))
    if not isinstance(selected, int) or selected <= 0:
        return False
    threshold = float(
        policy.get(
            "heldout_causal_prediction_min",
            metadata.get("prediction_fraction_threshold", 0.0),
        )
    )
    value = metadata.get("heldout_causal_prediction_fraction")
    if value is None:
        table = metadata.get("rank_selection_table", metadata.get("rank_selection"))
        if isinstance(table, list):
            matches = [row for row in table if isinstance(row, Mapping) and row.get("rank") == selected]
            if matches:
                value = matches[0].get("heldout_causal_prediction_fraction")
    return isinstance(value, (int, float)) and float(value) >= threshold


def _causal_stage_passes(
    report: Mapping[str, Any], policy: Mapping[str, Any]
) -> dict[str, bool]:
    pairing_eligible = bool(report.get("pairing_claim_eligible", False))
    instrument_flags = report.get("claim_gate_flags")
    if isinstance(instrument_flags, Mapping):
        independent_rescue = bool(
            instrument_flags.get(
                "independent_upstream_writer_rescue",
                instrument_flags.get(
                    "independent_upstream_residual_rescue_assay", False
                ),
            )
        )
        mediation_eligible = bool(
            instrument_flags.get("mediation_claim_eligible", False)
        )
    else:
        independent_rescue = bool(report.get("independent_rescue_available", False))
        mediation_eligible = bool(report.get("mediation_claim_eligible", False))
    explicit = report.get("claim_gates")
    if isinstance(explicit, Mapping):
        return {
            "necessity": pairing_eligible and bool(explicit.get("necessity", False)),
            "patch_and_rescue": bool(
                explicit.get("patch_and_rescue", explicit.get("patch_rescue", False))
            )
            and independent_rescue
            and pairing_eligible,
            "mediation": pairing_eligible
            and bool(explicit.get("mediation", False))
            and mediation_eligible,
            "shared_access": pairing_eligible
            and bool(explicit.get("shared_access", False)),
            "math_specificity": pairing_eligible
            and bool(explicit.get("math_specificity", False)),
        }
    candidate = _control_section(report, "candidate")
    controls = [
        _control_section(report, name)
        for name in ("pca", "random", "complement")
        if _control_section(report, name)
    ]
    margin = float(policy.get("control_margin_min", 0.05))

    def assay_metrics(section: Mapping[str, Any]) -> dict[str, float | None]:
        return {
            "ablation": _intervention_metric(section, "ablation"),
            "patch": _intervention_metric(section, "patch"),
            "rescue": _intervention_metric(section, "rescue"),
        }

    candidate_metrics = assay_metrics(candidate)
    control_metrics = [assay_metrics(section) for section in controls]

    def selective(kind: str, value: float | None, minimum: float) -> bool:
        if value is None or value < minimum or not controls:
            return False
        control_values = [
            float(metrics[kind])
            for metrics in control_metrics
            if metrics[kind] is not None
        ]
        return bool(control_values) and value >= max(control_values) + margin

    return {
        "necessity": pairing_eligible
        and selective(
            "ablation",
            candidate_metrics["ablation"],
            float(policy.get("ablation_drop_min", 0.10)),
        ),
        "patch_and_rescue": pairing_eligible
        and independent_rescue
        and selective(
            "patch",
            candidate_metrics["patch"],
            float(policy.get("patch_flip_min", 0.20)),
        )
        and selective(
            "rescue",
            candidate_metrics["rescue"],
            float(policy.get("rescue_rate_min", 0.20)),
        ),
        # These require separate registered assays; absence can never silently pass.
        "mediation": pairing_eligible
        and mediation_eligible
        and bool(report.get("mediation_pass", False)),
        "shared_access": pairing_eligible
        and bool(report.get("shared_access_pass", False)),
        "math_specificity": pairing_eligible
        and bool(report.get("math_specificity_pass", False)),
    }


def _candidate_selective_effect(report: Mapping[str, Any]) -> float | None:
    candidate = _control_section(report, "candidate")
    controls = [
        _control_section(report, name)
        for name in ("pca", "random", "complement")
        if _control_section(report, name)
    ]
    if not candidate or not controls:
        return None

    def patch_metric(section: Mapping[str, Any]) -> float | None:
        return _intervention_metric(section, "patch")

    candidate_metrics = [
        _intervention_metric(candidate, "ablation"),
        patch_metric(candidate),
        _intervention_metric(candidate, "rescue"),
    ]
    candidate_values = [value for value in candidate_metrics if value is not None]
    if not candidate_values:
        return None
    candidate_mean = sum(candidate_values) / len(candidate_values)
    control_means: list[float] = []
    for section in controls:
        values = [
            _intervention_metric(section, "ablation"),
            patch_metric(section),
            _intervention_metric(section, "rescue"),
        ]
        available = [value for value in values if value is not None]
        if available:
            control_means.append(sum(available) / len(available))
    return None if not control_means else candidate_mean - max(control_means)


def _selective_effect(report: Mapping[str, Any], kind: str) -> float | None:
    candidate = _control_section(report, "candidate")
    baseline = report.get("baseline", {})
    clean = baseline.get("clean", {}) if isinstance(baseline, Mapping) else {}
    baseline_exact = _as_rate(clean if isinstance(clean, Mapping) else {}, ("exact",))

    def value_for(section: Mapping[str, Any]) -> float | None:
        value = _intervention_metric(section, kind)
        if value is not None or kind != "ablation" or baseline_exact is None:
            return value
        # Compatibility for pre-v2/mock reports.  v2 reports always expose a
        # baseline-qualified primary estimand and never take this branch.
        ablation = section.get("ablation")
        if not isinstance(ablation, Mapping) or isinstance(
            ablation.get("primary_estimand"), Mapping
        ):
            return None
        exact = _as_rate(ablation, ("exact",))
        return None if exact is None else baseline_exact - exact

    candidate_value = value_for(candidate)
    if candidate_value is None:
        return None
    control_values = [
        value
        for name in ("pca", "random", "complement")
        if (value := value_for(_control_section(report, name)))
        is not None
    ]
    return None if not control_values else float(candidate_value) - max(control_values)


def _confirmation_statistics(
    seed_results: Mapping[str, Mapping[str, Any]],
    confirmatory_seeds: set[int],
    statistics_config: Mapping[str, Any],
    causal_config: Mapping[str, Any],
) -> dict[str, Any]:
    if not statistics_config:
        return {"status": "NOT_REQUIRED", "passed": True}
    from .workspace_stats import hierarchical_bootstrap, holm_correction, paired_effect_report

    effects: dict[str, dict[str, float]] = {
        "ablation": {},
        "patch": {},
        "rescue": {},
    }
    item_effects: dict[str, list[dict[str, Any]]] = {}
    for seed_text, result in seed_results.items():
        if int(seed_text) not in confirmatory_seeds:
            continue
        causal = result.get("causal")
        if isinstance(causal, Mapping) and isinstance(causal.get("correct"), Mapping):
            causal = causal["correct"]
        if not isinstance(causal, Mapping):
            continue
        for kind in effects:
            value = _selective_effect(causal, kind)
            if value is not None:
                effects[kind][seed_text] = value
        spaces = causal.get("spaces")
        metadata = causal.get("counterfactual_pair_metadata")
        if not isinstance(spaces, Mapping) or not isinstance(metadata, list):
            continue
        candidate = _control_section(causal, "candidate")
        candidate_patch = candidate.get("clean_to_corrupt_patch")
        candidate_items = (
            candidate_patch.get("directional_items", [])
            if isinstance(candidate_patch, Mapping)
            else []
        )
        control_items: list[list[Any]] = []
        for name in ("pca", "random", "complement"):
            section = _control_section(causal, name)
            patch = section.get("clean_to_corrupt_patch")
            if isinstance(patch, Mapping) and isinstance(patch.get("directional_items"), list):
                control_items.append(patch["directional_items"])
        records: list[dict[str, Any]] = []
        strict_qualification = str(causal.get("schema_version", "")).endswith("v2")
        for index, candidate_item in enumerate(candidate_items):
            if not isinstance(candidate_item, Mapping) or index >= len(metadata):
                continue
            candidate_eligible = bool(
                candidate_item.get("baseline_qualified", not strict_qualification)
            )
            if not candidate_eligible:
                continue
            candidate_success = bool(
                candidate_item.get(
                    "directional_output_valid", not strict_qualification
                )
                and
                candidate_item.get("affected_digits_match_clean_donor", False)
                and candidate_item.get("unaffected_digits_preserve_recipient", False)
            )
            control_success = any(
                index < len(items)
                and isinstance(items[index], Mapping)
                and bool(
                    items[index].get(
                        "baseline_qualified", not strict_qualification
                    )
                )
                and bool(
                    items[index].get(
                        "directional_output_valid", not strict_qualification
                    )
                )
                and items[index].get("affected_digits_match_clean_donor", False)
                and items[index].get("unaffected_digits_preserve_recipient", False)
                for items in control_items
            )
            meta = metadata[index] if isinstance(metadata[index], Mapping) else {}
            clean_meta = meta.get("clean", {}) if isinstance(meta, Mapping) else {}
            family_id = (
                clean_meta.get("family_id")
                if isinstance(clean_meta, Mapping)
                else None
            )
            records.append(
                {
                    "family_id": str(family_id or meta.get("pair_id", index)),
                    "effect": float(candidate_success) - float(control_success),
                }
            )
        if records:
            item_effects[seed_text] = records

    minimum_effect = float(causal_config.get("minimum_candidate_minus_random", 0.0))
    alpha = float(statistics_config.get("familywise_alpha", 0.05))
    tests = {
        name: paired_effect_report(
            values,
            minimum_effect=minimum_effect,
            alternative="greater",
            alpha=alpha,
        )
        for name, values in effects.items()
    }
    raw_p = {
        name: float(report["exact_test"]["p_value"])
        for name, report in tests.items()
        if report.get("valid") and report.get("exact_test", {}).get("p_value") is not None
    }
    holm = holm_correction(raw_p, alpha=alpha)
    bootstrap = (
        hierarchical_bootstrap(
            item_effects,
            replicates=int(
                statistics_config.get(
                    "bootstrap_samples", causal_config.get("bootstrap_samples", 5000)
                )
            ),
            confidence=float(statistics_config.get("confidence_level", 0.95)),
            random_seed=917_623,
        )
        if item_effects
        else {"valid": False, "reason": "no_family_level_directional_items"}
    )
    required = int(statistics_config.get("minimum_passing_seeds", 3))
    enough_seeds = all(len(values) >= required for values in effects.values())
    holm_pass = bool(holm.get("valid")) and all(
        value.get("reject") is True for value in holm.get("results", {}).values()
    ) and len(holm.get("results", {})) == len(effects)
    registered_minimum_effect_pass = len(tests) == len(effects) and all(
        report.get("passed") is True for report in tests.values()
    )
    bootstrap_pass = bool(bootstrap.get("valid")) and float(
        bootstrap.get("lower", float("-inf"))
    ) > 0.0
    passed = (
        enough_seeds
        and holm_pass
        and registered_minimum_effect_pass
        and bootstrap_pass
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "seed_is_replication_unit": True,
        "required_seed_count": required,
        "effects_by_contrast": effects,
        "paired_seed_tests": tests,
        "familywise_correction": holm,
        "item_family_hierarchical_bootstrap": bootstrap,
        "enough_seeds": enough_seeds,
        "holm_pass": holm_pass,
        "registered_minimum_effect": minimum_effect,
        "registered_minimum_effect_pass": registered_minimum_effect_pass,
        "bootstrap_lower_above_zero": bootstrap_pass,
    }


def _iid_exact(behavior: Mapping[str, Any]) -> float | None:
    panels = behavior.get("panels")
    if not isinstance(panels, Mapping):
        return None
    for name, value in panels.items():
        if "iid" in str(name).lower() and isinstance(value, Mapping):
            report = value.get("report", value)
            if isinstance(report, Mapping):
                return _extract_exact(report)
    return None


def _no_transfer_competence(
    behavior: Mapping[str, Any], gates: Mapping[str, Any]
) -> dict[str, Any]:
    panels = behavior.get("panels")
    panel_report: Mapping[str, Any] | None = None
    if isinstance(panels, Mapping):
        for name, value in panels.items():
            if "no_transfer" in str(name).lower() and isinstance(value, Mapping):
                candidate = value.get("report")
                if isinstance(candidate, Mapping):
                    panel_report = candidate
                    break
    thresholds = _gate_for_arm(gates, "no_carry")
    exact_min = float(thresholds.get("iid_exact", 0.0))
    malformed_max = float(thresholds.get("malformed_max", 1.0))
    exact = _extract_exact(panel_report or {})
    malformed = (
        float(panel_report.get("malformed_rate", 1.0))
        if isinstance(panel_report, Mapping)
        else 1.0
    )
    ready = panel_report is not None and exact >= exact_min and malformed <= malformed_max
    return {
        "status": "PASS" if ready else ("INCOMPLETE" if panel_report is None else "FAIL"),
        "ready": ready,
        "panel": "no_transfer",
        "observed": {"exact": exact, "malformed": malformed},
        "thresholds": {"exact_min": exact_min, "malformed_max": malformed_max},
    }


def _math_specificity_report(
    behavior: Mapping[str, Mapping[str, Any]],
    causal: Mapping[str, Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    arithmetic = causal.get("correct")
    pseudo = causal.get("pseudo_fst")
    arithmetic_behavior = behavior.get("correct")
    pseudo_behavior = behavior.get("pseudo_fst")
    if not all(isinstance(value, Mapping) for value in (arithmetic, pseudo, arithmetic_behavior, pseudo_behavior)):
        return {
            "status": "NOT_REACHED",
            "pass": False,
            "reason": "both competent correct and pseudo_fst causal assays are required",
        }
    arithmetic_effect = _candidate_selective_effect(arithmetic)
    pseudo_effect = _candidate_selective_effect(pseudo)
    arithmetic_exact = _iid_exact(arithmetic_behavior)
    pseudo_exact = _iid_exact(pseudo_behavior)
    if None in (arithmetic_effect, pseudo_effect, arithmetic_exact, pseudo_exact):
        return {
            "status": "INCOMPLETE",
            "pass": False,
            "reason": "specificity metrics were missing",
        }
    accuracy_tolerance = float(policy.get("specificity_accuracy_match_tolerance", 0.05))
    effect_margin = float(policy.get("math_specificity_effect_margin_min", 0.10))
    accuracy_matched = abs(float(arithmetic_exact) - float(pseudo_exact)) <= accuracy_tolerance
    selective = float(arithmetic_effect) >= float(pseudo_effect) + effect_margin
    passed = accuracy_matched and selective
    return {
        "status": "PASS" if passed else "FAIL",
        "pass": passed,
        "arithmetic_candidate_minus_controls": arithmetic_effect,
        "pseudo_candidate_minus_controls": pseudo_effect,
        "arithmetic_minus_pseudo": float(arithmetic_effect) - float(pseudo_effect),
        "arithmetic_iid_exact": arithmetic_exact,
        "pseudo_iid_exact": pseudo_exact,
        "accuracy_gap": abs(float(arithmetic_exact) - float(pseudo_exact)),
        "accuracy_match_tolerance": accuracy_tolerance,
        "effect_margin_minimum": effect_margin,
    }


def _cross_arm_geometry(
    spaces: Mapping[str, Any], reports: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    summaries = {
        name: {
            "rank": report.get("candidate", {}).get("rank"),
            "source_layer": report.get("candidate", {}).get("source_layer"),
            "target_blind_selection_score": report.get(
                "target_blind_layer_selection_score"
            ),
        }
        for name, report in reports.items()
    }
    overlaps: dict[str, float] = {}
    names = sorted(spaces)
    for left_index, left_name in enumerate(names):
        left = getattr(spaces[left_name], "basis", None)
        if left is None:
            continue
        for right_name in names[left_index + 1 :]:
            right = getattr(spaces[right_name], "basis", None)
            if right is None or left.shape[0] != right.shape[0]:
                continue
            rank = min(int(left.shape[1]), int(right.shape[1]))
            if rank <= 0:
                continue
            overlap = (left.T @ right).square().sum() / rank
            overlaps[f"{left_name}__{right_name}"] = float(overlap.item())
    return {
        "status": "PASS" if reports else "NOT_REACHED",
        "arm_summaries": summaries,
        "projection_overlaps": overlaps,
        "interpretation": (
            "Descriptive only; causal arithmetic-vs-pseudo specificity remains mandatory."
        ),
    }


def _seed_claim_ladder(
    *,
    competence_pass: bool,
    geometry: Mapping[str, Any] | None,
    causal: Mapping[str, Any] | None,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    raw = {
        "competence": competence_pass,
        "representation": bool(geometry and _representation_pass(geometry, policy)),
        "necessity": False,
        "patch_and_rescue": False,
        "mediation": False,
        "shared_access": False,
        "math_specificity": False,
    }
    if causal:
        raw.update(_causal_stage_passes(causal, policy))
    reached = True
    stages: dict[str, dict[str, Any]] = {}
    for name in CLAIM_STAGES:
        passed = bool(raw[name]) if reached else False
        status = "PASS" if passed else ("FAIL" if reached else "NOT_REACHED")
        stages[name] = {"status": status, "criterion_met": bool(raw[name])}
        reached = reached and passed
    return {"stages": stages, "all_mandatory_gates_pass": reached}


def _claim_policy(resolved: Mapping[str, Any]) -> dict[str, Any]:
    causal = resolved.get("causal", {})
    space = resolved.get("space", {})
    declared = resolved.get("claim_policy", {})
    policy: dict[str, Any] = {}
    if isinstance(causal, Mapping):
        aliases = {
            "minimum_candidate_minus_random": "control_margin_min",
            "minimum_rescue_fraction": "rescue_rate_min",
        }
        for source, target in aliases.items():
            if source in causal:
                policy[target] = causal[source]
    if isinstance(space, Mapping):
        for key in (
            "prediction_fraction_threshold",
            "minimum_heldout_causal_prediction",
        ):
            if key in space:
                policy["heldout_causal_prediction_min"] = space[key]
    if isinstance(declared, Mapping):
        policy.update(declared)
    return policy


def _build_claim_summary(
    seed_results: Mapping[str, Mapping[str, Any]],
    confirmatory_seeds: set[int],
    required_confirmatory: int,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    per_seed: dict[str, Any] = {}
    passing_confirmatory: list[int] = []
    for seed_text, result in seed_results.items():
        seed = int(seed_text)
        behavior = result.get("behavior", {})
        correct = behavior.get("correct", {}) if isinstance(behavior, Mapping) else {}
        competence = (
            correct.get("claim_competence", {})
            if isinstance(correct, Mapping)
            else {}
        )
        geometry = result.get("geometry")
        causal = result.get("causal")
        if isinstance(geometry, Mapping) and isinstance(geometry.get("correct"), Mapping):
            geometry = geometry["correct"]
        if isinstance(causal, Mapping) and isinstance(causal.get("correct"), Mapping):
            causal = causal["correct"]
        ladder = _seed_claim_ladder(
            competence_pass=isinstance(competence, Mapping) and _gate_pass(competence),
            geometry=geometry if isinstance(geometry, Mapping) else None,
            causal=causal if isinstance(causal, Mapping) else None,
            policy=policy,
        )
        ladder["confirmatory_seed"] = seed in confirmatory_seeds
        per_seed[seed_text] = ladder
        if seed in confirmatory_seeds and ladder["all_mandatory_gates_pass"]:
            passing_confirmatory.append(seed)
    claim_allowed = bool(policy.get("allow_jspace_claim", False))
    established = claim_allowed and len(passing_confirmatory) >= required_confirmatory
    return {
        "status": "ESTABLISHED" if established else "NOT_ESTABLISHED",
        "claim_name": "math_specific_workspace_equivalent",
        "release_ceiling": policy.get("release_ceiling", "CANDIDATE_ONLY"),
        "unimplemented_required_assays": list(
            policy.get("unimplemented_required_assays", [])
        ),
        "claim_ladder": list(CLAIM_STAGES),
        "per_seed": per_seed,
        "confirmatory_seed_count_required": required_confirmatory,
        "confirmatory_seed_count_passed": len(passing_confirmatory),
        "passing_confirmatory_seeds": sorted(passing_confirmatory),
        "claim_allowed_by_profile": claim_allowed,
        "unimplemented_required_assays": list(
            policy.get("unimplemented_required_assays", [])
        ),
        "all_conditions_and_replication_required": True,
    }


def _dry_summary(
    resolved: Mapping[str, Any], output: Path, seeds: Sequence[int], required: int
) -> dict[str, Any]:
    seed_results = {
        str(seed): {
            "status": "DRY_RUN",
            "training": {},
            "behavior": {},
            "geometry": None,
            "causal": None,
        }
        for seed in seeds
    }
    claim = _build_claim_summary(seed_results, set(), required, _claim_policy(resolved))
    return {
        "status": "DRY_RUN",
        "schema_version": SCHEMA_VERSION,
        "profile": resolved["profile"],
        "seeds": list(seeds),
        "seed_results": seed_results,
        "claim": claim,
        "JSPACE_CLAIM": claim["status"],
        "unimplemented_required_assays": claim[
            "unimplemented_required_assays"
        ],
        "workspace_lock_written": False,
        "workspace_lock_path": None,
        "workspace_lock_reason": (
            "dry_run_does_not_analyze_seed_selections"
            if resolved["profile"] == "carry_discovery"
            else "not_a_discovery_profile"
        ),
        "result_path": str(output),
    }


def run_workspace_experiment(
    profile: str,
    output: str | Path,
    seed: int | None = None,
    device_name: str = "cuda",
    resume: bool = True,
    dry_run: bool = False,
    lock_file: str | Path | None = None,
    *,
    profile_path: str | Path | None = None,
    components: Components | None = None,
) -> dict[str, Any]:
    selected_profile_path = (
        Path(profile_path)
        if profile_path is not None
        else PACKAGE_ROOT / "configs" / f"{profile}.json"
    )
    if profile_path is None and not selected_profile_path.is_file():
        legacy_candidate = PACKAGE_ROOT / "training_configs" / f"{profile}.json"
        if legacy_candidate.is_file():
            selected_profile_path = legacy_candidate
    if not selected_profile_path.is_file():
        raise ValueError(f"unknown workspace experiment profile: {profile}")
    resolved = validate_profile(_load_json(selected_profile_path), profile)
    # v0.4 discovers and causally tests candidate spaces, but the bundled assay
    # does not yet implement pre-registered mediation or multi-query shared
    # access.  A profile cannot opt around those missing mandatory experiments.
    claim_policy = dict(resolved.get("claim_policy", {}))
    claim_policy["requested_allow_jspace_claim"] = bool(
        claim_policy.get("allow_jspace_claim", False)
    )
    claim_policy["allow_jspace_claim"] = False
    claim_policy["unimplemented_required_assays"] = [
        "formal_causal_mediation",
        "shared_multiquery_access",
        "component_specific_writer_rescue",
    ]
    resolved["claim_policy"] = claim_policy
    run_seeds, confirmatory_seeds, required_confirmatory = _resolve_seeds(
        resolved["seeds"], seed
    )
    study_phase = str(resolved["experiment"].get("study_phase", "")).lower()
    policy = resolved.get("claim_policy", {})
    if study_phase != "confirmatory":
        confirmatory_seeds = set()
    statistics = resolved.get("statistics", {})
    if isinstance(statistics, Mapping) and "minimum_passing_seeds" in statistics:
        required_confirmatory = _positive_integer(
            statistics["minimum_passing_seeds"],
            "statistics.minimum_passing_seeds",
        )
    if study_phase == "confirmatory" or bool(
        resolved["experiment"].get("analysis_locked", False)
    ):
        if lock_file is None:
            raise ValueError(
                "the confirmatory profile requires --lock-file from a completed "
                "carry_discovery run"
            )
        lock, lock_sha256 = _read_analysis_lock(lock_file)
        selection = dict(lock["selection"])
        model_layers = int(resolved["model"]["n_layers"])
        if not 0 <= int(selection["upstream_layer"]) < int(selection["source_layer"]) < model_layers:
            raise ValueError("analysis-lock layers are incompatible with the confirmatory model")
        resolved["space"]["locked_selection"] = selection
        resolved["analysis_lock"] = {
            "sha256": lock_sha256,
            "schema_version": lock.get("schema_version"),
            "selection": selection,
        }
    elif lock_file is not None:
        raise ValueError("--lock-file is accepted only by a locked confirmatory profile")
    resolved["run"] = {
        "device": device_name,
        "resume": bool(resume),
        "dry_run": bool(dry_run),
        "seed_override": seed,
        "seeds": run_seeds,
        "confirmatory_seeds": sorted(confirmatory_seeds),
        "minimum_confirmatory": required_confirmatory,
        "analysis_lock_sha256": resolved.get("analysis_lock", {}).get("sha256"),
    }
    resolved["profile_configuration_sha256"] = _sha256_file(selected_profile_path)
    manifest = PACKAGE_ROOT / "PACKAGE_MANIFEST.sha256"
    if manifest.is_file():
        resolved["package_manifest_sha256"] = _sha256_file(manifest)

    output_path = Path(output).resolve()
    try:
        output_path.relative_to(PACKAGE_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError("run output must be outside the immutable package directory")
    _prepare_run(output_path, resolved)
    _progress(output_path, "run_started", profile=profile, seeds=run_seeds, dry_run=dry_run)

    if dry_run:
        runtime = {"device": device_name, "dry_run": True, "components_loaded": False}
        _atomic_json(runtime, output_path / "runtime.json")
        summary = _dry_summary(resolved, output_path, run_seeds, required_confirmatory)
        _atomic_json(summary, output_path / "experiment_summary.json")
        _progress(output_path, "run_finished", status="DRY_RUN")
        return summary

    components = components or _load_components()
    device = components.resolve_device(device_name)
    runtime = components.runtime_information(device)
    _atomic_json(runtime, output_path / "runtime.json")
    print(
        f"WORKSPACE_DEVICE={runtime.get('device', device)} TORCH={runtime.get('torch', 'unknown')} "
        f"GPU={runtime.get('gpu', 'none')}",
        flush=True,
    )

    started = time.perf_counter()
    seed_results: dict[str, dict[str, Any]] = {}
    arms = _enabled_arms(resolved)
    max_steps = int(resolved["training"]["max_steps"])
    for active_seed in run_seeds:
        seed_text = str(active_seed)
        _progress(output_path, "seed_started", seed=active_seed)
        provider_config = dict(resolved["data"])
        arm_by_name = {str(arm["name"]): arm for arm in arms}
        pseudo_arm = arm_by_name["pseudo_fst"]
        deranged_arm = arm_by_name["deranged"]
        provider_config.setdefault(
            "pseudo_states", int(pseudo_arm.get("states", 4))
        )
        provider_config.setdefault(
            "pseudo_seed",
            active_seed + int(pseudo_arm.get("transition_seed_offset", 41000)),
        )
        reject = deranged_arm.get("reject", {})
        if isinstance(reject, Mapping):
            provider_config.setdefault(
                "derangement_max_abs_pearson", reject.get("max_abs_pearson")
            )
            provider_config.setdefault(
                "derangement_max_prefix_excess", reject.get("max_prefix_match_rate")
            )
            provider_config.setdefault(
                "derangement_max_suffix_excess", reject.get("max_suffix_match_rate")
            )
        provider = components.provider_factory(provider_config, seed=active_seed)
        control_audits: dict[str, Any] = {}
        for arm in arms:
            name = str(arm["name"])
            if hasattr(provider, "audit_control"):
                audit_count = int(resolved["data"].get("control_audit_examples", 4096))
                print(
                    f"CONTROL_AUDIT_START SEED={active_seed} ARM={name} "
                    f"REQUESTED_ROWS={audit_count}",
                    flush=True,
                )
                control_audits[name] = provider.audit_control(name, "train", audit_count)
                audit_status = control_audits[name].get("status") if isinstance(control_audits[name], Mapping) else None
                audit_valid = control_audits[name].get("valid") if isinstance(control_audits[name], Mapping) else None
                if name == "deranged" and audit_status not in ("PASS", True) and audit_valid is not True:
                    raise RuntimeError("the randomized derangement control failed its audit")
                print(
                    f"CONTROL_AUDIT SEED={active_seed} ARM={name} "
                    f"STATUS={'PASS' if audit_status in ('PASS', True) or audit_valid is True else 'RECORDED'}",
                    flush=True,
                )
        audit_path = output_path / "behavior" / f"seed_{active_seed}" / "control_audits.json"
        _atomic_json(control_audits, audit_path)

        training: dict[str, dict[str, Any]] = {}
        for arm in arms:
            name = str(arm["name"])
            arm_output = output_path / "training" / f"seed_{active_seed}" / name
            _progress(output_path, "training_arm_started", seed=active_seed, arm=name)
            summary = _supported_call(
                components.train_arm,
                config=resolved,
                arm=name,
                seed=active_seed,
                output_dir=arm_output,
                output=arm_output,
                device=device,
                resume=resume,
                data_provider=provider,
                provider=provider,
            )
            if not isinstance(summary, Mapping):
                raise TypeError("workspace_trainer.train_arm must return an object")
            training[name] = dict(summary)
            _progress(
                output_path,
                "training_arm_finished",
                seed=active_seed,
                arm=name,
                optimizer_steps=summary.get("optimizer_steps", max_steps),
            )
        initial_hashes = {
            value.get("initial_model_hash") for value in training.values()
        }
        if None in initial_hashes or len(initial_hashes) != 1:
            raise RuntimeError("all arms must begin from one identical model initialization")
        if any(
            value.get("final_model_hash") == value.get("initial_model_hash")
            for value in training.values()
        ):
            raise RuntimeError("at least one enabled arm did not change its model weights")
        if any(int(value.get("optimizer_steps", -1)) != max_steps for value in training.values()):
            raise RuntimeError("every enabled arm must complete the same optimizer-step schedule")
        label_paired = ("correct", "pseudo_fst", "deranged")
        stream_hashes = {
            training[name].get("input_stream_probe_hash") for name in label_paired
        }
        if None in stream_hashes or len(stream_hashes) != 1:
            raise RuntimeError(
                "correct, pseudo_fst, and deranged did not consume the same "
                "audited input expression order"
            )
        _atomic_json(
            {
                "status": "PASS",
                "seed": active_seed,
                "paired_initialization": True,
                "paired_input_stream": True,
                "initial_model_hash": next(iter(initial_hashes)),
                "input_stream_probe_hash": next(iter(stream_hashes)),
                "arms": training,
            },
            output_path / "training" / f"seed_{active_seed}" / "training_summary.json",
        )

        behavior: dict[str, dict[str, Any]] = {}
        models: dict[str, Any] = {}
        for arm in arms:
            name = str(arm["name"])
            arm_output = output_path / "training" / f"seed_{active_seed}" / name
            checkpoint = _final_checkpoint(training[name], arm_output, max_steps)
            if not checkpoint.is_file():
                raise FileNotFoundError(f"final research checkpoint is missing: {checkpoint}")
            model, payload = _load_model(components, checkpoint, device)
            models[name] = model
            report_path = output_path / "behavior" / f"seed_{active_seed}" / f"{name}.json"
            behavior[name] = _evaluate_arm_behavior(
                components=components,
                resolved=resolved,
                provider=provider,
                arm=name,
                model=model,
                seed=active_seed,
                device=device,
                output=report_path,
            )
            behavior[name]["checkpoint"] = str(checkpoint)
            behavior[name]["checkpoint_step"] = int(
                payload.get("step", training[name].get("optimizer_steps", max_steps))
            )
            _atomic_json(behavior[name], report_path)

        _refresh_claim_competence(
            components=components,
            resolved=resolved,
            behavior=behavior,
        )
        behavior["no_carry"]["task_competence"] = _no_transfer_competence(
            behavior["no_carry"], resolved["competence_gates"]
        )
        for panel_name in behavior["correct"]["panels"]:
            paired_fingerprints = {
                behavior[name]["panels"][panel_name]["input_expression_fingerprint"]
                for name in ("correct", "pseudo_fst", "deranged")
            }
            if len(paired_fingerprints) != 1:
                raise RuntimeError(
                    f"paired behavior inputs differ for panel {panel_name}"
                )
        _atomic_json(
            behavior["correct"],
            output_path / "behavior" / f"seed_{active_seed}" / "correct.json",
        )
        _atomic_json(
            behavior["no_carry"],
            output_path / "behavior" / f"seed_{active_seed}" / "no_carry.json",
        )

        competence_pass = _gate_pass(behavior["correct"]["competence"])
        geometry_reports: dict[str, dict[str, Any]] = {}
        causal_reports: dict[str, dict[str, Any]] = {}
        spaces: dict[str, Any] = {}
        for probe_arm in ("correct", "no_carry", "pseudo_fst"):
            arm_competent = _gate_pass(
                behavior[probe_arm].get(
                    "task_competence", behavior[probe_arm]["competence"]
                )
            )
            print(
                f"COMPETENCE_GATE SEED={active_seed} ARM={probe_arm} "
                f"STATUS={'PASS' if arm_competent else 'NOT_REACHED'}",
                flush=True,
            )
            if not arm_competent:
                skipped = {
                    "status": "SKIPPED_COMPETENCE_GATE",
                    "seed": active_seed,
                    "arm": probe_arm,
                    "reason": "balanced discovery is forbidden before task competence",
                }
                _atomic_json(
                    skipped,
                    output_path
                    / "geometry"
                    / f"seed_{active_seed}"
                    / f"{probe_arm}_skipped.json",
                )
                continue
            space, geometry_report = _run_geometry(
                components=components,
                resolved=resolved,
                provider=provider,
                model=models[probe_arm],
                seed=active_seed,
                arm=probe_arm,
                device=device,
                output=output_path
                / "geometry"
                / f"seed_{active_seed}"
                / f"{probe_arm}_balanced_space",
            )
            spaces[probe_arm] = space
            geometry_reports[probe_arm] = geometry_report
            representation_pass = _representation_pass(
                geometry_report, _claim_policy(resolved)
            )
            print(
                f"REPRESENTATION_GATE SEED={active_seed} ARM={probe_arm} "
                f"STATUS={'PASS' if representation_pass else 'NOT_REACHED'}",
                flush=True,
            )
            if representation_pass and probe_arm in {"correct", "pseudo_fst"}:
                causal_reports[probe_arm] = _run_causal(
                    components=components,
                    resolved=resolved,
                    provider=provider,
                    model=models[probe_arm],
                    space=space,
                    seed=active_seed,
                    arm=probe_arm,
                    device=device,
                    output=output_path
                    / "causal"
                    / f"seed_{active_seed}"
                    / f"{probe_arm}_assay.json",
                )

        cross_arm_geometry = _cross_arm_geometry(spaces, geometry_reports)
        _atomic_json(
            cross_arm_geometry,
            output_path / "geometry" / f"seed_{active_seed}" / "cross_arm.json",
        )
        specificity = _math_specificity_report(
            behavior,
            causal_reports,
            _claim_policy(resolved),
        )
        _atomic_json(
            specificity,
            output_path / "causal" / f"seed_{active_seed}" / "math_specificity.json",
        )
        if "correct" in causal_reports:
            causal_reports["correct"]["math_specificity"] = specificity
            causal_reports["correct"]["math_specificity_pass"] = bool(
                specificity.get("pass", False)
            )
            _atomic_json(
                causal_reports["correct"],
                output_path
                / "causal"
                / f"seed_{active_seed}"
                / "correct_assay.json",
            )

        seed_results[seed_text] = {
            "status": "PASS",
            "seed": active_seed,
            "control_audits": control_audits,
            "training": training,
            "paired_initialization": True,
            "behavior": behavior,
            "geometry": geometry_reports,
            "cross_arm_geometry": cross_arm_geometry,
            "causal": causal_reports,
            "math_specificity": specificity,
        }
        _progress(
            output_path,
            "seed_finished",
            seed=active_seed,
            competence_pass=competence_pass,
            geometry_run=bool(geometry_reports),
            causal_run=bool(causal_reports),
        )
        models.clear()
        if getattr(device, "type", str(device)) == "cuda":
            try:
                import torch

                torch.cuda.empty_cache()
            except ImportError:
                pass

    policy = _claim_policy(resolved)
    statistics_config = resolved.get("statistics", {})
    if not isinstance(statistics_config, Mapping):
        raise ValueError("statistics must be an object when present")
    confirmation_statistics = _confirmation_statistics(
        seed_results,
        confirmatory_seeds,
        statistics_config,
        resolved["causal"],
    )
    _atomic_json(
        confirmation_statistics,
        output_path / "causal" / "confirmation_statistics.json",
    )
    claim = _build_claim_summary(
        seed_results, confirmatory_seeds, required_confirmatory, policy
    )
    claim["registered_confirmation_statistics_pass"] = bool(
        confirmation_statistics.get("passed", False)
    )
    claim["unimplemented_required_assays"] = list(
        resolved["claim_policy"].get("unimplemented_required_assays", [])
    )
    discovery_lock = None
    lock_telemetry = {
        "written": False,
        "path": str(output_path / "workspace_lock.json"),
        "reason": "not_a_discovery_profile",
    }
    if study_phase in {"exploratory", "discovery"}:
        discovery_lock = _write_discovery_lock(
            output=output_path,
            resolved=resolved,
            seed_results=seed_results,
            telemetry=lock_telemetry,
        )
    summary = {
        "status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "experiment": resolved["experiment"],
        "profile": profile,
        "device": str(device),
        "seeds": run_seeds,
        "seed_results": seed_results,
        "claim": claim,
        "confirmation_statistics": confirmation_statistics,
        "workspace_lock_written": discovery_lock is not None,
        "workspace_lock_path": (
            str(output_path / "workspace_lock.json") if discovery_lock else None
        ),
        "workspace_lock_reason": lock_telemetry["reason"],
        "JSPACE_CLAIM": claim["status"],
        "unimplemented_required_assays": claim[
            "unimplemented_required_assays"
        ],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "result_path": str(output_path),
    }
    _atomic_json(summary, output_path / "experiment_summary.json")
    _progress(output_path, "run_finished", status="PASS", claim=claim["status"])
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Train arithmetic controls and test a balanced causal workspace candidate."
    )
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--device", choices=["cuda", "cpu", "auto"], default="cuda")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lock-file")
    args = parser.parse_args(argv)
    try:
        result = run_workspace_experiment(
            profile=args.profile,
            output=args.output,
            seed=args.seed,
            device_name=args.device,
            resume=not args.no_resume,
            dry_run=args.dry_run,
            lock_file=args.lock_file,
        )
        print("ARITHMETIC_WORKSPACE_PIPELINE=PASS", flush=True)
        print(f"JSPACE_CLAIM={result['JSPACE_CLAIM']}", flush=True)
        if result.get("profile") == "carry_discovery":
            print(
                "WORKSPACE_LOCK_WRITTEN="
                f"{bool(result.get('workspace_lock_written', False))}",
                flush=True,
            )
            print(
                f"WORKSPACE_LOCK_PATH={result.get('workspace_lock_path') or ''}",
                flush=True,
            )
            print(
                f"WORKSPACE_LOCK_REASON={result.get('workspace_lock_reason', '')}",
                flush=True,
            )
        print(f"RESULT_PATH={result['result_path']}", flush=True)
        return 0
    except (FileNotFoundError, ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"ARITHMETIC_WORKSPACE_PIPELINE=FAIL: {error}", file=os.sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
