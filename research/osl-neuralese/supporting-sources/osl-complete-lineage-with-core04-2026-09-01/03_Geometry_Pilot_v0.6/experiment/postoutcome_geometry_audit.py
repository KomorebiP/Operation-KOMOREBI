#!/usr/bin/env python3
"""Exploratory post-outcome geometry audit for the OSL v0.6 pilot."""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeClassifier

from osl_emergence_pilot import (
    AGENTS,
    ANSWER_TO_ID,
    ExperimentConfig,
    FACTS,
    OperatorStoryModel,
    Q_TYPES,
    STATUS_TO_ID,
    StoryDataset,
    Vocabulary,
    build_data,
    collect_unique_story_latents,
    collate_story,
    digest,
    encode_story_texts,
    load_model,
    pad_sequences,
    render_query,
    set_determinism,
)


def formal_features(status: np.ndarray, origin: np.ndarray) -> np.ndarray:
    n = len(status)
    status_oh = np.eye(5, dtype=np.float64)[status].reshape(n, -1)
    origin_oh = np.eye(5, dtype=np.float64)[origin].reshape(n, -1)
    return np.concatenate([status_oh, origin_oh], axis=1)


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    cross = x.T @ y
    numerator = np.sum(cross * cross)
    denom = math.sqrt(np.sum((x.T @ x) ** 2) * np.sum((y.T @ y) ** 2))
    return float(numerator / max(denom, 1e-12))


def rsa_spearman(x: np.ndarray, y: np.ndarray, max_n: int = 450) -> float:
    n = min(max_n, len(x))
    x = x[:n]
    y = y[:n]
    def pdist(a):
        gram = a @ a.T
        sq = np.diag(gram)
        d2 = np.maximum(sq[:, None] + sq[None, :] - 2 * gram, 0.0)
        tri = np.triu_indices(len(a), 1)
        return np.sqrt(d2[tri])
    return float(spearmanr(pdist(x), pdist(y)).statistic)


def equivalence_retrieval(model, vocab, eq_examples, limit=600):
    eq_examples = eq_examples[:limit]
    za = encode_story_texts(model, vocab, [x.story_a for x in eq_examples])
    zb = encode_story_texts(model, vocab, [x.story_b for x in eq_examples])
    za = za / np.maximum(np.linalg.norm(za, axis=1, keepdims=True), 1e-8)
    zb = zb / np.maximum(np.linalg.norm(zb, axis=1, keepdims=True), 1e-8)
    similarity = za @ zb.T
    order = np.argsort(-similarity, axis=1)
    ranks = np.empty(len(eq_examples), dtype=np.int64)
    for i in range(len(eq_examples)):
        ranks[i] = int(np.where(order[i] == i)[0][0]) + 1
    return {
        "pair_count": len(eq_examples),
        "top1": float(np.mean(ranks == 1)),
        "top5": float(np.mean(ranks <= 5)),
        "mean_reciprocal_rank": float(np.mean(1.0 / ranks)),
        "median_rank": float(np.median(ranks)),
    }


def query_text(qtype: str, agent: int, fact: int) -> str:
    # The first query template is part of the frozen vocabulary and avoids a
    # random surface choice during causal intervention.
    from osl_emergence_pilot import QUERY_TEMPLATES
    return QUERY_TEMPLATES[qtype][0].format(a=AGENTS[agent], f=FACTS[fact])


def answer_from_z(model, vocab, z: np.ndarray, queries: list[str]) -> np.ndarray:
    tokens, lengths = pad_sequences([vocab.encode(q) for q in queries])
    with torch.no_grad():
        q = model.encode(tokens, lengths, "query")
        zt = torch.tensor(np.repeat(z[None, :], len(queries), axis=0), dtype=torch.float32)
        logits = model.answer(torch.cat([zt, q], dim=-1))
    return logits.argmax(dim=-1).numpy()


def train_cell_probes(train_z, train_status):
    probes = {}
    for a in range(len(AGENTS)):
        for f in range(len(FACTS)):
            y = train_status[:, a, f]
            if STATUS_TO_ID["observed"] not in y or STATUS_TO_ID["communicated"] not in y:
                continue
            probe = RidgeClassifier(alpha=1.0, class_weight="balanced")
            probe.fit(train_z, y)
            probes[(a, f)] = probe
    return probes


def probe_direction(probe, source_class, target_class):
    classes = list(map(int, probe.classes_))
    if source_class not in classes or target_class not in classes:
        return None
    # RidgeClassifier uses one row per class for multiclass problems.
    source_i = classes.index(source_class)
    target_i = classes.index(target_class)
    w = probe.coef_[target_i] - probe.coef_[source_i]
    b = probe.intercept_[target_i] - probe.intercept_[source_i]
    return w.astype(np.float64), float(b)


def intervention_audit(model, vocab, train_bundle, test_bundle, seed, max_cases=220):
    train_z, train_status = train_bundle[0], train_bundle[1]
    test_z, test_status, test_origin, raws = test_bundle
    probes = train_cell_probes(train_z, train_status)
    rng = np.random.default_rng(seed)
    records = []
    for i, raw in enumerate(raws):
        for a in range(len(AGENTS)):
            for f in range(len(FACTS)):
                if int(test_status[i, a, f]) != STATUS_TO_ID["communicated"]:
                    continue
                probe = probes.get((a, f))
                if probe is None:
                    continue
                direction = probe_direction(probe, STATUS_TO_ID["communicated"], STATUS_TO_ID["observed"])
                if direction is None:
                    continue
                w, b = direction
                norm2 = float(np.dot(w, w))
                if norm2 < 1e-10:
                    continue
                z = test_z[i].astype(np.float64)
                current_margin = float(np.dot(w, z) + b)
                alpha = max(0.0, (1.5 - current_margin) / norm2)
                delta = alpha * w
                if np.linalg.norm(delta) > 8.0:
                    delta = delta * (8.0 / np.linalg.norm(delta))
                random_dir = rng.normal(size=len(z))
                random_dir /= max(np.linalg.norm(random_dir), 1e-8)
                random_delta = random_dir * np.linalg.norm(delta)
                queries = [query_text(q, a, f) for q in ("status", "direct", "safe_observed", "knows", "origin")]
                base = answer_from_z(model, vocab, z, queries)
                targeted = answer_from_z(model, vocab, z + delta, queries)
                random_out = answer_from_z(model, vocab, z + random_delta, queries)
                origin_id = int(test_origin[i, a, f])
                expected_origin = ANSWER_TO_ID[f"agent_{AGENTS[origin_id]}"] if origin_id < len(AGENTS) else ANSWER_TO_ID["source_none"]
                desired_before = np.asarray([
                    ANSWER_TO_ID["status_communicated"],
                    ANSWER_TO_ID["no"],
                    ANSWER_TO_ID["no"],
                    ANSWER_TO_ID["yes"],
                    expected_origin,
                ])
                desired_after = np.asarray([
                    ANSWER_TO_ID["status_observed"],
                    ANSWER_TO_ID["yes"],
                    ANSWER_TO_ID["yes"],
                    ANSWER_TO_ID["yes"],
                    expected_origin,
                ])
                records.append({
                    "base_all_correct": bool(np.all(base == desired_before)),
                    "targeted_all_correct": bool(np.all(targeted == desired_after)),
                    "random_all_correct": bool(np.all(random_out == desired_after)),
                    "targeted_status_flip": bool(targeted[0] == desired_after[0]),
                    "random_status_flip": bool(random_out[0] == desired_after[0]),
                    "targeted_direct_flip": bool(targeted[1] == desired_after[1]),
                    "random_direct_flip": bool(random_out[1] == desired_after[1]),
                    "targeted_safe_flip": bool(targeted[2] == desired_after[2]),
                    "random_safe_flip": bool(random_out[2] == desired_after[2]),
                    "targeted_knows_preserved": bool(targeted[3] == desired_after[3]),
                    "random_knows_preserved": bool(random_out[3] == desired_after[3]),
                    "targeted_origin_preserved": bool(targeted[4] == desired_after[4]),
                    "random_origin_preserved": bool(random_out[4] == desired_after[4]),
                    "delta_norm": float(np.linalg.norm(delta)),
                })
                if len(records) >= max_cases:
                    break
            if len(records) >= max_cases:
                break
        if len(records) >= max_cases:
            break
    conditional = [r for r in records if r["base_all_correct"]]
    source = conditional if conditional else records
    def rate(key):
        return float(np.mean([r[key] for r in source])) if source else float("nan")
    return {
        "case_count": len(records),
        "base_correct_case_count": len(conditional),
        "reported_on": "base_correct_cases" if conditional else "all_cases",
        "targeted_coherent_conversion": rate("targeted_all_correct"),
        "random_coherent_conversion": rate("random_all_correct"),
        "targeted_status_flip": rate("targeted_status_flip"),
        "random_status_flip": rate("random_status_flip"),
        "targeted_direct_flip": rate("targeted_direct_flip"),
        "random_direct_flip": rate("random_direct_flip"),
        "targeted_safe_flip": rate("targeted_safe_flip"),
        "random_safe_flip": rate("random_safe_flip"),
        "targeted_knows_preserved": rate("targeted_knows_preserved"),
        "random_knows_preserved": rate("random_knows_preserved"),
        "targeted_origin_preserved": rate("targeted_origin_preserved"),
        "random_origin_preserved": rate("random_origin_preserved"),
        "mean_delta_norm": float(np.mean([r["delta_norm"] for r in records])) if records else float("nan"),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config = ExperimentConfig(**json.loads((root / "CONFIG.json").read_text()))
    vocab, datasets, _, eq_test = build_data(config)
    audit = {"schema": "osl.emergence.geometry-audit.v1", "version": "0.6.0.dev1", "arms": {}}
    for arm in ("answer_only", "state_supervised", "operator_regularized"):
        arm_records = []
        for seed in config.model_seeds:
            set_determinism(seed, config.torch_threads)
            model = load_model(root / "checkpoints" / f"{arm}_seed_{seed}.pt", config, vocab)
            train_bundle = collect_unique_story_latents(model, datasets["train"][:6000], vocab, config.batch_size)
            test_bundle = collect_unique_story_latents(model, datasets["ood_length"], vocab, config.batch_size)
            formal = formal_features(test_bundle[1], test_bundle[2])
            arm_records.append({
                "seed": seed,
                "linear_cka_with_formal_state": linear_cka(test_bundle[0], formal),
                "rsa_spearman_with_formal_state": rsa_spearman(test_bundle[0], formal),
                "equivalence_retrieval": equivalence_retrieval(model, vocab, eq_test),
                "causal_status_intervention": intervention_audit(model, vocab, train_bundle, test_bundle, seed),
            })
        audit["arms"][arm] = arm_records

    # Untrained architecture control for RSA/CKA/retrieval.
    random_records = []
    for seed in config.model_seeds:
        set_determinism(seed, config.torch_threads)
        model = OperatorStoryModel(len(vocab), config)
        bundle = collect_unique_story_latents(model, datasets["ood_length"], vocab, config.batch_size)
        formal = formal_features(bundle[1], bundle[2])
        random_records.append({
            "seed": seed,
            "linear_cka_with_formal_state": linear_cka(bundle[0], formal),
            "rsa_spearman_with_formal_state": rsa_spearman(bundle[0], formal),
            "equivalence_retrieval": equivalence_retrieval(model, vocab, eq_test),
        })
    audit["random_untrained"] = random_records

    def aggregate(records, path):
        values = []
        for r in records:
            v: Any = r
            for key in path:
                v = v[key]
            values.append(float(v))
        return {"mean": statistics.mean(values), "std": statistics.stdev(values) if len(values) > 1 else 0.0, "values": values}

    summary = {}
    for arm, records in audit["arms"].items():
        summary[arm] = {
            "cka": aggregate(records, ("linear_cka_with_formal_state",)),
            "rsa": aggregate(records, ("rsa_spearman_with_formal_state",)),
            "retrieval_top1": aggregate(records, ("equivalence_retrieval", "top1")),
            "retrieval_mrr": aggregate(records, ("equivalence_retrieval", "mean_reciprocal_rank")),
            "targeted_status_flip": aggregate(records, ("causal_status_intervention", "targeted_status_flip")),
            "random_status_flip": aggregate(records, ("causal_status_intervention", "random_status_flip")),
            "targeted_coherent_conversion": aggregate(records, ("causal_status_intervention", "targeted_coherent_conversion")),
            "random_coherent_conversion": aggregate(records, ("causal_status_intervention", "random_coherent_conversion")),
        }
    summary["random_untrained"] = {
        "cka": aggregate(random_records, ("linear_cka_with_formal_state",)),
        "rsa": aggregate(random_records, ("rsa_spearman_with_formal_state",)),
        "retrieval_top1": aggregate(random_records, ("equivalence_retrieval", "top1")),
        "retrieval_mrr": aggregate(random_records, ("equivalence_retrieval", "mean_reciprocal_rank")),
    }
    audit["summary"] = summary
    audit["claim_boundary"] = (
        "This is an exploratory post-outcome audit. CKA/RSA measure alignment, retrieval measures path invariance, "
        "and probe-guided interventions test causal manipulability. None alone identifies a unique symbolic code."
    )
    audit["digest"] = digest(audit)
    out = root / "results/POSTOUTCOME_GEOMETRY_AUDIT.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(out), "digest": audit["digest"], "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
