from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import random
import shutil
import sys
import time
import zipfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from transformers import BertConfig, BertModel


AGENTS = ["ada", "ben", "cara", "davi"]
FACTS = ["red marker", "blue key", "closed bridge", "cloudy sample", "faulty sensor", "open gate"]
OPS = ["OBSERVE", "TELL", "IMAGINE", "INFER", "AUTHORIZE"]
OP_ID = {x: i for i, x in enumerate(OPS)}
MODES = ["none", "observed", "communicated", "imagined", "inferred"]
MODE_ID = {x: i for i, x in enumerate(MODES)}
ORIGIN_NONE = len(AGENTS)
NULL_AGENT = len(AGENTS)
NULL_FACT = len(FACTS)
CELL_COUNT = len(AGENTS) * len(FACTS)
LINKED_MOTIF = ("TELL", "INFER")
TRAIN_CODE_TOKENS = ["dax", "mip", "rav", "sol", "vex"]
TEST_CODE_TOKENS = ["krel", "nuv", "pax", "tob", "zesh"]
LABEL_KEYS = ["mode", "origin", "access", "direct", "authorized", "eligible"]
LABEL_DIMS = {"mode": len(MODES), "origin": len(AGENTS) + 1, "access": 2, "direct": 2, "authorized": 2, "eligible": 2}
CHECKPOINT_SCHEMA_VERSION = 3
RELEASE_VERSION = "0.3.1"


NATURAL_TEMPLATES = {
    "train": {
        "OBSERVE": ["{a} directly observed the {f}.", "{a} observed the {f} directly."],
        "TELL": ["{a} told {b} about the {f}.", "{a} gave {b} a report about the {f}."],
        "IMAGINE": ["{a} imagined the {f}.", "{a} pictured the {f} in imagination."],
        "INFER": ["from the {src}, {a} inferred the {f}.", "{a} used the {src} and inferred the {f}."],
        "AUTHORIZE": ["policy authorized {a} to act on the {f}.", "{a} was authorized by policy to use the {f}."],
    },
    "held": {
        "OBSERVE": ["the {f} was directly observed by {a}."],
        "TELL": ["about the {f}, {b} was told by {a}."],
        "IMAGINE": ["the {f} was imagined by {a}."],
        "INFER": ["the {f} was inferred by {a} from the {src}."],
        "AUTHORIZE": ["to act on the {f}, {a} was authorized by policy."],
    },
    "alt": {
        "OBSERVE": ["direct observation of the {f} was made by {a}."],
        "TELL": ["{b} learned about the {f} from {a}."],
        "IMAGINE": ["in imagination, {a} considered the {f}."],
        "INFER": ["using the {src}, the {f} was a conclusion reached by {a}."],
        "AUTHORIZE": ["policy gave {a} authorization to use the {f}."],
    },
}


@dataclass(frozen=True)
class Event:
    op: str
    actor: int
    fact: int
    other: int = -1
    source_fact: int = -1


@dataclass
class WorldState:
    mode: np.ndarray
    origin: np.ndarray
    authorized: np.ndarray

    def clone(self) -> "WorldState":
        return WorldState(self.mode.copy(), self.origin.copy(), self.authorized.copy())

    def fingerprint(self) -> str:
        payload = self.mode.tobytes() + self.origin.tobytes() + self.authorized.tobytes()
        return hashlib.sha256(payload).hexdigest()[:20]


@dataclass
class Record:
    text: str
    alt_text: str
    prefix_text: str
    next_text: str
    orbit_texts: list[str]
    events: list[tuple]
    alt_events: list[tuple]
    query_agent: int
    query_fact: int
    mode: int
    origin: int
    access: int
    direct: int
    authorized: int
    eligible: int
    full_mode: list[int]
    full_origin: list[int]
    full_authorized: list[int]
    transition_index: int
    transition_changed: int
    next_op: int
    next_actor: int
    next_fact: int
    next_other: int
    next_source_fact: int
    prefix_full_mode: list[int]
    prefix_full_origin: list[int]
    prefix_full_authorized: list[int]
    next_full_mode: list[int]
    next_full_origin: list[int]
    next_full_authorized: list[int]
    length: int
    signature: str
    op_counts: list[int]
    structural_hash: str
    alpha_hash: str
    state_hash: str
    surface_kind: str


@dataclass
class CausalPair:
    base: Record
    counterfactual: Record
    protected_agent: int
    protected_fact: int
    added_event: tuple
    family: str
    bank: str
    case_id: str


def empty_state() -> WorldState:
    shape = (len(AGENTS), len(FACTS))
    return WorldState(
        mode=np.zeros(shape, dtype=np.int64),
        origin=np.full(shape, ORIGIN_NONE, dtype=np.int64),
        authorized=np.zeros(shape, dtype=np.int64),
    )


def execute(events: list[Event]) -> WorldState | None:
    state = empty_state()
    for e in events:
        mode = state.mode[e.actor, e.fact]
        if e.op == "OBSERVE":
            if state.origin[e.actor, e.fact] == ORIGIN_NONE:
                state.origin[e.actor, e.fact] = e.actor
            state.mode[e.actor, e.fact] = MODE_ID["observed"]
        elif e.op == "TELL":
            if mode == MODE_ID["none"] or e.other < 0:
                return None
            if state.mode[e.other, e.fact] != MODE_ID["observed"]:
                state.mode[e.other, e.fact] = MODE_ID["communicated"]
                state.origin[e.other, e.fact] = state.origin[e.actor, e.fact]
        elif e.op == "IMAGINE":
            if mode == MODE_ID["none"]:
                state.mode[e.actor, e.fact] = MODE_ID["imagined"]
                state.origin[e.actor, e.fact] = e.actor
        elif e.op == "INFER":
            if e.source_fact < 0:
                return None
            source_mode = state.mode[e.actor, e.source_fact]
            if source_mode in (MODE_ID["none"], MODE_ID["imagined"]):
                return None
            if mode == MODE_ID["none"]:
                state.mode[e.actor, e.fact] = MODE_ID["inferred"]
                state.origin[e.actor, e.fact] = e.actor
        elif e.op == "AUTHORIZE":
            state.authorized[e.actor, e.fact] = 1
        else:
            raise ValueError(f"unknown operator {e.op}")
    return state


def state_labels(state: WorldState, agent: int, fact: int) -> dict[str, int]:
    mode = int(state.mode[agent, fact])
    auth = int(state.authorized[agent, fact])
    access = int(mode != MODE_ID["none"])
    direct = int(mode == MODE_ID["observed"])
    eligible = int(auth == 1 and mode in (MODE_ID["observed"], MODE_ID["communicated"], MODE_ID["inferred"]))
    return {
        "mode": mode,
        "origin": int(state.origin[agent, fact]),
        "access": access,
        "direct": direct,
        "authorized": auth,
        "eligible": eligible,
    }


def event_tuple(e: Event) -> tuple:
    return (e.op, e.actor, e.fact, e.other, e.source_fact)


def event_from_tuple(x: tuple | list) -> Event:
    return Event(str(x[0]), int(x[1]), int(x[2]), int(x[3]), int(x[4]))


def linked_motif(events: list[Event]) -> bool:
    for left, right in zip(events, events[1:]):
        if left.op == "TELL" and right.op == "INFER":
            if left.other == right.actor and left.fact == right.source_fact:
                return True
    return False


def alpha_canonical(events: list[Event], query_agent: int, query_fact: int) -> list[tuple]:
    agent_map: dict[int, int] = {}
    fact_map: dict[int, int] = {}

    def aidx(x: int) -> int:
        if x < 0:
            return -1
        if x not in agent_map:
            agent_map[x] = len(agent_map)
        return agent_map[x]

    def fidx(x: int) -> int:
        if x < 0:
            return -1
        if x not in fact_map:
            fact_map[x] = len(fact_map)
        return fact_map[x]

    out = []
    for e in events:
        out.append((e.op, aidx(e.actor), fidx(e.fact), aidx(e.other), fidx(e.source_fact)))
    out.append(("QUERY", aidx(query_agent), fidx(query_fact), -1, -1))
    return out


def hashes_for(events: list[Event], query_agent: int, query_fact: int) -> tuple[str, str]:
    concrete = [event_tuple(e) for e in events] + [("QUERY", query_agent, query_fact, -1, -1)]
    alpha = alpha_canonical(events, query_agent, query_fact)
    return (
        hashlib.sha256(json.dumps(concrete).encode()).hexdigest()[:20],
        hashlib.sha256(json.dumps(alpha).encode()).hexdigest()[:20],
    )


def random_codebook(rng: random.Random, tokens: list[str]) -> dict[str, str]:
    shuffled = tokens[:]
    rng.shuffle(shuffled)
    return {op: token for op, token in zip(OPS, shuffled)}


def render_event(e: Event, rng: random.Random, bank: str = "train", codebook: dict[str, str] | None = None) -> str:
    a = AGENTS[e.actor]
    b = AGENTS[e.other] if e.other >= 0 else ""
    f = FACTS[e.fact]
    src = FACTS[e.source_fact] if e.source_fact >= 0 else ""
    if codebook is not None:
        token = codebook[e.op]
        if e.op == "OBSERVE":
            return f"{a} {token} the {f}."
        if e.op == "TELL":
            return f"{a} {token} {b} about the {f}."
        if e.op == "IMAGINE":
            return f"{a} {token} the {f}."
        if e.op == "INFER":
            return f"from the {src}, {a} {token} the {f}."
        return f"policy {token} {a} to use the {f}."
    templates = NATURAL_TEMPLATES[bank][e.op]
    return rng.choice(templates).format(a=a, b=b, f=f, src=src)


def codebook_legend(codebook: dict[str, str]) -> str:
    meanings = {"OBSERVE": "observe", "TELL": "tell", "IMAGINE": "imagine", "INFER": "infer", "AUTHORIZE": "authorize"}
    return "legend: " + " ".join(f"{codebook[op]} means {meanings[op]}." for op in OPS)


def render_events(events: list[Event], rng: random.Random, bank: str = "train", codebook: dict[str, str] | None = None) -> str:
    body = " ".join(render_event(e, rng, bank=bank, codebook=codebook) for e in events)
    if codebook is None:
        return body
    return codebook_legend(codebook) + " " + body


def add_valid_event(rng: random.Random, state: WorldState) -> Event:
    available = [(a, f) for a in range(len(AGENTS)) for f in range(len(FACTS)) if state.mode[a, f] != MODE_ID["none"]]
    infer_sources = [(a, f) for a, f in available if state.mode[a, f] != MODE_ID["imagined"]]
    choices = ["OBSERVE", "IMAGINE", "AUTHORIZE"]
    if available:
        choices.append("TELL")
    if infer_sources:
        choices.append("INFER")
    op = rng.choice(choices)
    if op == "OBSERVE":
        return Event(op, rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
    if op == "IMAGINE":
        return Event(op, rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
    if op == "TELL":
        actor, fact = rng.choice(available)
        recipients = [x for x in range(len(AGENTS)) if x != actor]
        return Event(op, actor, fact, other=rng.choice(recipients))
    if op == "INFER":
        actor, source = rng.choice(infer_sources)
        targets = [f for f in range(len(FACTS)) if f != source]
        return Event(op, actor, rng.choice(targets), source_fact=source)
    return Event(op, rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))


def generate_random_trace(rng: random.Random, length: int, forbid_linked_motif: bool = True) -> tuple[list[Event], WorldState]:
    for _ in range(500):
        events: list[Event] = []
        state = empty_state()
        for _step in range(length):
            accepted = False
            for _attempt in range(50):
                e = add_valid_event(rng, state)
                candidate_events = events + [e]
                candidate = execute(candidate_events)
                if candidate is None:
                    continue
                if forbid_linked_motif and linked_motif(candidate_events):
                    continue
                events = candidate_events
                state = candidate
                accepted = True
                break
            if not accepted:
                break
        if len(events) == length:
            return events, state
    raise RuntimeError("could not generate a valid random trace")


def generate_motif_trace(rng: random.Random, length: int) -> tuple[list[Event], WorldState]:
    if length < 3:
        raise ValueError("motif trace requires length at least three")
    for _ in range(500):
        prefix_length = length - 3
        if prefix_length:
            prefix, prefix_state = generate_random_trace(rng, prefix_length, forbid_linked_motif=True)
        else:
            prefix, prefix_state = [], empty_state()
        candidates = []
        for source in range(len(AGENTS)):
            for receiver in range(len(AGENTS)):
                if source == receiver:
                    continue
                for source_fact in range(len(FACTS)):
                    if prefix_state.mode[source, source_fact] != MODE_ID["none"]:
                        continue
                    for target_fact in range(len(FACTS)):
                        if target_fact == source_fact or prefix_state.mode[receiver, target_fact] != MODE_ID["none"]:
                            continue
                        candidates.append((source, receiver, source_fact, target_fact))
        if not candidates:
            continue
        source, receiver, source_fact, target_fact = rng.choice(candidates)
        motif = [
            Event("OBSERVE", source, source_fact),
            Event("TELL", source, source_fact, other=receiver),
            Event("INFER", receiver, target_fact, source_fact=source_fact),
        ]
        events = prefix + motif
        state = execute(events)
        if state is not None and linked_motif(events):
            return events, state
    raise RuntimeError("could not generate linked motif trace")


def equivalent_path(events: list[Event], state: WorldState, rng: random.Random) -> list[Event]:
    target = state.fingerprint()
    indices = list(range(len(events)))
    rng.shuffle(indices)
    for idx in indices:
        candidate = events[: idx + 1] + [events[idx]] + events[idx + 1 :]
        result = execute(candidate)
        if result is not None and result.fingerprint() == target:
            events = candidate
            break
    for idx in range(len(events) - 1):
        candidate = events[:]
        candidate[idx], candidate[idx + 1] = candidate[idx + 1], candidate[idx]
        result = execute(candidate)
        if result is not None and result.fingerprint() == target:
            events = candidate
            break
    result = execute(events)
    if result is None or result.fingerprint() != target:
        raise AssertionError("equivalent path changed the executable state")
    return events


def choose_query_for_mode(
    state: WorldState,
    desired_mode: int,
    rng: random.Random,
    desired_authorized: int | None = None,
) -> tuple[int, int] | None:
    selector = state.mode == desired_mode
    if desired_authorized is not None:
        selector = selector & (state.authorized == desired_authorized)
    cells = list(zip(*np.where(selector)))
    if not cells:
        return None
    a, f = rng.choice(cells)
    return int(a), int(f)


def make_record(
    events: list[Event],
    state: WorldState,
    query_agent: int,
    query_fact: int,
    rng: random.Random,
    bank: str = "train",
    codebook: dict[str, str] | None = None,
    surface_kind: str = "natural",
) -> Record:
    alt_events = equivalent_path(events, state, rng)
    text = render_events(events, rng, bank=bank, codebook=codebook)
    alt_text = render_events(alt_events, rng, bank="alt", codebook=None)
    changing_indices = []
    for index in range(len(events)):
        before = execute(events[:index])
        after = execute(events[: index + 1])
        if before is not None and after is not None and before.fingerprint() != after.fingerprint():
            changing_indices.append(index)
    if not changing_indices:
        raise AssertionError("valid nonempty trace contains no state-changing event")
    split_at = rng.choice(changing_indices)
    prefix_events = events[:split_at]
    next_events = events[: split_at + 1]
    prefix_state = execute(prefix_events)
    next_state = execute(next_events)
    if prefix_state is None or next_state is None:
        raise AssertionError("valid trace produced an invalid prefix transition")
    next_event = events[split_at]
    prefix_text = render_events(prefix_events, rng, bank="train", codebook=codebook) if prefix_events else "empty story."
    next_text = render_events(next_events, rng, bank="train", codebook=codebook)
    orbit_texts = [
        render_events(events, random.Random(rng.randrange(2**31)), bank="train"),
        render_events(events, random.Random(rng.randrange(2**31)), bank="held"),
        render_events(alt_events, random.Random(rng.randrange(2**31)), bank="alt"),
    ]
    labels = state_labels(state, query_agent, query_fact)
    structural_hash, alpha_hash = hashes_for(events, query_agent, query_fact)
    op_counts = [sum(e.op == op for e in events) for op in OPS]
    return Record(
        text=text,
        alt_text=alt_text,
        prefix_text=prefix_text,
        next_text=next_text,
        orbit_texts=orbit_texts,
        events=[event_tuple(e) for e in events],
        alt_events=[event_tuple(e) for e in alt_events],
        query_agent=query_agent,
        query_fact=query_fact,
        mode=labels["mode"],
        origin=labels["origin"],
        access=labels["access"],
        direct=labels["direct"],
        authorized=labels["authorized"],
        eligible=labels["eligible"],
        full_mode=state.mode.reshape(-1).tolist(),
        full_origin=state.origin.reshape(-1).tolist(),
        full_authorized=state.authorized.reshape(-1).tolist(),
        transition_index=split_at,
        transition_changed=1,
        next_op=OP_ID[next_event.op],
        next_actor=next_event.actor,
        next_fact=next_event.fact,
        next_other=next_event.other,
        next_source_fact=next_event.source_fact,
        prefix_full_mode=prefix_state.mode.reshape(-1).tolist(),
        prefix_full_origin=prefix_state.origin.reshape(-1).tolist(),
        prefix_full_authorized=prefix_state.authorized.reshape(-1).tolist(),
        next_full_mode=next_state.mode.reshape(-1).tolist(),
        next_full_origin=next_state.origin.reshape(-1).tolist(),
        next_full_authorized=next_state.authorized.reshape(-1).tolist(),
        length=len(events),
        signature=">".join(e.op for e in events),
        op_counts=op_counts,
        structural_hash=structural_hash,
        alpha_hash=alpha_hash,
        state_hash=state.fingerprint(),
        surface_kind=surface_kind,
    )


def make_split(
    seed: int,
    n: int,
    lengths: tuple[int, ...],
    bank: str,
    motif: bool = False,
    codebook_tokens: list[str] | None = None,
    codebook_rate: float = 0.0,
    blocked_structural: set[str] | None = None,
    blocked_alpha: set[str] | None = None,
    partition_mod: int | None = None,
    partition_buckets: set[int] | None = None,
) -> list[Record]:
    if n % len(MODES):
        raise ValueError("split size must be divisible by five")
    rng = random.Random(seed)
    rows: list[Record] = []
    counts = Counter()
    attempts = 0
    per_mode = n // len(MODES)
    authorized_per_mode = int(round(0.4 * per_mode))
    desired_schedule = []
    for desired_mode in range(len(MODES)):
        desired_schedule.extend(
            [(desired_mode, 1)] * authorized_per_mode
            + [(desired_mode, 0)] * (per_mode - authorized_per_mode)
        )
    rng.shuffle(desired_schedule)
    blocked_structural = blocked_structural or set()
    blocked_alpha = blocked_alpha or set()
    local_structural: set[str] = set()
    for desired, desired_authorized in desired_schedule:
        while True:
            attempts += 1
            if attempts > n * 2000:
                raise RuntimeError(f"could not construct balanced split, counts={dict(counts)}")
            length = rng.choice(lengths)
            if desired_authorized == 1:
                if length < 2:
                    continue
                prefix_length = length - 1
                if motif:
                    if prefix_length < 3:
                        continue
                    events, state = generate_motif_trace(rng, prefix_length)
                else:
                    events, state = generate_random_trace(rng, prefix_length, forbid_linked_motif=True)
                query = choose_query_for_mode(state, desired, rng)
                if query is None:
                    continue
                insertion_positions = list(range(len(events) + 1))
                if motif:
                    forbidden_positions = {
                        index + 1
                        for index, (left, right) in enumerate(zip(events, events[1:]))
                        if left.op == "TELL"
                        and right.op == "INFER"
                        and left.other == right.actor
                        and left.fact == right.source_fact
                    }
                    insertion_positions = [position for position in insertion_positions if position not in forbidden_positions]
                insertion = rng.choice(insertion_positions)
                events = events[:insertion] + [Event("AUTHORIZE", query[0], query[1])] + events[insertion:]
                state = execute(events)
                if state is None:
                    continue
            else:
                events, state = generate_motif_trace(rng, length) if motif else generate_random_trace(rng, length, forbid_linked_motif=True)
                query = choose_query_for_mode(state, desired, rng, desired_authorized=0)
            if query is None:
                continue
            use_codebook = codebook_tokens is not None and rng.random() < codebook_rate
            codebook = random_codebook(rng, codebook_tokens) if use_codebook else None
            surface_kind = "codebook" if use_codebook else bank
            record = make_record(events, state, query[0], query[1], rng, bank=bank, codebook=codebook, surface_kind=surface_kind)
            if partition_mod is not None:
                if not partition_buckets:
                    raise ValueError("partition_buckets must be supplied with partition_mod")
                bucket = int(record.alpha_hash, 16) % partition_mod
                if bucket not in partition_buckets:
                    continue
            if record.structural_hash in blocked_structural or record.alpha_hash in blocked_alpha:
                continue
            if record.structural_hash in local_structural:
                continue
            rows.append(record)
            local_structural.add(record.structural_hash)
            counts[(desired, desired_authorized)] += 1
            break
    rng.shuffle(rows)
    return rows


CAUSAL_FAMILIES = ["OBSERVE_UPGRADE", "TELL_WRITE", "IMAGINE_WRITE", "INFER_WRITE", "AUTHORIZE_WRITE"]


def event_write_cell(event: Event) -> tuple[int, int]:
    return (event.other, event.fact) if event.op == "TELL" else (event.actor, event.fact)


def add_causal_distractors(
    rng: random.Random,
    events: list[Event],
    forbidden_cells: set[tuple[int, int]],
    count: int,
) -> list[Event]:
    result = events[:]
    used: set[tuple[str, int, int]] = set()
    for _ in range(count):
        candidates = []
        for actor in range(len(AGENTS)):
            for fact in range(len(FACTS)):
                if (actor, fact) in forbidden_cells:
                    continue
                for op in ("OBSERVE", "IMAGINE", "AUTHORIZE"):
                    key = (op, actor, fact)
                    if key not in used:
                        candidates.append(Event(op, actor, fact))
        rng.shuffle(candidates)
        for event in candidates:
            proposal = result + [event]
            if execute(proposal) is not None:
                result = proposal
                used.add((event.op, event.actor, event.fact))
                break
        else:
            raise RuntimeError("could not add a causal distractor")
    return result


def make_causal_pairs(
    seed: int,
    n: int,
    bank: str,
    difficulty: str,
    blocked_case_ids: set[str] | None = None,
    blocked_structural: set[str] | None = None,
    blocked_alpha: set[str] | None = None,
) -> list[CausalPair]:
    if n % len(CAUSAL_FAMILIES):
        raise ValueError("causal bank size must be divisible by five")
    if difficulty not in ("id", "ood"):
        raise ValueError("causal difficulty must be id or ood")
    rng = random.Random(seed)
    pairs: list[CausalPair] = []
    blocked = set(blocked_case_ids or set())
    blocked_structures = set(blocked_structural or set())
    del blocked_alpha
    local_ids: set[str] = set()
    local_structures: set[str] = set()
    schedule = CAUSAL_FAMILIES * (n // len(CAUSAL_FAMILIES))
    rng.shuffle(schedule)
    attempts = 0
    for family in schedule:
        while True:
            attempts += 1
            if attempts > n * 500:
                raise RuntimeError("could not construct a unique balanced causal bank")
            actor = rng.randrange(len(AGENTS))
            fact = rng.randrange(len(FACTS))
            other = rng.choice([value for value in range(len(AGENTS)) if value != actor])
            source_fact = rng.choice([value for value in range(len(FACTS)) if value != fact])
            if family == "OBSERVE_UPGRADE":
                prefix = [Event("OBSERVE", actor, fact), Event("TELL", actor, fact, other=other)]
                added = Event("OBSERVE", other, fact)
                query_agent, query_fact = other, fact
                forbidden = {(actor, fact), (other, fact)}
            elif family == "TELL_WRITE":
                prefix = [Event("OBSERVE", actor, fact)]
                added = Event("TELL", actor, fact, other=other)
                query_agent, query_fact = other, fact
                forbidden = {(actor, fact), (other, fact)}
            elif family == "IMAGINE_WRITE":
                prefix = []
                added = Event("IMAGINE", actor, fact)
                query_agent, query_fact = actor, fact
                forbidden = {(actor, fact)}
            elif family == "INFER_WRITE":
                prefix = [Event("OBSERVE", actor, source_fact)]
                added = Event("INFER", actor, fact, source_fact=source_fact)
                query_agent, query_fact = actor, fact
                forbidden = {(actor, fact), (actor, source_fact)}
            else:
                prefix = [Event("OBSERVE", actor, fact)]
                added = Event("AUTHORIZE", actor, fact)
                query_agent, query_fact = actor, fact
                forbidden = {(actor, fact)}
            target_counter_length = rng.choice((2, 3, 4)) if difficulty == "id" else rng.choice((5, 6, 7))
            distractor_count = target_counter_length - len(prefix) - 1
            if distractor_count < 0:
                continue
            base_events = add_causal_distractors(rng, prefix, forbidden, distractor_count)
            rng.shuffle(base_events)
            base_state = execute(base_events)
            if base_state is None:
                continue
            counter_events = base_events + [added]
            counter_state = execute(counter_events)
            if counter_state is None:
                continue
            before = state_labels(base_state, query_agent, query_fact)
            after = state_labels(counter_state, query_agent, query_fact)
            if all(before[key] == after[key] for key in ("mode", "origin", "authorized")):
                continue
            payload = [family, [event_tuple(event) for event in base_events], event_tuple(added), query_agent, query_fact]
            case_id = hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:24]
            if case_id in blocked or case_id in local_ids:
                continue
            untouched = [
                (a, f)
                for a in range(len(AGENTS))
                for f in range(len(FACTS))
                if (a, f) != event_write_cell(added)
            ]
            protected_agent, protected_fact = rng.choice(untouched)
            base = make_record(
                base_events,
                base_state,
                query_agent,
                query_fact,
                rng,
                bank=bank,
                surface_kind=f"causal_{difficulty}_base",
            )
            counter = make_record(
                counter_events,
                counter_state,
                query_agent,
                query_fact,
                rng,
                bank=bank,
                surface_kind=f"causal_{difficulty}_counterfactual",
            )
            candidate_structures = {base.structural_hash, counter.structural_hash}
            if candidate_structures & (blocked_structures | local_structures):
                continue
            pairs.append(
                CausalPair(
                    base,
                    counter,
                    protected_agent,
                    protected_fact,
                    event_tuple(added),
                    family,
                    difficulty,
                    case_id,
                )
            )
            local_ids.add(case_id)
            local_structures.update(candidate_structures)
            break
    return pairs


def tokenize(text: str) -> list[str]:
    for c in ".,?:'":
        text = text.replace(c, f" {c} ")
    return text.lower().split()


def build_vocab(groups: Iterable[Iterable[Record]]) -> dict[str, int]:
    tokens = {"[PAD]", "[UNK]", "[CLS]"}
    for group in groups:
        for row in group:
            for text in [row.text, row.alt_text, row.prefix_text, row.next_text, *row.orbit_texts]:
                tokens.update(tokenize(text))
    return {token: i for i, token in enumerate(sorted(tokens))}


def encode(text: str, vocab: dict[str, int], max_len: int) -> tuple[list[int], list[int]]:
    ids = [vocab["[CLS]"]] + [vocab.get(token, vocab["[UNK]"]) for token in tokenize(text)]
    ids = ids[:max_len]
    mask = [1] * len(ids)
    ids += [vocab["[PAD]"]] * (max_len - len(ids))
    mask += [0] * (max_len - len(mask))
    return ids, mask


class TraceDataset(Dataset):
    def __init__(self, records: list[Record], vocab: dict[str, int], max_len: int):
        self.records = records
        self.rows = []
        for row in records:
            ids, mask = encode(row.text, vocab, max_len)
            alt_ids, alt_mask = encode(row.alt_text, vocab, max_len)
            prefix_ids, prefix_mask = encode(row.prefix_text, vocab, max_len)
            next_ids, next_mask = encode(row.next_text, vocab, max_len)
            self.rows.append(
                {
                    "ids": ids,
                    "mask": mask,
                    "alt_ids": alt_ids,
                    "alt_mask": alt_mask,
                    "prefix_ids": prefix_ids,
                    "prefix_mask": prefix_mask,
                    "next_ids": next_ids,
                    "next_mask": next_mask,
                    "query_agent": row.query_agent,
                    "query_fact": row.query_fact,
                    "mode": row.mode,
                    "origin": row.origin,
                    "access": row.access,
                    "direct": row.direct,
                    "authorized": row.authorized,
                    "eligible": row.eligible,
                    "full_mode": row.full_mode,
                    "full_origin": row.full_origin,
                    "full_authorized": row.full_authorized,
                    "transition_index": row.transition_index,
                    "transition_changed": row.transition_changed,
                    "next_op": row.next_op,
                    "next_actor": row.next_actor,
                    "next_fact": row.next_fact,
                    "next_other": row.next_other,
                    "next_source_fact": row.next_source_fact,
                    "prefix_full_mode": row.prefix_full_mode,
                    "prefix_full_origin": row.prefix_full_origin,
                    "prefix_full_authorized": row.prefix_full_authorized,
                    "next_full_mode": row.next_full_mode,
                    "next_full_origin": row.next_full_origin,
                    "next_full_authorized": row.next_full_authorized,
                }
            )

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        return {key: torch.tensor(value, dtype=torch.long) for key, value in self.rows[index].items()}


class OSLBert(nn.Module):
    def __init__(self, config: BertConfig):
        super().__init__()
        self.config = config
        self.config._attn_implementation = "eager"
        self.backbone = BertModel(config, add_pooling_layer=False)
        self.agent_embedding = nn.Embedding(len(AGENTS), config.hidden_size)
        self.fact_embedding = nn.Embedding(len(FACTS), config.hidden_size)
        self.slot_attention = nn.MultiheadAttention(
            config.hidden_size,
            config.num_attention_heads,
            dropout=config.attention_probs_dropout_prob,
            batch_first=True,
        )
        self.slot_attention_norm = nn.LayerNorm(config.hidden_size)
        self.slot_mlp = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Linear(config.hidden_size, config.hidden_size),
        )
        self.slot_output_norm = nn.LayerNorm(config.hidden_size)
        self.heads = nn.ModuleDict({key: nn.Linear(config.hidden_size, dim) for key, dim in LABEL_DIMS.items()})
        self.event_op_embedding = nn.Embedding(len(OPS), config.hidden_size)
        self.event_agent_embedding = nn.Embedding(len(AGENTS) + 1, config.hidden_size)
        self.event_fact_embedding = nn.Embedding(len(FACTS) + 1, config.hidden_size)
        self.write_locator = nn.Sequential(
            nn.Linear(config.hidden_size * 5, config.hidden_size),
            nn.GELU(),
            nn.Linear(config.hidden_size, config.hidden_size),
        )
        self.transition_mlp = nn.Sequential(
            nn.Linear(config.hidden_size * 7, config.hidden_size * 2),
            nn.GELU(),
            nn.Linear(config.hidden_size * 2, config.hidden_size),
        )
        self.transition_norm = nn.LayerNorm(config.hidden_size)

    def encode_story(self, ids: torch.Tensor, mask: torch.Tensor, output_hidden_states: bool = False):
        output = self.backbone(
            input_ids=ids,
            attention_mask=mask,
            output_hidden_states=output_hidden_states,
            return_dict=True,
        )
        token_states = output.last_hidden_state
        device = token_states.device
        agent = torch.arange(len(AGENTS), device=device).repeat_interleave(len(FACTS))
        fact = torch.arange(len(FACTS), device=device).repeat(len(AGENTS))
        queries = self.agent_embedding(agent) + self.fact_embedding(fact)
        queries = queries[None, :, :].expand(len(ids), -1, -1)
        attended, _ = self.slot_attention(
            queries,
            token_states,
            token_states,
            key_padding_mask=mask == 0,
            need_weights=False,
        )
        slots = self.slot_attention_norm(queries + attended)
        slots = self.slot_output_norm(slots + self.slot_mlp(slots))
        return token_states[:, 0], slots, output.hidden_states

    def predict_cell_from_slots(
        self,
        slots: torch.Tensor,
        agent: torch.Tensor,
        fact: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        index = agent * len(FACTS) + fact
        h = slots[torch.arange(len(slots), device=slots.device), index]
        return {key: head(h) for key, head in self.heads.items()}

    def predict_all_from_slots(self, slots: torch.Tensor) -> dict[str, torch.Tensor]:
        return {key: head(slots) for key, head in self.heads.items()}

    def predict_cell(self, slots: torch.Tensor, agent: torch.Tensor, fact: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.predict_cell_from_slots(slots, agent, fact)

    def predict_all(self, slots: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.predict_all_from_slots(slots)

    def transition_workspace(
        self,
        slots: torch.Tensor,
        op: torch.Tensor,
        actor: torch.Tensor,
        fact: torch.Tensor,
        other: torch.Tensor,
        source_fact: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Apply one typed, operand-conditioned event to one affected agent-fact slot."""
        safe_other = torch.where(other >= 0, other, torch.full_like(other, NULL_AGENT))
        safe_source = torch.where(source_fact >= 0, source_fact, torch.full_like(source_fact, NULL_FACT))
        affected_agent = torch.where(op == OP_ID["TELL"], safe_other, actor)
        if bool((affected_agent >= len(AGENTS)).any()):
            raise ValueError("TELL transition is missing a recipient")
        affected_index = affected_agent * len(FACTS) + fact
        batch_index = torch.arange(len(slots), device=slots.device)
        target = slots[batch_index, affected_index]
        infer_source_index = actor * len(FACTS) + safe_source.clamp_max(len(FACTS) - 1)
        tell_source_index = actor * len(FACTS) + fact
        source_index = torch.where(
            op == OP_ID["TELL"],
            tell_source_index,
            torch.where(op == OP_ID["INFER"], infer_source_index, affected_index),
        )
        source = slots[batch_index, source_index]
        features = torch.cat(
            [
                target,
                source,
                self.event_op_embedding(op),
                self.event_agent_embedding(actor),
                self.event_agent_embedding(safe_other),
                self.event_fact_embedding(fact),
                self.event_fact_embedding(safe_source),
            ],
            dim=-1,
        )
        updated_target = self.transition_norm(target + self.transition_mlp(features))
        write_mask = nn.functional.one_hot(affected_index, num_classes=CELL_COUNT).to(slots.dtype).unsqueeze(-1)
        updated = slots * (1.0 - write_mask) + updated_target[:, None, :] * write_mask
        return updated, affected_index

    def free_write_transition(
        self,
        slots: torch.Tensor,
        op: torch.Tensor,
        actor: torch.Tensor,
        fact: torch.Tensor,
        other: torch.Tensor,
        source_fact: torch.Tensor,
        hard: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict the write address from operands, then apply the event proposal."""
        safe_other = torch.where(other >= 0, other, torch.full_like(other, NULL_AGENT))
        safe_source = torch.where(source_fact >= 0, source_fact, torch.full_like(source_fact, NULL_FACT))
        event_parts = [
            self.event_op_embedding(op),
            self.event_agent_embedding(actor),
            self.event_agent_embedding(safe_other),
            self.event_fact_embedding(fact),
            self.event_fact_embedding(safe_source),
        ]
        location_query = self.write_locator(torch.cat(event_parts, dim=-1))
        device = slots.device
        cell_agents = torch.arange(len(AGENTS), device=device).repeat_interleave(len(FACTS))
        cell_facts = torch.arange(len(FACTS), device=device).repeat(len(AGENTS))
        cell_keys = self.agent_embedding(cell_agents) + self.fact_embedding(cell_facts)
        location_scores = torch.einsum("bd,cd->bc", location_query, cell_keys) / math.sqrt(slots.shape[-1])
        predicted_index = location_scores.argmax(dim=-1)
        if hard:
            write_weights = nn.functional.one_hot(predicted_index, num_classes=CELL_COUNT).to(slots.dtype)
        else:
            write_weights = nn.functional.softmax(location_scores, dim=-1).to(slots.dtype)

        infer_source_index = actor * len(FACTS) + safe_source.clamp_max(len(FACTS) - 1)
        tell_source_index = actor * len(FACTS) + fact
        oracle_write_agent = torch.where(op == OP_ID["TELL"], safe_other, actor)
        oracle_write_index = oracle_write_agent * len(FACTS) + fact
        source_index = torch.where(
            op == OP_ID["TELL"],
            tell_source_index,
            torch.where(op == OP_ID["INFER"], infer_source_index, oracle_write_index),
        )
        source = slots[torch.arange(len(slots), device=device), source_index]
        expanded_parts = [part[:, None, :].expand(-1, CELL_COUNT, -1) for part in event_parts]
        source_expanded = source[:, None, :].expand(-1, CELL_COUNT, -1)
        features = torch.cat([slots, source_expanded, *expanded_parts], dim=-1)
        proposals = self.transition_norm(slots + self.transition_mlp(features))
        weights = write_weights.unsqueeze(-1)
        updated = slots * (1.0 - weights) + proposals * weights
        return updated, predicted_index, location_scores


def set_seed(seed: int, deterministic: bool = True) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.use_deterministic_algorithms(True, warn_only=False)
        if hasattr(torch.backends, "cudnn"):
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.allow_tf32 = False
        if hasattr(torch.backends, "cuda"):
            torch.backends.cuda.matmul.allow_tf32 = False
            if hasattr(torch.backends.cuda, "enable_flash_sdp"):
                torch.backends.cuda.enable_flash_sdp(False)
            if hasattr(torch.backends.cuda, "enable_mem_efficient_sdp"):
                torch.backends.cuda.enable_mem_efficient_sdp(False)
            if hasattr(torch.backends.cuda, "enable_math_sdp"):
                torch.backends.cuda.enable_math_sdp(True)
    else:
        torch.use_deterministic_algorithms(False)


def move_batch(batch: dict[str, torch.Tensor], device: torch.device) -> dict[str, torch.Tensor]:
    return {key: value.to(device, non_blocking=device.type == "cuda") for key, value in batch.items()}


def label_class_weights(records: list[Record], device: torch.device) -> dict[str, torch.Tensor]:
    out = {}
    for key, dim in LABEL_DIMS.items():
        values = np.array([getattr(row, key) for row in records], dtype=np.int64)
        counts = np.bincount(values, minlength=dim).astype(np.float64)
        weights = np.sqrt(counts.sum() / np.maximum(counts, 1.0))
        weights = np.clip(weights / weights.mean(), 0.25, 4.0)
        out[key] = torch.tensor(weights, dtype=torch.float32, device=device)
    return out


def query_loss(
    logits: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    class_weights: dict[str, torch.Tensor],
) -> torch.Tensor:
    weights = {"mode": 1.0, "origin": 0.55, "access": 0.3, "direct": 0.3, "authorized": 0.3, "eligible": 0.3}
    return sum(
        weights[key] * nn.functional.cross_entropy(logits[key], batch[key], weight=class_weights[key])
        for key in LABEL_KEYS
    )


def full_state_class_weights(records: list[Record], device: torch.device) -> dict[str, torch.Tensor]:
    values = {
        "mode": np.array([x for row in records for x in row.full_mode]),
        "origin": np.array([x for row in records for x in row.full_origin]),
        "authorized": np.array([x for row in records for x in row.full_authorized]),
    }
    dims = {"mode": len(MODES), "origin": len(AGENTS) + 1, "authorized": 2}
    out = {}
    for key, array in values.items():
        counts = np.bincount(array, minlength=dims[key]).astype(np.float64)
        weights = np.sqrt(counts.sum() / np.maximum(counts, 1.0))
        weights = weights / weights.mean()
        weights = np.clip(weights, 0.25, 4.0)
        out[key] = torch.tensor(weights, dtype=torch.float32, device=device)
    return out


def full_state_loss_for_targets(
    logits: dict[str, torch.Tensor],
    mode_target: torch.Tensor,
    origin_target: torch.Tensor,
    authorized_target: torch.Tensor,
    class_weights: dict[str, torch.Tensor],
) -> torch.Tensor:
    mode = nn.functional.cross_entropy(logits["mode"].flatten(0, 1), mode_target.flatten(), weight=class_weights["mode"])
    origin = nn.functional.cross_entropy(logits["origin"].flatten(0, 1), origin_target.flatten(), weight=class_weights["origin"])
    auth = nn.functional.cross_entropy(
        logits["authorized"].flatten(0, 1),
        authorized_target.flatten(),
        weight=class_weights["authorized"],
    )
    return mode + 0.55 * origin + 0.35 * auth


def full_state_loss(
    logits: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    class_weights: dict[str, torch.Tensor],
) -> torch.Tensor:
    return full_state_loss_for_targets(
        logits,
        batch["full_mode"],
        batch["full_origin"],
        batch["full_authorized"],
        class_weights,
    )


def equivalence_loss(z: torch.Tensor, z_alt: torch.Tensor, temperature: float = 0.12) -> torch.Tensor:
    left = nn.functional.normalize(z, dim=-1)
    right = nn.functional.normalize(z_alt, dim=-1)
    logits = left @ right.T / temperature
    labels = torch.arange(len(z), device=z.device)
    return 0.5 * (nn.functional.cross_entropy(logits, labels) + nn.functional.cross_entropy(logits.T, labels))


def slot_transition_loss(
    model: OSLBert,
    prefix_slots: torch.Tensor,
    next_slots: torch.Tensor,
    batch: dict[str, torch.Tensor],
    class_weights: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    """Train a typed local write and penalize movement in every untouched slot."""
    if batch["next_op"].ndim != 1 or len(batch["next_op"]) != len(prefix_slots):
        raise ValueError("next_op must contain one operator index per representation")
    if bool(((batch["next_op"] < 0) | (batch["next_op"] >= len(OPS))).any()):
        raise ValueError("next_op contains an invalid operator index")
    with torch.autocast(device_type=prefix_slots.device.type, enabled=False):
        prefix = prefix_slots.float()
        target = next_slots.float().detach()
        predicted, _predicted_index, location_scores = model.free_write_transition(
            prefix,
            batch["next_op"],
            batch["next_actor"],
            batch["next_fact"],
            batch["next_other"],
            batch["next_source_fact"],
        )
        safe_other = torch.where(
            batch["next_other"] >= 0,
            batch["next_other"],
            torch.full_like(batch["next_other"], NULL_AGENT),
        )
        affected_agent = torch.where(batch["next_op"] == OP_ID["TELL"], safe_other, batch["next_actor"])
        affected_index = affected_agent * len(FACTS) + batch["next_fact"]
        batch_index = torch.arange(len(prefix), device=prefix.device)
        predicted_affected = predicted[batch_index, affected_index]
        target_affected = target[batch_index, affected_index]
        affected_cosine = 1.0 - nn.functional.cosine_similarity(predicted_affected, target_affected, dim=-1).mean()
        affected_mse = nn.functional.mse_loss(predicted_affected, target_affected)
        affected_mask = nn.functional.one_hot(affected_index, num_classes=CELL_COUNT).bool()
        unchanged_prefix = prefix[~affected_mask]
        unchanged_target = target[~affected_mask]
        untouched_cosine = 1.0 - nn.functional.cosine_similarity(unchanged_prefix, unchanged_target, dim=-1).mean()
        semantic = full_state_loss_for_targets(
            model.predict_all_from_slots(predicted),
            batch["next_full_mode"],
            batch["next_full_origin"],
            batch["next_full_authorized"],
            class_weights,
        )
        locator = nn.functional.cross_entropy(location_scores, affected_index)
        total = affected_cosine + 0.20 * affected_mse + 0.25 * untouched_cosine + 0.35 * semantic + 0.50 * locator
        return total, {
            "affected_cosine": affected_cosine.detach(),
            "affected_mse": affected_mse.detach(),
            "untouched_cosine": untouched_cosine.detach(),
            "semantic": semantic.detach(),
            "write_locator": locator.detach(),
        }


@torch.no_grad()
def collect_predictions(
    model: OSLBert,
    dataset: TraceDataset,
    device: torch.device,
    batch_size: int,
    collect_layers: bool = False,
    collect_alt: bool = False,
) -> dict:
    model.eval()
    labels = {key: [] for key in LABEL_KEYS}
    preds = {key: [] for key in LABEL_KEYS}
    full_labels = {"mode": [], "origin": [], "authorized": []}
    full_preds = {"mode": [], "origin": [], "authorized": []}
    zs = []
    alt_zs = []
    workspace_chunks = []
    alt_workspace_chunks = []
    layer_chunks = None
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    for raw_batch in loader:
        batch = move_batch(raw_batch, device)
        z, slots, hidden = model.encode_story(batch["ids"], batch["mask"], output_hidden_states=collect_layers)
        logits = model.predict_cell(slots, batch["query_agent"], batch["query_fact"])
        all_logits = model.predict_all(slots)
        for key in LABEL_KEYS:
            labels[key].append(batch[key].cpu().numpy())
            preds[key].append(logits[key].argmax(-1).cpu().numpy())
        for key in full_labels:
            full_labels[key].append(batch[f"full_{key}"].cpu().numpy())
            full_preds[key].append(all_logits[key].argmax(-1).cpu().numpy())
        zs.append(z.cpu().numpy())
        if collect_alt:
            workspace_chunks.append(slots.float().cpu().numpy())
            alt_z, alt_slots, _ = model.encode_story(batch["alt_ids"], batch["alt_mask"], output_hidden_states=False)
            alt_zs.append(alt_z.cpu().numpy())
            alt_workspace_chunks.append(alt_slots.float().cpu().numpy())
        if collect_layers:
            if layer_chunks is None:
                layer_chunks = [[] for _ in hidden]
            for index, layer in enumerate(hidden):
                layer_chunks[index].append(layer[:, 0].cpu().numpy())
    return {
        "labels": {key: np.concatenate(value) for key, value in labels.items()},
        "preds": {key: np.concatenate(value) for key, value in preds.items()},
        "full_labels": {key: np.concatenate(value) for key, value in full_labels.items()},
        "full_preds": {key: np.concatenate(value) for key, value in full_preds.items()},
        "z": np.concatenate(zs),
        "alt_z": np.concatenate(alt_zs) if alt_zs else None,
        "workspace": np.concatenate(workspace_chunks) if workspace_chunks else None,
        "alt_workspace": np.concatenate(alt_workspace_chunks) if alt_workspace_chunks else None,
        "layers": [np.concatenate(value) for value in layer_chunks] if layer_chunks is not None else None,
    }


def metrics_from_collection(collected: dict) -> dict[str, float]:
    labels = collected["labels"]
    preds = collected["preds"]
    metrics = {}
    correct = []
    for key in LABEL_KEYS:
        metrics[f"{key}_accuracy"] = float(accuracy_score(labels[key], preds[key]))
        correct.append(labels[key] == preds[key])
    metrics["mode_balanced_accuracy"] = float(balanced_accuracy_score(labels["mode"], preds["mode"]))
    metrics["joint_six_accuracy"] = float(np.logical_and.reduce(correct).mean())
    full_labels = collected["full_labels"]
    full_preds = collected["full_preds"]
    metrics["full_mode_balanced_accuracy"] = float(
        balanced_accuracy_score(full_labels["mode"].reshape(-1), full_preds["mode"].reshape(-1))
    )
    active = full_labels["mode"] != MODE_ID["none"]
    metrics["active_mode_accuracy"] = float((full_labels["mode"][active] == full_preds["mode"][active]).mean()) if active.any() else 0.0
    state_correct = (
        (full_labels["mode"] == full_preds["mode"]).all(axis=1)
        & (full_labels["origin"] == full_preds["origin"]).all(axis=1)
        & (full_labels["authorized"] == full_preds["authorized"]).all(axis=1)
    )
    metrics["full_state_exact"] = float(state_correct.mean())
    return metrics


def evaluate_model(model: OSLBert, dataset: TraceDataset, device: torch.device, batch_size: int) -> dict[str, float]:
    return metrics_from_collection(collect_predictions(model, dataset, device, batch_size))


def train_arm(
    arm: str,
    seed: int,
    model_config: BertConfig,
    train_ds: TraceDataset,
    val_ds: TraceDataset,
    train_records: list[Record],
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    deterministic: bool,
) -> tuple[OSLBert, list[dict]]:
    set_seed(seed, deterministic=deterministic)
    model = OSLBert(copy.deepcopy(model_config)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    class_weights = full_state_class_weights(train_records, device)
    query_weights = label_class_weights(train_records, device)
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    best_score = -1.0
    best_epoch = -1
    best_state = None
    history = []
    for epoch in range(epochs):
        generator = torch.Generator()
        generator.manual_seed(seed * 1000 + epoch)
        loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, generator=generator, num_workers=0, pin_memory=use_amp)
        model.train()
        loss_sum = 0.0
        transition_sums = defaultdict(float)
        examples_seen = 0
        for raw_batch in loader:
            batch = move_batch(raw_batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                z, slots, _ = model.encode_story(batch["ids"], batch["mask"])
                logits = model.predict_cell(slots, batch["query_agent"], batch["query_fact"])
                loss = query_loss(logits, batch, query_weights)
                if arm in ("state_supervised", "equivalence", "slot_operator"):
                    loss = loss + 0.3 * full_state_loss(model.predict_all(slots), batch, class_weights)
                if arm in ("equivalence", "slot_operator"):
                    _z_alt, slots_alt, _ = model.encode_story(batch["alt_ids"], batch["alt_mask"])
                    loss = loss + 0.08 * equivalence_loss(slots.flatten(1), slots_alt.flatten(1))
                if arm == "slot_operator":
                    _z_prefix, prefix_slots, _ = model.encode_story(batch["prefix_ids"], batch["prefix_mask"])
                    _z_next, next_slots, _ = model.encode_story(batch["next_ids"], batch["next_mask"])
                    transition_value, transition_parts = slot_transition_loss(
                        model,
                        prefix_slots,
                        next_slots,
                        batch,
                        class_weights,
                    )
                    loss = loss + 0.12 * transition_value
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            loss_sum += float(loss.detach().cpu()) * len(batch["ids"])
            if arm == "slot_operator":
                for key, value in transition_parts.items():
                    transition_sums[key] += float(value.cpu()) * len(batch["ids"])
            examples_seen += len(batch["ids"])
        val_metrics = evaluate_model(model, val_ds, device, batch_size)
        score = 0.60 * val_metrics["mode_balanced_accuracy"] + 0.40 * val_metrics["joint_six_accuracy"]
        history_row = {
            "epoch": epoch + 1,
            "train_loss": loss_sum / max(examples_seen, 1),
            "selection_score": score,
            **val_metrics,
        }
        if arm == "slot_operator":
            history_row["transition_components"] = {
                key: value / max(examples_seen, 1) for key, value in transition_sums.items()
            }
        history.append(history_row)
        print(
            f"arm={arm} seed={seed} epoch={epoch + 1}/{epochs} "
            f"loss={loss_sum / max(examples_seen, 1):.4f} "
            f"val_mode_balanced={val_metrics['mode_balanced_accuracy']:.4f} "
            f"val_joint={val_metrics['joint_six_accuracy']:.4f} selection={score:.4f}",
            flush=True,
        )
        if score > best_score:
            best_score = score
            best_epoch = epoch + 1
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if best_state is None:
        raise RuntimeError("training produced no checkpoint")
    for row in history:
        row["selected"] = row["epoch"] == best_epoch
    model.load_state_dict(best_state)
    return model, history


class ConstantPredictor:
    def __init__(self, value: int):
        self.value = int(value)

    def predict(self, x) -> np.ndarray:
        return np.full(x.shape[0], self.value, dtype=np.int64)


def fit_classifier(x, y: np.ndarray, seed: int = 0):
    unique = np.unique(y)
    if len(unique) == 1:
        return ConstantPredictor(int(unique[0]))
    del seed
    model = RidgeClassifier(alpha=1.0, class_weight="balanced", solver="lsqr", tol=1e-6)
    model.fit(x, y)
    return model


def baseline_text(row: Record, include_story: bool = True) -> str:
    query = f"query agent {AGENTS[row.query_agent]} fact {FACTS[row.query_fact]}"
    return f"{row.text} {query}" if include_story else query


def labels_matrix(records: list[Record]) -> dict[str, np.ndarray]:
    return {key: np.array([getattr(row, key) for row in records], dtype=np.int64) for key in LABEL_KEYS}


def score_baseline_predictions(labels: dict[str, np.ndarray], preds: dict[str, np.ndarray]) -> dict[str, float]:
    out = {f"{key}_accuracy": float(accuracy_score(labels[key], preds[key])) for key in LABEL_KEYS}
    out["mode_balanced_accuracy"] = float(balanced_accuracy_score(labels["mode"], preds["mode"]))
    out["joint_six_accuracy"] = float(np.logical_and.reduce([labels[key] == preds[key] for key in LABEL_KEYS]).mean())
    return out


def text_baseline(
    train: list[Record],
    splits: dict[str, list[Record]],
    kind: str,
    include_story: bool = True,
    shuffle_labels: bool = False,
    seed: int = 991,
) -> dict[str, dict[str, float]]:
    if kind == "word":
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True, max_features=30000)
    elif kind == "char":
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True, max_features=40000)
    else:
        raise ValueError(kind)
    train_text = [baseline_text(row, include_story=include_story) for row in train]
    x_train = vectorizer.fit_transform(train_text)
    train_labels = labels_matrix(train)
    rng = np.random.default_rng(seed)
    models = {}
    for key in LABEL_KEYS:
        y = train_labels[key].copy()
        if shuffle_labels:
            rng.shuffle(y)
        models[key] = fit_classifier(x_train, y, seed=seed)
    results = {}
    for split, rows in splits.items():
        x = vectorizer.transform([baseline_text(row, include_story=include_story) for row in rows])
        labels = labels_matrix(rows)
        preds = {key: models[key].predict(x) for key in LABEL_KEYS}
        results[split] = score_baseline_predictions(labels, preds)
    return results


@torch.no_grad()
def story_features(model: OSLBert, dataset: TraceDataset, device: torch.device, batch_size: int) -> np.ndarray:
    model.eval()
    chunks = []
    for raw_batch in DataLoader(dataset, batch_size=batch_size, shuffle=False):
        batch = move_batch(raw_batch, device)
        z, _slots, _ = model.encode_story(batch["ids"], batch["mask"])
        chunks.append(z.cpu().numpy())
    return np.concatenate(chunks)


@torch.no_grad()
def query_slot_features(model: OSLBert, dataset: TraceDataset, device: torch.device, batch_size: int) -> np.ndarray:
    model.eval()
    chunks = []
    for raw_batch in DataLoader(dataset, batch_size=batch_size, shuffle=False):
        batch = move_batch(raw_batch, device)
        _z, slots, _ = model.encode_story(batch["ids"], batch["mask"])
        index = batch["query_agent"] * len(FACTS) + batch["query_fact"]
        chunks.append(slots[torch.arange(len(slots), device=device), index].cpu().numpy())
    return np.concatenate(chunks)


def query_features(z: np.ndarray, records: list[Record]) -> np.ndarray:
    agent = np.eye(len(AGENTS), dtype=np.float32)[[row.query_agent for row in records]]
    fact = np.eye(len(FACTS), dtype=np.float32)[[row.query_fact for row in records]]
    return np.concatenate([z, agent, fact], axis=1)


def random_transformer_baseline(
    config: BertConfig,
    seed: int,
    train: list[Record],
    train_ds: TraceDataset,
    splits: dict[str, list[Record]],
    split_ds: dict[str, TraceDataset],
    device: torch.device,
    batch_size: int,
) -> tuple[dict[str, dict[str, float]], OSLBert]:
    set_seed(seed)
    model = OSLBert(copy.deepcopy(config)).to(device)
    x_train = query_slot_features(model, train_ds, device, batch_size)
    train_labels = labels_matrix(train)
    classifiers = {key: fit_classifier(x_train, train_labels[key], seed=seed) for key in LABEL_KEYS}
    results = {}
    for split, rows in splits.items():
        x = query_slot_features(model, split_ds[split], device, batch_size)
        labels = labels_matrix(rows)
        preds = {key: classifiers[key].predict(x) for key in LABEL_KEYS}
        results[split] = score_baseline_predictions(labels, preds)
    return results, model


def majority_baseline(train: list[Record], splits: dict[str, list[Record]]) -> dict[str, dict[str, float]]:
    labels = labels_matrix(train)
    majorities = {key: Counter(labels[key]).most_common(1)[0][0] for key in LABEL_KEYS}
    out = {}
    for split, rows in splits.items():
        truth = labels_matrix(rows)
        preds = {key: np.full(len(rows), majorities[key]) for key in LABEL_KEYS}
        out[split] = score_baseline_predictions(truth, preds)
    return out


def exact_executor_baseline(splits: dict[str, list[Record]]) -> dict[str, dict[str, float]]:
    return {
        split: {
            **{f"{key}_accuracy": 1.0 for key in LABEL_KEYS},
            "mode_balanced_accuracy": 1.0,
            "joint_six_accuracy": 1.0,
        }
        for split in splits
    }


def formal_state_matrix(records: list[Record]) -> np.ndarray:
    mode = np.eye(len(MODES), dtype=np.float32)[np.array([row.full_mode for row in records])].reshape(len(records), -1)
    origin = np.eye(len(AGENTS) + 1, dtype=np.float32)[np.array([row.full_origin for row in records])].reshape(len(records), -1)
    auth = np.eye(2, dtype=np.float32)[np.array([row.full_authorized for row in records])].reshape(len(records), -1)
    return np.concatenate([mode, origin, auth], axis=1)


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    x = x.astype(np.float64) - x.mean(axis=0, keepdims=True)
    y = y.astype(np.float64) - y.mean(axis=0, keepdims=True)
    numerator = np.linalg.norm(x.T @ y, "fro") ** 2
    denominator = np.linalg.norm(x.T @ x, "fro") * np.linalg.norm(y.T @ y, "fro")
    return float(numerator / (denominator + 1e-12))


def cosine_rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.sum(x * y, axis=1) / (np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1) + 1e-12)


def matched_near_miss_indices(records: list[Record]) -> np.ndarray:
    indices = []
    for index, row in enumerate(records):
        candidates = [
            j
            for j, other in enumerate(records)
            if j != index and other.mode == row.mode and other.state_hash != row.state_hash
        ]
        if not candidates:
            candidates = [j for j, other in enumerate(records) if j != index and other.state_hash != row.state_hash]
        if not candidates:
            indices.append(index)
            continue
        def score(j: int):
            other = records[j]
            op_distance = sum(abs(a - b) for a, b in zip(row.op_counts, other.op_counts))
            return (abs(row.length - other.length), op_distance, abs(row.query_agent - other.query_agent), abs(row.query_fact - other.query_fact))
        indices.append(min(candidates, key=score))
    return np.array(indices, dtype=np.int64)


def geometry_audit(
    model: OSLBert,
    random_model: OSLBert,
    records: list[Record],
    dataset: TraceDataset,
    device: torch.device,
    batch_size: int,
    permutations: int,
    seed: int,
) -> dict:
    trained = collect_predictions(model, dataset, device, batch_size, collect_layers=True, collect_alt=True)
    random_collected = collect_predictions(random_model, dataset, device, batch_size, collect_layers=True, collect_alt=True)
    formal = formal_state_matrix(records)
    negatives = matched_near_miss_indices(records)

    def global_triplet(collected: dict) -> dict[str, float]:
        z = collected["z"]
        alt = collected["alt_z"]
        positive = cosine_rows(z, alt)
        negative = cosine_rows(z, z[negatives])
        return {
            "accuracy": float((positive > negative).mean()),
            "mean_positive_cosine": float(positive.mean()),
            "mean_negative_cosine": float(negative.mean()),
            "margin": float((positive - negative).mean()),
        }

    def workspace_triplet(collected: dict) -> dict[str, float]:
        workspace = collected["workspace"]
        alt = collected["alt_workspace"]
        positive = cosine_rows(workspace.reshape(-1, workspace.shape[-1]), alt.reshape(-1, alt.shape[-1])).reshape(len(records), CELL_COUNT).mean(axis=1)
        negative_workspace = workspace[negatives]
        negative = cosine_rows(
            workspace.reshape(-1, workspace.shape[-1]),
            negative_workspace.reshape(-1, workspace.shape[-1]),
        ).reshape(len(records), CELL_COUNT).mean(axis=1)
        return {
            "accuracy": float((positive > negative).mean()),
            "mean_positive_cosine": float(positive.mean()),
            "mean_negative_cosine": float(negative.mean()),
            "margin": float((positive - negative).mean()),
        }

    rng = np.random.default_rng(seed)
    observed = linear_cka(trained["z"], formal)
    null = []
    strata = defaultdict(list)
    for i, row in enumerate(records):
        strata[(row.mode, row.length)].append(i)
    for _ in range(permutations):
        perm = np.arange(len(records))
        for members in strata.values():
            shuffled = np.array(members)
            rng.shuffle(shuffled)
            perm[np.array(members)] = shuffled
        null.append(linear_cka(trained["z"], formal[perm]))
    null_array = np.array(null)
    p_value = float((1 + np.sum(null_array >= observed)) / (len(null_array) + 1))
    return {
        "trained_layerwise_cka": [linear_cka(layer, formal) for layer in trained["layers"]],
        "random_layerwise_cka": [linear_cka(layer, formal) for layer in random_collected["layers"]],
        "trained_final_cka": observed,
        "random_final_cka": linear_cka(random_collected["z"], formal),
        "permutation_null_mean": float(null_array.mean()),
        "permutation_null_sd": float(null_array.std(ddof=1)) if len(null_array) > 1 else 0.0,
        "permutation_p_value": p_value,
        "trained_triplet": workspace_triplet(trained),
        "random_triplet": workspace_triplet(random_collected),
        "trained_global_triplet": global_triplet(trained),
        "random_global_triplet": global_triplet(random_collected),
        "triplet_representation": "aligned_agent_fact_workspace",
    }


def clone_records_with_variant(records: list[Record], variant_index: int) -> list[Record]:
    return [replace(row, text=row.orbit_texts[variant_index]) for row in records]


def orbit_audit(
    model: OSLBert,
    records: list[Record],
    vocab: dict[str, int],
    max_len: int,
    device: torch.device,
    batch_size: int,
) -> dict[str, float]:
    collections = []
    for variant_index in range(len(records[0].orbit_texts)):
        variant_records = clone_records_with_variant(records, variant_index)
        variant_ds = TraceDataset(variant_records, vocab, max_len)
        collections.append(collect_predictions(model, variant_ds, device, batch_size))
    strict_correct = []
    mode_predictions = []
    for collected in collections:
        labels = collected["labels"]
        preds = collected["preds"]
        strict_correct.append(np.logical_and.reduce([labels[key] == preds[key] for key in LABEL_KEYS]))
        mode_predictions.append(preds["mode"])
    return {
        "strict_all_variants_joint_accuracy": float(np.logical_and.reduce(strict_correct).mean()),
        "mode_prediction_consistency": float(np.all(np.stack(mode_predictions) == mode_predictions[0][None, :], axis=0).mean()),
        "variant_mean_joint_accuracy": float(np.mean([x.mean() for x in strict_correct])),
    }


def record_cell_labels(row: Record, agent: int, fact: int) -> dict[str, int]:
    index = agent * len(FACTS) + fact
    mode = int(row.full_mode[index])
    origin = int(row.full_origin[index])
    auth = int(row.full_authorized[index])
    return {
        "mode": mode,
        "origin": origin,
        "access": int(mode != MODE_ID["none"]),
        "direct": int(mode == MODE_ID["observed"]),
        "authorized": auth,
        "eligible": int(auth == 1 and mode in (MODE_ID["observed"], MODE_ID["communicated"], MODE_ID["inferred"])),
    }


@torch.no_grad()
def encode_record_workspaces(
    model: OSLBert,
    records: list[Record],
    vocab: dict[str, int],
    max_len: int,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    model.eval()
    chunks = []
    dataset = TraceDataset(records, vocab, max_len)
    for raw_batch in DataLoader(dataset, batch_size=batch_size, shuffle=False):
        batch = move_batch(raw_batch, device)
        _z, slots, _hidden = model.encode_story(batch["ids"], batch["mask"])
        chunks.append(slots.float().cpu().numpy())
    return np.concatenate(chunks)


@torch.no_grad()
def predict_workspace_bundles(
    model: OSLBert,
    slots: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> dict[str, np.ndarray]:
    chunks = {key: [] for key in LABEL_KEYS}
    for start in range(0, len(slots), batch_size):
        stop = min(start + batch_size, len(slots))
        slot_tensor = torch.tensor(slots[start:stop], dtype=torch.float32, device=device)
        logits = model.predict_all_from_slots(slot_tensor)
        for key in LABEL_KEYS:
            chunks[key].append(logits[key].argmax(-1).cpu().numpy())
    return {key: np.concatenate(value) for key, value in chunks.items()}


def truth_workspace_bundles(pairs: list[CausalPair], which: str) -> dict[str, np.ndarray]:
    rows = [pair.base if which == "base" else pair.counterfactual for pair in pairs]
    mode = np.array([row.full_mode for row in rows], dtype=np.int64)
    origin = np.array([row.full_origin for row in rows], dtype=np.int64)
    authorized = np.array([row.full_authorized for row in rows], dtype=np.int64)
    return {
        "mode": mode,
        "origin": origin,
        "access": (mode != MODE_ID["none"]).astype(np.int64),
        "direct": (mode == MODE_ID["observed"]).astype(np.int64),
        "authorized": authorized,
        "eligible": (
            (authorized == 1)
            & np.isin(mode, [MODE_ID["observed"], MODE_ID["communicated"], MODE_ID["inferred"]])
        ).astype(np.int64),
    }


def bundle_exact(pred: dict[str, np.ndarray], truth: dict[str, np.ndarray], keys: list[str] | None = None) -> np.ndarray:
    selected = keys or LABEL_KEYS
    return np.logical_and.reduce([pred[key] == truth[key] for key in selected])


def target_indices(pairs: list[CausalPair]) -> np.ndarray:
    return np.array(
        [pair.base.query_agent * len(FACTS) + pair.base.query_fact for pair in pairs],
        dtype=np.int64,
    )


def gather_target(values: dict[str, np.ndarray], indices: np.ndarray) -> dict[str, np.ndarray]:
    rows = np.arange(len(indices))
    return {key: array[rows, indices] for key, array in values.items()}


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total <= 0:
        return [0.0, 0.0]
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)) / denominator
    return [float(max(0.0, center - radius)), float(min(1.0, center + radius))]


def score_workspace_intervention(
    model: OSLBert,
    pairs: list[CausalPair],
    base_slots: np.ndarray,
    counter_slots: np.ndarray,
    patched_slots: np.ndarray,
    device: torch.device,
    batch_size: int,
    min_eligible: int,
) -> dict:
    indices = target_indices(pairs)
    base_pred_all = predict_workspace_bundles(model, base_slots, device, batch_size)
    counter_pred_all = predict_workspace_bundles(model, counter_slots, device, batch_size)
    patched_pred_all = predict_workspace_bundles(model, patched_slots, device, batch_size)
    base_truth_all = truth_workspace_bundles(pairs, "base")
    counter_truth_all = truth_workspace_bundles(pairs, "counter")
    base_pred = gather_target(base_pred_all, indices)
    counter_pred = gather_target(counter_pred_all, indices)
    patched_pred = gather_target(patched_pred_all, indices)
    base_truth = gather_target(base_truth_all, indices)
    counter_truth = gather_target(counter_truth_all, indices)
    core_keys = ["mode", "origin", "authorized"]
    eligible = bundle_exact(base_pred, base_truth, core_keys) & bundle_exact(counter_pred, counter_truth, core_keys)
    target_success = bundle_exact(patched_pred, counter_truth)
    changed_correct = []
    invariant_correct = []
    for row in range(len(pairs)):
        changed = [key for key in LABEL_KEYS if base_truth[key][row] != counter_truth[key][row]]
        invariant = [key for key in LABEL_KEYS if key not in changed]
        changed_correct.append(all(patched_pred[key][row] == counter_truth[key][row] for key in changed))
        invariant_correct.append(all(patched_pred[key][row] == counter_truth[key][row] for key in invariant))
    changed_correct = np.array(changed_correct, dtype=bool)
    invariant_correct = np.array(invariant_correct, dtype=bool)
    untouched_mask = np.ones((len(pairs), CELL_COUNT), dtype=bool)
    untouched_mask[np.arange(len(pairs)), indices] = False
    retention_fields = np.stack(
        [patched_pred_all[key] == base_pred_all[key] for key in LABEL_KEYS],
        axis=-1,
    )
    untouched_micro = retention_fields[untouched_mask].mean(axis=-1)
    all_untouched = retention_fields[untouched_mask].reshape(len(pairs), CELL_COUNT - 1, len(LABEL_KEYS)).all(axis=(1, 2))
    baseline_correct = np.stack(
        [base_pred_all[key] == base_truth_all[key] for key in LABEL_KEYS],
        axis=-1,
    )
    patched_correct = np.stack(
        [patched_pred_all[key] == base_truth_all[key] for key in LABEL_KEYS],
        axis=-1,
    )
    eligible_correct_fields = baseline_correct & untouched_mask[:, :, None]
    correctness_retained = float(patched_correct[eligible_correct_fields].mean()) if eligible_correct_fields.any() else None
    selective = target_success & all_untouched
    eligible_count = int(eligible.sum())

    def mean_on(mask: np.ndarray, values: np.ndarray) -> float | None:
        return float(values[mask].mean()) if mask.any() else None

    conditional = None
    status = "insufficient_endpoint_capacity"
    if eligible_count >= min_eligible:
        status = "evaluable"
        conditional = {
            "target_counterfactual_exact": mean_on(eligible, target_success),
            "changed_field_exact": mean_on(eligible, changed_correct),
            "target_invariant_exact": mean_on(eligible, invariant_correct),
            "untouched_prediction_retention_micro": float(retention_fields[eligible][untouched_mask[eligible]].mean()),
            "all_untouched_prediction_retention": mean_on(eligible, all_untouched),
            "selective_full_workspace_success": mean_on(eligible, selective),
        }
    by_family = {}
    for family in CAUSAL_FAMILIES:
        family_mask = np.array([pair.family == family for pair in pairs])
        family_eligible = family_mask & eligible
        by_family[family] = {
            "pairs": int(family_mask.sum()),
            "eligible_pairs": int(family_eligible.sum()),
            "eligibility_rate": float(eligible[family_mask].mean()) if family_mask.any() else 0.0,
            "target_counterfactual_exact": mean_on(family_eligible, target_success),
            "selective_full_workspace_success": mean_on(family_eligible, selective),
        }
    return {
        "status": status,
        "pairs": len(pairs),
        "eligible_pairs": eligible_count,
        "eligibility_rate": float(eligible.mean()),
        "eligibility_wilson_95": wilson_interval(eligible_count, len(pairs)),
        "minimum_eligible_required": min_eligible,
        "base_endpoint_core_exact": float(bundle_exact(base_pred, base_truth, core_keys).mean()),
        "counterfactual_endpoint_core_exact": float(bundle_exact(counter_pred, counter_truth, core_keys).mean()),
        "all_pair_target_counterfactual_exact": float(target_success.mean()),
        "all_pair_changed_field_exact": float(changed_correct.mean()),
        "all_pair_target_invariant_exact": float(invariant_correct.mean()),
        "all_pair_untouched_prediction_retention_micro": float(retention_fields[untouched_mask].mean()),
        "all_pair_all_untouched_prediction_retention": float(all_untouched.mean()),
        "all_pair_selective_full_workspace_success": float(selective.mean()),
        "untouched_correctness_retention": correctness_retained,
        "conditional": conditional,
        "by_family": by_family,
    }


def apply_family_directions(
    pairs: list[CausalPair],
    base_slots: np.ndarray,
    directions: dict[str, np.ndarray],
    alpha: float,
) -> np.ndarray:
    patched = base_slots.copy()
    indices = target_indices(pairs)
    for row, pair in enumerate(pairs):
        patched[row, indices[row]] += alpha * directions[pair.family]
    return patched


def fit_family_directions(
    pairs: list[CausalPair],
    base_slots: np.ndarray,
    counter_slots: np.ndarray,
) -> dict[str, np.ndarray]:
    indices = target_indices(pairs)
    rows = np.arange(len(pairs))
    delta = counter_slots[rows, indices] - base_slots[rows, indices]
    directions = {}
    for family in CAUSAL_FAMILIES:
        mask = np.array([pair.family == family for pair in pairs])
        directions[family] = delta[mask].mean(axis=0)
    return directions


@torch.no_grad()
def apply_learned_transitions(
    model: OSLBert,
    pairs: list[CausalPair],
    base_slots: np.ndarray,
    device: torch.device,
    batch_size: int,
    event_order: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    chunks = []
    predicted_chunks = []
    events = [event_from_tuple(pair.added_event) for pair in pairs]
    if event_order is not None:
        events = [events[int(index)] for index in event_order]
    for start in range(0, len(pairs), batch_size):
        stop = min(start + batch_size, len(pairs))
        batch_events = events[start:stop]
        slots = torch.tensor(base_slots[start:stop], dtype=torch.float32, device=device)
        op = torch.tensor([OP_ID[event.op] for event in batch_events], dtype=torch.long, device=device)
        actor = torch.tensor([event.actor for event in batch_events], dtype=torch.long, device=device)
        fact = torch.tensor([event.fact for event in batch_events], dtype=torch.long, device=device)
        other = torch.tensor([event.other for event in batch_events], dtype=torch.long, device=device)
        source = torch.tensor([event.source_fact for event in batch_events], dtype=torch.long, device=device)
        transitioned, predicted_index, _scores = model.free_write_transition(
            slots, op, actor, fact, other, source, hard=True
        )
        chunks.append(transitioned.cpu().numpy())
        predicted_chunks.append(predicted_index.cpu().numpy())
    return np.concatenate(chunks), np.concatenate(predicted_chunks)


def causal_audit(
    model: OSLBert,
    calibration_pairs: list[CausalPair],
    id_pairs: list[CausalPair],
    ood_pairs: list[CausalPair],
    vocab: dict[str, int],
    max_len: int,
    device: torch.device,
    batch_size: int,
    random_directions: int,
    min_eligible: int,
    seed: int,
) -> dict:
    encoded = {}
    for name, pairs in {"calibration": calibration_pairs, "id": id_pairs, "ood": ood_pairs}.items():
        encoded[name] = {
            "base": encode_record_workspaces(model, [pair.base for pair in pairs], vocab, max_len, device, batch_size),
            "counter": encode_record_workspaces(model, [pair.counterfactual for pair in pairs], vocab, max_len, device, batch_size),
        }
    directions = fit_family_directions(calibration_pairs, encoded["calibration"]["base"], encoded["calibration"]["counter"])
    norms = {family: float(np.linalg.norm(value)) for family, value in directions.items()}
    if any(value < 1e-12 for value in norms.values()):
        return {"status": "degenerate_direction", "direction_norms": norms}
    alpha_grid = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    calibration_scores = []
    calibration_min = max(1, min_eligible // 2)
    for alpha in alpha_grid:
        patched = apply_family_directions(calibration_pairs, encoded["calibration"]["base"], directions, alpha)
        score = score_workspace_intervention(
            model,
            calibration_pairs,
            encoded["calibration"]["base"],
            encoded["calibration"]["counter"],
            patched,
            device,
            batch_size,
            calibration_min,
        )
        score["alpha"] = alpha
        calibration_scores.append(score)
    best = max(
        calibration_scores,
        key=lambda score: (
            -1.0 if score["conditional"] is None else score["conditional"]["selective_full_workspace_success"],
            score["all_pair_selective_full_workspace_success"],
            -abs(score["alpha"] - 1.0),
        ),
    )
    selected_alpha = float(best["alpha"])

    def evaluate_bank(name: str, pairs: list[CausalPair]) -> dict:
        base = encoded[name]["base"]
        counter = encoded[name]["counter"]
        targeted_slots = apply_family_directions(pairs, base, directions, selected_alpha)
        targeted = score_workspace_intervention(
            model, pairs, base, counter, targeted_slots, device, batch_size, min_eligible
        )
        learned_slots, predicted_indices = apply_learned_transitions(model, pairs, base, device, batch_size)
        learned = score_workspace_intervention(
            model, pairs, base, counter, learned_slots, device, batch_size, min_eligible
        )
        learned["write_locator_accuracy"] = float((predicted_indices == target_indices(pairs)).mean())
        return {"targeted_slot_direction": targeted, "learned_operand_transition": learned}

    id_result = evaluate_bank("id", id_pairs)
    ood_result = evaluate_bank("ood", ood_pairs)
    rng = np.random.default_rng(seed)
    random_scores = []
    for _ in range(random_directions):
        random_map = {}
        for family, direction in directions.items():
            candidate = rng.normal(size=direction.shape)
            candidate *= np.linalg.norm(direction) / (np.linalg.norm(candidate) + 1e-12)
            random_map[family] = candidate
        random_slots = apply_family_directions(id_pairs, encoded["id"]["base"], random_map, selected_alpha)
        random_scores.append(
            score_workspace_intervention(
                model,
                id_pairs,
                encoded["id"]["base"],
                encoded["id"]["counter"],
                random_slots,
                device,
                batch_size,
                min_eligible,
            )
        )
    control_values = np.array(
        [
            score["all_pair_selective_full_workspace_success"]
            if score["conditional"] is None
            else score["conditional"]["selective_full_workspace_success"]
            for score in random_scores
        ],
        dtype=np.float64,
    )
    reversed_map = {family: -value for family, value in directions.items()}
    reversed_slots = apply_family_directions(id_pairs, encoded["id"]["base"], reversed_map, selected_alpha)
    reversed_score = score_workspace_intervention(
        model,
        id_pairs,
        encoded["id"]["base"],
        encoded["id"]["counter"],
        reversed_slots,
        device,
        batch_size,
        min_eligible,
    )
    operand_order = np.arange(len(id_pairs))
    for family in CAUSAL_FAMILIES:
        members = np.flatnonzero([pair.family == family for pair in id_pairs])
        shuffled = members.copy()
        rng.shuffle(shuffled)
        operand_order[members] = shuffled
    shuffled_transition_slots, shuffled_predicted_indices = apply_learned_transitions(
        model,
        id_pairs,
        encoded["id"]["base"],
        device,
        batch_size,
        event_order=operand_order,
    )
    shuffled_transition_score = score_workspace_intervention(
        model,
        id_pairs,
        encoded["id"]["base"],
        encoded["id"]["counter"],
        shuffled_transition_slots,
        device,
        batch_size,
        min_eligible,
    )
    shuffled_transition_score["write_locator_accuracy"] = float(
        (shuffled_predicted_indices == target_indices(id_pairs)).mean()
    )
    return {
        "status": "ok",
        "direction_norms": norms,
        "selected_alpha": selected_alpha,
        "calibration_scores": calibration_scores,
        "id": id_result,
        "ood": ood_result,
        "controls": {
            "random_directions": random_directions,
            "id_selective_mean": float(control_values.mean()),
            "id_selective_p95": float(np.quantile(control_values, 0.95)),
            "sign_reversed": reversed_score,
            "shuffled_operands_for_learned_transition": shuffled_transition_score,
        },
        "interpretation_guard": "Oracle-addressed slot retention is partly architectural; learned selectivity requires the operand transition and target conversion to pass together.",
    }


PROFILES = {
    "smoke": {
        "generator_seed": 731,
        "n_train": 200,
        "n_val": 50,
        "n_eval": 50,
        "epochs": 1,
        "seeds": [11],
        "layers": 1,
        "hidden": 64,
        "heads": 4,
        "intermediate": 128,
        "batch_size": 32,
        "causal_calibration": 15,
        "causal_test": 20,
        "permutations": 10,
        "random_directions": 4,
        "arms": ["answer_only", "state_supervised", "equivalence", "slot_operator"],
    },
    "pilot": {
        "generator_seed": 731,
        "n_train": 3000,
        "n_val": 500,
        "n_eval": 500,
        "epochs": 6,
        "seeds": [11, 29],
        "layers": 2,
        "hidden": 96,
        "heads": 4,
        "intermediate": 256,
        "batch_size": 64,
        "causal_calibration": 100,
        "causal_test": 250,
        "permutations": 100,
        "random_directions": 20,
        "arms": ["answer_only", "state_supervised", "equivalence", "slot_operator"],
    },
    "full": {
        "generator_seed": 731,
        "n_train": 12000,
        "n_val": 1500,
        "n_eval": 2000,
        "epochs": 10,
        "seeds": [11, 29, 47, 83],
        "layers": 4,
        "hidden": 192,
        "heads": 6,
        "intermediate": 512,
        "batch_size": 64,
        "causal_calibration": 300,
        "causal_test": 750,
        "permutations": 250,
        "random_directions": 40,
        "arms": ["answer_only", "state_supervised", "equivalence", "slot_operator"],
    },
    "confirmatory": {
        "generator_seed": 1907,
        "n_train": 30000,
        "n_val": 3000,
        "n_eval": 3000,
        "epochs": 12,
        "seeds": [101, 137, 173, 211, 251],
        "layers": 4,
        "hidden": 256,
        "heads": 8,
        "intermediate": 768,
        "batch_size": 64,
        "causal_calibration": 500,
        "causal_test": 1200,
        "permutations": 500,
        "random_directions": 80,
        "arms": ["answer_only", "state_supervised", "equivalence", "slot_operator"],
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=json_default), encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_matching_json(path: Path, expected, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"resume requires {label}: {path}")
    canonical_expected = json.loads(json.dumps(expected, default=json_default))
    if read_json(path) != canonical_expected:
        raise RuntimeError(f"resume refused because regenerated {label} does not match {path}")


def atomic_torch_save(value, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        torch.save(value, temporary)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_compatible_checkpoint(
    path: Path,
    arm: str,
    seed: int,
    model_config: BertConfig,
    vocab: dict[str, int],
    max_len: int,
    source_hash: str,
    protocol_hash: str,
    dataset_audit_hash: str,
    device: torch.device,
) -> tuple[OSLBert, list[dict], bool]:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    if int(checkpoint.get("checkpoint_schema_version", -1)) != CHECKPOINT_SCHEMA_VERSION:
        raise RuntimeError(f"checkpoint schema mismatch: {path}")
    if checkpoint.get("arm") != arm or int(checkpoint.get("seed", -1)) != seed:
        raise RuntimeError(f"checkpoint identity mismatch: {path}")
    if checkpoint.get("vocab") != vocab or int(checkpoint.get("max_len", -1)) != max_len:
        raise RuntimeError(f"checkpoint vocabulary or sequence length mismatch: {path}")
    if checkpoint.get("source_sha256") != source_hash or checkpoint.get("protocol_sha256") != protocol_hash:
        raise RuntimeError(f"checkpoint source or protocol hash mismatch: {path}")
    if checkpoint.get("dataset_audit_sha256") != dataset_audit_hash:
        raise RuntimeError(f"checkpoint dataset audit hash mismatch: {path}")
    expected_config = model_config.to_dict()
    saved_config = checkpoint.get("bert_config", {})
    structural_keys = [
        "vocab_size",
        "hidden_size",
        "num_hidden_layers",
        "num_attention_heads",
        "intermediate_size",
        "max_position_embeddings",
        "pad_token_id",
    ]
    if any(saved_config.get(key) != expected_config.get(key) for key in structural_keys):
        raise RuntimeError(f"checkpoint model configuration mismatch: {path}")
    model = OSLBert(copy.deepcopy(model_config))
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    history_available = "history" in checkpoint
    history = checkpoint.get("history", [])
    return model.to(device), history, history_available


def data_audit(train: list[Record], splits: dict[str, list[Record]]) -> dict:
    train_structural = {row.structural_hash for row in train}
    train_alpha = {row.alpha_hash for row in train}
    all_groups = {"train": train, **splits}
    pairwise = {}
    names = list(all_groups)
    for i, left_name in enumerate(names):
        left = all_groups[left_name]
        left_structural = {row.structural_hash for row in left}
        left_alpha = {row.alpha_hash for row in left}
        for right_name in names[i + 1 :]:
            right = all_groups[right_name]
            right_structural = {row.structural_hash for row in right}
            right_alpha = {row.alpha_hash for row in right}
            pairwise[f"{left_name}__{right_name}"] = {
                "structural_overlap": len(left_structural & right_structural),
                "alpha_overlap": len(left_alpha & right_alpha),
            }
    distributions = {}
    for name, rows in all_groups.items():
        distributions[name] = {
            "size": len(rows),
            "mode_counts": dict(sorted(Counter(row.mode for row in rows).items())),
            "query_label_counts": {
                key: dict(sorted(Counter(getattr(row, key) for row in rows).items()))
                for key in LABEL_KEYS
            },
            "length_counts": dict(sorted(Counter(row.length for row in rows).items())),
            "linked_motif_rate": float(np.mean([linked_motif([event_from_tuple(x) for x in row.events]) for row in rows])),
            "codebook_rate": float(np.mean([row.surface_kind == "codebook" for row in rows])),
            "unique_structural_hashes": len({row.structural_hash for row in rows}),
            "unique_alpha_hashes": len({row.alpha_hash for row in rows}),
            "overlap_with_train_structural": len({row.structural_hash for row in rows} & train_structural) if name != "train" else 0,
            "overlap_with_train_alpha": len({row.alpha_hash for row in rows} & train_alpha) if name != "train" else 0,
        }
    return {"distributions": distributions, "pairwise_overlap": pairwise}


def average_trained_metrics(metrics_rows: list[dict]) -> dict[str, dict[str, dict[str, float]]]:
    grouped = defaultdict(list)
    for row in metrics_rows:
        grouped[(row["arm"], row["split"])].append(row)
    out = defaultdict(dict)
    for (arm, split), rows in grouped.items():
        numeric_keys = [
            key
            for key, value in rows[0].items()
            if key not in ("arm", "split", "seed") and isinstance(value, (int, float, np.integer, np.floating))
        ]
        out[arm][split] = {key: float(np.mean([row[key] for row in rows])) for key in numeric_keys}
        out[arm][split]["seed_sd_mode_balanced"] = float(np.std([row["mode_balanced_accuracy"] for row in rows], ddof=1)) if len(rows) > 1 else 0.0
    return {key: value for key, value in out.items()}


def adjudicate(summary: dict) -> dict:
    trained = summary["trained_mean"]
    baselines = summary["baselines"]
    answer = trained.get("answer_only", {})
    required_arms = {"answer_only", "state_supervised", "equivalence", "slot_operator"}
    required_baselines = {"majority", "exact_executor", "word_tfidf", "char_tfidf", "question_only", "shuffled_label_tfidf", "random_transformer"}
    controls_complete = (
        required_arms.issubset(trained)
        and required_baselines.issubset(baselines)
        and bool(summary.get("geometry", {}).get("answer_only"))
        and bool(summary.get("causal", {}).get("answer_only"))
    )
    if "id" not in answer or "joint_ood" not in answer:
        return {
            "status": "engineering_incomplete",
            "strong_operator_evidence": False,
            "scaffolded_operator_evidence": False,
            "gates": {},
            "conclusion": "The required answer-only arm or evaluation splits were not run, so no scientific adjudication is available.",
            "scope_note": "The result concerns a bounded synthetic operator world. It is not evidence of awareness or consciousness.",
        }
    shortcut_systems = [name for name in baselines if name not in ("exact_executor",)]
    strongest_joint = max(
        [baselines[name]["joint_ood"]["mode_balanced_accuracy"] for name in shortcut_systems],
        default=None,
    )
    geometry_rows = summary["geometry"].get("answer_only", [])
    causal_rows = [row for row in summary["causal"].get("answer_only", []) if row.get("status") == "ok"]
    triplet = float(np.mean([row["trained_triplet"]["accuracy"] for row in geometry_rows])) if geometry_rows else 0.0
    random_triplet = float(np.mean([row["random_triplet"]["accuracy"] for row in geometry_rows])) if geometry_rows else 0.0

    def causal_summary(rows: list[dict], intervention: str) -> dict:
        result = {}
        for bank in ("id", "ood"):
            scores = [row[bank][intervention] for row in rows]
            evaluable = [score for score in scores if score.get("conditional") is not None]
            result[bank] = {
                "seeds": len(scores),
                "evaluable_seeds": len(evaluable),
                "eligibility_rate": float(np.mean([score["eligibility_rate"] for score in scores])) if scores else 0.0,
                "eligibility_wilson_lower": float(np.mean([score["eligibility_wilson_95"][0] for score in scores])) if scores else 0.0,
                "target_exact": float(np.mean([score["conditional"]["target_counterfactual_exact"] for score in evaluable])) if evaluable else None,
                "retention": float(np.mean([score["conditional"]["untouched_prediction_retention_micro"] for score in evaluable])) if evaluable else None,
                "selective": float(np.mean([score["conditional"]["selective_full_workspace_success"] for score in evaluable])) if evaluable else None,
                "write_locator_accuracy": float(np.mean([score["write_locator_accuracy"] for score in scores if "write_locator_accuracy" in score])) if any("write_locator_accuracy" in score for score in scores) else None,
            }
        return result

    spontaneous = causal_summary(causal_rows, "targeted_slot_direction") if causal_rows else {
        "id": {"seeds": 0, "evaluable_seeds": 0, "eligibility_rate": 0.0, "eligibility_wilson_lower": 0.0, "target_exact": None, "retention": None, "selective": None, "write_locator_accuracy": None},
        "ood": {"seeds": 0, "evaluable_seeds": 0, "eligibility_rate": 0.0, "eligibility_wilson_lower": 0.0, "target_exact": None, "retention": None, "selective": None, "write_locator_accuracy": None},
    }
    operator_rows = [row for row in summary["causal"].get("slot_operator", []) if row.get("status") == "ok"]
    scaffolded = causal_summary(operator_rows, "learned_operand_transition") if operator_rows else {
        "id": {"seeds": 0, "evaluable_seeds": 0, "eligibility_rate": 0.0, "eligibility_wilson_lower": 0.0, "target_exact": None, "retention": None, "selective": None, "write_locator_accuracy": None},
        "ood": {"seeds": 0, "evaluable_seeds": 0, "eligibility_rate": 0.0, "eligibility_wilson_lower": 0.0, "target_exact": None, "retention": None, "selective": None, "write_locator_accuracy": None},
    }
    random_p95 = float(np.mean([row["controls"]["id_selective_p95"] for row in causal_rows])) if causal_rows else None

    def status(condition: bool, available: bool = True) -> str:
        if not available:
            return "NOT_EVALUABLE"
        return "PASS" if condition else "FAIL"

    id_available = spontaneous["id"]["evaluable_seeds"] >= max(1, math.ceil(0.75 * max(spontaneous["id"]["seeds"], 1)))
    ood_available = spontaneous["ood"]["evaluable_seeds"] >= max(1, math.ceil(0.75 * max(spontaneous["ood"]["seeds"], 1)))
    gates = {
        "controls_complete": "PASS" if controls_complete else "NOT_RUN",
        "id_capacity": status(answer["id"]["mode_balanced_accuracy"] >= 0.85),
        "joint_ood_mode": status(answer["joint_ood"]["mode_balanced_accuracy"] >= 0.80),
        "joint_ood_six_output": status(answer["joint_ood"]["joint_six_accuracy"] >= 0.60),
        "shortcut_advantage": status(
            strongest_joint is not None and answer["joint_ood"]["mode_balanced_accuracy"] - strongest_joint >= 0.10,
            available=strongest_joint is not None,
        ),
        "formal_triplet": status(triplet >= 0.65 and triplet - random_triplet >= 0.10, available=bool(geometry_rows)),
        "causal_id_coverage": status(spontaneous["id"]["eligibility_wilson_lower"] >= 0.25, id_available),
        "causal_id_target_conversion": status((spontaneous["id"]["target_exact"] or 0.0) >= 0.70, id_available),
        "causal_id_selective_workspace": status((spontaneous["id"]["selective"] or 0.0) >= 0.55, id_available),
        "causal_id_untouched_retention": status((spontaneous["id"]["retention"] or 0.0) >= 0.995, id_available),
        "causal_control_advantage": status(
            (spontaneous["id"]["selective"] or 0.0) - (random_p95 or 0.0) >= 0.15,
            id_available and random_p95 is not None,
        ),
        "causal_ood_coverage": status(spontaneous["ood"]["eligibility_wilson_lower"] >= 0.10, ood_available),
        "causal_ood_target_conversion": status((spontaneous["ood"]["target_exact"] or 0.0) >= 0.50, ood_available),
        "causal_ood_selective_workspace": status((spontaneous["ood"]["selective"] or 0.0) >= 0.35, ood_available),
        "causal_ood_untouched_retention": status((spontaneous["ood"]["retention"] or 0.0) >= 0.99, ood_available),
    }
    strong = all(value == "PASS" for value in gates.values())
    behavior = all(gates[key] == "PASS" for key in ["id_capacity", "joint_ood_mode", "joint_ood_six_output", "shortcut_advantage"])
    geometry = gates["formal_triplet"] == "PASS"
    causal_keys = [key for key in gates if key.startswith("causal_")]
    causal = all(gates[key] == "PASS" for key in causal_keys)
    scaffolded_available = scaffolded["id"]["target_exact"] is not None and scaffolded["ood"]["target_exact"] is not None
    scaffolded_success = scaffolded_available and (
        scaffolded["id"]["eligibility_wilson_lower"] >= 0.25
        and scaffolded["id"]["target_exact"] >= 0.70
        and scaffolded["id"]["selective"] >= 0.55
        and (scaffolded["id"]["write_locator_accuracy"] or 0.0) >= 0.80
        and scaffolded["ood"]["eligibility_wilson_lower"] >= 0.10
        and scaffolded["ood"]["target_exact"] >= 0.50
        and scaffolded["ood"]["selective"] >= 0.35
        and (scaffolded["ood"]["write_locator_accuracy"] or 0.0) >= 0.60
    )
    if strong:
        conclusion = "The answer-only arm passed the frozen behavioral, geometry, and selective causal gates. This is strong evidence for a task-induced reusable operator abstraction in this synthetic world."
    elif behavior and geometry:
        conclusion = "The answer-only arm showed systematic behavior and operator-relevant geometry, but it did not pass the selective causal gates. This supports a partially organized representation, not a causal operator language."
    elif behavior:
        conclusion = "The answer-only arm passed behavioral gates but not the full geometry and causal conjunction. This supports systematic sentence-based reasoning, not an internal operator language."
    else:
        conclusion = "The answer-only arm did not pass the frozen behavioral conjunction. This configuration does not demonstrate a reusable operator-symbolic language."
    return {
        "status": "complete" if controls_complete else "engineering_incomplete",
        "strong_operator_evidence": strong,
        "scaffolded_operator_evidence": bool(scaffolded_success),
        "behavioral_evidence": behavior,
        "geometry_evidence": geometry,
        "causal_evidence": causal,
        "gates": gates,
        "diagnostics": {
            "strongest_shortcut_joint_mode": strongest_joint,
            "answer_only_joint_mode": answer["joint_ood"]["mode_balanced_accuracy"],
            "answer_only_joint_six": answer["joint_ood"]["joint_six_accuracy"],
            "formal_triplet": triplet,
            "random_formal_triplet": random_triplet,
            "answer_only_causal": spontaneous,
            "slot_operator_causal": scaffolded,
            "random_selective_p95": random_p95,
        },
        "conclusion": conclusion,
        "scope_note": "The result concerns a bounded synthetic operator world. It is not evidence of awareness or consciousness.",
    }


def make_plots(output: Path, summary: dict) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as error:
        (output / "PLOTS_SKIPPED.txt").write_text(
            f"Plot generation was skipped because a plotting dependency was unavailable: {error}\n",
            encoding="utf-8",
        )
        return

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 240, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    split_order = ["id", "length_ood", "motif_ood", "syntax_ood", "joint_ood", "codebook_id", "codebook_ood"]
    systems = {}
    for name in ["word_tfidf", "char_tfidf", "random_transformer"]:
        if name in summary["baselines"]:
            systems[name] = summary["baselines"][name]
    for name, values in summary["trained_mean"].items():
        systems[name] = values
    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(split_order))
    width = 0.8 / max(len(systems), 1)
    for index, (name, values) in enumerate(systems.items()):
        ax.bar(x - 0.4 + width / 2 + index * width, [values[split]["mode_balanced_accuracy"] for split in split_order], width, label=name)
    ax.axhline(0.2, color="black", linewidth=1, linestyle="--", label="chance")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Balanced provenance accuracy")
    ax.set_xticks(x, [name.replace("_", "\n") for name in split_order])
    ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    fig.tight_layout()
    fig.savefig(output / "behavior_accuracy.png", bbox_inches="tight")
    plt.close(fig)

    geometry = summary.get("geometry", {})
    if geometry:
        arms = list(geometry)
        trained = [np.mean([row["trained_triplet"]["accuracy"] for row in geometry[arm]]) for arm in arms]
        random_values = [np.mean([row["random_triplet"]["accuracy"] for row in geometry[arm]]) for arm in arms]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        x = np.arange(len(arms))
        ax.bar(x - 0.18, trained, 0.36, label="trained")
        ax.bar(x + 0.18, random_values, 0.36, label="random transformer")
        ax.axhline(0.5, color="black", linewidth=1, linestyle="--", label="triplet chance")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Formal triplet accuracy")
        ax.set_xticks(x, [name.replace("_", "\n") for name in arms])
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(output / "formal_triplet_accuracy.png", bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4.8))
        for arm in arms:
            values = np.mean(np.array([row["trained_layerwise_cka"] for row in geometry[arm]]), axis=0)
            ax.plot(range(len(values)), values, marker="o", label=arm)
        random_values = np.mean(np.array([row["random_layerwise_cka"] for row in geometry[arms[0]]]), axis=0)
        ax.plot(range(len(random_values)), random_values, marker="o", linestyle="--", color="black", label="random transformer")
        ax.set_xlabel("Layer, including embeddings as layer 0")
        ax.set_ylabel("Linear CKA with formal state")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(output / "layerwise_formal_cka.png", bbox_inches="tight")
        plt.close(fig)

    causal = summary.get("causal", {})
    causal_arms = [arm for arm, rows in causal.items() if any(row.get("status") == "ok" for row in rows)]
    if causal_arms:
        eligibility = []
        targeted = []
        learned = []
        controls = []
        for arm in causal_arms:
            rows = [row for row in causal[arm] if row.get("status") == "ok"]
            targeted_scores = [row["id"]["targeted_slot_direction"] for row in rows]
            learned_scores = [row["id"]["learned_operand_transition"] for row in rows]
            eligibility.append(np.mean([score["eligibility_rate"] for score in targeted_scores]))
            targeted_values = [score["conditional"]["selective_full_workspace_success"] for score in targeted_scores if score["conditional"] is not None]
            learned_values = [score["conditional"]["selective_full_workspace_success"] for score in learned_scores if score["conditional"] is not None]
            targeted.append(float(np.mean(targeted_values)) if targeted_values else 0.0)
            learned.append(float(np.mean(learned_values)) if learned_values else 0.0)
            controls.append(np.mean([row["controls"]["id_selective_p95"] for row in rows]))
        fig, ax = plt.subplots(figsize=(9, 4.8))
        x = np.arange(len(causal_arms))
        ax.bar(x - 0.3, eligibility, 0.2, label="endpoint coverage")
        ax.bar(x - 0.1, targeted, 0.2, label="empirical slot intervention")
        ax.bar(x + 0.1, learned, 0.2, label="learned operand transition")
        ax.bar(x + 0.3, controls, 0.2, label="random-direction p95")
        ax.set_ylim(0, 1)
        ax.set_ylabel("ID rate")
        ax.set_xticks(x, [name.replace("_", "\n") for name in causal_arms])
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(output / "causal_intervention.png", bbox_inches="tight")
        plt.close(fig)


def write_report(output: Path, summary: dict, adjudication: dict) -> None:
    split_order = ["id", "length_ood", "motif_ood", "syntax_ood", "joint_ood", "codebook_id", "codebook_ood"]
    elapsed_label = "Resume-process elapsed seconds" if summary.get("recovery", {}).get("resumed") else "Elapsed seconds"
    lines = [
        "# OSL Hugging Face operand-slot causal and compositional test v0.3",
        "",
        "## Result",
        "",
        adjudication["conclusion"],
        "",
        adjudication["scope_note"],
        "",
        "## Run configuration",
        "",
        f"- Profile: `{summary['config']['profile']}`",
        f"- Device: `{summary['environment']['device']}`",
        f"- Training stories: {summary['config']['n_train']:,}",
        f"- Model seeds: {len(summary['config']['seeds'])}",
        f"- Arms: {', '.join(summary['config']['arms'])}",
        f"- Parameters per model: {summary['environment']['parameters_per_model']:,}",
        f"- {elapsed_label}: {summary['environment']['elapsed_seconds']:.1f}",
    ]
    if summary.get("recovery", {}).get("resumed"):
        recovery = summary["recovery"]
        lines += [
            "",
            "## Interrupted-run recovery",
            "",
            f"- Completed checkpoints loaded without retraining: {len(recovery['loaded_checkpoints'])}",
            f"- Missing checkpoints trained during recovery: {len(recovery['trained_checkpoints'])}",
            f"- Loaded checkpoints without stored epoch histories: {len(recovery['history_unavailable_for_loaded_checkpoints'])}",
            "- Resume required exact source, protocol, configuration, vocabulary, dataset-audit, and checkpoint identities.",
        ]
    lines += [
        "",
        "## Balanced provenance accuracy",
        "",
        "| System | " + " | ".join(split_order) + " |",
        "|---|" + "---:|" * len(split_order),
    ]
    systems = {**summary["baselines"], **summary["trained_mean"]}
    for system, values in systems.items():
        lines.append("| " + system + " | " + " | ".join(f"{100 * values[split]['mode_balanced_accuracy']:.2f}%" for split in split_order) + " |")
    lines += ["", "## Six-output exact agreement", "", "| System | ID | Joint OOD |", "|---|---:|---:|"]
    for system, values in systems.items():
        lines.append(f"| {system} | {100 * values['id']['joint_six_accuracy']:.2f}% | {100 * values['joint_ood']['joint_six_accuracy']:.2f}% |")
    if summary.get("geometry"):
        lines += [
            "",
            "## Same-answer formal triplets",
            "",
            "| Arm | Trained | Random transformer | Margin over random |",
            "|---|---:|---:|---:|",
        ]
        for arm, rows in summary["geometry"].items():
            trained_triplet = float(np.mean([row["trained_triplet"]["accuracy"] for row in rows]))
            random_triplet = float(np.mean([row["random_triplet"]["accuracy"] for row in rows]))
            lines.append(f"| {arm} | {100 * trained_triplet:.2f}% | {100 * random_triplet:.2f}% | {100 * (trained_triplet - random_triplet):+.2f} points |")
    if summary.get("causal"):
        lines += [
            "",
            "## Five-family slot intervention",
            "",
            "| Arm | ID endpoint coverage | Empirical selective success | Learned write location | Learned-transition ID success | Learned-transition OOD success |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for arm, raw_rows in summary["causal"].items():
            rows = [row for row in raw_rows if row.get("status") == "ok"]
            if not rows:
                lines.append(f"| {arm} | not run | not evaluable | not evaluable | not evaluable | not evaluable |")
                continue
            eligibility = np.mean([row["id"]["targeted_slot_direction"]["eligibility_rate"] for row in rows])
            empirical_values = [
                row["id"]["targeted_slot_direction"]["conditional"]["selective_full_workspace_success"]
                for row in rows
                if row["id"]["targeted_slot_direction"]["conditional"] is not None
            ]
            learned_id_values = [
                row["id"]["learned_operand_transition"]["conditional"]["selective_full_workspace_success"]
                for row in rows
                if row["id"]["learned_operand_transition"]["conditional"] is not None
            ]
            learned_ood_values = [
                row["ood"]["learned_operand_transition"]["conditional"]["selective_full_workspace_success"]
                for row in rows
                if row["ood"]["learned_operand_transition"]["conditional"] is not None
            ]
            locator_values = [
                row["id"]["learned_operand_transition"]["write_locator_accuracy"]
                for row in rows
            ]
            def pct(values):
                return f"{100 * float(np.mean(values)):.2f}%" if values else "not evaluable"
            lines.append(
                f"| {arm} | {100 * eligibility:.2f}% | {pct(empirical_values)} | "
                f"{pct(locator_values)} | {pct(learned_id_values)} | {pct(learned_ood_values)} |"
            )
    if summary.get("orbit"):
        lines += [
            "",
            "## Nuisance-orbit stability",
            "",
            "| Arm | Strict all-variant joint accuracy | Provenance consistency |",
            "|---|---:|---:|",
        ]
        for arm, rows in summary["orbit"].items():
            strict = np.mean([row["strict_all_variants_joint_accuracy"] for row in rows])
            consistency = np.mean([row["mode_prediction_consistency"] for row in rows])
            lines.append(f"| {arm} | {100 * strict:.2f}% | {100 * consistency:.2f}% |")
    lines += ["", "## Frozen gates", ""]
    for gate, gate_status in adjudication.get("gates", {}).items():
        lines.append(f"- {gate_status}: `{gate}`")
    lines += [
        "",
        "## Interpretation discipline",
        "",
        "Behavioral accuracy alone does not establish an internal operator language. CKA is a supporting diagnostic only. The strongest claim requires held-out composition, same-answer formal triplets, endpoint capacity, selective slot conversion, and calibrated controls to pass together. Hard slot addressing makes untouched-slot retention partly architectural, so learned target conversion is reported separately.",
        "",
        "Bring the compact return ZIP back to ChatGPT for a full statistical and conceptual review.",
        "",
    ]
    (output / "FINAL_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def write_compact_results_zip(output: Path) -> Path:
    zip_path = output / "RETURN_THIS_OSL_HF_RESULTS.zip"
    excluded_names = {
        "RETURN_THIS_OSL_HF_RESULTS.zip",
        "RETURN_THIS_OSL_HF_RESULTS.zip.sha256",
        "SHA256SUMS.txt",
        "COMPACT_SHA256SUMS.txt",
    }
    included = [
        path
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name not in excluded_names and "checkpoints" not in path.parts
    ]
    compact_manifest = "\n".join(
        f"{sha256_file(path)}  {path.relative_to(output).as_posix()}" for path in included
    ) + "\n"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in included:
            archive.write(path, path.relative_to(output))
        archive.writestr("COMPACT_SHA256SUMS.txt", compact_manifest)
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test operator-language emergence in a randomly initialized Hugging Face transformer")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="pilot")
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--seed", type=int, help="dataset generator seed; profile-specific when omitted")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--n-train", type=int)
    parser.add_argument("--n-val", type=int)
    parser.add_argument("--n-eval", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--layers", type=int)
    parser.add_argument("--hidden", type=int)
    parser.add_argument("--heads", type=int)
    parser.add_argument("--intermediate", type=int)
    parser.add_argument("--causal-calibration", type=int)
    parser.add_argument("--causal-test", type=int)
    parser.add_argument("--permutations", type=int)
    parser.add_argument("--random-directions", type=int)
    parser.add_argument("--learning-rate", type=float, default=4e-4)
    parser.add_argument("--arms", type=str, help="comma-separated subset of answer_only,state_supervised,equivalence,slot_operator")
    parser.add_argument("--seeds", type=str, help="comma-separated integer model seeds")
    parser.add_argument("--no-baselines", action="store_true")
    parser.add_argument("--no-geometry", action="store_true")
    parser.add_argument("--no-causal", action="store_true")
    parser.add_argument("--no-checkpoints", action="store_true")
    parser.add_argument("--nondeterministic", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume a compatible interrupted run from its completed model checkpoints",
    )
    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> dict:
    config = copy.deepcopy(PROFILES[args.profile])
    config["profile"] = args.profile
    if args.seed is not None:
        config["generator_seed"] = args.seed
    for key in [
        "n_train",
        "n_val",
        "n_eval",
        "epochs",
        "batch_size",
        "layers",
        "hidden",
        "heads",
        "intermediate",
        "causal_calibration",
        "causal_test",
        "permutations",
        "random_directions",
    ]:
        value = getattr(args, key)
        if value is not None:
            config[key] = value
    if args.arms:
        config["arms"] = [value.strip() for value in args.arms.split(",") if value.strip()]
    if args.seeds:
        config["seeds"] = [int(value.strip()) for value in args.seeds.split(",") if value.strip()]
    valid_arms = set(PROFILES["confirmatory"]["arms"])
    if not config["arms"] or any(arm not in valid_arms for arm in config["arms"]):
        raise ValueError(f"arms must be chosen from {sorted(valid_arms)}")
    for key in ["n_train", "n_val", "n_eval"]:
        if config[key] % len(MODES):
            raise ValueError(f"{key} must be divisible by {len(MODES)}")
    for key in ["causal_calibration", "causal_test"]:
        if config[key] % len(CAUSAL_FAMILIES):
            raise ValueError(f"{key} must be divisible by {len(CAUSAL_FAMILIES)}")
    if config["hidden"] % config["heads"]:
        raise ValueError("hidden size must be divisible by attention heads")
    if len(config["arms"]) != len(set(config["arms"])):
        raise ValueError("arms must be unique")
    if len(config["seeds"]) != len(set(config["seeds"])):
        raise ValueError("model seeds must be unique")
    for key in ["n_train", "n_val", "n_eval", "epochs", "batch_size", "layers", "hidden", "heads", "intermediate", "causal_calibration", "causal_test", "permutations", "random_directions"]:
        if int(config[key]) <= 0:
            raise ValueError(f"{key} must be positive")
    if float(args.learning_rate) <= 0:
        raise ValueError("learning rate must be positive")
    config["learning_rate"] = args.learning_rate
    config["save_checkpoints"] = not args.no_checkpoints
    config["run_baselines"] = not args.no_baselines
    config["run_geometry"] = not args.no_geometry
    config["run_causal"] = not args.no_causal
    config["deterministic"] = not args.nondeterministic
    return config


def main() -> None:
    args = parse_args()
    config = resolve_config(args)
    args.seed = int(config["generator_seed"])
    output = args.output.resolve()
    output_has_files = output.exists() and any(output.iterdir())
    if args.resume and not output_has_files:
        raise RuntimeError(f"resume output does not exist or is empty: {output}")
    if not args.resume and output_has_files:
        raise RuntimeError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    (output / "checkpoints").mkdir(exist_ok=True)
    started = time.time()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was explicitly requested but torch.cuda.is_available() is false")
    if args.device == "cpu":
        device = torch.device("cpu")
    elif args.device == "cuda":
        device = torch.device("cuda")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.set_num_threads(min(8, os.cpu_count() or 1))
    print(f"device={device} profile={config['profile']} output={output}", flush=True)

    source_path = Path(__file__).resolve()
    protocol_path = source_path.with_name("EXPERIMENT_PROTOCOL.md")
    source_hash = sha256_file(source_path)
    protocol_hash = sha256_file(protocol_path)
    freeze_path = output / "PREOUTCOME_FREEZE.json"
    if args.resume:
        if not freeze_path.is_file():
            raise RuntimeError(f"resume requires the original pre-outcome freeze: {freeze_path}")
        freeze = read_json(freeze_path)
        if freeze.get("config") != config:
            raise RuntimeError("resume configuration does not exactly match PREOUTCOME_FREEZE.json")
        if int(freeze.get("generator_seed", -1)) != args.seed:
            raise RuntimeError("resume generator seed does not match PREOUTCOME_FREEZE.json")
        if freeze.get("protocol_sha256") != protocol_hash:
            raise RuntimeError("resume protocol hash differs from PREOUTCOME_FREEZE.json")
        if freeze.get("source_sha256") != source_hash:
            raise RuntimeError("resume source hash differs from PREOUTCOME_FREEZE.json; v0.3 permits source-exact resume only")
        provenance_path = output / "RESUME_PROVENANCE.json"
        if provenance_path.is_file():
            resume_provenance = read_json(provenance_path)
        else:
            resume_provenance = {
                "source_sha256": source_hash,
                "protocol_sha256": protocol_hash,
                "resume_policy": "source_protocol_config_and_dataset_exact",
                "attempts": [],
            }
        if resume_provenance.get("source_sha256") != source_hash:
            raise RuntimeError("resume source differs from the source recorded in RESUME_PROVENANCE.json")
        resume_provenance["attempts"].append({"started_unix": time.time(), "profile": config["profile"]})
        write_json(provenance_path, resume_provenance)
    else:
        freeze = {
            "created_before_training_unix": time.time(),
            "source_sha256": source_hash,
            "protocol_sha256": protocol_hash,
            "config": config,
            "generator_seed": args.seed,
        }
        write_json(freeze_path, freeze)

    print("generating executable datasets", flush=True)
    partition_mod = 100
    partition_buckets = {
        "train": set(range(0, 45)),
        "validation": set(range(45, 50)),
        "id": set(range(50, 55)),
        "length_ood": set(range(55, 65)),
        "motif_ood": set(range(65, 75)),
        "syntax_ood": set(range(75, 80)),
        "joint_ood": set(range(80, 90)),
        "codebook_id": set(range(90, 95)),
        "codebook_ood": set(range(95, 100)),
    }
    train = make_split(
        args.seed,
        config["n_train"],
        (2, 3, 4),
        bank="train",
        codebook_tokens=TRAIN_CODE_TOKENS,
        codebook_rate=0.30,
        partition_mod=partition_mod,
        partition_buckets=partition_buckets["train"],
    )
    blocked_structural = {row.structural_hash for row in train}
    blocked_alpha = {row.alpha_hash for row in train}

    def new_split(name: str, offset: int, lengths: tuple[int, ...], bank: str, motif: bool = False, code_tokens=None, code_rate=0.0):
        rows = make_split(
            args.seed + offset,
            config["n_eval"] if offset != 1 else config["n_val"],
            lengths,
            bank=bank,
            motif=motif,
            codebook_tokens=code_tokens,
            codebook_rate=code_rate,
            blocked_structural=blocked_structural,
            blocked_alpha=blocked_alpha,
            partition_mod=partition_mod,
            partition_buckets=partition_buckets[name],
        )
        blocked_structural.update(row.structural_hash for row in rows)
        blocked_alpha.update(row.alpha_hash for row in rows)
        return rows

    val = new_split("validation", 1, (2, 3, 4), "train")
    splits = {
        "id": new_split("id", 2, (2, 3, 4), "train"),
        "length_ood": new_split("length_ood", 3, (5, 6, 7), "train"),
        "motif_ood": new_split("motif_ood", 4, (3, 4, 5), "train", motif=True),
        "syntax_ood": new_split("syntax_ood", 5, (2, 3, 4), "held"),
        "joint_ood": new_split("joint_ood", 6, (5, 6, 7), "held", motif=True),
        "codebook_id": new_split("codebook_id", 7, (2, 3, 4), "train", code_tokens=TRAIN_CODE_TOKENS, code_rate=1.0),
        "codebook_ood": new_split("codebook_ood", 8, (2, 3, 4), "train", code_tokens=TEST_CODE_TOKENS, code_rate=1.0),
    }
    causal_calibration = make_causal_pairs(
        args.seed + 20,
        config["causal_calibration"],
        bank="train",
        difficulty="id",
        blocked_structural=blocked_structural,
        blocked_alpha=blocked_alpha,
    )
    blocked_structural.update(record.structural_hash for pair in causal_calibration for record in (pair.base, pair.counterfactual))
    blocked_alpha.update(record.alpha_hash for pair in causal_calibration for record in (pair.base, pair.counterfactual))
    causal_calibration_ids = {pair.case_id for pair in causal_calibration}
    causal_id_test = make_causal_pairs(
        args.seed + 21,
        config["causal_test"],
        bank="train",
        difficulty="id",
        blocked_case_ids=causal_calibration_ids,
        blocked_structural=blocked_structural,
        blocked_alpha=blocked_alpha,
    )
    blocked_structural.update(record.structural_hash for pair in causal_id_test for record in (pair.base, pair.counterfactual))
    blocked_alpha.update(record.alpha_hash for pair in causal_id_test for record in (pair.base, pair.counterfactual))
    causal_used_ids = causal_calibration_ids | {pair.case_id for pair in causal_id_test}
    causal_ood_test = make_causal_pairs(
        args.seed + 22,
        config["causal_test"],
        bank="held",
        difficulty="ood",
        blocked_case_ids=causal_used_ids,
        blocked_structural=blocked_structural,
        blocked_alpha=blocked_alpha,
    )
    all_causal_pairs = causal_calibration + causal_id_test + causal_ood_test
    causal_records = [pair.base for pair in all_causal_pairs] + [pair.counterfactual for pair in all_causal_pairs]
    vocab = build_vocab([train, val, *splits.values(), causal_records])
    max_len = 192
    encoded_lengths = [len(tokenize(row.text)) + 1 for row in train + val + [item for rows in splits.values() for item in rows] + causal_records]
    if max(encoded_lengths) > max_len:
        raise RuntimeError(f"max encoded length {max(encoded_lengths)} exceeds max_len {max_len}")
    if args.resume:
        require_matching_json(output / "vocab.json", vocab, "vocabulary")
    else:
        write_json(output / "vocab.json", vocab)
    audit = data_audit(train, splits)
    causal_banks = {
        "calibration_id": causal_calibration,
        "test_id": causal_id_test,
        "test_ood": causal_ood_test,
    }
    audit["causal_banks"] = {
        name: {
            "size": len(pairs),
            "unique_case_ids": len({pair.case_id for pair in pairs}),
            "family_counts": dict(sorted(Counter(pair.family for pair in pairs).items())),
            "counterfactual_length_counts": dict(sorted(Counter(pair.counterfactual.length for pair in pairs).items())),
        }
        for name, pairs in causal_banks.items()
    }
    audit["causal_case_overlap"] = {
        f"{left}__{right}": len(
            {pair.case_id for pair in causal_banks[left]}
            & {pair.case_id for pair in causal_banks[right]}
        )
        for index, left in enumerate(causal_banks)
        for right in list(causal_banks)[index + 1 :]
    }
    audit["causal_structural_overlap"] = {
        f"{left}__{right}": len(
            {
                record.structural_hash
                for pair in causal_banks[left]
                for record in (pair.base, pair.counterfactual)
            }
            & {
                record.structural_hash
                for pair in causal_banks[right]
                for record in (pair.base, pair.counterfactual)
            }
        )
        for index, left in enumerate(causal_banks)
        for right in list(causal_banks)[index + 1 :]
    }
    ordinary_structures = {
        row.structural_hash
        for rows in [train, val, *splits.values()]
        for row in rows
    }
    audit["causal_vs_ordinary_structural_overlap"] = {
        name: len(
            ordinary_structures
            & {
                record.structural_hash
                for pair in pairs
                for record in (pair.base, pair.counterfactual)
            }
        )
        for name, pairs in causal_banks.items()
    }
    audit["structural_partition"] = {
        "modulus": partition_mod,
        "buckets": {name: sorted(values) for name, values in partition_buckets.items()},
    }
    audit["tokenization"] = {
        "vocab_size": len(vocab),
        "max_len": max_len,
        "mean_encoded_length": float(np.mean(encoded_lengths)),
        "max_encoded_length": int(max(encoded_lengths)),
    }
    if args.resume:
        require_matching_json(output / "DATASET_AUDIT.json", audit, "dataset audit")
        if not (output / "sample_examples.jsonl").is_file():
            raise RuntimeError("resume requires sample_examples.jsonl from the original run")
        if not (output / "CAUSAL_CASES.jsonl").is_file():
            raise RuntimeError("resume requires CAUSAL_CASES.jsonl from the original run")
    else:
        write_json(output / "DATASET_AUDIT.json", audit)
        with (output / "sample_examples.jsonl").open("w", encoding="utf-8") as stream:
            for split_name, rows in {"train": train, "validation": val, **splits}.items():
                for row in rows[:5]:
                    stream.write(json.dumps({"split": split_name, **asdict(row)}) + "\n")
        with (output / "CAUSAL_CASES.jsonl").open("w", encoding="utf-8") as stream:
            for bank_name, pairs in causal_banks.items():
                for pair in pairs:
                    stream.write(json.dumps({"bank": bank_name, **asdict(pair)}) + "\n")
    dataset_audit_hash = sha256_file(output / "DATASET_AUDIT.json")

    train_ds = TraceDataset(train, vocab, max_len)
    val_ds = TraceDataset(val, vocab, max_len)
    split_ds = {name: TraceDataset(rows, vocab, max_len) for name, rows in splits.items()}
    model_config = BertConfig(
        vocab_size=len(vocab),
        hidden_size=config["hidden"],
        num_hidden_layers=config["layers"],
        num_attention_heads=config["heads"],
        intermediate_size=config["intermediate"],
        max_position_embeddings=max_len + 8,
        hidden_dropout_prob=0.10,
        attention_probs_dropout_prob=0.10,
        pad_token_id=vocab["[PAD]"],
    )
    if args.resume:
        require_matching_json(output / "model_config.json", model_config.to_dict(), "model configuration")
    else:
        write_json(output / "model_config.json", model_config.to_dict())

    baselines = {
        "majority": majority_baseline(train, splits),
        "exact_executor": exact_executor_baseline(splits),
    }
    print("running frozen controls", flush=True)
    if config["run_baselines"]:
        baselines["word_tfidf"] = text_baseline(train, splits, kind="word")
        baselines["char_tfidf"] = text_baseline(train, splits, kind="char")
        baselines["question_only"] = text_baseline(train, splits, kind="word", include_story=False)
        baselines["shuffled_label_tfidf"] = text_baseline(train, splits, kind="word", shuffle_labels=True)
        random_results, random_model = random_transformer_baseline(
            model_config,
            101,
            train,
            train_ds,
            splits,
            split_ds,
            device,
            config["batch_size"],
        )
        baselines["random_transformer"] = random_results
    else:
        set_seed(101)
        random_model = OSLBert(copy.deepcopy(model_config)).to(device)

    metrics_rows: list[dict] = []
    histories = defaultdict(dict)
    geometry_results = defaultdict(list)
    causal_results = defaultdict(list)
    orbit_results = defaultdict(list)
    parameter_count = sum(parameter.numel() for parameter in random_model.parameters())
    recovery = {
        "resumed": bool(args.resume),
        "loaded_checkpoints": [],
        "trained_checkpoints": [],
        "history_unavailable_for_loaded_checkpoints": [],
        "elapsed_scope": "resume_process_only" if args.resume else "complete_process",
    }
    for arm in config["arms"]:
        for model_seed in config["seeds"]:
            checkpoint_path = output / "checkpoints" / f"{arm}_seed{model_seed}.pt"
            if args.resume and checkpoint_path.is_file():
                print(f"loading completed checkpoint arm={arm} seed={model_seed}", flush=True)
                model, history, history_available = load_compatible_checkpoint(
                    checkpoint_path,
                    arm,
                    model_seed,
                    model_config,
                    vocab,
                    max_len,
                    source_hash,
                    protocol_hash,
                    dataset_audit_hash,
                    device,
                )
                recovery["loaded_checkpoints"].append(f"{arm}_seed{model_seed}")
                if not history_available:
                    recovery["history_unavailable_for_loaded_checkpoints"].append(f"{arm}_seed{model_seed}")
            else:
                print(f"training arm={arm} seed={model_seed}", flush=True)
                model, history = train_arm(
                    arm,
                    model_seed,
                    model_config,
                    train_ds,
                    val_ds,
                    train,
                    device,
                    config["epochs"],
                    config["batch_size"],
                    config["learning_rate"],
                    config["deterministic"],
                )
                recovery["trained_checkpoints"].append(f"{arm}_seed{model_seed}")
            histories[arm][str(model_seed)] = history
            if config["save_checkpoints"] and not (args.resume and checkpoint_path.is_file()):
                checkpoint = {
                    "checkpoint_schema_version": CHECKPOINT_SCHEMA_VERSION,
                    "arm": arm,
                    "seed": model_seed,
                    "model_state_dict": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                    "bert_config": model_config.to_dict(),
                    "vocab": vocab,
                    "max_len": max_len,
                    "source_sha256": source_hash,
                    "protocol_sha256": protocol_hash,
                    "dataset_audit_sha256": dataset_audit_hash,
                    "history": history,
                }
                atomic_torch_save(checkpoint, checkpoint_path)
            print(f"evaluating held-out splits arm={arm} seed={model_seed}", flush=True)
            for split_name, dataset in split_ds.items():
                result = evaluate_model(model, dataset, device, config["batch_size"])
                metrics_rows.append({"arm": arm, "seed": model_seed, "split": split_name, **result})
            print(f"running nuisance-orbit audit arm={arm} seed={model_seed}", flush=True)
            orbit_results[arm].append(
                {
                    "seed": model_seed,
                    **orbit_audit(model, splits["id"], vocab, max_len, device, config["batch_size"]),
                }
            )
            if config["run_geometry"]:
                print(f"running geometry audit arm={arm} seed={model_seed}", flush=True)
                geometry_results[arm].append(
                    {
                        "seed": model_seed,
                        **geometry_audit(
                            model,
                            random_model,
                            splits["joint_ood"],
                            split_ds["joint_ood"],
                            device,
                            config["batch_size"],
                            config["permutations"],
                            seed=args.seed + model_seed,
                        ),
                    }
                )
            if config["run_causal"]:
                print(f"running causal audit arm={arm} seed={model_seed}", flush=True)
                causal_results[arm].append(
                    {
                        "seed": model_seed,
                        **causal_audit(
                            model,
                            causal_calibration,
                            causal_id_test,
                            causal_ood_test,
                            vocab,
                            max_len,
                            device,
                            config["batch_size"],
                            config["random_directions"],
                            max(5, int(round(0.10 * config["causal_test"]))),
                            seed=args.seed + 1000 + model_seed,
                        ),
                    }
                )
            print(f"completed arm={arm} seed={model_seed}", flush=True)
            del model
            if device.type == "cuda":
                torch.cuda.empty_cache()

    metric_fields = sorted({key for row in metrics_rows for key in row})
    with (output / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows(metrics_rows)
    write_json(output / "training_history.json", histories)
    trained_mean = average_trained_metrics(metrics_rows)
    import transformers

    summary = {
        "release_version": RELEASE_VERSION,
        "config": config,
        "recovery": recovery,
        "environment": {
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
            "determinism": "strict_eager_math_attention" if config["deterministic"] else "disabled",
            "deterministic_algorithms": bool(torch.are_deterministic_algorithms_enabled()),
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark) if hasattr(torch.backends, "cudnn") else None,
            "cudnn_deterministic": bool(torch.backends.cudnn.deterministic) if hasattr(torch.backends, "cudnn") else None,
            "cuda_matmul_tf32": bool(torch.backends.cuda.matmul.allow_tf32) if hasattr(torch.backends, "cuda") else None,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "numpy": np.__version__,
            "python": sys.version,
            "parameters_per_model": parameter_count,
            "elapsed_seconds": time.time() - started,
        },
        "dataset": audit,
        "baseline_metadata": {
            "classifier": "RidgeClassifier",
            "alpha": 1.0,
            "solver": "lsqr",
            "tolerance": 1e-6,
            "class_weight": "balanced",
            "convergence_warning_policy": "not iterative under a fixed iteration cap",
        },
        "baselines": baselines,
        "trained_mean": trained_mean,
        "orbit": {key: value for key, value in orbit_results.items()},
        "geometry": {key: value for key, value in geometry_results.items()},
        "causal": {key: value for key, value in causal_results.items()},
    }
    adjudication = adjudicate(summary)
    summary["adjudication"] = adjudication
    write_json(output / "summary.json", summary)
    write_json(output / "FINAL_ADJUDICATION.json", adjudication)
    make_plots(output, summary)
    write_report(output, summary, adjudication)
    (output / "RETURN_RESULTS_INSTRUCTIONS.txt").write_text(
        "Return the file RETURN_THIS_OSL_HF_RESULTS.zip to ChatGPT. It contains the configuration, frozen protocol hashes, metrics, controls, causal audit, figures, and final adjudication. Model checkpoints remain outside the compact ZIP.\n",
        encoding="utf-8",
    )
    if args.resume:
        provenance_path = output / "RESUME_PROVENANCE.json"
        resume_provenance = read_json(provenance_path)
        resume_provenance["attempts"][-1].update(
            {
                "completed_unix": time.time(),
                "loaded_checkpoints": recovery["loaded_checkpoints"],
                "trained_checkpoints": recovery["trained_checkpoints"],
                "history_unavailable_for_loaded_checkpoints": recovery["history_unavailable_for_loaded_checkpoints"],
            }
        )
        write_json(provenance_path, resume_provenance)
    checkpoint_files = sorted((output / "checkpoints").glob("*.pt"))
    checkpoint_hashes = [sha256_file(path) for path in checkpoint_files]
    if len(checkpoint_hashes) != len(set(checkpoint_hashes)):
        raise RuntimeError("two trained checkpoints have identical SHA-256 hashes")
    (output / "CHECKPOINT_SHA256SUMS.txt").write_text(
        "\n".join(
            f"{digest}  checkpoints/{path.name}"
            for path, digest in zip(checkpoint_files, checkpoint_hashes)
        )
        + ("\n" if checkpoint_files else ""),
        encoding="utf-8",
    )
    manifest_lines = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name not in (
            "SHA256SUMS.txt",
            "RETURN_THIS_OSL_HF_RESULTS.zip",
            "RETURN_THIS_OSL_HF_RESULTS.zip.sha256",
        ):
            manifest_lines.append(f"{sha256_file(path)}  {path.relative_to(output).as_posix()}")
    (output / "SHA256SUMS.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    compact_zip = write_compact_results_zip(output)
    (output / "RETURN_THIS_OSL_HF_RESULTS.zip.sha256").write_text(
        f"{sha256_file(compact_zip)}  {compact_zip.name}\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": adjudication["conclusion"], "compact_results_zip": str(compact_zip), "sha256": sha256_file(compact_zip)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
