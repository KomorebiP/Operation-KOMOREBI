"""Exact finite semantic checkpoints for the OSL / Neuralese research edition.

This is a finite-state reference bridge, not a decoder of arbitrary neural states.
No network, code evaluation, credentials, external effects, or training are used.
Hashes bind bytes; they do not authenticate principals or establish world truth.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

SCHEMA = "komorebi.finite-semantic-interface.v1"
SCOPE = "all_states_all_words_of_declared_finite_machine"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: Any, low: int, high: int) -> bool:
    return type(value) is int and low <= value < high


@dataclass(frozen=True)
class FiniteMachine:
    """A completely declared deterministic Moore machine with immutable tables."""
    states: tuple[str, ...]
    alphabet: tuple[str, ...]
    transitions: tuple[tuple[int, ...], ...]  # action-major
    observations: tuple[str, ...]

    def __post_init__(self) -> None:
        n = len(self.states)
        require(0 < n <= 256, "reference profile requires 1..256 states")
        require(type(self.states) is tuple and type(self.alphabet) is tuple,
                "state and alphabet collections must be tuples")
        require(all(type(x) is str and x for x in self.states + self.alphabet), "names must be nonempty strings")
        require(len(set(self.states)) == n, "state names must be unique")
        require(0 < len(self.alphabet) <= 32 and len(set(self.alphabet)) == len(self.alphabet), "invalid alphabet")
        require(type(self.transitions) is tuple and len(self.transitions) == len(self.alphabet), "invalid action table")
        require(all(type(t) is tuple and len(t) == n and all(integer(j, 0, n) for j in t)
                    for t in self.transitions), "transitions must be total and in range")
        require(type(self.observations) is tuple and len(self.observations) == n
                and all(type(x) is str for x in self.observations), "invalid observation table")

    def payload(self) -> dict[str, Any]:
        return {"states": list(self.states), "alphabet": list(self.alphabet),
                "transitions": [list(t) for t in self.transitions], "observations": list(self.observations)}

    @property
    def fingerprint(self) -> str:
        return digest(self.payload())

    def step(self, state: int, action: str) -> int:
        require(integer(state, 0, len(self.states)), "state outside declared domain")
        require(action in self.alphabet, "action outside declared alphabet")
        return self.transitions[self.alphabet.index(action)][state]


def labels(signatures: tuple[Any, ...]) -> tuple[int, ...]:
    """Canonical class numbers ordered by first member; no semantic labels needed."""
    seen: dict[Any, int] = {}
    answer = []
    for sig in signatures:
        if sig not in seen:
            seen[sig] = len(seen)
        answer.append(seen[sig])
    return tuple(answer)


def horizon_partition(machine: FiniteMachine, horizon: int) -> tuple[int, ...]:
    require(integer(horizon, 0, 10001), "invalid finite horizon")
    q = labels(machine.observations)
    for _ in range(horizon):
        q = labels(tuple((machine.observations[s], *(q[t[s]] for t in machine.transitions))
                         for s in range(len(machine.states))))
    return q


def minimal_partition(machine: FiniteMachine) -> tuple[int, ...]:
    q = labels(machine.observations)
    for _ in range(len(machine.states)):
        new = labels(tuple((machine.observations[s], *(q[t[s]] for t in machine.transitions))
                           for s in range(len(machine.states))))
        if new == q:
            return q
        q = new
    raise AssertionError("finite partition refinement did not stabilize")


def make_certificate(machine: FiniteMachine) -> dict[str, Any]:
    q = minimal_partition(machine)
    reps = [q.index(k) for k in range(max(q) + 1)]
    body = {"schema": SCHEMA, "scope": SCOPE, "machine_digest": machine.fingerprint,
            "partition": list(q), "observations": [machine.observations[s] for s in reps],
            "transitions": [[q[t[s]] for s in reps] for t in machine.transitions]}
    return {**body, "certificate_digest": digest(body)}


def verify_certificate(machine: FiniteMachine, certificate: Any) -> bool:
    """Check local equations, not a hash alone and not the producer's search trace.

    Certifies a sound quotient, not minimality: a finer valid partition is allowed.
    Malformed or stale evidence returns False. The machine table is a trust root.
    """
    try:
        keys = {"schema", "scope", "machine_digest", "partition", "observations", "transitions", "certificate_digest"}
        require(type(certificate) is dict and set(certificate) == keys, "certificate schema")
        c = certificate
        require(c["schema"] == SCHEMA and c["scope"] == SCOPE, "unsupported scope")
        require(c["machine_digest"] == machine.fingerprint, "stale machine")
        body = {k: v for k, v in c.items() if k != "certificate_digest"}
        require(c["certificate_digest"] == digest(body), "digest mismatch")
        q, obs, ts = c["partition"], c["observations"], c["transitions"]
        n = len(machine.states)
        require(type(q) is list and len(q) == n and all(integer(k, 0, n) for k in q), "partition domain")
        k = max(q) + 1
        require(set(q) == set(range(k)), "class range")
        require(type(obs) is list and len(obs) == k and all(type(x) is str for x in obs), "output classes")
        require(type(ts) is list and len(ts) == len(machine.alphabet), "quotient alphabet")
        require(all(type(t) is list and len(t) == k and all(integer(j, 0, k) for j in t) for t in ts), "quotient transitions")
        for s in range(n):
            require(obs[q[s]] == machine.observations[s], "observation not preserved")
            for action, t in enumerate(machine.transitions):
                require(q[t[s]] == ts[action][q[s]], "transition not preserved")
        return True
    except (ValueError, TypeError, KeyError, IndexError, OverflowError):
        return False


def checkpoint(machine: FiniteMachine, certificate: dict[str, Any], state: int) -> dict[str, Any]:
    require(verify_certificate(machine, certificate), "invalid quotient certificate")
    require(integer(state, 0, len(machine.states)), "invalid state")
    body = {"schema": SCHEMA + ".checkpoint", "machine_digest": machine.fingerprint,
            "certificate_digest": certificate["certificate_digest"], "scope": SCOPE,
            "class": certificate["partition"][state]}
    return {**body, "checkpoint_digest": digest(body)}


def restore(machine: FiniteMachine, certificate: dict[str, Any], saved: Any) -> int:
    require(verify_certificate(machine, certificate), "invalid quotient certificate")
    keys = {"schema", "machine_digest", "certificate_digest", "scope", "class", "checkpoint_digest"}
    require(type(saved) is dict and set(saved) == keys, "invalid checkpoint schema")
    require(saved["schema"] == SCHEMA + ".checkpoint" and saved["scope"] == SCOPE, "invalid checkpoint scope")
    require(saved["machine_digest"] == machine.fingerprint, "checkpoint is for another machine")
    require(saved["certificate_digest"] == certificate["certificate_digest"], "checkpoint is for another quotient")
    require(saved["checkpoint_digest"] == digest({k:v for k,v in saved.items() if k != "checkpoint_digest"}), "checkpoint digest mismatch")
    q = saved["class"]
    require(integer(q, 0, len(certificate["observations"])), "invalid checkpoint class")
    return q


def quotient_step(machine: FiniteMachine, certificate: dict[str, Any], q: int, action: str) -> int:
    require(verify_certificate(machine, certificate), "invalid quotient certificate")
    require(integer(q, 0, len(certificate["observations"])), "invalid quotient state")
    require(action in machine.alphabet, "action outside certified alphabet")
    return certificate["transitions"][machine.alphabet.index(action)][q]


def emit_osl(machine: FiniteMachine, certificate: Any, state: int) -> str:
    """Render a scoped finite-checker decision; it is NOT neural semantic inference.

    OSL attestations are symbolic trust declarations made by this adapter. The
    external checker is a declared trust root, not cryptographic authentication.
    """
    valid = verify_certificate(machine, certificate)
    if valid:
        payload = checkpoint(machine, certificate, state)
    else:
        payload = {"decision": "quarantine", "reason": "no valid finite quotient certificate"}
    quoted = json.dumps(canonical(payload), ensure_ascii=True)
    lines = ["module finite_semantic_checkpoint", "lineage L_finite", "agent Bridge lineage L_finite",
             f'neural_propose checkpoint to Bridge feature finite_quotient content {quoted} confidence {1.0 if valid else 0.0}']
    if valid:
        lines += ["attest origin checkpoint by Bridge lineage L_finite as origin",
                  "attest relevance checkpoint by Bridge for planning as relevance",
                  'admit checkpoint by Bridge using ["origin","relevance"]',
                  "assert packet checkpoint status admitted"]
    else:
        lines += ["assert packet checkpoint status provisional", "assert packet checkpoint quarantined_by Bridge true"]
    return "\n".join(lines + ["verify_receipts", "show", ""])


def d4_fixture() -> FiniteMachine:
    """D4 regular action on eight semantic states plus one unobserved private bit."""
    states = tuple(f"a{a}b{b}u{u}" for a in range(4) for b in range(2) for u in range(2))
    def idx(a: int,b: int,u: int) -> int: return (a % 4)*4+b*2+u
    r = tuple(idx(a+1,b,u) for a in range(4) for b in range(2) for u in range(2))
    f = tuple(idx(-a,1-b,u) for a in range(4) for b in range(2) for u in range(2))
    u = tuple(idx(a,b,1-z) for a in range(4) for b in range(2) for z in range(2))
    return FiniteMachine(states,("r","f","private"),(r,f,u),tuple(f"{a},{b}" for a in range(4) for b in range(2) for u in range(2)))
