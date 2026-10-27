#!/usr/bin/env python3
"""Structural invariant checks for the executable OSL-Core 0.5 runtime."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

try:  # pragma: no cover
    from .osl_model import (
        MEMORY_COMPATIBILITY,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        RuntimeState,
        digest,
    )
except ImportError:  # pragma: no cover
    from osl_model import (  # type: ignore
        MEMORY_COMPATIBILITY,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        RuntimeState,
        digest,
    )


def verify_audit_log(receipts: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(receipts)
    previous = "0" * 64
    failures: list[str] = []
    for expected_index, receipt in enumerate(records):
        if receipt.get("index") != expected_index:
            failures.append(f"index:{expected_index}")
        if receipt.get("previous_digest") != previous:
            failures.append(f"previous_digest:{expected_index}")
        observed = receipt.get("digest")
        unsigned = dict(receipt)
        unsigned.pop("digest", None)
        if observed != digest(unsigned):
            failures.append(f"digest:{expected_index}")
        previous = str(observed)
    payload = {
        "schema": "osl.core.audit-chain-verification.v1",
        "receipt_count": len(records),
        "chain_tip": previous,
        "failed_checks": failures,
        "all_checks_pass": not failures,
    }
    payload["verification_digest"] = digest(payload)
    return payload


def check_runtime_state(
    state: RuntimeState,
    *,
    audit_log: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    failures: list[str] = []

    for name, agent in state.agents.items():
        if agent.lineage not in state.lineage_parents:
            failures.append(f"agent_lineage:{name}")
        if name not in state.memories:
            failures.append(f"agent_memory_table:{name}")

    for name, packet in state.packets.items():
        if packet.provenance not in PROVENANCE_CLASSES:
            failures.append(f"packet_provenance:{name}")
        expected_content = digest(packet.canonical_content())
        if packet.content_digest != expected_content:
            failures.append(f"packet_content_digest:{name}")
        expected_packet = digest(packet.canonical(include_digest=False))
        if packet.packet_digest != expected_packet:
            failures.append(f"packet_digest:{name}")
        external_source_allowed = packet.provenance in {
            "injected", "unresolved"
        } or packet.status in {"provisional", "rejected"}
        if packet.source_agent not in state.agents and not external_source_allowed:
            failures.append(f"packet_source_agent:{name}")
        if packet.source_lineage not in state.lineage_parents and not external_source_allowed:
            failures.append(f"packet_source_lineage:{name}")
        for agent_name in packet.observation_tokens:
            agent = state.agents.get(agent_name)
            if (
                agent is None
                or packet.provenance != "observed"
                or packet.source_agent != agent_name
                or packet.source_lineage != agent.lineage
            ):
                failures.append(f"observation_token:{name}:{agent_name}")
        for agent_name in packet.endorsed_by:
            if agent_name in packet.quarantined_by:
                failures.append(f"quarantined_endorsement:{name}:{agent_name}")
        for agent_name, scopes in packet.authorizations.items():
            if agent_name in packet.quarantined_by:
                failures.append(f"quarantined_authorization:{name}:{agent_name}")
            if not scopes:
                failures.append(f"empty_authorization:{name}:{agent_name}")

    for name, proof in state.proofs.items():
        if proof.resource_mode not in PROOF_RESOURCE_MODES:
            failures.append(f"proof_resource_mode:{name}")
        if not proof.construction_digest_valid():
            failures.append(f"proof_digest:{name}")
        if proof.resource_mode == "persistent":
            if proof.remaining_uses is not None or proof.consumed_step is not None:
                failures.append(f"persistent_proof_resource_state:{name}")
        else:
            if proof.remaining_uses not in {0, 1}:
                failures.append(f"bounded_proof_uses:{name}")
            if proof.remaining_uses == 0 and proof.consumed_step is None:
                failures.append(f"consumed_proof_step:{name}")
            if proof.remaining_uses == 1 and proof.consumed_step is not None:
                failures.append(f"unconsumed_proof_step:{name}")
        for premise in proof.premises:
            if premise not in state.proofs:
                failures.append(f"proof_premise:{name}:{premise}")

    for agent_name, records in state.memories.items():
        if agent_name not in state.agents:
            failures.append(f"memory_unknown_agent:{agent_name}")
            continue
        for index, record in enumerate(records):
            payload = {
                "agent": record.agent,
                "packet_name": record.packet_name,
                "content": record.content,
                "memory_class": record.memory_class,
                "source_agent": record.source_agent,
                "source_lineage": record.source_lineage,
                "packet_digest": record.packet_digest,
                "proof_digest": record.proof_digest,
            }
            if record.record_digest != digest(payload):
                failures.append(f"memory_digest:{agent_name}:{index}")
            packet = state.packets.get(record.packet_name)
            if packet is not None:
                allowed = MEMORY_COMPATIBILITY.get(packet.provenance, set())
                if record.memory_class not in allowed:
                    failures.append(f"memory_compatibility:{agent_name}:{index}")
                if record.memory_class == "observed":
                    agent = state.agents[agent_name]
                    if not (
                        packet.source_agent == agent_name
                        and packet.source_lineage == agent.lineage
                        and agent_name in packet.observation_tokens
                    ):
                        failures.append(f"observed_memory_origin:{agent_name}:{index}")

    for name, action in state.actions.items():
        expected = digest(
            {
                "name": action.name,
                "agent": action.agent,
                "packet_name": action.packet_name,
                "effect": action.effect,
                "expected": action.expected,
                "required_proof": action.required_proof,
                "executed": action.executed,
                "observed": action.observed,
                "capability_digest": action.capability_digest,
            }
        )
        if action.action_digest != expected:
            failures.append(f"action_digest:{name}")
        if action.agent not in state.agents:
            failures.append(f"action_agent:{name}")
        if action.packet_name not in state.packets:
            failures.append(f"action_packet:{name}")
        if action.executed and action.capability_digest is None:
            failures.append(f"executed_action_capability:{name}")
        if action.observed is not None and not action.executed:
            failures.append(f"feedback_without_execution:{name}")

    for name, contract in state.contracts.items():
        for action_name in contract.pending:
            if action_name not in state.actions:
                failures.append(f"contract_pending_action:{name}:{action_name}")

    for name, session in state.sessions.items():
        if any(participant not in state.agents for participant in session.participants):
            failures.append(f"session_participant:{name}")
        previous_state = session.initial_state
        for index, event in enumerate(session.history):
            if event.get("event") == "start":
                if index != 0 or event.get("state") != session.initial_state:
                    failures.append(f"session_start:{name}")
                previous_state = session.initial_state
                continue
            key = (
                str(event.get("from")),
                str(event.get("event")),
                str(event.get("sender")),
                str(event.get("receiver")),
            )
            target = session.transitions.get(key)
            if event.get("from") != previous_state or target != event.get("to"):
                failures.append(f"session_history:{name}:{index}")
            previous_state = str(event.get("to"))
        if session.active and session.current_state != previous_state:
            failures.append(f"session_current_state:{name}")

    if audit_log is not None:
        chain = verify_audit_log(audit_log)
        if not chain["all_checks_pass"]:
            failures.extend(f"audit:{item}" for item in chain["failed_checks"])
        audit_digests = {record.get("digest") for record in audit_log}
        for index, receipt in enumerate(state.receipts):
            if receipt.get("digest") not in audit_digests:
                failures.append(f"state_receipt_not_audited:{index}")

    payload: dict[str, Any] = {
        "schema": "osl.core.runtime-invariant-report.v1",
        "module": state.module,
        "semantic_digest": state.semantic_digest(),
        "packet_count": len(state.packets),
        "proof_count": len(state.proofs),
        "memory_record_count": sum(len(records) for records in state.memories.values()),
        "action_count": len(state.actions),
        "failure_count": len(failures),
        "failures": failures,
        "all_checks_pass": not failures,
    }
    payload["report_digest"] = digest(payload)
    return payload


__all__ = ["check_runtime_state", "verify_audit_log"]
