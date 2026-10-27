from __future__ import annotations

from rrct_lab.metrics import functional_profile


def test_fuzzy_j_causal_metrics_map_to_existing_profile_axes() -> None:
    profile = functional_profile(
        {
            "jspace_ablation_drop": 0.61,
            "workspace_decodability": 0.99,
            "provenance_accuracy": 0.73,
            "planner_cut_drop": 0.47,
            "plan_accuracy": 0.98,
            "recurrence_reopen_rate": 0.82,
            "broadcast_ablation_drop": 0.56,
            "formation_accuracy": 0.77,
            "causal_membership_calibration": 0.68,
        }
    )
    axes = profile["axes"]
    assert axes["global_access"] == 0.61
    assert axes["autobiographical_provenance"] == 0.73
    assert axes["planner_coupling"] == 0.47
    assert axes["feedback_recurrence"] == 0.82
    assert axes["distributed_integration"] == 0.56
    assert axes["endogenous_formation"] == 0.77
    assert axes["fuzzy_structure"] == 0.68


if __name__ == "__main__":
    test_fuzzy_j_causal_metrics_map_to_existing_profile_axes()
    print("test_metrics: 1 direct test passed")
