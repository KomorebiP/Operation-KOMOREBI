from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapters.fake import FakeProcedureLatentAdapter
from .adapters.multimode_coconut import (
    MultimodeCoconutProntoQAAdapter,
    fingerprint_real_inputs,
)
from .dataset import (
    dataset_fingerprint,
    deterministic_calibration_audit_split,
    deterministic_group_split,
    deterministic_subset,
    load_prontoqa_json,
)
from .donors import (
    build_different_answer_far_proof_plan,
    build_same_answer_far_proof_plan,
    donor_plan_digest,
)
from .fixture import write_fixture
from .hashing import sha256_object
from .pipeline import run_block24_pipeline
from .cache import CachedCaptureAdapter
from .receipts import load_and_verify_result, write_json
from .schemas import AuditConfig
from .sealing import build_protocol_seal, load_and_verify_seal, verify_seal, write_seal
from .source_lock import load_source_lock, verify_external_repository


SOURCE_LOCK_PATH = Path(__file__).resolve().parents[1] / "external_source_lock.json"
SOURCE_LOCK = load_source_lock(SOURCE_LOCK_PATH)
EXTERNAL_REPOSITORY = SOURCE_LOCK["external_repository"]
PRIMARY_CHECKPOINT = SOURCE_LOCK["checkpoints"]["prontoqa_primary"]
BASE_MODEL_LOCK = SOURCE_LOCK["base_model"]



def _load_config(path: str) -> AuditConfig:
    return AuditConfig.load(path)



def _causal_partitions(records: list[Any], config: AuditConfig) -> dict[str, list[Any]]:
    if not config.run_covariance_noise:
        return {"calibration": [], "audit": list(records)}
    return deterministic_calibration_audit_split(
        records,
        seed=config.seed,
        calibration_fraction=config.causal_calibration_fraction,
    )

def _experiment_plan(records: list[Any], config: AuditConfig) -> dict[str, Any]:
    causal = _causal_partitions(records, config)
    audit_records = causal["audit"]
    splits = deterministic_group_split(
        audit_records,
        seed=config.seed,
        discovery_fraction=config.semantic_discovery_fraction,
        calibration_fraction=config.semantic_calibration_fraction,
    ) if config.semantic_escalation and len({r.group_id for r in audit_records}) >= 3 else {}
    return {
        "task_ids_digest": sha256_object([record.task_id for record in records]),
        "causal_calibration_task_ids_digest": sha256_object([record.task_id for record in causal["calibration"]]),
        "causal_audit_task_ids_digest": sha256_object([record.task_id for record in audit_records]),
        "semantic_split_digest": sha256_object(
            {name: [record.task_id for record in split] for name, split in splits.items()}
        ) if splits else None,
        "causal_interventions": [
            "exact_replay",
            "zero_trace",
            "step_derangement",
            "norm_matched_noise",
            "covariance_matched_noise",
            "same_answer_far_proof_transplant_content_test",
            "different_answer_far_proof_transplant",
            "premise_order_semantic_twin",
            "truncation_curve",
        ],
        "semantic_construction_inputs": [
            "latent_trajectory",
            "future_latent_state",
            "anonymous_query_polarity_response",
            "final_answer",
            "semantic_twin_relation",
        ],
        "post_seal_witnesses": [
            "formal_proof_instance_witness_post_seal",
            "counterfactual_subspace_patching",
        ],
        "gold_proof_witness_excluded_from_construction": True,
        "explicit_cot_excluded_from_construction": True,
        "prontoqa_algorithmic_procedure_claim": False,
    }


def command_make_fixture(args: argparse.Namespace) -> None:
    write_fixture(args.output, args.count)
    print(f"WROTE_FIXTURE={Path(args.output).resolve()}")


def _fake_seal_components(config: AuditConfig, records: list[Any], hidden_size: int) -> dict[str, Any]:
    causal = _causal_partitions(records, config)
    audit_records = causal["audit"]
    same_plan = build_same_answer_far_proof_plan(audit_records)
    different_plan = build_different_answer_far_proof_plan(audit_records)
    adapter = FakeProcedureLatentAdapter(
        num_latents=config.num_latents, hidden_size=hidden_size, seed=config.seed
    )
    return {
        "causal": causal,
        "same_plan": same_plan,
        "different_plan": different_plan,
        "model_fingerprint": dict(adapter.model_fingerprint()),
        "dataset_fingerprint": dataset_fingerprint("data/engineered_fixture.json", records),
        "experiment_plan": _experiment_plan(records, config),
    }


def command_stage_fake(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    components = _fake_seal_components(config, records, args.hidden_size)
    # Use the actual provided data path for the frozen fingerprint.
    data_fp = dataset_fingerprint(args.data, records)
    seal = build_protocol_seal(
        config,
        external_repository={"name": "engineered-fixture", "commit": "not-applicable"},
        model_fingerprint=components["model_fingerprint"],
        dataset_fingerprint=data_fp,
        donor_plan_digest={
            "same_answer_far_proof": donor_plan_digest(components["same_plan"]),
            "different_answer_far_proof": donor_plan_digest(components["different_plan"]),
        },
        experiment_plan=components["experiment_plan"],
        output_contract={
            "result_schema": "sric.block24.external-lrm-causal-semantic-admission-result.v1",
            "maximum_claim": "CAUSALLY_VALIDATED_ENGINEERED_FIXTURE_ONLY",
            "real_model_claim": False,
            "specificity_claim": config.specificity_claim,
            "causal_calibration_rows": len(components["causal"]["calibration"]),
            "audit_rows": len(components["causal"]["audit"]),
        },
    )
    write_seal(args.output, seal)
    print(f"FAKE_PREAUDIT_SEAL={seal['seal_sha256']}")
    print(f"SEAL_PATH={Path(args.output).resolve()}")


def command_run_fake(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    adapter = FakeProcedureLatentAdapter(
        num_latents=config.num_latents,
        hidden_size=args.hidden_size,
        seed=config.seed,
    )
    seal = load_and_verify_seal(args.seal) if args.seal else None
    if seal is not None:
        components = _fake_seal_components(config, records, args.hidden_size)
        comparisons = {
            "config": config.to_mapping(),
            "model_fingerprint": components["model_fingerprint"],
            "dataset_fingerprint": dataset_fingerprint(args.data, records),
            "donor_plan_digest": {
                "same_answer_far_proof": donor_plan_digest(components["same_plan"]),
                "different_answer_far_proof": donor_plan_digest(components["different_plan"]),
            },
            "experiment_plan": components["experiment_plan"],
        }
        for key, value in comparisons.items():
            if seal.get(key) != value:
                raise ValueError(f"Fake fixture {key} does not match the sealed value")
    result = run_block24_pipeline(adapter, records, config)
    if seal is not None:
        result["preaudit_seal_sha256"] = seal["seal_sha256"]
    result["execution_boundary"] = {
        "real_checkpoint_used": False,
        "engineered_positive_control": True,
        "external_model_claim": False,
    }
    result["result_sha256"] = sha256_object({k: v for k, v in result.items() if k != "result_sha256"})
    output = Path(args.output)
    write_json(output, result)
    print(f"FAKE_STATUS={result['overall_status']}")
    print(f"RESULT_SHA256={result['result_sha256']}")
    print(f"RESULT_PATH={output.resolve()}")


def command_stage_real(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    causal = _causal_partitions(records, config)
    audit_records = causal["audit"]
    same_plan = build_same_answer_far_proof_plan(audit_records)
    different_plan = build_different_answer_far_proof_plan(audit_records)
    source_verification = verify_external_repository(
        args.external_repo, SOURCE_LOCK, dataset_key="prontoqa_test"
    )
    model_fingerprint = fingerprint_real_inputs(
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
        num_latents=config.num_latents,
        checkpoint_revision=args.checkpoint_revision,
        base_model_revision=args.base_model_revision,
        source_lock_path=SOURCE_LOCK_PATH,
    )
    data_fingerprint = dataset_fingerprint(args.data, records)
    donor_digests = {
        "same_answer_far_proof": donor_plan_digest(same_plan),
        "different_answer_far_proof": donor_plan_digest(different_plan),
    }
    plan = _experiment_plan(records, config)
    seal = build_protocol_seal(
        config,
        external_repository={**EXTERNAL_REPOSITORY, "verification": source_verification},
        model_fingerprint=model_fingerprint,
        dataset_fingerprint=data_fingerprint,
        donor_plan_digest=donor_digests,
        experiment_plan=plan,
        output_contract={
            "result_schema": "sric.block24.external-lrm-causal-semantic-admission-result.v1",
            "maximum_claim": "CAUSALLY_VALIDATED",
            "semantic_escalation_requires_specificity": config.specificity_claim,
            "gold_proof_steps_withheld_until_quotient_seal": True,
            "causal_calibration_rows": len(causal["calibration"]),
            "audit_rows": len(audit_records),
        },
    )
    write_seal(args.output, seal)
    parent = Path(args.output).parent
    (parent / "same_answer_donor_plan.json").write_text(
        json.dumps([item.to_mapping() for item in same_plan], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (parent / "different_answer_donor_plan.json").write_text(
        json.dumps([item.to_mapping() for item in different_plan], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (parent / "experiment_plan.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"PREAUDIT_SEAL={seal['seal_sha256']}")
    print(f"SEAL_PATH={Path(args.output).resolve()}")


def _assert_seal_matches(
    *,
    seal: dict[str, Any],
    config: AuditConfig,
    data: str,
    records: list[Any],
    external_repo: str,
    checkpoint: str,
    base_model: str,
    checkpoint_revision: str,
    base_model_revision: str,
) -> None:
    causal = _causal_partitions(records, config)
    audit_records = causal["audit"]
    same_plan = build_same_answer_far_proof_plan(audit_records)
    different_plan = build_different_answer_far_proof_plan(audit_records)
    current_model = fingerprint_real_inputs(
        external_repo=external_repo,
        checkpoint=checkpoint,
        base_model=base_model,
        num_latents=config.num_latents,
        checkpoint_revision=checkpoint_revision,
        base_model_revision=base_model_revision,
        source_lock_path=SOURCE_LOCK_PATH,
    )
    current_data = dataset_fingerprint(data, records)
    comparisons = {
        "config": config.to_mapping(),
        "model_fingerprint": current_model,
        "dataset_fingerprint": current_data,
        "donor_plan_digest": {
            "same_answer_far_proof": donor_plan_digest(same_plan),
            "different_answer_far_proof": donor_plan_digest(different_plan),
        },
        "experiment_plan": _experiment_plan(records, config),
    }
    for key, value in comparisons.items():
        if seal.get(key) != value:
            raise ValueError(f"Current {key} does not match the sealed value")


def command_run_real(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    seal = load_and_verify_seal(args.seal)
    _assert_seal_matches(
        seal=seal,
        config=config,
        data=args.data,
        records=records,
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
        checkpoint_revision=args.checkpoint_revision,
        base_model_revision=args.base_model_revision,
    )
    base_adapter = MultimodeCoconutProntoQAAdapter(
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
        device=args.device,
        num_latents=config.num_latents,
        checkpoint_revision=args.checkpoint_revision,
        base_model_revision=args.base_model_revision,
        source_lock_path=SOURCE_LOCK_PATH,
    )
    adapter = (
        CachedCaptureAdapter(base_adapter, Path(args.output).parent / "capture_cache")
        if config.cache_captures
        else base_adapter
    )
    try:
        result = run_block24_pipeline(adapter, records, config)
    finally:
        adapter.close()
    result["preaudit_seal_sha256"] = seal["seal_sha256"]
    result["execution_boundary"] = {
        "real_checkpoint_used": True,
        "external_model_retrained": False,
        "maximum_claim": "CAUSALLY_VALIDATED",
    }
    result["result_sha256"] = sha256_object({k: v for k, v in result.items() if k != "result_sha256"})
    output = Path(args.output)
    write_json(output, result)
    print(f"REAL_STATUS={result['overall_status']}")
    print(f"RESULT_SHA256={result['result_sha256']}")
    print(f"RESULT_PATH={output.resolve()}")


def command_preflight(args: argparse.Namespace) -> None:
    checks: dict[str, Any] = {}
    try:
        import torch
        checks["torch"] = torch.__version__
        checks["cuda_available"] = bool(torch.cuda.is_available())
    except Exception as exc:
        checks["torch_error"] = str(exc)
    try:
        import transformers
        checks["transformers"] = transformers.__version__
    except Exception as exc:
        checks["transformers_error"] = str(exc)
    for name, path in {
        "external_repo": args.external_repo,
        "checkpoint": args.checkpoint,
        "data": args.data,
    }.items():
        checks[f"{name}_exists"] = bool(path and Path(path).exists())
    ready = (
        checks.get("external_repo_exists")
        and checks.get("checkpoint_exists")
        and checks.get("data_exists")
        and "torch" in checks
        and "transformers" in checks
    )
    checks["ready"] = bool(ready)
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not ready:
        raise SystemExit(2)


def command_verify_source(args: argparse.Namespace) -> None:
    receipt = verify_external_repository(args.external_repo, SOURCE_LOCK, dataset_key=args.dataset_key)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def command_verify_result(args: argparse.Namespace) -> None:
    result = load_and_verify_result(args.result)
    print(f"RESULT_VALID={result['result_sha256']}")
    print(f"STATUS={result.get('overall_status', result.get('summary', {}).get('status'))}")


def command_verify_seal(args: argparse.Namespace) -> None:
    seal = json.loads(Path(args.seal).read_text(encoding="utf-8"))
    verify_seal(seal)
    print(f"SEAL_VALID={seal['seal_sha256']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SRIC Block 24 / Real-LRM Pilot 0.3.2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fixture = subparsers.add_parser("make-fixture", help="Generate the engineered causal-semantic fixture")
    fixture.add_argument("--output", default="data/engineered_fixture.json")
    fixture.add_argument("--count", type=int, default=48)
    fixture.set_defaults(func=command_make_fixture)


    stage_fake = subparsers.add_parser("stage-fake", help="Freeze the engineered fixture before running it")
    stage_fake.add_argument("--config", default="configs/fake_fixture.json")
    stage_fake.add_argument("--data", default="data/engineered_fixture.json")
    stage_fake.add_argument("--output", default="frozen/fake_fixture_preaudit_seal.json")
    stage_fake.add_argument("--hidden-size", type=int, default=32)
    stage_fake.set_defaults(func=command_stage_fake)

    fake = subparsers.add_parser("run-fake", help="Run causal admission and semantic escalation on the fixture")
    fake.add_argument("--config", default="configs/fake_fixture.json")
    fake.add_argument("--data", default="data/engineered_fixture.json")
    fake.add_argument("--output", default="results/fake_fixture_block24.json")
    fake.add_argument("--hidden-size", type=int, default=32)
    fake.add_argument("--seal", default="frozen/fake_fixture_preaudit_seal.json")
    fake.set_defaults(func=command_run_fake)

    preflight = subparsers.add_parser("preflight", help="Fail-closed external runtime check")
    preflight.add_argument("--external-repo", default="")
    preflight.add_argument("--checkpoint", default="")
    preflight.add_argument("--data", default="")
    preflight.set_defaults(func=command_preflight)

    stage = subparsers.add_parser("stage-real", help="Freeze model, data, donors, semantic splits, and gates")
    stage.add_argument("--config", default="configs/prontoqa_multimode_coconut_gpt2.json")
    stage.add_argument("--data", required=True)
    stage.add_argument("--external-repo", required=True)
    stage.add_argument("--checkpoint", required=True)
    stage.add_argument("--base-model", default="openai-community/gpt2")
    stage.add_argument("--checkpoint-revision", default=PRIMARY_CHECKPOINT["revision"])
    stage.add_argument("--base-model-revision", default=BASE_MODEL_LOCK["revision"])
    stage.add_argument("--output", default="frozen/real_preaudit_seal.json")
    stage.set_defaults(func=command_stage_real)

    real = subparsers.add_parser("run-real", help="Run the sealed third-party checkpoint audit")
    real.add_argument("--config", default="configs/prontoqa_multimode_coconut_gpt2.json")
    real.add_argument("--data", required=True)
    real.add_argument("--external-repo", required=True)
    real.add_argument("--checkpoint", required=True)
    real.add_argument("--base-model", default="openai-community/gpt2")
    real.add_argument("--checkpoint-revision", default=PRIMARY_CHECKPOINT["revision"])
    real.add_argument("--base-model-revision", default=BASE_MODEL_LOCK["revision"])
    real.add_argument("--seal", default="frozen/real_preaudit_seal.json")
    real.add_argument("--device", default="cuda")
    real.add_argument("--output", default="results/real_checkpoint_block24.json")
    real.set_defaults(func=command_run_real)


    source = subparsers.add_parser("verify-source", help="Verify the pinned external commit and Git blobs")
    source.add_argument("--external-repo", required=True)
    source.add_argument("--dataset-key", default="prontoqa_test", choices=["prontoqa_test", "prosqa_test"])
    source.set_defaults(func=command_verify_source)

    verify_result = subparsers.add_parser("verify-result")
    verify_result.add_argument("result")
    verify_result.set_defaults(func=command_verify_result)

    verify_seal_parser = subparsers.add_parser("verify-seal")
    verify_seal_parser.add_argument("seal")
    verify_seal_parser.set_defaults(func=command_verify_seal)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
