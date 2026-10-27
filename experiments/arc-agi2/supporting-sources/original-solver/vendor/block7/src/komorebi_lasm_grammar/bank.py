"""Persistent evidence bank and grammar-promotion policy."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.model import canonical_value, sha256_record

from .abstraction import abstraction_descriptor, abstraction_key, build_macro_template
from .model import MacroBank, MacroEvidence, MacroStatus, MacroTemplate


@dataclass
class PersistentEvidenceBank:
    """Mutable audit-time evidence store with fail-closed retirement.

    Prediction uses a frozen :class:`MacroBank` snapshot created *before* the
    current label is revealed.  Observation occurs afterward.
    """

    minimum_support: int = 2
    evidence: dict[str, MacroEvidence] = field(default_factory=dict)

    def _entry(self, family: str, parameters: Mapping[str, Any]) -> MacroEvidence:
        scope, controls, _ = abstraction_descriptor(family, parameters)
        key = abstraction_key(family, parameters)
        if key not in self.evidence:
            self.evidence[key] = MacroEvidence(
                key=key,
                scope=scope,
                family=str(family),
                controls=dict(canonical_value(controls)),
            )
        return self.evidence[key]

    def observe_candidate(
        self,
        *,
        task_id: str,
        family: str,
        parameters: Mapping[str, Any],
        signature: str,
        correct: bool,
    ) -> None:
        self._entry(family, parameters).observe(
            task_id=task_id,
            signature=signature,
            parameters=parameters,
            correct=correct,
        )

    def templates(self) -> tuple[MacroTemplate, ...]:
        return tuple(
            sorted(
                (build_macro_template(item, self.minimum_support) for item in self.evidence.values()),
                key=lambda macro: (macro.family, macro.scope.value, macro.macro_id),
            )
        )

    def stable_bank(self) -> MacroBank:
        stable = tuple(macro for macro in self.templates() if macro.status is MacroStatus.STABLE)
        return MacroBank(tuple(sorted(stable, key=lambda macro: macro.macro_id)), minimum_support=self.minimum_support)

    def provisional_templates(self) -> tuple[MacroTemplate, ...]:
        return tuple(macro for macro in self.templates() if macro.status is MacroStatus.PROVISIONAL)

    def retired_templates(self) -> tuple[MacroTemplate, ...]:
        return tuple(macro for macro in self.templates() if macro.status is MacroStatus.RETIRED)

    def audit_record(self) -> dict[str, Any]:
        templates = self.templates()
        record = {
            "schema": "komorebi.lasm_persistent_evidence_bank",
            "schema_version": 1,
            "minimum_support": int(self.minimum_support),
            "stable_count": sum(macro.status is MacroStatus.STABLE for macro in templates),
            "provisional_count": sum(macro.status is MacroStatus.PROVISIONAL for macro in templates),
            "retired_count": sum(macro.status is MacroStatus.RETIRED for macro in templates),
            "candidate_count": sum(macro.status is MacroStatus.CANDIDATE for macro in templates),
            "evidence": [self.evidence[key].to_audit_record() for key in sorted(self.evidence)],
            "templates": [macro.to_record() for macro in templates],
        }
        record["content_hash"] = sha256_record({key: value for key, value in record.items() if key != "content_hash"})
        return record


__all__ = ["PersistentEvidenceBank"]
