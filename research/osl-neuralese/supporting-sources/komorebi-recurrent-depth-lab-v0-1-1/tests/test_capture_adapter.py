from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "capture_huginn.py"
SPEC = importlib.util.spec_from_file_location("capture_huginn_for_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)


class FakeTensor:
    def __init__(self, value):
        self.value = np.asarray(value, dtype=float)

    def clone(self):
        return FakeTensor(self.value.copy())

    def detach(self):
        return self

    def float(self):
        return self

    def norm(self):
        return FakeScalar(np.linalg.norm(self.value))

    def abs(self):
        return FakeTensor(np.abs(self.value))

    def max(self):
        return FakeScalar(np.max(self.value))

    def __sub__(self, other):
        return FakeTensor(self.value - other.value)


class FakeScalar:
    def __init__(self, value):
        self.value = float(value)

    def item(self):
        return self.value


class FakeModel:
    def __init__(self):
        self.transformer = SimpleNamespace(ln_f=lambda state: FakeTensor(2.0 * state.value))
        self.forward_flags = []

    def iterate_one_step(
        self,
        input_embeds,
        input_states,
        *,
        block_idx,
        current_step,
        past_key_values,
    ):
        return FakeTensor(input_states.value + 1.0), block_idx + 1, current_step + 1

    def predict_from_latents(self, state):
        return SimpleNamespace(logits=FakeTensor(5.0 * state.value))

    def __call__(self, **kwargs):
        return self.forward(**kwargs)

    def forward(
        self,
        input_ids,
        input_states,
        num_steps,
        use_cache,
        output_details,
    ):
        assert use_cache is False
        assert set(output_details) == {
            "return_logits",
            "return_latents",
            "return_head",
            "return_stats",
        }
        self.forward_flags.append(output_details.copy())
        raw = FakeTensor(input_states.value + float(num_steps))
        return SimpleNamespace(
            latent_states=self.transformer.ln_f(raw),
            logits=self.predict_from_latents(raw).logits,
        )


def test_manual_forward_adapter_uses_raw_state_and_complete_output_flags() -> None:
    model = FakeModel()
    rows = CAPTURE._forward_equivalence(
        model,
        input_ids=FakeTensor([[1.0]]),
        embedded=FakeTensor([[9.0]]),
        initial_state=FakeTensor([[0.25]]),
        block_idx=0,
        depths=[1, 2, 4],
    )
    assert len(rows) == 3
    assert len(model.forward_flags) == 3
    for row in rows:
        assert row["latent_relative_error"] == 0.0
        assert row["latent_max_absolute_error"] == 0.0
        assert row["logit_relative_error"] == 0.0
        assert row["logit_max_absolute_error"] == 0.0


def test_huginn_transformers_version_gate_accepts_v4() -> None:
    CAPTURE._require_huginn_transformers_4("4.57.6")
    CAPTURE._require_huginn_transformers_4("4.44.2")


def test_huginn_transformers_version_gate_rejects_v5_before_download() -> None:
    with pytest.raises(RuntimeError, match=r"Transformers 4\.x; found '5\.16\.1'") as exc:
        CAPTURE._require_huginn_transformers_4("5.16.1")
    assert "transformers==4.57.6" in str(exc.value)
    assert "do not add --allow-download" in str(exc.value)
