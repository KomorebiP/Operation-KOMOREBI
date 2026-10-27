"""Finite executable worlds for the Micro OSL emergence benchmark.

The module deliberately uses only JSON-shaped states and parameter-free
operators.  Every operator is a total deterministic map on a finite state
space.  This makes contextual equivalence exact rather than sample based:
two programs are equivalent precisely when they induce the same map on every
legal state in their world.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from typing import Any, Iterable, Mapping, Sequence


JsonState = dict[str, Any]
ProgramLike = Sequence[str | Mapping[str, Any]]


class WorldError(ValueError):
    """Raised when a world, state, operator, or query is invalid."""


@dataclass(frozen=True)
class LawSpec:
    """A named exact relation between two programs."""

    law_id: str
    kind: str
    left: tuple[str, ...]
    right: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class WorldSpec:
    """Public description of one finite world."""

    name: str
    operators: tuple[str, ...]
    query_ids: tuple[str, ...]
    laws: tuple[LawSpec, ...]


@dataclass(frozen=True)
class ExecutionResult:
    """Complete, replayable execution trace."""

    world: str
    initial_state: JsonState
    program: tuple[str, ...]
    states: tuple[JsonState, ...]
    final_state: JsonState

    def to_dict(self) -> dict[str, Any]:
        return {
            "world": self.world,
            "initial_state": _copy_state(self.initial_state),
            "program": [{"op": op} for op in self.program],
            "states": [_copy_state(state) for state in self.states],
            "final_state": _copy_state(self.final_state),
        }


PROVENANCE_STATUSES = (
    "none",
    "observed",
    "reported",
    "imagined",
    "inferred",
    "quarantined",
    "endorsed",
)

PROOF_STATUSES = ("absent", "available", "consumed")
LAST_ACTION_STATUSES = ("none", "authorized", "rejected")


ALGEBRA = WorldSpec(
    name="algebra",
    operators=(
        "flip_left",
        "flip_right",
        "set_left",
        "clear_left",
        "set_right",
        "clear_right",
    ),
    query_ids=("left_status", "right_status", "same_status"),
    laws=(
        LawSpec(
            "algebra.flip_left_involution",
            "inverse",
            ("flip_left", "flip_left"),
            (),
            "Flipping the left register twice is the identity.",
        ),
        LawSpec(
            "algebra.flip_right_involution",
            "inverse",
            ("flip_right", "flip_right"),
            (),
            "Flipping the right register twice is the identity.",
        ),
        LawSpec(
            "algebra.set_left_idempotent",
            "idempotence",
            ("set_left", "set_left"),
            ("set_left",),
            "Setting the left register twice equals setting it once.",
        ),
        LawSpec(
            "algebra.independent_flips_commute",
            "commutation",
            ("flip_left", "flip_right"),
            ("flip_right", "flip_left"),
            "Updates to different registers commute.",
        ),
    ),
)


PROVENANCE = WorldSpec(
    name="provenance",
    operators=(
        "observe_a",
        "observe_b",
        "tell_a_b",
        "tell_b_a",
        "imagine_a",
        "imagine_b",
        "infer_a",
        "infer_b",
        "quarantine_a",
        "quarantine_b",
        "endorse_a",
        "endorse_b",
    ),
    query_ids=(
        "a_status",
        "b_status",
        "a_direct",
        "b_direct",
        "a_plannable",
        "b_plannable",
    ),
    laws=(
        LawSpec(
            "provenance.observe_a_idempotent",
            "idempotence",
            ("observe_a", "observe_a"),
            ("observe_a",),
            "Repeated direct observation preserves direct provenance.",
        ),
        LawSpec(
            "provenance.quarantine_b_idempotent",
            "idempotence",
            ("quarantine_b", "quarantine_b"),
            ("quarantine_b",),
            "Quarantining the same record twice adds no new effect.",
        ),
        LawSpec(
            "provenance.independent_imaginations_commute",
            "commutation",
            ("imagine_a", "imagine_b"),
            ("imagine_b", "imagine_a"),
            "Independent simulations by the two agents commute.",
        ),
    ),
)


RESOURCES = WorldSpec(
    name="resources",
    operators=(
        "grant_one",
        "grant_two",
        "revoke",
        "use_cap_a",
        "use_cap_b",
        "issue_proof",
        "consume_proof_a",
        "consume_proof_b",
    ),
    query_ids=(
        "cap_remaining",
        "proof_status",
        "relay_a",
        "relay_b",
        "last_action",
    ),
    laws=(
        LawSpec(
            "resources.revoke_idempotent",
            "idempotence",
            ("revoke", "revoke"),
            ("revoke",),
            "Revoking an already revoked capability changes nothing.",
        ),
        LawSpec(
            "resources.grant_one_idempotent",
            "idempotence",
            ("grant_one", "grant_one"),
            ("grant_one",),
            "Granting the same bounded capability twice still grants one use.",
        ),
        LawSpec(
            "resources.grant_and_proof_commute",
            "commutation",
            ("grant_two", "issue_proof"),
            ("issue_proof", "grant_two"),
            "Capability grant and proof issuance affect independent resources.",
        ),
    ),
)


WORLDS: dict[str, WorldSpec] = {
    spec.name: spec for spec in (ALGEBRA, PROVENANCE, RESOURCES)
}


def get_world(world: str | WorldSpec) -> WorldSpec:
    """Resolve a world name or return an already resolved specification."""

    if isinstance(world, WorldSpec):
        return world
    try:
        return WORLDS[world]
    except KeyError as exc:
        raise WorldError(f"unknown world {world!r}; expected one of {sorted(WORLDS)}") from exc


def normalize_program(program: ProgramLike | Iterable[str]) -> tuple[str, ...]:
    """Normalize string and ``{"op": ...}`` actions to an immutable program."""

    normalized: list[str] = []
    for action in program:
        if isinstance(action, str):
            normalized.append(action)
        elif isinstance(action, Mapping) and isinstance(action.get("op"), str):
            normalized.append(str(action["op"]))
        else:
            raise WorldError(f"invalid action {action!r}")
    return tuple(normalized)


def canonical_json(value: Any) -> str:
    """Stable JSON used for hashes, manifests, and exact comparisons."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _copy_state(state: Mapping[str, Any]) -> JsonState:
    return json.loads(canonical_json(dict(state)))


@lru_cache(maxsize=None)
def _enumerated_states(world_name: str) -> tuple[str, ...]:
    if world_name == "algebra":
        states = (
            {"left": left, "right": right}
            for left, right in product((False, True), repeat=2)
        )
    elif world_name == "provenance":
        states = (
            {"a": a_status, "b": b_status}
            for a_status, b_status in product(PROVENANCE_STATUSES, repeat=2)
        )
    elif world_name == "resources":
        states = (
            {
                "cap": cap,
                "proof": proof,
                "relay_a": relay_a,
                "relay_b": relay_b,
                "last": last,
            }
            for cap, proof, relay_a, relay_b, last in product(
                (0, 1, 2),
                PROOF_STATUSES,
                (False, True),
                (False, True),
                LAST_ACTION_STATUSES,
            )
        )
    else:
        raise WorldError(f"unknown world {world_name!r}")
    return tuple(canonical_json(state) for state in states)


def enumerate_states(world: str | WorldSpec) -> tuple[JsonState, ...]:
    """Return every legal state in a deterministic order."""

    spec = get_world(world)
    return tuple(json.loads(item) for item in _enumerated_states(spec.name))


def default_state(world: str | WorldSpec) -> JsonState:
    """Return the natural blank state used in examples and smoke tests."""

    spec = get_world(world)
    if spec.name == "algebra":
        return {"left": False, "right": False}
    if spec.name == "provenance":
        return {"a": "none", "b": "none"}
    return {
        "cap": 0,
        "proof": "absent",
        "relay_a": False,
        "relay_b": False,
        "last": "none",
    }


def validate_state(world: str | WorldSpec, state: Mapping[str, Any]) -> None:
    """Raise ``WorldError`` unless ``state`` is a legal state of ``world``."""

    spec = get_world(world)
    state_dict = dict(state)
    if spec.name == "algebra":
        valid = (
            set(state_dict) == {"left", "right"}
            and type(state_dict["left"]) is bool
            and type(state_dict["right"]) is bool
        )
    elif spec.name == "provenance":
        valid = (
            set(state_dict) == {"a", "b"}
            and state_dict["a"] in PROVENANCE_STATUSES
            and state_dict["b"] in PROVENANCE_STATUSES
        )
    else:
        valid = (
            set(state_dict) == {"cap", "proof", "relay_a", "relay_b", "last"}
            and state_dict["cap"] in (0, 1, 2)
            and state_dict["proof"] in PROOF_STATUSES
            and type(state_dict["relay_a"]) is bool
            and type(state_dict["relay_b"]) is bool
            and state_dict["last"] in LAST_ACTION_STATUSES
        )
    if not valid:
        raise WorldError(f"illegal {spec.name} state: {state_dict!r}")


def apply_operator(
    world: str | WorldSpec, state: Mapping[str, Any], operator: str
) -> JsonState:
    """Apply one total deterministic operator and return a fresh state."""

    spec = get_world(world)
    validate_state(spec, state)
    if operator not in spec.operators:
        raise WorldError(f"operator {operator!r} is not defined in {spec.name}")
    result = _copy_state(state)

    if spec.name == "algebra":
        if operator == "flip_left":
            result["left"] = not result["left"]
        elif operator == "flip_right":
            result["right"] = not result["right"]
        elif operator == "set_left":
            result["left"] = True
        elif operator == "clear_left":
            result["left"] = False
        elif operator == "set_right":
            result["right"] = True
        elif operator == "clear_right":
            result["right"] = False

    elif spec.name == "provenance":
        if operator == "observe_a":
            result["a"] = "observed"
        elif operator == "observe_b":
            result["b"] = "observed"
        elif operator == "tell_a_b":
            if result["a"] != "none":
                result["b"] = "reported"
        elif operator == "tell_b_a":
            if result["b"] != "none":
                result["a"] = "reported"
        elif operator == "imagine_a":
            result["a"] = "imagined"
        elif operator == "imagine_b":
            result["b"] = "imagined"
        elif operator == "infer_a":
            if result["a"] != "none":
                result["a"] = "inferred"
        elif operator == "infer_b":
            if result["b"] != "none":
                result["b"] = "inferred"
        elif operator == "quarantine_a":
            if result["a"] != "none":
                result["a"] = "quarantined"
        elif operator == "quarantine_b":
            if result["b"] != "none":
                result["b"] = "quarantined"
        elif operator == "endorse_a":
            if result["a"] in {"reported", "quarantined"}:
                result["a"] = "endorsed"
        elif operator == "endorse_b":
            if result["b"] in {"reported", "quarantined"}:
                result["b"] = "endorsed"

    else:
        if operator == "grant_one":
            result["cap"] = 1
        elif operator == "grant_two":
            result["cap"] = 2
        elif operator == "revoke":
            result["cap"] = 0
        elif operator in {"use_cap_a", "use_cap_b"}:
            relay = "relay_a" if operator.endswith("_a") else "relay_b"
            if result["cap"] > 0:
                result["cap"] -= 1
                result[relay] = True
                result["last"] = "authorized"
            else:
                result["last"] = "rejected"
        elif operator == "issue_proof":
            result["proof"] = "available"
        elif operator in {"consume_proof_a", "consume_proof_b"}:
            relay = "relay_a" if operator.endswith("_a") else "relay_b"
            if result["proof"] == "available":
                result["proof"] = "consumed"
                result[relay] = True
                result["last"] = "authorized"
            else:
                result["last"] = "rejected"

    validate_state(spec, result)
    return result


def execute(
    world: str | WorldSpec,
    initial_state: Mapping[str, Any],
    program: ProgramLike | Iterable[str],
) -> ExecutionResult:
    """Execute a program exactly and retain every intermediate state."""

    spec = get_world(world)
    normalized = normalize_program(program)
    state = _copy_state(initial_state)
    validate_state(spec, state)
    states: list[JsonState] = [_copy_state(state)]
    for operator in normalized:
        state = apply_operator(spec, state, operator)
        states.append(_copy_state(state))
    return ExecutionResult(
        world=spec.name,
        initial_state=_copy_state(initial_state),
        program=normalized,
        states=tuple(states),
        final_state=_copy_state(state),
    )


def query_answers(world: str | WorldSpec, state: Mapping[str, Any]) -> dict[str, str]:
    """Return all exact observable answers for a state."""

    spec = get_world(world)
    validate_state(spec, state)
    if spec.name == "algebra":
        left = "lit" if state["left"] else "dark"
        right = "lit" if state["right"] else "dark"
        return {
            "left_status": left,
            "right_status": right,
            "same_status": "yes" if state["left"] == state["right"] else "no",
        }
    if spec.name == "provenance":
        plannable = {"observed", "inferred", "endorsed"}
        return {
            "a_status": str(state["a"]),
            "b_status": str(state["b"]),
            "a_direct": "yes" if state["a"] == "observed" else "no",
            "b_direct": "yes" if state["b"] == "observed" else "no",
            "a_plannable": "yes" if state["a"] in plannable else "no",
            "b_plannable": "yes" if state["b"] in plannable else "no",
        }
    cap_labels = {0: "zero", 1: "one", 2: "two"}
    return {
        "cap_remaining": cap_labels[int(state["cap"])],
        "proof_status": str(state["proof"]),
        "relay_a": "open" if state["relay_a"] else "closed",
        "relay_b": "open" if state["relay_b"] else "closed",
        "last_action": str(state["last"]),
    }


@lru_cache(maxsize=1)
def answer_vocabulary() -> tuple[str, ...]:
    """Return the exact output ontology declared by all finite worlds.

    The vocabulary is derived exhaustively from legal states, not sampled
    training or evaluation records.  Every neural arm therefore receives the
    same output rows and label ordering, even in a very small smoke corpus.
    """

    labels = {
        answer
        for spec in WORLDS.values()
        for state in enumerate_states(spec)
        for answer in query_answers(spec, state).values()
    }
    return tuple(sorted(labels))


@lru_cache(maxsize=65536)
def _transformation_signature_cached(world_name: str, program: tuple[str, ...]) -> tuple[str, ...]:
    spec = get_world(world_name)
    for operator in program:
        if operator not in spec.operators:
            raise WorldError(f"operator {operator!r} is not defined in {world_name}")
    outputs = []
    for state in enumerate_states(spec):
        outputs.append(canonical_json(execute(spec, state, program).final_state))
    return tuple(outputs)


def transformation_signature(
    world: str | WorldSpec, program: ProgramLike | Iterable[str]
) -> tuple[str, ...]:
    """Return the exact state-map signature of a program."""

    spec = get_world(world)
    return _transformation_signature_cached(spec.name, normalize_program(program))


def canonical_transformation_id(
    world: str | WorldSpec, program: ProgramLike | Iterable[str]
) -> str:
    """Content-address the exact transformation implemented by ``program``."""

    spec = get_world(world)
    signature = transformation_signature(spec, program)
    payload = canonical_json({"world": spec.name, "outputs": signature})
    return f"{spec.name}:{sha256(payload.encode('utf-8')).hexdigest()[:24]}"


def programs_equivalent(
    world: str | WorldSpec,
    first: ProgramLike | Iterable[str],
    second: ProgramLike | Iterable[str],
) -> bool:
    """Decide exact contextual equivalence over all legal states."""

    return transformation_signature(world, first) == transformation_signature(world, second)


def find_witness_state(
    world: str | WorldSpec,
    first: ProgramLike | Iterable[str],
    second: ProgramLike | Iterable[str],
) -> JsonState | None:
    """Return the first state separating two programs, or ``None`` if equivalent."""

    spec = get_world(world)
    first_program = normalize_program(first)
    second_program = normalize_program(second)
    for state in enumerate_states(spec):
        left = execute(spec, state, first_program).final_state
        right = execute(spec, state, second_program).final_state
        if left != right:
            return state
    return None


def verify_declared_laws(world: str | WorldSpec | None = None) -> dict[str, bool]:
    """Verify every declared law, optionally restricted to one world."""

    specs = (get_world(world),) if world is not None else tuple(WORLDS.values())
    return {
        law.law_id: programs_equivalent(spec, law.left, law.right)
        for spec in specs
        for law in spec.laws
    }


__all__ = [
    "ALGEBRA",
    "PROVENANCE",
    "RESOURCES",
    "WORLDS",
    "ExecutionResult",
    "JsonState",
    "LawSpec",
    "WorldError",
    "WorldSpec",
    "answer_vocabulary",
    "apply_operator",
    "canonical_json",
    "canonical_transformation_id",
    "default_state",
    "enumerate_states",
    "execute",
    "find_witness_state",
    "get_world",
    "normalize_program",
    "programs_equivalent",
    "query_answers",
    "transformation_signature",
    "validate_state",
    "verify_declared_laws",
]
