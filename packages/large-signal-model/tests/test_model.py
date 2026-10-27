from __future__ import annotations

import numpy as np

from komorebi_arc3_offline.actions import ActionCandidateGenerator
from komorebi_arc3_offline.memory import TransitionMemory
from komorebi_arc3_offline.model import BayesianOperatorWorldModel
from komorebi_arc3_offline.types import ActionCandidate, FramePackets


def packets(coarse: np.ndarray, fine: np.ndarray, signature: str) -> FramePackets:
    return FramePackets(
        coarse=coarse,
        fine=fine,
        raw=np.zeros(4),
        signature=signature,
        background=0,
        components=(),
        salient_points=(),
        change_fraction=0.0,
        non_background_fraction=0.0,
        phase2_energy=(0.0,) * 4,
        phase4_energy=(0.0,) * 16,
    )


def test_bayesian_operator_model_fits_action_conditioned_linear_dynamics() -> None:
    rng = np.random.default_rng(2)
    memory = TransitionMemory(maximum_records=128)
    generator = ActionCandidateGenerator()
    state_c = rng.normal(size=24)
    state_f = rng.normal(size=48)
    first = packets(state_c, state_f, "s0")
    memory.initialize(first)
    for step in range(30):
        action_id = 1 + (step % 2)
        candidate = ActionCandidate(action_id, role=("simple", action_id))
        action_features = generator.features(candidate)
        delta_c = 0.06 * state_c + (0.03 if action_id == 2 else -0.02)
        delta_f = 0.04 * state_f + (0.025 if action_id == 2 else -0.015)
        next_c = state_c + delta_c
        next_f = state_f + delta_f
        before = packets(state_c, state_f, f"s{step}")
        after = packets(next_c, next_f, f"s{step+1}")
        record = memory.make_record(
            before=before,
            after=after,
            action_features=action_features,
            candidate=candidate,
            reward=float(action_id == 2),
            level_delta=0,
            terminal_win=False,
            terminal_loss=False,
            step_index=step,
            source="committed",
        )
        memory.add(record, after_packets=after)
        state_c, state_f = next_c, next_f
    model = BayesianOperatorWorldModel(minimum_records=8)
    fitted = model.fit(memory)
    assert fitted
    summary = model.posterior_summary()
    assert summary["best_program"] is not None
    assert sum(summary["family_probabilities"].values()) > 0.999
