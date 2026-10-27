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
from .audit import run_causal_audit
from .dataset import dataset_fingerprint, deterministic_subset, load_prontoqa_json
from .donors import build_same_answer_far_proof_plan, donor_plan_digest
from .fixture import write_fixture
from .hashing import sha256_file, sha256_object
from .receipts import load_and_verify_result, write_json
from .schemas import AuditConfig
from .sealing import build_protocol_seal, load_and_verify_seal, verify_seal, write_seal


EXTERNAL_REPOSITORY = {
    "name": "connordilgren/are-lrms-easily-interpretable",
    "commit": "32f413d8d55239d9bc54bb6b6ec37b0630891ed4",
    "model_wrapper": "models/multimode_coconut/multimode_coconut_model.py",
    "latent_runtime": "src_coconut_multimode/coconut.py",
    "dataset": "data/prontoqa_test.json",
}


def _load_config(path: str) -> AuditConfig:
    return AuditConfig.load(path)


def command_make_fixture(args: argparse.Namespace) -> None:
    write_fixture(args.output, args.count)
    print(f"WROTE_FIXTURE={Path(args.output).resolve()}")


def command_run_fake(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    adapter = FakeProcedureLatentAdapter(num_latents=config.num_latents, hidden_size=args.hidden_size, seed=config.seed)
    result = run_causal_audit(adapter, records, config)
    result["execution_boundary"] = {
        "real_checkpoint_used": False,
        "engineered_positive_control": True,
    }
    result["result_sha256"] = sha256_object({k: v for k, v in result.items() if k != "result_sha256"})
    output = Path(args.output)
    write_json(output, result)
    print(f"FAKE_STATUS={result['summary']['status']}")
    print(f"RESULT_SHA256={result['result_sha256']}")
    print(f"RESULT_PATH={output.resolve()}")


def command_stage_real(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    donor_plan = build_same_answer_far_proof_plan(records)
    model_fingerprint = fingerprint_real_inputs(
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
        num_latents=config.num_latents,
    )
    data_fingerprint = dataset_fingerprint(args.data, records)
    seal = build_protocol_seal(
        config,
        external_repository=EXTERNAL_REPOSITORY,
        model_fingerprint=model_fingerprint,
        dataset_fingerprint=data_fingerprint,
        donor_plan_digest=donor_plan_digest(donor_plan),
        output_contract={
            "result_schema": "sric.real-lrm.causal-audit-result.v1",
            "maximum_claim": "PROCEDURE_SPECIFIC",
            "gold_proof_steps_withheld_during_primary_causal_audit": True,
            "audit_rows": len(records),
        },
    )
    write_seal(args.output, seal)
    donor_output = Path(args.output).with_name("donor_plan.json")
    donor_output.write_text(
        json.dumps([item.to_mapping() for item in donor_plan], indent=2, sort_keys=True) + "\n",
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
) -> list[Any]:
    plan = build_same_answer_far_proof_plan(records)
    current_model = fingerprint_real_inputs(
        external_repo=external_repo,
        checkpoint=checkpoint,
        base_model=base_model,
        num_latents=config.num_latents,
    )
    current_data = dataset_fingerprint(data, records)
    comparisons = {
        "config": config.to_mapping(),
        "model_fingerprint": current_model,
        "dataset_fingerprint": current_data,
        "donor_plan_digest": donor_plan_digest(plan),
    }
    for key, value in comparisons.items():
        if seal.get(key) != value:
            raise ValueError(f"Current {key} does not match the sealed value")
    return plan


def command_run_real(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    records = deterministic_subset(load_prontoqa_json(args.data), config.max_tasks, config.seed)
    seal = load_and_verify_seal(args.seal)
    plan = _assert_seal_matches(
        seal=seal,
        config=config,
        data=args.data,
        records=records,
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
    )
    adapter = MultimodeCoconutProntoQAAdapter(
        external_repo=args.external_repo,
        checkpoint=args.checkpoint,
        base_model=args.base_model,
        device=args.device,
        num_latents=config.num_latents,
    )
    try:
        result = run_causal_audit(adapter, records, config, plan)
    finally:
        adapter.close()
    result["preaudit_seal_sha256"] = seal["seal_sha256"]
    result["execution_boundary"] = {
        "real_checkpoint_used": True,
        "external_model_retrained": False,
        "maximum_claim": "PROCEDURE_SPECIFIC",
    }
    result["result_sha256"] = sha256_object({k: v for k, v in result.items() if k != "result_sha256"})
    output = Path(args.output)
    write_json(output, result)
    print(f"REAL_STATUS={result['summary']['status']}")
    print(f"RESULT_SHA256={result['result_sha256']}")
    print(f"RESULT_PATH={output.resolve()}")


def command_verify_result(args: argparse.Namespace) -> None:
    result = load_and_verify_result(args.result)
    print(f"RESULT_VALID={result['result_sha256']}")
    print(f"STATUS={result['summary']['status']}")


def command_verify_seal(args: argparse.Namespace) -> None:
    seal = json.loads(Path(args.seal).read_text(encoding="utf-8"))
    verify_seal(seal)
    print(f"SEAL_VALID={seal['seal_sha256']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SRIC Real-LRM Pilot 0.1")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fixture = subparsers.add_parser("make-fixture", help="Generate the engineered adapter fixture")
    fixture.add_argument("--output", default="data/engineered_fixture.json")
    fixture.add_argument("--count", type=int, default=48)
    fixture.set_defaults(func=command_make_fixture)

    fake = subparsers.add_parser("run-fake", help="Run the complete audit against the engineered adapter")
    fake.add_argument("--config", default="configs/fake_fixture.json")
    fake.add_argument("--data", default="data/engineered_fixture.json")
    fake.add_argument("--output", default="results/fake_fixture_audit.json")
    fake.add_argument("--hidden-size", type=int, default=32)
    fake.set_defaults(func=command_run_fake)

    stage = subparsers.add_parser("stage-real", help="Freeze model, data, donors, thresholds, and output contract")
    stage.add_argument("--config", default="configs/prontoqa_multimode_coconut_gpt2.json")
    stage.add_argument("--data", required=True)
    stage.add_argument("--external-repo", required=True)
    stage.add_argument("--checkpoint", required=True)
    stage.add_argument("--base-model", default="openai-community/gpt2")
    stage.add_argument("--output", default="frozen/real_preaudit_seal.json")
    stage.set_defaults(func=command_stage_real)

    real = subparsers.add_parser("run-real", help="Run a sealed real-checkpoint audit")
    real.add_argument("--config", default="configs/prontoqa_multimode_coconut_gpt2.json")
    real.add_argument("--data", required=True)
    real.add_argument("--external-repo", required=True)
    real.add_argument("--checkpoint", required=True)
    real.add_argument("--base-model", default="openai-community/gpt2")
    real.add_argument("--seal", default="frozen/real_preaudit_seal.json")
    real.add_argument("--device", default="cuda")
    real.add_argument("--output", default="results/real_checkpoint_audit.json")
    real.set_defaults(func=command_run_real)

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
