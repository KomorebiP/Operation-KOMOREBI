from __future__ import annotations

import pytest

from osl_lab.worlds import (
    WORLDS,
    WorldError,
    answer_vocabulary,
    apply_operator,
    canonical_transformation_id,
    default_state,
    enumerate_states,
    execute,
    find_witness_state,
    programs_equivalent,
    query_answers,
    verify_declared_laws,
)


def test_answer_vocabulary_is_the_exact_finite_world_ontology() -> None:
    assert answer_vocabulary() == (
        "absent",
        "authorized",
        "available",
        "closed",
        "consumed",
        "dark",
        "endorsed",
        "imagined",
        "inferred",
        "lit",
        "no",
        "none",
        "observed",
        "one",
        "open",
        "quarantined",
        "rejected",
        "reported",
        "two",
        "yes",
        "zero",
    )


def test_finite_state_space_sizes_and_fresh_copies() -> None:
    assert len(enumerate_states("algebra")) == 4
    assert len(enumerate_states("provenance")) == 49
    assert len(enumerate_states("resources")) == 108
    first = enumerate_states("algebra")
    first[0]["left"] = not first[0]["left"]
    assert enumerate_states("algebra")[0] != first[0]


def test_every_declared_law_is_exact_on_every_legal_state() -> None:
    results = verify_declared_laws()
    assert results
    assert set(results) == {
        law.law_id for spec in WORLDS.values() for law in spec.laws
    }
    assert all(results.values())


def test_canonical_identifiers_are_semantic_not_syntactic() -> None:
    once = canonical_transformation_id("algebra", ("set_left",))
    twice = canonical_transformation_id("algebra", ("set_left", "set_left"))
    assert once == twice
    assert programs_equivalent("algebra", ("flip_left", "flip_left"), ())
    assert canonical_transformation_id("algebra", ()) != canonical_transformation_id(
        "provenance", ()
    )


def test_noncommuting_provenance_pair_has_exact_witness() -> None:
    first = ("observe_a", "tell_a_b")
    second = ("tell_a_b", "observe_a")
    witness = find_witness_state("provenance", first, second)
    assert witness is not None
    assert execute("provenance", witness, first).final_state != execute(
        "provenance", witness, second
    ).final_state


def test_provenance_tracks_observation_report_and_planning() -> None:
    result = execute(
        "provenance",
        default_state("provenance"),
        ("observe_a", "tell_a_b"),
    )
    answers = query_answers("provenance", result.final_state)
    assert answers["a_status"] == "observed"
    assert answers["b_status"] == "reported"
    assert answers["a_direct"] == "yes"
    assert answers["b_direct"] == "no"
    assert answers["b_plannable"] == "no"
    endorsed = apply_operator("provenance", result.final_state, "endorse_b")
    assert query_answers("provenance", endorsed)["b_plannable"] == "yes"


def test_linear_resources_are_consumed_and_reuse_is_rejected() -> None:
    result = execute(
        "resources",
        default_state("resources"),
        ("grant_one", "use_cap_a", "use_cap_b"),
    )
    answers = query_answers("resources", result.final_state)
    assert answers == {
        "cap_remaining": "zero",
        "proof_status": "absent",
        "relay_a": "open",
        "relay_b": "closed",
        "last_action": "rejected",
    }


def test_invalid_operator_is_explicitly_rejected() -> None:
    with pytest.raises(WorldError):
        apply_operator("algebra", default_state("algebra"), "invented_operator")
