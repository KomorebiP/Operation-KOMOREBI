#!/usr/bin/env python3
"""Independent finite metatheory model for OSL-Core 0.3.

This module does not execute OSL source programs.  It defines five deliberately
small transition systems that isolate the safety obligations behind provenance,
capabilities, temporal contracts, transactions, and session protocols.  Each
system is finite, so its complete reachable-state closure can be enumerated.

The resulting certificate is stronger than example testing but weaker than a
proof-assistant mechanization of the full language.  It establishes the stated
properties only for the explicit finite models below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Hashable, Iterable


AGENTS = ("A", "B")


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Outcome:
    status: str  # stepped | rejected | stuck
    state: Hashable
    reason: str = ""


@dataclass(frozen=True)
class ModelCertificate:
    name: str
    state_count: int
    transition_attempt_count: int
    stepped_transition_count: int
    rejected_transition_count: int
    max_shortest_depth: int
    fixpoint_reached: bool
    progress_with_safe_rejection: bool
    static_dynamic_agreement: bool
    preservation: bool
    invariant_checks: dict[str, bool]
    special_checks: dict[str, bool]
    counterexamples: tuple[dict[str, Any], ...]
    reachable_state_digest: str
    certificate_digest: str


def _certificate_payload(cert: ModelCertificate) -> dict[str, Any]:
    payload = asdict(cert)
    payload.pop("certificate_digest", None)
    return payload


def explore_finite_model(
    *,
    name: str,
    initial: Hashable,
    commands: tuple[str, ...],
    admissible: Callable[[Hashable, str], bool],
    may_reject_when_admissible: Callable[[str], bool],
    step: Callable[[Hashable, str], Outcome],
    well_formed: Callable[[Hashable], bool],
    invariants: dict[str, Callable[[Hashable], bool]],
    special_transition_checks: dict[
        str, Callable[[Hashable, str, Outcome], bool]
    ] | None = None,
    max_states: int = 250_000,
) -> ModelCertificate:
    """Enumerate the complete reachable-state closure of one finite model."""

    if not well_formed(initial):
        raise ValueError(f"initial state for {name} is not well formed")

    queue: deque[Hashable] = deque([initial])
    depths: dict[Hashable, int] = {initial: 0}
    counterexamples: list[dict[str, Any]] = []
    transition_attempts = 0
    stepped = 0
    rejected = 0
    progress_ok = True
    agreement_ok = True
    preservation_ok = True
    invariant_results = {key: True for key in invariants}
    special_results = {
        key: True for key in (special_transition_checks or {})
    }

    while queue:
        state = queue.popleft()
        depth = depths[state]
        for inv_name, predicate in invariants.items():
            if not predicate(state):
                invariant_results[inv_name] = False
                counterexamples.append(
                    {
                        "property": inv_name,
                        "state": _jsonable(state),
                        "depth": depth,
                    }
                )

        for command in commands:
            transition_attempts += 1
            static_ok = bool(admissible(state, command))
            outcome = step(state, command)
            if outcome.status == "stuck":
                progress_ok = False
                counterexamples.append(
                    {
                        "property": "progress_with_safe_rejection",
                        "state": _jsonable(state),
                        "command": command,
                        "reason": outcome.reason,
                    }
                )
                continue
            if outcome.status == "stepped":
                stepped += 1
            elif outcome.status == "rejected":
                rejected += 1
            else:
                progress_ok = False
                counterexamples.append(
                    {
                        "property": "known_outcome_status",
                        "state": _jsonable(state),
                        "command": command,
                        "status": outcome.status,
                    }
                )
                continue

            if static_ok and not may_reject_when_admissible(command):
                if outcome.status != "stepped":
                    agreement_ok = False
                    counterexamples.append(
                        {
                            "property": "static_dynamic_agreement",
                            "state": _jsonable(state),
                            "command": command,
                            "expected": "stepped",
                            "observed": outcome.status,
                            "reason": outcome.reason,
                        }
                    )
            elif not static_ok:
                if outcome.status != "rejected" or outcome.state != state:
                    agreement_ok = False
                    counterexamples.append(
                        {
                            "property": "safe_static_rejection",
                            "state": _jsonable(state),
                            "command": command,
                            "observed_state": _jsonable(outcome.state),
                            "observed": outcome.status,
                        }
                    )

            if not well_formed(outcome.state):
                preservation_ok = False
                counterexamples.append(
                    {
                        "property": "preservation",
                        "state": _jsonable(state),
                        "command": command,
                        "outcome_state": _jsonable(outcome.state),
                        "outcome": outcome.status,
                    }
                )

            for check_name, checker in (special_transition_checks or {}).items():
                if not checker(state, command, outcome):
                    special_results[check_name] = False
                    counterexamples.append(
                        {
                            "property": check_name,
                            "state": _jsonable(state),
                            "command": command,
                            "outcome_state": _jsonable(outcome.state),
                            "outcome": outcome.status,
                        }
                    )

            # A declared rejection can still perform a safe rollback.  Its
            # resulting state is therefore part of the reachable closure.
            successor = outcome.state
            if successor not in depths:
                if len(depths) >= max_states:
                    raise RuntimeError(
                        f"{name} exceeded max_states={max_states}; model may not be finite"
                    )
                depths[successor] = depth + 1
                queue.append(successor)

    states_sorted = sorted(canonical_json(state) for state in depths)
    payload = {
        "name": name,
        "state_count": len(depths),
        "transition_attempt_count": transition_attempts,
        "stepped_transition_count": stepped,
        "rejected_transition_count": rejected,
        "max_shortest_depth": max(depths.values()),
        "fixpoint_reached": True,
        "progress_with_safe_rejection": progress_ok,
        "static_dynamic_agreement": agreement_ok,
        "preservation": preservation_ok,
        "invariant_checks": invariant_results,
        "special_checks": special_results,
        "counterexamples": tuple(counterexamples),
        "reachable_state_digest": digest(states_sorted),
    }
    cert = ModelCertificate(**payload, certificate_digest=digest(payload))
    return cert


# ---------------------------------------------------------------------------
# Provenance and autobiographical ownership model
# ---------------------------------------------------------------------------


class Provenance(str, Enum):
    NONE = "none"
    OBSERVED = "observed"
    COMMUNICATED = "communicated"
    SIMULATED = "simulated"
    INJECTED = "injected"


class MemoryClass(str, Enum):
    OBSERVED = "observed"
    COMMUNICATED = "communicated"
    SIMULATED = "simulated"


@dataclass(frozen=True)
class MemoryFact:
    owner: str
    memory_class: MemoryClass
    source: str | None
    provenance_at_write: Provenance
    observation_token_at_write: str | None


@dataclass(frozen=True)
class ProvenanceState:
    provenance: Provenance = Provenance.NONE
    source: str | None = None
    holder: str | None = None
    accessible: bool = False
    bound: bool = False
    quarantined: bool = False
    endorsed: bool = False
    authorized: bool = False
    observation_token: str | None = None
    memory_a: MemoryFact | None = None
    memory_b: MemoryFact | None = None


def _memory_of(state: ProvenanceState, agent: str) -> MemoryFact | None:
    return state.memory_a if agent == "A" else state.memory_b


def _replace_memory(
    state: ProvenanceState, agent: str, record: MemoryFact
) -> ProvenanceState:
    payload = asdict(state)
    payload["provenance"] = state.provenance
    payload["memory_a"] = state.memory_a
    payload["memory_b"] = state.memory_b
    payload["memory_a" if agent == "A" else "memory_b"] = record
    return ProvenanceState(**payload)


def provenance_commands() -> tuple[str, ...]:
    commands: list[str] = []
    for agent in AGENTS:
        commands.extend(
            [
                f"observe:{agent}",
                f"simulate:{agent}",
                f"inject:{agent}",
                f"endorse:{agent}",
                f"authorize:{agent}",
                f"quarantine:{agent}",
                f"write_observed:{agent}",
                f"write_communicated:{agent}",
                f"write_simulated:{agent}",
            ]
        )
    commands.extend(["communicate:A:B", "communicate:B:A"])
    return tuple(commands)


def provenance_well_formed(state: ProvenanceState) -> bool:
    if state.provenance == Provenance.NONE:
        if any(
            [
                state.source is not None,
                state.holder is not None,
                state.accessible,
                state.bound,
                state.quarantined,
                state.endorsed,
                state.authorized,
                state.observation_token is not None,
            ]
        ):
            return False
    else:
        if state.holder not in AGENTS or not state.accessible or not state.bound:
            return False
    if state.provenance == Provenance.OBSERVED:
        if state.source not in AGENTS or state.observation_token != state.source:
            return False
    elif state.provenance == Provenance.COMMUNICATED:
        if state.source not in AGENTS or state.observation_token is not None:
            return False
    elif state.provenance == Provenance.SIMULATED:
        if state.source != state.holder or state.observation_token is not None:
            return False
    elif state.provenance == Provenance.INJECTED:
        if state.source is not None or state.observation_token is not None:
            return False
        if not state.quarantined:
            return False
    if state.endorsed and state.quarantined:
        return False
    for owner in AGENTS:
        record = _memory_of(state, owner)
        if record is None:
            continue
        if record.owner != owner:
            return False
        if record.memory_class == MemoryClass.OBSERVED:
            if not (
                record.provenance_at_write == Provenance.OBSERVED
                and record.source == owner
                and record.observation_token_at_write == owner
            ):
                return False
        elif record.memory_class == MemoryClass.COMMUNICATED:
            if record.provenance_at_write != Provenance.COMMUNICATED:
                return False
        elif record.memory_class == MemoryClass.SIMULATED:
            if not (
                record.provenance_at_write == Provenance.SIMULATED
                and record.source == owner
            ):
                return False
    return True


def provenance_admissible(state: ProvenanceState, command: str) -> bool:
    parts = command.split(":")
    op = parts[0]
    if op in {"observe", "simulate", "inject"}:
        return parts[1] in AGENTS
    if op == "communicate":
        sender, receiver = parts[1], parts[2]
        return bool(
            sender != receiver
            and state.provenance != Provenance.NONE
            and state.holder == sender
            and state.accessible
        )
    agent = parts[1]
    if op == "endorse":
        return bool(
            state.holder == agent
            and state.accessible
            and not state.quarantined
        )
    if op == "authorize":
        return bool(state.holder == agent and state.accessible)
    if op == "quarantine":
        return state.holder == agent and state.provenance != Provenance.NONE
    if op == "write_observed":
        return bool(
            state.holder == agent
            and state.accessible
            and state.bound
            and not state.quarantined
            and state.provenance == Provenance.OBSERVED
            and state.source == agent
            and state.observation_token == agent
        )
    if op == "write_communicated":
        return bool(
            state.holder == agent
            and state.accessible
            and state.bound
            and not state.quarantined
            and state.provenance == Provenance.COMMUNICATED
        )
    if op == "write_simulated":
        return bool(
            state.holder == agent
            and state.accessible
            and state.bound
            and not state.quarantined
            and state.provenance == Provenance.SIMULATED
            and state.source == agent
        )
    return False


def provenance_step(state: ProvenanceState, command: str) -> Outcome:
    if not provenance_admissible(state, command):
        return Outcome("rejected", state, "premise not satisfied")
    parts = command.split(":")
    op = parts[0]
    if op in {"observe", "simulate", "inject"}:
        agent = parts[1]
        memory_a, memory_b = state.memory_a, state.memory_b
        if op == "observe":
            successor = ProvenanceState(
                provenance=Provenance.OBSERVED,
                source=agent,
                holder=agent,
                accessible=True,
                bound=True,
                observation_token=agent,
                memory_a=memory_a,
                memory_b=memory_b,
            )
        elif op == "simulate":
            successor = ProvenanceState(
                provenance=Provenance.SIMULATED,
                source=agent,
                holder=agent,
                accessible=True,
                bound=True,
                memory_a=memory_a,
                memory_b=memory_b,
            )
        else:
            successor = ProvenanceState(
                provenance=Provenance.INJECTED,
                source=None,
                holder=agent,
                accessible=True,
                bound=True,
                quarantined=True,
                memory_a=memory_a,
                memory_b=memory_b,
            )
        return Outcome("stepped", successor)
    if op == "communicate":
        receiver = parts[2]
        return Outcome(
            "stepped",
            ProvenanceState(
                provenance=Provenance.COMMUNICATED,
                source=state.source or state.holder,
                holder=receiver,
                accessible=True,
                bound=True,
                memory_a=state.memory_a,
                memory_b=state.memory_b,
            ),
        )
    agent = parts[1]
    payload = asdict(state)
    payload["provenance"] = state.provenance
    payload["memory_a"] = state.memory_a
    payload["memory_b"] = state.memory_b
    if op == "endorse":
        payload["endorsed"] = True
        return Outcome("stepped", ProvenanceState(**payload))
    if op == "authorize":
        payload["authorized"] = True
        return Outcome("stepped", ProvenanceState(**payload))
    if op == "quarantine":
        payload["quarantined"] = True
        payload["endorsed"] = False
        return Outcome("stepped", ProvenanceState(**payload))
    memory_class = {
        "write_observed": MemoryClass.OBSERVED,
        "write_communicated": MemoryClass.COMMUNICATED,
        "write_simulated": MemoryClass.SIMULATED,
    }[op]
    record = MemoryFact(
        owner=agent,
        memory_class=memory_class,
        source=state.source,
        provenance_at_write=state.provenance,
        observation_token_at_write=state.observation_token,
    )
    return Outcome("stepped", _replace_memory(state, agent, record))


def _no_forged_observed_memory(state: ProvenanceState) -> bool:
    for owner in AGENTS:
        record = _memory_of(state, owner)
        if record is None or record.memory_class != MemoryClass.OBSERVED:
            continue
        if not (
            record.provenance_at_write == Provenance.OBSERVED
            and record.source == owner
            and record.observation_token_at_write == owner
        ):
            return False
    return True


def _simulated_not_observed(state: ProvenanceState) -> bool:
    for owner in AGENTS:
        record = _memory_of(state, owner)
        if record is None:
            continue
        if (
            record.provenance_at_write == Provenance.SIMULATED
            and record.memory_class == MemoryClass.OBSERVED
        ):
            return False
    return True


def _communicated_not_observed(state: ProvenanceState) -> bool:
    for owner in AGENTS:
        record = _memory_of(state, owner)
        if record is None:
            continue
        if (
            record.provenance_at_write == Provenance.COMMUNICATED
            and record.memory_class == MemoryClass.OBSERVED
        ):
            return False
    return True


# ---------------------------------------------------------------------------
# Capability model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapabilityState:
    issued_a: int = 0
    remaining_a: int = 0
    consumed_a: int = 0
    revoked_a: bool = False
    planned_a: bool = False
    issued_b: int = 0
    remaining_b: int = 0
    consumed_b: int = 0
    revoked_b: bool = False
    planned_b: bool = False


def _cap_fields(agent: str) -> tuple[str, str, str, str, str]:
    suffix = agent.lower()
    return (
        f"issued_{suffix}",
        f"remaining_{suffix}",
        f"consumed_{suffix}",
        f"revoked_{suffix}",
        f"planned_{suffix}",
    )


def capability_commands() -> tuple[str, ...]:
    commands: list[str] = []
    for agent in AGENTS:
        commands.extend(
            [
                f"grant1:{agent}",
                f"grant2:{agent}",
                f"plan:{agent}",
                f"execute:{agent}",
                f"revoke:{agent}",
            ]
        )
    return tuple(commands)


def capability_well_formed(state: CapabilityState) -> bool:
    for agent in AGENTS:
        issued_f, remaining_f, consumed_f, revoked_f, _ = _cap_fields(agent)
        issued = getattr(state, issued_f)
        remaining = getattr(state, remaining_f)
        consumed = getattr(state, consumed_f)
        revoked = getattr(state, revoked_f)
        if not (0 <= issued <= 2 and 0 <= remaining <= 2 and 0 <= consumed <= 2):
            return False
        if consumed > issued or remaining > issued:
            return False
        if revoked:
            if remaining != 0:
                return False
        elif remaining + consumed != issued:
            return False
    return True


def capability_admissible(state: CapabilityState, command: str) -> bool:
    op, agent = command.split(":")
    issued_f, remaining_f, _, revoked_f, planned_f = _cap_fields(agent)
    if op in {"grant1", "grant2", "plan"}:
        return True
    if op == "revoke":
        return getattr(state, issued_f) > 0 and not getattr(state, revoked_f)
    if op == "execute":
        return bool(
            getattr(state, planned_f)
            and not getattr(state, revoked_f)
            and getattr(state, remaining_f) > 0
        )
    return False


def capability_step(state: CapabilityState, command: str) -> Outcome:
    if not capability_admissible(state, command):
        return Outcome("rejected", state, "capability premise not satisfied")
    op, agent = command.split(":")
    issued_f, remaining_f, consumed_f, revoked_f, planned_f = _cap_fields(agent)
    payload = asdict(state)
    if op in {"grant1", "grant2"}:
        budget = int(op[-1])
        payload[issued_f] = budget
        payload[remaining_f] = budget
        payload[consumed_f] = 0
        payload[revoked_f] = False
    elif op == "plan":
        payload[planned_f] = True
    elif op == "revoke":
        payload[remaining_f] = 0
        payload[revoked_f] = True
    elif op == "execute":
        payload[remaining_f] -= 1
        payload[consumed_f] += 1
    return Outcome("stepped", CapabilityState(**payload))


def _capability_confinement(state: CapabilityState) -> bool:
    for agent in AGENTS:
        issued_f, _, consumed_f, _, _ = _cap_fields(agent)
        if getattr(state, consumed_f) > getattr(state, issued_f):
            return False
    return True


def _execute_consumes_one(
    state: CapabilityState, command: str, outcome: Outcome
) -> bool:
    if not command.startswith("execute:") or outcome.status != "stepped":
        return True
    agent = command.split(":")[1]
    _, remaining_f, consumed_f, _, _ = _cap_fields(agent)
    successor = outcome.state
    assert isinstance(successor, CapabilityState)
    return bool(
        getattr(successor, remaining_f) == getattr(state, remaining_f) - 1
        and getattr(successor, consumed_f) == getattr(state, consumed_f) + 1
    )


# ---------------------------------------------------------------------------
# Temporal feedback contract model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContractState:
    step: int = 0
    pending_due: int | None = None
    finalized: bool = False


def contract_commands() -> tuple[str, ...]:
    return ("execute", "feedback", "advance", "finalize")


def contract_well_formed(state: ContractState) -> bool:
    if not (0 <= state.step <= 5):
        return False
    if state.pending_due is not None:
        if not (state.step <= state.pending_due <= 5):
            return False
    if state.finalized and state.pending_due is not None:
        return False
    return True


def contract_admissible(state: ContractState, command: str) -> bool:
    if state.finalized:
        return False
    if command == "execute":
        return state.pending_due is None and state.step <= 3
    if command == "feedback":
        return state.pending_due is not None
    if command == "advance":
        if state.step >= 5:
            return False
        next_step = state.step + 1
        return state.pending_due is None or next_step <= state.pending_due
    if command == "finalize":
        return state.pending_due is None
    return False


def contract_step(state: ContractState, command: str) -> Outcome:
    if not contract_admissible(state, command):
        return Outcome("rejected", state, "temporal contract would be violated")
    if command == "execute":
        return Outcome(
            "stepped",
            ContractState(step=state.step, pending_due=state.step + 2),
        )
    if command == "feedback":
        return Outcome("stepped", ContractState(step=state.step))
    if command == "advance":
        return Outcome(
            "stepped",
            ContractState(step=state.step + 1, pending_due=state.pending_due),
        )
    if command == "finalize":
        return Outcome("stepped", ContractState(step=state.step, finalized=True))
    return Outcome("stuck", state, "unknown command")


def _no_overdue_accepted_state(state: ContractState) -> bool:
    return state.pending_due is None or state.step <= state.pending_due


# ---------------------------------------------------------------------------
# Transaction model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransactionState:
    store_value: int = 0
    active: bool = False
    checkpoint: int | None = None


def transaction_commands() -> tuple[str, ...]:
    return ("begin", "write0", "write1", "commit", "rollback", "fail")


def transaction_well_formed(state: TransactionState) -> bool:
    if state.store_value not in {0, 1}:
        return False
    return state.active == (state.checkpoint is not None)


def transaction_admissible(state: TransactionState, command: str) -> bool:
    if command == "begin":
        return not state.active
    if command in {"write0", "write1", "commit", "rollback", "fail"}:
        return state.active
    return False


def transaction_step(state: TransactionState, command: str) -> Outcome:
    if not transaction_admissible(state, command):
        return Outcome("rejected", state, "transaction premise not satisfied")
    if command == "begin":
        return Outcome(
            "stepped",
            TransactionState(
                store_value=state.store_value,
                active=True,
                checkpoint=state.store_value,
            ),
        )
    if command == "write0":
        return Outcome(
            "stepped",
            TransactionState(store_value=0, active=True, checkpoint=state.checkpoint),
        )
    if command == "write1":
        return Outcome(
            "stepped",
            TransactionState(store_value=1, active=True, checkpoint=state.checkpoint),
        )
    if command == "commit":
        return Outcome("stepped", TransactionState(store_value=state.store_value))
    assert state.checkpoint is not None
    rolled_back = TransactionState(store_value=state.checkpoint)
    if command == "rollback":
        return Outcome("stepped", rolled_back)
    if command == "fail":
        return Outcome("rejected", rolled_back, "declared failure with atomic rollback")
    return Outcome("stuck", state, "unknown command")


def _rollback_equivalence(
    state: TransactionState, command: str, outcome: Outcome
) -> bool:
    if command not in {"rollback", "fail"} or not state.active:
        return True
    successor = outcome.state
    assert isinstance(successor, TransactionState)
    return bool(
        successor.store_value == state.checkpoint
        and not successor.active
        and successor.checkpoint is None
    )


# ---------------------------------------------------------------------------
# Session fidelity model
# ---------------------------------------------------------------------------


class SessionPhase(str, Enum):
    WAITING_A = "waiting_A"
    WAITING_B = "waiting_B"
    READY = "ready"


@dataclass(frozen=True)
class SessionState:
    phase: SessionPhase = SessionPhase.WAITING_A
    history: tuple[str, ...] = ()


def session_commands() -> tuple[str, ...]:
    return ("send_A_B", "send_B_A")


def session_well_formed(state: SessionState) -> bool:
    expected: SessionPhase = SessionPhase.WAITING_A
    for event in state.history:
        if expected == SessionPhase.WAITING_A and event == "send_A_B":
            expected = SessionPhase.WAITING_B
        elif expected == SessionPhase.WAITING_B and event == "send_B_A":
            expected = SessionPhase.READY
        else:
            return False
    return expected == state.phase


def session_admissible(state: SessionState, command: str) -> bool:
    return bool(
        (state.phase == SessionPhase.WAITING_A and command == "send_A_B")
        or (state.phase == SessionPhase.WAITING_B and command == "send_B_A")
    )


def session_step(state: SessionState, command: str) -> Outcome:
    if not session_admissible(state, command):
        return Outcome("rejected", state, "session transition unavailable")
    if command == "send_A_B":
        return Outcome(
            "stepped",
            SessionState(
                phase=SessionPhase.WAITING_B,
                history=state.history + (command,),
            ),
        )
    if command == "send_B_A":
        return Outcome(
            "stepped",
            SessionState(
                phase=SessionPhase.READY,
                history=state.history + (command,),
            ),
        )
    return Outcome("stuck", state, "unknown command")


def _session_trace_fidelity(state: SessionState) -> bool:
    return session_well_formed(state)


# ---------------------------------------------------------------------------
# Certificate construction and CLI
# ---------------------------------------------------------------------------


def build_certificates() -> tuple[ModelCertificate, ...]:
    provenance = explore_finite_model(
        name="provenance_ownership",
        initial=ProvenanceState(),
        commands=provenance_commands(),
        admissible=provenance_admissible,
        may_reject_when_admissible=lambda _command: False,
        step=provenance_step,
        well_formed=provenance_well_formed,
        invariants={
            "no_forged_observed_memory": _no_forged_observed_memory,
            "simulated_not_observed": _simulated_not_observed,
            "communicated_not_observed": _communicated_not_observed,
        },
    )
    capability = explore_finite_model(
        name="bounded_capability",
        initial=CapabilityState(),
        commands=capability_commands(),
        admissible=capability_admissible,
        may_reject_when_admissible=lambda _command: False,
        step=capability_step,
        well_formed=capability_well_formed,
        invariants={"capability_confinement": _capability_confinement},
        special_transition_checks={"execute_consumes_one": _execute_consumes_one},
    )
    contract = explore_finite_model(
        name="feedback_deadline",
        initial=ContractState(),
        commands=contract_commands(),
        admissible=contract_admissible,
        may_reject_when_admissible=lambda _command: False,
        step=contract_step,
        well_formed=contract_well_formed,
        invariants={"no_overdue_accepted_state": _no_overdue_accepted_state},
    )
    transaction = explore_finite_model(
        name="transaction_atomicity",
        initial=TransactionState(),
        commands=transaction_commands(),
        admissible=transaction_admissible,
        may_reject_when_admissible=lambda command: command == "fail",
        step=transaction_step,
        well_formed=transaction_well_formed,
        invariants={},
        special_transition_checks={"rollback_equivalence": _rollback_equivalence},
    )
    session = explore_finite_model(
        name="session_fidelity",
        initial=SessionState(),
        commands=session_commands(),
        admissible=session_admissible,
        may_reject_when_admissible=lambda _command: False,
        step=session_step,
        well_formed=session_well_formed,
        invariants={"session_trace_fidelity": _session_trace_fidelity},
    )
    return (provenance, capability, contract, transaction, session)


def build_report() -> dict[str, Any]:
    certificates = build_certificates()
    all_checks = all(
        cert.fixpoint_reached
        and cert.progress_with_safe_rejection
        and cert.static_dynamic_agreement
        and cert.preservation
        and all(cert.invariant_checks.values())
        and all(cert.special_checks.values())
        and not cert.counterexamples
        for cert in certificates
    )
    payload: dict[str, Any] = {
        "schema": "osl.metacore.exhaustive-finite-certificate.v1",
        "language_version": "OSL-Core 0.3",
        "scientific_status": "exhaustive finite-state metatheory",
        "model_count": len(certificates),
        "models": [asdict(cert) for cert in certificates],
        "aggregate": {
            "reachable_state_count": sum(cert.state_count for cert in certificates),
            "transition_attempt_count": sum(
                cert.transition_attempt_count for cert in certificates
            ),
            "stepped_transition_count": sum(
                cert.stepped_transition_count for cert in certificates
            ),
            "rejected_transition_count": sum(
                cert.rejected_transition_count for cert in certificates
            ),
            "all_checks_pass": all_checks,
        },
        "claim_boundary": (
            "The certificate exhaustively enumerates the explicitly defined finite "
            "models. It is not a proof-assistant mechanization of the full OSL parser, "
            "Python runtime, nonlinear extensions, or arbitrary user programs."
        ),
    }
    payload["report_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["aggregate"]["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
