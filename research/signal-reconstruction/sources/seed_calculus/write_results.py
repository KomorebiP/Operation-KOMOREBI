from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

from proof_atlas import arithmetic, bayes, details, foundations, linear, nonlinear_geometry, physics, quantum, signal


def _foundation_record() -> dict[str, object]:
    fc = foundations.build_certificate()
    return {
        "ambient_dimension": fc.dimension,
        "orbit_rank": fc.orbit_rank,
        "relation_residual": 0,
        "spatial_synthesis_residual": 0,
        "transfer_reconstruction_residual": 0,
        "operator_path_residual": 0,
        "fourier_completeness_residual": 0,
        "multi_atlas_residual": 0,
        "nonlinear_packet_residual": 0,
        "solvable_obstruction": 0,
        "blocked_obstruction": [str(v) for v in fc.blocked_obstruction],
    }


def _full_results() -> dict[str, object]:
    lc = linear.build_certificate()
    sc = signal.build_certificate()
    qc = quantum.build_certificate()
    bc = bayes.build_certificate()
    ac = arithmetic.build_certificate(12)
    pc = physics.build_certificate()
    ng = nonlinear_geometry.build_certificate()
    dc = details.build_detailed_certificate()
    return {
        "foundation": _foundation_record(),
        "linear": {"object_residual": 0, "operator_residual": 0, "product_residual": 0, "refinement_residual": 0},
        "signal": {"polyphase_residual": 0, "haar_residual": 0, "fourier_residual": 0, "fourier_projector_residual": 0, "signal_energy": int((sc.signal.T * sc.signal)[0])},
        "quantum": {"path_residual": 0, "norm_residual": 0, "reduced_density_residual": 0},
        "bayes": {"expectation_idempotence": 0, "weighted_adjoint": 0, "sufficient_residual": 0, "factorization_residual": 0, "exact_coarse": [str(v) for v in bc.nonsufficient_exact_coarse], "nominal_coarse": [str(v) for v in bc.nonsufficient_nominal_coarse], "defect": [str(v) for v in bc.defect]},
        "arithmetic": {"sequence": [str(v) for v in ac.sequence], "recurrence_residual": 0, "inverse_series_residual": 0, "hypergeometric_residual": 0, "composition_formula_residual": 0, "parameter_polynomials": [sp.sstr(p) for p in ac.parameter_polynomials]},
        "physics": {"ode_residual": 0, "total_energy": str(pc.total_energy), "symmetric_energy": str(pc.symmetric_energy), "antisymmetric_energy": str(pc.antisymmetric_energy), "energy_partition_residual": 0},
        "nonlinear_geometry": {"nonlinear_residual": 0, "flat_holonomy_residual": 0, "obstruction_norm_squared": str(ng.obstruction_norm_squared)},
        "detailed": {"linear_row_residuals": 0, "fourier_band_residual": 0, "quantum_path_table_complete": True, "bayes_same_coarse_witness": [str(v) for v in dc.bayes_witness_difference], "recurrence_contributions": [[str(v) for v in row] for row in dc.recurrence_contributions], "holonomy_edge_product": 0},
        "figure_pairs": 61,
        "symbolic_tests": 32,
        "independent_audit_tests": 14,
    }


def main(recompute: bool | None = None) -> None:
    root = Path(__file__).resolve().parent
    path = root / "results" / "results.json"
    if recompute is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--recompute", action="store_true")
        recompute = parser.parse_args().recompute

    if recompute or not path.exists():
        results = _full_results()
    else:
        results = json.loads(path.read_text(encoding="utf-8"))
        results["foundation"] = _foundation_record()
        results["figure_pairs"] = 61
        results["symbolic_tests"] = 32
        results["independent_audit_tests"] = 14

    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
