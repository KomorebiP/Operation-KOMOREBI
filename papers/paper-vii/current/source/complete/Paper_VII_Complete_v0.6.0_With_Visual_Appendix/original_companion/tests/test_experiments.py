from projector_quantum_calculus.experiments import run_experiments


def test_experiment_certificates() -> None:
    r = run_experiments()
    assert r["bell"]["state_error"] < 1e-12
    assert r["symmetry"]["parity_off_block_norm"] < 1e-12
    assert r["symmetry"]["circuit_path_reconstruction_error"] < 1e-12
    assert r["symmetry"]["maximum_leakage_bound_violation"] < 1e-9
    assert r["effective_dynamics"]["feshbach_resolvent_error"] < 1e-10
    assert r["effective_dynamics"]["moving_frame_error"] < 1e-6
    assert r["effective_dynamics"]["canonical_connection_error"] < 1e-10
    assert r["channels"]["kraus_completeness_error"] < 1e-12
    assert r["geometry"]["circle_observed_order"] > 1.95
    assert r["geometry"]["minimum_transfer_eigenvalue"] > 0
    assert r["geometry"]["transfer_semigroup_error"] < 1e-10
