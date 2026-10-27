#!/usr/bin/env python3
"""Reference interpreter for OSL-Core 0.4 receipt hardening.

Core 0.4 keeps the finite Core 0.3 source language while making every execution
attempt auditable: source/AST anchors are explicit, parse and static failures
produce terminal traces, statement spans use the append-only audit index, and
the terminal receipt binds the complete semantic projection.  Capabilities,
proof resources, provenance, and rollback receive stricter runtime checks.

This remains a deterministic research interpreter, not an OS sandbox, an
authentication system, or a mechanized proof-assistant kernel.
"""
from __future__ import annotations

import argparse
import ast
import copy
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:  # pragma: no cover - package/script dual use
    from .osl_model import (
        CONTRACT_TEMPLATES,
        EFFECTS,
        MEMORY_COMPATIBILITY,
        PROOF_KINDS,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        Action,
        Agent,
        Capability,
        MemoryRecord,
        Operator,
        OSLError,
        OSLStaticError,
        Packet,
        ProofTerm,
        RuntimeState,
        SessionProtocol,
        Space,
        Statement,
        TemporalContract,
        VectorValue,
        canonical_json,
        digest,
        verify_receipt_chain,
    )
    from .osl_parser import StaticChecker, parse_program
    from .osl_session_verify import verify_session_protocol
except ImportError:  # pragma: no cover
    from osl_model import (  # type: ignore
        CONTRACT_TEMPLATES,
        EFFECTS,
        MEMORY_COMPATIBILITY,
        PROOF_KINDS,
        PROOF_RESOURCE_MODES,
        PROVENANCE_CLASSES,
        Action,
        Agent,
        Capability,
        MemoryRecord,
        Operator,
        OSLError,
        OSLStaticError,
        Packet,
        ProofTerm,
        RuntimeState,
        SessionProtocol,
        Space,
        Statement,
        TemporalContract,
        VectorValue,
        canonical_json,
        digest,
        verify_receipt_chain,
    )
    from osl_parser import StaticChecker, parse_program  # type: ignore
    from osl_session_verify import verify_session_protocol  # type: ignore


CORE_VERSION = "0.4"
RECEIPT_SCHEMA = "osl.core.receipt.v2"


class OSLRuntime:
    """Deterministic state machine for the finite OSL-Core 0.4 language."""

    def __init__(self) -> None:
        self.state = RuntimeState()
        # State-local receipts are transactional and may be restored by a
        # rollback.  ``audit_log`` is deliberately outside RuntimeState, so it
        # remains append-only for the lifetime of the runtime instance.
        self.audit_log: list[dict[str, Any]] = []
        self._line_number = 0
        self._secrets: dict[str, Any] = {}
        self._transaction_name: str | None = None
        self._transaction_checkpoint: RuntimeState | None = None
        self._transaction_secrets_checkpoint: dict[str, Any] | None = None
        self._transaction_checkpoint_digest: str | None = None
        self._transaction_begin_audit_index: int | None = None
        self._transaction_begin_step: int | None = None
        self._run_started = False
        self._terminal_emitted = False
        self._source_digest: str | None = None
        self._ast_digest: str | None = None
        self._statement_count = 0
        self._committed_count = 0

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------
    def _error(self, message: str) -> OSLError:
        return OSLError(f"line {self._line_number}: {message}")

    def _event(self, kind: str, **payload: Any) -> dict[str, Any]:
        body = {
            "index": len(self.state.events),
            "step": self.state.step,
            "kind": kind,
            **payload,
        }
        body["digest"] = digest(body)
        self.state.events.append(body)
        return body

    def _receipt(self, kind: str, **payload: Any) -> dict[str, Any]:
        if self._terminal_emitted:
            raise OSLError("cannot append a receipt after the program terminal")
        previous_digest = (
            self.audit_log[-1]["digest"] if self.audit_log else "0" * 64
        )
        body = {
            "schema": RECEIPT_SCHEMA,
            "core_version": CORE_VERSION,
            "index": len(self.audit_log),
            "state_index": len(self.state.receipts),
            "step": self.state.step,
            "kind": kind,
            "transaction": self._transaction_name,
            "previous_digest": previous_digest,
            **payload,
        }
        body["digest"] = digest(body)
        self.state.receipts.append(copy.deepcopy(body))
        self.audit_log.append(copy.deepcopy(body))
        self._monitor_contract_event(kind, body)
        return body

    @staticmethod
    def _statement_manifest(statement: Statement, ordinal: int) -> dict[str, Any]:
        payload = {
            "ordinal": ordinal,
            "line_number": statement.line_number,
            "kind": statement.kind,
            "source": statement.source,
            "args": statement.args,
        }
        payload["node_digest"] = digest(payload)
        return payload

    def _transaction_projection(self) -> dict[str, Any]:
        projection = self.state.semantic_snapshot()
        projection.pop("semantic_digest", None)
        projection.pop("step", None)
        projection["private_secret_commitments"] = {
            name: digest(value) for name, value in sorted(self._secrets.items())
        }
        return projection

    def _terminal(
        self,
        kind: str,
        *,
        phase: str,
        error: str | None = None,
        reason_code: str | None = None,
        failed_ordinal: int | None = None,
        failed_line: int | None = None,
        failed_statement_kind: str | None = None,
    ) -> dict[str, Any]:
        if kind not in {"program_complete", "program_reject"}:
            raise ValueError(f"invalid terminal kind {kind!r}")
        semantic_state = self.state.semantic_snapshot()
        receipt = self._receipt(
            kind,
            outcome="accepted" if kind == "program_complete" else "rejected",
            phase=phase,
            source_digest=self._source_digest,
            ast_digest=self._ast_digest,
            statement_count=self._statement_count,
            committed_count=self._committed_count,
            failed_ordinal=failed_ordinal,
            failed_line=failed_line,
            failed_statement_kind=failed_statement_kind,
            reason_code=reason_code,
            error=error,
            final_semantic_state=semantic_state,
            semantic_digest=semantic_state["semantic_digest"],
            preterminal_chain_tip=(
                self.audit_log[-1]["digest"] if self.audit_log else "0" * 64
            ),
            audit_receipt_count=len(self.audit_log) + 1,
        )
        self._terminal_emitted = True
        return receipt

    def _agent(self, name: str) -> Agent:
        try:
            return self.state.agents[name]
        except KeyError as exc:
            raise self._error(f"unknown agent {name!r}") from exc

    def _packet(self, name: str) -> Packet:
        try:
            return self.state.packets[name]
        except KeyError as exc:
            raise self._error(f"unknown packet {name!r}") from exc

    def _operator(self, name: str) -> Operator:
        try:
            return self.state.operators[name]
        except KeyError as exc:
            raise self._error(f"unknown operator {name!r}") from exc

    def _vector(self, name: str) -> VectorValue:
        try:
            return self.state.vectors[name]
        except KeyError as exc:
            raise self._error(f"unknown vector {name!r}") from exc

    def _space(self, name: str) -> Space:
        try:
            return self.state.spaces[name]
        except KeyError as exc:
            raise self._error(f"unknown space {name!r}") from exc

    def _proof(self, name: str) -> ProofTerm:
        try:
            return self.state.proofs[name]
        except KeyError as exc:
            raise self._error(f"unknown proof {name!r}") from exc

    def _session(self, name: str) -> SessionProtocol:
        try:
            return self.state.sessions[name]
        except KeyError as exc:
            raise self._error(f"unknown session {name!r}") from exc

    def _capability(self, agent_name: str, effect: str) -> Capability:
        try:
            capability = self.state.capabilities[agent_name][effect]
        except KeyError as exc:
            raise self._error(
                f"agent {agent_name!r} lacks capability for effect {effect!r}"
            ) from exc
        if capability.expires_at is not None and self.state.step > capability.expires_at:
            raise self._error(
                f"capability {effect!r} for agent {agent_name!r} expired at step "
                f"{capability.expires_at}"
            )
        if capability.remaining_uses is not None and capability.remaining_uses <= 0:
            raise self._error(
                f"capability {effect!r} for agent {agent_name!r} has no remaining uses"
            )
        return capability

    def _install_default_capabilities(self, agent_name: str) -> None:
        table = self.state.capabilities.setdefault(agent_name, {})
        for effect in ("read", "communicate", "simulate"):
            if effect in table:
                continue
            cap = Capability(
                effect=effect,
                initial_uses=None,
                remaining_uses=None,
                source="default",
                grant_index=len(self.audit_log),
                issued_step=self.state.step,
            )
            cap.refresh_digest(agent=agent_name)
            table[effect] = cap
            self._receipt(
                "capability_grant",
                agent=agent_name,
                capability=cap.canonical(),
                previous_capability=None,
                implicit=True,
            )

    # ------------------------------------------------------------------
    # Parsing, static checking, and execution lifecycle
    # ------------------------------------------------------------------
    def run_text(self, source: str, *, filename: str = "<string>") -> RuntimeState:
        if self._run_started:
            raise OSLError("OSLRuntime instances execute exactly one program attempt")
        self._run_started = True
        self._source_digest = digest(source)
        source_bytes = len(source.encode("utf-8"))
        source_lines = len(source.splitlines())
        self._receipt(
            "program_open",
            filename=filename,
            source_digest=self._source_digest,
            source_bytes=source_bytes,
            source_lines=source_lines,
        )

        try:
            statements = parse_program(source)
        except OSLStaticError as exc:
            error_text = str(exc)
            self._receipt("parse_reject", error=error_text)
            self._terminal(
                "program_reject",
                phase="parse",
                error=error_text,
                reason_code="E_PARSE",
            )
            raise

        manifests = tuple(
            self._statement_manifest(statement, ordinal)
            for ordinal, statement in enumerate(statements)
        )
        self._statement_count = len(statements)
        self._ast_digest = digest(manifests)
        self._receipt(
            "parse_accept",
            ast_digest=self._ast_digest,
            statement_count=self._statement_count,
        )

        try:
            report = StaticChecker().check(statements)
        except OSLStaticError as exc:
            error_text = str(exc)
            self._receipt(
                "static_reject",
                ast_digest=self._ast_digest,
                statement_count=self._statement_count,
                error=error_text,
            )
            self._terminal(
                "program_reject",
                phase="static",
                error=error_text,
                reason_code="E_STATIC",
            )
            raise

        self.state.static_report = asdict(report)
        self._receipt(
            "static_check",
            ast_digest=self._ast_digest,
            report=self.state.static_report,
        )

        for ordinal, statement in enumerate(statements):
            self._line_number = statement.line_number
            manifest = manifests[ordinal]
            before_state = self.state.semantic_snapshot()
            before_digest = before_state["semantic_digest"]
            receipt_start = len(self.audit_log)
            self.state.step += 1
            try:
                self.execute_statement(statement)
                self._check_contracts(final=False)
            except OSLError as exc:
                rolled_back = False
                error_text = str(exc)
                if self._transaction_name is not None:
                    tx_name = self._transaction_name
                    self._restore_transaction(
                        reason=error_text, automatic=True, failed_step=self.state.step
                    )
                    rolled_back = True
                    error_text = (
                        f"line {statement.line_number}: transaction {tx_name!r} "
                        f"rolled back: {exc}"
                    )
                after_state = self.state.semantic_snapshot()
                after_digest = after_state["semantic_digest"]
                emitted = tuple(range(receipt_start, len(self.audit_log)))
                self._receipt(
                    "statement_reject",
                    statement_ordinal=ordinal,
                    line_number=statement.line_number,
                    statement_kind=statement.kind,
                    source_digest=digest(statement.source),
                    node_digest=manifest["node_digest"],
                    before_semantic_digest=before_digest,
                    after_semantic_digest=after_digest,
                    emitted_receipt_indices=emitted,
                    effect_span=(receipt_start, len(self.audit_log)),
                    rolled_back=rolled_back,
                    error=error_text,
                )
                self._terminal(
                    "program_reject",
                    phase="statement",
                    reason_code="E_RUNTIME",
                    failed_ordinal=ordinal,
                    failed_line=statement.line_number,
                    failed_statement_kind=statement.kind,
                    error=error_text,
                )
                raise OSLError(error_text) from exc

            after_state = self.state.semantic_snapshot()
            after_digest = after_state["semantic_digest"]
            emitted = tuple(range(receipt_start, len(self.audit_log)))
            self._receipt(
                "statement_commit",
                statement_ordinal=ordinal,
                line_number=statement.line_number,
                statement_kind=statement.kind,
                source_digest=digest(statement.source),
                node_digest=manifest["node_digest"],
                before_semantic_digest=before_digest,
                after_semantic_digest=after_digest,
                emitted_receipt_indices=emitted,
                effect_span=(receipt_start, len(self.audit_log)),
            )
            self._committed_count += 1

        try:
            self._check_linear_proof_obligations()
            self._check_contracts(final=True)
        except OSLError as exc:
            self._terminal(
                "program_reject",
                phase="finalization",
                reason_code="E_FINALIZATION",
                error=str(exc),
            )
            raise
        self._terminal(
            "program_complete",
            phase="complete",
        )
        chain = verify_receipt_chain(self.audit_log)
        if not chain["all_checks_pass"]:
            raise OSLError("append-only receipt chain failed verification")
        return self.state

    def run_file(self, path: Path) -> RuntimeState:
        return self.run_text(path.read_text(encoding="utf-8"), filename=str(path))

    def execute_statement(self, statement: Statement) -> None:
        kind = statement.kind
        a = statement.args

        # --------------------------------------------------------------
        # Identity, declarations, and bounded capabilities
        # --------------------------------------------------------------
        if kind == "module":
            self.state.module = a["name"]
            self._event("module", name=a["name"])
            self._receipt("module_declare", name=a["name"])
            return

        if kind == "lineage":
            self.state.lineage_parents[a["name"]] = a["parent"]
            self._event("lineage", name=a["name"], parent=a["parent"])
            self._receipt("lineage_declare", name=a["name"], parent=a["parent"])
            return

        if kind == "agent":
            agent = Agent(a["name"], a["lineage"])
            self.state.agents[agent.name] = agent
            self.state.memories.setdefault(agent.name, [])
            self._event("agent", name=agent.name, lineage=agent.lineage)
            self._receipt("agent_declare", agent=asdict(agent))
            self._install_default_capabilities(agent.name)
            return

        if kind == "grant":
            cap = Capability(
                effect=a["effect"],
                initial_uses=a["uses"],
                remaining_uses=a["uses"],
                expires_at=a["until"],
                source="grant",
                grant_index=len(self.audit_log),
                issued_step=self.state.step,
            )
            cap.refresh_digest(agent=a["agent"])
            table = self.state.capabilities.setdefault(a["agent"], {})
            previous = table.get(a["effect"])
            table[a["effect"]] = cap
            self._receipt(
                "capability_grant",
                agent=a["agent"],
                capability=cap.canonical(),
                previous_capability=(
                    None if previous is None else previous.canonical()
                ),
                implicit=False,
            )
            return

        if kind == "revoke":
            removed = self.state.capabilities.setdefault(a["agent"], {}).pop(a["effect"], None)
            self._receipt(
                "capability_revoke",
                agent=a["agent"],
                effect=a["effect"],
                revoked_capability=None if removed is None else removed.canonical(),
            )
            return

        # --------------------------------------------------------------
        # Numerical operator layer
        # --------------------------------------------------------------
        if kind == "space":
            space = Space(a["name"], a["dim"])
            self.state.spaces[a["name"]] = space
            self._event("space", name=a["name"], dim=a["dim"])
            self._receipt("space_declare", space=asdict(space))
            return

        if kind == "vector":
            space = self._space(a["space"])
            value = np.asarray(a["values"], dtype=float)
            if value.shape != (space.dim,):
                raise self._error(
                    f"vector {a['name']!r} has shape {value.shape}, expected {(space.dim,)}"
                )
            vector = VectorValue(a["name"], a["space"], value)
            self.state.vectors[a["name"]] = vector
            self._event("vector", name=a["name"], space=a["space"], value=value.tolist())
            self._receipt("vector_declare", vector=vector.canonical())
            return

        if kind == "operator":
            source = self._space(a["source_space"])
            target = self._space(a["target_space"])
            matrix = np.asarray(a["matrix"], dtype=float)
            expected = (target.dim, source.dim)
            if matrix.shape != expected:
                raise self._error(
                    f"operator {a['name']!r} has shape {matrix.shape}, expected {expected}"
                )
            if a["operator_kind"] == "projector" and not np.allclose(
                matrix @ matrix, matrix, atol=1e-9, rtol=0.0
            ):
                raise self._error(
                    f"operator {a['name']!r} declared projector but is not idempotent"
                )
            operator = Operator(
                a["name"],
                a["source_space"],
                a["target_space"],
                a["operator_kind"],
                matrix,
            )
            self.state.operators[a["name"]] = operator
            self._receipt("operator", operator=operator.canonical())
            return

        if kind == "apply":
            operator = self._operator(a["operator"])
            vector = self._vector(a["vector"])
            if vector.space != operator.source:
                raise self._error("operator source space does not match vector space")
            result = operator.matrix @ vector.value
            self.state.vectors[a["target"]] = VectorValue(
                a["target"], operator.target, result
            )
            self._event(
                "apply",
                target=a["target"],
                operator=a["operator"],
                vector=a["vector"],
                result=result.tolist(),
            )
            self._receipt(
                "operator_apply",
                target=a["target"],
                operator=a["operator"],
                vector=a["vector"],
                result=self.state.vectors[a["target"]].canonical(),
            )
            return

        if kind == "transport":
            operator = self._operator(a["operator"])
            transport = self._operator(a["transport"])
            if operator.source != operator.target:
                raise self._error("transported operator must be an endomorphism")
            if transport.source != operator.source or transport.target != operator.source:
                raise self._error("transport operator must act on the same space")
            try:
                inverse = np.linalg.inv(transport.matrix)
            except np.linalg.LinAlgError as exc:
                raise self._error("transport matrix must be invertible") from exc
            matrix = transport.matrix @ operator.matrix @ inverse
            result = Operator(
                a["result"], operator.source, operator.target, operator.kind, matrix
            )
            self.state.operators[a["result"]] = result
            self._receipt(
                "transport",
                source_operator=a["operator"],
                transport=a["transport"],
                result=result.canonical(),
            )
            return

        if kind == "check_projector":
            operator = self._operator(a["operator"])
            residual = float(
                np.linalg.norm(operator.matrix @ operator.matrix - operator.matrix)
            )
            if residual > a["tolerance"]:
                raise self._error(
                    f"projector residual {residual:.6g} exceeds tolerance "
                    f"{a['tolerance']:.6g}"
                )
            self._receipt(
                "projector_check",
                operator=a["operator"],
                residual=residual,
                tolerance=a["tolerance"],
            )
            return

        if kind == "check_intertwiner":
            transport = self._operator(a["transport"])
            left = self._operator(a["left"])
            right = self._operator(a["right"])
            if not (
                left.source == left.target == transport.source
                and right.source == right.target == transport.target
            ):
                raise self._error("intertwiner spaces are incompatible")
            residual = float(
                np.linalg.norm(transport.matrix @ left.matrix - right.matrix @ transport.matrix)
            )
            if residual > a["tolerance"]:
                raise self._error(
                    f"intertwiner residual {residual:.6g} exceeds tolerance "
                    f"{a['tolerance']:.6g}"
                )
            self._receipt(
                "intertwiner_check",
                transport=a["transport"],
                left=a["left"],
                right=a["right"],
                residual=residual,
                tolerance=a["tolerance"],
            )
            return

        # --------------------------------------------------------------
        # Provenance-aware packets and neural-boundary proposals
        # --------------------------------------------------------------
        if kind == "observe":
            agent = self._agent(a["agent"])
            packet = Packet(
                name=a["name"],
                content=a["content"],
                source_agent=agent.name,
                source_lineage=agent.lineage,
                provenance="observed",
                confidence=a["confidence"],
                accessible_to={agent.name},
                bound_to={agent.name},
                observation_tokens={agent.name},
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt("observe", packet=packet.canonical(include_digest=True))
            return

        if kind == "infer":
            agent = self._agent(a["agent"])
            source = self._packet(a["source_packet"])
            if source.status not in {"grounded", "admitted"}:
                raise self._error(
                    f"cannot infer from packet in status {source.status!r}"
                )
            if agent.name not in source.accessible_to:
                raise self._error(
                    f"agent {agent.name!r} cannot access source packet "
                    f"{a['source_packet']!r}"
                )
            packet = Packet(
                name=a["name"],
                content=a["content"],
                source_agent=agent.name,
                source_lineage=agent.lineage,
                provenance="inferred",
                confidence=a["confidence"],
                accessible_to={agent.name},
                bound_to={agent.name},
                parent_digest=source.packet_digest,
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt("infer", packet=packet.canonical(include_digest=True))
            return

        if kind == "simulate":
            agent = self._agent(a["agent"])
            packet = Packet(
                name=a["name"],
                content=a["content"],
                source_agent=agent.name,
                source_lineage=agent.lineage,
                provenance="simulated",
                confidence=a["confidence"],
                accessible_to={agent.name},
                bound_to={agent.name},
                simulated=True,
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt("simulate", packet=packet.canonical(include_digest=True))
            return

        if kind == "inject":
            self._agent(a["agent"])
            packet = Packet(
                name=a["name"],
                content=a["content"],
                source_agent="external",
                source_lineage="external",
                provenance="injected",
                confidence=a["confidence"],
                accessible_to={a["agent"]},
                quarantined_by={a["agent"]},
                status="quarantined",
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt(
                "inject", target=a["agent"], packet=packet.canonical(include_digest=True)
            )
            return

        if kind == "neural_propose":
            self._agent(a["agent"])
            packet = Packet(
                name=a["name"],
                content=a["content"],
                source_agent="unresolved",
                source_lineage="unresolved",
                provenance="unresolved",
                confidence=a["confidence"],
                accessible_to={a["agent"]},
                quarantined_by={a["agent"]},
                status="provisional",
                latent_source=a["feature"],
                obligations={"origin", "lineage", "task_relevance"},
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt(
                "neural_proposal",
                target=a["agent"],
                packet=packet.canonical(include_digest=True),
            )
            return

        if kind == "communicate":
            source = self._packet(a["source_packet"])
            self._agent(a["source_agent"])
            target = self._agent(a["target_agent"])
            if source.status not in {"grounded", "admitted"}:
                raise self._error(
                    f"cannot communicate packet in status {source.status!r}"
                )
            if a["source_agent"] not in source.accessible_to:
                raise self._error(
                    f"source agent {a['source_agent']!r} cannot access "
                    f"{a['source_packet']!r}"
                )
            if a["session"] is not None:
                self._advance_session(
                    a["session"], "communicate", a["source_agent"], a["target_agent"]
                )
            packet = Packet(
                name=a["target_packet"],
                content=source.content,
                source_agent=source.source_agent,
                source_lineage=source.source_lineage,
                provenance="communicated",
                confidence=source.confidence,
                accessible_to={target.name},
                bound_to={target.name},
                parent_digest=source.packet_digest,
                status="grounded" if source.status != "rejected" else "rejected",
            )
            packet.refresh_digest()
            self.state.packets[packet.name] = packet
            self._receipt(
                "communicate",
                from_agent=a["source_agent"],
                to_agent=target.name,
                session=a["session"],
                packet=packet.canonical(include_digest=True),
            )
            return

        if kind == "bind":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if a["agent"] not in packet.accessible_to:
                raise self._error(f"agent {a['agent']!r} cannot bind inaccessible packet")
            packet.bound_to.add(a["agent"])
            packet.refresh_digest()
            self._receipt(
                "bind", packet=a["packet"], agent=a["agent"], packet_digest=packet.packet_digest
            )
            return

        if kind == "quarantine":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            packet.quarantined_by.add(a["agent"])
            packet.status = "quarantined"
            packet.refresh_digest()
            self._receipt(
                "quarantine",
                packet=a["packet"],
                agent=a["agent"],
                packet_digest=packet.packet_digest,
            )
            return

        if kind == "endorse":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if a["agent"] not in packet.accessible_to:
                raise self._error("cannot endorse inaccessible packet")
            if a["agent"] in packet.quarantined_by:
                raise self._error("cannot endorse quarantined packet")
            if packet.status not in {"grounded", "admitted"}:
                raise self._error(
                    f"cannot endorse packet in status {packet.status!r}"
                )
            if packet.confidence < a["threshold"]:
                raise self._error(
                    f"confidence {packet.confidence:.3f} is below threshold "
                    f"{a['threshold']:.3f}"
                )
            packet.endorsed_by.add(a["agent"])
            packet.refresh_digest()
            self._receipt(
                "endorse",
                packet=a["packet"],
                agent=a["agent"],
                threshold=a["threshold"],
                packet_digest=packet.packet_digest,
            )
            return

        if kind == "authorize":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if a["agent"] not in packet.accessible_to or a["agent"] not in packet.bound_to:
                raise self._error("authorization requires accessible, bound content")
            if a["agent"] in packet.quarantined_by:
                raise self._error("authorization denied for quarantined packet")
            if packet.status not in {"grounded", "admitted"}:
                raise self._error(
                    f"cannot authorize packet in status {packet.status!r}"
                )
            if a["proof"] is not None:
                self._verify_proof(
                    a["proof"], packet=packet, agent=a["agent"], consume=True
                )
            packet.authorizations.setdefault(a["agent"], set()).add(a["scope"])
            packet.refresh_digest()
            self._receipt(
                "authorize",
                packet=a["packet"],
                agent=a["agent"],
                scope=a["scope"],
                proof=a["proof"],
                packet_digest=packet.packet_digest,
            )
            return

        # --------------------------------------------------------------
        # First-class proof terms and trusted boundary attestations
        # --------------------------------------------------------------
        if kind == "proof":
            self._derive_proof(a)
            return

        if kind == "attest_origin":
            if a["proof"] in self.state.proofs:
                raise self._error(f"proof {a['proof']!r} already exists")
            packet = self._packet(a["packet"])
            agent = self._agent(a["agent"])
            if packet.status != "provisional":
                raise self._error("origin attestation requires a provisional neural packet")
            if agent.lineage != a["lineage"]:
                raise self._error("origin attestation lineage does not match active agent")
            proof = self._new_proof(
                name=a["proof"],
                kind="origin",
                subject=packet.name,
                agent=agent.name,
                source_agent=agent.name,
                source_lineage=agent.lineage,
                claims=("trusted_origin_attestation", "trusted_lineage_attestation"),
                packet=packet,
                trusted=True,
            )
            self.state.proofs[proof.name] = proof
            self._receipt("trusted_attestation", proof=asdict(proof))
            return

        if kind == "attest_relevance":
            if a["proof"] in self.state.proofs:
                raise self._error(f"proof {a['proof']!r} already exists")
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if packet.status != "provisional":
                raise self._error("relevance attestation requires a provisional neural packet")
            proof = self._new_proof(
                name=a["proof"],
                kind="relevance",
                subject=packet.name,
                agent=a["agent"],
                scope=a["scope"],
                claims=("trusted_task_relevance",),
                packet=packet,
                trusted=True,
            )
            self.state.proofs[proof.name] = proof
            self._receipt("trusted_attestation", proof=asdict(proof))
            return

        if kind == "admit":
            packet = self._packet(a["packet"])
            agent = self._agent(a["agent"])
            if packet.status != "provisional":
                raise self._error("only provisional neural packets can be admitted")
            supplied = [self._proof(name) for name in a["proofs"]]
            origin = next(
                (
                    proof
                    for proof in supplied
                    if proof.kind == "origin"
                    and proof.trusted
                    and proof.subject == packet.name
                    and proof.agent == agent.name
                ),
                None,
            )
            relevance = next(
                (
                    proof
                    for proof in supplied
                    if proof.kind == "relevance"
                    and proof.trusted
                    and proof.subject == packet.name
                    and proof.agent == agent.name
                ),
                None,
            )
            if origin is None or relevance is None:
                raise self._error("neural admission requires trusted origin and relevance proofs")
            if origin.subject_digest != packet.content_digest or relevance.subject_digest != packet.content_digest:
                raise self._error("neural admission proof refers to a different candidate content")
            packet.source_agent = origin.source_agent or agent.name
            packet.source_lineage = origin.source_lineage or agent.lineage
            packet.provenance = "inferred"
            packet.status = "admitted"
            packet.obligations.clear()
            packet.bound_to.add(agent.name)
            packet.quarantined_by.discard(agent.name)
            packet.refresh_digest()
            self._receipt(
                "neural_admission",
                agent=agent.name,
                origin_proof=origin.proof_digest,
                relevance_proof=relevance.proof_digest,
                packet=packet.canonical(include_digest=True),
            )
            return

        if kind == "reject_candidate":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if packet.status != "provisional":
                raise self._error("only provisional neural packets can be rejected")
            packet.status = "rejected"
            packet.obligations.clear()
            packet.quarantined_by.add(a["agent"])
            packet.refresh_digest()
            self._receipt(
                "neural_rejection",
                agent=a["agent"],
                packet=packet.canonical(include_digest=True),
            )
            return

        # --------------------------------------------------------------
        # Autobiographical memory, planning, execution, and feedback
        # --------------------------------------------------------------
        if kind == "write_memory":
            packet = self._packet(a["packet"])
            agent = self._agent(a["agent"])
            memory_class = a["memory_class"]
            proof_digest: str | None = None
            if memory_class not in PROVENANCE_CLASSES:
                raise self._error(f"unknown memory class {memory_class!r}")
            self._validate_memory_write(packet, agent, memory_class)
            if a["proof"] is not None:
                proof = self._verify_proof(
                    a["proof"],
                    expected_kind="ownership",
                    packet=packet,
                    agent=agent.name,
                    memory_class=memory_class,
                    consume=True,
                )
                proof_digest = proof.proof_digest
            record_payload = {
                "agent": agent.name,
                "packet_name": packet.name,
                "content": packet.content,
                "memory_class": memory_class,
                "source_agent": packet.source_agent,
                "source_lineage": packet.source_lineage,
                "packet_digest": packet.packet_digest,
                "proof_digest": proof_digest,
            }
            record = MemoryRecord(**record_payload, record_digest=digest(record_payload))
            self.state.memories.setdefault(agent.name, []).append(record)
            self._receipt("memory_write", record=asdict(record))
            return

        if kind == "plan":
            packet = self._packet(a["packet"])
            self._agent(a["agent"])
            if a["action"] in self.state.actions:
                raise self._error(f"action {a['action']!r} already exists")
            if a["effect"] not in EFFECTS:
                raise self._error(f"unknown effect {a['effect']!r}")
            self._validate_planning(packet, a["agent"], a["effect"])
            if a["proof"] is not None:
                proof = self._verify_proof(
                    a["proof"],
                    expected_kind="use",
                    packet=packet,
                    agent=a["agent"],
                    consume=True,
                )
                if proof.scope not in {"planning", a["effect"]}:
                    raise self._error(
                        f"proof {proof.name!r} is bound to scope {proof.scope!r}, "
                        f"not planning or effect {a['effect']!r}"
                    )
            action = Action(
                name=a["action"],
                agent=a["agent"],
                packet_name=packet.name,
                effect=a["effect"],
                expected=a["expected"],
                required_proof=a["proof"],
            )
            action.refresh_digest()
            self.state.actions[action.name] = action
            self._receipt("plan", action=asdict(action))
            return

        if kind == "execute":
            try:
                action = self.state.actions[a["action"]]
            except KeyError as exc:
                raise self._error(f"unknown action {a['action']!r}") from exc
            if action.agent != a["agent"]:
                raise self._error("action belongs to a different agent")
            if action.executed:
                raise self._error(f"action {action.name!r} has already been executed")
            if self._transaction_name is not None:
                raise self._error(
                    "execute is forbidden inside rollbackable transactions"
                )
            capability = self._capability(a["agent"], action.effect)
            prior_action_digest = action.action_digest
            capability_before = capability.canonical()
            action.capability_digest = capability.grant_digest
            action.executed = True
            action.refresh_digest()
            if capability.remaining_uses is not None:
                capability.remaining_uses -= 1
            self._receipt(
                "execute",
                action=asdict(action),
                prior_action_digest=prior_action_digest,
                capability_before=capability_before,
                capability_after=capability.canonical(),
            )
            return

        if kind == "feedback":
            try:
                action = self.state.actions[a["action"]]
            except KeyError as exc:
                raise self._error(f"unknown action {a['action']!r}") from exc
            if action.agent != a["agent"] or not action.executed:
                raise self._error("feedback requires an executed action owned by the agent")
            if action.observed is not None:
                raise self._error(f"action {action.name!r} already has feedback")
            prior_action_digest = action.action_digest
            action.observed = a["observed"]
            error = None if action.expected is None else action.observed - action.expected
            action.refresh_digest()
            self._receipt(
                "feedback",
                action=asdict(action),
                prior_action_digest=prior_action_digest,
                prediction_error=error,
            )
            return

        # --------------------------------------------------------------
        # Temporal contracts
        # --------------------------------------------------------------
        if kind == "contract":
            if a["template"] not in CONTRACT_TEMPLATES:
                raise self._error(f"unknown contract template {a['template']!r}")
            contract = TemporalContract(
                name=a["name"],
                template=a["template"],
                within=a["within"],
                declared_step=self.state.step,
            )
            self.state.contracts[contract.name] = contract
            self._receipt("contract_declare", contract=contract.canonical())
            return

        if kind == "check_contracts":
            self._check_contracts(final=False)
            self._receipt(
                "contract_check",
                contracts={k: v.canonical() for k, v in sorted(self.state.contracts.items())},
            )
            return

        if kind == "verify_receipts":
            report = verify_receipt_chain(self.audit_log)
            if not report["all_checks_pass"]:
                raise self._error("receipt chain verification failed")
            self._receipt("receipt_chain_verify", report=report)
            return

        # --------------------------------------------------------------
        # Transactions and rollback
        # --------------------------------------------------------------
        if kind == "begin_transaction":
            if self._transaction_name is not None:
                raise self._error("nested transactions are not supported")
            self._transaction_name = a["name"]
            self._transaction_checkpoint = copy.deepcopy(self.state)
            self._transaction_secrets_checkpoint = copy.deepcopy(self._secrets)
            self._transaction_checkpoint_digest = digest(
                self._transaction_projection()
            )
            self._transaction_begin_audit_index = len(self.audit_log)
            self._transaction_begin_step = self.state.step
            self._receipt(
                "transaction_begin",
                transaction=a["name"],
                begin_audit_index=self._transaction_begin_audit_index,
                checkpoint_digest=self._transaction_checkpoint_digest,
            )
            return

        if kind == "commit_transaction":
            if self._transaction_name != a["name"]:
                raise self._error(f"transaction {a['name']!r} is not active")
            self._receipt(
                "transaction_commit",
                transaction=a["name"],
                begin_audit_index=self._transaction_begin_audit_index,
                begin_step=self._transaction_begin_step,
                body_effect_span=(
                    (self._transaction_begin_audit_index or 0) + 1,
                    len(self.audit_log),
                ),
                final_state_digest=digest(self._transaction_projection()),
            )
            self._transaction_name = None
            self._transaction_checkpoint = None
            self._transaction_secrets_checkpoint = None
            self._transaction_checkpoint_digest = None
            self._transaction_begin_audit_index = None
            self._transaction_begin_step = None
            return

        if kind == "rollback_transaction":
            if self._transaction_name != a["name"]:
                raise self._error(f"transaction {a['name']!r} is not active")
            self._restore_transaction(
                reason="explicit rollback", automatic=False, failed_step=self.state.step
            )
            return

        # --------------------------------------------------------------
        # Session protocols
        # --------------------------------------------------------------
        if kind == "session":
            protocol = SessionProtocol(
                name=a["name"],
                participants=tuple(a["participants"]),
                initial_state=a["initial"],
            )
            self.state.sessions[protocol.name] = protocol
            self._receipt("session_declare", session=protocol.canonical())
            return

        if kind == "session_transition":
            protocol = self._session(a["session"])
            key = (a["source_state"], "communicate", a["sender"], a["receiver"])
            if key in protocol.transitions:
                raise self._error("duplicate session transition")
            protocol.transitions[key] = a["target_state"]
            protocol.verification = None
            self._receipt(
                "session_transition_declare",
                session=protocol.name,
                source_state=a["source_state"],
                event="communicate",
                sender=a["sender"],
                receiver=a["receiver"],
                target_state=a["target_state"],
            )
            return

        if kind == "session_terminal":
            protocol = self._session(a["session"])
            protocol.terminal_states.add(a["state"])
            protocol.verification = None
            self._receipt(
                "session_terminal_declare",
                session=protocol.name,
                state=a["state"],
            )
            return

        if kind == "verify_session":
            protocol = self._session(a["session"])
            report = verify_session_protocol(protocol)
            protocol.verification = asdict(report)
            self._receipt("session_verify", report=protocol.verification)
            if not report.all_checks_pass:
                details = []
                if report.reachable_deadlocks:
                    details.append(
                        "reachable deadlocks=" + ",".join(report.reachable_deadlocks)
                    )
                if report.terminal_with_outgoing:
                    details.append(
                        "terminal states with outgoing transitions="
                        + ",".join(report.terminal_with_outgoing)
                    )
                if report.states_without_terminal_path:
                    details.append(
                        "states without terminal path="
                        + ",".join(report.states_without_terminal_path)
                    )
                if not report.terminal_declared:
                    details.append("no terminal state declared")
                raise self._error(
                    "session verification failed"
                    + (": " + "; ".join(details) if details else "")
                )
            return

        if kind == "start_session":
            protocol = self._session(a["session"])
            if protocol.active:
                raise self._error(f"session {protocol.name!r} is already active")
            if protocol.terminal_states and not (
                protocol.verification
                and protocol.verification.get("all_checks_pass") is True
            ):
                raise self._error(
                    f"session {protocol.name!r} declares terminal states but has not "
                    "passed verify_session"
                )
            protocol.active = True
            protocol.current_state = protocol.initial_state
            protocol.history.append(
                {"step": self.state.step, "event": "start", "state": protocol.current_state}
            )
            self._receipt("session_start", session=protocol.canonical())
            return

        # --------------------------------------------------------------
        # Paired-trace noninterference carriers
        # --------------------------------------------------------------
        if kind == "secret":
            self._secrets[a["name"]] = a["value"]
            self.state.secret_digests[a["name"]] = digest(a["value"])
            self._receipt("secret_register", name=a["name"], value_digest=digest(a["value"]))
            return

        if kind == "metadata":
            value = a["value"] if a["secret"] is None else self._secrets[a["secret"]]
            payload = {
                "value": value,
                "source": a["source"],
                "step": self.state.step,
            }
            payload["digest"] = digest(payload)
            self.state.metadata[a["name"]] = payload
            self._receipt(
                "metadata_publish",
                name=a["name"],
                source=a["source"],
                from_secret=a["secret"] is not None,
                metadata_digest=payload["digest"],
            )
            return

        # --------------------------------------------------------------
        # Assertions and inspection
        # --------------------------------------------------------------
        if kind == "assert":
            self._execute_assert(a["body"])
            self.state.assertions += 1
            self._receipt(
                "assert_pass",
                assertion=a["body"],
                assertion_count=self.state.assertions,
            )
            return

        if kind == "show":
            self._event("show", snapshot=self.state.snapshot())
            self._receipt("show", semantic_digest=self.state.semantic_digest())
            return

        raise self._error(f"runtime does not recognize statement kind {kind!r}")

    # ------------------------------------------------------------------
    # Proof system
    # ------------------------------------------------------------------
    def _new_proof(
        self,
        *,
        name: str,
        kind: str,
        subject: str,
        agent: str | None = None,
        scope: str | None = None,
        memory_class: str | None = None,
        source_agent: str | None = None,
        source_lineage: str | None = None,
        premises: tuple[str, ...] = (),
        claims: tuple[str, ...] = (),
        packet: Packet | None = None,
        trusted: bool = False,
        resource_mode: str = "persistent",
    ) -> ProofTerm:
        if kind not in PROOF_KINDS:
            raise self._error(f"unknown proof kind {kind!r}")
        if resource_mode not in PROOF_RESOURCE_MODES:
            raise self._error(f"unknown proof resource mode {resource_mode!r}")
        remaining_uses = None if resource_mode == "persistent" else 1
        payload = {
            "name": name,
            "kind": kind,
            "subject": subject,
            "agent": agent,
            "scope": scope,
            "memory_class": memory_class,
            "source_agent": source_agent,
            "source_lineage": source_lineage,
            "premises": list(premises),
            "claims": list(claims),
            "subject_digest": None if packet is None else packet.content_digest,
            "state_digest": None if packet is None else packet.packet_digest,
            "created_step": self.state.step,
            "trusted": trusted,
            "resource_mode": resource_mode,
            "remaining_uses": remaining_uses,
            "consumed_step": None,
        }
        return ProofTerm(
            name=name,
            kind=kind,
            subject=subject,
            agent=agent,
            scope=scope,
            memory_class=memory_class,
            source_agent=source_agent,
            source_lineage=source_lineage,
            premises=tuple(premises),
            claims=tuple(claims),
            subject_digest=payload["subject_digest"],
            state_digest=payload["state_digest"],
            created_step=self.state.step,
            trusted=trusted,
            resource_mode=resource_mode,
            remaining_uses=remaining_uses,
            consumed_step=None,
            proof_digest=digest(payload),
        )

    def _derive_proof(self, args: dict[str, Any]) -> None:
        kind = args["proof_kind"]
        name = args["name"]
        if name in self.state.proofs:
            raise self._error(f"proof {name!r} already exists")
        resource_mode = args.get("resource_mode", "persistent")
        if name in self.state.proofs:
            raise self._error(f"proof {name!r} already exists")

        if kind == "capability":
            capability = self._capability(args["agent"], args["effect"])
            proof = self._new_proof(
                name=name,
                kind=kind,
                subject=args["effect"],
                agent=args["agent"],
                scope=args["effect"],
                claims=("capability_available", capability.grant_digest),
                resource_mode=resource_mode,
            )
        else:
            packet = self._packet(args["packet"])
            if kind == "access":
                if args["agent"] not in packet.accessible_to:
                    raise self._error("access proof premise is false")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    agent=args["agent"],
                    claims=("workspace_access",),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "origin":
                if (
                    packet.source_agent != args["source_agent"]
                    or packet.source_lineage != args["source_lineage"]
                ):
                    raise self._error("origin proof does not match packet provenance")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    source_agent=args["source_agent"],
                    source_lineage=args["source_lineage"],
                    claims=("origin_matches", "lineage_matches"),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "clear":
                if args["agent"] in packet.quarantined_by:
                    raise self._error("clear proof premise is false: packet is quarantined")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    agent=args["agent"],
                    claims=("not_quarantined",),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "endorsement":
                if args["agent"] not in packet.endorsed_by:
                    raise self._error("endorsement proof premise is false")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    agent=args["agent"],
                    claims=("epistemically_endorsed",),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "authorization":
                if args["scope"] not in packet.authorizations.get(args["agent"], set()):
                    raise self._error("authorization proof premise is false")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    agent=args["agent"],
                    scope=args["scope"],
                    claims=("use_authorized",),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "observation":
                agent = self._agent(args["agent"])
                if (
                    args["agent"] not in packet.observation_tokens
                    or packet.source_agent != agent.name
                    or packet.source_lineage != agent.lineage
                ):
                    raise self._error("observation proof premise is false")
                proof = self._new_proof(
                    name=name,
                    kind=kind,
                    subject=packet.name,
                    agent=agent.name,
                    source_agent=agent.name,
                    source_lineage=agent.lineage,
                    claims=("direct_observation_token",),
                    packet=packet,
                    resource_mode=resource_mode,
                )
            elif kind == "use":
                proof = self._derive_use_proof(args, packet)
            elif kind == "ownership":
                proof = self._derive_ownership_proof(args, packet)
            else:  # pragma: no cover - parser guards remaining kinds
                raise self._error(f"proof kind {kind!r} requires a trusted attestation")

        self.state.proofs[name] = proof
        self._receipt("proof_construct", proof=asdict(proof))

    def _derive_use_proof(self, args: dict[str, Any], packet: Packet) -> ProofTerm:
        agent = args["agent"]
        scope = args["scope"]
        premises = tuple(args.get("premises", ()))
        terms = [self._proof(name) for name in premises]
        for term in terms:
            if not self._proof_semantically_valid(term):
                raise self._error(f"premise proof {term.name!r} is no longer valid")
            if term.subject != packet.name or term.subject_digest != packet.content_digest:
                raise self._error("use-proof premises refer to a different packet")
        required = {"access", "origin", "clear", "endorsement", "authorization"}
        present = {term.kind for term in terms}
        missing = sorted(required - present)
        if missing:
            raise self._error(f"use proof is missing premises: {', '.join(missing)}")
        if len(terms) != len(required) or present != required:
            raise self._error("use proof requires each primitive premise exactly once")
        by_kind = {term.kind: term for term in terms}
        for premise_kind in ("access", "clear", "endorsement", "authorization"):
            if by_kind[premise_kind].agent != agent:
                raise self._error(
                    f"use-proof {premise_kind} premise is bound to a different agent"
                )
        authorization = by_kind["authorization"]
        if authorization.scope not in {scope, "planning"}:
            raise self._error(
                "use-proof authorization premise is bound to a different scope"
            )
        if agent not in packet.accessible_to or agent not in packet.bound_to:
            raise self._error("use proof requires accessible, bound content")
        if agent in packet.quarantined_by or agent not in packet.endorsed_by:
            raise self._error("use proof requires clear, endorsed content")
        scopes = packet.authorizations.get(agent, set())
        if scope not in scopes and "planning" not in scopes:
            raise self._error("use proof scope is not authorized")
        proof = self._new_proof(
            name=args["name"],
            kind="use",
            subject=packet.name,
            agent=agent,
            scope=scope,
            premises=premises,
            claims=("workspace_access", "origin_valid", "not_quarantined", "endorsed", "authorized"),
            packet=packet,
            resource_mode=args.get("resource_mode", "persistent"),
        )
        for term in terms:
            if term.resource_mode in {"affine", "linear"}:
                self._consume_proof(term, purpose=f"premise:{proof.name}")
        return proof

    def _derive_ownership_proof(self, args: dict[str, Any], packet: Packet) -> ProofTerm:
        agent = args["agent"]
        memory_class = args["memory_class"]
        premises = tuple(args.get("premises", ()))
        if memory_class not in PROVENANCE_CLASSES:
            raise self._error(f"unknown memory class {memory_class!r}")
        terms = [self._proof(name) for name in premises]
        for term in terms:
            if not self._proof_semantically_valid(term):
                raise self._error(f"premise proof {term.name!r} is no longer valid")
            if term.subject != packet.name or term.subject_digest != packet.content_digest:
                raise self._error("ownership-proof premises refer to a different packet")
        required = {"access", "origin", "clear"}
        if memory_class == "observed":
            required.add("observation")
        present = {term.kind for term in terms}
        missing = sorted(required - present)
        if missing:
            raise self._error(f"ownership proof is missing premises: {', '.join(missing)}")
        if len(terms) != len(required) or present != required:
            raise self._error(
                "ownership proof requires each primitive premise exactly once"
            )
        for term in terms:
            if term.kind in {"access", "clear", "observation"} and term.agent != agent:
                raise self._error(
                    f"ownership-proof {term.kind} premise is bound to a different agent"
                )
        self._validate_memory_write(packet, self._agent(agent), memory_class)
        proof = self._new_proof(
            name=args["name"],
            kind="ownership",
            subject=packet.name,
            agent=agent,
            memory_class=memory_class,
            premises=premises,
            claims=("autobiographical_write_authorized",),
            packet=packet,
            resource_mode=args.get("resource_mode", "persistent"),
        )
        for term in terms:
            if term.resource_mode in {"affine", "linear"}:
                self._consume_proof(term, purpose=f"premise:{proof.name}")
        return proof

    def _proof_semantically_valid(
        self, proof: ProofTerm, *, require_available: bool = True
    ) -> bool:
        if require_available and proof.resource_mode in {"affine", "linear"}:
            if proof.remaining_uses is None or proof.remaining_uses <= 0:
                return False
        if proof.kind == "capability":
            try:
                capability = self._capability(proof.agent or "", proof.scope or "")
            except OSLError:
                return False
            return tuple(proof.claims) == (
                "capability_available",
                capability.grant_digest,
            )
        try:
            packet = self._packet(proof.subject)
        except OSLError:
            return False
        if proof.subject_digest != packet.content_digest:
            return False
        agent = proof.agent
        if proof.kind == "access":
            return agent is not None and agent in packet.accessible_to
        if proof.kind == "origin":
            if proof.trusted and packet.status == "provisional":
                return True
            return (
                packet.source_agent == proof.source_agent
                and packet.source_lineage == proof.source_lineage
            )
        if proof.kind == "clear":
            return agent is not None and agent not in packet.quarantined_by
        if proof.kind == "endorsement":
            return agent is not None and agent in packet.endorsed_by
        if proof.kind == "authorization":
            return (
                agent is not None
                and proof.scope in packet.authorizations.get(agent, set())
            )
        if proof.kind == "observation":
            if agent is None:
                return False
            current = self.state.agents.get(agent)
            return bool(
                current
                and agent in packet.observation_tokens
                and packet.source_agent == agent
                and packet.source_lineage == current.lineage
            )
        if proof.kind == "relevance":
            return proof.trusted and packet.status == "provisional"
        if proof.kind == "use":
            if proof.state_digest != packet.packet_digest or agent is None:
                return False
            return bool(
                agent in packet.accessible_to
                and agent in packet.bound_to
                and agent not in packet.quarantined_by
                and agent in packet.endorsed_by
                and (
                    proof.scope in packet.authorizations.get(agent, set())
                    or "planning" in packet.authorizations.get(agent, set())
                )
                and all(
                    self._proof_semantically_valid(
                        self._proof(name), require_available=False
                    )
                    for name in proof.premises
                )
            )
        if proof.kind == "ownership":
            if proof.state_digest != packet.packet_digest or agent is None:
                return False
            try:
                self._validate_memory_write(packet, self._agent(agent), proof.memory_class or "")
            except OSLError:
                return False
            return all(
                self._proof_semantically_valid(
                    self._proof(name), require_available=False
                )
                for name in proof.premises
            )
        return False

    def _verify_proof(
        self,
        name: str,
        *,
        expected_kind: str | None = None,
        packet: Packet | None = None,
        agent: str | None = None,
        scope: str | None = None,
        memory_class: str | None = None,
        consume: bool = False,
    ) -> ProofTerm:
        proof = self._proof(name)
        if expected_kind is not None and proof.kind != expected_kind:
            raise self._error(
                f"proof {name!r} has kind {proof.kind!r}, expected {expected_kind!r}"
            )
        if packet is not None and (
            proof.subject != packet.name or proof.subject_digest != packet.content_digest
        ):
            raise self._error(f"proof {name!r} is bound to different content")
        if agent is not None and proof.agent not in {None, agent}:
            raise self._error(f"proof {name!r} is bound to a different agent")
        if scope is not None and proof.scope not in {None, scope}:
            raise self._error(f"proof {name!r} is bound to scope {proof.scope!r}")
        if memory_class is not None and proof.memory_class != memory_class:
            raise self._error(f"proof {name!r} is bound to a different memory class")
        if not self._proof_semantically_valid(proof):
            raise self._error(f"proof {name!r} is stale or semantically invalid")
        if consume:
            self._consume_proof(proof, purpose=expected_kind or "verification")
        return proof

    def _consume_proof(self, proof: ProofTerm, *, purpose: str) -> None:
        if proof.resource_mode == "persistent":
            self._receipt(
                "proof_use",
                proof=proof.name,
                proof_digest=proof.proof_digest,
                resource_mode=proof.resource_mode,
                purpose=purpose,
                remaining_uses=None,
            )
            return
        if proof.remaining_uses is None or proof.remaining_uses <= 0:
            raise self._error(f"proof {proof.name!r} has already been consumed")
        proof.remaining_uses -= 1
        if proof.remaining_uses == 0:
            proof.consumed_step = self.state.step
        self._receipt(
            "proof_consume",
            proof=proof.name,
            proof_digest=proof.proof_digest,
            resource_mode=proof.resource_mode,
            purpose=purpose,
            remaining_uses=proof.remaining_uses,
            consumed_step=proof.consumed_step,
        )

    def _check_linear_proof_obligations(self) -> None:
        unused = sorted(
            proof.name
            for proof in self.state.proofs.values()
            if proof.resource_mode == "linear"
            and proof.remaining_uses is not None
            and proof.remaining_uses > 0
        )
        if unused:
            raise self._error(
                "linear proofs must be consumed exactly once: " + ", ".join(unused)
            )

    # ------------------------------------------------------------------
    # Memory and planning policy
    # ------------------------------------------------------------------
    def _validate_memory_write(
        self, packet: Packet, agent: Agent, memory_class: str
    ) -> None:
        if agent.name in packet.quarantined_by:
            raise self._error("quarantined content cannot be written to ordinary memory")
        if agent.name not in packet.accessible_to or agent.name not in packet.bound_to:
            raise self._error("memory write requires accessible, bound content")
        if memory_class not in MEMORY_COMPATIBILITY.get(packet.provenance, set()):
            raise self._error(
                f"packet provenance {packet.provenance!r} cannot be written as "
                f"{memory_class!r}"
            )
        if memory_class == "observed":
            if agent.name not in packet.observation_tokens:
                raise self._error(
                    "direct observed memory requires a nonforgeable observation token"
                )
            if packet.source_agent != agent.name or packet.source_lineage != agent.lineage:
                raise self._error("observation token does not match active agent lineage")
        if packet.status not in {"grounded", "admitted"}:
            raise self._error(
                f"packet status {packet.status!r} is not eligible for memory"
            )

    def _validate_planning(self, packet: Packet, agent_name: str, effect: str) -> None:
        if agent_name not in packet.accessible_to or agent_name not in packet.bound_to:
            raise self._error("planning requires accessible, self-bound content")
        if agent_name in packet.quarantined_by:
            raise self._error("planning cannot use quarantined content")
        if agent_name not in packet.endorsed_by:
            raise self._error("planning requires epistemic endorsement")
        scopes = packet.authorizations.get(agent_name, set())
        if "planning" not in scopes and effect not in scopes:
            raise self._error("planning requires planning or effect-specific authorization")
        if packet.status not in {"grounded", "admitted"}:
            raise self._error(
                f"packet status {packet.status!r} is not eligible for planning"
            )

    # ------------------------------------------------------------------
    # Temporal contracts
    # ------------------------------------------------------------------
    def _monitor_contract_event(self, kind: str, receipt: dict[str, Any]) -> None:
        for contract in self.state.contracts.values():
            if contract.template != "feedback_deadline":
                continue
            if kind == "execute":
                action = receipt.get("action", {})
                action_name = action.get("name")
                if action_name is not None:
                    contract.pending[action_name] = self.state.step + int(contract.within or 0)
            elif kind == "feedback":
                action = receipt.get("action", {})
                action_name = action.get("name")
                if action_name is not None:
                    contract.pending.pop(action_name, None)

    def _record_contract_violation(self, contract: TemporalContract, message: str) -> None:
        if message not in contract.violations:
            contract.violations.append(message)
        raise self._error(f"contract {contract.name!r} violated: {message}")

    def _check_contracts(self, *, final: bool) -> None:
        for contract in self.state.contracts.values():
            if contract.template == "no_foreign_observed":
                for agent_name, records in self.state.memories.items():
                    agent = self.state.agents[agent_name]
                    for record in records:
                        if record.memory_class == "observed" and (
                            record.source_agent != agent_name
                            or record.source_lineage != agent.lineage
                        ):
                            self._record_contract_violation(
                                contract,
                                f"foreign record {record.packet_name!r} written as observed by {agent_name}",
                            )
            elif contract.template == "no_simulated_observed":
                for agent_name, records in self.state.memories.items():
                    for record in records:
                        packet = self.state.packets.get(record.packet_name)
                        if (
                            record.memory_class == "observed"
                            and packet is not None
                            and (packet.simulated or packet.provenance == "simulated")
                        ):
                            self._record_contract_violation(
                                contract,
                                f"simulated packet {record.packet_name!r} written as observed by {agent_name}",
                            )
            elif contract.template == "quarantine_blocks_endorsement":
                for packet in self.state.packets.values():
                    overlap = packet.quarantined_by & packet.endorsed_by
                    if overlap:
                        self._record_contract_violation(
                            contract,
                            f"packet {packet.name!r} is both quarantined and endorsed by {sorted(overlap)}",
                        )
            elif contract.template == "capability_confinement":
                for action in self.state.actions.values():
                    if action.executed and action.capability_digest is None:
                        self._record_contract_violation(
                            contract,
                            f"executed action {action.name!r} lacks a capability receipt",
                        )
            elif contract.template == "feedback_deadline":
                for action_name, due in sorted(contract.pending.items()):
                    if final or self.state.step > due:
                        self._record_contract_violation(
                            contract,
                            f"action {action_name!r} lacks feedback by step {due}",
                        )

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def _restore_transaction(
        self, *, reason: str, automatic: bool, failed_step: int
    ) -> None:
        if (
            self._transaction_name is None
            or self._transaction_checkpoint is None
            or self._transaction_secrets_checkpoint is None
            or self._transaction_checkpoint_digest is None
            or self._transaction_begin_audit_index is None
        ):
            raise self._error("no transaction is active")
        name = self._transaction_name
        checkpoint = self._transaction_checkpoint
        checkpoint_digest = self._transaction_checkpoint_digest
        begin_audit_index = self._transaction_begin_audit_index
        pre_restore_digest = digest(self._transaction_projection())
        discarded_chain_tip = (
            self.audit_log[-1]["digest"] if self.audit_log else "0" * 64
        )
        discarded_receipt_count = max(0, len(self.audit_log) - begin_audit_index - 1)
        evidence_events = copy.deepcopy(self.state.events)
        self.state = copy.deepcopy(checkpoint)
        self.state.receipts = copy.deepcopy(self.audit_log)
        self.state.events = evidence_events
        self.state.step = failed_step
        self._secrets = copy.deepcopy(self._transaction_secrets_checkpoint)
        self._transaction_name = None
        self._transaction_checkpoint = None
        self._transaction_secrets_checkpoint = None
        self._transaction_checkpoint_digest = None
        self._transaction_begin_audit_index = None
        begin_step = self._transaction_begin_step
        self._transaction_begin_step = None
        restored_digest = digest(self._transaction_projection())
        self._receipt(
            "transaction_rollback",
            transaction=name,
            automatic=automatic,
            reason=reason,
            begin_audit_index=begin_audit_index,
            begin_step=begin_step,
            checkpoint_digest=checkpoint_digest,
            body_effect_span=(begin_audit_index + 1, len(self.audit_log)),
            pre_restore_digest=pre_restore_digest,
            discarded_chain_tip=discarded_chain_tip,
            discarded_receipt_count=discarded_receipt_count,
            restored_state_digest=restored_digest,
        )

    # ------------------------------------------------------------------
    # Session protocols
    # ------------------------------------------------------------------
    def _advance_session(
        self, session_name: str, event: str, sender: str, receiver: str
    ) -> None:
        protocol = self._session(session_name)
        if not protocol.active or protocol.current_state is None:
            raise self._error(f"session {session_name!r} is not active")
        if sender not in protocol.participants or receiver not in protocol.participants:
            raise self._error("session event uses a nonparticipant")
        key = (protocol.current_state, event, sender, receiver)
        target = protocol.transitions.get(key)
        if target is None:
            raise self._error(
                f"session {session_name!r} has no transition from "
                f"{protocol.current_state!r} for {event} {sender}->{receiver}"
            )
        before = protocol.current_state
        protocol.current_state = target
        if target in protocol.terminal_states:
            protocol.active = False
        protocol.history.append(
            {
                "step": self.state.step,
                "event": event,
                "sender": sender,
                "receiver": receiver,
                "from": before,
                "to": target,
                "terminal": target in protocol.terminal_states,
            }
        )
        self._receipt(
            "session_advance",
            session=session_name,
            event=event,
            sender=sender,
            receiver=receiver,
            source_state=before,
            target_state=target,
        )

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------
    def _execute_assert(self, body: str) -> None:
        import re

        IDENT = r"[A-Za-z_][\w-]*"
        if match := re.fullmatch(rf"packet\s+({IDENT})\s+provenance\s+({IDENT})", body):
            actual = self._packet(match.group(1)).provenance
            if actual != match.group(2):
                raise self._error(
                    f"expected provenance {match.group(2)!r}, got {actual!r}"
                )
            return

        if match := re.fullmatch(rf"packet\s+({IDENT})\s+status\s+({IDENT})", body):
            actual = self._packet(match.group(1)).status
            if actual != match.group(2):
                raise self._error(f"expected status {match.group(2)!r}, got {actual!r}")
            return

        if match := re.fullmatch(
            rf"packet\s+({IDENT})\s+accessible_to\s+({IDENT})\s+(true|false)", body
        ):
            actual = match.group(2) in self._packet(match.group(1)).accessible_to
            if actual != (match.group(3) == "true"):
                raise self._error("packet access assertion failed")
            return

        if match := re.fullmatch(
            rf"packet\s+({IDENT})\s+quarantined_by\s+({IDENT})\s+(true|false)", body
        ):
            actual = match.group(2) in self._packet(match.group(1)).quarantined_by
            if actual != (match.group(3) == "true"):
                raise self._error("packet quarantine assertion failed")
            return

        if match := re.fullmatch(
            rf"packet\s+({IDENT})\s+obligation\s+({IDENT})\s+(true|false)", body
        ):
            actual = match.group(2) in self._packet(match.group(1)).obligations
            if actual != (match.group(3) == "true"):
                raise self._error("packet obligation assertion failed")
            return

        if match := re.fullmatch(
            rf"memory\s+({IDENT})\s+contains\s+({IDENT})\s+as\s+({IDENT})\s+(true|false)",
            body,
        ):
            records = self.state.memories.get(match.group(1), [])
            actual = any(
                record.packet_name == match.group(2)
                and record.memory_class == match.group(3)
                for record in records
            )
            if actual != (match.group(4) == "true"):
                raise self._error("memory assertion failed")
            return

        if match := re.fullmatch(rf"action\s+({IDENT})\s+executed\s+(true|false)", body):
            action = self.state.actions.get(match.group(1))
            actual = bool(action is not None and action.executed)
            if actual != (match.group(2) == "true"):
                raise self._error("action execution assertion failed")
            return

        if match := re.fullmatch(rf"proof\s+({IDENT})\s+valid\s+(true|false)", body):
            proof = self._proof(match.group(1))
            actual = self._proof_semantically_valid(proof)
            if actual != (match.group(2) == "true"):
                raise self._error("proof validity assertion failed")
            return

        if match := re.fullmatch(rf"session\s+({IDENT})\s+state\s+({IDENT})", body):
            actual = self._session(match.group(1)).current_state
            if actual != match.group(2):
                raise self._error(
                    f"session assertion failed: expected {match.group(2)!r}, got {actual!r}"
                )
            return

        if match := re.fullmatch(
            rf"contract\s+({IDENT})\s+violations\s+(\d+)", body
        ):
            actual = len(self.state.contracts[match.group(1)].violations)
            if actual != int(match.group(2)):
                raise self._error(
                    f"contract assertion failed: expected {match.group(2)}, got {actual}"
                )
            return

        if match := re.fullmatch(
            rf"capability\s+({IDENT})\s+effect\s+({IDENT})\s+remaining\s+(\d+|unlimited)",
            body,
        ):
            try:
                cap = self.state.capabilities[match.group(1)][match.group(2)]
            except KeyError as exc:
                raise self._error("capability assertion refers to an unknown capability") from exc
            expected = None if match.group(3) == "unlimited" else int(match.group(3))
            if cap.remaining_uses != expected:
                raise self._error(
                    f"capability assertion failed: expected {expected}, got {cap.remaining_uses}"
                )
            return

        if match := re.fullmatch(
            rf"metadata\s+({IDENT})\s+equals\s+(.+)", body
        ):
            expected_text = match.group(2).strip()
            try:
                expected = json.loads(expected_text)
            except json.JSONDecodeError:
                expected = ast.literal_eval(expected_text)
            actual = self.state.metadata.get(match.group(1), {}).get("value")
            if actual != expected:
                raise self._error(f"metadata assertion failed: {actual!r} != {expected!r}")
            return

        if match := re.fullmatch(
            rf"vector\s+({IDENT})\s+approx\s+(.+?)\s+tolerance\s+([-+0-9.eE]+)",
            body,
        ):
            vector = self._vector(match.group(1))
            try:
                expected = np.asarray(json.loads(match.group(2)), dtype=float)
            except json.JSONDecodeError:
                expected = np.asarray(ast.literal_eval(match.group(2)), dtype=float)
            tolerance = float(match.group(3))
            if vector.value.shape != expected.shape or not np.allclose(
                vector.value, expected, atol=tolerance, rtol=0.0
            ):
                raise self._error(
                    f"vector assertion failed: {vector.value.tolist()} != {expected.tolist()}"
                )
            return

        if match := re.fullmatch(
            rf"lineage\s+({IDENT})\s+parent\s+({IDENT}|none)", body
        ):
            actual = self.state.lineage_parents.get(match.group(1))
            expected = None if match.group(2) == "none" else match.group(2)
            if actual != expected:
                raise self._error(
                    f"lineage assertion failed: expected {expected!r}, got {actual!r}"
                )
            return

        raise self._error(f"unrecognized assertion: {body}")


def run_program(path: Path) -> dict[str, Any]:
    runtime = OSLRuntime()
    try:
        state = runtime.run_file(path)
    except (OSLError, OSLStaticError) as exc:
        return {
            "file": str(path),
            "ok": False,
            "error": str(exc),
            "state": runtime.state.snapshot(),
            "public": runtime.state.public_projection(),
            "audit": {
                "receipt_count": len(runtime.audit_log),
                "head_digest": (
                    None if not runtime.audit_log else runtime.audit_log[-1]["digest"]
                ),
                "receipts": runtime.audit_log,
            },
        }
    return {
        "file": str(path),
        "ok": True,
        "error": None,
        "state": state.snapshot(),
        "public": state.public_projection(),
        "audit": {
            "receipt_count": len(runtime.audit_log),
            "head_digest": (
                None if not runtime.audit_log else runtime.audit_log[-1]["digest"]
            ),
            "receipts": runtime.audit_log,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute an OSL-Core 0.4 program")
    parser.add_argument("program", type=Path)
    parser.add_argument("--json", action="store_true", help="print canonical JSON result")
    parser.add_argument(
        "--public", action="store_true", help="print only the public projection"
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = run_program(args.program)
    if args.public:
        print(json.dumps(result["public"], indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        state = result["state"]
        print(
            f"OSL_CORE_PASS version=0.4 module={state['module']} "
            f"agents={len(state['agents'])} packets={len(state['packets'])} "
            f"proofs={len(state['proofs'])} "
            f"memories={sum(len(v) for v in state['memories'].values())} "
            f"actions={len(state['actions'])} contracts={len(state['contracts'])} "
            f"sessions={len(state['sessions'])} assertions={state['assertions']} "
            f"digest={state['snapshot_digest']}"
        )
    else:
        print(f"OSL_CORE_REJECT {result['error']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
