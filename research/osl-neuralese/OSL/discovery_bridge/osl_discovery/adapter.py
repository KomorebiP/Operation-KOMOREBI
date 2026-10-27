"""Render discovery decisions as valid OSL-Core 0.3 source programs."""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

from .core import ProposalError, verify_certificate
from .worlds import canonical_json


def _identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not cleaned or not (cleaned[0].isalpha() or cleaned[0] == "_"):
        cleaned = f"candidate_{cleaned}"
    return cleaned


def emit_osl(proposal: Mapping[str, Any], certificate: Mapping[str, Any]) -> str:
    """Compile a bridge decision to a quarantine, rejection, or admission trace."""

    if not verify_certificate(proposal, certificate)["valid"]:
        raise ProposalError("refusing to emit OSL from a certificate that fails semantic replay")

    candidate = _identifier(str(proposal["candidate"]["name"]))
    module = _identifier(f"discovery_{candidate}_{proposal['candidate']['version']}")
    feature = _identifier(f"q_{certificate['certificate_digest'][:16]}")
    content_record = {
        "candidate": proposal["candidate"],
        "certificate_digest": certificate["certificate_digest"],
        "decision": certificate["decision"],
        "representative": certificate.get("representative"),
        "status": certificate["status"],
        "transformation_id": certificate.get("transformation_id"),
    }
    content_literal = json.dumps(canonical_json(content_record), ensure_ascii=True)
    confidence = 1.0 if certificate["decision"] == "admit" else 0.5 if certificate["decision"] == "quarantine" else 0.0
    lines = [
        f"module {module}",
        "lineage L_Discovery",
        "agent Bridge lineage L_Discovery",
        f"neural_propose {candidate} to Bridge feature {feature} content {content_literal} confidence {confidence:.1f}",
    ]
    if certificate["decision"] == "admit":
        lines.extend(
            [
                f"attest origin {candidate} by Bridge lineage L_Discovery as p_origin",
                f"attest relevance {candidate} by Bridge for planning as p_relevance",
                f'admit {candidate} by Bridge using ["p_origin","p_relevance"]',
                f"assert packet {candidate} status admitted",
                f"assert packet {candidate} quarantined_by Bridge false",
            ]
        )
    elif certificate["decision"] == "reject":
        lines.extend(
            [
                f"reject_candidate {candidate} by Bridge",
                f"assert packet {candidate} status rejected",
                f"assert packet {candidate} quarantined_by Bridge true",
            ]
        )
    else:
        lines.extend(
            [
                f"assert packet {candidate} status provisional",
                f"assert packet {candidate} quarantined_by Bridge true",
            ]
        )
    lines.append("show")
    return "\n".join(lines) + "\n"


__all__ = ["emit_osl"]
