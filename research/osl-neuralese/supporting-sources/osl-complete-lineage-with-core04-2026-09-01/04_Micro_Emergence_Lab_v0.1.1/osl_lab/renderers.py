"""Deterministic natural-language renderers for finite Micro OSL traces."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random
from typing import Any, Mapping, Sequence

from .worlds import (
    ExecutionResult,
    apply_operator,
    enumerate_states,
    execute,
    get_world,
    normalize_program,
    query_answers,
)


RENDERERS = ("direct", "narrative", "dialogue", "log", "passive")
LEXICONS = ("train", "lexical")


@dataclass(frozen=True)
class RenderContext:
    lexicon: str
    agent_a: str
    agent_b: str
    object_left: str
    object_right: str


_NAME_POOLS = {
    "train": (("Mira", "Niko"), ("Elena", "Tariq"), ("Iris", "Jonah")),
    "lexical": (("Soraya", "Dev"), ("Keiko", "Omar"), ("Lin", "Priya")),
}


def _stable_seed(seed: int, *parts: str) -> int:
    material = "|".join((str(seed),) + tuple(parts))
    return int.from_bytes(sha256(material.encode("utf-8")).digest()[:8], "big")


def make_context(world: str, lexicon: str = "train", seed: int = 0) -> RenderContext:
    """Create stable names and nouns for one rendered record."""

    if lexicon not in LEXICONS:
        raise ValueError(f"unknown lexicon {lexicon!r}; expected one of {LEXICONS}")
    rng = random.Random(_stable_seed(seed, world, lexicon))
    agent_a, agent_b = rng.choice(_NAME_POOLS[lexicon])
    if world == "algebra":
        objects = ("left lamp", "right lamp") if lexicon == "train" else (
            "west beacon",
            "east beacon",
        )
    elif world == "provenance":
        objects = ("gate report", "gate report") if lexicon == "train" else (
            "portal claim",
            "portal claim",
        )
    else:
        objects = ("amber relay", "cobalt relay") if lexicon == "train" else (
            "north channel",
            "south channel",
        )
    return RenderContext(lexicon, agent_a, agent_b, objects[0], objects[1])


def _on_off(value: bool, context: RenderContext) -> str:
    if context.lexicon == "train":
        return "lit" if value else "dark"
    return "active" if value else "inactive"


def summarize_state(
    world: str,
    state: Mapping[str, Any],
    lexicon: str = "train",
    seed: int = 0,
    compact: bool = False,
) -> str:
    """Render a complete state without concealing normally unqueried fields."""

    context = make_context(world, lexicon, seed)
    if world == "algebra":
        if compact:
            return f"{_on_off(bool(state['left']), context)} {_on_off(bool(state['right']), context)}"
        return (
            f"the {context.object_left} was {_on_off(bool(state['left']), context)} "
            f"and the {context.object_right} was {_on_off(bool(state['right']), context)}"
        )
    if world == "provenance":
        if compact:
            return f"{state['a']} {state['b']}"
        return (
            f"{context.agent_a}'s record was {state['a']} and "
            f"{context.agent_b}'s record was {state['b']}"
        )
    cap_word = {0: "zero", 1: "one", 2: "two"}[int(state["cap"])]
    left = "open" if state["relay_a"] else "closed"
    right = "open" if state["relay_b"] else "closed"
    if compact:
        return f"{cap_word} {state['proof']} {left} {right} {state['last']}"
    if lexicon == "train":
        resource = "pass" if int(state["cap"]) == 1 else "passes"
    else:
        resource = "credit" if int(state["cap"]) == 1 else "credits"
    return (
        f"{cap_word} {resource} remained, the proof was {state['proof']}, "
        f"the {context.object_left} was {left}, the {context.object_right} was {right}, "
        f"and the last decision was {state['last']}"
    )


def _active_phrase(world: str, operator: str, context: RenderContext) -> str:
    a, b = context.agent_a, context.agent_b
    left, right = context.object_left, context.object_right
    train = context.lexicon == "train"
    if world == "algebra":
        if train:
            verbs = {
                "flip_left": f"The {left} was switched to its opposite state.",
                "flip_right": f"The {right} was switched to its opposite state.",
                "set_left": f"The {left} was turned on.",
                "clear_left": f"The {left} was turned off.",
                "set_right": f"The {right} was turned on.",
                "clear_right": f"The {right} was turned off.",
            }
        else:
            verbs = {
                "flip_left": f"The state of the {left} was inverted.",
                "flip_right": f"The state of the {right} was inverted.",
                "set_left": f"The {left} entered active mode.",
                "clear_left": f"The {left} entered inactive mode.",
                "set_right": f"The {right} entered active mode.",
                "clear_right": f"The {right} entered inactive mode.",
            }
    elif world == "provenance":
        subject = "gate" if train else "portal"
        if train:
            verbs = {
                "observe_a": f"{a} directly inspected the {subject}.",
                "observe_b": f"{b} directly inspected the {subject}.",
                "tell_a_b": f"{a} passed the claim to {b}.",
                "tell_b_a": f"{b} passed the claim to {a}.",
                "imagine_a": f"{a} simulated the claim without observing it.",
                "imagine_b": f"{b} simulated the claim without observing it.",
                "infer_a": f"{a} derived a conclusion from the current record.",
                "infer_b": f"{b} derived a conclusion from the current record.",
                "quarantine_a": f"{a} isolated the current claim from planning.",
                "quarantine_b": f"{b} isolated the current claim from planning.",
                "endorse_a": f"{a} accepted the received claim for planning.",
                "endorse_b": f"{b} accepted the received claim for planning.",
            }
        else:
            verbs = {
                "observe_a": f"{a} personally verified the {subject}.",
                "observe_b": f"{b} personally verified the {subject}.",
                "tell_a_b": f"{a} relayed the assertion to {b}.",
                "tell_b_a": f"{b} relayed the assertion to {a}.",
                "imagine_a": f"{a} constructed a hypothetical assertion.",
                "imagine_b": f"{b} constructed a hypothetical assertion.",
                "infer_a": f"{a} deduced a result from the available entry.",
                "infer_b": f"{b} deduced a result from the available entry.",
                "quarantine_a": f"{a} sequestered the assertion from decisions.",
                "quarantine_b": f"{b} sequestered the assertion from decisions.",
                "endorse_a": f"{a} certified the relayed assertion for decisions.",
                "endorse_b": f"{b} certified the relayed assertion for decisions.",
            }
    else:
        grant = "pass" if train else "credit"
        if train:
            verbs = {
                "grant_one": f"The controller granted one bounded {grant}.",
                "grant_two": f"The controller granted two bounded {grant}s.",
                "revoke": f"The controller revoked every remaining {grant}.",
                "use_cap_a": f"An attempt was made to open the {left} with one {grant}.",
                "use_cap_b": f"An attempt was made to open the {right} with one {grant}.",
                "issue_proof": "A single-use proof token was issued.",
                "consume_proof_a": f"An attempt was made to open the {left} with the proof token.",
                "consume_proof_b": f"An attempt was made to open the {right} with the proof token.",
            }
        else:
            verbs = {
                "grant_one": "One bounded credit became available.",
                "grant_two": "Two bounded credits became available.",
                "revoke": "All remaining credits were invalidated.",
                "use_cap_a": f"One credit was presented to activate the {left}.",
                "use_cap_b": f"One credit was presented to activate the {right}.",
                "issue_proof": "A one-use certificate became available.",
                "consume_proof_a": f"The certificate was presented to activate the {left}.",
                "consume_proof_b": f"The certificate was presented to activate the {right}.",
            }
    return verbs[operator]


def _passive_phrase(world: str, operator: str, context: RenderContext) -> str:
    active = _active_phrase(world, operator, context)
    prefixes = {
        "algebra": "As the next recorded operation, ",
        "provenance": "In the provenance ledger, ",
        "resources": "Under the resource protocol, ",
    }
    return prefixes[world] + active[0].lower() + active[1:]


def render_execution(
    execution: ExecutionResult,
    renderer: str = "direct",
    lexicon: str = "train",
    seed: int = 0,
) -> str:
    """Render a previously executed trace through one of five grammar families."""

    if renderer not in RENDERERS:
        raise ValueError(f"unknown renderer {renderer!r}; expected one of {RENDERERS}")
    context = make_context(execution.world, lexicon, seed)
    initial = summarize_state(execution.world, execution.initial_state, lexicon, seed)
    active = [_active_phrase(execution.world, op, context) for op in execution.program]
    if renderer == "direct":
        opening = f"At the start, {initial}."
        return " ".join([opening] + active) if active else opening + " No operation followed."
    if renderer == "narrative":
        opening = f"The episode began as {initial}."
        transitions = []
        for index, sentence in enumerate(active):
            if index == 0:
                connector = "First"
            elif index == len(active) - 1:
                connector = "Finally"
            else:
                connector = "Next" if index % 2 else "After that"
            transitions.append(f"{connector}, {sentence[0].lower() + sentence[1:]}")
        return " ".join([opening] + transitions) if transitions else opening + " Nothing changed."
    if renderer == "dialogue":
        opening = f'The monitor reported, "Initially, {initial}."'
        quoted = [f'Then the monitor reported, "{sentence}"' for sentence in active]
        return " ".join([opening] + quoted) if quoted else opening
    if renderer == "log":
        entries = [f"Initial state: {initial}."]
        entries.extend(f"Event {index}: {sentence}" for index, sentence in enumerate(active, 1))
        if not active:
            entries.append("Event count: zero.")
        return " ".join(entries)
    passive = [_passive_phrase(execution.world, op, context) for op in execution.program]
    opening = f"Initially, {initial}."
    return " ".join([opening] + passive) if passive else opening + " No update was applied."


def render_trace(
    world: str,
    initial_state: Mapping[str, Any],
    program: Sequence[str | Mapping[str, Any]],
    renderer: str = "direct",
    lexicon: str = "train",
    seed: int = 0,
) -> str:
    """Execute and render a trace in one call."""

    return render_execution(execute(world, initial_state, program), renderer, lexicon, seed)


def render_question(
    world: str,
    query_id: str,
    renderer: str = "direct",
    lexicon: str = "train",
    seed: int = 0,
) -> str:
    """Render one query while preserving its exact semantic identifier."""

    spec = get_world(world)
    if query_id not in spec.query_ids:
        raise ValueError(f"query {query_id!r} is not defined in {world}")
    context = make_context(world, lexicon, seed)
    a, b = context.agent_a, context.agent_b
    left, right = context.object_left, context.object_right
    if world == "algebra":
        train = lexicon == "train"
        questions = {
            "left_status": f"Is the {left} now {'lit or dark' if train else 'active or inactive'}?",
            "right_status": f"Is the {right} now {'lit or dark' if train else 'active or inactive'}?",
            "same_status": f"Do the {left} and {right} now have the same state?",
        }
    elif world == "provenance":
        questions = {
            "a_status": f"What provenance status does {a}'s claim now have?",
            "b_status": f"What provenance status does {b}'s claim now have?",
            "a_direct": f"Does {a}'s current claim count as a direct observation?",
            "b_direct": f"Does {b}'s current claim count as a direct observation?",
            "a_plannable": f"May {a}'s current claim be used for planning?",
            "b_plannable": f"May {b}'s current claim be used for planning?",
        }
    else:
        unit = "passes" if lexicon == "train" else "credits"
        questions = {
            "cap_remaining": f"How many bounded {unit} remain?",
            "proof_status": "What is the current status of the proof token?",
            "relay_a": f"Is the {left} open or closed?",
            "relay_b": f"Is the {right} open or closed?",
            "last_action": "Was the most recent attempted action authorized, rejected, or neither?",
        }
    question = questions[query_id]
    if renderer == "log":
        return f"Audit query: {question}"
    if renderer == "dialogue":
        return f'The evaluator asked, "{question}"'
    return question


def render_answer(world: str, query_id: str, answer: str, lexicon: str = "train") -> str:
    """Translate an abstract answer into the vocabulary used by a renderer."""

    if world == "algebra" and lexicon == "lexical":
        return {"lit": "active", "dark": "inactive"}.get(answer, answer)
    return answer


def render_queries(
    world: str,
    final_state: Mapping[str, Any],
    renderer: str = "direct",
    lexicon: str = "train",
    seed: int = 0,
) -> list[dict[str, str]]:
    """Render every exact query and answer for ``final_state``."""

    answers = query_answers(world, final_state)
    return [
        {
            "question_id": query_id,
            "question": render_question(world, query_id, renderer, lexicon, seed),
            "answer": render_answer(world, query_id, answers[query_id], lexicon),
        }
        for query_id in get_world(world).query_ids
    ]


def _diagnostic_states(world: str, operators: Sequence[str]) -> tuple[Mapping[str, Any], ...]:
    """Greedily find a small state set whose transition fingerprints are unique."""

    candidates = enumerate_states(world)
    if len(operators) == 1:
        operator = operators[0]
        for state in candidates:
            if apply_operator(world, state, operator) != state:
                return (state,)
        return (candidates[0],)
    chosen: list[Mapping[str, Any]] = []
    signatures: dict[str, tuple[str, ...]] = {operator: () for operator in operators}
    while len(set(signatures.values())) < len(operators):
        best_state = None
        best_signatures = None
        best_unique = -1
        for state in candidates:
            if state in chosen:
                continue
            proposed = {
                operator: signatures[operator]
                + (str(sorted(apply_operator(world, state, operator).items())),)
                for operator in operators
            }
            unique = len(set(proposed.values()))
            if unique > best_unique:
                best_state = state
                best_signatures = proposed
                best_unique = unique
        if best_state is None or best_signatures is None:
            raise ValueError(f"could not distinguish operators {operators!r} in {world}")
        chosen.append(best_state)
        signatures = best_signatures
    return tuple(chosen)


def render_renaming_episode(
    world: str,
    initial_state: Mapping[str, Any],
    program: Sequence[str | Mapping[str, Any]],
    operator_to_nonce: Mapping[str, str],
    lexicon: str = "train",
    seed: int = 0,
) -> str:
    """Render diagnostic demonstrations followed by nonce-named commands.

    Only operators used in the target program are demonstrated.  Each
    demonstration contains an exact before/after state, so its meaning is
    identifiable without a persistent association between nonce and operator.
    """

    normalized = normalize_program(program)
    missing = sorted(set(normalized) - set(operator_to_nonce))
    if missing:
        raise ValueError(f"missing nonce aliases for operators: {missing}")
    used = tuple(dict.fromkeys(normalized))
    context = make_context(world, lexicon, seed)
    if world == "algebra":
        state_order = f"{context.object_left}, {context.object_right}"
    elif world == "provenance":
        state_order = f"{context.agent_a}, {context.agent_b}"
    else:
        state_order = (
            f"remaining credits, proof, {context.object_left}, "
            f"{context.object_right}, last decision"
        )
    demonstrations = [f"Calibration state order: {state_order}."]
    for before in _diagnostic_states(world, used):
        before_text = summarize_state(world, before, lexicon, seed, compact=True)
        outcomes = []
        for operator in used:
            after = apply_operator(world, before, operator)
            after_text = summarize_state(world, after, lexicon, seed, compact=True)
            outcomes.append(f"{operator_to_nonce[operator]} yielded [{after_text}]")
        demonstrations.append(f"Calibration: from [{before_text}], " + "; ".join(outcomes) + ".")
    start = summarize_state(world, initial_state, lexicon, seed)
    commands = ", then ".join(operator_to_nonce[operator] for operator in normalized)
    target = f"At the start of the target episode, {start}. Its commands were {commands}."
    return " ".join(demonstrations + [target])


__all__ = [
    "LEXICONS",
    "RENDERERS",
    "RenderContext",
    "make_context",
    "render_answer",
    "render_execution",
    "render_question",
    "render_queries",
    "render_renaming_episode",
    "render_trace",
    "summarize_state",
]
