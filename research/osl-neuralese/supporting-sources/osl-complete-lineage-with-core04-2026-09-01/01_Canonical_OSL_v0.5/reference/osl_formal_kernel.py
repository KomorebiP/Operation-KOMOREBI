#!/usr/bin/env python3
"""Finite abstract metatheory kernel for OSL-Core 0.3.

The kernel is deliberately smaller than the reference interpreter.  It isolates
access, provenance, quarantine, proof freshness, autobiographical writes,
capabilities, planning, execution, feedback, and a bounded feedback contract in
a finite transition system.  The complete reachable state graph can therefore
be explored exactly.

The certificate produced by :func:`explore_kernel` is a bounded mechanized
result for this abstract kernel.  It is not a proof assistant verification of
the entire Python interpreter or of arbitrary neural backends.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Iterable

try:  # pragma: no cover - package/script dual use
    from .osl_model import digest
except ImportError:  # pragma: no cover
    from osl_model import digest  # type: ignore


class Agent(str, Enum):
    A = "A"
    B = "B"


class Provenance(str, Enum):
    NONE = "none"
    OBSERVED = "observed"
    COMMUNICATED = "communicated"
    SIMULATED = "simulated"
    INJECTED = "injected"
    INFERRED = "inferred"


class MemoryClass(str, Enum):
    NONE = "none"
    OBSERVED = "observed"
    COMMUNICATED = "communicated"
    SIMULATED = "simulated"
    INFERRED = "inferred"


@dataclass(frozen=True, order=True)
class KernelState:
    source: str = ""
    holder: str = ""
    provenance: str = Provenance.NONE.value
    accessible: bool = False
    bound: bool = False
    quarantined: bool = False
    endorsed: bool = False
    authorized: bool = False
    observation_token: bool = False
    use_proof: bool = False
    ownership_proof: bool = False
    memory_class: str = MemoryClass.NONE.value
    capability_uses: int = 0
    planned: bool = False
    executed: bool = False
    feedback: bool = False
    feedback_contract: bool = False
    feedback_due: bool = False

    @property
    def has_packet(self) -> bool:
        return bool(self.source and self.holder and self.provenance != Provenance.NONE.value)

    def canonical(self) -> dict[str, object]:
        return asdict(self)

    def state_digest(self) -> str:
        return digest(self.canonical())


@dataclass(frozen=True, order=True)
class Command:
    name: str
    argument: str = ""

    def canonical(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Outcome:
    accepted: bool
    state: KernelState
    reason: str


INITIAL_STATE = KernelState()


def other(agent: str) -> str:
    return Agent.B.value if agent == Agent.A.value else Agent.A.value


def well_formed(state: KernelState) -> tuple[bool, tuple[str, ...]]:
    failures: list[str] = []
    valid_agents = {Agent.A.value, Agent.B.value}
    valid_provenance = {item.value for item in Provenance}
    valid_memory = {item.value for item in MemoryClass}

    if state.provenance not in valid_provenance:
        failures.append("provenance")
    if state.memory_class not in valid_memory:
        failures.append("memory_class")
    if state.capability_uses not in {0, 1}:
        failures.append("capability_domain")

    if not state.has_packet:
        if state.source or state.holder or state.provenance != Provenance.NONE.value:
            failures.append("empty_packet_identity")
        packet_flags = (
            state.accessible,
            state.bound,
            state.quarantined,
            state.endorsed,
            state.authorized,
            state.observation_token,
            state.use_proof,
            state.ownership_proof,
            state.memory_class != MemoryClass.NONE.value,
            state.planned,
            state.executed,
            state.feedback,
            state.feedback_due,
        )
        if any(packet_flags):
            failures.append("empty_packet_flags")
    else:
        if state.source not in valid_agents or state.holder not in valid_agents:
            failures.append("packet_agents")
        if state.provenance == Provenance.NONE.value:
            failures.append("packet_provenance")

    if state.observation_token and not (
        state.has_packet
        and state.provenance == Provenance.OBSERVED.value
        and state.source == state.holder
    ):
        failures.append("observation_token")

    if state.provenance == Provenance.INJECTED.value and not state.quarantined:
        failures.append("injected_not_quarantined")

    if state.quarantined and any(
        (
            state.endorsed,
            state.authorized,
            state.use_proof,
            state.ownership_proof,
            state.planned,
        )
    ):
        failures.append("quarantine_confinement")

    if state.bound and not state.accessible:
        failures.append("binding_without_access")
    if state.endorsed and not (state.accessible and state.bound and not state.quarantined):
        failures.append("endorsement")
    if state.authorized and not state.endorsed:
        failures.append("authorization")
    if state.use_proof and not (
        state.accessible
        and state.bound
        and state.endorsed
        and state.authorized
        and not state.quarantined
    ):
        failures.append("use_proof")
    if state.ownership_proof and not (
        state.observation_token
        and state.provenance == Provenance.OBSERVED.value
        and state.source == state.holder
        and not state.quarantined
    ):
        failures.append("ownership_proof")

    if state.memory_class == MemoryClass.OBSERVED.value and not (
        state.provenance == Provenance.OBSERVED.value
        and state.source == state.holder
        and state.observation_token
    ):
        failures.append("observed_memory")
    if state.memory_class == MemoryClass.COMMUNICATED.value and state.provenance != Provenance.COMMUNICATED.value:
        failures.append("communicated_memory")
    if state.memory_class == MemoryClass.SIMULATED.value and state.provenance != Provenance.SIMULATED.value:
        failures.append("simulated_memory")
    if state.memory_class == MemoryClass.INFERRED.value and state.provenance != Provenance.INFERRED.value:
        failures.append("inferred_memory")

    if state.planned and not state.use_proof:
        failures.append("plan_without_proof")
    if state.executed and not state.planned:
        failures.append("execute_without_plan")
    if state.feedback and not state.executed:
        failures.append("feedback_without_execute")
    if state.feedback_due and not (
        state.feedback_contract and state.executed and not state.feedback
    ):
        failures.append("feedback_due")
    if state.feedback_contract and state.executed and not state.feedback and not state.feedback_due:
        failures.append("missing_feedback_obligation")

    return not failures, tuple(sorted(set(failures)))


def _reject(state: KernelState, reason: str) -> Outcome:
    return Outcome(False, state, reason)


def _accept(state: KernelState) -> Outcome:
    return Outcome(True, state, "accepted")


def transition(state: KernelState, command: Command) -> Outcome:
    """Total deterministic transition relation with explicit safe rejection."""

    name = command.name
    arg = command.argument

    if name in {"observe", "simulate", "inject"}:
        if state.has_packet:
            return _reject(state, "packet already exists")
        if arg not in {Agent.A.value, Agent.B.value}:
            return _reject(state, "unknown agent")
        if name == "observe":
            return _accept(
                replace(
                    state,
                    source=arg,
                    holder=arg,
                    provenance=Provenance.OBSERVED.value,
                    accessible=True,
                    bound=True,
                    observation_token=True,
                )
            )
        if name == "simulate":
            return _accept(
                replace(
                    state,
                    source=arg,
                    holder=arg,
                    provenance=Provenance.SIMULATED.value,
                    accessible=True,
                    bound=True,
                )
            )
        return _accept(
            replace(
                state,
                source=other(arg),
                holder=arg,
                provenance=Provenance.INJECTED.value,
                accessible=True,
                quarantined=True,
            )
        )

    if name == "communicate":
        if not state.has_packet:
            return _reject(state, "no packet")
        if arg not in {Agent.A.value, Agent.B.value} or arg == state.holder:
            return _reject(state, "invalid receiver")
        if state.planned or state.executed:
            return _reject(state, "packet already committed to action")
        return _accept(
            replace(
                state,
                holder=arg,
                provenance=Provenance.COMMUNICATED.value,
                accessible=True,
                bound=False,
                quarantined=False,
                endorsed=False,
                authorized=False,
                observation_token=False,
                use_proof=False,
                ownership_proof=False,
                memory_class=MemoryClass.NONE.value,
            )
        )

    if name == "bind":
        if not state.has_packet or not state.accessible:
            return _reject(state, "binding requires accessible packet")
        if state.quarantined:
            return _reject(state, "quarantined packet")
        return _accept(replace(state, bound=True))

    if name == "admit":
        if not state.has_packet or state.provenance != Provenance.INJECTED.value:
            return _reject(state, "admission requires injected candidate")
        if not state.quarantined:
            return _reject(state, "candidate already admitted")
        return _accept(
            replace(
                state,
                provenance=Provenance.INFERRED.value,
                quarantined=False,
                bound=True,
            )
        )

    if name == "quarantine":
        if not state.has_packet or state.executed:
            return _reject(state, "cannot quarantine")
        return _accept(
            replace(
                state,
                quarantined=True,
                endorsed=False,
                authorized=False,
                use_proof=False,
                ownership_proof=False,
                planned=False,
            )
        )

    if name == "endorse":
        if not state.has_packet or not state.accessible or not state.bound:
            return _reject(state, "endorsement prerequisites")
        if state.quarantined:
            return _reject(state, "quarantined packet")
        return _accept(replace(state, endorsed=True))

    if name == "authorize":
        if not state.endorsed or state.quarantined:
            return _reject(state, "authorization prerequisites")
        return _accept(replace(state, authorized=True))

    if name == "derive_use_proof":
        if not (
            state.accessible
            and state.bound
            and state.endorsed
            and state.authorized
            and not state.quarantined
        ):
            return _reject(state, "use-proof premises")
        return _accept(replace(state, use_proof=True))

    if name == "derive_ownership_proof":
        if not (
            state.observation_token
            and state.provenance == Provenance.OBSERVED.value
            and state.source == state.holder
            and not state.quarantined
        ):
            return _reject(state, "ownership-proof premises")
        return _accept(replace(state, ownership_proof=True))

    if name == "mutate_authorization":
        if not state.has_packet or not state.authorized or state.planned:
            return _reject(state, "authorization not mutable")
        return _accept(replace(state, authorized=False, use_proof=False))

    if name.startswith("write_"):
        if not state.has_packet or state.memory_class != MemoryClass.NONE.value:
            return _reject(state, "memory unavailable")
        requested = name.removeprefix("write_")
        if requested == MemoryClass.OBSERVED.value:
            if not state.ownership_proof:
                return _reject(state, "observed memory requires ownership proof")
        elif requested == MemoryClass.COMMUNICATED.value:
            if state.provenance != Provenance.COMMUNICATED.value or not state.bound:
                return _reject(state, "communicated memory mismatch")
        elif requested == MemoryClass.SIMULATED.value:
            if state.provenance != Provenance.SIMULATED.value or not state.bound:
                return _reject(state, "simulated memory mismatch")
        elif requested == MemoryClass.INFERRED.value:
            if state.provenance != Provenance.INFERRED.value or not state.bound:
                return _reject(state, "inferred memory mismatch")
        else:
            return _reject(state, "unknown memory class")
        return _accept(replace(state, memory_class=requested))

    if name == "grant_capability":
        return _accept(replace(state, capability_uses=1))

    if name == "revoke_capability":
        return _accept(replace(state, capability_uses=0))

    if name == "enable_feedback_contract":
        if state.executed:
            return _reject(state, "contract must precede execution")
        return _accept(replace(state, feedback_contract=True))

    if name == "plan":
        if not state.use_proof or state.quarantined:
            return _reject(state, "planning requires current use proof")
        return _accept(replace(state, planned=True))

    if name == "execute":
        if not state.planned:
            return _reject(state, "execution requires plan")
        if state.capability_uses <= 0:
            return _reject(state, "execution requires capability")
        if state.executed:
            return _reject(state, "action already executed")
        return _accept(
            replace(
                state,
                capability_uses=state.capability_uses - 1,
                executed=True,
                feedback_due=state.feedback_contract,
            )
        )

    if name == "feedback":
        if not state.executed or state.feedback:
            return _reject(state, "feedback requires unclosed execution")
        return _accept(replace(state, feedback=True, feedback_due=False))

    return _reject(state, "unknown command")


def command_alphabet() -> tuple[Command, ...]:
    commands = [
        Command("observe", Agent.A.value),
        Command("observe", Agent.B.value),
        Command("simulate", Agent.A.value),
        Command("simulate", Agent.B.value),
        Command("inject", Agent.A.value),
        Command("inject", Agent.B.value),
        Command("communicate", Agent.A.value),
        Command("communicate", Agent.B.value),
    ]
    commands.extend(
        Command(name)
        for name in (
            "bind",
            "admit",
            "quarantine",
            "endorse",
            "authorize",
            "derive_use_proof",
            "derive_ownership_proof",
            "mutate_authorization",
            "write_observed",
            "write_communicated",
            "write_simulated",
            "write_inferred",
            "grant_capability",
            "revoke_capability",
            "enable_feedback_contract",
            "plan",
            "execute",
            "feedback",
        )
    )
    return tuple(commands)


def transition_properties(
    before: KernelState,
    command: Command,
    outcome: Outcome,
) -> tuple[str, ...]:
    """Return violated one-step metatheory obligations."""

    failures: list[str] = []
    if not outcome.accepted:
        if outcome.state != before:
            failures.append("safe_rejection_state_change")
        return tuple(failures)

    after = outcome.state
    ok, wf_failures = well_formed(after)
    if not ok:
        failures.extend(f"preservation:{item}" for item in wf_failures)

    if not before.observation_token and after.observation_token and command.name != "observe":
        failures.append("provenance_nonforging")
    if (
        before.memory_class != MemoryClass.OBSERVED.value
        and after.memory_class == MemoryClass.OBSERVED.value
        and command.name != "write_observed"
    ):
        failures.append("observed_memory_constructor")
    if (
        before.memory_class != MemoryClass.OBSERVED.value
        and after.memory_class == MemoryClass.OBSERVED.value
        and not before.ownership_proof
    ):
        failures.append("ownership_gate")
    if not before.executed and after.executed:
        if command.name != "execute" or not before.planned or before.capability_uses <= 0:
            failures.append("effect_confinement")
    if not before.feedback and after.feedback:
        if command.name != "feedback" or not before.executed:
            failures.append("feedback_causality")
    if not before.use_proof and after.use_proof and command.name != "derive_use_proof":
        failures.append("use_proof_constructor")
    if before.use_proof and command.name in {"mutate_authorization", "quarantine", "communicate"} and after.use_proof:
        failures.append("proof_freshness")
    if command.name == "communicate" and outcome.accepted and after.source != before.source:
        failures.append("source_preservation")
    if after.planned and after.quarantined:
        failures.append("quarantine_planning")
    if command.name == "execute" and before.feedback_contract and not after.feedback_due:
        failures.append("contract_obligation_creation")
    if command.name == "feedback" and after.feedback_due:
        failures.append("contract_obligation_discharge")
    if command.name == "execute" and after.capability_uses != before.capability_uses - 1:
        failures.append("linear_capability_consumption")

    return tuple(sorted(set(failures)))


def explore_kernel(commands: Iterable[Command] | None = None) -> dict[str, object]:
    alphabet = tuple(command_alphabet() if commands is None else commands)
    queue: deque[KernelState] = deque([INITIAL_STATE])
    seen: set[KernelState] = {INITIAL_STATE}
    edges: list[tuple[KernelState, Command, Outcome]] = []
    failures: list[dict[str, object]] = []
    accepted_counter: Counter[str] = Counter()
    rejected_counter: Counter[str] = Counter()

    while queue:
        state = queue.popleft()
        ok, wf_failures = well_formed(state)
        if not ok:
            failures.append(
                {
                    "property": "reachable_state_well_formed",
                    "state": state.canonical(),
                    "violations": list(wf_failures),
                }
            )
        for command in alphabet:
            outcome = transition(state, command)
            edges.append((state, command, outcome))
            violations = transition_properties(state, command, outcome)
            if violations:
                failures.append(
                    {
                        "property": "transition",
                        "before": state.canonical(),
                        "command": command.canonical(),
                        "after": outcome.state.canonical(),
                        "accepted": outcome.accepted,
                        "violations": list(violations),
                    }
                )
            if outcome.accepted:
                accepted_counter[command.name] += 1
                if outcome.state not in seen:
                    seen.add(outcome.state)
                    queue.append(outcome.state)
            else:
                rejected_counter[command.name] += 1

    states_sorted = sorted(seen)
    graph_payload = {
        "states": [state.canonical() for state in states_sorted],
        "commands": [command.canonical() for command in alphabet],
        "edges": [
            {
                "before": before.state_digest(),
                "command": command.canonical(),
                "accepted": outcome.accepted,
                "after": outcome.state.state_digest(),
                "reason": outcome.reason,
            }
            for before, command, outcome in edges
        ],
    }
    graph_digest = digest(graph_payload)

    properties = {
        "progress_with_explicit_rejection": True,
        "preservation": not any(
            any(str(v).startswith("preservation:") for v in failure.get("violations", []))
            for failure in failures
        ),
        "safe_rejection": not any(
            "safe_rejection_state_change" in failure.get("violations", [])
            for failure in failures
        ),
        "provenance_nonforging": not any(
            "provenance_nonforging" in failure.get("violations", [])
            for failure in failures
        ),
        "ownership_gating": not any(
            "ownership_gate" in failure.get("violations", [])
            for failure in failures
        ),
        "effect_confinement": not any(
            "effect_confinement" in failure.get("violations", [])
            for failure in failures
        ),
        "proof_freshness": not any(
            "proof_freshness" in failure.get("violations", [])
            for failure in failures
        ),
        "source_preservation": not any(
            "source_preservation" in failure.get("violations", [])
            for failure in failures
        ),
        "quarantine_confinement": not any(
            "quarantine_planning" in failure.get("violations", [])
            for failure in failures
        ),
        "feedback_causality": not any(
            "feedback_causality" in failure.get("violations", [])
            for failure in failures
        ),
        "contract_obligation_soundness": not any(
            set(failure.get("violations", []))
            & {"contract_obligation_creation", "contract_obligation_discharge"}
            for failure in failures
        ),
        "linear_capability_consumption": not any(
            "linear_capability_consumption" in failure.get("violations", [])
            for failure in failures
        ),
    }

    certificate: dict[str, object] = {
        "schema": "osl.core.compact-closure-certificate.v1",
        "language": "OSL-Core 0.3 compact abstract kernel",
        "reachable_state_count": len(seen),
        "command_count": len(alphabet),
        "transition_count": len(edges),
        "accepted_transition_count": sum(accepted_counter.values()),
        "rejected_transition_count": sum(rejected_counter.values()),
        "accepted_by_command": dict(sorted(accepted_counter.items())),
        "rejected_by_command": dict(sorted(rejected_counter.items())),
        "properties": properties,
        "failure_count": len(failures),
        "failures": failures,
        "state_graph_digest": graph_digest,
        "all_checks_pass": not failures and all(properties.values()),
        "claim_boundary": (
            "Exact exhaustive exploration of the compact integrated abstract kernel.  It is not "
            "a proof-assistant verification of the complete Python interpreter, "
            "neural proposal generators, arbitrary distributed protocols, or all "
            "unbounded OSL programs."
        ),
    }
    certificate["certificate_digest"] = digest(certificate)
    return certificate


__all__ = [
    "Agent",
    "Command",
    "INITIAL_STATE",
    "KernelState",
    "MemoryClass",
    "Outcome",
    "Provenance",
    "command_alphabet",
    "explore_kernel",
    "transition",
    "transition_properties",
    "well_formed",
]
