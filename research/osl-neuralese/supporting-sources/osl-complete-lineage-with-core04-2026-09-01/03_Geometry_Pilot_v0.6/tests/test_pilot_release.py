from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "experiment"))

from osl_emergence_pilot import (
    Event,
    ExperimentConfig,
    WorldState,
    apply_event,
    build_data,
    make_equivalent_pair,
    verify_freeze,
)


def test_preoutcome_freeze_still_verifies() -> None:
    assert verify_freeze(ROOT)["all_checks_pass"]


def test_operator_equivalence_generator_is_exact() -> None:
    import random
    rng = random.Random(711)
    for _ in range(250):
        a, b, expected = make_equivalent_pair(rng)
        sa = WorldState.empty()
        sb = WorldState.empty()
        for event in a:
            sa = apply_event(sa, event)
        for event in b:
            sb = apply_event(sb, event)
        assert sa.key() == sb.key() == expected.key()


def test_dataset_is_deterministic() -> None:
    config = ExperimentConfig(**json.loads((ROOT / "CONFIG.json").read_text()))
    _, first, _, _ = build_data(config)
    _, second, _, _ = build_data(config)
    assert [x.story for x in first["ood_combined"][:100]] == [x.story for x in second["ood_combined"][:100]]
    assert [x.answer for x in first["ood_combined"][:100]] == [x.answer for x in second["ood_combined"][:100]]


def test_frozen_analysis_and_replay() -> None:
    analysis = json.loads((ROOT / "results/PILOT_ANALYSIS.json").read_text())
    replay = json.loads((ROOT / "results/DETERMINISTIC_RECHECK.json").read_text())
    assert analysis["endpoint_pass_count"] == analysis["endpoint_count"] == 8
    assert analysis["all_endpoints_met"]
    assert replay["exact_metric_replay"]
    assert replay["first_digest"] == replay["second_digest"]


def test_postoutcome_controls_narrow_the_claim() -> None:
    frozen = json.loads((ROOT / "results/PILOT_ANALYSIS.json").read_text())
    controls = json.loads((ROOT / "results/POSTOUTCOME_CONTROLS.json").read_text())
    random_r2 = controls["random_aggregate"]["affine_transition_r2"]["mean"]
    trained_r2 = frozen["aggregate"]["answer_only"]["transition_geometry.affine_transition_r2"]["mean"]
    assert random_r2 > trained_r2
    assert controls["tfidf_state_probe"]["status_balanced_accuracy"] > frozen["aggregate"]["answer_only"]["linear_probe.linear_probe_status_balanced_accuracy"]["mean"]


def test_supervision_improves_formal_alignment_and_retrieval() -> None:
    audit = json.loads((ROOT / "results/POSTOUTCOME_GEOMETRY_AUDIT.json").read_text())["summary"]
    assert audit["state_supervised"]["cka"]["mean"] > audit["answer_only"]["cka"]["mean"]
    assert audit["operator_regularized"]["retrieval_top1"]["mean"] > audit["state_supervised"]["retrieval_top1"]["mean"]
    assert audit["answer_only"]["retrieval_top1"]["mean"] > audit["random_untrained"]["retrieval_top1"]["mean"]


def test_no_coherent_causal_operator_claim() -> None:
    sweep = json.loads((ROOT / "results/POSTOUTCOME_INTERVENTION_SWEEP.json").read_text())["summary"]
    assert sweep["answer_only"]["targeted_coherent_rate"]["mean"] == 0.0
    assert sweep["operator_regularized"]["targeted_coherent_rate"]["mean"] < 0.03


def test_final_adjudication_is_bounded() -> None:
    result = json.loads((ROOT / "results/FINAL_ADJUDICATION.json").read_text())
    assert result["scientific_status"] == "PARTIAL_OPERATOR_RELEVANT_STRUCTURE_NOT_FULL_SYMBOLIC_EMERGENCE"
    assert "does not establish" in result["claim_boundary"].lower()
