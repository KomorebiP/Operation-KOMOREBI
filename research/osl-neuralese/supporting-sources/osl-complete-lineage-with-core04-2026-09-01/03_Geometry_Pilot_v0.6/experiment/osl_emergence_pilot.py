#!/usr/bin/env python3
"""OSL Emergent Operator Geometry Pilot v0.6.

A deterministic synthetic experiment testing whether sentence-only supervision
induces a compact latent representation of provenance operators, and how that
representation changes under explicit state and algebraic-equivalence losses.

The experiment is deliberately small and controlled.  It is an existence pilot,
not evidence about large language models or general emergent symbolic reasoning.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge, RidgeClassifier, SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, r2_score
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from torch.utils.data import DataLoader, Dataset

SCHEMA = "osl.emergent-operator-geometry.pilot.v1"
VERSION = "0.6.0.dev1"

AGENTS = ("ada", "ben", "cara", "dax")
FACTS = ("red_circle", "blue_square", "green_triangle", "yellow_star", "silver_key", "black_cube")
OPS = ("observe", "tell", "imagine", "infer")
STATUSES = ("none", "observed", "communicated", "inferred", "simulated")
STATUS_TO_ID = {name: i for i, name in enumerate(STATUSES)}
AGENT_TO_ID = {name: i for i, name in enumerate(AGENTS)}
NONE_ORIGIN = len(AGENTS)
Q_TYPES = ("status", "origin", "direct", "knows", "safe_observed", "can_plan")
ANSWER_LABELS = (
    "status_none",
    "status_observed",
    "status_communicated",
    "status_inferred",
    "status_simulated",
    "agent_ada",
    "agent_ben",
    "agent_cara",
    "agent_dax",
    "source_none",
    "yes",
    "no",
)
ANSWER_TO_ID = {name: i for i, name in enumerate(ANSWER_LABELS)}

# Priority determines whether a later epistemic event may overwrite an earlier one.
# Direct observation dominates all other statuses; communication dominates inference;
# inference dominates simulation.  This creates useful idempotent and absorption laws.
STATUS_PRIORITY = {
    STATUS_TO_ID["none"]: 0,
    STATUS_TO_ID["simulated"]: 1,
    STATUS_TO_ID["inferred"]: 2,
    STATUS_TO_ID["communicated"]: 3,
    STATUS_TO_ID["observed"]: 4,
}

TRAIN_TEMPLATES: dict[str, tuple[str, ...]] = {
    "observe": (
        "{a} sees {f} .",
        "{f} is observed by {a} .",
    ),
    "tell": (
        "{a} tells {b} that {f} is present .",
        "{f} is reported by {a} to {b} .",
    ),
    "imagine": (
        "{a} imagines {f} .",
        "{f} is simulated by {a} .",
    ),
    "infer": (
        "{a} infers {f} .",
        "{f} is concluded by {a} .",
    ),
}

# Held-out templates use no held-out lexical items; they recombine words and syntax
# that occur somewhere in the training language.
HELDOUT_TEMPLATES: dict[str, tuple[str, ...]] = {
    "observe": ("{a} observed {f} .",),
    "tell": ("{a} reported to {b} that {f} is present .",),
    "imagine": ("{a} simulated {f} .",),
    "infer": ("{a} concluded {f} .",),
}

QUERY_TEMPLATES: dict[str, tuple[str, ...]] = {
    "status": (
        "what is the status of {f} for {a} ?",
        "how does {a} hold {f} ?",
    ),
    "origin": (
        "who is the source of {f} for {a} ?",
        "from whom did {a} get {f} ?",
    ),
    "direct": (
        "did {a} directly observe {f} ?",
        "was {f} directly observed by {a} ?",
    ),
    "knows": (
        "does {a} know {f} ?",
        "is {f} available to {a} ?",
    ),
    "safe_observed": (
        "may {a} record {f} as observed ?",
        "can {a} write {f} as a direct observation ?",
    ),
    "can_plan": (
        "may {a} use {f} for planning ?",
        "can {a} plan using {f} ?",
    ),
}

TOKEN_RE = re.compile(r"[a-z0-9_]+|[?.:,]", re.IGNORECASE)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Event:
    op: str
    a: int
    fact: int
    b: int = -1

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (OPS.index(self.op), self.a, self.b, self.fact)


@dataclass
class WorldState:
    status: np.ndarray  # [agent, fact]
    origin: np.ndarray  # [agent, fact], agent id or NONE_ORIGIN

    @classmethod
    def empty(cls) -> "WorldState":
        return cls(
            status=np.zeros((len(AGENTS), len(FACTS)), dtype=np.int64),
            origin=np.full((len(AGENTS), len(FACTS)), NONE_ORIGIN, dtype=np.int64),
        )

    def clone(self) -> "WorldState":
        return WorldState(self.status.copy(), self.origin.copy())

    def key(self) -> bytes:
        return self.status.tobytes() + self.origin.tobytes()

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.tolist(), "origin": self.origin.tolist()}


def set_if_higher(state: WorldState, agent: int, fact: int, status: int, origin: int) -> None:
    current = int(state.status[agent, fact])
    if STATUS_PRIORITY[status] >= STATUS_PRIORITY[current]:
        state.status[agent, fact] = status
        state.origin[agent, fact] = origin


def apply_event(state: WorldState, event: Event) -> WorldState:
    out = state.clone()
    if event.op == "observe":
        set_if_higher(out, event.a, event.fact, STATUS_TO_ID["observed"], event.a)
    elif event.op == "imagine":
        set_if_higher(out, event.a, event.fact, STATUS_TO_ID["simulated"], event.a)
    elif event.op == "infer":
        set_if_higher(out, event.a, event.fact, STATUS_TO_ID["inferred"], event.a)
    elif event.op == "tell":
        source_status = int(out.status[event.a, event.fact])
        if source_status != STATUS_TO_ID["none"]:
            source_origin = int(out.origin[event.a, event.fact])
            set_if_higher(
                out,
                event.b,
                event.fact,
                STATUS_TO_ID["communicated"],
                source_origin,
            )
    else:
        raise ValueError(f"unknown operation {event.op!r}")
    return out


def render_event(event: Event, rng: random.Random, heldout: bool = False) -> str:
    templates = HELDOUT_TEMPLATES[event.op] if heldout else TRAIN_TEMPLATES[event.op]
    template = rng.choice(templates)
    values = {"a": AGENTS[event.a], "f": FACTS[event.fact]}
    if event.b >= 0:
        values["b"] = AGENTS[event.b]
    return template.format(**values)


def render_query(qtype: str, agent: int, fact: int, rng: random.Random) -> str:
    return rng.choice(QUERY_TEMPLATES[qtype]).format(a=AGENTS[agent], f=FACTS[fact])


def answer_for(state: WorldState, qtype: str, agent: int, fact: int) -> int:
    status = int(state.status[agent, fact])
    origin = int(state.origin[agent, fact])
    if qtype == "status":
        return ANSWER_TO_ID[f"status_{STATUSES[status]}"]
    if qtype == "origin":
        if origin == NONE_ORIGIN:
            return ANSWER_TO_ID["source_none"]
        return ANSWER_TO_ID[f"agent_{AGENTS[origin]}"]
    if qtype == "direct":
        return ANSWER_TO_ID["yes" if status == STATUS_TO_ID["observed"] else "no"]
    if qtype == "knows":
        return ANSWER_TO_ID["yes" if status != STATUS_TO_ID["none"] else "no"]
    if qtype == "safe_observed":
        return ANSWER_TO_ID["yes" if status == STATUS_TO_ID["observed"] else "no"]
    if qtype == "can_plan":
        usable = status in {
            STATUS_TO_ID["observed"],
            STATUS_TO_ID["communicated"],
            STATUS_TO_ID["inferred"],
        }
        return ANSWER_TO_ID["yes" if usable else "no"]
    raise ValueError(qtype)


def sample_event(state: WorldState, rng: random.Random) -> Event:
    known = np.argwhere(state.status != STATUS_TO_ID["none"])
    if len(known) and rng.random() < 0.38:
        src, fact = map(int, rng.choice(known.tolist()))
        candidates = [i for i in range(len(AGENTS)) if i != src]
        dst = rng.choice(candidates)
        return Event("tell", src, fact, dst)
    op = rng.choices(("observe", "imagine", "infer"), weights=(0.46, 0.25, 0.29), k=1)[0]
    return Event(op, rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))


def random_story(length: int, rng: random.Random) -> tuple[list[Event], WorldState]:
    state = WorldState.empty()
    events: list[Event] = []
    for _ in range(length):
        event = sample_event(state, rng)
        state = apply_event(state, event)
        events.append(event)
    return events, state


def chain_story(chain_length: int, rng: random.Random) -> tuple[list[Event], WorldState]:
    if chain_length < 1 or chain_length > len(AGENTS) - 1:
        raise ValueError("chain_length out of range")
    fact = rng.randrange(len(FACTS))
    order = list(range(len(AGENTS)))
    rng.shuffle(order)
    order = order[: chain_length + 1]
    events = [Event("observe", order[0], fact)]
    for src, dst in zip(order[:-1], order[1:]):
        events.append(Event("tell", src, fact, dst))
    state = WorldState.empty()
    for event in events:
        state = apply_event(state, event)
    return events, state


def make_equivalent_pair(rng: random.Random, max_base_length: int = 3) -> tuple[list[Event], list[Event], WorldState]:
    mode = rng.choice(("idempotent", "commute", "absorb"))
    if mode == "idempotent":
        base, state = random_story(rng.randint(0, max_base_length), rng)
        op = rng.choice(("observe", "imagine", "infer"))
        event = Event(op, rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
        one = base + [event]
        two = base + [event, event]
    elif mode == "commute":
        base, state = random_story(rng.randint(0, max_base_length), rng)
        e1 = Event(rng.choice(("observe", "imagine", "infer")), rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
        e2 = Event(rng.choice(("observe", "imagine", "infer")), rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
        guard = 0
        while (e1.a, e1.fact) == (e2.a, e2.fact):
            e2 = Event(rng.choice(("observe", "imagine", "infer")), rng.randrange(len(AGENTS)), rng.randrange(len(FACTS)))
            guard += 1
            if guard > 20:
                break
        one = base + [e1, e2]
        two = base + [e2, e1]
    else:
        base, state = random_story(rng.randint(0, max_base_length), rng)
        agent = rng.randrange(len(AGENTS))
        fact = rng.randrange(len(FACTS))
        low = Event(rng.choice(("imagine", "infer")), agent, fact)
        high = Event("observe", agent, fact)
        one = base + [low, high]
        two = base + [high]
    s1 = WorldState.empty()
    for event in one:
        s1 = apply_event(s1, event)
    s2 = WorldState.empty()
    for event in two:
        s2 = apply_event(s2, event)
    if s1.key() != s2.key():
        # This is rare when a random base conflicts with an intended law. Retry.
        return make_equivalent_pair(rng, max_base_length)
    return one, two, s1


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass
class Example:
    story: str
    query: str
    answer: int
    qtype: str
    agent: int
    fact: int
    state_status: list[list[int]]
    state_origin: list[list[int]]
    events: list[tuple[int, int, int, int]]


@dataclass
class EquivalenceExample:
    story_a: str
    story_b: str


@dataclass(frozen=True)
class ExperimentConfig:
    train_story_count: int = 5000
    val_story_count: int = 700
    test_story_count: int = 900
    queries_per_story: int = 3
    train_min_length: int = 1
    train_max_length: int = 3
    ood_min_length: int = 4
    ood_max_length: int = 6
    equivalence_pair_count: int = 3500
    batch_size: int = 128
    hidden_dim: int = 96
    latent_dim: int = 64
    embedding_dim: int = 56
    query_hidden_dim: int = 48
    dropout: float = 0.08
    epochs: int = 12
    patience: int = 3
    learning_rate: float = 0.0025
    weight_decay: float = 0.0001
    state_loss_weight: float = 0.35
    law_loss_weight: float = 0.20
    law_every: int = 4
    gradient_clip: float = 1.0
    model_seeds: tuple[int, ...] = (1409, 1697, 2017)
    train_data_seed: int = 61001
    val_data_seed: int = 61003
    holdout_seeds: tuple[int, ...] = (62011, 62017, 62039, 62047)
    torch_threads: int = 4


class Vocabulary:
    def __init__(self, texts: Iterable[str]) -> None:
        tokens = sorted({token for text in texts for token in tokenize(text)})
        self.itos = ["<pad>", "<unk>"] + tokens
        self.stoi = {token: i for i, token in enumerate(self.itos)}

    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(token, 1) for token in tokenize(text)] or [1]

    def __len__(self) -> int:
        return len(self.itos)


def all_template_texts() -> list[str]:
    texts: list[str] = []
    sample = {"a": AGENTS[0], "b": AGENTS[1], "f": FACTS[0]}
    for family in (TRAIN_TEMPLATES, HELDOUT_TEMPLATES):
        for templates in family.values():
            texts.extend(template.format(**sample) for template in templates)
    for templates in QUERY_TEMPLATES.values():
        texts.extend(template.format(a=AGENTS[0], f=FACTS[0]) for template in templates)
    texts.extend(AGENTS)
    texts.extend(FACTS)
    return texts


def choose_query_target(state: WorldState, rng: random.Random, qtype: str) -> tuple[int, int]:
    cells = [(a, f) for a in range(len(AGENTS)) for f in range(len(FACTS))]
    known = [(a, f) for a, f in cells if state.status[a, f] != STATUS_TO_ID["none"]]
    unknown = [(a, f) for a, f in cells if state.status[a, f] == STATUS_TO_ID["none"]]
    observed = [(a, f) for a, f in cells if state.status[a, f] == STATUS_TO_ID["observed"]]
    communicated = [(a, f) for a, f in cells if state.status[a, f] == STATUS_TO_ID["communicated"]]
    simulated = [(a, f) for a, f in cells if state.status[a, f] == STATUS_TO_ID["simulated"]]
    inferred = [(a, f) for a, f in cells if state.status[a, f] == STATUS_TO_ID["inferred"]]
    if qtype == "status":
        pools = [p for p in (observed, communicated, inferred, simulated, unknown) if p]
        return rng.choice(rng.choice(pools))
    if qtype == "origin":
        return rng.choice(known if known and rng.random() < 0.75 else cells)
    if qtype in {"direct", "safe_observed"}:
        positive = observed
        negative = [p for p in cells if p not in observed]
        pool = positive if positive and rng.random() < 0.5 else negative
        return rng.choice(pool)
    if qtype == "knows":
        pool = known if known and rng.random() < 0.5 else unknown
        return rng.choice(pool)
    if qtype == "can_plan":
        positive = observed + communicated + inferred
        negative = simulated + unknown
        pool = positive if positive and rng.random() < 0.5 else negative
        return rng.choice(pool)
    return rng.choice(cells)


def story_to_text(events: Sequence[Event], rng: random.Random, heldout_templates: bool) -> str:
    return " ".join(render_event(event, rng, heldout_templates) for event in events)


def make_examples(
    story_count: int,
    length_range: tuple[int, int],
    seed: int,
    queries_per_story: int,
    heldout_templates: bool = False,
    chain_only: bool = False,
) -> list[Example]:
    rng = random.Random(seed)
    examples: list[Example] = []
    for _ in range(story_count):
        if chain_only:
            chain_length = rng.choice((2, 3))
            events, state = chain_story(chain_length, rng)
        else:
            events, state = random_story(rng.randint(*length_range), rng)
        story = story_to_text(events, rng, heldout_templates)
        qtypes = list(Q_TYPES)
        rng.shuffle(qtypes)
        for qtype in qtypes[:queries_per_story]:
            agent, fact = choose_query_target(state, rng, qtype)
            query = render_query(qtype, agent, fact, rng)
            examples.append(
                Example(
                    story=story,
                    query=query,
                    answer=answer_for(state, qtype, agent, fact),
                    qtype=qtype,
                    agent=agent,
                    fact=fact,
                    state_status=state.status.tolist(),
                    state_origin=state.origin.tolist(),
                    events=[event.as_tuple() for event in events],
                )
            )
    return examples


def make_equivalence_examples(count: int, seed: int) -> list[EquivalenceExample]:
    rng = random.Random(seed)
    out: list[EquivalenceExample] = []
    for _ in range(count):
        a, b, _ = make_equivalent_pair(rng)
        out.append(
            EquivalenceExample(
                story_a=story_to_text(a, rng, False),
                story_b=story_to_text(b, rng, False),
            )
        )
    return out


class StoryDataset(Dataset[dict[str, Any]]):
    def __init__(self, examples: Sequence[Example], vocab: Vocabulary) -> None:
        self.examples = list(examples)
        self.vocab = vocab

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        ex = self.examples[index]
        return {
            "story": self.vocab.encode(ex.story),
            "query": self.vocab.encode(ex.query),
            "answer": ex.answer,
            "qtype": Q_TYPES.index(ex.qtype),
            "agent": ex.agent,
            "fact": ex.fact,
            "status": np.asarray(ex.state_status, dtype=np.int64),
            "origin": np.asarray(ex.state_origin, dtype=np.int64),
            "events": ex.events,
            "raw": ex,
        }


class EquivalenceDataset(Dataset[dict[str, Any]]):
    def __init__(self, examples: Sequence[EquivalenceExample], vocab: Vocabulary) -> None:
        self.examples = list(examples)
        self.vocab = vocab

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        ex = self.examples[index]
        return {"story_a": self.vocab.encode(ex.story_a), "story_b": self.vocab.encode(ex.story_b)}


def pad_sequences(sequences: Sequence[Sequence[int]]) -> tuple[torch.Tensor, torch.Tensor]:
    lengths = torch.tensor([len(seq) for seq in sequences], dtype=torch.long)
    max_len = int(lengths.max().item())
    output = torch.zeros((len(sequences), max_len), dtype=torch.long)
    for i, seq in enumerate(sequences):
        output[i, : len(seq)] = torch.tensor(seq, dtype=torch.long)
    return output, lengths


def collate_story(batch: Sequence[dict[str, Any]]) -> dict[str, Any]:
    story, story_len = pad_sequences([item["story"] for item in batch])
    query, query_len = pad_sequences([item["query"] for item in batch])
    return {
        "story": story,
        "story_len": story_len,
        "query": query,
        "query_len": query_len,
        "answer": torch.tensor([item["answer"] for item in batch], dtype=torch.long),
        "qtype": torch.tensor([item["qtype"] for item in batch], dtype=torch.long),
        "agent": torch.tensor([item["agent"] for item in batch], dtype=torch.long),
        "fact": torch.tensor([item["fact"] for item in batch], dtype=torch.long),
        "status": torch.tensor(np.stack([item["status"] for item in batch]), dtype=torch.long),
        "origin": torch.tensor(np.stack([item["origin"] for item in batch]), dtype=torch.long),
        "events": [item["events"] for item in batch],
        "raw": [item["raw"] for item in batch],
    }


def collate_equivalence(batch: Sequence[dict[str, Any]]) -> dict[str, Any]:
    a, a_len = pad_sequences([item["story_a"] for item in batch])
    b, b_len = pad_sequences([item["story_b"] for item in batch])
    return {"story_a": a, "story_a_len": a_len, "story_b": b, "story_b_len": b_len}


class OperatorStoryModel(nn.Module):
    def __init__(self, vocab_size: int, config: ExperimentConfig) -> None:
        super().__init__()
        self.config = config
        self.embedding = nn.Embedding(vocab_size, config.embedding_dim, padding_idx=0)
        self.story_gru = nn.RNN(
            config.embedding_dim,
            config.hidden_dim,
            num_layers=1,
            nonlinearity="tanh",
            batch_first=True,
        )
        self.query_gru = nn.RNN(
            config.embedding_dim,
            config.query_hidden_dim,
            num_layers=1,
            nonlinearity="tanh",
            batch_first=True,
        )
        self.story_norm = nn.LayerNorm(config.hidden_dim)
        self.latent = nn.Sequential(
            nn.Linear(config.hidden_dim, config.latent_dim),
            nn.Tanh(),
            nn.LayerNorm(config.latent_dim),
        )
        combined = config.latent_dim + config.query_hidden_dim
        self.answer = nn.Sequential(
            nn.Linear(combined, 128),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(128, len(ANSWER_LABELS)),
        )
        self.status_head = nn.Linear(config.latent_dim, len(AGENTS) * len(FACTS) * len(STATUSES))
        self.origin_head = nn.Linear(config.latent_dim, len(AGENTS) * len(FACTS) * (len(AGENTS) + 1))

    def encode(self, tokens: torch.Tensor, lengths: torch.Tensor, which: str) -> torch.Tensor:
        emb = self.embedding(tokens)
        recurrent = self.story_gru if which == "story" else self.query_gru
        output, _ = recurrent(emb)
        index = (lengths.to(output.device) - 1).clamp_min(0)
        return output[torch.arange(output.shape[0], device=output.device), index]

    def encode_story(self, story: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        raw = self.story_norm(self.encode(story, lengths, "story"))
        return self.latent(raw)

    def forward(self, batch: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        z = self.encode_story(batch["story"], batch["story_len"])
        q = self.encode(batch["query"], batch["query_len"], "query")
        answer_logits = self.answer(torch.cat([z, q], dim=-1))
        status_logits = self.status_head(z).view(-1, len(AGENTS), len(FACTS), len(STATUSES))
        origin_logits = self.origin_head(z).view(-1, len(AGENTS), len(FACTS), len(AGENTS) + 1)
        return {"z": z, "answer": answer_logits, "status": status_logits, "origin": origin_logits}


@dataclass
class ArmResult:
    arm: str
    model_seed: int
    best_epoch: int
    metrics: dict[str, Any]
    checkpoint: str


def move_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


def state_loss(outputs: dict[str, torch.Tensor], batch: dict[str, torch.Tensor]) -> torch.Tensor:
    # Most agent-fact cells are empty.  Downweight the null classes so explicit
    # state supervision cannot be satisfied by predicting "none" everywhere.
    status_weight = torch.tensor([0.18, 1.0, 1.0, 1.0, 1.0], device=outputs["status"].device)
    origin_weight = torch.tensor([1.0, 1.0, 1.0, 1.0, 0.18], device=outputs["origin"].device)
    status = nn.functional.cross_entropy(
        outputs["status"].reshape(-1, len(STATUSES)),
        batch["status"].reshape(-1),
        weight=status_weight,
    )
    origin = nn.functional.cross_entropy(
        outputs["origin"].reshape(-1, len(AGENTS) + 1),
        batch["origin"].reshape(-1),
        weight=origin_weight,
    )
    return 0.5 * (status + origin)


def law_loss(model: OperatorStoryModel, batch: dict[str, torch.Tensor]) -> torch.Tensor:
    """Contrastive quotient loss for operator-equivalent paths.

    Positive pairs are distinct surface/operator paths with the same formal state.
    A deterministic cyclic shift supplies negatives.  The negative term prevents
    the trivial solution in which every story occupies the same latent direction.
    """

    z1 = nn.functional.normalize(model.encode_story(batch["story_a"], batch["story_a_len"]), dim=-1)
    z2 = nn.functional.normalize(model.encode_story(batch["story_b"], batch["story_b_len"]), dim=-1)
    positive = 1.0 - (z1 * z2).sum(dim=-1)
    negative_z2 = torch.roll(z2, shifts=1, dims=0)
    negative_cosine = (z1 * negative_z2).sum(dim=-1)
    negative = nn.functional.relu(negative_cosine - 0.45)
    return positive.mean() + 0.35 * negative.mean()


def set_determinism(seed: int, threads: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True)


@torch.no_grad()
def evaluate_model(
    model: OperatorStoryModel,
    loader: DataLoader,
    device: torch.device,
) -> dict[str, Any]:
    model.eval()
    total = correct = 0
    by_q = {q: [0, 0] for q in Q_TYPES}
    status_correct = status_total = origin_correct = origin_total = 0
    state_exact = 0
    native_status_targets: list[np.ndarray] = []
    native_status_predictions: list[np.ndarray] = []
    native_origin_targets: list[np.ndarray] = []
    native_origin_predictions: list[np.ndarray] = []
    latents: list[np.ndarray] = []
    statuses: list[np.ndarray] = []
    origins: list[np.ndarray] = []
    raws: list[Example] = []
    for batch in loader:
        batch = move_batch(batch, device)
        out = model(batch)
        pred = out["answer"].argmax(dim=-1)
        match = pred.eq(batch["answer"])
        total += len(pred)
        correct += int(match.sum().item())
        for idx, qid in enumerate(batch["qtype"].tolist()):
            q = Q_TYPES[qid]
            by_q[q][1] += 1
            by_q[q][0] += int(match[idx].item())
        sp = out["status"].argmax(dim=-1)
        op = out["origin"].argmax(dim=-1)
        status_correct += int(sp.eq(batch["status"]).sum().item())
        status_total += int(batch["status"].numel())
        origin_correct += int(op.eq(batch["origin"]).sum().item())
        origin_total += int(batch["origin"].numel())
        state_exact += int((sp.eq(batch["status"]).all(dim=(1, 2)) & op.eq(batch["origin"]).all(dim=(1, 2))).sum().item())
        native_status_targets.append(batch["status"].cpu().numpy().reshape(-1))
        native_status_predictions.append(sp.cpu().numpy().reshape(-1))
        native_origin_targets.append(batch["origin"].cpu().numpy().reshape(-1))
        native_origin_predictions.append(op.cpu().numpy().reshape(-1))
        latents.extend(out["z"].cpu().numpy())
        statuses.extend(batch["status"].cpu().numpy())
        origins.extend(batch["origin"].cpu().numpy())
        raws.extend(batch["raw"])
    return {
        "answer_accuracy": correct / total,
        "answer_count": total,
        "by_query": {q: wins / count if count else None for q, (wins, count) in by_q.items()},
        "native_status_cell_accuracy": status_correct / status_total,
        "native_origin_cell_accuracy": origin_correct / origin_total,
        "native_state_exact_accuracy": state_exact / total,
        "native_status_balanced_accuracy": float(balanced_accuracy_score(
            np.concatenate(native_status_targets), np.concatenate(native_status_predictions)
        )),
        "native_origin_balanced_accuracy": float(balanced_accuracy_score(
            np.concatenate(native_origin_targets), np.concatenate(native_origin_predictions)
        )),
        "latents": np.asarray(latents),
        "statuses": np.asarray(statuses),
        "origins": np.asarray(origins),
        "raws": raws,
    }


def train_arm(
    arm: Literal["answer_only", "state_supervised", "operator_regularized"],
    model_seed: int,
    config: ExperimentConfig,
    vocab: Vocabulary,
    train_examples: Sequence[Example],
    val_examples: Sequence[Example],
    eq_examples: Sequence[EquivalenceExample],
    output_dir: Path,
) -> ArmResult:
    set_determinism(model_seed, config.torch_threads)
    device = torch.device("cpu")
    model = OperatorStoryModel(len(vocab), config).to(device)
    train_loader = DataLoader(
        StoryDataset(train_examples, vocab),
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collate_story,
        generator=torch.Generator().manual_seed(model_seed + 1),
    )
    val_loader = DataLoader(
        StoryDataset(val_examples, vocab),
        batch_size=config.batch_size,
        shuffle=False,
        collate_fn=collate_story,
    )
    eq_loader = DataLoader(
        EquivalenceDataset(eq_examples, vocab),
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collate_equivalence,
        generator=torch.Generator().manual_seed(model_seed + 2),
    )
    eq_iter = iter(eq_loader)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    best_acc = -1.0
    best_epoch = 0
    best_state: dict[str, torch.Tensor] | None = None
    history: list[dict[str, float]] = []
    stale = 0
    for epoch in range(1, config.epochs + 1):
        model.train()
        losses: list[float] = []
        for batch_index, batch in enumerate(train_loader):
            batch = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            out = model(batch)
            loss = nn.functional.cross_entropy(out["answer"], batch["answer"])
            if arm in {"state_supervised", "operator_regularized"}:
                loss = loss + config.state_loss_weight * state_loss(out, batch)
            if arm == "operator_regularized" and batch_index % config.law_every == 0:
                try:
                    eq_batch = next(eq_iter)
                except StopIteration:
                    eq_iter = iter(eq_loader)
                    eq_batch = next(eq_iter)
                eq_batch = move_batch(eq_batch, device)
                loss = loss + config.law_loss_weight * law_loss(model, eq_batch)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clip)
            optimizer.step()
            losses.append(float(loss.item()))
        val = evaluate_model(model, val_loader, device)
        val_acc = float(val["answer_accuracy"])
        history.append({"epoch": epoch, "train_loss": statistics.mean(losses), "val_accuracy": val_acc})
        if val_acc > best_acc + 1e-6:
            best_acc = val_acc
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
        if stale >= config.patience:
            break
    assert best_state is not None
    model.load_state_dict(best_state)
    checkpoint = output_dir / f"{arm}_seed_{model_seed}.pt"
    torch.save({"model": best_state, "vocab": vocab.itos, "config": asdict(config), "history": history}, checkpoint)
    return ArmResult(
        arm=arm,
        model_seed=model_seed,
        best_epoch=best_epoch,
        metrics={"validation_accuracy": best_acc, "history": history},
        checkpoint=checkpoint.name,
    )


def load_model(checkpoint: Path, config: ExperimentConfig, vocab: Vocabulary) -> OperatorStoryModel:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = OperatorStoryModel(len(vocab), config)
    model.load_state_dict(payload["model"])
    model.eval()
    return model


def collect_unique_story_latents(
    model: OperatorStoryModel,
    examples: Sequence[Example],
    vocab: Vocabulary,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[Example]]:
    # Deduplicate story strings so probe metrics are not inflated by repeated queries.
    by_story: dict[str, Example] = {}
    for ex in examples:
        by_story.setdefault(ex.story, ex)
    unique = list(by_story.values())
    loader = DataLoader(StoryDataset(unique, vocab), batch_size=batch_size, shuffle=False, collate_fn=collate_story)
    result = evaluate_model(model, loader, torch.device("cpu"))
    return result["latents"], result["statuses"], result["origins"], result["raws"]


def cell_features(latents: np.ndarray, status: np.ndarray, origin: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(latents)
    rows: list[np.ndarray] = []
    status_y: list[int] = []
    origin_y: list[int] = []
    for i in range(n):
        for a in range(len(AGENTS)):
            for f in range(len(FACTS)):
                onehot = np.zeros(len(AGENTS) + len(FACTS), dtype=np.float32)
                onehot[a] = 1.0
                onehot[len(AGENTS) + f] = 1.0
                rows.append(np.concatenate([latents[i], onehot]))
                status_y.append(int(status[i, a, f]))
                origin_y.append(int(origin[i, a, f]))
    return np.asarray(rows), np.asarray(status_y), np.asarray(origin_y)


def linear_probe_metrics(
    train_bundle: tuple[np.ndarray, np.ndarray, np.ndarray, list[Example]],
    test_bundle: tuple[np.ndarray, np.ndarray, np.ndarray, list[Example]],
    seed: int,
) -> dict[str, float]:
    del seed
    train_x, train_s, train_o = cell_features(train_bundle[0], train_bundle[1], train_bundle[2])
    test_x, test_s, test_o = cell_features(test_bundle[0], test_bundle[1], test_bundle[2])
    # Closed-form ridge probes keep the audit fast and deterministic.  They are
    # diagnostic readouts, not components of the trained sequence model.
    status_probe = RidgeClassifier(alpha=1.0, class_weight="balanced")
    origin_probe = RidgeClassifier(alpha=1.0, class_weight="balanced")
    status_probe.fit(train_x, train_s)
    origin_probe.fit(train_x, train_o)
    status_pred = status_probe.predict(test_x)
    origin_pred = origin_probe.predict(test_x)
    return {
        "linear_probe_status_accuracy": float(accuracy_score(test_s, status_pred)),
        "linear_probe_origin_accuracy": float(accuracy_score(test_o, origin_pred)),
        "linear_probe_status_balanced_accuracy": float(balanced_accuracy_score(test_s, status_pred)),
        "linear_probe_origin_balanced_accuracy": float(balanced_accuracy_score(test_o, origin_pred)),
    }


def encode_story_texts(model: OperatorStoryModel, vocab: Vocabulary, stories: Sequence[str], batch_size: int = 256) -> np.ndarray:
    model.eval()
    outputs: list[np.ndarray] = []
    for start in range(0, len(stories), batch_size):
        chunk = stories[start : start + batch_size]
        tokens, lengths = pad_sequences([vocab.encode(text) for text in chunk])
        with torch.no_grad():
            outputs.append(model.encode_story(tokens, lengths).cpu().numpy())
    return np.concatenate(outputs, axis=0) if outputs else np.empty((0, model.config.latent_dim))


def equivalence_geometry(
    model: OperatorStoryModel,
    vocab: Vocabulary,
    eq_examples: Sequence[EquivalenceExample],
    seed: int,
) -> dict[str, float]:
    stories_a = [ex.story_a for ex in eq_examples]
    stories_b = [ex.story_b for ex in eq_examples]
    za = encode_story_texts(model, vocab, stories_a)
    zb = encode_story_texts(model, vocab, stories_b)
    za_n = za / np.maximum(np.linalg.norm(za, axis=1, keepdims=True), 1e-8)
    zb_n = zb / np.maximum(np.linalg.norm(zb, axis=1, keepdims=True), 1e-8)
    eq_cos = np.sum(za_n * zb_n, axis=1)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(zb_n))
    # Avoid accidental fixed points in the random baseline.
    perm = np.roll(perm, 1)
    neq_cos = np.sum(za_n * zb_n[perm], axis=1)
    eq_dist = np.linalg.norm(za - zb, axis=1)
    neq_dist = np.linalg.norm(za - zb[perm], axis=1)
    return {
        "equivalent_cosine_mean": float(eq_cos.mean()),
        "nonequivalent_cosine_mean": float(neq_cos.mean()),
        "equivalence_separation": float(eq_cos.mean() - neq_cos.mean()),
        "equivalent_distance_mean": float(eq_dist.mean()),
        "nonequivalent_distance_mean": float(neq_dist.mean()),
        "distance_separation": float(neq_dist.mean() - eq_dist.mean()),
    }


def event_feature(event_tuple: tuple[int, int, int, int]) -> np.ndarray:
    op, a, b, fact = event_tuple
    vector = np.zeros(len(OPS) + len(AGENTS) * 2 + len(FACTS), dtype=np.float64)
    vector[op] = 1.0
    vector[len(OPS) + a] = 1.0
    if b >= 0:
        vector[len(OPS) + len(AGENTS) + b] = 1.0
    vector[len(OPS) + 2 * len(AGENTS) + fact] = 1.0
    return vector


def transition_records(
    model: OperatorStoryModel,
    vocab: Vocabulary,
    examples: Sequence[Example],
    heldout_templates: bool,
    seed: int,
) -> list[tuple[int, np.ndarray, np.ndarray, np.ndarray]]:
    """Collect latent transitions with one vectorized encoder pass.

    Prefixes are rendered canonically so the geometry measure reflects event
    composition rather than random template choice.
    """

    del heldout_templates, seed
    seen: set[tuple[tuple[int, int, int, int], ...]] = set()
    prefix_index: dict[str, int] = {}
    prefix_texts: list[str] = []
    pending: list[tuple[int, int, int, np.ndarray]] = []

    def canonical_event(event: Event) -> str:
        template = TRAIN_TEMPLATES[event.op][0]
        values = {"a": AGENTS[event.a], "f": FACTS[event.fact]}
        if event.b >= 0:
            values["b"] = AGENTS[event.b]
        return template.format(**values)

    def index_of(text: str) -> int:
        if text not in prefix_index:
            prefix_index[text] = len(prefix_texts)
            prefix_texts.append(text)
        return prefix_index[text]

    for ex in examples:
        key = tuple(ex.events)
        if key in seen:
            continue
        seen.add(key)
        events = [Event(OPS[op], a, fact, b) for op, a, b, fact in ex.events]
        rendered: list[str] = []
        before_text = ""
        for event in events:
            before_idx = index_of(before_text)
            rendered.append(canonical_event(event))
            after_text = " ".join(rendered)
            after_idx = index_of(after_text)
            pending.append((OPS.index(event.op), before_idx, after_idx, event_feature(event.as_tuple())))
            before_text = after_text
    latent = encode_story_texts(model, vocab, prefix_texts, batch_size=512)
    return [(op, latent[before], feature, latent[after]) for op, before, after, feature in pending]


def fit_transition_models(
    train_records: Sequence[tuple[int, np.ndarray, np.ndarray, np.ndarray]],
) -> dict[int, Ridge]:
    models: dict[int, Ridge] = {}
    for op in range(len(OPS)):
        subset = [r for r in train_records if r[0] == op]
        x = np.asarray([np.concatenate([r[1], r[2]]) for r in subset])
        y = np.asarray([r[3] for r in subset])
        reg = Ridge(alpha=1.0)
        reg.fit(x, y)
        models[op] = reg
    return models


def transition_geometry_metrics(
    model: OperatorStoryModel,
    vocab: Vocabulary,
    train_examples: Sequence[Example],
    test_examples: Sequence[Example],
    seed: int,
) -> dict[str, float]:
    train_records = transition_records(model, vocab, train_examples[: min(len(train_examples), 5000)], False, seed)
    test_records = transition_records(model, vocab, test_examples[: min(len(test_examples), 3500)], False, seed + 1)
    maps = fit_transition_models(train_records)
    actual = np.asarray([r[3] for r in test_records])
    predicted = np.asarray([maps[r[0]].predict(np.concatenate([r[1], r[2]])[None, :])[0] for r in test_records])
    noop = np.asarray([r[1] for r in test_records])
    rng = np.random.default_rng(seed)
    shuffled_ops = rng.permutation([r[0] for r in test_records])
    shuffled = np.asarray([
        maps[int(op)].predict(np.concatenate([r[1], r[2]])[None, :])[0]
        for r, op in zip(test_records, shuffled_ops)
    ])
    mse = float(np.mean((predicted - actual) ** 2))
    noop_mse = float(np.mean((noop - actual) ** 2))
    shuffled_mse = float(np.mean((shuffled - actual) ** 2))
    return {
        "affine_transition_r2": float(r2_score(actual, predicted, multioutput="variance_weighted")),
        "affine_transition_mse": mse,
        "noop_transition_mse": noop_mse,
        "shuffled_operator_mse": shuffled_mse,
        "operator_advantage_vs_noop": float((noop_mse - mse) / max(noop_mse, 1e-12)),
        "operator_advantage_vs_shuffled": float((shuffled_mse - mse) / max(shuffled_mse, 1e-12)),
        "transition_record_count": len(test_records),
    }


def strip_large_eval(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key not in {"latents", "statuses", "origins", "raws"}}


def evaluate_checkpoint(
    checkpoint: Path,
    arm: str,
    model_seed: int,
    config: ExperimentConfig,
    vocab: Vocabulary,
    datasets: dict[str, list[Example]],
    train_examples: list[Example],
    eq_test: list[EquivalenceExample],
) -> dict[str, Any]:
    set_determinism(model_seed, config.torch_threads)
    model = load_model(checkpoint, config, vocab)
    split_metrics: dict[str, Any] = {}
    eval_cache: dict[str, dict[str, Any]] = {}
    for name, examples in datasets.items():
        loader = DataLoader(StoryDataset(examples, vocab), batch_size=config.batch_size, shuffle=False, collate_fn=collate_story)
        result = evaluate_model(model, loader, torch.device("cpu"))
        eval_cache[name] = result
        split_metrics[name] = strip_large_eval(result)
    train_bundle = collect_unique_story_latents(model, train_examples[:6000], vocab, config.batch_size)
    ood_bundle = collect_unique_story_latents(model, datasets["ood_length"], vocab, config.batch_size)
    probe = linear_probe_metrics(train_bundle, ood_bundle, model_seed)
    eq = equivalence_geometry(model, vocab, eq_test, model_seed)
    trans = transition_geometry_metrics(model, vocab, train_examples, datasets["ood_length"], model_seed)
    return {
        "arm": arm,
        "model_seed": model_seed,
        "splits": split_metrics,
        "linear_probe": probe,
        "equivalence_geometry": eq,
        "transition_geometry": trans,
    }


def query_majority_baseline(train_examples: Sequence[Example], datasets: dict[str, list[Example]]) -> dict[str, float]:
    by_q: dict[str, Counter[int]] = defaultdict(Counter)
    for ex in train_examples:
        by_q[ex.qtype][ex.answer] += 1
    prediction = {q: counts.most_common(1)[0][0] for q, counts in by_q.items()}
    return {
        name: float(np.mean([prediction[ex.qtype] == ex.answer for ex in examples]))
        for name, examples in datasets.items()
    }


def ngram_baseline(train_examples: Sequence[Example], datasets: dict[str, list[Example]], seed: int) -> dict[str, float]:
    train_text = [f"{ex.story} query {ex.query}" for ex in train_examples]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=40000)
    x_train = vectorizer.fit_transform(train_text)
    y_train = np.asarray([ex.answer for ex in train_examples])
    classifier = SGDClassifier(
        loss="log_loss",
        alpha=1e-5,
        max_iter=1200,
        tol=1e-4,
        random_state=seed,
        class_weight="balanced",
    )
    classifier.fit(x_train, y_train)
    result: dict[str, float] = {}
    for name, examples in datasets.items():
        x = vectorizer.transform([f"{ex.story} query {ex.query}" for ex in examples])
        result[name] = float(accuracy_score([ex.answer for ex in examples], classifier.predict(x)))
    return result


def aggregate_results(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_arm[record["arm"]].append(record)
    aggregate: dict[str, Any] = {}
    metric_paths = [
        ("splits", "id", "answer_accuracy"),
        ("splits", "ood_length", "answer_accuracy"),
        ("splits", "ood_templates", "answer_accuracy"),
        ("splits", "ood_combined", "answer_accuracy"),
        ("splits", "long_chain", "answer_accuracy"),
        ("linear_probe", "linear_probe_status_accuracy"),
        ("linear_probe", "linear_probe_origin_accuracy"),
        ("linear_probe", "linear_probe_status_balanced_accuracy"),
        ("linear_probe", "linear_probe_origin_balanced_accuracy"),
        ("equivalence_geometry", "equivalent_cosine_mean"),
        ("equivalence_geometry", "equivalence_separation"),
        ("equivalence_geometry", "distance_separation"),
        ("transition_geometry", "affine_transition_r2"),
        ("transition_geometry", "operator_advantage_vs_noop"),
        ("transition_geometry", "operator_advantage_vs_shuffled"),
    ]
    for arm, arm_records in by_arm.items():
        summary: dict[str, Any] = {"seed_count": len(arm_records), "seeds": [r["model_seed"] for r in arm_records]}
        for path in metric_paths:
            values: list[float] = []
            for record in arm_records:
                value: Any = record
                for key in path:
                    value = value[key]
                values.append(float(value))
            label = ".".join(path)
            summary[label] = {
                "mean": float(statistics.mean(values)),
                "std": float(statistics.stdev(values)) if len(values) > 1 else 0.0,
                "values": values,
            }
        aggregate[arm] = summary
    return aggregate


def endpoint_evaluation(aggregate: dict[str, Any], baselines: dict[str, dict[str, float]]) -> dict[str, bool]:
    a = aggregate["answer_only"]
    c = aggregate["operator_regularized"]
    majority = baselines["query_type_majority"]
    return {
        "E01_all_arms_beat_query_majority_id": all(
            aggregate[arm]["splits.id.answer_accuracy"]["mean"] > majority["id"] + 0.03
            for arm in aggregate
        ),
        "E02_answer_only_has_nontrivial_ood_composition": (
            a["splits.ood_length.answer_accuracy"]["mean"] > majority["ood_length"] + 0.03
        ),
        "E03_answer_only_status_geometry_is_decodable": (
            a["linear_probe.linear_probe_status_balanced_accuracy"]["mean"] > 0.28
        ),
        "E04_answer_only_origin_geometry_is_decodable": (
            a["linear_probe.linear_probe_origin_balanced_accuracy"]["mean"] > 0.40
        ),
        "E05_operator_regularization_improves_path_invariance": (
            c["equivalence_geometry.distance_separation"]["mean"]
            > a["equivalence_geometry.distance_separation"]["mean"] + 0.20
        ),
        "E06_affine_operator_maps_beat_noop_in_all_arms": all(
            aggregate[arm]["transition_geometry.operator_advantage_vs_noop"]["mean"] > 0.05
            for arm in aggregate
        ),
        "E07_affine_operator_maps_beat_shuffled_labels_in_all_arms": all(
            aggregate[arm]["transition_geometry.operator_advantage_vs_shuffled"]["mean"] > 0.02
            for arm in aggregate
        ),
        "E08_no_result_is_represented_as_perfect_open_ended_emergence": (
            max(aggregate[arm]["splits.ood_combined.answer_accuracy"]["mean"] for arm in aggregate) < 0.999
        ),
    }


def build_data(config: ExperimentConfig) -> tuple[Vocabulary, dict[str, list[Example]], list[EquivalenceExample], list[EquivalenceExample]]:
    vocab = Vocabulary(all_template_texts())
    train = make_examples(
        config.train_story_count,
        (config.train_min_length, config.train_max_length),
        config.train_data_seed,
        config.queries_per_story,
    )
    val = make_examples(
        config.val_story_count,
        (config.train_min_length, config.train_max_length),
        config.val_data_seed,
        config.queries_per_story,
    )
    datasets: dict[str, list[Example]] = {"train": train, "val": val}
    # The frozen holdout combines four independently generated seed blocks.
    splits = {"id": [], "ood_length": [], "ood_templates": [], "ood_combined": [], "long_chain": []}
    per_seed = max(1, config.test_story_count // len(config.holdout_seeds))
    for seed in config.holdout_seeds:
        splits["id"].extend(make_examples(per_seed, (1, 3), seed, config.queries_per_story))
        splits["ood_length"].extend(make_examples(per_seed, (4, 6), seed + 101, config.queries_per_story))
        splits["ood_templates"].extend(make_examples(per_seed, (1, 3), seed + 211, config.queries_per_story, heldout_templates=True))
        splits["ood_combined"].extend(make_examples(per_seed, (4, 6), seed + 307, config.queries_per_story, heldout_templates=True))
        splits["long_chain"].extend(make_examples(per_seed, (3, 4), seed + 401, config.queries_per_story, chain_only=True))
    datasets.update(splits)
    eq_train = make_equivalence_examples(config.equivalence_pair_count, config.train_data_seed + 777)
    eq_test: list[EquivalenceExample] = []
    for seed in config.holdout_seeds:
        eq_test.extend(make_equivalence_examples(300, seed + 991))
    return vocab, datasets, eq_train, eq_test


def save_dataset_manifest(root: Path, vocab: Vocabulary, datasets: dict[str, list[Example]], eq_train: list[EquivalenceExample], eq_test: list[EquivalenceExample]) -> dict[str, Any]:
    manifest = {
        "schema": "osl.emergence.dataset-manifest.v1",
        "vocabulary": vocab.itos,
        "splits": {
            name: {
                "example_count": len(examples),
                "digest": digest([asdict(ex) for ex in examples]),
                "answer_distribution": dict(Counter(ANSWER_LABELS[ex.answer] for ex in examples)),
                "query_distribution": dict(Counter(ex.qtype for ex in examples)),
            }
            for name, examples in datasets.items()
        },
        "equivalence_train": {"count": len(eq_train), "digest": digest([asdict(ex) for ex in eq_train])},
        "equivalence_test": {"count": len(eq_test), "digest": digest([asdict(ex) for ex in eq_test])},
    }
    (root / "results" / "DATASET_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def write_csv(records: Sequence[dict[str, Any]], path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for record in records:
        base = {"arm": record["arm"], "model_seed": record["model_seed"]}
        for split, metrics in record["splits"].items():
            rows.append({**base, "metric_group": f"split:{split}", "metric": "answer_accuracy", "value": metrics["answer_accuracy"]})
        for group in ("linear_probe", "equivalence_geometry", "transition_geometry"):
            for key, value in record[group].items():
                if isinstance(value, (int, float)):
                    rows.append({**base, "metric_group": group, "metric": key, "value": value})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["arm", "model_seed", "metric_group", "metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


def run_experiment(root: Path, config: ExperimentConfig) -> dict[str, Any]:
    vocab, datasets, eq_train, eq_test = build_data(config)
    data_manifest = save_dataset_manifest(root, vocab, datasets, eq_train, eq_test)
    arms = ("answer_only", "state_supervised", "operator_regularized")
    training_records: list[dict[str, Any]] = []
    evaluation_records: list[dict[str, Any]] = []
    for arm in arms:
        for seed in config.model_seeds:
            print(f"TRAIN arm={arm} seed={seed}", flush=True)
            result = train_arm(
                arm, seed, config, vocab, datasets["train"], datasets["val"], eq_train, root / "checkpoints"
            )
            training_records.append(asdict(result))
            print(f"EVAL arm={arm} seed={seed} epoch={result.best_epoch}", flush=True)
            evaluation_records.append(
                evaluate_checkpoint(
                    root / "checkpoints" / result.checkpoint,
                    arm,
                    seed,
                    config,
                    vocab,
                    {k: v for k, v in datasets.items() if k not in {"train", "val"}},
                    datasets["train"],
                    eq_test,
                )
            )
    aggregate = aggregate_results(evaluation_records)
    heldout_datasets = {k: v for k, v in datasets.items() if k not in {"train", "val"}}
    baselines = {
        "query_type_majority": query_majority_baseline(datasets["train"], heldout_datasets),
        "tfidf_bigram": ngram_baseline(datasets["train"], heldout_datasets, config.train_data_seed),
        "symbolic_oracle": {name: 1.0 for name in heldout_datasets},
    }
    endpoints = endpoint_evaluation(aggregate, baselines)
    report = {
        "schema": SCHEMA,
        "version": VERSION,
        "scientific_status": "CONTROLLED_SYNTHETIC_PILOT",
        "config": asdict(config),
        "dataset_manifest_digest": digest(data_manifest),
        "training": training_records,
        "evaluations": evaluation_records,
        "aggregate": aggregate,
        "baselines": baselines,
        "endpoints": endpoints,
        "endpoint_pass_count": sum(endpoints.values()),
        "endpoint_count": len(endpoints),
        "all_endpoints_met": all(endpoints.values()),
        "claim_boundary": (
            "This is a small deterministic synthetic-language pilot using GRU encoders. "
            "It tests whether provenance-relevant state and approximate affine transition structure become "
            "decodable under matched supervision regimes. It does not establish emergence in large language "
            "models, open-ended symbol discovery, or a universal machine language."
        ),
    }
    report["digest"] = digest(report)
    (root / "results" / "PILOT_ANALYSIS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(evaluation_records, root / "results" / "PILOT_METRICS.csv")
    return report


def verify_freeze(root: Path) -> dict[str, Any]:
    path = root / "PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    unsigned = dict(payload)
    expected_digest = unsigned.pop("digest")
    checks: dict[str, bool] = {"manifest_digest": digest(unsigned) == expected_digest}
    for relative, expected in payload["files"].items():
        file_path = root / relative
        checks[f"file::{relative}"] = file_path.is_file() and file_sha256(file_path) == expected
    result = {
        "schema": "osl.emergence.freeze-verification.v1",
        "freeze_digest": expected_digest,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    return result


def make_freeze(root: Path, config: ExperimentConfig) -> dict[str, Any]:
    tracked = ["experiment/osl_emergence_pilot.py", "EXPERIMENT_PROTOCOL.md", "CONFIG.json"]
    payload = {
        "schema": "osl.emergence.preoutcome-freeze.v1",
        "version": VERSION,
        "scientific_status": "PREOUTCOME_DEVELOPMENT_PROTOCOL_FREEZE",
        "holdout_seeds": list(config.holdout_seeds),
        "model_seeds": list(config.model_seeds),
        "files": {relative: file_sha256(root / relative) for relative in tracked},
        "claim_boundary": "The holdout seeds and analysis endpoints are fixed before final model training and holdout evaluation.",
    }
    payload["digest"] = digest(payload)
    (root / "PREOUTCOME_FREEZE.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def deterministic_recheck(root: Path, config: ExperimentConfig) -> dict[str, Any]:
    # Re-evaluate one frozen checkpoint twice to verify deterministic inference and metrics.
    vocab, datasets, _, eq_test = build_data(config)
    checkpoint = root / "checkpoints" / f"operator_regularized_seed_{config.model_seeds[0]}.pt"
    first = evaluate_checkpoint(
        checkpoint,
        "operator_regularized",
        config.model_seeds[0],
        config,
        vocab,
        {k: v for k, v in datasets.items() if k not in {"train", "val"}},
        datasets["train"],
        eq_test,
    )
    second = evaluate_checkpoint(
        checkpoint,
        "operator_regularized",
        config.model_seeds[0],
        config,
        vocab,
        {k: v for k, v in datasets.items() if k not in {"train", "val"}},
        datasets["train"],
        eq_test,
    )
    exact = canonical_json(first) == canonical_json(second)
    result = {
        "schema": "osl.emergence.deterministic-recheck.v1",
        "checkpoint": checkpoint.name,
        "exact_metric_replay": exact,
        "first_digest": digest(first),
        "second_digest": digest(second),
    }
    (root / "results" / "DETERMINISTIC_RECHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "run", "verify", "recheck"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    config = ExperimentConfig(**json.loads((root / "CONFIG.json").read_text(encoding="utf-8")))
    if args.command == "freeze":
        print(json.dumps(make_freeze(root, config), indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        result = verify_freeze(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["all_checks_pass"] else 1
    if args.command == "run":
        freeze = verify_freeze(root)
        if not freeze["all_checks_pass"]:
            raise RuntimeError("preoutcome freeze verification failed")
        report = run_experiment(root, config)
        print(json.dumps({
            "status": report["scientific_status"],
            "endpoints": f"{report['endpoint_pass_count']}/{report['endpoint_count']}",
            "all_endpoints_met": report["all_endpoints_met"],
            "digest": report["digest"],
        }, indent=2))
        return 0
    if args.command == "recheck":
        result = deterministic_recheck(root, config)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["exact_metric_replay"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
