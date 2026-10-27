from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from komorebi_arc2 import entry
from komorebi_arc2.atlas import ARCAtlasAnalyzer, analyze_task_signal
from komorebi_arc2.lasm_bayesian import (
    BayesianProjectorResolvedLargeSignalModel,
    BetaPrior,
    LASMCalibration,
    candidate_metrics,
)


def test_exact_multi_atlas_reconstruction() -> None:
    grid = np.zeros((7, 11), dtype=np.int16)
    grid[1:4, 2:6] = 3
    grid[5, 8:10] = 7
    state = ARCAtlasAnalyzer().analyze(grid)
    assert state.raw.size == 392
    assert state.macro.size == 48
    assert state.meso.size == 96
    assert state.micro.size == 192
    assert max(state.reconstruction_residuals.values()) < 1e-10
    assert set(state.feature_groups) == {
        "spatial",
        "color",
        "fourier",
        "haar",
        "polyphase2",
        "polyphase3",
        "polyphase4",
        "object",
    }


def test_task_signal_detects_recolor_route() -> None:
    x = np.zeros((6, 6), dtype=np.int16)
    x[1:4, 2:5] = 2
    y = x.copy()
    y[y == 2] = 7
    state = analyze_task_signal([(x, y)], ARCAtlasAnalyzer())
    assert state.primary_route == "recolor"
    assert state.atlas_probabilities["color"] > state.atlas_probabilities["fourier"]


def test_bayesian_posterior_prefers_exact_demonstration_fit() -> None:
    x = np.array([[0, 2], [0, 0]], dtype=np.int16)
    y = np.array([[0, 7], [0, 0]], dtype=np.int16)
    test = np.array([[2, 0], [0, 0]], dtype=np.int16)
    exact_candidate = entry.RuleCandidate(
        name="exact_recolor",
        grids=[np.array([[7, 0], [0, 0]], dtype=np.int16)],
        train_error=0,
        complexity=4,
        family="color_replace",
        train_grids=(y.copy(),),
    )
    approximate = entry.RuleCandidate(
        name="identity",
        grids=[test.copy()],
        train_error=1,
        complexity=1,
        family="learned_transform",
        train_grids=(x.copy(),),
    )
    model = BayesianProjectorResolvedLargeSignalModel(calibration=LASMCalibration.neutral())
    posterior = model.fit_posterior([approximate, exact_candidate], [(x, y)], [test])
    assert abs(sum(item.probability for item in posterior.candidate_posteriors) - 1.0) < 1e-10
    assert posterior.candidate_posteriors[0].name == "exact_recolor"
    attempts = model.select_attempts(posterior, 0)
    assert np.array_equal(attempts[0], exact_candidate.grids[0]) or np.array_equal(attempts[1], exact_candidate.grids[0])


def test_calibration_round_trip(tmp_path: Path) -> None:
    calibration = LASMCalibration(
        model_version="test",
        families=("family_a",),
        family_priors={"family_a": BetaPrior(3.0, 2.0), "__unknown__": BetaPrior(1.0, 4.0)},
        route_family_priors={"recolor": {"family_a": BetaPrior(5.0, 1.0)}},
        regression=None,
        training_metadata={"tasks": 10},
    )
    path = tmp_path / "model.json"
    path.write_text(json.dumps(calibration.to_json()), encoding="utf-8")
    restored = LASMCalibration.from_json(json.loads(path.read_text(encoding="utf-8")))
    assert restored.model_version == "test"
    assert restored.family_prior("family_a").mean == 0.6
    assert restored.route_prior("recolor", "family_a").mean == 5.0 / 6.0


def test_candidate_metrics_use_all_atlases() -> None:
    x = np.zeros((5, 5), dtype=np.int16)
    y = x.copy()
    y[2, 2] = 4
    candidate = entry.RuleCandidate(
        name="identity",
        grids=[x.copy()],
        train_error=1,
        complexity=1,
        family="learned_transform",
        train_grids=(x.copy(),),
    )
    metrics = candidate_metrics(candidate, [(x, y)], ARCAtlasAnalyzer())
    assert metrics.shape_match_rate == 1.0
    assert metrics.cell_match_rate == 24 / 25
    assert set(metrics.group_residuals) == {
        "spatial",
        "color",
        "fourier",
        "haar",
        "polyphase2",
        "polyphase3",
        "polyphase4",
        "object",
    }


def test_family_diverse_pruning_preserves_reusable_exact_programs() -> None:
    grid = np.zeros((2, 2), dtype=np.int16)
    candidates = []
    # Several exact residual predictions must not crowd out the reusable rule.
    for index in range(8):
        prediction = np.full((2, 2), index % 10, dtype=np.int16)
        candidates.append(
            entry.RuleCandidate(
                name=f"residual_{index}",
                grids=[prediction],
                train_error=0,
                complexity=20 + index,
                family="residual_input_polyphase",
                train_grids=(grid.copy(),),
            )
        )
    reusable = entry.RuleCandidate(
        name="simple_color_map",
        grids=[np.full((2, 2), 7, dtype=np.int16)],
        train_error=0,
        complexity=4,
        family="color_map",
        train_grids=(grid.copy(),),
    )
    selected = entry.prune_candidates_for_bayesian(candidates + [reusable], maximum=4)
    assert any(candidate.name == "simple_color_map" for candidate in selected)
    assert sum(candidate.family == "residual_input_polyphase" for candidate in selected) <= 2


def test_bayesian_ridge_retains_intercept() -> None:
    from komorebi_arc2.lasm_bayesian import BayesianRidge

    design = np.column_stack([np.ones(12), np.zeros(12)])
    targets = np.full(12, 2.0)
    fitted = BayesianRidge().fit(design, targets, ("bias", "unused"))
    mean, variance = fitted.predict(np.array([1.0, 0.0]))
    assert float(mean[0]) > 1.0
    assert float(variance[0]) > 0.0


def test_posterior_diagnostics_are_probability_complete() -> None:
    x = np.array([[0, 1], [0, 0]], dtype=np.int16)
    y = np.array([[0, 2], [0, 0]], dtype=np.int16)
    exact_candidate = entry.RuleCandidate(
        name="recolor",
        grids=[y.copy()],
        train_error=0,
        complexity=3,
        family="color_map",
        train_grids=(y.copy(),),
    )
    fallback = entry.RuleCandidate(
        name="identity",
        grids=[x.copy()],
        train_error=1,
        complexity=1,
        family="program",
        train_grids=(x.copy(),),
    )
    model = BayesianProjectorResolvedLargeSignalModel(calibration=LASMCalibration.neutral())
    posterior = model.fit_posterior([exact_candidate, fallback], [(x, y)], [x])
    diagnostics = posterior.diagnostics()
    assert abs(sum(diagnostics["posterior_family_probabilities"].values()) - 1.0) < 1e-10
    assert abs(sum(diagnostics["posterior_atlas_probabilities"].values()) - 1.0) < 1e-10
    assert abs(sum(diagnostics["posterior_resolution_probabilities"].values()) - 1.0) < 1e-10
    assert diagnostics["posterior_entropy"] >= 0.0
    assert 0.0 <= diagnostics["model_disagreement"] <= 1.0


def test_embedded_calibration_is_complete() -> None:
    from komorebi_arc2.lasm_bayesian import load_calibration

    calibration = load_calibration()
    assert calibration.model_version == "pr-lasm-arc2-bayesian-0.4.0"
    assert len(calibration.families) >= 20
    assert calibration.regression is not None
    assert calibration.regression.coefficient_mean.size == len(calibration.regression.feature_names)
    assert calibration.training_metadata["source_split"] == "ARC-AGI-2 public training only"
    assert calibration.training_metadata["calibration_task_count"] == 799
    assert calibration.training_metadata["locked_holdout_task_count"] == 201


def test_solve_task_emits_complete_bayesian_diagnostics() -> None:
    task, _ = entry.synthetic_task("recolor_largest", 8)
    diagnostics: dict[str, object] = {}
    predictions = entry.solve_task(task, time_limit=0.2, diagnostics=diagnostics)
    assert len(predictions) == len(task["test"])
    assert diagnostics["mode"] == "bayesian_pr_lasm"
    assert diagnostics["calibration_version"] == "pr-lasm-arc2-bayesian-0.4.0"
    assert diagnostics["candidate_count"] >= 1
    assert abs(sum(diagnostics["posterior_family_probabilities"].values()) - 1.0) < 1e-10
    assert abs(sum(diagnostics["posterior_atlas_probabilities"].values()) - 1.0) < 1e-10
    assert abs(sum(diagnostics["posterior_resolution_probabilities"].values()) - 1.0) < 1e-10
