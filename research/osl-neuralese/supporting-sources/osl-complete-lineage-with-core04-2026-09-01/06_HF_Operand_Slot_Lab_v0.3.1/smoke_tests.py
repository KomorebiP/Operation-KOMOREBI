from __future__ import annotations

import random

import torch
from transformers import BertConfig

from run_experiment import (
    AGENTS,
    CAUSAL_FAMILIES,
    CELL_COUNT,
    FACTS,
    LABEL_DIMS,
    MODE_ID,
    OP_ID,
    OPS,
    Event,
    OSLBert,
    equivalent_path,
    execute,
    generate_motif_trace,
    generate_random_trace,
    linked_motif,
    make_causal_pairs,
    set_seed,
    slot_transition_loss,
    state_labels,
)


def tiny_model(device: torch.device) -> OSLBert:
    config = BertConfig(
        vocab_size=96,
        hidden_size=32,
        num_hidden_layers=1,
        num_attention_heads=4,
        intermediate_size=64,
        max_position_embeddings=64,
        pad_token_id=0,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
    )
    return OSLBert(config).to(device)


def workspace_and_precision_smoke() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    set_seed(17, deterministic=True)
    model = tiny_model(device)
    batch_size = len(OPS)
    ids = torch.randint(3, 95, (batch_size, 20), device=device)
    ids[:, 0] = 2
    mask = torch.ones_like(ids)
    z, slots, _ = model.encode_story(ids, mask)
    assert z.shape == (batch_size, 32)
    assert slots.shape == (batch_size, CELL_COUNT, 32)

    dtype = torch.float16 if device.type == "cuda" else torch.float32
    prefix = slots.detach().to(dtype).requires_grad_(True)
    target = torch.randn_like(prefix)
    op = torch.arange(len(OPS), device=device)
    actor = torch.tensor([0, 0, 1, 2, 3], dtype=torch.long, device=device)
    fact = torch.tensor([0, 1, 2, 3, 4], dtype=torch.long, device=device)
    other = torch.tensor([-1, 2, -1, -1, -1], dtype=torch.long, device=device)
    source = torch.tensor([-1, -1, -1, 0, -1], dtype=torch.long, device=device)
    batch = {
        "next_op": op,
        "next_actor": actor,
        "next_fact": fact,
        "next_other": other,
        "next_source_fact": source,
        "next_full_mode": torch.randint(0, LABEL_DIMS["mode"], (batch_size, CELL_COUNT), device=device),
        "next_full_origin": torch.randint(0, LABEL_DIMS["origin"], (batch_size, CELL_COUNT), device=device),
        "next_full_authorized": torch.randint(0, 2, (batch_size, CELL_COUNT), device=device),
    }
    class_weights = {
        "mode": torch.ones(LABEL_DIMS["mode"], device=device),
        "origin": torch.ones(LABEL_DIMS["origin"], device=device),
        "authorized": torch.ones(2, device=device),
    }
    context = (
        torch.autocast(device_type="cuda", dtype=torch.float16)
        if device.type == "cuda"
        else torch.autocast(device_type="cpu", enabled=False)
    )
    with context:
        loss, parts = slot_transition_loss(model, prefix, target, batch, class_weights)
    assert loss.dtype == torch.float32 and torch.isfinite(loss)
    assert all(torch.isfinite(value) for value in parts.values())
    loss.backward()
    assert prefix.grad is not None and torch.isfinite(prefix.grad).all()
    for name, parameter in model.named_parameters():
        if name.startswith(("transition_mlp", "transition_norm", "write_locator", "event_")):
            assert parameter.grad is not None, f"missing transition gradient: {name}"
            assert torch.isfinite(parameter.grad).all(), f"non-finite transition gradient: {name}"

    with torch.no_grad():
        updated, affected = model.transition_workspace(prefix.float(), op, actor, fact, other, source)
    write_mask = torch.nn.functional.one_hot(affected, num_classes=CELL_COUNT).bool()
    assert torch.equal(updated[~write_mask], prefix.float()[~write_mask])
    print(f"workspace and transition precision smoke passed on {device}")


def executable_world_smoke() -> None:
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


def causal_bank_smoke() -> None:
    id_pairs = make_causal_pairs(119, 10, bank="train", difficulty="id")
    blocked = {pair.case_id for pair in id_pairs}
    ood_pairs = make_causal_pairs(211, 10, bank="held", difficulty="ood", blocked_case_ids=blocked)
    assert {pair.family for pair in id_pairs} == set(CAUSAL_FAMILIES)
    assert len({pair.case_id for pair in id_pairs + ood_pairs}) == 20
    assert all(2 <= pair.counterfactual.length <= 4 for pair in id_pairs)
    assert all(5 <= pair.counterfactual.length <= 7 for pair in ood_pairs)
    for pair in id_pairs + ood_pairs:
        base_state = execute([Event(*value) for value in pair.base.events])
        counter_state = execute([Event(*value) for value in pair.counterfactual.events])
        assert base_state is not None and counter_state is not None
        before = state_labels(base_state, pair.base.query_agent, pair.base.query_fact)
        after = state_labels(counter_state, pair.counterfactual.query_agent, pair.counterfactual.query_fact)
        assert any(before[key] != after[key] for key in ("mode", "origin", "authorized"))
        added = Event(*pair.added_event)
        assert added.op in OP_ID
        assert 0 <= pair.base.query_agent < len(AGENTS)
        assert 0 <= pair.base.query_fact < len(FACTS)
    print("causal bank smoke passed")


def main() -> None:
    workspace_and_precision_smoke()
    executable_world_smoke()
    causal_bank_smoke()
    print("smoke tests passed")


if __name__ == "__main__":
    main()
