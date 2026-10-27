"""Exact task factorization on a finite, fully declared archive domain.

String labels identify archives, attained representations, and answers. They are
opaque exact symbols, not mathematical truth values. The solver constructs a
uniform decoder or an explicit collision pair. It cannot generalize a finite
sample to an undeclared archive population.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


def _table(value: Mapping[str, str], name: str) -> dict[str, str]:
    result = dict(value)
    if any(type(k) is not str or type(v) is not str for k, v in result.items()):
        raise ValueError(f"{name} requires string identifiers and string values")
    return result


def _aligned(encoding: Mapping[str, str], answers: Mapping[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    e, a = _table(encoding, "encoding"), _table(answers, "answers")
    if e.keys() != a.keys():
        raise ValueError("encoding and task must have exactly the same declared domain")
    return e, a


@dataclass(frozen=True, slots=True)
class DecoderCertificate:
    """One answer for each attained code, with no unattained-domain obligations."""
    entries: tuple[tuple[str, str], ...]

    def decode(self, code: str) -> str:
        table = _decoder(self)
        if type(code) is not str:
            raise ValueError("code must be a string")
        if code not in table:
            raise KeyError("unattained representation")
        return table[code]


@dataclass(frozen=True, slots=True)
class CollisionWitness:
    left: str
    right: str


@dataclass(frozen=True, slots=True)
class FactorizationResult:
    decoder: DecoderCertificate | None = None
    collision: CollisionWitness | None = None

    @property
    def sufficient(self) -> bool:
        return self.decoder is not None and self.collision is None


def _decoder(value: DecoderCertificate) -> dict[str, str]:
    if not isinstance(value, DecoderCertificate) or type(value.entries) is not tuple:
        raise ValueError("invalid decoder record")
    result: dict[str, str] = {}
    for pair in value.entries:
        if type(pair) is not tuple or len(pair) != 2 or any(type(v) is not str for v in pair):
            raise ValueError("decoder entries must be pairs of strings")
        key, answer = pair
        if key in result:
            raise ValueError("decoder repeats a representation")
        result[key] = answer
    return result


def factor_task(encoding: Mapping[str, str], answers: Mapping[str, str]) -> FactorizationResult:
    """Construct a decoder or a deterministic first collision on the full domain."""
    e, a = _aligned(encoding, answers)
    first: dict[str, str] = {}
    table: dict[str, str] = {}
    for archive in sorted(e):
        code, answer = e[archive], a[archive]
        if code in table and table[code] != answer:
            return FactorizationResult(collision=CollisionWitness(first[code], archive))
        first.setdefault(code, archive)
        table[code] = answer
    return FactorizationResult(decoder=DecoderCertificate(tuple(sorted(table.items()))))


def verify_factorization(encoding: Mapping[str, str], answers: Mapping[str, str],
                         result: FactorizationResult) -> bool:
    """Check an output without invoking factor_task or trusting its status flag.

    Malformed problem specifications raise ValueError. Invalid certificates return
    False. An empty decoder is valid for an empty archive domain.
    """
    e, a = _aligned(encoding, answers)
    if not isinstance(result, FactorizationResult):
        return False
    if (result.decoder is None) == (result.collision is None):
        return False
    if result.decoder is not None:
        try:
            table = _decoder(result.decoder)
        except (ValueError, TypeError):
            return False
        return set(table) == set(e.values()) and all(table[e[x]] == a[x] for x in e)
    w = result.collision
    if not isinstance(w, CollisionWitness) or type(w.left) is not str or type(w.right) is not str:
        return False
    return (w.left in e and w.right in e and w.left != w.right
            and e[w.left] == e[w.right] and a[w.left] != a[w.right])


def compose_decoders(outer: DecoderCertificate, inner: DecoderCertificate) -> DecoderCertificate:
    """Compose fine-to-coarse and coarse-to-task tables, rejecting missing intermediates."""
    d, r = _decoder(outer), _decoder(inner)
    if not set(r.values()) <= set(d):
        raise ValueError("an intermediate representation has no outer decoder value")
    return DecoderCertificate(tuple(sorted((key, d[value]) for key, value in r.items())))


def joint_task_scheme(domain: Iterable[str], tasks: Sequence[Mapping[str, str]]) -> dict[str, str]:
    """Encode equality classes of the joint task vector, including an empty task family.

    Generated class labels encode equality only. Permuting or changing the task
    family can relabel the classes. No storage-optimal byte encoding is claimed.
    """
    ids = tuple(domain)
    if any(type(x) is not str for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("domain identifiers must be distinct strings")
    tables = tuple(_table(t, "task") for t in tasks)
    if any(set(t) != set(ids) for t in tables):
        raise ValueError("every task must have exactly the declared domain")
    signatures = {x: tuple(t[x] for t in tables) for x in ids}
    labels = {s: f"task-class-{i}" for i, s in enumerate(sorted(set(signatures.values())))}
    return {x: labels[signatures[x]] for x in sorted(ids)}
