#!/usr/bin/env python3
"""Post-outcome controls for OSL Emergent Operator Geometry Pilot v0.6.

These controls were not part of the pre-outcome endpoint set.  They probe
alternative explanations: random recurrent features, lexical bag-of-words state
recovery, shuffled labels, and architecture-induced affine transition fits.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score

from osl_emergence_pilot import (
    AGENTS,
    FACTS,
    ExperimentConfig,
    OperatorStoryModel,
    build_data,
    cell_features,
    collect_unique_story_latents,
    digest,
    equivalence_geometry,
    linear_probe_metrics,
    set_determinism,
    transition_geometry_metrics,
)


def lexical_cell_dataset(examples):
    by_story = {}
    for ex in examples:
        by_story.setdefault(ex.story, ex)
    docs = []
    status = []
    origin = []
    for ex in by_story.values():
        s = np.asarray(ex.state_status)
        o = np.asarray(ex.state_origin)
        for a, agent in enumerate(AGENTS):
            for f, fact in enumerate(FACTS):
                docs.append(f"{ex.story} cell_agent {agent} cell_fact {fact}")
                status.append(int(s[a, f]))
                origin.append(int(o[a, f]))
    return docs, np.asarray(status), np.asarray(origin)


def lexical_probe(train_examples, test_examples):
    train_docs, train_s, train_o = lexical_cell_dataset(train_examples)
    test_docs, test_s, test_o = lexical_cell_dataset(test_examples)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=50000)
    x_train = vectorizer.fit_transform(train_docs)
    x_test = vectorizer.transform(test_docs)
    status = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(x_train, train_s)
    origin = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(x_train, train_o)
    sp = status.predict(x_test)
    op = origin.predict(x_test)
    return {
        "status_accuracy": float(accuracy_score(test_s, sp)),
        "origin_accuracy": float(accuracy_score(test_o, op)),
        "status_balanced_accuracy": float(balanced_accuracy_score(test_s, sp)),
        "origin_balanced_accuracy": float(balanced_accuracy_score(test_o, op)),
        "vocabulary_size": len(vectorizer.vocabulary_),
    }


def shuffled_probe(train_bundle, test_bundle, seed):
    train_x, train_s, train_o = cell_features(train_bundle[0], train_bundle[1], train_bundle[2])
    test_x, test_s, test_o = cell_features(test_bundle[0], test_bundle[1], test_bundle[2])
    rng = np.random.default_rng(seed)
    train_s = rng.permutation(train_s)
    train_o = rng.permutation(train_o)
    status = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(train_x, train_s)
    origin = RidgeClassifier(alpha=1.0, class_weight="balanced").fit(train_x, train_o)
    sp = status.predict(test_x)
    op = origin.predict(test_x)
    return {
        "status_balanced_accuracy": float(balanced_accuracy_score(test_s, sp)),
        "origin_balanced_accuracy": float(balanced_accuracy_score(test_o, op)),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config = ExperimentConfig(**json.loads((root / "CONFIG.json").read_text()))
    vocab, datasets, _, eq_test = build_data(config)
    random_records = []
    for seed in config.model_seeds:
        set_determinism(seed, config.torch_threads)
        model = OperatorStoryModel(len(vocab), config)
        train_bundle = collect_unique_story_latents(model, datasets["train"][:6000], vocab, config.batch_size)
        test_bundle = collect_unique_story_latents(model, datasets["ood_length"], vocab, config.batch_size)
        random_records.append({
            "seed": seed,
            "linear_probe": linear_probe_metrics(train_bundle, test_bundle, seed),
            "shuffled_probe": shuffled_probe(train_bundle, test_bundle, seed + 1000),
            "equivalence_geometry": equivalence_geometry(model, vocab, eq_test, seed),
            "transition_geometry": transition_geometry_metrics(model, vocab, datasets["train"], datasets["ood_length"], seed),
        })

    def mean(path):
        vals = []
        for record in random_records:
            value: Any = record
            for key in path:
                value = value[key]
            vals.append(float(value))
        return {"mean": statistics.mean(vals), "values": vals}

    lexical = lexical_probe(datasets["train"], datasets["ood_length"])
    trained = json.loads((root / "results/PILOT_ANALYSIS.json").read_text())
    answer = trained["aggregate"]["answer_only"]
    report = {
        "schema": "osl.emergence.postoutcome-controls.v1",
        "version": "0.6.0.dev1",
        "scientific_status": "POSTOUTCOME_ALTERNATIVE_EXPLANATION_AUDIT",
        "random_untrained_models": random_records,
        "random_aggregate": {
            "status_balanced_probe": mean(("linear_probe", "linear_probe_status_balanced_accuracy")),
            "origin_balanced_probe": mean(("linear_probe", "linear_probe_origin_balanced_accuracy")),
            "shuffled_status_balanced_probe": mean(("shuffled_probe", "status_balanced_accuracy")),
            "shuffled_origin_balanced_probe": mean(("shuffled_probe", "origin_balanced_accuracy")),
            "equivalence_distance_separation": mean(("equivalence_geometry", "distance_separation")),
            "affine_transition_r2": mean(("transition_geometry", "affine_transition_r2")),
            "operator_advantage_vs_noop": mean(("transition_geometry", "operator_advantage_vs_noop")),
            "operator_advantage_vs_shuffled": mean(("transition_geometry", "operator_advantage_vs_shuffled")),
        },
        "tfidf_state_probe": lexical,
        "trained_answer_only_reference": {
            "status_balanced_probe": answer["linear_probe.linear_probe_status_balanced_accuracy"]["mean"],
            "origin_balanced_probe": answer["linear_probe.linear_probe_origin_balanced_accuracy"]["mean"],
            "equivalence_distance_separation": answer["equivalence_geometry.distance_separation"]["mean"],
            "affine_transition_r2": answer["transition_geometry.affine_transition_r2"]["mean"],
        },
        "interpretation_rules": {
            "learned_state_geometry": "Supported only when trained probes exceed both shuffled-label and untrained-feature controls.",
            "operator_transition_geometry": "Not attributed to learning if untrained recurrent features obtain comparable affine transition scores.",
            "lexical_shortcut": "Retained as a viable alternative when TF-IDF state or answer baselines are competitive.",
        },
        "claim_boundary": (
            "These post-outcome controls refine interpretation but do not modify the sealed endpoint set. "
            "Random-feature decodability or transition predictability demonstrates architectural inductive bias, "
            "not learned operator semantics."
        ),
    }
    report["digest"] = digest(report)
    out = root / "results/POSTOUTCOME_CONTROLS.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(out), "digest": report["digest"], "random_aggregate": report["random_aggregate"], "tfidf_state_probe": lexical}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
