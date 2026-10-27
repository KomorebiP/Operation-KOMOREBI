import json
from pathlib import Path
import pytest
from nested_workspace_pilot import Config, analyze, information_receipt, state_dict_sha256, train

ROOT = Path(__file__).resolve().parents[1]

def test_exact_nested_synergy():
    i = information_receipt()
    assert i["I_U_A1"] == pytest.approx(0.0); assert i["I_U_A2"] == pytest.approx(0.0); assert i["I_U_A1A2"] == pytest.approx(2.0)
    assert i["I_V_B1"] == pytest.approx(0.0); assert i["I_V_B2"] == pytest.approx(0.0); assert i["I_V_B1B2"] == pytest.approx(2.0)
    assert i["I_Y_U"] == pytest.approx(0.0); assert i["I_Y_V"] == pytest.approx(0.0); assert i["I_Y_UV"] == pytest.approx(2.0)

def test_dimensions_compress_at_both_levels():
    c = Config(); assert c.local_dim < 2 * c.leaf_dim; assert c.global_dim < 2 * c.local_dim

def test_training_is_deterministic():
    a, af, ar = train(520531); b, bf, br = train(520531)
    assert state_dict_sha256(a) == state_dict_sha256(b); assert state_dict_sha256(af) == state_dict_sha256(bf); assert ar["digest"] == br["digest"]

def test_development_seed_passes():
    r = analyze(52011); assert r["all_endpoints_met"]; assert len(r["endpoints"]) == 18
    assert r["modes"]["global_cut"]["local_a"] == 1.0; assert r["modes"]["global_cut"]["local_b"] == 1.0; assert r["modes"]["global_cut"]["global"] == 0.25
    assert r["modes"]["topdown_cut"]["global"] == 1.0; assert r["modes"]["topdown_cut"]["mean_action"] == 0.25

def test_holdout_if_present():
    path = ROOT / "results" / "summary.json"
    if not path.is_file(): pytest.skip("holdout not run")
    s = json.loads(path.read_text()); assert s["all_endpoints_met"]; assert len(s["endpoints"]) == 18
