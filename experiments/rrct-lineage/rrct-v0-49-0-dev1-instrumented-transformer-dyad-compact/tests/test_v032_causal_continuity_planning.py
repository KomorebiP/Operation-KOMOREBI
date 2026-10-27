from rrct.causal_continuity_planning_experiment import (
    _baseline_certificate,
    _candidate_effect,
    _candidate_row,
    _fit_preview_map,
    _hidden_interface,
    _scenario_candidates,
)
import numpy as np


def test_preview_detects_route_not_snapshot_similarity():
    seed = 6051
    baseline = _baseline_certificate(seed)
    base_map = _fit_preview_map(seed, _hidden_interface(seed).sensory_effect, offset=17)
    base_norm = float(np.linalg.norm(baseline.discovery.source_projector @ base_map @ baseline.discovery.sensory_projector, ord="fro"))
    a, b = _scenario_candidates(seed, "copy_trap", 0)
    ra = _candidate_row(seed, "copy_trap", 0, 0, baseline, base_norm, a)
    rb = _candidate_row(seed, "copy_trap", 0, 1, baseline, base_norm, b)
    assert ra["snapshot_similarity"] < rb["snapshot_similarity"]
    assert ra["route_strength"] > 0.7
    assert rb["route_strength"] < 0.2
    assert ra["actual_external_value"] > rb["actual_external_value"]


def test_superior_replacement_is_not_blocked_by_identity():
    seed = 6057
    baseline = _baseline_certificate(seed)
    base_map = _fit_preview_map(seed, _hidden_interface(seed).sensory_effect, offset=17)
    base_norm = float(np.linalg.norm(baseline.discovery.source_projector @ base_map @ baseline.discovery.sensory_projector, ord="fro"))
    a, b = _scenario_candidates(seed, "superior_replacement", 0)
    ra = _candidate_row(seed, "superior_replacement", 0, 0, baseline, base_norm, a)
    rb = _candidate_row(seed, "superior_replacement", 0, 1, baseline, base_norm, b)
    assert rb["route_strength"] < 0.2
    assert rb["causal_predicted_value"] > ra["causal_predicted_value"]
    assert rb["actual_external_value"] > ra["actual_external_value"]
