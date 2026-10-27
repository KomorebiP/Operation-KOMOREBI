"""Data model for OSL-Core 0.5.

The model is deliberately finite and JSON-canonical.  It separates stable
content identity from mutable packet state, makes proof terms first-class, and
exposes temporal contracts, session protocols, bounded capabilities, and
provisional neural-boundary packets as explicit runtime objects.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

import numpy as np


PROVENANCE_CLASSES = {
    "observed",
    "inferred",
    "recalled",
    "simulated",
    "communicated",
    "injected",
    "foreign",
    "reconstructed",
    "conflicted",
    "unresolved",
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

PROOF_RESOURCE_MODES = {"persistent", "affine", "linear"}

CONTRACT_TEMPLATES = {
    "no_foreign_observed",
    "no_simulated_observed",
    "quarantine_blocks_endorsement",
    "capability_confinement",
    "feedback_deadline",
}


class OSLError(RuntimeError):
    """Raised when an OSL program violates syntax or semantic policy."""


class OSLStaticError(OSLError):
    """Raised when a program fails the pre-execution static pass."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _round(value: float) -> float:
    return round(float(value), 12)


@dataclass(frozen=True)
class Statement:
    kind: str
    args: dict[str, Any]
    line_number: int
    source: str


@dataclass(frozen=True)
class StaticReport:
    ok: bool
    statement_count: int
    symbol_counts: dict[str, int]
    warnings: tuple[str, ...]
    report_digest: str


@dataclass(frozen=True)
class Agent:
    name: str
    lineage: str


@dataclass(frozen=True)
class Space:
    name: str
    dim: int


@dataclass
class Operator:
    name: str
    source: str
    target: str
    kind: str
    matrix: np.ndarray

    def canonical(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "matrix": self.matrix.tolist(),
        }


@dataclass
class VectorValue:
    name: str
    space: str
    value: np.ndarray

    def canonical(self) -> dict[str, Any]:
        return {"name": self.name, "space": self.space, "value": self.value.tolist()}


@dataclass
class Capability:
    effect: str
    initial_uses: int | None = None
    remaining_uses: int | None = None
    expires_at: int | None = None
    source: str = "grant"
    grant_index: int = 0
    issued_step: int = 0
    grant_digest: str = ""

    def canonical(self) -> dict[str, Any]:
        return {
            "effect": self.effect,
            "initial_uses": self.initial_uses,
            "remaining_uses": self.remaining_uses,
            "expires_at": self.expires_at,
            "source": self.source,
            "grant_index": self.grant_index,
            "issued_step": self.issued_step,
            "grant_digest": self.grant_digest,
        }

    def refresh_digest(self, *, agent: str) -> None:
        self.grant_digest = digest(
            {
                "agent": agent,
                "effect": self.effect,
                "initial_uses": self.initial_uses,
                "expires_at": self.expires_at,
                "source": self.source,
                "grant_index": self.grant_index,
                "issued_step": self.issued_step,
            }
        )


@dataclass
class Packet:
    name: str
    content: str
    source_agent: str
    source_lineage: str
    provenance: str
    confidence: float
    accessible_to: set[str] = field(default_factory=set)
    bound_to: set[str] = field(default_factory=set)
    quarantined_by: set[str] = field(default_factory=set)
    endorsed_by: set[str] = field(default_factory=set)
    authorizations: dict[str, set[str]] = field(default_factory=dict)
    observation_tokens: set[str] = field(default_factory=set)
    simulated: bool = False
    parent_digest: str | None = None
    status: str = "grounded"
    latent_source: str | None = None
    obligations: set[str] = field(default_factory=set)
    support: float | None = None
    refutation: float = 0.0
    unresolved: float | None = None
    content_digest: str = ""
    packet_digest: str = ""

    def canonical_content(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "content": self.content,
            "source_agent": self.source_agent,
            "source_lineage": self.source_lineage,
            "provenance": self.provenance,
            "confidence": _round(self.confidence),
            "simulated": bool(self.simulated),
            "parent_digest": self.parent_digest,
            "latent_source": self.latent_source,
        }

    def canonical(self, include_digest: bool = False) -> dict[str, Any]:
        payload = {
            **self.canonical_content(),
            "accessible_to": sorted(self.accessible_to),
            "bound_to": sorted(self.bound_to),
            "quarantined_by": sorted(self.quarantined_by),
            "endorsed_by": sorted(self.endorsed_by),
            "authorizations": {
                agent: sorted(scopes) for agent, scopes in sorted(self.authorizations.items())
            },
            "observation_tokens": sorted(self.observation_tokens),
            "status": self.status,
            "obligations": sorted(self.obligations),
            "support": _round(self.confidence if self.support is None else self.support),
            "refutation": _round(self.refutation),
            "unresolved": _round(
                max(0.0, 1.0 - self.confidence)
                if self.unresolved is None
                else self.unresolved
            ),
            "content_digest": self.content_digest,
        }
        if include_digest:
            payload["packet_digest"] = self.packet_digest
        return payload

    def refresh_digest(self) -> None:
        self.content_digest = digest(self.canonical_content())
        self.packet_digest = digest(self.canonical(include_digest=False))


@dataclass
class ProofTerm:
    name: str
    kind: str
    subject: str
    agent: str | None
    scope: str | None
    memory_class: str | None
    source_agent: str | None
    source_lineage: str | None
    premises: tuple[str, ...]
    claims: tuple[str, ...]
    subject_digest: str | None
    state_digest: str | None
    created_step: int
    trusted: bool
    resource_mode: str
    remaining_uses: int | None
    consumed_step: int | None
    proof_digest: str

    def construction_payload(self) -> dict[str, Any]:
        initial_uses = None if self.resource_mode == "persistent" else 1
        return {
            "name": self.name,
            "kind": self.kind,
            "subject": self.subject,
            "agent": self.agent,
            "scope": self.scope,
            "memory_class": self.memory_class,
            "source_agent": self.source_agent,
            "source_lineage": self.source_lineage,
            "premises": list(self.premises),
            "claims": list(self.claims),
            "subject_digest": self.subject_digest,
            "state_digest": self.state_digest,
            "created_step": self.created_step,
            "trusted": self.trusted,
            "resource_mode": self.resource_mode,
            "remaining_uses": initial_uses,
            "consumed_step": None,
        }

    def construction_digest_valid(self) -> bool:
        return self.proof_digest == digest(self.construction_payload())

    def available(self) -> bool:
        return self.resource_mode == "persistent" or bool(
            self.remaining_uses is not None and self.remaining_uses > 0
        )

    def canonical(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryRecord:
    agent: str
    packet_name: str
    content: str
    memory_class: str
    source_agent: str
    source_lineage: str
    packet_digest: str
    proof_digest: str | None
    record_digest: str


@dataclass
class Action:
    name: str
    agent: str
    packet_name: str
    effect: str
    expected: float | None = None
    required_proof: str | None = None
    executed: bool = False
    observed: float | None = None
    capability_digest: str | None = None
    action_digest: str = ""

    def refresh_digest(self) -> None:
        self.action_digest = digest(
            {
                "name": self.name,
                "agent": self.agent,
                "packet_name": self.packet_name,
                "effect": self.effect,
                "expected": self.expected,
                "required_proof": self.required_proof,
                "executed": self.executed,
                "observed": self.observed,
                "capability_digest": self.capability_digest,
            }
        )


@dataclass
class TemporalContract:
    name: str
    template: str
    within: int | None = None
    pending: dict[str, int] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    declared_step: int = 0

    def canonical(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "template": self.template,
            "within": self.within,
            "pending": dict(sorted(self.pending.items())),
            "violations": list(self.violations),
            "declared_step": self.declared_step,
        }


@dataclass
class SessionProtocol:
    name: str
    participants: tuple[str, ...]
    initial_state: str
    current_state: str | None = None
    active: bool = False
    transitions: dict[tuple[str, str, str, str], str] = field(default_factory=dict)
    terminal_states: set[str] = field(default_factory=set)
    verification: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def canonical(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "participants": list(self.participants),
            "initial_state": self.initial_state,
            "current_state": self.current_state,
            "active": self.active,
            "terminal_states": sorted(self.terminal_states),
            "verification": self.verification,
            "transitions": [
                {
                    "from": key[0],
                    "event": key[1],
                    "sender": key[2],
                    "receiver": key[3],
                    "to": target,
                }
                for key, target in sorted(self.transitions.items())
            ],
            "history": list(self.history),
        }


@dataclass
class RuntimeState:
    module: str | None = None
    agents: dict[str, Agent] = field(default_factory=dict)
    lineage_parents: dict[str, str | None] = field(default_factory=dict)
    spaces: dict[str, Space] = field(default_factory=dict)
    operators: dict[str, Operator] = field(default_factory=dict)
    vectors: dict[str, VectorValue] = field(default_factory=dict)
    packets: dict[str, Packet] = field(default_factory=dict)
    proofs: dict[str, ProofTerm] = field(default_factory=dict)
    memories: dict[str, list[MemoryRecord]] = field(default_factory=dict)
    actions: dict[str, Action] = field(default_factory=dict)
    capabilities: dict[str, dict[str, Capability]] = field(default_factory=dict)
    contracts: dict[str, TemporalContract] = field(default_factory=dict)
    sessions: dict[str, SessionProtocol] = field(default_factory=dict)
    metadata: dict[str, dict[str, Any]] = field(default_factory=dict)
    secret_digests: dict[str, str] = field(default_factory=dict)
    receipts: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    static_report: dict[str, Any] | None = None
    assertions: int = 0
    step: int = 0

    def semantic_snapshot(self) -> dict[str, Any]:
        """Return the receipt-independent operational state.

        This projection intentionally excludes receipts, events, and the static
        report.  It is used to bind each source statement to the exact semantic
        state transition it caused without creating a circular dependency on the
        receipt log itself.
        """

        payload = {
            "module": self.module,
            "agents": {k: asdict(v) for k, v in sorted(self.agents.items())},
            "lineage_parents": dict(sorted(self.lineage_parents.items())),
            "spaces": {k: asdict(v) for k, v in sorted(self.spaces.items())},
            "operators": {k: v.canonical() for k, v in sorted(self.operators.items())},
            "vectors": {k: v.canonical() for k, v in sorted(self.vectors.items())},
            "packets": {
                k: v.canonical(include_digest=True) for k, v in sorted(self.packets.items())
            },
            "proofs": {k: asdict(v) for k, v in sorted(self.proofs.items())},
            "memories": {
                k: [asdict(record) for record in records]
                for k, records in sorted(self.memories.items())
            },
            "actions": {k: asdict(v) for k, v in sorted(self.actions.items())},
            "capabilities": {
                agent: {effect: cap.canonical() for effect, cap in sorted(caps.items())}
                for agent, caps in sorted(self.capabilities.items())
            },
            "contracts": {k: v.canonical() for k, v in sorted(self.contracts.items())},
            "sessions": {k: v.canonical() for k, v in sorted(self.sessions.items())},
            # Receipt-facing semantic state commits to metadata without
            # disclosing its raw value.  The full snapshot below retains the
            # value for local execution and independently verifies its digest.
            "metadata": {
                k: {
                    "source": v.get("source"),
                    "step": v.get("step"),
                    "digest": v.get("digest"),
                }
                for k, v in sorted(self.metadata.items())
            },
            "secret_digests": dict(sorted(self.secret_digests.items())),
            "assertions": self.assertions,
            "step": self.step,
        }
        payload["semantic_digest"] = digest(payload)
        return payload

    def semantic_digest(self) -> str:
        return str(self.semantic_snapshot()["semantic_digest"])

    def snapshot(self) -> dict[str, Any]:
        payload = {
            "module": self.module,
            "agents": {k: asdict(v) for k, v in sorted(self.agents.items())},
            "lineage_parents": dict(sorted(self.lineage_parents.items())),
            "spaces": {k: asdict(v) for k, v in sorted(self.spaces.items())},
            "operators": {k: v.canonical() for k, v in sorted(self.operators.items())},
            "vectors": {k: v.canonical() for k, v in sorted(self.vectors.items())},
            "packets": {
                k: v.canonical(include_digest=True) for k, v in sorted(self.packets.items())
            },
            "proofs": {k: asdict(v) for k, v in sorted(self.proofs.items())},
            "memories": {
                k: [asdict(record) for record in records]
                for k, records in sorted(self.memories.items())
            },
            "actions": {k: asdict(v) for k, v in sorted(self.actions.items())},
            "capabilities": {
                agent: {effect: cap.canonical() for effect, cap in sorted(caps.items())}
                for agent, caps in sorted(self.capabilities.items())
            },
            "contracts": {k: v.canonical() for k, v in sorted(self.contracts.items())},
            "sessions": {k: v.canonical() for k, v in sorted(self.sessions.items())},
            "metadata": {k: dict(v) for k, v in sorted(self.metadata.items())},
            "secret_digests": dict(sorted(self.secret_digests.items())),
            "receipt_count": len(self.receipts),
            "receipt_chain_tip": (
                self.receipts[-1]["digest"] if self.receipts else "0" * 64
            ),
            "event_count": len(self.events),
            "static_report": self.static_report,
            "assertions": self.assertions,
            "step": self.step,
        }
        payload["snapshot_digest"] = digest(payload)
        return payload

    def public_projection(self) -> dict[str, Any]:
        """Return the declared public surface used by paired-trace audits."""
        payload = {
            "agents": {k: asdict(v) for k, v in sorted(self.agents.items())},
            "lineages": dict(sorted(self.lineage_parents.items())),
            "packets": {
                k: {
                    "content": p.content,
                    "confidence": _round(p.confidence),
                    "provenance": p.provenance,
                    "status": p.status,
                    "accessible_to": sorted(p.accessible_to),
                    "bound_to": sorted(p.bound_to),
                    "quarantined_by": sorted(p.quarantined_by),
                }
                for k, p in sorted(self.packets.items())
            },
            "metadata": {k: dict(v) for k, v in sorted(self.metadata.items())},
            "actions": {
                k: {
                    "agent": a.agent,
                    "effect": a.effect,
                    "executed": a.executed,
                    "observed": a.observed,
                }
                for k, a in sorted(self.actions.items())
            },
        }
        payload["public_digest"] = digest(payload)
        return payload


def verify_receipt_chain(
    source: RuntimeState | Iterable[dict[str, Any]],
    *,
    require_genesis: bool = True,
) -> dict[str, Any]:
    """Verify the deterministic hash chain over all runtime receipts.

    The check establishes byte-level linkage and index continuity.  It does not
    by itself establish that a receipt's semantic claim is true; semantic
    validators remain separately responsible for that obligation.
    """

    receipts = list(source.receipts if isinstance(source, RuntimeState) else source)
    previous = "0" * 64 if require_genesis else (
        str(receipts[0].get("previous_digest", "0" * 64)) if receipts else "0" * 64
    )
    failures: list[str] = []
    first_index = 0 if require_genesis else (
        int(receipts[0].get("index", 0)) if receipts else 0
    )
    for offset, receipt in enumerate(receipts):
        expected_index = first_index + offset
        if receipt.get("index") != expected_index:
            failures.append(f"index:{expected_index}")
        if receipt.get("previous_digest") != previous:
            failures.append(f"previous_digest:{expected_index}")
        observed = receipt.get("digest")
        unsigned = dict(receipt)
        unsigned.pop("digest", None)
        expected = digest(unsigned)
        if observed != expected:
            failures.append(f"digest:{expected_index}")
        previous = str(observed)
    payload = {
        "schema": "osl.core.receipt-chain-verification.v1",
        "receipt_count": len(receipts),
        "chain_tip": previous,
        "failed_checks": failures,
        "all_checks_pass": not failures,
    }
    payload["verification_digest"] = digest(payload)
    return payload
