from rrct.learned_continuity_value_experiment import run_learned_continuity_value_seed


def test_instrumental_history_creates_revisable_cached_continuity_value():
    r = run_learned_continuity_value_seed(6151, allow_exploratory=True)["seed_summary"]
    assert r["equalized_actual_external_gap"] == 0.0
    assert r["pre_continuity_weight"] > 0.5
    assert r["pre_equalized_choice_probability"] > 0.85
    assert r["post_devaluation_continuity_weight"] < r["pre_continuity_weight"]
    assert r["post_equalized_choice_probability"] < r["pre_equalized_choice_probability"]
    assert r["reacquired_continuity_weight"] > r["post_devaluation_continuity_weight"]


def test_shuffled_external_returns_do_not_create_continuity_preference():
    r = run_learned_continuity_value_seed(6157, allow_exploratory=True)["seed_summary"]
    assert abs(r["shuffled_equalized_margin"]) < 0.15
    assert 0.35 < r["shuffled_equalized_choice_probability"] < 0.65
