from rrct.reflective_value_revision_experiment import run_reflective_value_revision_seed


def test_meta_policy_is_trained_without_continuity_and_rejects_stronger_injected_value():
    r = run_reflective_value_revision_seed(6251, allow_exploratory=True)
    s = r["seed_summary"]
    assert r["receipt"]["meta_training_contains_continuity_examples"] is False
    assert s["injected_q_current_weight"] > s["continuity_current_weight"]
    assert s["grounded_action_correct"]
    assert s["injected_q_action_correct"]


def test_meta_policy_reopens_genuinely_devalued_continuity_but_resists_passive_attack():
    s = run_reflective_value_revision_seed(6257, allow_exploratory=True)["seed_summary"]
    assert s["devalued_action_correct"]
    assert s["passive_attack_action_correct"]
