from __future__ import annotations

import numpy as np

import komorebi_pr_lasm as lasm
from komorebi_pr_lasm.refinement import PacketTree, best_basis, l1_packet_cost


def test_public_facade_reports_repository_version() -> None:
    assert lasm.__version__ == "2.3.0"


def test_public_facade_exact_reconstruction() -> None:
    frame = np.arange(64, dtype=np.int16).reshape(8, 8) % 16
    analysis = lasm.MultiAtlasAnalyzer(lasm.MultiAtlasConfig(haar_levels=3)).analyze(frame)
    residuals = analysis.reconstruction_residuals()
    assert max(residuals.values()) < 1e-12
    assert np.max(np.abs(analysis.tight_frame_synthesis() - frame)) < 1e-12


def test_public_facade_packet_tree_reconstruction() -> None:
    values = np.linspace(-1.0, 1.0, 64)
    tree = PacketTree.analyze(values, maximum_depth=6)
    selected = best_basis(tree, cost=l1_packet_cost, packet_penalty=0.05)
    rebuilt = tree.synthesize(selected.paths)
    assert np.max(np.abs(rebuilt - values)) < 1e-12


def test_public_facade_exposes_typed_model() -> None:
    model = lasm.ProjectorResolvedLargeSignalModel()
    summary = model.posterior_summary()
    assert summary["best_program"] is None
    assert len(lasm.default_lasm_programs()) >= 1
