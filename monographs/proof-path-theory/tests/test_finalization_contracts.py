"""Finite regressions for the publication's explicit logical and encoding contracts.

These tests are executable examples, not formal proofs of the general statements.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json

import pytest

from proof_path_theory import (
    ClaimNode, Justification, NodeKind, ProofField, ProofFieldViews,
    ClaimRevision, LedgerSnapshot, provenance_digest,
)

PREFIX = b"proof-path-provenance:v2\x00"


def reference_bytes(parts: tuple[str, ...]) -> bytes:
    return PREFIX + json.dumps(list(parts), ensure_ascii=True, separators=(",", ":")).encode("ascii")


def supports(encoding: tuple[int, ...], answers: tuple[int, ...]) -> bool:
    return all(encoding[i] != encoding[j] or answers[i] == answers[j]
               for i in range(len(encoding)) for j in range(len(encoding)))


def test_tuple_boundaries_survive_embedded_legacy_separator() -> None:
    left, right = ("A\x1fB", "C"), ("A", "B\x1fC")
    # This was an encoding collision, not a collision between different hash inputs.
    assert "\x1f".join(left) == "\x1f".join(right)
    assert provenance_digest(*left) != provenance_digest(*right)


def test_zero_parts_and_one_empty_part_are_distinct() -> None:
    assert provenance_digest() != provenance_digest("")
    assert provenance_digest("") != provenance_digest("", "")


@pytest.mark.parametrize("parts", [(), ("A", "B"), ("\x00", "\x1f", "é", "e\u0301", "\U0001f600")])
def test_versioned_digest_matches_documented_bytes(parts: tuple[str, ...]) -> None:
    encoded = reference_bytes(parts)
    assert json.loads(encoded[len(PREFIX):]) == list(parts)
    assert provenance_digest(*parts) == sha256(encoded).hexdigest()


@pytest.mark.parametrize("bad", [None, 2, b"bytes"])
def test_digest_requires_string_parts(bad: object) -> None:
    with pytest.raises(TypeError):
        provenance_digest("A", bad)  # type: ignore[arg-type]


def test_finite_tuple_encoding_preserves_empty_control_and_unicode_parts() -> None:
    alphabet = ("", "a", "|", "\x1f", "\x00", "é", "e\u0301")
    inputs = [parts for size in range(5) for parts in product(alphabet, repeat=size)]
    encoded = [reference_bytes(parts) for parts in inputs]
    assert len(inputs) == 2801
    assert len(set(encoded)) == len(inputs)
    for parts, data in zip(inputs, encoded):
        assert tuple(json.loads(data[len(PREFIX):])) == parts
    # Finite observation only: this is not a universal no-hash-collision assertion.
    assert len({provenance_digest(*parts) for parts in inputs}) == len(inputs)


def test_snapshot_digest_retains_its_separate_existing_protocol() -> None:
    snap = LedgerSnapshot("fixed", (ClaimRevision("A", "proved", timestamp_utc="2026-10-19T00:00:00Z"),))
    data = json.dumps(snap.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    assert snap.digest() == sha256(data).hexdigest()


def test_preserving_the_target_does_not_preserve_side_tasks() -> None:
    # Both archives certify the same goal, but their side observations differ.
    old, new = (0, 1), (0, 0)
    goal, side = (1, 1), (0, 1)
    assert supports(old, goal) and supports(new, goal)
    assert supports(old, side) and not supports(new, side)


def test_factorized_refinement_preserves_supported_tasks_exhaustively() -> None:
    for fine in product(range(3), repeat=4):
        for back in product(range(2), repeat=3):
            coarse = tuple(back[value] for value in fine)
            for task in product(range(2), repeat=4):
                if supports(coarse, task):
                    assert supports(fine, task)


def test_full_positive_rule_model_exists_for_all_256_declared_cases() -> None:
    possible = [((), 'a'), (('a',), 'b'), (('a',), 'c'), (('b',), 'c'), (('a', 'b'), 'c')]
    for mask in range(32):
        rules = [Justification(str(i), pre, con, 'declared positive rule')
                 for i, (pre, con) in enumerate(possible) if mask & (1 << i)]
        for bits in product((False, True), repeat=3):
            leaves = tuple(v for v, keep in zip(('a', 'b', 'c'), bits) if keep)
            field = ProofField([ClaimNode(v, v, NodeKind.PREMISE if v in leaves else NodeKind.CLAIM)
                                for v in ('a', 'b', 'c')], rules, premises=leaves, targets=('c',))
            views = ProofFieldViews(field)
            assert views.is_local_model(views.nodes, views.nodes)
            assert views.least_model() <= views.nodes


def test_same_labels_and_required_premises_do_not_fix_admitted_axioms() -> None:
    def field(kind: NodeKind) -> ProofField:
        return ProofField([ClaimNode('a', 'a', kind), ClaimNode('b', 'b', NodeKind.CLAIM)],
                          [Justification('ab', ('a',), 'b', 'declared implication')],
                          premises=(), targets=('b',))
    admitted, unadmitted = field(NodeKind.AXIOM), field(NodeKind.CLAIM)
    assert admitted.premises == unadmitted.premises and admitted.targets == unadmitted.targets
    assert 'b' in admitted.derive() and 'b' not in unadmitted.derive()


@pytest.mark.parametrize('bad', ['\ud800', '\udfff', '\ud83d\ude00'])
def test_surrogate_code_points_are_outside_the_unicode_scalar_contract(bad: str) -> None:
    # JSON's ASCII escapes otherwise identify a surrogate pair with an astral scalar.
    if len(bad) == 2:
        assert json.dumps(bad, ensure_ascii=True) == json.dumps('\U0001f600', ensure_ascii=True)
    with pytest.raises(ValueError, match='surrogate'):
        provenance_digest(bad)
