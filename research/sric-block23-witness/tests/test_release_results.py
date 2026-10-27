import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_frozen_results_are_consistent():
 seal=json.loads((ROOT/'frozen/preaudit_seal.json').read_text());res=json.loads((ROOT/'results/block23_final.json').read_text())
 assert res['summary']['all_correct'];assert res['summary']['certificate_accuracy']==1.0;assert res['summary']['preaudit_seal']==seal['preaudit_seal'];assert res['summary']['counterfactual_patch']['minimum_selected_future_r2']>.90;assert not res['summary']['answer_shortcut_control']['any_passed']
