from rrct.meta_criterion_revision_experiment import run_meta_criterion_revision_seed


def test_anonymous_meta_criterion_is_discovered_without_continuity_or_channel_semantics():
    r = run_meta_criterion_revision_seed(6351, allow_exploratory=True)
    s = r["seed_summary"]
    assert r["receipt"]["criterion_training_contains_continuity_examples"] is False
    assert r["receipt"]["learner_receives_channel_semantics"] is False
    assert s["initial_holdout_r2"] > 0.85
    assert s["stable_audit_action_correct"]


def test_criterion_reopens_after_hidden_reliability_shift_and_repairs_heldout_self_cases():
    r = run_meta_criterion_revision_seed(6357, allow_exploratory=True)
    s = r["seed_summary"]
    assert s["shifted_audit_action_correct"]
    assert s["shifted_nonself_revised_mae"] < s["shifted_nonself_old_mae"]
    assert s["shifted_cases_correct"]
