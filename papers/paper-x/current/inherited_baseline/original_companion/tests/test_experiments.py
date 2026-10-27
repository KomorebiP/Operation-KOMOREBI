import json

from projector_seed_residuals.experiments import run_experiments


def test_experiment_release(tmp_path) -> None:
    output = tmp_path / "results"
    results = run_experiments(output)
    assert results["transport"]["minimum_count"] == 3
    assert results["carrier_completion"]["recovered_multiplicities"] == (2, 0, 1)
    assert results["finite_occupancy"]["ranks"] == [3, 2, 1, 0]
    loaded = json.loads((output / "residual_seed_results.json").read_text())
    assert loaded["inverse_limit"]["compatible"] is True
