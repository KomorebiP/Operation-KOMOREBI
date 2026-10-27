from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
from unittest import mock

try:
    import torch
    import torch.nn as nn
except ImportError:  # pragma: no cover - expected in lightweight verification
    torch = None
    nn = None


if nn is not None:
    from neuralese_g1.model import FrozenRecurrentCausalLM, last_valid_positions
    from neuralese_g1.runtime import (
        atomic_torch_save,
        capture_rng_state,
        restore_rng_state,
        train_steps,
    )

    class _FakeBlock(nn.Module):
        def __init__(self, width: int) -> None:
            super().__init__()
            self.linear = nn.Linear(width, width)

        def forward(self, hidden_states, **_kwargs):
            return (hidden_states + torch.tanh(self.linear(hidden_states)),)


    class _FakeCore(nn.Module):
        def __init__(self, width: int, layers: int) -> None:
            super().__init__()
            self.layers = nn.ModuleList([_FakeBlock(width) for _ in range(layers)])


    class _FakeCausalLM(nn.Module):
        def __init__(self, width: int = 12, layers: int = 3, vocab: int = 31) -> None:
            super().__init__()
            self.config = SimpleNamespace(hidden_size=width)
            self.embedding = nn.Embedding(vocab, width)
            self.model = _FakeCore(width, layers)
            self.output = nn.Linear(width, vocab, bias=False)
            self.calls: list[bool] = []

        def forward(
            self,
            *,
            input_ids,
            attention_mask,
            output_hidden_states,
            use_cache,
            return_dict,
        ):
            del attention_mask, return_dict
            self.calls.append(bool(use_cache))
            hidden = self.embedding(input_ids)
            states = [hidden]
            for block in self.model.layers:
                hidden = block(hidden)[0]
                states.append(hidden)
            return SimpleNamespace(
                logits=self.output(hidden),
                hidden_states=tuple(states) if output_hidden_states else None,
            )


    class _TrainingStub(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.weight = nn.Parameter(torch.tensor(0.25))

        def workspace_parameters(self):
            return [self.weight]

        def forward(self, compute_ids, compute_mask, query_ids, query_mask, **_kwargs):
            del compute_mask, query_ids, query_mask
            rows = compute_ids.shape[0]
            logits = torch.stack(
                (self.weight.expand(rows), (-self.weight).expand(rows)), dim=-1
            )
            trace = SimpleNamespace(
                detached_statistics=lambda: {
                    "logical_steps": 1,
                    "state_mean_norm_by_step": [1.0, 1.0],
                    "injection_mean_norm_by_step": [1.0],
                    "feedback_mean_norm_by_step": [1.0, 1.0],
                    "halt_probability_mean_by_step": [0.5],
                }
            )
            return logits, trace


    class _OneOverflowScaler:
        def __init__(self, parameter) -> None:
            self.parameter = parameter
            self.current_scale = 1024.0
            self.unscale_calls = 0
            self.found_inf = False

        def is_enabled(self):
            return True

        def get_scale(self):
            return self.current_scale

        def scale(self, loss):
            return loss

        def unscale_(self, _optimizer):
            self.found_inf = self.unscale_calls == 0
            self.unscale_calls += 1
            if self.found_inf:
                self.parameter.grad.fill_(float("inf"))

        def step(self, optimizer):
            if not self.found_inf:
                optimizer.step()

        def update(self):
            if self.found_inf:
                self.current_scale /= 2.0
            self.found_inf = False


@unittest.skipUnless(torch is not None, "PyTorch is unavailable")
class ModelTests(unittest.TestCase):
    def setUp(self) -> None:
        assert torch is not None
        torch.manual_seed(17)
        self.backbone = _FakeCausalLM()
        self.model = FrozenRecurrentCausalLM(
            self.backbone,
            source_layer=1,
            workspace_width=8,
            recurrent_steps=2,
            injection_scale=5.0,
            state_clip=8.0,
            dropout=0.0,
        )
        self.compute_ids = torch.tensor([[1, 2, 3], [4, 5, 0]])
        self.compute_mask = torch.tensor([[1, 1, 1], [1, 1, 0]])
        self.query_ids = torch.tensor([[6, 7], [8, 9]])
        self.query_mask = torch.ones_like(self.query_ids)

    def test_forward_backprop_freezes_backbone_and_removes_hook(self) -> None:
        logits, trace = self.model(
            self.compute_ids,
            self.compute_mask,
            self.query_ids,
            self.query_mask,
        )
        logits.float().square().mean().backward()
        self.assertEqual(trace.detached_statistics()["logical_steps"], 2)
        self.assertTrue(any(parameter.grad is not None for parameter in self.model.workspace.parameters()))
        self.assertTrue(all(parameter.grad is None for parameter in self.backbone.parameters()))
        self.assertTrue(all(value is False for value in self.backbone.calls))
        self.assertFalse(self.backbone.model.layers[1]._forward_pre_hooks)
        self.assertFalse(any(name.startswith("layers.") for name, _ in self.model.named_parameters()))

    def test_one_step_consumes_injected_feedback(self) -> None:
        one_step = FrozenRecurrentCausalLM(
            _FakeCausalLM(),
            source_layer=1,
            workspace_width=8,
            recurrent_steps=1,
            injection_scale=20.0,
            state_clip=8.0,
            dropout=0.0,
        )
        recurrent, _ = one_step.encode(self.compute_ids, self.compute_mask, mode="recurrent")
        ablated, _ = one_step.encode(self.compute_ids, self.compute_mask, mode="no_feedback")
        self.assertGreater(float((recurrent - ablated).abs().max().item()), 0.0)

    def test_zero_mode_is_literal_no_injection(self) -> None:
        actual = self.model.answer(self.query_ids, self.query_mask, None)
        raw = self.backbone(
            input_ids=self.query_ids,
            attention_mask=self.query_mask,
            output_hidden_states=True,
            use_cache=False,
            return_dict=True,
        )
        positions = last_valid_positions(self.query_mask)
        rows = torch.arange(self.query_ids.shape[0])
        self.assertTrue(torch.equal(actual, raw.logits[rows, positions]))

    def test_padding_mask_must_be_contiguous(self) -> None:
        with self.assertRaises(ValueError):
            last_valid_positions(torch.tensor([[1, 0, 1]]))

    def test_checkpoint_primitives_load_with_restricted_unpickler(self) -> None:
        parameter = torch.nn.Parameter(torch.tensor([1.0]))
        optimizer = torch.optim.AdamW([parameter])
        scaler = torch.amp.GradScaler("cuda", enabled=torch.cuda.is_available())
        payload = {
            "workspace_state": {"weight": parameter.detach().clone()},
            "optimizer_state": optimizer.state_dict(),
            "scaler_state": scaler.state_dict(),
            "rng_state": capture_rng_state(),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            atomic_torch_save(path, payload)
            loaded = torch.load(path, map_location="cpu", weights_only=True)
        self.assertEqual(set(loaded), set(payload))
        restore_rng_state(loaded["rng_state"])

    def test_overflow_retries_same_batch_without_counting_failed_step(self) -> None:
        model = _TrainingStub()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        scaler = _OneOverflowScaler(model.weight)
        examples = [SimpleNamespace(name="first"), SimpleNamespace(name="second")]
        batches = []

        def fake_tokenize(_tokenizer, selected, *, max_length, device):
            del max_length, device
            batches.append([item.name for item in selected])
            rows = len(selected)
            values = torch.ones((rows, 1), dtype=torch.long)
            return {
                "compute_input_ids": values,
                "compute_attention_mask": values,
                "query_input_ids": values,
                "query_attention_mask": values,
                "labels": torch.zeros(rows, dtype=torch.long),
            }

        records = []
        checkpoints = []
        config = {
            "model": {"max_sequence_length": 8, "device": "cpu"},
            "training": {
                "batch_size": 1,
                "steps": 2,
                "log_every": 1,
                "gradient_clip": 1.0,
                "max_overflow_retries": 2,
            },
        }
        with mock.patch("neuralese_g1.runtime.tokenize_batch", side_effect=fake_tokenize):
            result = train_steps(
                model,
                None,
                examples,
                config=config,
                optimizer=optimizer,
                scaler=scaler,
                start_step=0,
                start_overflow_retries=0,
                log_callback=records.append,
                checkpoint_callback=checkpoints.append,
            )
        self.assertEqual(batches, [["first"], ["first"], ["second"]])
        self.assertEqual([record["step"] for record in records], [1, 2])
        self.assertEqual(
            [record["overflow_retries_total"] for record in records], [1, 1]
        )
        self.assertEqual(
            [record["optimizer_attempts_total"] for record in records], [2, 3]
        )
        self.assertEqual(checkpoints, [1, 2])
        self.assertEqual(result["completed_steps"], 2)

if __name__ == "__main__":
    unittest.main()
