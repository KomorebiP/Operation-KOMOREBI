#!/usr/bin/env python3
"""Source-bound independent protected-state verifier for OSL-Core 0.5.

The verifier treats the receipt chain as untrusted input, requires its exact
source, and independently reconstructs the finite packet, proof, memory,
capability, action, identity, and protected rollback state. A separately
labeled same-runtime replay supplements that independent core for delegated
numerical, session, and complete interpreter behavior.

SHA-256 here is a content-integrity primitive, not principal authentication.
The verifier therefore rejects semantically invalid traces even when an
attacker has consistently recomputed every public digest.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


CORE_VERSION = "0.5"
RECEIPT_SCHEMA = "osl.core.receipt.v2"
ZERO_DIGEST = "0" * 64

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

EFFECTS = {
    "read",
    "writeMemory",
    "communicate",
    "toolCall",
    "externalAct",
    "simulate",
    "modifyModel",
}

PROOF_KINDS = {
    "access",
    "origin",
    "clear",
    "endorsement",
    "authorization",
    "observation",
    "relevance",
    "use",
    "ownership",
    "capability",
}

PROOF_MODES = {"persistent", "affine", "linear"}

LIFECYCLE_KINDS = {
    "program_open",
    "parse_accept",
    "parse_reject",
    "static_check",
    "static_reject",
    "statement_commit",
    "statement_reject",
    "program_complete",
    "program_reject",
}

SEMANTIC_RECEIPT_KINDS = {
    "module_declare",
    "lineage_declare",
    "agent_declare",
    "capability_grant",
    "capability_revoke",
    "space_declare",
    "vector_declare",
    "operator",
    "operator_apply",
    "transport",
    "projector_check",
    "intertwiner_check",
    "observe",
    "infer",
    "simulate",
    "inject",
    "neural_proposal",
    "communicate",
    "bind",
    "quarantine",
    "endorse",
    "authorize",
    "trusted_attestation",
    "neural_admission",
    "neural_rejection",
    "proof_construct",
    "proof_use",
    "proof_consume",
    "memory_write",
    "plan",
    "execute",
    "feedback",
    "contract_declare",
    "contract_check",
    "receipt_chain_verify",
    "transaction_begin",
    "transaction_commit",
    "transaction_rollback",
    "session_declare",
    "session_transition_declare",
    "session_terminal_declare",
    "session_verify",
    "session_start",
    "session_advance",
    "secret_register",
    "metadata_publish",
    "assert_pass",
    "show",
}

KNOWN_RECEIPT_KINDS = LIFECYCLE_KINDS | SEMANTIC_RECEIPT_KINDS

PRIMARY_RECEIPT: dict[str, str] = {
    "module": "module_declare",
    "lineage": "lineage_declare",
    "agent": "agent_declare",
    "grant": "capability_grant",
    "revoke": "capability_revoke",
    "space": "space_declare",
    "vector": "vector_declare",
    "operator": "operator",
    "apply": "operator_apply",
    "transport": "transport",
    "check_projector": "projector_check",
    "check_intertwiner": "intertwiner_check",
    "observe": "observe",
    "infer": "infer",
    "simulate": "simulate",
    "inject": "inject",
    "neural_propose": "neural_proposal",
    "communicate": "communicate",
    "bind": "bind",
    "quarantine": "quarantine",
    "endorse": "endorse",
    "authorize": "authorize",
    "proof": "proof_construct",
    "attest_origin": "trusted_attestation",
    "attest_relevance": "trusted_attestation",
    "admit": "neural_admission",
    "reject_candidate": "neural_rejection",
    "write_memory": "memory_write",
    "plan": "plan",
    "execute": "execute",
    "feedback": "feedback",
    "contract": "contract_declare",
    "check_contracts": "contract_check",
    "verify_receipts": "receipt_chain_verify",
    "begin_transaction": "transaction_begin",
    "commit_transaction": "transaction_commit",
    "rollback_transaction": "transaction_rollback",
    "session": "session_declare",
    "session_transition": "session_transition_declare",
    "session_terminal": "session_terminal_declare",
    "verify_session": "session_verify",
    "start_session": "session_start",
    "secret": "secret_register",
    "metadata": "metadata_publish",
    "assert": "assert_pass",
    "show": "show",
}

SEMANTIC_KEYS = (
    "module",
    "agents",
    "lineage_parents",
    "spaces",
    "operators",
    "vectors",
    "packets",
    "proofs",
    "memories",
    "actions",
    "capabilities",
    "contracts",
    "sessions",
    "metadata",
    "secret_digests",
    "assertions",
    "step",
)


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
    return {
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


def _capability_payload(agent: str, capability: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent": agent,
        "effect": capability.get("effect"),
        "initial_uses": capability.get("initial_uses"),
        "expires_at": capability.get("expires_at"),
        "source": capability.get("source"),
        "grant_index": capability.get("grant_index"),
        "issued_step": capability.get("issued_step"),
    }


def _semantic_projection(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = {key: copy.deepcopy(snapshot.get(key)) for key in SEMANTIC_KEYS}
    metadata = snapshot.get("metadata", {})
    payload["metadata"] = {
        name: {
            "source": value.get("source"),
            "step": value.get("step"),
            "digest": value.get("digest"),
        }
        for name, value in sorted(metadata.items())
        if isinstance(value, dict)
    }
    payload["semantic_digest"] = digest(payload)
    return payload


def _manifest(statement: Any, ordinal: int) -> dict[str, Any]:
    payload = {
        "ordinal": ordinal,
        "line_number": statement.line_number,
        "kind": statement.kind,
        "source": statement.source,
        "args": statement.args,
    }
    payload["node_digest"] = digest(payload)
    return payload


def _same_number(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
    return left == right


def _is_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass
class KernelCounters:
    receipts: int = 0
    packets: int = 0
    proofs: int = 0
    memory_records: int = 0
    capability_grants: int = 0
    capability_revocations: int = 0
    plans: int = 0
    executions: int = 0
    feedbacks: int = 0
    statement_boundaries: int = 0
    transaction_begins: int = 0
    transaction_commits: int = 0
    transaction_rollbacks: int = 0


class KernelVerifier:
    """Independent, fail-closed verifier for the OSL-Core 0.5 receipt grammar."""

    def __init__(self) -> None:
        self.failures: list[dict[str, Any]] = []
        self.counters = KernelCounters()
        self.module: str | None = None
        self.lineages: dict[str, str | None] = {}
        self.agents: dict[str, dict[str, Any]] = {}
        self.packets: dict[str, dict[str, Any]] = {}
        self.packet_by_digest: dict[str, dict[str, Any]] = {}
        self.proofs: dict[str, dict[str, Any]] = {}
        self.proof_by_digest: dict[str, dict[str, Any]] = {}
        self.capabilities: dict[tuple[str, str], dict[str, Any]] = {}
        self.actions: dict[str, dict[str, Any]] = {}
        self.memories: dict[str, list[dict[str, Any]]] = {}
        self.secret_digests: dict[str, str] = {}
        self.private_secrets: dict[str, str] = {}
        self.active_transaction: dict[str, Any] | None = None
        self.receipt_statement: dict[int, Any] = {}
        self.proof_events_by_statement: dict[int, list[dict[str, Any]]] = {}
        self.statements: tuple[Any, ...] = ()
        self.manifests: tuple[dict[str, Any], ...] = ()
        self.source_digest: str | None = None
        self.ast_digest: str | None = None
        self.static_report: dict[str, Any] | None = None
        self.source_parse_error: str | None = None
        self.supplementary_replay: dict[str, Any] = {
            "performed": False,
            "receipt_match": False,
            "final_state_match": False,
            "runtime_outcome": None,
        }

    def fail(self, property_name: str, **details: Any) -> None:
        self.failures.append({"property": property_name, **details})

    def _expect(self, condition: bool, property_name: str, **details: Any) -> bool:
        if not condition:
            self.fail(property_name, **details)
        return condition

    def _statement(self, receipt: dict[str, Any]) -> Any | None:
        return self.receipt_statement.get(int(receipt.get("index", -1)))

    def _proof_events(self, statement: Any | None) -> list[dict[str, Any]]:
        return [] if statement is None else self.proof_events_by_statement.get(id(statement), [])

    def _validate_gate_proof_event(
        self,
        *,
        statement: Any | None,
        proof_name: Any,
        gate_index: int,
        property_name: str,
    ) -> None:
        events = self._proof_events(statement)
        if proof_name is None:
            self._expect(not events, property_name, receipt_index=gate_index)
            return
        proof = self.proofs.get(str(proof_name))
        expected_kind = (
            "proof_use"
            if proof is not None and proof.get("resource_mode") == "persistent"
            else "proof_consume"
        )
        self._expect(
            len(events) == 1
            and events[0].get("proof") == proof_name
            and events[0].get("kind") == expected_kind
            and events[0].get("index") == gate_index - 1,
            property_name,
            receipt_index=gate_index,
            proof=proof_name,
        )

    def _packet_digest_valid(self, packet: dict[str, Any], index: int) -> bool:
        content_digest = digest(_packet_content_payload(packet))
        state_digest = digest(_packet_state_payload(packet))
        ok = True
        if packet.get("content_digest") != content_digest:
            self.fail("packet_content_digest", receipt_index=index, packet=packet.get("name"))
            ok = False
        if packet.get("packet_digest") != state_digest:
            self.fail("packet_state_digest", receipt_index=index, packet=packet.get("name"))
            ok = False
        return ok

    def _set_packet(self, packet: dict[str, Any]) -> None:
        record = copy.deepcopy(packet)
        self.packets[str(record.get("name"))] = record
        if record.get("packet_digest"):
            self.packet_by_digest[str(record["packet_digest"])] = copy.deepcopy(record)

    def _packet_list(self, packet: dict[str, Any], field: str) -> set[str]:
        return {str(item) for item in packet.get(field, [])}

    @staticmethod
    def _canonical_new_packet(
        *,
        name: Any,
        content: Any,
        source_agent: Any,
        source_lineage: Any,
        provenance: str,
        confidence: Any,
        accessible_to: set[str],
        bound_to: set[str] | None = None,
        quarantined_by: set[str] | None = None,
        observation_tokens: set[str] | None = None,
        simulated: bool = False,
        parent_digest: Any = None,
        status: str = "grounded",
        latent_source: Any = None,
        obligations: set[str] | None = None,
    ) -> dict[str, Any]:
        """Recreate ``Packet.canonical`` without importing the runtime model."""

        bounded = set() if bound_to is None else bound_to
        quarantined = set() if quarantined_by is None else quarantined_by
        observed = set() if observation_tokens is None else observation_tokens
        required = set() if obligations is None else obligations
        rounded_confidence = round(float(confidence), 12)
        return {
            "name": name,
            "content": content,
            "source_agent": source_agent,
            "source_lineage": source_lineage,
            "provenance": provenance,
            "confidence": rounded_confidence,
            "simulated": simulated,
            "parent_digest": parent_digest,
            "latent_source": latent_source,
            "accessible_to": sorted(accessible_to),
            "bound_to": sorted(bounded),
            "quarantined_by": sorted(quarantined),
            "endorsed_by": [],
            "authorizations": {},
            "observation_tokens": sorted(observed),
            "status": status,
            "obligations": sorted(required),
            "support": rounded_confidence,
            "refutation": 0.0,
            "unresolved": round(max(0.0, 1.0 - rounded_confidence), 12),
        }

    def _validate_packet_constructor(
        self, kind: str, receipt: dict[str, Any], packet: dict[str, Any]
    ) -> None:
        index = int(receipt.get("index", -1))
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args
        name = str(packet.get("name"))
        expected_constructor: dict[str, Any] | None = None
        if name in self.packets and kind not in {"neural_admission", "neural_rejection"}:
            self.fail("packet_unique_constructor", receipt_index=index, packet=name)
        self._packet_digest_valid(packet, index)

        if kind == "observe":
            agent = str(packet.get("source_agent"))
            lineage = self.agents.get(agent, {}).get("lineage")
            expected = {
                "provenance": "observed",
                "simulated": False,
                "source_lineage": lineage,
                "status": "grounded",
                "parent_digest": None,
                "latent_source": None,
            }
            for field, value in expected.items():
                self._expect(packet.get(field) == value, "observe_constructor", receipt_index=index, field=field)
            self._expect(self._packet_list(packet, "accessible_to") == {agent}, "observe_access", receipt_index=index)
            self._expect(self._packet_list(packet, "bound_to") == {agent}, "observe_binding", receipt_index=index)
            self._expect(self._packet_list(packet, "observation_tokens") == {agent}, "observe_token", receipt_index=index)
            self._expect(not self._packet_list(packet, "quarantined_by"), "observe_quarantine", receipt_index=index)
            if args:
                for field, value in (("name", args.get("name")), ("content", args.get("content")), ("confidence", args.get("confidence"))):
                    self._expect(_same_number(packet.get(field), value), "observe_source_correspondence", receipt_index=index, field=field)
                self._expect(agent == args.get("agent"), "observe_source_agent", receipt_index=index)
                expected_constructor = self._canonical_new_packet(
                    name=args.get("name"),
                    content=args.get("content"),
                    source_agent=args.get("agent"),
                    source_lineage=lineage,
                    provenance="observed",
                    confidence=args.get("confidence"),
                    accessible_to={agent},
                    bound_to={agent},
                    observation_tokens={agent},
                )

        elif kind == "simulate":
            agent = str(packet.get("source_agent"))
            lineage = self.agents.get(agent, {}).get("lineage")
            for field, value in {
                "provenance": "simulated",
                "simulated": True,
                "source_lineage": lineage,
                "status": "grounded",
                "parent_digest": None,
            }.items():
                self._expect(packet.get(field) == value, "simulate_constructor", receipt_index=index, field=field)
            self._expect(self._packet_list(packet, "accessible_to") == {agent}, "simulate_access", receipt_index=index)
            self._expect(self._packet_list(packet, "bound_to") == {agent}, "simulate_binding", receipt_index=index)
            self._expect(not self._packet_list(packet, "observation_tokens"), "simulate_token", receipt_index=index)
            if args:
                self._expect(agent == args.get("agent"), "simulate_source_agent", receipt_index=index)
                self._expect(packet.get("name") == args.get("name"), "simulate_source_name", receipt_index=index)
                self._expect(packet.get("content") == args.get("content"), "simulate_source_content", receipt_index=index)
                expected_constructor = self._canonical_new_packet(
                    name=args.get("name"),
                    content=args.get("content"),
                    source_agent=args.get("agent"),
                    source_lineage=lineage,
                    provenance="simulated",
                    confidence=args.get("confidence"),
                    accessible_to={agent},
                    bound_to={agent},
                    simulated=True,
                )

        elif kind == "inject":
            target = str(receipt.get("target"))
            for field, value in {
                "source_agent": "external",
                "source_lineage": "external",
                "provenance": "injected",
                "simulated": False,
                "status": "quarantined",
                "parent_digest": None,
            }.items():
                self._expect(packet.get(field) == value, "inject_constructor", receipt_index=index, field=field)
            self._expect(self._packet_list(packet, "accessible_to") == {target}, "inject_access", receipt_index=index)
            self._expect(self._packet_list(packet, "bound_to") == set(), "inject_binding", receipt_index=index)
            self._expect(self._packet_list(packet, "quarantined_by") == {target}, "inject_quarantine", receipt_index=index)
            self._expect(not self._packet_list(packet, "observation_tokens"), "inject_token", receipt_index=index)
            if args:
                self._expect(target == args.get("agent"), "inject_source_target", receipt_index=index)
                self._expect(packet.get("name") == args.get("name"), "inject_source_name", receipt_index=index)
                self._expect(packet.get("content") == args.get("content"), "inject_source_content", receipt_index=index)
                expected_constructor = self._canonical_new_packet(
                    name=args.get("name"),
                    content=args.get("content"),
                    source_agent="external",
                    source_lineage="external",
                    provenance="injected",
                    confidence=args.get("confidence"),
                    accessible_to={target},
                    quarantined_by={target},
                    status="quarantined",
                )

        elif kind == "neural_proposal":
            target = str(receipt.get("target"))
            self._expect(target in self.agents, "neural_proposal_target_exists", receipt_index=index)
            for field, value in {
                "source_agent": "unresolved",
                "source_lineage": "unresolved",
                "provenance": "unresolved",
                "simulated": False,
                "status": "provisional",
                "parent_digest": None,
            }.items():
                self._expect(packet.get(field) == value, "neural_proposal_constructor", receipt_index=index, field=field)
            self._expect(self._packet_list(packet, "accessible_to") == {target}, "neural_proposal_access", receipt_index=index)
            self._expect(self._packet_list(packet, "quarantined_by") == {target}, "neural_proposal_quarantine", receipt_index=index)
            self._expect(self._packet_list(packet, "obligations") == {"origin", "lineage", "task_relevance"}, "neural_proposal_obligations", receipt_index=index)
            if args:
                self._expect(target == args.get("agent"), "neural_proposal_source_target", receipt_index=index)
                self._expect(packet.get("latent_source") == args.get("feature"), "neural_proposal_feature", receipt_index=index)
                self._expect(packet.get("name") == args.get("name"), "neural_proposal_name", receipt_index=index)
                expected_constructor = self._canonical_new_packet(
                    name=args.get("name"),
                    content=args.get("content"),
                    source_agent="unresolved",
                    source_lineage="unresolved",
                    provenance="unresolved",
                    confidence=args.get("confidence"),
                    accessible_to={target},
                    quarantined_by={target},
                    status="provisional",
                    latent_source=args.get("feature"),
                    obligations={"origin", "lineage", "task_relevance"},
                )

        elif kind == "infer":
            parent = self.packet_by_digest.get(str(packet.get("parent_digest")))
            agent = str(packet.get("source_agent"))
            self._expect(parent is not None, "infer_parent_exists", receipt_index=index)
            if parent is not None:
                self._expect(parent.get("status") in {"grounded", "admitted"}, "infer_parent_status", receipt_index=index)
                self._expect(agent in self._packet_list(parent, "accessible_to"), "infer_parent_access", receipt_index=index)
            self._expect(packet.get("provenance") == "inferred", "infer_provenance", receipt_index=index)
            self._expect(packet.get("source_lineage") == self.agents.get(agent, {}).get("lineage"), "infer_lineage", receipt_index=index)
            self._expect(self._packet_list(packet, "accessible_to") == {agent}, "infer_access", receipt_index=index)
            self._expect(self._packet_list(packet, "bound_to") == {agent}, "infer_binding", receipt_index=index)
            self._expect(not self._packet_list(packet, "observation_tokens"), "infer_token", receipt_index=index)
            if args:
                source_packet = self.packets.get(str(args.get("source_packet")))
                self._expect(source_packet is not None and packet.get("parent_digest") == source_packet.get("packet_digest"), "infer_source_parent", receipt_index=index)
                self._expect(agent == args.get("agent"), "infer_source_agent", receipt_index=index)
                self._expect(packet.get("name") == args.get("name"), "infer_source_name", receipt_index=index)
                self._expect(packet.get("content") == args.get("content"), "infer_source_content", receipt_index=index)
                expected_constructor = self._canonical_new_packet(
                    name=args.get("name"),
                    content=args.get("content"),
                    source_agent=args.get("agent"),
                    source_lineage=self.agents.get(str(args.get("agent")), {}).get("lineage"),
                    provenance="inferred",
                    confidence=args.get("confidence"),
                    accessible_to={agent},
                    bound_to={agent},
                    parent_digest=(
                        None if source_packet is None else source_packet.get("packet_digest")
                    ),
                )

        elif kind == "communicate":
            parent = self.packet_by_digest.get(str(packet.get("parent_digest")))
            sender = str(receipt.get("from_agent"))
            target = str(receipt.get("to_agent"))
            self._expect(parent is not None, "communicate_parent_exists", receipt_index=index)
            if parent is not None:
                for field in ("content", "source_agent", "source_lineage", "confidence"):
                    self._expect(packet.get(field) == parent.get(field), "communicate_source_preservation", receipt_index=index, field=field)
                self._expect(sender in self._packet_list(parent, "accessible_to"), "communicate_sender_access", receipt_index=index)
                self._expect(parent.get("status") in {"grounded", "admitted"}, "communicate_parent_status", receipt_index=index)
            self._expect(packet.get("provenance") == "communicated", "communicate_provenance", receipt_index=index)
            self._expect(packet.get("status") == "grounded", "communicate_status", receipt_index=index)
            self._expect(self._packet_list(packet, "accessible_to") == {target}, "communicate_access", receipt_index=index)
            self._expect(self._packet_list(packet, "bound_to") == {target}, "communicate_binding", receipt_index=index)
            self._expect(not self._packet_list(packet, "observation_tokens"), "communicate_token_nontransfer", receipt_index=index)
            self._expect(not self._packet_list(packet, "quarantined_by"), "communicate_quarantine_nonlaundering", receipt_index=index)
            if args:
                source_packet = self.packets.get(str(args.get("source_packet")))
                self._expect(source_packet is not None and packet.get("parent_digest") == source_packet.get("packet_digest"), "communicate_source_parent", receipt_index=index)
                self._expect(sender == args.get("source_agent") and target == args.get("target_agent"), "communicate_source_agents", receipt_index=index)
                self._expect(packet.get("name") == args.get("target_packet"), "communicate_source_name", receipt_index=index)
                self._expect(receipt.get("session") == args.get("session"), "communicate_source_session", receipt_index=index)
                if source_packet is not None:
                    expected_constructor = self._canonical_new_packet(
                        name=args.get("target_packet"),
                        content=source_packet.get("content"),
                        source_agent=source_packet.get("source_agent"),
                        source_lineage=source_packet.get("source_lineage"),
                        provenance="communicated",
                        confidence=source_packet.get("confidence"),
                        accessible_to={target},
                        bound_to={target},
                        parent_digest=source_packet.get("packet_digest"),
                    )

        if expected_constructor is not None:
            expected_keys = set(expected_constructor) | {"content_digest", "packet_digest"}
            self._expect(
                set(packet) == expected_keys,
                "packet_constructor_schema",
                receipt_index=index,
                packet=name,
            )
            for field, value in expected_constructor.items():
                comparison = (
                    _same_number(packet.get(field), value)
                    if field in {"confidence", "support", "refutation", "unresolved"}
                    else packet.get(field) == value
                )
                self._expect(
                    comparison,
                    "packet_constructor_exact",
                    receipt_index=index,
                    packet=name,
                    field=field,
                )

        self._set_packet(packet)
        self.counters.packets += 1

    def _apply_packet_mutation(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        kind = str(receipt.get("kind"))
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args
        self._expect(
            statement is not None and statement.kind == kind,
            "packet_mutation_source_kind",
            receipt_index=index,
            kind=kind,
        )
        name = receipt.get("packet")
        if not isinstance(name, str) or name not in self.packets:
            self.fail("packet_mutation_subject", receipt_index=index, kind=kind)
            return
        packet = copy.deepcopy(self.packets[name])
        agent = str(receipt.get("agent"))
        self._expect(agent in self.agents, "packet_mutation_agent_exists", receipt_index=index, kind=kind)
        self._expect(
            name == args.get("packet") and agent == args.get("agent"),
            "packet_mutation_source_correspondence",
            receipt_index=index,
            kind=kind,
        )
        if kind == "bind":
            self._expect(agent in self._packet_list(packet, "accessible_to"), "bind_access", receipt_index=index)
            packet["bound_to"] = sorted(self._packet_list(packet, "bound_to") | {agent})
        elif kind == "quarantine":
            packet["quarantined_by"] = sorted(self._packet_list(packet, "quarantined_by") | {agent})
            packet["status"] = "quarantined"
        elif kind == "endorse":
            self._expect(agent in self._packet_list(packet, "accessible_to"), "endorse_access", receipt_index=index)
            self._expect(agent not in self._packet_list(packet, "quarantined_by"), "endorse_clear", receipt_index=index)
            self._expect(packet.get("status") in {"grounded", "admitted"}, "endorse_status", receipt_index=index)
            threshold = receipt.get("threshold")
            self._expect(_same_number(threshold, args.get("threshold")), "endorse_source_threshold", receipt_index=index)
            self._expect(float(packet.get("confidence", 0.0)) >= float(threshold), "endorse_threshold", receipt_index=index)
            packet["endorsed_by"] = sorted(self._packet_list(packet, "endorsed_by") | {agent})
        elif kind == "authorize":
            self._expect(agent in self._packet_list(packet, "accessible_to"), "authorize_access", receipt_index=index)
            self._expect(agent in self._packet_list(packet, "bound_to"), "authorize_binding", receipt_index=index)
            self._expect(agent not in self._packet_list(packet, "quarantined_by"), "authorize_clear", receipt_index=index)
            self._expect(packet.get("status") in {"grounded", "admitted"}, "authorize_status", receipt_index=index)
            self._expect(receipt.get("scope") == args.get("scope"), "authorize_source_scope", receipt_index=index)
            self._expect(receipt.get("proof") == args.get("proof"), "authorize_source_proof", receipt_index=index)
            if args.get("proof") is not None:
                proof = self.proofs.get(str(args.get("proof")))
                self._expect(
                    proof is not None
                    and proof.get("subject") == name
                    and proof.get("subject_digest") == packet.get("content_digest")
                    and proof.get("agent") in {None, agent}
                    and self._proof_semantically_valid(
                        proof,
                        step=int(receipt.get("step", -1)),
                        require_available=False,
                    ),
                    "authorize_proof_binding",
                    receipt_index=index,
                )
            self._validate_gate_proof_event(
                statement=statement,
                proof_name=args.get("proof"),
                gate_index=index,
                property_name="authorize_proof_gate",
            )
            authorizations = {
                key: list(value) for key, value in packet.get("authorizations", {}).items()
            }
            authorizations.setdefault(agent, [])
            authorizations[agent] = sorted(set(authorizations[agent]) | {receipt.get("scope")})
            packet["authorizations"] = authorizations
        expected = digest(_packet_state_payload(packet))
        self._expect(receipt.get("packet_digest") == expected, "packet_mutation_digest", receipt_index=index, kind=kind)
        packet["packet_digest"] = expected
        self._set_packet(packet)

    def _proof_semantically_valid(
        self, proof: dict[str, Any], *, step: int, require_available: bool = True
    ) -> bool:
        mode = proof.get("resource_mode")
        if require_available and mode in {"affine", "linear"}:
            remaining = proof.get("remaining_uses")
            if not isinstance(remaining, int) or remaining <= 0:
                return False
        kind = proof.get("kind")
        if kind == "capability":
            key = (str(proof.get("agent")), str(proof.get("scope")))
            capability = self.capabilities.get(key)
            if capability is None:
                return False
            expires = capability.get("expires_at")
            remaining = capability.get("remaining_uses")
            return bool(
                proof.get("subject") == key[1]
                and tuple(proof.get("claims", ()))
                == ("capability_available", capability.get("grant_digest"))
                and (expires is None or step <= int(expires))
                and (remaining is None or int(remaining) > 0)
            )
        packet = self.packets.get(str(proof.get("subject")))
        if packet is None or proof.get("subject_digest") != packet.get("content_digest"):
            return False
        agent = proof.get("agent")
        if kind == "access":
            return agent in self._packet_list(packet, "accessible_to")
        if kind == "origin":
            if proof.get("trusted") and packet.get("status") == "provisional":
                return True
            return bool(
                proof.get("source_agent") == packet.get("source_agent")
                and proof.get("source_lineage") == packet.get("source_lineage")
            )
        if kind == "clear":
            return agent not in self._packet_list(packet, "quarantined_by")
        if kind == "endorsement":
            return agent in self._packet_list(packet, "endorsed_by")
        if kind == "authorization":
            return proof.get("scope") in packet.get("authorizations", {}).get(agent, [])
        if kind == "observation":
            return bool(
                agent in self._packet_list(packet, "observation_tokens")
                and packet.get("source_agent") == agent
                and packet.get("source_lineage") == self.agents.get(str(agent), {}).get("lineage")
            )
        if kind == "relevance":
            return bool(proof.get("trusted") and packet.get("status") == "provisional")
        if kind in {"use", "ownership"}:
            if proof.get("state_digest") != packet.get("packet_digest"):
                return False
            premises = [self.proofs.get(str(name)) for name in proof.get("premises", [])]
            if any(term is None for term in premises):
                return False
            if not all(
                self._proof_semantically_valid(term, step=step, require_available=False)
                for term in premises
                if term is not None
            ):
                return False
            if kind == "use":
                scopes = packet.get("authorizations", {}).get(agent, [])
                return bool(
                    agent in self._packet_list(packet, "accessible_to")
                    and agent in self._packet_list(packet, "bound_to")
                    and agent not in self._packet_list(packet, "quarantined_by")
                    and agent in self._packet_list(packet, "endorsed_by")
                    and (proof.get("scope") in scopes or "planning" in scopes)
                )
            memory_class = str(proof.get("memory_class"))
            return bool(
                agent in self._packet_list(packet, "accessible_to")
                and agent in self._packet_list(packet, "bound_to")
                and agent not in self._packet_list(packet, "quarantined_by")
                and memory_class in MEMORY_COMPATIBILITY.get(str(packet.get("provenance")), set())
                and (
                    memory_class != "observed"
                    or (
                        agent in self._packet_list(packet, "observation_tokens")
                        and packet.get("source_agent") == agent
                    )
                )
            )
        return False

    def _validate_proof_shape_and_source(
        self, proof: dict[str, Any], receipt: dict[str, Any]
    ) -> None:
        """Bind every proof field to its constructor and source statement.

        A semantically true proof with attacker-chosen claims, scope, or
        premises is still not the proof authorized by the program.  Keep this
        check independent of ``_proof_semantically_valid`` so the latter can
        also be used after affine/linear resource-state changes.
        """

        index = int(receipt.get("index", -1))
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args
        receipt_kind = receipt.get("kind")
        kind = proof.get("kind")

        if receipt_kind == "trusted_attestation":
            self._expect(
                statement is not None
                and statement.kind in {"attest_origin", "attest_relevance"},
                "trusted_attestation_source_kind",
                receipt_index=index,
            )
            expected_kind = (
                "origin"
                if statement is not None and statement.kind == "attest_origin"
                else "relevance"
            )
            expected_scope = args.get("scope") if expected_kind == "relevance" else None
            expected_source_agent = args.get("agent") if expected_kind == "origin" else None
            expected_source_lineage = args.get("lineage") if expected_kind == "origin" else None
            expected_claims = (
                ("trusted_origin_attestation", "trusted_lineage_attestation")
                if expected_kind == "origin"
                else ("trusted_task_relevance",)
            )
            expected = {
                "name": args.get("proof"),
                "kind": expected_kind,
                "subject": args.get("packet"),
                "agent": args.get("agent"),
                "scope": expected_scope,
                "memory_class": None,
                "source_agent": expected_source_agent,
                "source_lineage": expected_source_lineage,
                "premises": (),
                "claims": expected_claims,
                "trusted": True,
                "resource_mode": "persistent",
            }
        else:
            self._expect(
                statement is not None and statement.kind == "proof",
                "proof_source_kind",
                receipt_index=index,
            )
            expected_kind = args.get("proof_kind")
            expected_subject = (
                args.get("effect") if expected_kind == "capability" else args.get("packet")
            )
            expected_agent = None if expected_kind == "origin" else args.get("agent")
            expected_scope = (
                args.get("effect")
                if expected_kind == "capability"
                else args.get("scope")
                if expected_kind in {"authorization", "use"}
                else None
            )
            expected_memory_class = (
                args.get("memory_class") if expected_kind == "ownership" else None
            )
            expected_source_agent = (
                args.get("source_agent")
                if expected_kind == "origin"
                else args.get("agent")
                if expected_kind == "observation"
                else None
            )
            expected_source_lineage = (
                args.get("source_lineage")
                if expected_kind == "origin"
                else self.agents.get(str(args.get("agent")), {}).get("lineage")
                if expected_kind == "observation"
                else None
            )
            claims_by_kind: dict[str, tuple[str, ...]] = {
                "access": ("workspace_access",),
                "origin": ("origin_matches", "lineage_matches"),
                "clear": ("not_quarantined",),
                "endorsement": ("epistemically_endorsed",),
                "authorization": ("use_authorized",),
                "observation": ("direct_observation_token",),
                "use": (
                    "workspace_access",
                    "origin_valid",
                    "not_quarantined",
                    "endorsed",
                    "authorized",
                ),
                "ownership": ("autobiographical_write_authorized",),
            }
            expected_claims = (
                (
                    "capability_available",
                    self.capabilities.get(
                        (str(args.get("agent")), str(args.get("effect"))), {}
                    ).get("grant_digest"),
                )
                if expected_kind == "capability"
                else claims_by_kind.get(str(expected_kind), ())
            )
            expected = {
                "name": args.get("name"),
                "kind": expected_kind,
                "subject": expected_subject,
                "agent": expected_agent,
                "scope": expected_scope,
                "memory_class": expected_memory_class,
                "source_agent": expected_source_agent,
                "source_lineage": expected_source_lineage,
                "premises": tuple(args.get("premises", ())),
                "claims": expected_claims,
                "trusted": False,
                "resource_mode": args.get("resource_mode", "persistent"),
            }

        for field, value in expected.items():
            self._expect(
                canonical_json(proof.get(field)) == canonical_json(value),
                "proof_source_correspondence",
                receipt_index=index,
                proof=proof.get("name"),
                field=field,
            )

        if receipt_kind == "trusted_attestation" and kind == "origin":
            self._expect(
                proof.get("source_lineage")
                == self.agents.get(str(proof.get("agent")), {}).get("lineage"),
                "trusted_origin_active_lineage",
                receipt_index=index,
                proof=proof.get("name"),
            )

        if kind == "capability":
            self._expect(
                proof.get("subject_digest") is None
                and proof.get("state_digest") is None,
                "capability_proof_digest_shape",
                receipt_index=index,
            )
        else:
            packet = self.packets.get(str(proof.get("subject")))
            self._expect(packet is not None, "proof_subject_exists", receipt_index=index)
            if packet is not None:
                self._expect(
                    proof.get("subject_digest") == packet.get("content_digest")
                    and proof.get("state_digest") == packet.get("packet_digest"),
                    "proof_subject_state_binding",
                    receipt_index=index,
                    proof=proof.get("name"),
                )

    def _validate_composite_premises(
        self, proof: dict[str, Any], receipt: dict[str, Any]
    ) -> None:
        index = int(receipt.get("index", -1))
        kind = proof.get("kind")
        if kind not in {"use", "ownership"}:
            return
        names = tuple(proof.get("premises", ()))
        terms = [self.proofs.get(str(name)) for name in names]
        required = (
            {"access", "origin", "clear", "endorsement", "authorization"}
            if kind == "use"
            else {"access", "origin", "clear"}
            | ({"observation"} if proof.get("memory_class") == "observed" else set())
        )
        observed_kinds = {
            term.get("kind") for term in terms if isinstance(term, dict)
        }
        self._expect(
            len(names) == len(required)
            and len(set(names)) == len(names)
            and observed_kinds == required,
            f"{kind}_proof_exact_premises",
            receipt_index=index,
            proof=proof.get("name"),
        )
        for term in terms:
            if term is None:
                continue
            self._expect(
                term.get("subject") == proof.get("subject")
                and term.get("subject_digest") == proof.get("subject_digest"),
                f"{kind}_proof_premise_subject",
                receipt_index=index,
                proof=proof.get("name"),
                premise=term.get("name"),
            )
        by_kind = {
            str(term.get("kind")): term for term in terms if isinstance(term, dict)
        }
        agent_bound = (
            {"access", "clear", "endorsement", "authorization"}
            if kind == "use"
            else {"access", "clear", "observation"}
        ) & required
        for premise_kind in agent_bound:
            term = by_kind.get(premise_kind)
            self._expect(
                term is not None and term.get("agent") == proof.get("agent"),
                f"{kind}_proof_premise_agent",
                receipt_index=index,
                proof=proof.get("name"),
                premise_kind=premise_kind,
            )
        if kind == "use":
            authorization = by_kind.get("authorization")
            self._expect(
                authorization is not None
                and authorization.get("scope")
                in {proof.get("scope"), "planning"},
                "use_proof_premise_scope",
                receipt_index=index,
                proof=proof.get("name"),
            )
        for term in terms:
            if isinstance(term, dict) and term.get("resource_mode") in {"affine", "linear"}:
                self._expect(
                    term.get("remaining_uses") == 0
                    and term.get("consumed_step") == receipt.get("step"),
                    f"{kind}_proof_premise_consumption",
                    receipt_index=index,
                    proof=proof.get("name"),
                    premise=term.get("name"),
                )
        expected_consumptions = [
            str(term.get("name"))
            for term in terms
            if isinstance(term, dict)
            and term.get("resource_mode") in {"affine", "linear"}
        ]
        events = self._proof_events(self._statement(receipt))
        self._expect(
            [event.get("proof") for event in events] == expected_consumptions
            and all(event.get("kind") == "proof_consume" for event in events)
            and (
                not events
                or [event.get("index") for event in events]
                == list(range(index - len(events), index))
            ),
            f"{kind}_proof_consumption_receipts",
            receipt_index=index,
            proof=proof.get("name"),
        )

    def _install_proof(self, proof: dict[str, Any], receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        name = str(proof.get("name"))
        if name in self.proofs:
            self.fail("proof_unique_constructor", receipt_index=index, proof=name)
            return
        self._expect(
            set(proof) == set(_proof_payload(proof)) | {"proof_digest"},
            "proof_schema",
            receipt_index=index,
            proof=name,
        )
        self._expect(
            isinstance(proof.get("name"), str)
            and isinstance(proof.get("kind"), str)
            and isinstance(proof.get("subject"), str)
            and (proof.get("agent") is None or isinstance(proof.get("agent"), str))
            and (proof.get("scope") is None or isinstance(proof.get("scope"), str))
            and (proof.get("memory_class") is None or isinstance(proof.get("memory_class"), str))
            and (proof.get("source_agent") is None or isinstance(proof.get("source_agent"), str))
            and (proof.get("source_lineage") is None or isinstance(proof.get("source_lineage"), str))
            and isinstance(proof.get("premises"), (list, tuple))
            and isinstance(proof.get("claims"), (list, tuple))
            and isinstance(proof.get("trusted"), bool)
            and isinstance(proof.get("created_step"), int)
            and not isinstance(proof.get("created_step"), bool),
            "proof_schema_types",
            receipt_index=index,
            proof=name,
        )
        expected = digest(_proof_payload(proof))
        self._expect(proof.get("proof_digest") == expected, "proof_digest", receipt_index=index, proof=name)
        self._expect(proof.get("kind") in PROOF_KINDS, "proof_kind", receipt_index=index, proof=name)
        self._expect(proof.get("resource_mode") in PROOF_MODES, "proof_resource_mode", receipt_index=index, proof=name)
        self._expect(proof.get("created_step") == receipt.get("step"), "proof_created_step", receipt_index=index, proof=name)
        mode = proof.get("resource_mode")
        expected_uses = None if mode == "persistent" else 1
        self._expect(proof.get("remaining_uses") == expected_uses, "proof_initial_uses", receipt_index=index, proof=name)
        self._expect(proof.get("consumed_step") is None, "proof_initial_consumed_step", receipt_index=index, proof=name)
        self._validate_proof_shape_and_source(proof, receipt)
        for premise in proof.get("premises", []):
            self._expect(str(premise) in self.proofs, "proof_premise_exists", receipt_index=index, proof=name, premise=premise)
        self._validate_composite_premises(proof, receipt)
        kind = proof.get("kind")
        if kind == "use":
            present = {
                self.proofs[str(item)].get("kind")
                for item in proof.get("premises", [])
                if str(item) in self.proofs
            }
            self._expect({"access", "origin", "clear", "endorsement", "authorization"}.issubset(present), "use_proof_premises", receipt_index=index, proof=name)
        elif kind == "ownership":
            present = {
                self.proofs[str(item)].get("kind")
                for item in proof.get("premises", [])
                if str(item) in self.proofs
            }
            required = {"access", "origin", "clear"}
            if proof.get("memory_class") == "observed":
                required.add("observation")
            self._expect(required.issubset(present), "ownership_proof_premises", receipt_index=index, proof=name)
        self._expect(
            self._proof_semantically_valid(proof, step=int(receipt.get("step", -1))),
            "proof_constructor_semantics",
            receipt_index=index,
            proof=name,
            kind=kind,
        )
        self.proofs[name] = copy.deepcopy(proof)
        if proof.get("proof_digest"):
            self.proof_by_digest[str(proof["proof_digest"])] = copy.deepcopy(proof)
        self.counters.proofs += 1

    def _use_proof(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        name = str(receipt.get("proof"))
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args
        expected_name: Any = None
        expected_purpose: str | None = None
        if statement is not None and statement.kind == "proof":
            expected_name = name if name in tuple(args.get("premises", ())) else None
            expected_purpose = f"premise:{args.get('name')}"
        elif statement is not None and statement.kind == "authorize":
            expected_name = args.get("proof")
            expected_purpose = "verification"
        elif statement is not None and statement.kind == "write_memory":
            expected_name = args.get("proof")
            expected_purpose = "ownership"
        elif statement is not None and statement.kind == "plan":
            expected_name = args.get("proof")
            expected_purpose = "use"
        self._expect(
            expected_name == name and expected_purpose is not None,
            "proof_use_source_correspondence",
            receipt_index=index,
            proof=name,
        )
        self._expect(
            receipt.get("purpose") == expected_purpose,
            "proof_use_purpose",
            receipt_index=index,
            proof=name,
        )
        if statement is not None:
            self.proof_events_by_statement.setdefault(id(statement), []).append(
                {
                    "index": index,
                    "proof": name,
                    "kind": receipt.get("kind"),
                    "purpose": receipt.get("purpose"),
                }
            )
        proof = self.proofs.get(name)
        if proof is None:
            self.fail("proof_use_exists", receipt_index=index, proof=name)
            return
        self._expect(receipt.get("proof_digest") == proof.get("proof_digest"), "proof_use_digest", receipt_index=index, proof=name)
        self._expect(receipt.get("resource_mode") == proof.get("resource_mode"), "proof_use_mode", receipt_index=index, proof=name)
        self._expect(self._proof_semantically_valid(proof, step=int(receipt.get("step", -1))), "proof_use_semantics", receipt_index=index, proof=name)
        mode = proof.get("resource_mode")
        if receipt.get("kind") == "proof_use":
            self._expect(mode == "persistent", "proof_persistent_use", receipt_index=index, proof=name)
            self._expect(receipt.get("remaining_uses") is None, "proof_persistent_remaining", receipt_index=index, proof=name)
            return
        self._expect(mode in {"affine", "linear"}, "proof_consume_mode", receipt_index=index, proof=name)
        remaining = proof.get("remaining_uses")
        if not isinstance(remaining, int) or remaining <= 0:
            self.fail("proof_single_consumption", receipt_index=index, proof=name)
            return
        expected_remaining = remaining - 1
        expected_step = receipt.get("step") if expected_remaining == 0 else None
        self._expect(receipt.get("remaining_uses") == expected_remaining, "proof_remaining_transition", receipt_index=index, proof=name)
        self._expect(receipt.get("consumed_step") == expected_step, "proof_consumed_step", receipt_index=index, proof=name)
        proof["remaining_uses"] = expected_remaining
        proof["consumed_step"] = expected_step

    def _install_capability(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        agent = str(receipt.get("agent"))
        capability = receipt.get("capability")
        if not isinstance(capability, dict):
            self.fail("capability_payload", receipt_index=index)
            return
        self._expect(
            set(capability)
            == {
                "effect",
                "initial_uses",
                "remaining_uses",
                "expires_at",
                "source",
                "grant_index",
                "issued_step",
                "grant_digest",
            },
            "capability_schema",
            receipt_index=index,
        )
        effect = str(capability.get("effect"))
        key = (agent, effect)
        self._expect(agent in self.agents, "capability_agent_exists", receipt_index=index, agent=agent)
        self._expect(effect in EFFECTS, "capability_effect", receipt_index=index, effect=effect)
        self._expect(capability.get("grant_index") == index, "capability_grant_index", receipt_index=index)
        self._expect(capability.get("issued_step") == receipt.get("step"), "capability_issued_step", receipt_index=index)
        self._expect(capability.get("initial_uses") == capability.get("remaining_uses"), "capability_initial_budget", receipt_index=index)
        uses = capability.get("initial_uses")
        self._expect(uses is None or (isinstance(uses, int) and not isinstance(uses, bool) and uses > 0), "capability_budget_domain", receipt_index=index)
        expires = capability.get("expires_at")
        # An already-expired grant is a valid (but unusable) ledger entry; the
        # temporal bound is enforced at capability proof/use and execution.
        self._expect(expires is None or (isinstance(expires, int) and not isinstance(expires, bool) and expires >= 0), "capability_expiry_domain", receipt_index=index)
        self._expect(capability.get("grant_digest") == digest(_capability_payload(agent, capability)), "capability_grant_digest", receipt_index=index)
        self._expect(receipt.get("previous_capability") == self.capabilities.get(key), "capability_previous_correspondence", receipt_index=index)
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args
        if statement is not None and statement.kind == "agent":
            self._expect(receipt.get("implicit") is True, "capability_default_implicit", receipt_index=index)
            self._expect(agent == args.get("name") and effect in {"read", "communicate", "simulate"}, "capability_default_source", receipt_index=index)
            self._expect(capability.get("source") == "default" and uses is None and expires is None, "capability_default_shape", receipt_index=index)
        elif statement is not None and statement.kind == "grant":
            self._expect(receipt.get("implicit") is False, "capability_explicit_marker", receipt_index=index)
            self._expect(agent == args.get("agent") and effect == args.get("effect"), "capability_grant_source", receipt_index=index)
            self._expect(uses == args.get("uses") and expires == args.get("until"), "capability_grant_limits", receipt_index=index)
            self._expect(capability.get("source") == "grant", "capability_grant_source_class", receipt_index=index)
        else:
            self.fail("capability_grant_statement", receipt_index=index)
        self.capabilities[key] = copy.deepcopy(capability)
        self.counters.capability_grants += 1

    def _revoke_capability(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        key = (str(receipt.get("agent")), str(receipt.get("effect")))
        current = self.capabilities.get(key)
        self._expect(receipt.get("revoked_capability") == current, "capability_revoke_correspondence", receipt_index=index)
        statement = self._statement(receipt)
        if statement is not None:
            self._expect(statement.kind == "revoke" and statement.args.get("agent") == key[0] and statement.args.get("effect") == key[1], "capability_revoke_source", receipt_index=index)
        self.capabilities.pop(key, None)
        self.counters.capability_revocations += 1

    def _install_plan(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        action = receipt.get("action")
        if not isinstance(action, dict):
            self.fail("plan_payload", receipt_index=index)
            return
        name = str(action.get("name"))
        self._expect(
            set(action) == set(_action_payload(action)) | {"action_digest"},
            "action_schema",
            receipt_index=index,
            action=name,
        )
        self._expect(name not in self.actions, "action_unique_plan", receipt_index=index, action=name)
        self._expect(action.get("executed") is False and action.get("observed") is None and action.get("capability_digest") is None, "plan_initial_state", receipt_index=index, action=name)
        self._expect(action.get("action_digest") == digest(_action_payload(action)), "action_digest", receipt_index=index, action=name)
        agent = str(action.get("agent"))
        packet = self.packets.get(str(action.get("packet_name")))
        self._expect(agent in self.agents, "plan_agent_exists", receipt_index=index, action=name)
        self._expect(action.get("effect") in EFFECTS, "plan_effect", receipt_index=index, action=name)
        self._expect(packet is not None, "plan_packet_exists", receipt_index=index, action=name)
        if packet is not None:
            scopes = packet.get("authorizations", {}).get(agent, [])
            self._expect(agent in self._packet_list(packet, "accessible_to"), "plan_access", receipt_index=index, action=name)
            self._expect(agent in self._packet_list(packet, "bound_to"), "plan_binding", receipt_index=index, action=name)
            self._expect(agent not in self._packet_list(packet, "quarantined_by"), "plan_clear", receipt_index=index, action=name)
            self._expect(agent in self._packet_list(packet, "endorsed_by"), "plan_endorsement", receipt_index=index, action=name)
            self._expect("planning" in scopes or action.get("effect") in scopes, "plan_authorization", receipt_index=index, action=name)
            self._expect(packet.get("status") in {"grounded", "admitted"}, "plan_packet_status", receipt_index=index, action=name)
        required = action.get("required_proof")
        if required is not None:
            proof = self.proofs.get(str(required))
            self._expect(proof is not None and proof.get("kind") == "use", "plan_required_proof", receipt_index=index, action=name)
            if proof is not None and packet is not None:
                self._expect(
                    proof.get("subject") == packet.get("name")
                    and proof.get("subject_digest") == packet.get("content_digest")
                    and proof.get("state_digest") == packet.get("packet_digest")
                    and proof.get("agent") == agent
                    and proof.get("scope") in {"planning", action.get("effect")}
                    and self._proof_semantically_valid(
                        proof,
                        step=int(receipt.get("step", -1)),
                        require_available=False,
                    ),
                    "plan_required_proof_binding",
                    receipt_index=index,
                    action=name,
                )
        statement = self._statement(receipt)
        if statement is not None:
            args = statement.args
            self._expect(statement.kind == "plan", "plan_source_kind", receipt_index=index)
            for field, value in (
                ("name", args.get("action")),
                ("agent", args.get("agent")),
                ("packet_name", args.get("packet")),
                ("effect", args.get("effect")),
                ("expected", args.get("expected")),
                ("required_proof", args.get("proof")),
            ):
                self._expect(_same_number(action.get(field), value), "plan_source_correspondence", receipt_index=index, field=field)
            self._validate_gate_proof_event(
                statement=statement,
                proof_name=args.get("proof"),
                gate_index=index,
                property_name="plan_proof_gate",
            )
        self.actions[name] = copy.deepcopy(action)
        self.counters.plans += 1

    def _execute_action(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        action = receipt.get("action")
        if not isinstance(action, dict):
            self.fail("execute_payload", receipt_index=index)
            return
        name = str(action.get("name"))
        self._expect(
            set(action) == set(_action_payload(action)) | {"action_digest"},
            "action_schema",
            receipt_index=index,
            action=name,
        )
        prior = self.actions.get(name)
        if prior is None:
            self.fail("execute_has_plan", receipt_index=index, action=name)
            return
        self._expect(prior.get("executed") is False and prior.get("observed") is None, "execute_once", receipt_index=index, action=name)
        self._expect(receipt.get("prior_action_digest") == prior.get("action_digest"), "execute_prior_action_digest", receipt_index=index, action=name)
        for field in ("name", "agent", "packet_name", "effect", "expected", "required_proof"):
            self._expect(action.get(field) == prior.get(field), "execute_plan_correspondence", receipt_index=index, action=name, field=field)
        self._expect(action.get("executed") is True and action.get("observed") is None, "execute_state_transition", receipt_index=index, action=name)
        self._expect(action.get("action_digest") == digest(_action_payload(action)), "action_digest", receipt_index=index, action=name)
        self._expect(receipt.get("transaction") is None, "execute_transaction_confinement", receipt_index=index, action=name)
        key = (str(action.get("agent")), str(action.get("effect")))
        capability = self.capabilities.get(key)
        if capability is None:
            self.fail("execute_capability_exists", receipt_index=index, action=name)
        else:
            self._expect(receipt.get("capability_before") == capability, "execute_capability_before", receipt_index=index, action=name)
            self._expect(action.get("capability_digest") == capability.get("grant_digest"), "execute_capability_digest", receipt_index=index, action=name)
            expires = capability.get("expires_at")
            self._expect(expires is None or int(receipt.get("step", -1)) <= int(expires), "execute_capability_expiry", receipt_index=index, action=name)
            remaining = capability.get("remaining_uses")
            self._expect(remaining is None or (isinstance(remaining, int) and remaining > 0), "execute_capability_available", receipt_index=index, action=name)
            after = copy.deepcopy(capability)
            if isinstance(remaining, int):
                after["remaining_uses"] = remaining - 1
            self._expect(receipt.get("capability_after") == after, "execute_capability_decrement", receipt_index=index, action=name)
            self.capabilities[key] = after
        statement = self._statement(receipt)
        if statement is not None:
            self._expect(statement.kind == "execute" and statement.args.get("action") == name and statement.args.get("agent") == action.get("agent"), "execute_source_correspondence", receipt_index=index, action=name)
        self.actions[name] = copy.deepcopy(action)
        self.counters.executions += 1

    def _feedback_action(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        action = receipt.get("action")
        if not isinstance(action, dict):
            self.fail("feedback_payload", receipt_index=index)
            return
        name = str(action.get("name"))
        self._expect(
            set(action) == set(_action_payload(action)) | {"action_digest"},
            "action_schema",
            receipt_index=index,
            action=name,
        )
        prior = self.actions.get(name)
        if prior is None:
            self.fail("feedback_has_execution", receipt_index=index, action=name)
            return
        self._expect(prior.get("executed") is True and prior.get("observed") is None, "feedback_once", receipt_index=index, action=name)
        self._expect(receipt.get("prior_action_digest") == prior.get("action_digest"), "feedback_prior_action_digest", receipt_index=index, action=name)
        for field in ("name", "agent", "packet_name", "effect", "expected", "required_proof", "executed", "capability_digest"):
            self._expect(action.get(field) == prior.get(field), "feedback_execute_correspondence", receipt_index=index, action=name, field=field)
        self._expect(action.get("observed") is not None, "feedback_observation", receipt_index=index, action=name)
        self._expect(action.get("action_digest") == digest(_action_payload(action)), "action_digest", receipt_index=index, action=name)
        expected_error = None if action.get("expected") is None else float(action["observed"]) - float(action["expected"])
        observed_error = receipt.get("prediction_error")
        self._expect(
            (expected_error is None and observed_error is None)
            or (
                expected_error is not None
                and observed_error is not None
                and math.isclose(float(observed_error), expected_error, rel_tol=0.0, abs_tol=1e-12)
            ),
            "feedback_prediction_error",
            receipt_index=index,
            action=name,
        )
        statement = self._statement(receipt)
        if statement is not None:
            self._expect(statement.kind == "feedback" and statement.args.get("action") == name and statement.args.get("agent") == action.get("agent") and _same_number(statement.args.get("observed"), action.get("observed")), "feedback_source_correspondence", receipt_index=index, action=name)
        self.actions[name] = copy.deepcopy(action)
        self.counters.feedbacks += 1

    def _write_memory(self, receipt: dict[str, Any]) -> None:
        index = int(receipt.get("index", -1))
        record = receipt.get("record")
        if not isinstance(record, dict):
            self.fail("memory_payload", receipt_index=index)
            return
        self._expect(
            set(record) == set(_record_payload(record)) | {"record_digest"},
            "memory_record_schema",
            receipt_index=index,
        )
        self._expect(record.get("record_digest") == digest(_record_payload(record)), "memory_record_digest", receipt_index=index)
        agent = str(record.get("agent"))
        packet = self.packets.get(str(record.get("packet_name")))
        self._expect(agent in self.agents, "memory_agent_exists", receipt_index=index)
        self._expect(packet is not None, "memory_packet_exists", receipt_index=index)
        if packet is not None:
            for field in ("content", "source_agent", "source_lineage", "packet_digest"):
                packet_field = "packet_digest" if field == "packet_digest" else field
                self._expect(record.get(field) == packet.get(packet_field), "memory_packet_binding", receipt_index=index, field=field)
            memory_class = str(record.get("memory_class"))
            self._expect(memory_class in MEMORY_COMPATIBILITY.get(str(packet.get("provenance")), set()), "memory_provenance_compatibility", receipt_index=index)
            self._expect(agent in self._packet_list(packet, "accessible_to") and agent in self._packet_list(packet, "bound_to") and agent not in self._packet_list(packet, "quarantined_by"), "memory_access_binding", receipt_index=index)
            self._expect(packet.get("status") in {"grounded", "admitted"}, "memory_packet_status", receipt_index=index)
            if memory_class == "observed":
                self._expect(agent in self._packet_list(packet, "observation_tokens") and packet.get("source_agent") == agent and packet.get("source_lineage") == self.agents.get(agent, {}).get("lineage"), "observed_memory_nonforging", receipt_index=index)
        statement = self._statement(receipt)
        if statement is not None:
            args = statement.args
            self._expect(statement.kind == "write_memory" and args.get("agent") == agent and args.get("packet") == record.get("packet_name") and args.get("memory_class") == record.get("memory_class"), "memory_source_correspondence", receipt_index=index)
            proof_name = args.get("proof")
            proof_digest = record.get("proof_digest")
            self._expect(
                (proof_name is None and proof_digest is None)
                or (proof_name is not None and proof_digest is not None),
                "memory_source_proof_presence",
                receipt_index=index,
            )
            if proof_name is not None:
                proof = self.proofs.get(str(proof_name))
                self._expect(
                    proof is not None
                    and proof.get("proof_digest") == proof_digest
                    and proof.get("kind") == "ownership"
                    and proof.get("subject") == record.get("packet_name")
                    and proof.get("agent") == agent
                    and proof.get("memory_class") == record.get("memory_class")
                    and packet is not None
                    and proof.get("subject_digest") == packet.get("content_digest")
                    and proof.get("state_digest") == packet.get("packet_digest")
                    and self._proof_semantically_valid(
                        proof,
                        step=int(receipt.get("step", -1)),
                        require_available=False,
                    ),
                    "memory_ownership_proof",
                    receipt_index=index,
                )
            self._validate_gate_proof_event(
                statement=statement,
                proof_name=proof_name,
                gate_index=index,
                property_name="memory_proof_gate",
            )
        else:
            self.fail("memory_source_statement", receipt_index=index)
        self.memories.setdefault(agent, []).append(copy.deepcopy(record))
        self.counters.memory_records += 1

    def _snapshot_tables(self) -> dict[str, Any]:
        return copy.deepcopy(
            {
                "module": self.module,
                "lineages": self.lineages,
                "agents": self.agents,
                "packets": self.packets,
                "packet_by_digest": self.packet_by_digest,
                "proofs": self.proofs,
                "proof_by_digest": self.proof_by_digest,
                "capabilities": self.capabilities,
                "actions": self.actions,
                "memories": self.memories,
                "secret_digests": self.secret_digests,
                "private_secrets": self.private_secrets,
            }
        )

    def _restore_tables(self, snapshot: dict[str, Any]) -> None:
        self.module = snapshot["module"]
        self.lineages = snapshot["lineages"]
        self.agents = snapshot["agents"]
        self.packets = snapshot["packets"]
        self.packet_by_digest = snapshot["packet_by_digest"]
        self.proofs = snapshot["proofs"]
        self.proof_by_digest = snapshot["proof_by_digest"]
        self.capabilities = snapshot["capabilities"]
        self.actions = snapshot["actions"]
        self.memories = snapshot["memories"]
        self.secret_digests = snapshot["secret_digests"]
        self.private_secrets = snapshot["private_secrets"]

    def _handle_transaction(self, receipt: dict[str, Any]) -> None:
        kind = receipt.get("kind")
        index = int(receipt.get("index", -1))
        name = str(receipt.get("transaction"))
        statement = self._statement(receipt)
        base_keys = {
            "schema",
            "core_version",
            "index",
            "state_index",
            "step",
            "kind",
            "transaction",
            "previous_digest",
            "digest",
        }
        if kind == "transaction_begin":
            self._expect(
                set(receipt)
                == base_keys | {"begin_audit_index", "checkpoint_digest"},
                "transaction_begin_schema",
                receipt_index=index,
            )
            self._expect(self.active_transaction is None, "transaction_non_nested", receipt_index=index)
            self._expect(receipt.get("begin_audit_index") == index, "transaction_begin_index", receipt_index=index)
            self._expect(_is_sha256(receipt.get("checkpoint_digest")), "transaction_checkpoint_shape", receipt_index=index)
            self._expect(
                statement is not None
                and statement.kind == "begin_transaction"
                and statement.args.get("name") == name,
                "transaction_begin_source",
                receipt_index=index,
            )
            self.active_transaction = {
                "name": name,
                "index": index,
                "step": receipt.get("step"),
                "checkpoint_digest": receipt.get("checkpoint_digest"),
                "tables": self._snapshot_tables(),
            }
            self.counters.transaction_begins += 1
            return
        active = self.active_transaction
        if active is None or active.get("name") != name:
            self.fail("transaction_has_begin", receipt_index=index, transaction=name)
            return
        self._expect(receipt.get("begin_audit_index") == active.get("index"), "transaction_begin_index_correspondence", receipt_index=index)
        self._expect(receipt.get("begin_step") == active.get("step"), "transaction_begin_step_correspondence", receipt_index=index)
        span = tuple(receipt.get("body_effect_span", ()))
        self._expect(span == (int(active["index"]) + 1, index), "transaction_effect_span", receipt_index=index)
        if kind == "transaction_commit":
            self._expect(
                set(receipt)
                == base_keys
                | {
                    "begin_audit_index",
                    "begin_step",
                    "body_effect_span",
                    "final_state_digest",
                },
                "transaction_commit_schema",
                receipt_index=index,
            )
            self._expect(_is_sha256(receipt.get("final_state_digest")), "transaction_final_digest_shape", receipt_index=index)
            self._expect(
                statement is not None
                and statement.kind == "commit_transaction"
                and statement.args.get("name") == name,
                "transaction_commit_source",
                receipt_index=index,
            )
            self.counters.transaction_commits += 1
        else:
            self._expect(
                set(receipt)
                == base_keys
                | {
                    "automatic",
                    "reason",
                    "begin_audit_index",
                    "begin_step",
                    "body_effect_span",
                    "checkpoint_digest",
                    "pre_restore_digest",
                    "discarded_chain_tip",
                    "discarded_receipt_count",
                    "restored_state_digest",
                },
                "transaction_rollback_schema",
                receipt_index=index,
            )
            self._expect(receipt.get("checkpoint_digest") == active.get("checkpoint_digest"), "transaction_checkpoint_digest", receipt_index=index)
            self._expect(_is_sha256(receipt.get("pre_restore_digest")), "transaction_pre_restore_digest_shape", receipt_index=index)
            self._expect(receipt.get("discarded_chain_tip") == receipt.get("previous_digest"), "transaction_discarded_chain_tip", receipt_index=index)
            self._expect(receipt.get("discarded_receipt_count") == index - int(active["index"]) - 1, "transaction_discarded_receipt_count", receipt_index=index)
            self._expect(receipt.get("restored_state_digest") == active.get("checkpoint_digest"), "transaction_restored_state_digest", receipt_index=index)
            if statement is not None and statement.kind == "rollback_transaction":
                self._expect(
                    statement.args.get("name") == name
                    and receipt.get("automatic") is False
                    and receipt.get("reason") == "explicit rollback",
                    "transaction_explicit_rollback_source",
                    receipt_index=index,
                )
            else:
                self._expect(
                    statement is not None and receipt.get("automatic") is True,
                    "transaction_automatic_rollback_source",
                    receipt_index=index,
                )
            self._restore_tables(active["tables"])
            self.counters.transaction_rollbacks += 1
        self.active_transaction = None

    def _source_setup(self, source: str | None) -> None:
        if source is None:
            return
        self.source_digest = digest(source)
        try:
            try:
                from .osl_parser import StaticChecker, parse_program
            except ImportError:
                from osl_parser import StaticChecker, parse_program  # type: ignore
            statements = tuple(parse_program(source))
            self.statements = statements
            self.manifests = tuple(_manifest(statement, ordinal) for ordinal, statement in enumerate(statements))
            self.ast_digest = digest(self.manifests)
            try:
                report = StaticChecker().check(statements)
                self.static_report = asdict(report)
            except Exception as exc:  # static rejection is part of the public outcome
                self.source_parse_error = "static:" + str(exc)
        except Exception as exc:
            self.source_parse_error = "parse:" + str(exc)

    def _validate_lifecycle_and_boundaries(
        self, receipts: list[dict[str, Any]], source: str | None
    ) -> None:
        if not receipts:
            self.fail("nonempty_trace")
            return
        kinds = [str(receipt.get("kind")) for receipt in receipts]
        self._expect(kinds[0] == "program_open", "program_open_first")
        self._expect(kinds.count("program_open") == 1, "program_open_unique")
        terminals = [index for index, kind in enumerate(kinds) if kind in {"program_complete", "program_reject"}]
        self._expect(len(terminals) == 1, "single_program_terminal", observed=len(terminals))
        if terminals:
            self._expect(terminals[0] == len(receipts) - 1, "program_terminal_last", receipt_index=terminals[0])
        terminal_index = terminals[0] if terminals else len(receipts)
        terminal = receipts[terminal_index] if terminal_index < len(receipts) else {}
        opened = receipts[0]
        for prelude_index in range(min(3, len(receipts))):
            self._expect(receipts[prelude_index].get("step") == 0, "lifecycle_prelude_step", receipt_index=prelude_index)
        if source is not None:
            self._expect(opened.get("source_digest") == self.source_digest, "program_source_digest")
            self._expect(opened.get("source_bytes") == len(source.encode("utf-8")), "program_source_bytes")
            self._expect(opened.get("source_lines") == len(source.splitlines()), "program_source_lines")

        parse_accepts = [receipt for receipt in receipts if receipt.get("kind") == "parse_accept"]
        parse_rejects = [receipt for receipt in receipts if receipt.get("kind") == "parse_reject"]
        static_checks = [receipt for receipt in receipts if receipt.get("kind") == "static_check"]
        static_rejects = [receipt for receipt in receipts if receipt.get("kind") == "static_reject"]
        if self.source_parse_error and self.source_parse_error.startswith("parse:"):
            expected_error = self.source_parse_error.split(":", 1)[1]
            self._expect(kinds == ["program_open", "parse_reject", "program_reject"], "parse_rejection_envelope", observed=kinds)
            if len(receipts) > 1:
                self._expect(receipts[1].get("error") == expected_error, "parse_rejection_error")
            for field, value in {
                "kind": "program_reject",
                "outcome": "rejected",
                "phase": "parse",
                "ast_digest": None,
                "statement_count": 0,
                "committed_count": 0,
                "failed_ordinal": None,
                "failed_line": None,
                "failed_statement_kind": None,
                "reason_code": "E_PARSE",
                "error": expected_error,
                "step": 0,
            }.items():
                self._expect(terminal.get(field) == value, "terminal_parse_shape", field=field)
            return

        if source is None:
            return
        self._expect(len(parse_accepts) == 1 and not parse_rejects, "parse_acceptance_envelope")
        self._expect(len(receipts) > 1 and kinds[1] == "parse_accept", "parse_accept_order")
        if parse_accepts:
            self._expect(parse_accepts[0].get("ast_digest") == self.ast_digest, "parse_ast_digest")
            self._expect(parse_accepts[0].get("statement_count") == len(self.statements), "parse_statement_count")

        if self.source_parse_error and self.source_parse_error.startswith("static:"):
            expected_error = self.source_parse_error.split(":", 1)[1]
            self._expect(kinds == ["program_open", "parse_accept", "static_reject", "program_reject"], "static_rejection_envelope", observed=kinds)
            if len(receipts) > 2:
                rejected_receipt = receipts[2]
                self._expect(rejected_receipt.get("ast_digest") == self.ast_digest, "static_reject_ast_digest")
                self._expect(rejected_receipt.get("statement_count") == len(self.statements), "static_reject_statement_count")
                self._expect(rejected_receipt.get("error") == expected_error, "static_rejection_error")
            for field, value in {
                "kind": "program_reject",
                "outcome": "rejected",
                "phase": "static",
                "ast_digest": self.ast_digest,
                "statement_count": len(self.statements),
                "committed_count": 0,
                "failed_ordinal": None,
                "failed_line": None,
                "failed_statement_kind": None,
                "reason_code": "E_STATIC",
                "error": expected_error,
                "step": 0,
            }.items():
                self._expect(terminal.get(field) == value, "terminal_static_shape", field=field)
            return

        self._expect(len(static_checks) == 1 and not static_rejects, "static_acceptance_envelope")
        self._expect(kinds[:3] == ["program_open", "parse_accept", "static_check"], "accepted_prelude_order")
        if static_checks:
            self._expect(static_checks[0].get("ast_digest") == self.ast_digest, "static_ast_digest")
            self._expect(canonical_json(static_checks[0].get("report")) == canonical_json(self.static_report), "static_report_binding")

        boundaries = [
            (index, receipt)
            for index, receipt in enumerate(receipts)
            if receipt.get("kind") in {"statement_commit", "statement_reject"}
        ]
        previous_after: str | None = None
        expected_ordinal = 0
        rejected = False
        cursor = 3
        for index, boundary in boundaries:
            ordinal = boundary.get("statement_ordinal")
            self.counters.statement_boundaries += 1
            self._expect(not rejected, "boundary_after_rejection", receipt_index=index)
            self._expect(ordinal == expected_ordinal, "statement_boundary_ordinal", receipt_index=index, expected=expected_ordinal, observed=ordinal)
            statement = self.statements[expected_ordinal] if source is not None and expected_ordinal < len(self.statements) else None
            if statement is not None:
                manifest = self.manifests[expected_ordinal]
                self._expect(boundary.get("line_number") == statement.line_number, "statement_boundary_line", receipt_index=index)
                self._expect(boundary.get("statement_kind") == statement.kind, "statement_boundary_kind", receipt_index=index)
                self._expect(boundary.get("source_digest") == digest(statement.source), "statement_boundary_source", receipt_index=index)
                self._expect(boundary.get("node_digest") == manifest["node_digest"], "statement_boundary_node", receipt_index=index)
                expected_step = expected_ordinal + 1
                self._expect(boundary.get("step") == expected_step, "statement_boundary_step", receipt_index=index)
            raw_emitted = boundary.get("emitted_receipt_indices", ())
            emitted = tuple(raw_emitted) if isinstance(raw_emitted, (list, tuple)) else ()
            expected_emitted = tuple(range(cursor, index))
            self._expect(tuple(boundary.get("effect_span", ())) == (cursor, index), "statement_effect_span", receipt_index=index)
            self._expect(emitted == expected_emitted, "statement_effect_partition", receipt_index=index)
            for item in expected_emitted:
                self._expect(receipts[item].get("step") == expected_ordinal + 1, "statement_effect_step", receipt_index=item, statement_ordinal=expected_ordinal)
            if statement is not None:
                for item in emitted:
                    if isinstance(item, int) and 0 <= item < len(receipts):
                        self.receipt_statement[item] = statement
                primary = PRIMARY_RECEIPT.get(statement.kind)
                if primary is not None:
                    count = sum(receipts[item].get("kind") == primary for item in emitted if isinstance(item, int) and 0 <= item < len(receipts))
                    if boundary.get("kind") == "statement_commit":
                        self._expect(count == 1, "statement_primary_effect", receipt_index=index, expected=primary, observed=count)
                    else:
                        self._expect(count <= 1, "statement_reject_primary_effect", receipt_index=index, expected=primary, observed=count)
                if statement.kind == "agent" and boundary.get("kind") == "statement_commit":
                    effect_receipts = [receipts[item] for item in emitted if isinstance(item, int) and 0 <= item < len(receipts)]
                    self._expect(
                        [item.get("kind") for item in effect_receipts]
                        == ["agent_declare", "capability_grant", "capability_grant", "capability_grant"]
                        and [
                            item.get("capability", {}).get("effect")
                            for item in effect_receipts[1:]
                            if isinstance(item.get("capability"), dict)
                        ]
                        == ["read", "communicate", "simulate"]
                        and all(item.get("implicit") is True for item in effect_receipts[1:])
                        and all(item.get("previous_capability") is None for item in effect_receipts[1:]),
                        "agent_default_capability_bundle",
                        receipt_index=index,
                    )
            if previous_after is not None:
                self._expect(boundary.get("before_semantic_digest") == previous_after, "statement_semantic_continuity", receipt_index=index)
            previous_after = str(boundary.get("after_semantic_digest"))
            expected_ordinal += 1
            cursor = index + 1
            if boundary.get("kind") == "statement_reject":
                rejected = True
        self._expect(cursor == terminal_index, "statement_effect_partition_complete", expected=cursor, observed=terminal_index)

        committed = sum(boundary.get("kind") == "statement_commit" for _, boundary in boundaries)
        rejected_count = sum(boundary.get("kind") == "statement_reject" for _, boundary in boundaries)
        self._expect(terminal.get("statement_count") == len(self.statements), "terminal_statement_count")
        self._expect(terminal.get("ast_digest") == self.ast_digest, "terminal_ast_digest")
        self._expect(terminal.get("committed_count") == committed, "terminal_committed_count")
        self._expect(terminal.get("transaction") is None, "terminal_transaction_closed")
        phase = terminal.get("phase")
        expected_terminal_step = (
            expected_ordinal
            if phase == "statement"
            else len(self.statements)
        )
        self._expect(terminal.get("step") == expected_terminal_step, "terminal_step")
        if terminal.get("kind") == "program_complete":
            self._expect(terminal.get("outcome") == "accepted" and phase == "complete", "terminal_success_shape")
            self._expect(committed == len(self.statements) and rejected_count == 0, "terminal_success_coverage")
            for field in ("failed_ordinal", "failed_line", "failed_statement_kind", "reason_code", "error"):
                self._expect(terminal.get(field) is None, "terminal_success_failure_fields", field=field)
        elif terminal.get("kind") == "program_reject" and phase == "statement":
            self._expect(terminal.get("outcome") == "rejected", "terminal_outcome")
            self._expect(rejected_count == 1 and committed + 1 == len(boundaries), "terminal_statement_rejection_shape")
            rejected_boundary = boundaries[-1][1] if boundaries else {}
            failed_ordinal = committed
            failed_statement = self.statements[failed_ordinal] if failed_ordinal < len(self.statements) else None
            self._expect(terminal.get("failed_ordinal") == failed_ordinal, "terminal_failed_ordinal")
            if failed_statement is not None:
                self._expect(terminal.get("failed_line") == failed_statement.line_number, "terminal_failed_line")
                self._expect(terminal.get("failed_statement_kind") == failed_statement.kind, "terminal_failed_statement_kind")
            self._expect(terminal.get("reason_code") == "E_RUNTIME", "terminal_statement_reason")
            self._expect(terminal.get("error") == rejected_boundary.get("error"), "terminal_statement_error")
        elif terminal.get("kind") == "program_reject" and phase == "finalization":
            self._expect(terminal.get("outcome") == "rejected", "terminal_outcome")
            self._expect(rejected_count == 0 and committed == len(self.statements), "terminal_finalization_shape")
            for field in ("failed_ordinal", "failed_line", "failed_statement_kind"):
                self._expect(terminal.get(field) is None, "terminal_finalization_failure_fields", field=field)
            self._expect(terminal.get("reason_code") == "E_FINALIZATION", "terminal_finalization_reason")
            self._expect(isinstance(terminal.get("error"), str) and bool(terminal.get("error")), "terminal_finalization_error")
        else:
            self.fail("terminal_phase_grammar", observed_kind=terminal.get("kind"), observed_phase=phase)

        if previous_after is not None and phase != "finalization":
            self._expect(terminal.get("semantic_digest") == previous_after, "terminal_boundary_state_anchor")

    def _validate_terminal(
        self, receipts: list[dict[str, Any]], final_state: dict[str, Any]
    ) -> None:
        if not receipts or receipts[-1].get("kind") not in {"program_complete", "program_reject"}:
            return
        terminal = receipts[-1]
        preterminal = receipts[-2].get("digest") if len(receipts) > 1 else ZERO_DIGEST
        self._expect(terminal.get("preterminal_chain_tip") == preterminal, "terminal_predecessor_commitment")
        self._expect(terminal.get("audit_receipt_count") == len(receipts), "terminal_receipt_count")
        self._expect(terminal.get("source_digest") == receipts[0].get("source_digest"), "terminal_source_digest")
        self._expect(terminal.get("step") == final_state.get("step"), "terminal_final_step")
        if terminal.get("kind") == "program_complete":
            self._expect(terminal.get("outcome") == "accepted" and terminal.get("phase") == "complete", "terminal_success_shape")
        else:
            self._expect(terminal.get("outcome") == "rejected" and terminal.get("phase") in {"parse", "static", "statement", "finalization"}, "terminal_rejection_shape")
        semantic_state = terminal.get("final_semantic_state")
        if not isinstance(semantic_state, dict):
            self.fail("terminal_semantic_state")
        else:
            unsigned = copy.deepcopy(semantic_state)
            observed = unsigned.pop("semantic_digest", None)
            expected = digest(unsigned)
            self._expect(observed == expected, "terminal_semantic_state_digest")
            self._expect(terminal.get("semantic_digest") == expected, "terminal_semantic_digest")
            projection = _semantic_projection(final_state)
            self._expect(semantic_state == projection, "terminal_final_state_correspondence")
        snapshot = copy.deepcopy(final_state)
        observed_snapshot = snapshot.pop("snapshot_digest", None)
        self._expect(observed_snapshot == digest(snapshot), "final_snapshot_digest")
        self._expect(final_state.get("receipt_count") == len(receipts), "final_receipt_count")
        self._expect(final_state.get("receipt_chain_tip") == receipts[-1].get("digest"), "final_receipt_tip")

    def _apply_receipt(self, receipt: dict[str, Any]) -> None:
        kind = str(receipt.get("kind"))
        index = int(receipt.get("index", -1))
        statement = self._statement(receipt)
        args = {} if statement is None else statement.args

        if kind == "module_declare":
            self._expect(self.module is None, "module_unique", receipt_index=index)
            self._expect(statement is None or (statement.kind == "module" and receipt.get("name") == args.get("name")), "module_source_correspondence", receipt_index=index)
            self.module = str(receipt.get("name"))
        elif kind == "lineage_declare":
            name = str(receipt.get("name"))
            parent = receipt.get("parent")
            self._expect(name not in self.lineages, "lineage_unique", receipt_index=index)
            self._expect(parent is None or str(parent) in self.lineages, "lineage_parent_exists", receipt_index=index)
            self._expect(statement is None or (statement.kind == "lineage" and name == args.get("name") and parent == args.get("parent")), "lineage_source_correspondence", receipt_index=index)
            self.lineages[name] = None if parent is None else str(parent)
        elif kind == "agent_declare":
            agent = receipt.get("agent")
            if not isinstance(agent, dict):
                self.fail("agent_payload", receipt_index=index)
            else:
                name = str(agent.get("name"))
                self._expect(
                    agent == {"name": args.get("name"), "lineage": args.get("lineage")},
                    "agent_source_payload",
                    receipt_index=index,
                )
                self._expect(name not in self.agents, "agent_unique", receipt_index=index)
                self._expect(str(agent.get("lineage")) in self.lineages, "agent_lineage_exists", receipt_index=index)
                self._expect(statement is None or (statement.kind == "agent" and name == args.get("name") and agent.get("lineage") == args.get("lineage")), "agent_source_correspondence", receipt_index=index)
                self.agents[name] = copy.deepcopy(agent)
                self.memories.setdefault(name, [])
        elif kind == "capability_grant":
            self._install_capability(receipt)
        elif kind == "capability_revoke":
            self._revoke_capability(receipt)
        elif kind in {"observe", "infer", "simulate", "inject", "neural_proposal", "communicate"}:
            packet = receipt.get("packet")
            if isinstance(packet, dict):
                self._validate_packet_constructor(kind, receipt, packet)
            else:
                self.fail("packet_payload", receipt_index=index, kind=kind)
        elif kind in {"bind", "quarantine", "endorse", "authorize"}:
            self._apply_packet_mutation(receipt)
        elif kind in {"proof_construct", "trusted_attestation"}:
            proof = receipt.get("proof")
            if isinstance(proof, dict):
                self._install_proof(proof, receipt)
            else:
                self.fail("proof_payload", receipt_index=index)
        elif kind in {"proof_use", "proof_consume"}:
            self._use_proof(receipt)
        elif kind == "neural_admission":
            packet = receipt.get("packet")
            current = self.packets.get(str(packet.get("name"))) if isinstance(packet, dict) else None
            self._expect(current is not None and current.get("status") == "provisional", "neural_admission_candidate", receipt_index=index)
            agent = str(receipt.get("agent"))
            self._expect(
                statement is not None
                and statement.kind == "admit"
                and args.get("agent") == agent
                and isinstance(packet, dict)
                and args.get("packet") == packet.get("name"),
                "neural_admission_source_correspondence",
                receipt_index=index,
            )
            supplied = [
                self.proofs.get(str(name)) for name in tuple(args.get("proofs", ()))
            ]
            origin = next(
                (
                    proof
                    for proof in supplied
                    if isinstance(proof, dict)
                    and proof.get("kind") == "origin"
                    and proof.get("trusted")
                    and proof.get("subject") == (None if current is None else current.get("name"))
                    and proof.get("agent") == agent
                ),
                None,
            )
            relevance = next(
                (
                    proof
                    for proof in supplied
                    if isinstance(proof, dict)
                    and proof.get("kind") == "relevance"
                    and proof.get("trusted")
                    and proof.get("subject") == (None if current is None else current.get("name"))
                    and proof.get("agent") == agent
                ),
                None,
            )
            self._expect(
                receipt.get("origin_proof") == (None if origin is None else origin.get("proof_digest"))
                and receipt.get("relevance_proof") == (None if relevance is None else relevance.get("proof_digest")),
                "neural_admission_source_proofs",
                receipt_index=index,
            )
            self._expect(origin is not None and origin.get("kind") == "origin" and origin.get("trusted") and origin.get("subject") == (None if current is None else current.get("name")) and origin.get("agent") == agent, "neural_admission_origin_proof", receipt_index=index)
            self._expect(relevance is not None and relevance.get("kind") == "relevance" and relevance.get("trusted") and relevance.get("subject") == (None if current is None else current.get("name")) and relevance.get("agent") == agent, "neural_admission_relevance_proof", receipt_index=index)
            if isinstance(packet, dict):
                self._packet_digest_valid(packet, index)
                if current is not None:
                    # Admission resolves provenance, so source_agent,
                    # source_lineage, and therefore content_digest legitimately
                    # change.  The candidate payload itself must not.
                    for field in (
                        "name",
                        "content",
                        "confidence",
                        "simulated",
                        "parent_digest",
                        "latent_source",
                        "accessible_to",
                        "endorsed_by",
                        "authorizations",
                        "observation_tokens",
                        "support",
                        "refutation",
                        "unresolved",
                    ):
                        self._expect(
                            packet.get(field) == current.get(field),
                            "neural_admission_candidate_preservation",
                            receipt_index=index,
                            field=field,
                        )
                    self._expect(
                        origin is not None
                        and relevance is not None
                        and origin.get("subject_digest") == current.get("content_digest")
                        and relevance.get("subject_digest") == current.get("content_digest"),
                        "neural_admission_proof_content_binding",
                        receipt_index=index,
                    )
                    expected_source_agent = (
                        origin.get("source_agent") if origin is not None else None
                    ) or agent
                    expected_source_lineage = (
                        origin.get("source_lineage") if origin is not None else None
                    ) or self.agents.get(agent, {}).get("lineage")
                    self._expect(
                        packet.get("source_agent") == expected_source_agent
                        and packet.get("source_lineage") == expected_source_lineage,
                        "neural_admission_resolved_origin",
                        receipt_index=index,
                    )
                    self._expect(
                        self._packet_list(packet, "bound_to")
                        == self._packet_list(current, "bound_to") | {agent}
                        and self._packet_list(packet, "quarantined_by")
                        == self._packet_list(current, "quarantined_by") - {agent},
                        "neural_admission_access_transition",
                        receipt_index=index,
                    )
                    expected_packet = copy.deepcopy(current)
                    expected_packet["source_agent"] = expected_source_agent
                    expected_packet["source_lineage"] = expected_source_lineage
                    expected_packet["provenance"] = "inferred"
                    expected_packet["status"] = "admitted"
                    expected_packet["obligations"] = []
                    expected_packet["bound_to"] = sorted(
                        self._packet_list(current, "bound_to") | {agent}
                    )
                    expected_packet["quarantined_by"] = sorted(
                        self._packet_list(current, "quarantined_by") - {agent}
                    )
                    expected_packet["content_digest"] = digest(
                        _packet_content_payload(expected_packet)
                    )
                    expected_packet["packet_digest"] = digest(
                        _packet_state_payload(expected_packet)
                    )
                    self._expect(
                        packet == expected_packet,
                        "neural_admission_exact_transition",
                        receipt_index=index,
                    )
                self._expect(packet.get("provenance") == "inferred" and packet.get("status") == "admitted" and not self._packet_list(packet, "obligations") and agent in self._packet_list(packet, "bound_to") and agent not in self._packet_list(packet, "quarantined_by"), "neural_admission_transition", receipt_index=index)
                self._set_packet(packet)
        elif kind == "neural_rejection":
            packet = receipt.get("packet")
            current = self.packets.get(str(packet.get("name"))) if isinstance(packet, dict) else None
            self._expect(current is not None and current.get("status") == "provisional", "neural_rejection_candidate", receipt_index=index)
            agent = str(receipt.get("agent"))
            self._expect(
                statement is not None
                and statement.kind == "reject_candidate"
                and args.get("agent") == agent
                and isinstance(packet, dict)
                and args.get("packet") == packet.get("name"),
                "neural_rejection_source_correspondence",
                receipt_index=index,
            )
            if isinstance(packet, dict):
                self._packet_digest_valid(packet, index)
                if current is not None:
                    expected_packet = copy.deepcopy(current)
                    expected_packet["status"] = "rejected"
                    expected_packet["obligations"] = []
                    expected_packet["quarantined_by"] = sorted(
                        self._packet_list(current, "quarantined_by") | {agent}
                    )
                    expected_packet["packet_digest"] = digest(
                        _packet_state_payload(expected_packet)
                    )
                    self._expect(
                        packet == expected_packet,
                        "neural_rejection_exact_transition",
                        receipt_index=index,
                    )
                self._expect(packet.get("status") == "rejected" and not self._packet_list(packet, "obligations") and agent in self._packet_list(packet, "quarantined_by"), "neural_rejection_transition", receipt_index=index)
                self._set_packet(packet)
        elif kind == "memory_write":
            self._write_memory(receipt)
        elif kind == "plan":
            self._install_plan(receipt)
        elif kind == "execute":
            self._execute_action(receipt)
        elif kind == "feedback":
            self._feedback_action(receipt)
        elif kind in {"transaction_begin", "transaction_commit", "transaction_rollback"}:
            self._handle_transaction(receipt)
        elif kind == "secret_register":
            self._expect(
                statement is not None
                and statement.kind == "secret"
                and receipt.get("name") == args.get("name")
                and receipt.get("value_digest") == digest(args.get("value")),
                "secret_source_correspondence",
                receipt_index=index,
            )
            if statement is not None and statement.kind == "secret":
                self.private_secrets[str(args.get("name"))] = str(args.get("value"))
                self.secret_digests[str(args.get("name"))] = digest(args.get("value"))
        elif kind in {"space_declare", "vector_declare", "operator", "operator_apply", "transport", "projector_check", "intertwiner_check", "contract_declare", "contract_check", "receipt_chain_verify", "session_declare", "session_transition_declare", "session_terminal_declare", "session_verify", "session_start", "session_advance", "metadata_publish", "assert_pass", "show"}:
            # These receipts are source-bound and terminal-state-bound here. The
            # protected provenance/authority state is reconstructed independently
            # above; numerical/session refinements remain separate finite checks.
            pass

    def _compare_reconstructed_state(self, final_state: dict[str, Any]) -> None:
        expected_capabilities: dict[str, dict[str, Any]] = {}
        for (agent, effect), capability in sorted(self.capabilities.items()):
            expected_capabilities.setdefault(agent, {})[effect] = copy.deepcopy(capability)
        for field, expected, observed in (
            ("module", self.module, final_state.get("module")),
            ("lineages", self.lineages, final_state.get("lineage_parents", {})),
            ("agents", self.agents, final_state.get("agents", {})),
            ("packets", self.packets, final_state.get("packets", {})),
            ("proofs", self.proofs, final_state.get("proofs", {})),
            ("memories", self.memories, final_state.get("memories", {})),
            ("actions", self.actions, final_state.get("actions", {})),
            ("capabilities", expected_capabilities, final_state.get("capabilities", {})),
            ("secret_digests", self.secret_digests, final_state.get("secret_digests", {})),
        ):
            self._expect(expected == observed, f"final_{field}_correspondence")

    def _verify_supplementary_same_runtime_replay(
        self,
        records: list[dict[str, Any]],
        final_state: dict[str, Any],
        source: str,
    ) -> None:
        """Replay delegated semantics without conflating them with independence."""

        try:
            from .osl_core import OSLError, OSLRuntime, OSLStaticError
        except ImportError:
            from osl_core import OSLError, OSLRuntime, OSLStaticError  # type: ignore

        filename = "<string>"
        if records and isinstance(records[0].get("filename"), str):
            filename = str(records[0]["filename"])
        runtime = OSLRuntime()
        runtime_error: Exception | None = None
        try:
            runtime.run_text(source, filename=filename)
        except (OSLError, OSLStaticError) as exc:
            runtime_error = exc

        receipt_match = canonical_json(runtime.audit_log) == canonical_json(records)
        replay_state = runtime.state.snapshot()
        final_state_match = canonical_json(replay_state) == canonical_json(final_state)
        self.supplementary_replay = {
            "performed": True,
            "receipt_match": receipt_match,
            "final_state_match": final_state_match,
            "runtime_outcome": "accepted" if runtime_error is None else "rejected",
            "runtime_error_type": (
                None if runtime_error is None else type(runtime_error).__name__
            ),
        }
        self._expect(receipt_match, "supplementary_replay_receipts")
        self._expect(final_state_match, "supplementary_replay_final_state")

    def _verify_strict(
        self,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any],
        source: str | None = None,
    ) -> dict[str, Any]:
        # A digest chain alone is self-consistent, not authoritative: an
        # attacker can rewrite a trace and recompute every public SHA-256
        # value.  Strict verification therefore always requires the source
        # whose statement manifests authorize the semantic receipts.
        if source is None:
            self.fail("source_binding_required", reason_code="UNBOUND_SOURCE")
        self._source_setup(source)
        records = copy.deepcopy(list(receipts))
        self._validate_lifecycle_and_boundaries(records, source)

        previous = ZERO_DIGEST
        previous_step = -1
        for expected_index, receipt in enumerate(records):
            self.counters.receipts += 1
            index = receipt.get("index")
            self._expect(receipt.get("schema") == RECEIPT_SCHEMA, "receipt_schema", receipt_index=expected_index)
            self._expect(receipt.get("core_version") == CORE_VERSION, "receipt_core_version", receipt_index=expected_index)
            self._expect(index == expected_index, "receipt_index", expected=expected_index, observed=index)
            self._expect(receipt.get("state_index") == expected_index, "receipt_state_index", receipt_index=expected_index)
            self._expect(receipt.get("previous_digest") == previous, "receipt_hash_chain", receipt_index=expected_index)
            expected_digest = digest(_without_digest(receipt))
            self._expect(receipt.get("digest") == expected_digest, "receipt_digest", receipt_index=expected_index)
            try:
                step = int(receipt.get("step"))
            except (TypeError, ValueError):
                step = -1
                self.fail("receipt_step", receipt_index=expected_index)
            self._expect(step >= previous_step, "receipt_step_monotonicity", receipt_index=expected_index)
            previous_step = step
            previous = str(receipt.get("digest"))
            kind = str(receipt.get("kind"))
            self._expect(kind in KNOWN_RECEIPT_KINDS, "known_receipt_kind", receipt_index=expected_index, kind=kind)

            if kind in SEMANTIC_RECEIPT_KINDS:
                active_name = None if self.active_transaction is None else self.active_transaction.get("name")
                if kind == "transaction_begin":
                    pass
                elif kind in {"transaction_commit", "transaction_rollback"}:
                    self._expect(receipt.get("transaction") == active_name, "receipt_transaction_scope", receipt_index=expected_index)
                else:
                    self._expect(receipt.get("transaction") == active_name, "receipt_transaction_scope", receipt_index=expected_index)
                self._apply_receipt(receipt)
            elif kind in {"statement_commit", "statement_reject"}:
                active_name = None if self.active_transaction is None else self.active_transaction.get("name")
                self._expect(receipt.get("transaction") == active_name, "boundary_transaction_scope", receipt_index=expected_index)
            else:
                self._expect(receipt.get("transaction") is None, "lifecycle_transaction_scope", receipt_index=expected_index)

        self._expect(self.active_transaction is None, "transactions_closed")
        unused_linear = sorted(
            name
            for name, proof in self.proofs.items()
            if proof.get("resource_mode") == "linear"
            and isinstance(proof.get("remaining_uses"), int)
            and proof.get("remaining_uses", 0) > 0
        )
        terminal = records[-1] if records else {}
        if terminal.get("kind") == "program_complete":
            self._expect(not unused_linear, "linear_proof_finalization", proofs=unused_linear)
        elif terminal.get("kind") == "program_reject" and terminal.get("phase") == "finalization" and unused_linear:
            line_number = self.statements[-1].line_number if self.statements else 0
            self._expect(
                terminal.get("error")
                == f"line {line_number}: linear proofs must be consumed exactly once: "
                + ", ".join(unused_linear),
                "linear_proof_finalization_error",
                proofs=unused_linear,
            )
        self._validate_terminal(records, final_state)
        self._compare_reconstructed_state(final_state)
        if source is not None:
            self._verify_supplementary_same_runtime_replay(
                records, final_state, source
            )

        categories = {
            "schema_and_hash": {"receipt_schema", "receipt_core_version", "receipt_index", "receipt_state_index", "receipt_hash_chain", "receipt_digest", "receipt_step", "receipt_step_monotonicity", "known_receipt_kind"},
            "source_and_lifecycle": {failure["property"] for failure in self.failures if failure["property"].startswith(("program_", "parse_", "static_", "statement_", "semantic_", "terminal_", "all_statements"))},
            "packet_and_memory": {failure["property"] for failure in self.failures if failure["property"].startswith(("packet_", "observe_", "simulate_", "inject_", "infer_", "communicate_", "neural_", "memory_", "observed_"))},
            "proofs": {failure["property"] for failure in self.failures if failure["property"].startswith(("proof_", "use_proof_", "ownership_proof_"))},
            "capabilities": {failure["property"] for failure in self.failures if "capability" in failure["property"]},
            "actions": {failure["property"] for failure in self.failures if failure["property"].startswith(("action_", "plan_", "execute_", "feedback_"))},
            "transactions": {failure["property"] for failure in self.failures if failure["property"].startswith(("transaction_", "transactions_", "receipt_transaction"))},
            "final_state": {failure["property"] for failure in self.failures if failure["property"].startswith("final_")},
            "supplementary_replay": {failure["property"] for failure in self.failures if failure["property"].startswith("supplementary_replay_")},
        }
        checks = {
            name: not any(failure["property"] in properties for failure in self.failures)
            for name, properties in categories.items()
        }
        independent_checks_pass = not any(
            not str(failure.get("property", "")).startswith("supplementary_replay_")
            for failure in self.failures
        )
        payload: dict[str, Any] = {
            "schema": "osl.kernel.verification.v2",
            "core_version": CORE_VERSION,
            "source_bound": source is not None,
            "checks": checks,
            "independent_checks_pass": independent_checks_pass,
            "all_checks_pass": not self.failures,
            "counters": asdict(self.counters),
            "failure_count": len(self.failures),
            "failures": self.failures,
            "audit_head_digest": records[-1].get("digest") if records else None,
            # Retain the public report field exposed by the packaged kernel.
            "rolled_back_transaction_count": self.counters.transaction_rollbacks,
            "supplementary_same_runtime_replay": self.supplementary_replay,
            "claim_boundary": (
                "Independent finite replay covers OSL-Core 0.5 source/lifecycle "
                "structure and the protected packet, proof, memory, capability, "
                "and action ledgers, including their rollback and secret-commitment "
                "state. Numerical/operator semantics, contracts, complete session "
                "graphs, metadata, assertions/show, complete transaction-projection "
                "digests, and interpreter rejection causality remain delegated to "
                "the packaged same-runtime replay or dedicated verifiers. SHA-256 "
                "authenticates no principal."
            ),
        }
        payload["verification_digest"] = digest(payload)
        return payload

    def verify(
        self,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any],
        source: str | None = None,
    ) -> dict[str, Any]:
        """Verify untrusted evidence without propagating malformed-input errors."""

        try:
            return self._verify_strict(receipts, final_state, source=source)
        except Exception as exc:  # fail closed at the verifier trust boundary
            self.fail(
                "malformed_verifier_input",
                error=f"{type(exc).__name__}: {exc}",
            )
            checks = {
                "schema_and_hash": False,
                "source_and_lifecycle": False,
                "packet_and_memory": False,
                "proofs": False,
                "capabilities": False,
                "actions": False,
                "transactions": False,
                "final_state": False,
                "supplementary_replay": False,
            }
            audit_head = None
            if receipts and isinstance(receipts[-1], dict):
                audit_head = receipts[-1].get("digest")
            payload: dict[str, Any] = {
                "schema": "osl.kernel.verification.v2",
                "core_version": CORE_VERSION,
                "source_bound": source is not None,
                "checks": checks,
                "independent_checks_pass": False,
                "all_checks_pass": False,
                "counters": asdict(self.counters),
                "failure_count": len(self.failures),
                "failures": self.failures,
                "audit_head_digest": audit_head,
                "rolled_back_transaction_count": self.counters.transaction_rollbacks,
                "supplementary_same_runtime_replay": self.supplementary_replay,
                "claim_boundary": (
                    "Malformed evidence was rejected at the verifier boundary. "
                    "No semantic verification claim is made."
                ),
            }
            payload["verification_digest"] = digest(payload)
            return payload


def verify_program(path: Path) -> dict[str, Any]:
    try:
        from .osl_core import OSLError, OSLRuntime, OSLStaticError
    except ImportError:
        from osl_core import OSLError, OSLRuntime, OSLStaticError  # type: ignore

    source = path.read_text(encoding="utf-8")
    runtime = OSLRuntime()
    runtime_error: str | None = None
    try:
        runtime.run_text(source, filename=str(path))
    except (OSLError, OSLStaticError) as exc:
        runtime_error = str(exc)
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
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
        "schema": "osl.kernel.suite.v2",
        "core_version": CORE_VERSION,
        "language_version": "OSL-Core 0.5",
        "program_count": len(records),
        "verified_program_count": sum(bool(record["all_checks_pass"]) for record in records),
        "receipt_count": sum(int(record["counters"]["receipts"]) for record in records),
        "proof_count": sum(int(record["counters"]["proofs"]) for record in records),
        "memory_record_count": sum(
            int(record["counters"]["memory_records"]) for record in records
        ),
        "transaction_rollback_count": sum(
            int(record["counters"]["transaction_rollbacks"])
            for record in records
        ),
        "records": records,
        "all_checks_pass": bool(records and all(record["all_checks_pass"] for record in records)),
    }
    payload["suite_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = verify_directory(args.path) if args.path.is_dir() else verify_program(args.path)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
