from __future__ import annotations

import inspect
import json

from block23.core import (
    FAMILIES, EpisodeSpec, audit_hidden, build_episode, compile_ontology,
    expected_certificate,
)


def test_visible_contract_hides_family_and_gold_semantics():
    ep = build_episode(EpisodeSpec("identified", 91, "preaudit"))
    assert not hasattr(ep.visible, "spec")
    assert not hasattr(ep.visible, "family")
    assert ep.visible.visible_contract["gold_intermediate_semantics_visible"] is False


def test_compiler_source_does_not_read_hidden_audit():
    source = inspect.getsource(compile_ontology)
    assert "audit_hidden" not in source
    assert ".hidden" not in source
    assert ".family" not in source


def test_all_final_certificates():
    for i in range(36):
        family = FAMILIES[i % len(FAMILIES)]
        seed = 23100 + i
        ep = build_episode(EpisodeSpec(family, seed, "final"))
        co = compile_ontology(ep.visible, seed + 17011)
        result = audit_hidden(ep, co)
        assert result["certificate"] == expected_certificate(family)


def test_answer_shortcut_is_not_accepted_as_semantic_quotient():
    ep = build_episode(EpisodeSpec("answer_shortcut", 23101, "final"))
    co = compile_ontology(ep.visible, 23101 + 17011)
    rows = [r for r in co.candidate_table if r["method"] == "answer_only"]
    assert len(rows) == 1
    assert rows[0]["worst_answer_accuracy"] >= 0.78
    assert rows[0]["passed"] is False
    assert co.selected_method != "answer_only"


def test_counterfactual_patch_requires_selected_packet():
    ep = build_episode(EpisodeSpec("identified", 23100, "final"))
    co = compile_ontology(ep.visible, 23100 + 17011)
    result = audit_hidden(ep, co)
    for system in result["counterfactual_patch"].values():
        assert system["selected_future_r2"] > 0.98
        assert system["answer_only_future_r2"] < 0.0
        assert system["pca_future_r2"] < 0.0


def test_collision_produces_information_loss_certificate():
    ep = build_episode(EpisodeSpec("destructive_loss", 23105, "final"))
    co = compile_ontology(ep.visible, 23105 + 17011)
    assert co.pre_certificate == "NO_GO"
    result = audit_hidden(ep, co)
    assert result["certificate"] == "SEMANTIC_INFORMATION_LOSS"
    assert result["collision_count"] >= 48
    assert result["minimum_protected_consequence_gap"] >= 0.75
