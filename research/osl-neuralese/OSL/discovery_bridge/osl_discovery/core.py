"""Deterministic finite operator synthesis and admission for OSL.

The bridge treats a learned or human-proposed operator as untrusted.  It may
receive a name only after demonstrations identify one exact transformation
class in a declared finite world and every claimed law is exhaustively checked.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import re
from typing import Any, Iterable, Mapping, Sequence

from .worlds import (
    canonical_json,
    canonical_transformation_id,
    enumerate_states,
    execute,
    find_witness_state,
    get_world,
    normalize_program,
    programs_equivalent,
    transformation_signature,
    validate_state,
)


SCHEMA = "osl.discovery.proposal.v1"
CERTIFICATE_SCHEMA = "osl.discovery.certificate.v1"
CLAIM_BOUNDARY = (
    "Exact bounded admission within the declared finite world and synthesis "
    "depth. This does not establish open-world discovery, neural semantic "
    "truth, spontaneous language emergence, or consciousness."
)
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ProposalError(ValueError):
    """Raised when a proposal is malformed rather than scientifically negative."""


@dataclass(frozen=True)
class CandidateClass:
    signature: tuple[str, ...]
    representative: tuple[str, ...]
    programs: tuple[tuple[str, ...], ...]


def digest_object(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


def _programs(operators: Sequence[str], max_depth: int) -> Iterable[tuple[str, ...]]:
    yield ()
    for depth in range(1, max_depth + 1):
        yield from product(operators, repeat=depth)


def quotient_classes(world: str, max_depth: int) -> tuple[CandidateClass, ...]:
    spec = get_world(world)
    grouped: dict[tuple[str, ...], list[tuple[str, ...]]] = {}
    for program in _programs(spec.operators, max_depth):
        signature = transformation_signature(spec, program)
        grouped.setdefault(signature, []).append(program)
    classes = []
    for signature, programs in grouped.items():
        ordered = tuple(sorted(programs, key=lambda item: (len(item), item)))
        classes.append(CandidateClass(signature, ordered[0], ordered))
    return tuple(sorted(classes, key=lambda item: (len(item.representative), item.representative)))


def _validate_proposal(proposal: Mapping[str, Any]) -> dict[str, Any]:
    data = _copy(dict(proposal))
    if data.get("schema") != SCHEMA:
        raise ProposalError(f"schema must be {SCHEMA!r}")
    candidate = data.get("candidate")
    if not isinstance(candidate, dict):
        raise ProposalError("candidate must be an object")
    name = candidate.get("name")
    version = candidate.get("version")
    world = candidate.get("world")
    if not isinstance(name, str) or not IDENT.fullmatch(name):
        raise ProposalError("candidate.name must be an OSL identifier")
    if not isinstance(version, str) or not version:
        raise ProposalError("candidate.version must be a nonempty string")
    spec = get_world(str(world))
    candidate["world"] = spec.name
    max_depth = data.get("max_depth")
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or not 0 <= max_depth <= 4:
        raise ProposalError("max_depth must be an integer from 0 through 4")
    source = data.get("source")
    if not isinstance(source, dict):
        raise ProposalError("source must be an object")
    if not isinstance(source.get("kind"), str) or not source["kind"]:
        raise ProposalError("source.kind must be a nonempty string")
    if not isinstance(source.get("digest"), str) or not HEX64.fullmatch(source["digest"]):
        raise ProposalError("source.digest must be a lowercase SHA-256 hex digest")
    demonstrations = data.get("demonstrations")
    if not isinstance(demonstrations, list) or not demonstrations:
        raise ProposalError("demonstrations must be a nonempty list")
    for index, demonstration in enumerate(demonstrations):
        if not isinstance(demonstration, dict):
            raise ProposalError(f"demonstration {index} must be an object")
        if set(demonstration) != {"input", "output"}:
            raise ProposalError(f"demonstration {index} must contain exactly input and output")
        try:
            validate_state(spec, demonstration["input"])
            validate_state(spec, demonstration["output"])
        except Exception as exc:
            raise ProposalError(f"invalid demonstration {index}: {exc}") from exc
    laws = data.get("claimed_laws", [])
    if not isinstance(laws, list):
        raise ProposalError("claimed_laws must be a list")
    seen_laws: set[str] = set()
    for index, law in enumerate(laws):
        if not isinstance(law, dict):
            raise ProposalError(f"claimed law {index} must be an object")
        if set(law) != {"law_id", "left", "right"}:
            raise ProposalError(f"claimed law {index} must contain law_id, left, and right")
        law_id = law["law_id"]
        if not isinstance(law_id, str) or not IDENT.fullmatch(law_id):
            raise ProposalError(f"claimed law {index} has an invalid law_id")
        if law_id in seen_laws:
            raise ProposalError(f"duplicate claimed law {law_id!r}")
        seen_laws.add(law_id)
        for side in ("left", "right"):
            word = law[side]
            if not isinstance(word, list) or not all(isinstance(token, str) for token in word):
                raise ProposalError(f"claimed law {law_id!r} side {side!r} must be a string list")
            unknown = [token for token in word if token != "$candidate" and token not in spec.operators]
            if unknown:
                raise ProposalError(f"claimed law {law_id!r} uses unknown operators {unknown}")
    data["claimed_laws"] = laws
    return data


def _base_certificate(proposal: Mapping[str, Any], classes: Sequence[CandidateClass]) -> dict[str, Any]:
    spec = get_world(proposal["candidate"]["world"])
    raw_program_count = sum(len(item.programs) for item in classes)
    return {
        "schema": CERTIFICATE_SCHEMA,
        "proposal": _copy(proposal),
        "candidate": _copy(proposal["candidate"]),
        "proposal_digest": digest_object(proposal),
        "source": _copy(proposal["source"]),
        "synthesis": {
            "max_depth": proposal["max_depth"],
            "primitive_count": len(spec.operators),
            "raw_program_count": raw_program_count,
            "quotient_class_count": len(classes),
            "legal_state_count": len(enumerate_states(spec)),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _seal(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = _copy(dict(payload))
    result["certificate_digest"] = digest_object(result)
    return result


def _demo_map(proposal: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, Any] | None]:
    mapping: dict[str, str] = {}
    first: dict[str, Any] = {}
    for index, demo in enumerate(proposal["demonstrations"]):
        input_key = canonical_json(demo["input"])
        output_key = canonical_json(demo["output"])
        if input_key in mapping and mapping[input_key] != output_key:
            return mapping, {
                "kind": "conflicting_demonstrations",
                "demonstration_index": index,
                "input": _copy(demo["input"]),
                "first_output": json.loads(mapping[input_key]),
                "conflicting_output": _copy(demo["output"]),
            }
        mapping[input_key] = output_key
        first.setdefault(input_key, demo)
    return mapping, None


def _matches_demonstrations(candidate: CandidateClass, demo_map: Mapping[str, str], states: Sequence[Mapping[str, Any]]) -> bool:
    state_index = {canonical_json(state): index for index, state in enumerate(states)}
    for input_key, expected_output in demo_map.items():
        position = state_index[input_key]
        if candidate.signature[position] != expected_output:
            return False
    return True


def _expand(word: Sequence[str], representative: Sequence[str]) -> tuple[str, ...]:
    expanded: list[str] = []
    for token in word:
        if token == "$candidate":
            expanded.extend(representative)
        else:
            expanded.append(token)
    return tuple(expanded)


def _law_results(world: str, representative: Sequence[str], laws: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for law in laws:
        left = _expand(law["left"], representative)
        right = _expand(law["right"], representative)
        passed = programs_equivalent(world, left, right)
        witness = None
        if not passed:
            state = find_witness_state(world, left, right)
            assert state is not None
            witness = {
                "input": state,
                "left_output": execute(world, state, left).final_state,
                "right_output": execute(world, state, right).final_state,
            }
        results.append(
            {
                "law_id": law["law_id"],
                "left_expansion": list(left),
                "right_expansion": list(right),
                "passed": passed,
                "witness": witness,
            }
        )
    return results


def synthesize(proposal: Mapping[str, Any]) -> dict[str, Any]:
    """Synthesize and adjudicate one finite operator proposal."""

    normalized = _validate_proposal(proposal)
    world = normalized["candidate"]["world"]
    states = enumerate_states(world)
    classes = quotient_classes(world, normalized["max_depth"])
    base = _base_certificate(normalized, classes)
    demos, conflict = _demo_map(normalized)
    if conflict is not None:
        return _seal(
            {
                **base,
                "status": "UNSATISFIABLE",
                "decision": "reject",
                "compatible_quotient_count": 0,
                "witness": conflict,
                "law_results": [],
            }
        )

    compatible = [item for item in classes if _matches_demonstrations(item, demos, states)]
    if not compatible:
        ranked = []
        state_index = {canonical_json(state): index for index, state in enumerate(states)}
        for item in classes:
            matches = sum(item.signature[state_index[key]] == value for key, value in demos.items())
            ranked.append((matches, item))
        _, nearest = max(ranked, key=lambda pair: (pair[0], -len(pair[1].representative), tuple(reversed(pair[1].representative))))
        witness = None
        for demo in normalized["demonstrations"]:
            actual = execute(world, demo["input"], nearest.representative).final_state
            if actual != demo["output"]:
                witness = {
                    "kind": "no_program_matches_all_demonstrations",
                    "input": _copy(demo["input"]),
                    "expected_output": _copy(demo["output"]),
                    "nearest_program": list(nearest.representative),
                    "nearest_output": actual,
                }
                break
        return _seal(
            {
                **base,
                "status": "UNSATISFIABLE",
                "decision": "reject",
                "compatible_quotient_count": 0,
                "witness": witness,
                "law_results": [],
            }
        )

    if len(compatible) > 1:
        first, second = compatible[0], compatible[1]
        witness_state = find_witness_state(world, first.representative, second.representative)
        assert witness_state is not None
        candidates = [list(item.representative) for item in compatible]
        return _seal(
            {
                **base,
                "status": "AMBIGUOUS",
                "decision": "quarantine",
                "compatible_quotient_count": len(compatible),
                "candidate_representatives": candidates[:32],
                "candidate_set_digest": digest_object(candidates),
                "witness": {
                    "kind": "separating_state",
                    "input": witness_state,
                    "first_program": list(first.representative),
                    "first_output": execute(world, witness_state, first.representative).final_state,
                    "second_program": list(second.representative),
                    "second_output": execute(world, witness_state, second.representative).final_state,
                },
                "law_results": [],
            }
        )

    identified = compatible[0]
    laws = _law_results(world, identified.representative, normalized["claimed_laws"])
    transformation_id = canonical_transformation_id(world, identified.representative)
    signature_digest = digest_object(list(identified.signature))
    common = {
        **base,
        "compatible_quotient_count": 1,
        "representative": list(identified.representative),
        "equivalent_program_count": len(identified.programs),
        "equivalent_programs": [list(item) for item in identified.programs[:64]],
        "transformation_id": transformation_id,
        "transformation_signature_digest": signature_digest,
        "law_results": laws,
    }
    if len(identified.representative) <= 1:
        return _seal(
            {
                **common,
                "status": "REJECTED_NONNOVEL",
                "decision": "reject",
                "witness": {
                    "kind": "identity_or_primitive_equivalence",
                    "shortest_representative": list(identified.representative),
                },
            }
        )
    failed = next((law for law in laws if not law["passed"]), None)
    if failed is not None:
        return _seal(
            {
                **common,
                "status": "REJECTED_FALSE_LAW",
                "decision": "reject",
                "witness": failed["witness"],
            }
        )
    return _seal(
        {
            **common,
            "status": "ADMITTED",
            "decision": "admit",
            "witness": None,
        }
    )


def verify_certificate(
    proposal: Mapping[str, Any] | None,
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify integrity and deterministic semantic replay of a certificate."""

    supplied = _copy(dict(certificate))
    digest = supplied.pop("certificate_digest", None)
    integrity = isinstance(digest, str) and digest == digest_object(supplied)
    replay_proposal = proposal if proposal is not None else certificate.get("proposal")
    if not isinstance(replay_proposal, Mapping):
        return {
            "schema": "osl.discovery.certificate-verification.v1",
            "integrity_valid": integrity,
            "deterministic_replay_equal": False,
            "proposal_digest_matches": False,
            "valid": False,
            "certificate_digest": digest,
            "error": "certificate does not contain a replayable proposal",
        }
    try:
        replay = synthesize(replay_proposal)
        replay_equal = canonical_json(replay) == canonical_json(certificate)
        proposal_digest_matches = certificate.get("proposal_digest") == digest_object(
            _validate_proposal(replay_proposal)
        )
        error = None
    except (KeyError, TypeError, ValueError) as exc:
        replay_equal = False
        proposal_digest_matches = False
        error = f"certificate proposal cannot be replayed: {exc}"
    return {
        "schema": "osl.discovery.certificate-verification.v1",
        "integrity_valid": integrity,
        "deterministic_replay_equal": replay_equal,
        "proposal_digest_matches": proposal_digest_matches,
        "valid": bool(integrity and replay_equal and proposal_digest_matches),
        "certificate_digest": digest,
        "error": error,
    }


__all__ = [
    "CERTIFICATE_SCHEMA",
    "CLAIM_BOUNDARY",
    "ProposalError",
    "SCHEMA",
    "digest_object",
    "quotient_classes",
    "synthesize",
    "verify_certificate",
]
