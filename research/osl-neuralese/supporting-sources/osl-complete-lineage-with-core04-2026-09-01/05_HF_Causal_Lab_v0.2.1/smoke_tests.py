from __future__ import annotations

import random

import torch
from torch import nn

from run_experiment import (
    Event,
    MODE_ID,
    OPS,
    equivalent_path,
    execute,
    generate_motif_trace,
    generate_random_trace,
    linked_motif,
    make_causal_pairs,
    state_labels,
    transition_loss,
)


class TinyTransitionModel(nn.Module):
    def __init__(self, hidden: int):
        super().__init__()
        self.transitions = nn.ModuleList([nn.Linear(hidden, hidden) for _ in OPS])


def mixed_precision_transition_smoke() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    hidden = 16
    model = TinyTransitionModel(hidden).to(device)
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    prefix = torch.randn(len(OPS), hidden, device=device, dtype=dtype, requires_grad=True)
    target = torch.randn(len(OPS), hidden, device=device, dtype=dtype)
    next_op = torch.arange(len(OPS), device=device)
    if device.type == "cuda":
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            loss = transition_loss(model, prefix, target, next_op)
    else:
        loss = transition_loss(model, prefix, target, next_op)
    assert loss.dtype == torch.float32
    assert torch.isfinite(loss)
    loss.backward()
    for transition in model.transitions:
        assert transition.weight.grad is not None
        assert torch.isfinite(transition.weight.grad).all()
    print(f"transition precision smoke passed on {device}")


def main() -> None:
    mixed_precision_transition_smoke()
    events = [
        Event("OBSERVE", 0, 0),
        Event("TELL", 0, 0, other=1),
        Event("INFER", 1, 1, source_fact=0),
        Event("AUTHORIZE", 1, 1),
    ]
    state = execute(events)
    assert state is not None
    assert state.mode[0, 0] == MODE_ID["observed"]
    assert state.mode[1, 0] == MODE_ID["communicated"]
    assert state.mode[1, 1] == MODE_ID["inferred"]
    assert state.authorized[1, 1] == 1
    assert linked_motif(events)
    labels = state_labels(state, 1, 1)
    assert labels["access"] == 1 and labels["eligible"] == 1

    rng = random.Random(71)
    random_events, random_state = generate_random_trace(rng, 6, forbid_linked_motif=True)
    assert not linked_motif(random_events)
    alternate = equivalent_path(random_events, random_state, rng)
    alternate_state = execute(alternate)
    assert alternate_state is not None
    assert alternate_state.fingerprint() == random_state.fingerprint()

    motif_events, motif_state = generate_motif_trace(random.Random(93), 6)
    assert motif_state is not None and linked_motif(motif_events)

    pair = make_causal_pairs(119, 1)[0]
    before = state_labels(execute([Event(*x) for x in pair.base.events]), pair.base.query_agent, pair.base.query_fact)
    after = state_labels(execute([Event(*x) for x in pair.counterfactual.events]), pair.counterfactual.query_agent, pair.counterfactual.query_fact)
    assert before["mode"] == MODE_ID["communicated"]
    assert after["mode"] == MODE_ID["observed"]
    assert before["origin"] == after["origin"]
    assert before["access"] == after["access"] == 1
    print("smoke tests passed")


if __name__ == "__main__":
    main()
