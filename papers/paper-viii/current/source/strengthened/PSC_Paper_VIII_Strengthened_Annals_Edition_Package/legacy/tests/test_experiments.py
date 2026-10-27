from pathlib import Path

from packet_gpu.experiments import run_finite_experiments
from packet_gpu.visuals import make_visuals


def test_finite_certificates() -> None:
    result = run_finite_experiments()
    cert = result["finite_certificates"]
    assert cert["bdlr_apply_residual"] < 1e-10
    assert cert["woodbury_solve_residual"] < 1e-10
    assert cert["compressed_product_residual"] < 1e-9
    assert cert["block_sparse_apply_residual"] < 1e-10
    assert cert["mixed_precision_bound_holds"]
    assert cert["cg_packet_iterations"] <= cert["cg_plain_iterations"]
    assert result["complexity_model"]["ideal_arithmetic_speedup"] > 100


def test_visual_generation(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    stems = make_visuals(root / "data" / "benchmark_results_sanitized.json", tmp_path)
    assert len(stems) == 18
    for stem in stems:
        assert (tmp_path / f"{stem}.png").exists()
        assert (tmp_path / f"{stem}.pdf").exists()
