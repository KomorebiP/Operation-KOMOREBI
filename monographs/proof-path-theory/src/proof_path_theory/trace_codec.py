"""Versioned exchange for the Lean-refined finite trace checker.

The mathematical input and its certificate are separate, explicitly ordered
JSON arrays. There are no object keys whose duplicates could be silently lost.
At the Lean Json syntax-tree boundary the encoders have proved left inverses.
This Python implementation is conformance-tested, not universally verified.

Canonical UTF-8 bytes contain compact arrays, literal booleans, null, and
nonnegative integer tokens. One final LF is accepted for a standalone file.
No decimal coercion, boolean-as-integer coercion, duplicate node slots, or
unknown rule address is permitted. Resource rejection is not an obstruction.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable

from .extension import DerivationWitness, ExtensionResult, verify_extension_result
from .views import ProofFieldViews

PROBLEM_TAG = "proof-path/problem/1"
CERTIFICATE_TAG = "proof-path/certificate/1"
DEFAULT_MAX_BYTES = 4 * 1024 * 1024


class WireFormatError(ValueError):
    """The value does not satisfy the explicit exchange syntax."""


class WireResourceError(WireFormatError):
    """A configured resource limit was exceeded, with no mathematical verdict."""


@dataclass(frozen=True, slots=True)
class IndexedRule:
    premises: tuple[int, ...]
    conclusion: int


@dataclass(frozen=True, slots=True)
class IndexedProblem:
    node_count: int
    leaves: tuple[int, ...]
    rules: tuple[IndexedRule, ...]
    positive: tuple[int, ...]
    negative: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class IndexedWitness:
    target: int
    trace: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class IndexedCertificate:
    feasible: bool
    closure: tuple[int, ...]
    trace: tuple[int, ...]
    obstruction: IndexedWitness | None = None


@dataclass(frozen=True, slots=True)
class IndexedBinding:
    """The ordered address book must be checked against the intended snapshot."""
    problem: IndexedProblem
    node_names: tuple[str, ...]
    rule_names: tuple[str, ...]


def _nat(x: object) -> int:
    if type(x) is not int or x < 0:
        raise WireFormatError("expected a nonnegative integer, not a boolean or decimal")
    return x


def _array(x: object, length: int | None = None) -> list:
    if type(x) is not list or (length is not None and len(x) != length):
        raise WireFormatError(f"expected an array of length {length}" if length is not None else "expected an array")
    return x


def _nats(x: object) -> tuple[int, ...]:
    return tuple(_nat(v) for v in _array(x))


def problem_from_value(value: object) -> IndexedProblem:
    a = _array(value, 6)
    if a[0] != PROBLEM_TAG:
        raise WireFormatError("unsupported problem format tag")
    rules = []
    for raw in _array(a[3]):
        row = _array(raw, 2)
        rules.append(IndexedRule(_nats(row[0]), _nat(row[1])))
    return IndexedProblem(_nat(a[1]), _nats(a[2]), tuple(rules), _nats(a[4]), _nats(a[5]))


def certificate_from_value(value: object) -> IndexedCertificate:
    a = _array(value, 5)
    if a[0] != CERTIFICATE_TAG or type(a[1]) is not bool:
        raise WireFormatError("expected the certificate format tag and a literal boolean")
    obstruction = None
    if a[4] is not None:
        row = _array(a[4], 2)
        obstruction = IndexedWitness(_nat(row[0]), _nats(row[1]))
    return IndexedCertificate(a[1], _nats(a[2]), _nats(a[3]), obstruction)


def problem_to_value(p: IndexedProblem) -> list:
    if not isinstance(p, IndexedProblem):
        raise WireFormatError("expected IndexedProblem")
    result = [PROBLEM_TAG, p.node_count, list(p.leaves),
              [[list(r.premises), r.conclusion] for r in p.rules], list(p.positive), list(p.negative)]
    # Check syntax, but deliberately retain semantically invalid indices for audits.
    problem_from_value(result)
    return result


def certificate_to_value(c: IndexedCertificate) -> list:
    if not isinstance(c, IndexedCertificate):
        raise WireFormatError("expected IndexedCertificate")
    ob = None if c.obstruction is None else [c.obstruction.target, list(c.obstruction.trace)]
    result = [CERTIFICATE_TAG, c.feasible, list(c.closure), list(c.trace), ob]
    certificate_from_value(result)
    return result


def canonical_bytes(value: object) -> bytes:
    """Formatting only; callers must still decode the required record schema."""
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("ascii")
    except (ValueError, TypeError, RecursionError) as exc:
        raise WireFormatError("not a finite JSON value") from exc


def _reject_float(_: str) -> None:
    raise WireFormatError("decimal and exponent tokens are outside the canonical exchange format")


def _reject_object(_: list[tuple[str, object]]) -> None:
    raise WireFormatError("objects are not part of the positional exchange schema")


def _read_value(data: str | bytes, max_bytes: int) -> object:
    if type(max_bytes) is not int or max_bytes < 1:
        raise ValueError("max_bytes must be a positive integer")
    if type(data) not in (str, bytes):
        raise WireFormatError("expected UTF-8 bytes or text")
    try:
        raw = data.encode("utf-8") if type(data) is str else data
    except UnicodeError as exc:
        raise WireFormatError("invalid Unicode input") from exc
    if len(raw) > max_bytes:
        raise WireResourceError("exchange exceeds max_bytes; no mathematical verdict")
    # Permit the ordinary newline produced by text-file writers, but no
    # internal whitespace, alternate number spellings, or multiple records.
    body = raw[:-1] if raw.endswith(b"\n") else raw
    try:
        value = json.loads(body.decode("utf-8"), parse_float=_reject_float,
                           parse_constant=_reject_float, object_pairs_hook=_reject_object)
    except WireFormatError:
        raise
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise WireFormatError("invalid or excessively nested JSON") from exc
    if canonical_bytes(value) != body:
        raise WireFormatError("noncanonical exchange bytes")
    return value


def dumps_problem(p: IndexedProblem) -> bytes:
    return canonical_bytes(problem_to_value(p))


def loads_problem(data: str | bytes, *, max_bytes: int = DEFAULT_MAX_BYTES) -> IndexedProblem:
    return problem_from_value(_read_value(data, max_bytes))


def dumps_trace_certificate(c: IndexedCertificate) -> bytes:
    return canonical_bytes(certificate_to_value(c))


def loads_trace_certificate(data: str | bytes, *, max_bytes: int = DEFAULT_MAX_BYTES) -> IndexedCertificate:
    return certificate_from_value(_read_value(data, max_bytes))


def _nat_tuple(xs: object) -> bool:
    return type(xs) is tuple and all(type(x) is int and x >= 0 for x in xs)


def _node_tuple(xs: object, count: int) -> bool:
    return _nat_tuple(xs) and all(x < count for x in xs) and len(set(xs)) == len(xs)


def valid_indexed_problem(p: IndexedProblem) -> bool:
    if not isinstance(p, IndexedProblem) or type(p.node_count) is not int or p.node_count < 0 or type(p.rules) is not tuple:
        return False
    return (all(_node_tuple(xs, p.node_count) for xs in (p.leaves, p.positive, p.negative))
            and all(isinstance(r, IndexedRule) and _node_tuple(r.premises, p.node_count)
                    and type(r.conclusion) is int and 0 <= r.conclusion < p.node_count for r in p.rules))


def valid_indexed_certificate(p: IndexedProblem, c: IndexedCertificate) -> bool:
    if not isinstance(c, IndexedCertificate) or type(c.feasible) is not bool:
        return False
    def trace_ok(xs: object) -> bool:
        return _nat_tuple(xs) and all(i < len(p.rules) for i in xs)
    if not _node_tuple(c.closure, p.node_count) or not trace_ok(c.trace):
        return False
    w = c.obstruction
    return w is None or (isinstance(w, IndexedWitness) and type(w.target) is int
                         and 0 <= w.target < p.node_count and trace_ok(w.trace))


def replay_indexed(p: IndexedProblem, trace: tuple[int, ...], *, strict: bool,
                   known: tuple[int, ...] | None = None) -> tuple[int, ...] | None:
    """List semantics matching Trace.replay; safe failure for malformed indices."""
    if not valid_indexed_problem(p) or not _nat_tuple(trace) or type(strict) is not bool:
        return None
    state = p.leaves + p.positive if known is None else known
    if not _nat_tuple(state) or any(v >= p.node_count for v in state):
        return None
    for i in trace:
        if i >= len(p.rules):
            return None
        r = p.rules[i]
        if not all(v in state for v in r.premises) or (strict and r.conclusion in state):
            return None
        state = (r.conclusion,) + state
    return state


def check_indexed_witness(p: IndexedProblem, w: IndexedWitness) -> bool:
    if (not valid_indexed_problem(p) or not isinstance(w, IndexedWitness)
            or type(w.target) is not int or not 0 <= w.target < p.node_count):
        return False
    out = replay_indexed(p, w.trace, strict=False)
    return out is not None and w.target in out and w.target in p.negative


def check_indexed_certificate(p: IndexedProblem, c: IndexedCertificate) -> bool:
    """Independent checking: no call to solve_extension or its result checker."""
    if not valid_indexed_problem(p) or not valid_indexed_certificate(p, c):
        return False
    out = replay_indexed(p, c.trace, strict=True)
    if out is None or set(out) != set(c.closure):
        return False
    if not all(v in c.closure for v in p.leaves):
        return False
    if not all(not all(v in c.closure for v in r.premises) or r.conclusion in c.closure for r in p.rules):
        return False
    if c.feasible:
        return c.obstruction is None and not any(v in p.negative for v in c.closure)
    return c.obstruction is not None and check_indexed_witness(p, c.obstruction)


def check_trace_json(problem_data: str | bytes, certificate_data: str | bytes, *,
                     max_bytes: int = DEFAULT_MAX_BYTES) -> bool:
    """Malformed exchange raises WireFormatError; a mathematical checker rejection
    returns False. In neither case is rejection a proof of infeasibility."""
    p = loads_problem(problem_data, max_bytes=max_bytes)
    c = loads_trace_certificate(certificate_data, max_bytes=max_bytes)
    return check_indexed_certificate(p, c)


def index_problem(views: ProofFieldViews, *, positive: Iterable[str] = (),
                  negative: Iterable[str] = ()) -> IndexedBinding:
    """Assign stable positions to the existing certified-rule snapshot.

    Node names are sorted; rule positions follow the snapshot's explicit order.
    Identical rule rows are not merged. The binding records the names lost by
    indexing and must accompany any interpretation in the original vocabulary.
    """
    if not isinstance(views, ProofFieldViews):
        raise ValueError("expected a ProofFieldViews snapshot")
    if any(type(v) is not str for v in views.nodes):
        raise ValueError("node identifiers must be strings")
    names = tuple(sorted(views.nodes))
    slot = {v: i for i, v in enumerate(names)}
    rule_names = tuple(r.id for r in views.rules)
    if any(type(r) is not str for r in rule_names) or len(set(rule_names)) != len(rule_names):
        raise ValueError("rule identifiers must be unique strings")
    def slots(values: Iterable[str]) -> tuple[int, ...]:
        values = tuple(values)
        if any(type(v) is not str or v not in slot for v in values):
            raise ValueError("unknown node identifier")
        return tuple(sorted({slot[v] for v in values}))
    rows = tuple(IndexedRule(slots(r.premises), slots((r.conclusion,))[0]) for r in views.rules)
    p = IndexedProblem(len(names), slots(views.leaves), rows, slots(positive), slots(negative))
    if not valid_indexed_problem(p):
        raise ValueError("invalid indexed snapshot")
    return IndexedBinding(p, names, rule_names)


def index_certificate(binding: IndexedBinding, result: ExtensionResult) -> IndexedCertificate:
    """Translate a named result without claiming it is valid; run the checker next."""
    if not isinstance(binding, IndexedBinding) or not isinstance(result, ExtensionResult):
        raise ValueError("expected a binding and ExtensionResult")
    nslot = {v: i for i, v in enumerate(binding.node_names)}
    rslot = {v: i for i, v in enumerate(binding.rule_names)}
    try:
        if type(result.closure) is not frozenset or type(result.rule_ids) is not tuple:
            raise ValueError("invalid result containers")
        closure = tuple(sorted(nslot[v] for v in result.closure))
        trace = tuple(rslot[v] for v in result.rule_ids)
        obstruction = None
        if result.obstruction is not None:
            w = result.obstruction
            if not isinstance(w, DerivationWitness) or type(w.rule_ids) is not tuple:
                raise ValueError("invalid witness container")
            obstruction = IndexedWitness(nslot[w.target], tuple(rslot[v] for v in w.rule_ids))
    except (KeyError, TypeError) as exc:
        raise ValueError("result refers to an unknown node or rule") from exc
    return IndexedCertificate(result.feasible, closure, trace, obstruction)


def export_trace_exchange(views: ProofFieldViews, result: ExtensionResult, *,
                          positive: Iterable[str] = (), negative: Iterable[str] = ()) -> tuple[IndexedBinding, bytes, bytes]:
    """Export only a result accepted by both independent finite checkers."""
    s, n = tuple(positive), tuple(negative)
    if not verify_extension_result(views, positive=s, negative=n, result=result):
        raise ValueError("the named result failed its independent checker")
    binding = index_problem(views, positive=s, negative=n)
    cert = index_certificate(binding, result)
    if not check_indexed_certificate(binding.problem, cert):
        raise ValueError("the indexed result failed its independent checker")
    return binding, dumps_problem(binding.problem), dumps_trace_certificate(cert)
