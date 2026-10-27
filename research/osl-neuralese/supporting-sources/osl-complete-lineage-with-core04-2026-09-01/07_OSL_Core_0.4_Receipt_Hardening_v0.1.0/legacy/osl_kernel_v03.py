#!/usr/bin/env python3
"""Independent receipt and proof kernel for the finite OSL-Core 0.3 runtime.

The runtime creates state transitions.  This module rechecks the append-only
receipt log using a separate implementation of canonical hashing and the finite
proof/trace rules.  It deliberately imports the runtime only in the optional
program runner; all receipt validation is dictionary based.

This is a small trusted kernel, not a general proof assistant or cryptographic
authentication system.  SHA-256 establishes integrity of the serialized chain,
not authorship.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


MEMORY_COMPATIBILITY: dict[str, set[str]] = {
    "observed": {"observed"},
    "inferred": {"inferred"},
    "recalled": {"recalled", "reconstructed"},
    "simulated": {"simulated"},
    "communicated": {"communicated", "foreign"},
    "injected": {"injected"},
    "foreign": {"foreign", "communicated"},
    "reconstructed": {"reconstructed", "recalled"},
    "conflicted": {"conflicted"},
    "unresolved": {"unresolved"},
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _without_digest(value: dict[str, Any], key: str = "digest") -> dict[str, Any]:
    payload = copy.deepcopy(value)
    payload.pop(key, None)
    return payload


def _proof_payload(proof: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "name",
        "kind",
        "subject",
        "agent",
        "scope",
        "memory_class",
        "source_agent",
        "source_lineage",
        "premises",
        "claims",
        "subject_digest",
        "state_digest",
        "created_step",
        "trusted",
        "resource_mode",
        "remaining_uses",
        "consumed_step",
    )
    return {key: proof.get(key) for key in keys}


def _action_payload(action: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "name",
        "agent",
        "packet_name",
        "effect",
        "expected",
        "required_proof",
        "executed",
        "observed",
        "capability_digest",
    )
    return {key: action.get(key) for key in keys}


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "agent",
        "packet_name",
        "content",
        "memory_class",
        "source_agent",
        "source_lineage",
        "packet_digest",
        "proof_digest",
    )
    return {key: record.get(key) for key in keys}


def _packet_content_payload(packet: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "name",
        "content",
        "source_agent",
        "source_lineage",
        "provenance",
        "confidence",
        "simulated",
        "parent_digest",
        "latent_source",
    )
    return {key: packet.get(key) for key in keys}


def _packet_state_payload(packet: dict[str, Any]) -> dict[str, Any]:
    payload = {
        **_packet_content_payload(packet),
        "accessible_to": sorted(packet.get("accessible_to", [])),
        "bound_to": sorted(packet.get("bound_to", [])),
        "quarantined_by": sorted(packet.get("quarantined_by", [])),
        "endorsed_by": sorted(packet.get("endorsed_by", [])),
        "authorizations": {
            agent: sorted(scopes)
            for agent, scopes in sorted(packet.get("authorizations", {}).items())
        },
        "observation_tokens": sorted(packet.get("observation_tokens", [])),
        "status": packet.get("status"),
        "obligations": sorted(packet.get("obligations", [])),
        "support": packet.get("support"),
        "refutation": packet.get("refutation"),
        "unresolved": packet.get("unresolved"),
        "content_digest": packet.get("content_digest"),
    }
    return payload


def _capability_payload(agent: str, cap: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent": agent,
        "effect": cap.get("effect"),
        "remaining_uses": cap.get("remaining_uses"),
        "expires_at": cap.get("expires_at"),
        "source": cap.get("source"),
    }


@dataclass
class KernelCounters:
    receipts: int = 0
    packets: int = 0
    proofs: int = 0
    memory_records: int = 0
    plans: int = 0
    executions: int = 0
    feedbacks: int = 0
    session_advances: int = 0
    transaction_begins: int = 0
    transaction_commits: int = 0
    transaction_rollbacks: int = 0


class KernelVerifier:
    def __init__(self) -> None:
        self.failures: list[dict[str, Any]] = []
        self.counters = KernelCounters()
        self.packets: dict[str, dict[str, Any]] = {}
        self.packet_by_digest: dict[str, dict[str, Any]] = {}
        self.proofs: dict[str, dict[str, Any]] = {}
        self.proof_by_digest: dict[str, dict[str, Any]] = {}
        self.proof_remaining: dict[str, int | None] = {}
        self.capabilities: dict[tuple[str, str], dict[str, Any]] = {}
        self.actions: dict[str, dict[str, Any]] = {}
        self.session_transitions: dict[
            tuple[str, str, str, str, str], str
        ] = {}
        self.session_initial: dict[str, str] = {}
        self.session_terminals: dict[str, set[str]] = {}
        self.session_state: dict[str, str] = {}
        self.active_transactions: dict[str, dict[str, Any]] = {}
        self.rolled_back_ranges: list[tuple[int, int, str]] = []

    def fail(self, property_name: str, **details: Any) -> None:
        self.failures.append({"property": property_name, **details})

    def _install_packet(self, packet: dict[str, Any], receipt_index: int) -> None:
        expected_content = digest(_packet_content_payload(packet))
        if packet.get("content_digest") != expected_content:
            self.fail(
                "packet_content_digest",
                receipt_index=receipt_index,
                packet=packet.get("name"),
            )
        expected_packet = digest(_packet_state_payload(packet))
        if packet.get("packet_digest") != expected_packet:
            self.fail(
                "packet_state_digest",
                receipt_index=receipt_index,
                packet=packet.get("name"),
                expected=expected_packet,
                observed=packet.get("packet_digest"),
            )
        parent = packet.get("parent_digest")
        if parent is not None and parent not in self.packet_by_digest:
            self.fail(
                "packet_parent_exists",
                receipt_index=receipt_index,
                packet=packet.get("name"),
                parent_digest=parent,
            )
        name = str(packet.get("name"))
        self.packets[name] = copy.deepcopy(packet)
        if packet.get("packet_digest"):
            self.packet_by_digest[str(packet["packet_digest"])] = copy.deepcopy(packet)
        self.counters.packets += 1

    def _apply_packet_mutation(self, receipt: dict[str, Any]) -> None:
        kind = receipt.get("kind")
        name = receipt.get("packet")
        if not isinstance(name, str) or name not in self.packets:
            self.fail("packet_mutation_subject", receipt_index=receipt.get("index"), kind=kind)
            return
        packet = copy.deepcopy(self.packets[name])
        agent = receipt.get("agent")
        if kind == "endorse":
            packet.setdefault("endorsed_by", [])
            packet["endorsed_by"] = sorted(set(packet["endorsed_by"]) | {agent})
        elif kind == "authorize":
            auth = {
                key: list(value)
                for key, value in packet.get("authorizations", {}).items()
            }
            auth.setdefault(agent, [])
            auth[agent] = sorted(set(auth[agent]) | {receipt.get("scope")})
            packet["authorizations"] = auth
        else:
            return
        expected = digest(_packet_state_payload(packet))
        if receipt.get("packet_digest") != expected:
            self.fail(
                "packet_mutation_digest",
                receipt_index=receipt.get("index"),
                kind=kind,
                packet=name,
                expected=expected,
                observed=receipt.get("packet_digest"),
            )
        packet["packet_digest"] = expected
        self.packets[name] = packet
        self.packet_by_digest[expected] = copy.deepcopy(packet)

    def _verify_proof(self, proof: dict[str, Any], receipt_index: int) -> None:
        expected_digest = digest(_proof_payload(proof))
        if proof.get("proof_digest") != expected_digest:
            self.fail(
                "proof_digest",
                receipt_index=receipt_index,
                proof=proof.get("name"),
                expected=expected_digest,
                observed=proof.get("proof_digest"),
            )
        name = str(proof.get("name"))
        kind = proof.get("kind")
        subject = proof.get("subject")
        premises = tuple(proof.get("premises", ()))
        if kind != "capability":
            packet = self.packets.get(str(subject))
            if packet is None:
                self.fail("proof_subject_exists", receipt_index=receipt_index, proof=name)
            else:
                if proof.get("subject_digest") != packet.get("content_digest"):
                    self.fail("proof_subject_digest", receipt_index=receipt_index, proof=name)
                if kind in {"use", "ownership"} and proof.get("state_digest") != packet.get(
                    "packet_digest"
                ):
                    self.fail("composite_proof_state_digest", receipt_index=receipt_index, proof=name)
        premise_terms: list[dict[str, Any]] = []
        for premise in premises:
            term = self.proofs.get(str(premise))
            if term is None:
                self.fail(
                    "proof_premise_exists",
                    receipt_index=receipt_index,
                    proof=name,
                    premise=premise,
                )
            else:
                premise_terms.append(term)
        kinds = {term.get("kind") for term in premise_terms}
        if kind == "use":
            required = {"access", "origin", "clear", "endorsement", "authorization"}
            if not required.issubset(kinds):
                self.fail(
                    "use_proof_premises",
                    receipt_index=receipt_index,
                    proof=name,
                    missing=sorted(required - kinds),
                )
        if kind == "ownership":
            required = {"access", "origin", "clear"}
            if proof.get("memory_class") == "observed":
                required.add("observation")
            if not required.issubset(kinds):
                self.fail(
                    "ownership_proof_premises",
                    receipt_index=receipt_index,
                    proof=name,
                    missing=sorted(required - kinds),
                )
        self.proofs[name] = copy.deepcopy(proof)
        self.proof_remaining[name] = proof.get("remaining_uses")
        if proof.get("proof_digest"):
            self.proof_by_digest[str(proof["proof_digest"])] = copy.deepcopy(proof)
        self.counters.proofs += 1

    def _verify_memory(self, record: dict[str, Any], receipt_index: int) -> None:
        expected = digest(_record_payload(record))
        if record.get("record_digest") != expected:
            self.fail(
                "memory_record_digest",
                receipt_index=receipt_index,
                packet=record.get("packet_name"),
            )
        packet = self.packet_by_digest.get(str(record.get("packet_digest")))
        if packet is None:
            self.fail(
                "memory_packet_digest_exists",
                receipt_index=receipt_index,
                packet_digest=record.get("packet_digest"),
            )
            return
        memory_class = str(record.get("memory_class"))
        provenance = str(packet.get("provenance"))
        if memory_class not in MEMORY_COMPATIBILITY.get(provenance, set()):
            self.fail(
                "memory_provenance_compatibility",
                receipt_index=receipt_index,
                provenance=provenance,
                memory_class=memory_class,
            )
        if memory_class == "observed":
            agent = record.get("agent")
            if not (
                provenance == "observed"
                and packet.get("source_agent") == agent
                and agent in packet.get("observation_tokens", [])
            ):
                self.fail(
                    "observed_memory_nonforging",
                    receipt_index=receipt_index,
                    agent=agent,
                    packet=packet.get("name"),
                )
        proof_digest = record.get("proof_digest")
        if proof_digest is not None:
            proof = self.proof_by_digest.get(str(proof_digest))
            if proof is None or proof.get("kind") != "ownership":
                self.fail(
                    "memory_ownership_proof",
                    receipt_index=receipt_index,
                    proof_digest=proof_digest,
                )
        self.counters.memory_records += 1

    def _verify_action_digest(self, action: dict[str, Any], receipt_index: int) -> None:
        expected = digest(_action_payload(action))
        if action.get("action_digest") != expected:
            self.fail(
                "action_digest",
                receipt_index=receipt_index,
                action=action.get("name"),
                expected=expected,
                observed=action.get("action_digest"),
            )

    def _verify_session_report(self, report: dict[str, Any], receipt_index: int) -> None:
        unsigned = dict(report)
        observed_digest = unsigned.pop("report_digest", None)
        if observed_digest != digest(unsigned):
            self.fail("session_report_digest", receipt_index=receipt_index)
        name = str(report.get("session"))
        initial = self.session_initial.get(name)
        terminals = set(self.session_terminals.get(name, set()))
        transitions = {
            (source, event, sender, receiver): target
            for (session, source, event, sender, receiver), target in self.session_transitions.items()
            if session == name
        }
        states: set[str] = set(terminals)
        if initial is not None:
            states.add(initial)
        for (source, _event, _sender, _receiver), target in transitions.items():
            states.add(source)
            states.add(target)
        reachable: set[str] = set()
        if initial is not None:
            frontier = [initial]
            while frontier:
                state = frontier.pop()
                if state in reachable:
                    continue
                reachable.add(state)
                frontier.extend(
                    target
                    for (source, _event, _sender, _receiver), target in transitions.items()
                    if source == state and target not in reachable
                )
        deadlocks = {
            state
            for state in reachable
            if state not in terminals
            and not any(source == state for source, _e, _s, _r in transitions)
        }
        outgoing_terminals = {
            state
            for state in terminals
            if any(source == state for source, _e, _s, _r in transitions)
        }
        reverse: dict[str, set[str]] = {state: set() for state in states}
        for (source, _event, _sender, _receiver), target in transitions.items():
            reverse.setdefault(target, set()).add(source)
        can_terminate: set[str] = set(terminals)
        frontier = list(terminals)
        while frontier:
            state = frontier.pop()
            for predecessor in reverse.get(state, set()):
                if predecessor not in can_terminate:
                    can_terminate.add(predecessor)
                    frontier.append(predecessor)
        no_path = reachable - can_terminate
        expected_pass = bool(terminals) and not deadlocks and not outgoing_terminals and not no_path
        if bool(report.get("all_checks_pass")) != expected_pass:
            self.fail("session_report_result", receipt_index=receipt_index, session=name)
        if tuple(report.get("reachable_deadlocks", ())) != tuple(sorted(deadlocks)):
            self.fail("session_report_deadlocks", receipt_index=receipt_index, session=name)
        if tuple(report.get("terminal_with_outgoing", ())) != tuple(sorted(outgoing_terminals)):
            self.fail("session_report_terminal_outgoing", receipt_index=receipt_index, session=name)
        if tuple(report.get("states_without_terminal_path", ())) != tuple(sorted(no_path)):
            self.fail("session_report_terminal_paths", receipt_index=receipt_index, session=name)

    def verify(self, receipts: list[dict[str, Any]], final_state: dict[str, Any]) -> dict[str, Any]:
        previous = "0" * 64
        previous_step = -1
        program_completed = False
        program_reject_reason: str | None = None
        for expected_index, receipt in enumerate(receipts):
            self.counters.receipts += 1
            index = receipt.get("index")
            if index != expected_index:
                self.fail("receipt_index", expected=expected_index, observed=index)
            if receipt.get("previous_digest") != previous:
                self.fail(
                    "receipt_hash_chain",
                    receipt_index=index,
                    expected=previous,
                    observed=receipt.get("previous_digest"),
                )
            observed_digest = receipt.get("digest")
            expected_digest = digest(_without_digest(receipt))
            if observed_digest != expected_digest:
                self.fail(
                    "receipt_digest",
                    receipt_index=index,
                    expected=expected_digest,
                    observed=observed_digest,
                )
            step = int(receipt.get("step", -1))
            if step < previous_step:
                self.fail(
                    "receipt_step_monotonicity",
                    receipt_index=index,
                    previous_step=previous_step,
                    observed_step=step,
                )
            previous_step = step
            previous = str(observed_digest)
            kind = receipt.get("kind")
            if kind == "program_complete":
                program_completed = True
            elif kind == "program_reject":
                program_reject_reason = str(receipt.get("error") or receipt.get("reason") or "")

            if kind in {
                "observe",
                "infer",
                "simulate",
                "inject",
                "communicate",
                "neural_proposal",
                "neural_admission",
                "neural_rejection",
            }:
                packet = receipt.get("packet")
                if isinstance(packet, dict):
                    self._install_packet(packet, expected_index)
                else:
                    self.fail("packet_receipt_payload", receipt_index=expected_index, kind=kind)
            elif kind in {"endorse", "authorize"}:
                self._apply_packet_mutation(receipt)
            elif kind in {"proof_construct", "trusted_attestation"}:
                proof = receipt.get("proof")
                if isinstance(proof, dict):
                    self._verify_proof(proof, expected_index)
                else:
                    self.fail("proof_receipt_payload", receipt_index=expected_index)
            elif kind in {"proof_use", "proof_consume"}:
                proof_name = str(receipt.get("proof"))
                proof = self.proofs.get(proof_name)
                if proof is None:
                    self.fail("proof_use_exists", receipt_index=expected_index, proof=proof_name)
                else:
                    if receipt.get("proof_digest") != proof.get("proof_digest"):
                        self.fail("proof_use_digest", receipt_index=expected_index, proof=proof_name)
                    mode = proof.get("resource_mode")
                    if receipt.get("resource_mode") != mode:
                        self.fail("proof_use_resource_mode", receipt_index=expected_index, proof=proof_name)
                    remaining = self.proof_remaining.get(proof_name)
                    if kind == "proof_use":
                        if mode != "persistent" or receipt.get("remaining_uses") is not None:
                            self.fail("persistent_proof_use", receipt_index=expected_index, proof=proof_name)
                    else:
                        if mode not in {"affine", "linear"}:
                            self.fail("linear_proof_consume_mode", receipt_index=expected_index, proof=proof_name)
                        if remaining is None or remaining <= 0:
                            self.fail("linear_proof_single_use", receipt_index=expected_index, proof=proof_name)
                        else:
                            expected_remaining = remaining - 1
                            if receipt.get("remaining_uses") != expected_remaining:
                                self.fail("linear_proof_remaining", receipt_index=expected_index, proof=proof_name)
                            self.proof_remaining[proof_name] = expected_remaining
            elif kind == "memory_write":
                record = receipt.get("record")
                if isinstance(record, dict):
                    self._verify_memory(record, expected_index)
                else:
                    self.fail("memory_receipt_payload", receipt_index=expected_index)
            elif kind == "capability_grant":
                agent = str(receipt.get("agent"))
                cap = receipt.get("capability")
                if not isinstance(cap, dict):
                    self.fail("capability_payload", receipt_index=expected_index)
                else:
                    expected_grant = digest(_capability_payload(agent, cap))
                    if cap.get("grant_digest") != expected_grant:
                        self.fail("capability_grant_digest", receipt_index=expected_index)
                    self.capabilities[(agent, str(cap.get("effect")))] = copy.deepcopy(cap)
            elif kind == "plan":
                action = receipt.get("action")
                if isinstance(action, dict):
                    self._verify_action_digest(action, expected_index)
                    self.actions[str(action.get("name"))] = copy.deepcopy(action)
                    self.counters.plans += 1
                else:
                    self.fail("plan_payload", receipt_index=expected_index)
            elif kind == "execute":
                action = receipt.get("action")
                if not isinstance(action, dict):
                    self.fail("execute_payload", receipt_index=expected_index)
                else:
                    self._verify_action_digest(action, expected_index)
                    prior = self.actions.get(str(action.get("name")))
                    if prior is None:
                        self.fail("execute_has_plan", receipt_index=expected_index)
                    else:
                        for field in ("agent", "packet_name", "effect", "required_proof"):
                            if action.get(field) != prior.get(field):
                                self.fail(
                                    "execute_plan_correspondence",
                                    receipt_index=expected_index,
                                    field=field,
                                )
                    if action.get("executed") is not True or not action.get("capability_digest"):
                        self.fail("execute_capability_binding", receipt_index=expected_index)
                    self.actions[str(action.get("name"))] = copy.deepcopy(action)
                    self.counters.executions += 1
            elif kind == "feedback":
                action = receipt.get("action")
                if not isinstance(action, dict):
                    self.fail("feedback_payload", receipt_index=expected_index)
                else:
                    self._verify_action_digest(action, expected_index)
                    prior = self.actions.get(str(action.get("name")))
                    if prior is None or prior.get("executed") is not True:
                        self.fail("feedback_has_execution", receipt_index=expected_index)
                    if action.get("observed") is None:
                        self.fail("feedback_has_observation", receipt_index=expected_index)
                    expected_error = (
                        None
                        if action.get("expected") is None
                        else float(action["observed"]) - float(action["expected"])
                    )
                    observed_error = receipt.get("prediction_error")
                    if expected_error is None:
                        if observed_error is not None:
                            self.fail("prediction_error", receipt_index=expected_index)
                    elif observed_error is None or not math.isclose(
                        float(observed_error), expected_error, rel_tol=0.0, abs_tol=1e-12
                    ):
                        self.fail("prediction_error", receipt_index=expected_index)
                    self.actions[str(action.get("name"))] = copy.deepcopy(action)
                    self.counters.feedbacks += 1
            elif kind == "session_declare":
                session = receipt.get("session", {})
                if isinstance(session, dict):
                    name = str(session.get("name"))
                    self.session_initial[name] = str(session.get("initial_state"))
                    self.session_terminals[name] = set(session.get("terminal_states", []))
            elif kind == "session_transition_declare":
                key = (
                    str(receipt.get("session")),
                    str(receipt.get("source_state")),
                    str(receipt.get("event")),
                    str(receipt.get("sender")),
                    str(receipt.get("receiver")),
                )
                self.session_transitions[key] = str(receipt.get("target_state"))
            elif kind == "session_terminal_declare":
                self.session_terminals.setdefault(str(receipt.get("session")), set()).add(
                    str(receipt.get("state"))
                )
            elif kind == "session_verify":
                report = receipt.get("report")
                if isinstance(report, dict):
                    self._verify_session_report(report, expected_index)
                else:
                    self.fail("session_report_payload", receipt_index=expected_index)
            elif kind == "session_start":
                session = receipt.get("session", {})
                if isinstance(session, dict):
                    self.session_state[str(session.get("name"))] = str(
                        session.get("current_state")
                    )
            elif kind == "session_advance":
                session = str(receipt.get("session"))
                current = self.session_state.get(session)
                if current != receipt.get("source_state"):
                    self.fail("session_source_state", receipt_index=expected_index)
                key = (
                    session,
                    str(receipt.get("source_state")),
                    str(receipt.get("event")),
                    str(receipt.get("sender")),
                    str(receipt.get("receiver")),
                )
                expected_target = self.session_transitions.get(key)
                if expected_target != receipt.get("target_state"):
                    self.fail("session_declared_transition", receipt_index=expected_index)
                self.session_state[session] = str(receipt.get("target_state"))
                self.counters.session_advances += 1
            elif kind == "transaction_begin":
                name = str(receipt.get("transaction"))
                if name in self.active_transactions:
                    self.fail("transaction_non_nested", receipt_index=expected_index)
                self.active_transactions[name] = {
                    "begin_index": expected_index,
                    "begin_step": receipt.get("step"),
                    "checkpoint_digest": receipt.get("checkpoint_digest"),
                }
                self.counters.transaction_begins += 1
            elif kind == "transaction_commit":
                name = str(receipt.get("transaction"))
                begin = self.active_transactions.pop(name, None)
                if begin is None:
                    self.fail("transaction_commit_has_begin", receipt_index=expected_index)
                elif receipt.get("begin_step") != begin.get("begin_step"):
                    self.fail("transaction_commit_begin_step", receipt_index=expected_index)
                self.counters.transaction_commits += 1
            elif kind == "transaction_rollback":
                name = str(receipt.get("transaction"))
                begin = self.active_transactions.pop(name, None)
                if begin is None:
                    self.fail("transaction_rollback_has_begin", receipt_index=expected_index)
                else:
                    if receipt.get("checkpoint_digest") != begin.get("checkpoint_digest"):
                        self.fail("transaction_checkpoint_correspondence", receipt_index=expected_index)
                    self.rolled_back_ranges.append(
                        (int(begin["begin_index"]), expected_index, name)
                    )
                self.counters.transaction_rollbacks += 1

        if self.active_transactions:
            self.fail("transactions_closed", active=sorted(self.active_transactions))

        # Every persistent final memory/action must have a matching committed
        # receipt.  Rolled-back receipt segments are retained in the audit log
        # but are intentionally excluded from this final-state correspondence.
        rolled_indices: set[int] = set()
        for begin, end, _name in self.rolled_back_ranges:
            rolled_indices.update(range(begin, end))
        committed = [
            receipt
            for receipt in receipts
            if int(receipt.get("index", -1)) not in rolled_indices
        ]
        committed_memory_digests = {
            receipt.get("record", {}).get("record_digest")
            for receipt in committed
            if receipt.get("kind") == "memory_write"
        }
        for records in final_state.get("memories", {}).values():
            for record in records:
                if record.get("record_digest") not in committed_memory_digests:
                    self.fail(
                        "final_memory_receipt_correspondence",
                        record_digest=record.get("record_digest"),
                    )
        committed_action_receipts = {
            (receipt.get("kind"), receipt.get("action", {}).get("action_digest"))
            for receipt in committed
            if receipt.get("kind") in {"plan", "execute", "feedback"}
        }
        for action in final_state.get("actions", {}).values():
            kind = "feedback" if action.get("observed") is not None else (
                "execute" if action.get("executed") else "plan"
            )
            if (kind, action.get("action_digest")) not in committed_action_receipts:
                self.fail(
                    "final_action_receipt_correspondence",
                    action=action.get("name"),
                    expected_kind=kind,
                )

        for name, proof in final_state.get("proofs", {}).items():
            mode = proof.get("resource_mode")
            remaining = proof.get("remaining_uses")
            if mode == "linear" and remaining not in {0, None}:
                expected_rejection = (
                    not program_completed
                    and program_reject_reason is not None
                    and "linear proofs must be consumed exactly once" in program_reject_reason
                )
                if not expected_rejection:
                    self.fail("linear_proof_final_consumption", proof=name, remaining=remaining)
            if name in self.proof_remaining and remaining != self.proof_remaining[name]:
                self.fail(
                    "proof_resource_final_correspondence",
                    proof=name,
                    kernel_remaining=self.proof_remaining[name],
                    runtime_remaining=remaining,
                )

        checks = {
            "hash_chain": not any(
                failure["property"] in {"receipt_index", "receipt_hash_chain", "receipt_digest"}
                for failure in self.failures
            ),
            "packet_integrity": not any(
                failure["property"].startswith("packet_") for failure in self.failures
            ),
            "proof_kernel": not any(
                failure["property"].startswith("proof_")
                or failure["property"].endswith("_proof")
                for failure in self.failures
            ),
            "provenance_nonforging": not any(
                failure["property"] in {
                    "memory_provenance_compatibility",
                    "observed_memory_nonforging",
                }
                for failure in self.failures
            ),
            "action_trace_correspondence": not any(
                failure["property"].startswith(("action_", "execute_", "feedback_", "prediction_"))
                or failure["property"] == "final_action_receipt_correspondence"
                for failure in self.failures
            ),
            "session_fidelity": not any(
                failure["property"].startswith("session_") for failure in self.failures
            ),
            "transaction_correspondence": not any(
                failure["property"].startswith("transaction_") for failure in self.failures
            ),
            "final_state_correspondence": not any(
                failure["property"].startswith("final_") for failure in self.failures
            ),
        }
        payload: dict[str, Any] = {
            "schema": "osl.kernel.verification.v1",
            "checks": checks,
            "all_checks_pass": all(checks.values()) and not self.failures,
            "counters": self.counters.__dict__,
            "failure_count": len(self.failures),
            "failures": self.failures,
            "audit_head_digest": previous if receipts else None,
            "rolled_back_transaction_count": len(self.rolled_back_ranges),
            "claim_boundary": (
                "The kernel verifies the finite receipt and proof rules encoded here. "
                "It does not authenticate principals, prove the Python runtime correct, "
                "or establish security for language features outside this kernel."
            ),
        }
        payload["verification_digest"] = digest(payload)
        return payload


def verify_program(path: Path) -> dict[str, Any]:
    try:
        from .osl_core import OSLRuntime, OSLError, OSLStaticError
    except ImportError:
        from osl_core import OSLRuntime, OSLError, OSLStaticError  # type: ignore

    runtime = OSLRuntime()
    runtime_error: str | None = None
    try:
        runtime.run_file(path)
    except (OSLError, OSLStaticError) as exc:
        runtime_error = str(exc)
    report = KernelVerifier().verify(runtime.audit_log, runtime.state.snapshot())
    report.update(
        {
            "file": str(path),
            "runtime_accepted": runtime_error is None,
            "runtime_error": runtime_error,
        }
    )
    report["program_verification_digest"] = digest(report)
    return report


def verify_directory(directory: Path) -> dict[str, Any]:
    records = [verify_program(path) for path in sorted(directory.glob("*.osl"))]
    payload: dict[str, Any] = {
        "schema": "osl.kernel.suite.v1",
        "language_version": "OSL-Core 0.3",
        "program_count": len(records),
        "verified_program_count": sum(record["all_checks_pass"] for record in records),
        "receipt_count": sum(record["counters"]["receipts"] for record in records),
        "proof_count": sum(record["counters"]["proofs"] for record in records),
        "memory_record_count": sum(
            record["counters"]["memory_records"] for record in records
        ),
        "transaction_rollback_count": sum(
            record["counters"]["transaction_rollbacks"] for record in records
        ),
        "records": records,
    }
    payload["all_checks_pass"] = bool(
        records and all(record["all_checks_pass"] for record in records)
    )
    payload["suite_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.path.is_dir():
        result = verify_directory(args.path)
    else:
        result = verify_program(args.path)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
