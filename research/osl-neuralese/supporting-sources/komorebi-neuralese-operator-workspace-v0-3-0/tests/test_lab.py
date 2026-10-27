from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import D4_RELATIONS, N_STATES, audit_algebra, canonical_maps, compose_single, conjugate_maps
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.evaluate import _norm_matched_random, apply_slots_torch
from komorebi_neuralese.models import RecurrentOperatorModel, build_model
from komorebi_neuralese.transport import collect_paired_hidden, fit_affine_transport


def test_d4_relations_are_exact() -> None:
    audit = audit_algebra("d4")
    assert audit.valid_permutations
    assert audit.relation_results == {name: True for name in D4_RELATIONS}


def test_conjugation_preserves_relations() -> None:
    rng = np.random.default_rng(11)
    phi = np.argsort(rng.random((32, N_STATES)), axis=1)
    conjugated = conjugate_maps(canonical_maps("d4"), phi)
    identity = np.arange(N_STATES)
    for example in range(conjugated.shape[0]):
        for word in D4_RELATIONS.values():
            assert np.array_equal(compose_single(conjugated[example], word), identity)


def test_episode_targets_match_exact_map_execution() -> None:
    generator = EpisodeGenerator(7)
    batch = generator.sample(64, 9, family="d4")
    observed = apply_slots_torch(batch.maps, batch.start, batch.op_slots)
    assert torch.equal(observed, batch.target)
    assert torch.equal(batch.intermediates[:, -1], batch.target)


def test_slot_randomization_hides_fixed_token_semantics() -> None:
    generator = EpisodeGenerator(19)
    batch = generator.sample(1024, 1, family="d4")
    r_slot = batch.canonical_to_slot[:, 0]
    fraction_slot_zero = float((r_slot == 0).float().mean())
    assert 0.45 < fraction_slot_zero < 0.55


def test_models_have_valid_shapes() -> None:
    generator = EpisodeGenerator(23)
    batch = generator.sample(16, 5, family="d4")
    for name in ("linear_hyper", "gru", "token_only", "one_shot"):
        model = build_model(name, max_length=12)
        logits = model(batch.tables, batch.op_slots, batch.start)
        assert logits.shape == (16, N_STATES)
        assert torch.isfinite(logits).all()
        if isinstance(model, RecurrentOperatorModel):
            trace = model.run(batch.tables, batch.op_slots, batch.start)
            assert len(trace.hidden) == 6
            assert trace.operator_codes is not None


def test_affine_transport_recovers_known_map() -> None:
    generator = torch.Generator().manual_seed(31)
    x = torch.randn(4096, 8, generator=generator)
    q, _ = torch.linalg.qr(torch.randn(8, 8, generator=generator))
    bias = torch.randn(8, generator=generator)
    y = x @ q + bias
    transport = fit_affine_transport(x, y, ridge=1e-8)
    prediction = transport.apply(x)
    assert torch.max(torch.abs(prediction - y)) < 1e-4


def test_norm_matched_random_preserves_per_example_norm() -> None:
    generator = torch.Generator().manual_seed(37)
    reference = torch.randn(64, 8, generator=generator)
    random = _norm_matched_random(reference, generator)
    assert torch.allclose(reference.norm(dim=1), random.norm(dim=1), atol=1e-5, rtol=1e-5)


def test_paired_hidden_collection_uses_d4_anchors() -> None:
    torch.manual_seed(41)
    source = build_model("linear_hyper", max_length=12)
    torch.manual_seed(43)
    target = build_model("linear_hyper", max_length=12)
    x, y = collect_paired_hidden(source, target, seed=47, examples=16, batch_size=8, max_length=4, device=torch.device("cpu"))
    assert x.shape == y.shape
    assert x.ndim == 2
    assert x.shape[1] == 8
    assert torch.isfinite(x).all() and torch.isfinite(y).all()
