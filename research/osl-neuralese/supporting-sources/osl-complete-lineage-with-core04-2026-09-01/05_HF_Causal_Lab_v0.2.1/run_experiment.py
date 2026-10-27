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

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
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
LINKED_MOTIF = ("TELL", "INFER")
TRAIN_CODE_TOKENS = ["dax", "mip", "rav", "sol", "vex"]
TEST_CODE_TOKENS = ["krel", "nuv", "pax", "tob", "zesh"]
LABEL_KEYS = ["mode", "origin", "access", "direct", "authorized", "eligible"]
LABEL_DIMS = {"mode": len(MODES), "origin": len(AGENTS) + 1, "access": 2, "direct": 2, "authorized": 2, "eligible": 2}


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
    next_op: int
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
    split_at = rng.randrange(len(events)) if events else 0
    prefix_events = events[:split_at]
    next_events = events[: split_at + 1]
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
        next_op=OP_ID[events[split_at].op],
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


def make_causal_pairs(seed: int, n: int, bank: str = "held") -> list[CausalPair]:
    rng = random.Random(seed)
    pairs: list[CausalPair] = []
    for _ in range(n):
        source = rng.randrange(len(AGENTS))
        receiver = rng.choice([a for a in range(len(AGENTS)) if a != source])
        fact = rng.randrange(len(FACTS))
        protected_agent = rng.choice([a for a in range(len(AGENTS)) if a not in (source, receiver)])
        protected_fact = rng.choice([f for f in range(len(FACTS)) if f != fact])
        target_events = [
            Event("OBSERVE", source, fact),
            Event("TELL", source, fact, other=receiver),
        ]
        protected_events = [
            Event("OBSERVE", protected_agent, protected_fact),
            Event("AUTHORIZE", protected_agent, protected_fact),
        ]
        base_events = target_events + protected_events if rng.random() < 0.5 else protected_events + target_events
        base_state = execute(base_events)
        counter_events = base_events + [Event("OBSERVE", receiver, fact)]
        counter_state = execute(counter_events)
        if base_state is None or counter_state is None:
            raise AssertionError("invalid causal pair")
        base = make_record(base_events, base_state, receiver, fact, rng, bank=bank, surface_kind="causal_base")
        counter = make_record(counter_events, counter_state, receiver, fact, rng, bank=bank, surface_kind="causal_counterfactual")
        pairs.append(CausalPair(base, counter, protected_agent, protected_fact))
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
                    "next_op": row.next_op,
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
        self.backbone = BertModel(config, add_pooling_layer=False)
        self.agent_embedding = nn.Embedding(len(AGENTS), config.hidden_size)
        self.fact_embedding = nn.Embedding(len(FACTS), config.hidden_size)
        self.cell_norm = nn.LayerNorm(config.hidden_size)
        self.cell_mlp = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.LayerNorm(config.hidden_size),
        )
        self.heads = nn.ModuleDict({key: nn.Linear(config.hidden_size, dim) for key, dim in LABEL_DIMS.items()})
        self.transitions = nn.ModuleList([nn.Linear(config.hidden_size, config.hidden_size) for _ in OPS])

    def encode_story(self, ids: torch.Tensor, mask: torch.Tensor, output_hidden_states: bool = False):
        output = self.backbone(
            input_ids=ids,
            attention_mask=mask,
            output_hidden_states=output_hidden_states,
            return_dict=True,
        )
        return output.last_hidden_state[:, 0], output.hidden_states

    def cell_representation(self, z: torch.Tensor, agent: torch.Tensor, fact: torch.Tensor) -> torch.Tensor:
        h = z + self.agent_embedding(agent) + self.fact_embedding(fact)
        return self.cell_mlp(self.cell_norm(h))

    def predict_cell(self, z: torch.Tensor, agent: torch.Tensor, fact: torch.Tensor) -> dict[str, torch.Tensor]:
        h = self.cell_representation(z, agent, fact)
        return {key: head(h) for key, head in self.heads.items()}

    def predict_all(self, z: torch.Tensor) -> dict[str, torch.Tensor]:
        batch = z.shape[0]
        device = z.device
        agent = torch.arange(len(AGENTS), device=device).repeat_interleave(len(FACTS))
        fact = torch.arange(len(FACTS), device=device).repeat(len(AGENTS))
        h = z[:, None, :] + self.agent_embedding(agent)[None, :, :] + self.fact_embedding(fact)[None, :, :]
        h = self.cell_mlp(self.cell_norm(h))
        return {key: head(h) for key, head in self.heads.items()}


def set_seed(seed: int, deterministic: bool = True) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.use_deterministic_algorithms(True, warn_only=True)
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


def full_state_loss(
    logits: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    class_weights: dict[str, torch.Tensor],
) -> torch.Tensor:
    mode = nn.functional.cross_entropy(logits["mode"].flatten(0, 1), batch["full_mode"].flatten(), weight=class_weights["mode"])
    origin = nn.functional.cross_entropy(logits["origin"].flatten(0, 1), batch["full_origin"].flatten(), weight=class_weights["origin"])
    auth = nn.functional.cross_entropy(
        logits["authorized"].flatten(0, 1),
        batch["full_authorized"].flatten(),
        weight=class_weights["authorized"],
    )
    return mode + 0.55 * origin + 0.35 * auth


def equivalence_loss(z: torch.Tensor, z_alt: torch.Tensor, temperature: float = 0.12) -> torch.Tensor:
    left = nn.functional.normalize(z, dim=-1)
    right = nn.functional.normalize(z_alt, dim=-1)
    logits = left @ right.T / temperature
    labels = torch.arange(len(z), device=z.device)
    return 0.5 * (nn.functional.cross_entropy(logits, labels) + nn.functional.cross_entropy(logits.T, labels))


def transition_loss(model: OSLBert, z_prefix: torch.Tensor, z_next: torch.Tensor, next_op: torch.Tensor) -> torch.Tensor:
    if next_op.ndim != 1 or len(next_op) != len(z_prefix):
        raise ValueError("next_op must contain one operator index per representation")
    if bool(((next_op < 0) | (next_op >= len(model.transitions))).any()):
        raise ValueError("next_op contains an invalid operator index")
    # Keep this small auxiliary objective in FP32.  On CUDA, the surrounding
    # autocast region can return a half-precision encoder state while an
    # operator Linear returns FP32.  Indexed assignment requires identical
    # dtypes, and the mismatch only appears on the mixed-precision path.
    with torch.autocast(device_type=z_prefix.device.type, enabled=False):
        prefix = z_prefix.float()
        target = z_next.float()
        predicted = torch.empty_like(prefix)
        for op_index, transition in enumerate(model.transitions):
            mask = next_op == op_index
            if mask.any():
                predicted[mask] = transition(prefix[mask])
        cosine = 1.0 - nn.functional.cosine_similarity(predicted, target, dim=-1).mean()
        scale = nn.functional.mse_loss(predicted.norm(dim=-1), target.norm(dim=-1)) / float(target.shape[-1])
        return cosine + 0.05 * scale


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
    layer_chunks = None
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    for raw_batch in loader:
        batch = move_batch(raw_batch, device)
        z, hidden = model.encode_story(batch["ids"], batch["mask"], output_hidden_states=collect_layers)
        logits = model.predict_cell(z, batch["query_agent"], batch["query_fact"])
        all_logits = model.predict_all(z)
        for key in LABEL_KEYS:
            labels[key].append(batch[key].cpu().numpy())
            preds[key].append(logits[key].argmax(-1).cpu().numpy())
        for key in full_labels:
            full_labels[key].append(batch[f"full_{key}"].cpu().numpy())
            full_preds[key].append(all_logits[key].argmax(-1).cpu().numpy())
        zs.append(z.cpu().numpy())
        if collect_alt:
            alt_z, _ = model.encode_story(batch["alt_ids"], batch["alt_mask"], output_hidden_states=False)
            alt_zs.append(alt_z.cpu().numpy())
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
    best_state = None
    history = []
    for epoch in range(epochs):
        generator = torch.Generator()
        generator.manual_seed(seed * 1000 + epoch)
        loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, generator=generator, num_workers=0, pin_memory=use_amp)
        model.train()
        loss_sum = 0.0
        examples_seen = 0
        for raw_batch in loader:
            batch = move_batch(raw_batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                z, _ = model.encode_story(batch["ids"], batch["mask"])
                logits = model.predict_cell(z, batch["query_agent"], batch["query_fact"])
                loss = query_loss(logits, batch, query_weights)
                if arm in ("state_supervised", "equivalence", "operator_regularized"):
                    loss = loss + 0.3 * full_state_loss(model.predict_all(z), batch, class_weights)
                if arm in ("equivalence", "operator_regularized"):
                    z_alt, _ = model.encode_story(batch["alt_ids"], batch["alt_mask"])
                    loss = loss + 0.08 * equivalence_loss(z, z_alt)
                if arm == "operator_regularized":
                    z_prefix, _ = model.encode_story(batch["prefix_ids"], batch["prefix_mask"])
                    z_next, _ = model.encode_story(batch["next_ids"], batch["next_mask"])
                    loss = loss + 0.08 * transition_loss(model, z_prefix, z_next, batch["next_op"])
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            loss_sum += float(loss.detach().cpu()) * len(batch["ids"])
            examples_seen += len(batch["ids"])
        val_metrics = evaluate_model(model, val_ds, device, batch_size)
        score = val_metrics["mode_balanced_accuracy"]
        history.append({"epoch": epoch + 1, "train_loss": loss_sum / max(examples_seen, 1), **val_metrics})
        print(
            f"arm={arm} seed={seed} epoch={epoch + 1}/{epochs} "
            f"loss={loss_sum / max(examples_seen, 1):.4f} "
            f"val_mode_balanced={score:.4f} val_joint={val_metrics['joint_six_accuracy']:.4f}",
            flush=True,
        )
        if score > best_score:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if best_state is None:
        raise RuntimeError("training produced no checkpoint")
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
    model = LogisticRegression(max_iter=600, class_weight="balanced", random_state=seed, solver="lbfgs")
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
        z, _ = model.encode_story(batch["ids"], batch["mask"])
        chunks.append(z.cpu().numpy())
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
    z_train = story_features(model, train_ds, device, batch_size)
    x_train = query_features(z_train, train)
    train_labels = labels_matrix(train)
    classifiers = {key: fit_classifier(x_train, train_labels[key], seed=seed) for key in LABEL_KEYS}
    results = {}
    for split, rows in splits.items():
        z = story_features(model, split_ds[split], device, batch_size)
        x = query_features(z, rows)
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

    def triplet(collected: dict) -> dict[str, float]:
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
        "trained_triplet": triplet(trained),
        "random_triplet": triplet(random_collected),
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
def encode_record_list(
    model: OSLBert,
    records: list[Record],
    vocab: dict[str, int],
    max_len: int,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    return story_features(model, TraceDataset(records, vocab, max_len), device, batch_size)


@torch.no_grad()
def predict_bundles_from_z(
    model: OSLBert,
    z: np.ndarray,
    agents: np.ndarray,
    facts: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> dict[str, np.ndarray]:
    chunks = {key: [] for key in LABEL_KEYS}
    for start in range(0, len(z), batch_size):
        stop = min(start + batch_size, len(z))
        z_t = torch.tensor(z[start:stop], dtype=torch.float32, device=device)
        a_t = torch.tensor(agents[start:stop], dtype=torch.long, device=device)
        f_t = torch.tensor(facts[start:stop], dtype=torch.long, device=device)
        logits = model.predict_cell(z_t, a_t, f_t)
        for key in LABEL_KEYS:
            chunks[key].append(logits[key].argmax(-1).cpu().numpy())
    return {key: np.concatenate(value) for key, value in chunks.items()}


def truth_bundles(pairs: list[CausalPair], which: str, protected: bool) -> dict[str, np.ndarray]:
    out = {key: [] for key in LABEL_KEYS}
    for pair in pairs:
        row = pair.base if which == "base" else pair.counterfactual
        if protected:
            labels = record_cell_labels(row, pair.protected_agent, pair.protected_fact)
        else:
            labels = record_cell_labels(row, row.query_agent, row.query_fact)
        for key in LABEL_KEYS:
            out[key].append(labels[key])
    return {key: np.array(value, dtype=np.int64) for key, value in out.items()}


def bundle_exact(pred: dict[str, np.ndarray], truth: dict[str, np.ndarray]) -> np.ndarray:
    return np.logical_and.reduce([pred[key] == truth[key] for key in LABEL_KEYS])


def intervention_score(
    model: OSLBert,
    pairs: list[CausalPair],
    z_base: np.ndarray,
    z_counter: np.ndarray,
    direction: np.ndarray,
    alpha: float,
    device: torch.device,
    batch_size: int,
) -> dict[str, float | int]:
    target_agents = np.array([pair.base.query_agent for pair in pairs], dtype=np.int64)
    target_facts = np.array([pair.base.query_fact for pair in pairs], dtype=np.int64)
    protected_agents = np.array([pair.protected_agent for pair in pairs], dtype=np.int64)
    protected_facts = np.array([pair.protected_fact for pair in pairs], dtype=np.int64)
    patched = z_base + alpha * direction[None, :]
    base_target = predict_bundles_from_z(model, z_base, target_agents, target_facts, device, batch_size)
    counter_target = predict_bundles_from_z(model, z_counter, target_agents, target_facts, device, batch_size)
    patched_target = predict_bundles_from_z(model, patched, target_agents, target_facts, device, batch_size)
    base_protected = predict_bundles_from_z(model, z_base, protected_agents, protected_facts, device, batch_size)
    counter_protected = predict_bundles_from_z(model, z_counter, protected_agents, protected_facts, device, batch_size)
    patched_protected = predict_bundles_from_z(model, patched, protected_agents, protected_facts, device, batch_size)

    truth_base_target = truth_bundles(pairs, "base", protected=False)
    truth_counter_target = truth_bundles(pairs, "counter", protected=False)
    truth_base_protected = truth_bundles(pairs, "base", protected=True)
    truth_counter_protected = truth_bundles(pairs, "counter", protected=True)

    eligible = (
        bundle_exact(base_target, truth_base_target)
        & bundle_exact(counter_target, truth_counter_target)
        & bundle_exact(base_protected, truth_base_protected)
        & bundle_exact(counter_protected, truth_counter_protected)
    )
    target_success = bundle_exact(patched_target, truth_counter_target)
    protected_correct = bundle_exact(patched_protected, truth_base_protected)
    protected_prediction_retained = np.logical_and.reduce(
        [patched_protected[key] == base_protected[key] for key in LABEL_KEYS]
    )
    coherent = target_success & protected_correct & protected_prediction_retained
    changed_required = (
        (patched_target["mode"] == truth_counter_target["mode"])
        & (patched_target["direct"] == truth_counter_target["direct"])
    )
    unchanged_required = np.logical_and.reduce(
        [
            patched_target[key] == truth_counter_target[key]
            for key in ["origin", "access", "authorized", "eligible"]
        ]
    )
    eligible_count = int(eligible.sum())
    return {
        "alpha": float(alpha),
        "pairs": len(pairs),
        "eligible_pairs": eligible_count,
        "eligibility_rate": float(eligible.mean()),
        "all_pair_target_exact": float(target_success.mean()),
        "all_pair_protected_retention": float(protected_prediction_retained.mean()),
        "all_pair_coherent": float(coherent.mean()),
        "required_change_accuracy": float(changed_required.mean()),
        "required_invariant_accuracy": float(unchanged_required.mean()),
        "eligible_target_exact": float(target_success[eligible].mean()) if eligible_count else 0.0,
        "eligible_protected_retention": float(protected_prediction_retained[eligible].mean()) if eligible_count else 0.0,
        "eligible_coherent": float(coherent[eligible].mean()) if eligible_count else 0.0,
    }


def causal_audit(
    model: OSLBert,
    calibration_pairs: list[CausalPair],
    test_pairs: list[CausalPair],
    vocab: dict[str, int],
    max_len: int,
    device: torch.device,
    batch_size: int,
    random_directions: int,
    seed: int,
) -> dict:
    cal_base = [pair.base for pair in calibration_pairs]
    cal_counter = [pair.counterfactual for pair in calibration_pairs]
    test_base = [pair.base for pair in test_pairs]
    test_counter = [pair.counterfactual for pair in test_pairs]
    z_cal_base = encode_record_list(model, cal_base, vocab, max_len, device, batch_size)
    z_cal_counter = encode_record_list(model, cal_counter, vocab, max_len, device, batch_size)
    z_test_base = encode_record_list(model, test_base, vocab, max_len, device, batch_size)
    z_test_counter = encode_record_list(model, test_counter, vocab, max_len, device, batch_size)
    direction = (z_cal_counter - z_cal_base).mean(axis=0)
    direction_norm = float(np.linalg.norm(direction))
    if direction_norm < 1e-12:
        return {"status": "degenerate_direction", "direction_norm": direction_norm}
    alpha_grid = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    calibration_scores = []
    for alpha in alpha_grid:
        score = intervention_score(model, calibration_pairs, z_cal_base, z_cal_counter, direction, alpha, device, batch_size)
        calibration_scores.append(score)
    best = max(
        calibration_scores,
        key=lambda score: (
            score["eligible_coherent"],
            score["all_pair_coherent"],
            score["eligible_protected_retention"],
            -abs(score["alpha"] - 1.0),
        ),
    )
    targeted = intervention_score(
        model,
        test_pairs,
        z_test_base,
        z_test_counter,
        direction,
        float(best["alpha"]),
        device,
        batch_size,
    )
    rng = np.random.default_rng(seed)
    random_scores = []
    for _ in range(random_directions):
        random_direction = rng.normal(size=direction.shape)
        random_direction *= direction_norm / (np.linalg.norm(random_direction) + 1e-12)
        random_scores.append(
            intervention_score(
                model,
                test_pairs,
                z_test_base,
                z_test_counter,
                random_direction,
                float(best["alpha"]),
                device,
                batch_size,
            )
        )
    random_coherent = np.array([score["eligible_coherent"] for score in random_scores])
    random_retention = np.array([score["eligible_protected_retention"] for score in random_scores])
    return {
        "status": "ok",
        "direction_norm": direction_norm,
        "selected_alpha": float(best["alpha"]),
        "calibration_scores": calibration_scores,
        "targeted_test": targeted,
        "random_control": {
            "directions": random_directions,
            "eligible_coherent_mean": float(random_coherent.mean()),
            "eligible_coherent_max": float(random_coherent.max()),
            "eligible_protected_retention_mean": float(random_retention.mean()),
            "eligible_protected_retention_min": float(random_retention.min()),
        },
    }


PROFILES = {
    "smoke": {
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
        "arms": ["answer_only", "state_supervised", "equivalence", "operator_regularized"],
    },
    "pilot": {
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
        "arms": ["answer_only", "state_supervised", "equivalence", "operator_regularized"],
    },
    "full": {
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
        "arms": ["answer_only", "state_supervised", "equivalence", "operator_regularized"],
    },
    "confirmatory": {
        "n_train": 30000,
        "n_val": 3000,
        "n_eval": 3000,
        "epochs": 12,
        "seeds": [11, 29, 47, 83, 131],
        "layers": 4,
        "hidden": 256,
        "heads": 8,
        "intermediate": 768,
        "batch_size": 64,
        "causal_calibration": 500,
        "causal_test": 1200,
        "permutations": 500,
        "random_directions": 80,
        "arms": ["answer_only", "state_supervised", "equivalence", "operator_regularized"],
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
    path.write_text(json.dumps(value, indent=2, default=json_default), encoding="utf-8")


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
    device: torch.device,
) -> tuple[OSLBert, list[dict], bool]:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    if checkpoint.get("arm") != arm or int(checkpoint.get("seed", -1)) != seed:
        raise RuntimeError(f"checkpoint identity mismatch: {path}")
    if checkpoint.get("vocab") != vocab or int(checkpoint.get("max_len", -1)) != max_len:
        raise RuntimeError(f"checkpoint vocabulary or sequence length mismatch: {path}")
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
    if "id" not in answer or "joint_ood" not in answer:
        return {"status": "incomplete", "strong_operator_evidence": False}
    shortcut_systems = [name for name in baselines if name not in ("exact_executor",)]
    strongest_joint = max(
        baselines[name]["joint_ood"]["mode_balanced_accuracy"] for name in shortcut_systems
    )
    geometry_rows = summary["geometry"].get("answer_only", [])
    causal_rows = [row for row in summary["causal"].get("answer_only", []) if row.get("status") == "ok"]
    triplet = float(np.mean([row["trained_triplet"]["accuracy"] for row in geometry_rows])) if geometry_rows else 0.0
    random_triplet = float(np.mean([row["random_triplet"]["accuracy"] for row in geometry_rows])) if geometry_rows else 0.0
    eligibility = float(np.mean([row["targeted_test"]["eligibility_rate"] for row in causal_rows])) if causal_rows else 0.0
    coherent = float(np.mean([row["targeted_test"]["eligible_coherent"] for row in causal_rows])) if causal_rows else 0.0
    retention = float(np.mean([row["targeted_test"]["eligible_protected_retention"] for row in causal_rows])) if causal_rows else 0.0
    random_max = float(np.mean([row["random_control"]["eligible_coherent_max"] for row in causal_rows])) if causal_rows else 0.0
    gates = {
        "id_capacity": answer["id"]["mode_balanced_accuracy"] >= 0.85,
        "joint_ood_mode": answer["joint_ood"]["mode_balanced_accuracy"] >= 0.80,
        "joint_ood_six_output": answer["joint_ood"]["joint_six_accuracy"] >= 0.60,
        "shortcut_advantage": answer["joint_ood"]["mode_balanced_accuracy"] - strongest_joint >= 0.10,
        "formal_triplet": triplet >= 0.65 and triplet - random_triplet >= 0.10,
        "causal_eligibility": eligibility >= 0.70,
        "causal_coherence": coherent >= 0.50,
        "protected_retention": retention >= 0.95,
        "causal_control_advantage": coherent - random_max >= 0.20,
    }
    strong = all(gates.values())
    behavior = gates["id_capacity"] and gates["joint_ood_mode"] and gates["joint_ood_six_output"] and gates["shortcut_advantage"]
    geometry = gates["formal_triplet"]
    causal = gates["causal_eligibility"] and gates["causal_coherence"] and gates["protected_retention"] and gates["causal_control_advantage"]
    if strong:
        conclusion = "The answer-only arm passed the frozen behavioral, geometry, and selective causal gates. This is strong evidence for a task-induced reusable operator abstraction in this synthetic world."
    elif behavior and geometry:
        conclusion = "The answer-only arm showed systematic behavior and operator-relevant geometry, but it did not pass the selective causal gates. This supports a partially organized representation, not a causal operator language."
    elif behavior:
        conclusion = "The answer-only arm passed behavioral gates but not the full geometry and causal conjunction. This supports systematic sentence-based reasoning, not an internal operator language."
    else:
        conclusion = "The answer-only arm did not pass the frozen behavioral conjunction. This configuration does not demonstrate a reusable operator-symbolic language."
    return {
        "status": "complete",
        "strong_operator_evidence": strong,
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
            "causal_eligibility": eligibility,
            "eligible_coherent": coherent,
            "protected_retention": retention,
            "random_coherent_max": random_max,
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
        targeted = []
        controls = []
        retention = []
        for arm in causal_arms:
            rows = [row for row in causal[arm] if row.get("status") == "ok"]
            targeted.append(np.mean([row["targeted_test"]["eligible_coherent"] for row in rows]))
            controls.append(np.mean([row["random_control"]["eligible_coherent_max"] for row in rows]))
            retention.append(np.mean([row["targeted_test"]["eligible_protected_retention"] for row in rows]))
        fig, ax = plt.subplots(figsize=(9, 4.8))
        x = np.arange(len(causal_arms))
        ax.bar(x - 0.25, targeted, 0.25, label="targeted coherence")
        ax.bar(x, controls, 0.25, label="best random control")
        ax.bar(x + 0.25, retention, 0.25, label="protected retention")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Eligible-pair rate")
        ax.set_xticks(x, [name.replace("_", "\n") for name in causal_arms])
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(output / "causal_intervention.png", bbox_inches="tight")
        plt.close(fig)


def write_report(output: Path, summary: dict, adjudication: dict) -> None:
    split_order = ["id", "length_ood", "motif_ood", "syntax_ood", "joint_ood", "codebook_id", "codebook_ood"]
    elapsed_label = "Resume-process elapsed seconds" if summary.get("recovery", {}).get("resumed") else "Elapsed seconds"
    lines = [
        "# OSL Hugging Face causal and compositional test",
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
            "- The original pre-outcome freeze was preserved. RESUME_PROVENANCE.json records the post-start compatibility repair.",
            "- This recovered run remains exploratory. A strict confirmatory replication should start cleanly from the repaired source.",
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
            "## Communicated-to-observed intervention",
            "",
            "| Arm | Eligible pairs | Coherent conversion | Protected retention | Best random coherence |",
            "|---|---:|---:|---:|---:|",
        ]
        for arm, raw_rows in summary["causal"].items():
            rows = [row for row in raw_rows if row.get("status") == "ok"]
            if not rows:
                lines.append(f"| {arm} | 0.00% | 0.00% | 0.00% | 0.00% |")
                continue
            eligibility = np.mean([row["targeted_test"]["eligibility_rate"] for row in rows])
            coherent = np.mean([row["targeted_test"]["eligible_coherent"] for row in rows])
            retention = np.mean([row["targeted_test"]["eligible_protected_retention"] for row in rows])
            random_control = np.mean([row["random_control"]["eligible_coherent_max"] for row in rows])
            lines.append(f"| {arm} | {100 * eligibility:.2f}% | {100 * coherent:.2f}% | {100 * retention:.2f}% | {100 * random_control:.2f}% |")
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
    for gate, passed in adjudication.get("gates", {}).items():
        lines.append(f"- {'PASS' if passed else 'FAIL'}: `{gate}`")
    lines += [
        "",
        "## Interpretation discipline",
        "",
        "Behavioral accuracy alone does not establish an internal operator language. CKA, probes, and affine predictability are supporting diagnostics only. The strongest claim requires held-out composition, same-answer formal triplets, and selective causal conversion to pass together against lexical and random-feature controls.",
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
    parser.add_argument("--seed", type=int, default=731)
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
    parser.add_argument("--arms", type=str, help="comma-separated subset of answer_only,state_supervised,equivalence,operator_regularized")
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
    if config["hidden"] % config["heads"]:
        raise ValueError("hidden size must be divisible by attention heads")
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
        provenance_path = output / "RESUME_PROVENANCE.json"
        if provenance_path.is_file():
            resume_provenance = read_json(provenance_path)
        else:
            resume_provenance = {
                "original_frozen_source_sha256": freeze.get("source_sha256"),
                "patched_source_sha256": source_hash,
                "protocol_sha256": protocol_hash,
                "reason": "post-start CUDA mixed-precision compatibility hotfix in transition_loss",
                "compatibility_and_recovery_changes": [
                    "transition regularization is evaluated in FP32 outside CUDA autocast",
                    "completed checkpoints can be loaded and re-evaluated without retraining",
                    "checkpoint writes are atomic and new checkpoints retain training history",
                    "compact-result checksums cover only files actually present in the return ZIP",
                    "result verification checks every configured arm, seed, and split",
                ],
                "protocol_objectives_and_gates_changed": False,
                "reproducibility_note": "The original seeded warn-only deterministic setting is preserved. CUDA attention may remain nondeterministic, as reported by PyTorch.",
                "baseline_note": "The frozen logistic baseline settings are preserved. Any convergence warnings must be considered when interpreting shortcut-advantage results.",
                "strict_confirmatory_note": "A clean start from the patched source is required before treating a later run as a strict confirmatory replication.",
                "attempts": [],
            }
        if resume_provenance.get("patched_source_sha256") != source_hash:
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
    causal_calibration = make_causal_pairs(args.seed + 20, config["causal_calibration"], bank="held")
    causal_test = make_causal_pairs(args.seed + 21, config["causal_test"], bank="held")
    causal_records = [pair.base for pair in causal_calibration + causal_test] + [pair.counterfactual for pair in causal_calibration + causal_test]
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
    else:
        write_json(output / "DATASET_AUDIT.json", audit)
        with (output / "sample_examples.jsonl").open("w", encoding="utf-8") as stream:
            for split_name, rows in {"train": train, "validation": val, **splits}.items():
                for row in rows[:5]:
                    stream.write(json.dumps({"split": split_name, **asdict(row)}) + "\n")

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
                    "arm": arm,
                    "seed": model_seed,
                    "model_state_dict": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                    "bert_config": model_config.to_dict(),
                    "vocab": vocab,
                    "max_len": max_len,
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
                            causal_test,
                            vocab,
                            max_len,
                            device,
                            config["batch_size"],
                            config["random_directions"],
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
        "config": config,
        "recovery": recovery,
        "environment": {
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
            "determinism": "seeded_warn_only" if config["deterministic"] else "disabled",
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "numpy": np.__version__,
            "python": sys.version,
            "parameters_per_model": parameter_count,
            "elapsed_seconds": time.time() - started,
        },
        "dataset": audit,
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
