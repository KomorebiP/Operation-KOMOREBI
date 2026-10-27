from __future__ import annotations

from pathlib import Path

import sympy as sp

from proof_atlas.foundations import build_certificate, matrix_zero

ROOT = Path(__file__).resolve().parents[1]


def test_seed_orbit_spans_the_ambient_space() -> None:
    c = build_certificate()
    assert c.orbit_rank == c.dimension == 8
    assert c.orbit_matrix.det() in (1, -1)


def test_seed_relation_is_exact() -> None:
    c = build_certificate()
    assert matrix_zero(c.relation_residual)
    assert matrix_zero(c.shift ** 8 - sp.eye(8))


def test_spatial_packet_reconstruction_is_exact() -> None:
    c = build_certificate()
    assert matrix_zero(c.spatial_reconstruction_residual)
    assert sum(c.spatial_packets, sp.zeros(8, 1)) == c.signal


def test_refinement_tree_is_exact() -> None:
    c = build_certificate()
    assert all(matrix_zero(r) for r in c.parity_refinement_residuals)
    assert all(matrix_zero(r) for r in c.mod4_to_spatial_residuals)


def test_transfer_blocks_reconstruct_the_operator() -> None:
    c = build_certificate()
    assert matrix_zero(c.transfer_reconstruction_residual)
    rebuilt = sum((c.transfer_blocks[b][a] for b in range(8) for a in range(8)), sp.zeros(8))
    assert rebuilt == c.operator


def test_operator_product_is_sum_over_packet_paths() -> None:
    c = build_certificate()
    assert matrix_zero(c.product_path_residual)


def test_fourier_character_packets_are_complete() -> None:
    c = build_certificate()
    assert matrix_zero(c.fourier_completeness_residual)
    assert all(matrix_zero(r) for r in c.fourier_idempotence_residuals)
    assert all(matrix_zero(r) for r in c.fourier_annihilation_residuals)


def test_weighted_multi_atlas_is_exact() -> None:
    c = build_certificate()
    assert matrix_zero(c.multi_atlas_reconstruction_residual)


def test_nonlinear_packet_interactions_reconstruct() -> None:
    c = build_certificate()
    assert matrix_zero(c.nonlinear_packet_residual)
    assert matrix_zero(c.bilinear_interaction_residual)


def test_obstruction_packet_has_positive_and_negative_controls() -> None:
    c = build_certificate()
    assert matrix_zero(c.solvable_obstruction)
    assert c.blocked_obstruction == sp.Matrix([-sp.Rational(1, 3), -sp.Rational(1, 3), sp.Rational(1, 3)])


def test_foundation_figure_pairs_exist() -> None:
    for index in range(38, 61):
        matches_pdf = list((ROOT / "figures").glob(f"{index:02d}_*.pdf"))
        matches_png = list((ROOT / "figures").glob(f"{index:02d}_*.png"))
        assert len(matches_pdf) == len(matches_png) == 1
        assert matches_pdf[0].stat().st_size > 1000
        assert matches_png[0].stat().st_size > 1000
