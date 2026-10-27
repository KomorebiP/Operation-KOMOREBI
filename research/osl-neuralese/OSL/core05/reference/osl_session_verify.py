"""Finite graph verifier for OSL-Core 0.5 session protocols.

The verifier proves graph-theoretic properties of the declared finite protocol:
transition determinism, reachability, deadlock freedom relative to declared
terminal states, and universal terminal reachability.  It does not prove
asynchronous queue safety, fairness under an external scheduler, or general
multiparty progress for recursive protocols.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import networkx as nx

try:  # pragma: no cover - package/script dual use
    from .osl_model import SessionProtocol, digest
except ImportError:  # pragma: no cover
    from osl_model import SessionProtocol, digest  # type: ignore


@dataclass(frozen=True)
class SessionVerification:
    schema: str
    session: str
    state_count: int
    transition_count: int
    initial_state: str
    terminal_states: tuple[str, ...]
    reachable_states: tuple[str, ...]
    unreachable_states: tuple[str, ...]
    reachable_deadlocks: tuple[str, ...]
    terminal_with_outgoing: tuple[str, ...]
    states_without_terminal_path: tuple[str, ...]
    deterministic: bool
    initial_declared: bool
    terminal_declared: bool
    all_reachable_states_can_terminate: bool
    all_checks_pass: bool
    report_digest: str


def _states(protocol: SessionProtocol) -> set[str]:
    states = {protocol.initial_state, *protocol.terminal_states}
    for (source, _event, _sender, _receiver), target in protocol.transitions.items():
        states.add(source)
        states.add(target)
    return states


def verify_session_protocol(protocol: SessionProtocol) -> SessionVerification:
    states = _states(protocol)
    graph = nx.DiGraph()
    graph.add_nodes_from(states)
    for key, target in protocol.transitions.items():
        source, _event, _sender, _receiver = key
        graph.add_edge(source, target)

    # The runtime map already forbids duplicate exact event keys.  This explicit
    # check makes the certificate independent of that implementation detail.
    keys = list(protocol.transitions)
    deterministic = len(keys) == len(set(keys))
    initial_declared = protocol.initial_state in states
    terminal_declared = bool(protocol.terminal_states)

    reachable = (
        {protocol.initial_state}
        | nx.descendants(graph, protocol.initial_state)
        if initial_declared
        else set()
    )
    unreachable = states - reachable
    reachable_deadlocks = {
        state
        for state in reachable
        if graph.out_degree(state) == 0 and state not in protocol.terminal_states
    }
    terminal_with_outgoing = {
        state for state in protocol.terminal_states if graph.out_degree(state) > 0
    }

    reverse = graph.reverse(copy=False)
    can_reach_terminal: set[str] = set()
    for terminal in protocol.terminal_states:
        if terminal in graph:
            can_reach_terminal.add(terminal)
            can_reach_terminal.update(nx.descendants(reverse, terminal))
    states_without_terminal_path = reachable - can_reach_terminal
    all_reachable_can_terminate = bool(terminal_declared) and not states_without_terminal_path

    checks = {
        "deterministic": deterministic,
        "initial_declared": initial_declared,
        "terminal_declared": terminal_declared,
        "no_reachable_nonterminal_deadlocks": not reachable_deadlocks,
        "no_terminal_outgoing_transitions": not terminal_with_outgoing,
        "all_reachable_states_can_terminate": all_reachable_can_terminate,
    }
    unsigned: dict[str, Any] = {
        "schema": "osl.core.session-verification.v1",
        "session": protocol.name,
        "state_count": len(states),
        "transition_count": len(protocol.transitions),
        "initial_state": protocol.initial_state,
        "terminal_states": tuple(sorted(protocol.terminal_states)),
        "reachable_states": tuple(sorted(reachable)),
        "unreachable_states": tuple(sorted(unreachable)),
        "reachable_deadlocks": tuple(sorted(reachable_deadlocks)),
        "terminal_with_outgoing": tuple(sorted(terminal_with_outgoing)),
        "states_without_terminal_path": tuple(sorted(states_without_terminal_path)),
        "deterministic": deterministic,
        "initial_declared": initial_declared,
        "terminal_declared": terminal_declared,
        "all_reachable_states_can_terminate": all_reachable_can_terminate,
        "all_checks_pass": all(checks.values()),
    }
    return SessionVerification(**unsigned, report_digest=digest(unsigned))


def verification_payload(report: SessionVerification) -> dict[str, Any]:
    return asdict(report)


__all__ = ["SessionVerification", "verify_session_protocol", "verification_payload"]
