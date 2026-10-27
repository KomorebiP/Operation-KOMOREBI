from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

try:
    import torch
except ImportError:  # Pure-data package tests remain usable before torch install.
    torch = None  # type: ignore[assignment]

if torch is not None:
    from arithmetic_space_lab.byte_tokenizer import ByteTokenizer
    from arithmetic_space_lab.tiny_model import ModelConfig, TinyDecoderLM
    from arithmetic_space_lab.workspace_trainer import (
        RESUME_SCHEMA,
        WorkspaceTrainSettings,
        _atomic_torch_save,
        _data_stage,
        _load_latest_resume,
        _load_resume_candidate,
        _model_state_hash,
        competence_report,
        evaluate_free_generation,
        learning_rate_at_step,
        load_research_checkpoint,
        train_arm,
    )


@dataclass(frozen=True)
class _Metadata:
    left_digits: int = 1
    right_digits: int = 1
    output_digits: int = 1
    carry_count: int = 0
    borrow_count: int = 0
    event_count: int = 0
    longest_chain: int = 0
    result_width_change: int = 0
    zero_digit_count: int = 0
    nine_digit_count: int = 0
    has_zero: bool = False
    has_nine: bool = False
    requested_structure: str = "balanced"
    observed_structure: str = "no_event"


@dataclass(frozen=True)
class _Example:
    pair_id: str
    prompt: str
    completion: str
    answer: str
    operation: str
    metadata: _Metadata

    @property
    def difficulty(self) -> int:
        return max(self.metadata.left_digits, self.metadata.right_digits)


class _Provider:
    def __init__(self) -> None:
        self.seen_stages: list[dict[str, object]] = []

    @staticmethod
    def _example(arm: str, split: str, counter: int) -> _Example:
        operation = "add" if counter % 2 == 0 else "sub"
        left = counter % 7 + 1
        right = counter % 3 + 1
        if operation == "add":
            answer = str(left + right)
            prompt = f"{left}+{right}="
            metadata = _Metadata(
                carry_count=1,
                event_count=1,
                longest_chain=1,
                requested_structure="event",
                observed_structure="event",
            )
        else:
            left += right
            answer = str(left - right)
            prompt = f"{left}-{right}="
            metadata = _Metadata(
                borrow_count=1,
                event_count=1,
                longest_chain=1,
                requested_structure="event",
                observed_structure="event",
            )
        if arm == "pseudo_fst":
            completion = str((int(answer) + 3) % 10)
        elif arm == "deranged":
            completion = str((int(answer) + 5) % 10)
        else:
            completion = answer
        return _Example(
            pair_id=f"{split}-{counter}",
            prompt=prompt,
            completion=completion,
            answer=answer,
            operation=operation,
            metadata=metadata,
        )

    def batch(
        self,
        arm: str,
        split: str,
        start: int,
        size: int,
        stage: dict[str, object] | None = None,
    ) -> list[_Example]:
        self.seen_stages.append(dict(stage or {}))
        return [self._example(arm, split, counter) for counter in range(start, start + size)]

    def fixed_eval(
        self,
        arm: str,
        split: str,
        count: int,
        stage: dict[str, object] | None = None,
    ) -> list[_Example]:
        return self.batch(arm, split, 0, count, stage)

    def audit_control(
        self,
        arm: str,
        split: str,
        count: int,
        stage: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return {"valid": True, "arm": arm, "rows": count}


def _config(max_steps: int = 4) -> dict[str, object]:
    return {
        "model": {
            "vocab_size": 260,
            "d_model": 32,
            "n_layers": 1,
            "n_heads": 4,
            "d_ff": 64,
            "max_seq_len": 48,
            "dropout": 0.0,
            "rope_base": 10000.0,
            "tie_embeddings": True,
            "gradient_checkpointing": False,
        },
        "data": {"min_digits": 1, "max_digits": 2},
        "training": {
            "max_steps": max_steps,
            "microbatch_size": 2,
            "gradient_accumulation_steps": 1,
            "optimizer": "adamw",
            "learning_rate": 1e-3,
            "min_learning_rate": 1e-4,
            "weight_decay": 0.01,
            "beta1": 0.9,
            "beta2": 0.95,
            "adam_eps": 1e-8,
            "gradient_clip": 1.0,
            "precision": "fp32",
            "deterministic": True,
            "warmup_steps": 1,
            "stable_steps": 1,
            "decay_steps": max_steps - 2,
            "progress_every_steps": 2,
            "light_eval_every_steps": 2,
            "full_eval_every_steps": 4,
            "resume_every_steps": 2,
            "research_checkpoints": [0, 2, max_steps],
            "curriculum": [
                {
                    "name": "unit",
                    "start_step": 0,
                    "end_step": max_steps,
                    "digits": [1, 2],
                    "carry_chain": [0, 2],
                    "borrow_chain": [0, 2],
                    "operations": ["add", "sub"],
                }
            ],
        },
        "evaluation": {
            "light_items": 2,
            "full_items": 4,
            "full_batch_size": 2,
            "generation_max_new_tokens": 4,
            "splits": ["test_iid"],
            "panels": [
                {
                    "name": "test_iid",
                    "split": "test_iid",
                    "count": 4,
                    "stage": {"min_digits": 1, "max_digits": 2},
                }
            ],
        },
        "competence_gates": {
            "probe_requires": {
                "iid_exact": 0.0,
                "carry_exact": 0.0,
                "borrow_exact": 0.0,
                "malformed_max": 1.0,
            }
        },
    }


@unittest.skipUnless(torch is not None, "PyTorch is not installed")
class WorkspaceTrainerTests(unittest.TestCase):
    def test_atomic_checkpoint_fsync_uses_writable_descriptor(self) -> None:
        modes: list[str] = []
        real_open = Path.open

        def recording_open(path: Path, mode: str = "r", *args, **kwargs):
            modes.append(mode)
            return real_open(path, mode, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "checkpoint.pt"
            with patch.object(Path, "open", recording_open):
                _atomic_torch_save({"value": torch.tensor([1, 2, 3])}, destination)
            self.assertTrue(destination.is_file())
            self.assertFalse(destination.with_suffix(".pt.tmp").exists())
            self.assertIn("r+b", modes)
            loaded = torch.load(destination, map_location="cpu", weights_only=False)
            torch.testing.assert_close(loaded["value"], torch.tensor([1, 2, 3]))

    def test_resume_rejects_runtime_mismatch_and_tampered_model_fallback(self) -> None:
        model_config = ModelConfig.from_dict(
            {
                "vocab_size": 260,
                "d_model": 32,
                "n_layers": 1,
                "n_heads": 4,
                "ff_multiplier": 2,
                "max_seq_len": 48,
                "dropout": 0.0,
                "rope_base": 10000.0,
                "tie_embeddings": True,
            }
        )
        torch.manual_seed(41)
        model = TinyDecoderLM(model_config)
        runtime = {
            "schema_version": "workspace-runtime-compatibility-v1",
            "device_type": "cpu",
            "precision": "fp32",
            "torch": str(torch.__version__),
        }
        model_state = {
            name: tensor.detach().clone() for name, tensor in model.state_dict().items()
        }
        base_payload = {
            "schema_version": RESUME_SCHEMA,
            "fingerprint": "unit-fingerprint",
            "model_config": model_config.to_dict(),
            "runtime_compatibility": runtime,
            "step": 0,
            "successful_optimizer_steps": 0,
            "model": model_state,
            "model_hash": _model_state_hash(model),
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            valid_path = output / "resume_a.pt"
            _atomic_torch_save(base_payload, valid_path)
            self.assertIsNotNone(
                _load_resume_candidate(
                    valid_path,
                    "unit-fingerprint",
                    model_config,
                    runtime,
                )
            )
            self.assertIsNone(
                _load_resume_candidate(
                    valid_path,
                    "unit-fingerprint",
                    model_config,
                    {**runtime, "device_type": "cuda"},
                )
            )

            tampered = dict(base_payload)
            tampered["step"] = 1
            tampered["successful_optimizer_steps"] = 1
            tampered_state = {
                name: tensor.detach().clone()
                for name, tensor in model_state.items()
            }
            first_name = next(iter(tampered_state))
            tampered_state[first_name].view(-1)[0].add_(1.0)
            tampered["model"] = tampered_state
            # Deliberately retain the pre-tamper model_hash.
            tampered_path = output / "resume_b.pt"
            _atomic_torch_save(tampered, tampered_path)
            digest = hashlib.sha256(tampered_path.read_bytes()).hexdigest()
            (output / "resume_pointer.json").write_text(
                json.dumps(
                    {
                        "schema_version": RESUME_SCHEMA,
                        "slot": "resume_b.pt",
                        "sha256": digest,
                        "step": 1,
                        "resume_generation": 1,
                        "fingerprint": "unit-fingerprint",
                    }
                ),
                encoding="utf-8",
            )
            loaded = _load_latest_resume(
                output,
                "unit-fingerprint",
                model_config,
                runtime,
            )
            self.assertIsNotNone(loaded)
            assert loaded is not None
            payload, selected_path = loaded
            self.assertEqual(selected_path.name, "resume_a.pt")
            self.assertEqual(payload["step"], 0)

    def test_warmup_stable_decay_schedule(self) -> None:
        config = _config(max_steps=10)
        training = config["training"]
        assert isinstance(training, dict)
        training["warmup_steps"] = 2
        training["stable_steps"] = 4
        training["decay_steps"] = 4
        training["research_checkpoints"] = [0, 10]
        training["curriculum"][0]["end_step"] = 10
        settings = WorkspaceTrainSettings.from_config(config)
        self.assertAlmostEqual(learning_rate_at_step(settings, 1), 5e-4)
        self.assertAlmostEqual(learning_rate_at_step(settings, 2), 1e-3)
        self.assertAlmostEqual(learning_rate_at_step(settings, 6), 1e-3)
        self.assertAlmostEqual(learning_rate_at_step(settings, 10), 1e-4)

    def test_curriculum_translation_reaches_provider_fields(self) -> None:
        stage = _data_stage(
            {
                "name": "propagation",
                "digits": [3, 7],
                "carry_chain": [1, 3],
                "borrow_chain": [1, 3],
                "operations": ["add", "sub"],
            }
        )
        self.assertEqual(stage["min_digits"], 3)
        self.assertEqual(stage["max_digits"], 7)
        self.assertEqual(stage["structure_cycle"], ["event", "chain"])

    def test_control_exact_uses_completion_not_arithmetic_oracle(self) -> None:
        tokenizer = ByteTokenizer()
        example = _Example(
            pair_id="pseudo",
            prompt="1+2=",
            completion="7",
            answer="3",
            operation="add",
            metadata=_Metadata(),
        )

        class ExactTargetModel:
            config = SimpleNamespace(max_seq_len=48)

            def eval(self) -> "ExactTargetModel":
                return self

            def generate_batch(self, prefixes, eos_id, max_new_tokens, device):
                return [[ord("7"), eos_id] for _ in prefixes]

        report = evaluate_free_generation(
            model=ExactTargetModel(),  # type: ignore[arg-type]
            examples=[example],
            tokenizer=tokenizer,
            device="cpu",
            max_new_tokens=2,
            batch_size=1,
        )
        self.assertEqual(report["answer_exact_match"], 1.0)
        self.assertEqual(report["arithmetic_oracle_exact_match"], 0.0)

    def test_eos_only_output_is_malformed(self) -> None:
        example = _Provider._example("correct", "test", 0)

        class EmptyModel:
            config = SimpleNamespace(max_seq_len=48)

            def eval(self) -> "EmptyModel":
                return self

            def generate_batch(self, prefixes, eos_id, max_new_tokens, device):
                return [[eos_id] for _ in prefixes]

        report = evaluate_free_generation(
            model=EmptyModel(),  # type: ignore[arg-type]
            examples=[example],
            device="cpu",
            max_new_tokens=2,
            batch_size=1,
        )
        self.assertEqual(report["well_formed_rate"], 0.0)
        self.assertEqual(report["malformed_rate"], 1.0)

    def test_competence_gate_reports_missing_and_pass(self) -> None:
        group = {"answer_exact_match": 0.96, "examples": 20}
        evaluation = {
            "test_iid": {
                "answer_exact_match": 0.98,
                "malformed_rate": 0.0,
                "by_structure": {"carry": group, "borrow": group},
            },
            "test_ood_plus2": {
                "answer_exact_match": 0.93,
                "malformed_rate": 0.0,
                "by_structure": {},
            },
        }
        report = competence_report(
            evaluation,
            {
                "iid_exact": 0.97,
                "ood_exact": 0.90,
                "carry_exact": 0.95,
                "borrow_exact": 0.95,
                "malformed_max": 0.0,
            },
        )
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["ready"])

    def test_cpu_smoke_train_resume_and_model_only_checkpoint(self) -> None:
        provider = _Provider()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "correct"
            summary = train_arm(
                config=_config(),
                arm="correct",
                seed=123,
                output_dir=output,
                device="cpu",
                resume=True,
                data_provider=provider,
            )
            self.assertEqual(summary["optimizer_steps"], 4)
            self.assertNotEqual(
                summary["initial_model_hash"], summary["final_model_hash"]
            )
            progress = [
                json.loads(line)
                for line in (output / "progress.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([row["step"] for row in progress], [2, 4])
            self.assertTrue(all("latest_eval_age_steps" in row for row in progress))
            checkpoint = output / "checkpoints" / "model_step_000004.pt"
            payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
            self.assertEqual(payload["kind"], "model_only")
            self.assertNotIn("optimizer", payload)
            model, loaded = load_research_checkpoint(checkpoint)
            self.assertEqual(loaded["model_hash"], summary["final_model_hash"])
            self.assertEqual(model.config.d_model, 32)
            reused = train_arm(
                config=_config(),
                arm="correct",
                seed=123,
                output_dir=output,
                device="cpu",
                resume=True,
                data_provider=provider,
            )
            self.assertEqual(reused["final_model_hash"], summary["final_model_hash"])
            self.assertTrue(any(stage.get("min_digits") == 1 for stage in provider.seen_stages))


if __name__ == "__main__":
    unittest.main()
