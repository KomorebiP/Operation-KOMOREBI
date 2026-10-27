from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
analysis=json.loads((ROOT/'results/EDGE_ANALYSIS.json').read_text())
mechanism=json.loads((ROOT/'results/EDGE_MECHANISM_ANALYSIS.json').read_text())
replay=json.loads((ROOT/'results/REPRESENTATIVE_REPLAY.json').read_text())
checks={
 'primary_14_of_14': analysis['endpoints_passed']==14 and analysis['endpoint_count']==14 and analysis['all_endpoints_met'],
 'extension_4_of_4': mechanism['overcomplete_extension_passed']==4 and mechanism['overcomplete_extension_total']==4,
 'trajectory_count_248': mechanism['trajectory_counts']['total']==248,
 'rank_warning_auc': mechanism['two_stage_transition']['rank_precursor']['auc']>=0.80,
 'representative_replay': replay['all_passed'],
 'primary_files': len(list((ROOT/'results/primary').glob('*.json')))==132,
 'crossed_files': len(list((ROOT/'results/crossed').glob('*.json')))==32,
 'tail_files': len(list((ROOT/'results/posthoc_d2_tail').glob('*.json')))==24,
 'overcomplete_files': len(list((ROOT/'results/overcomplete').glob('*.json')))==60,
}
out={'schema':'rrct.v055.release_scientific_verification.v1','status':'V055_RELEASE_SCIENTIFIC_EVIDENCE_VERIFIED' if all(checks.values()) else 'V055_RELEASE_VERIFICATION_FAILED','all_checks_pass':all(checks.values()),'checks':checks,'edge_analysis_sha256':hashlib.sha256((ROOT/'results/EDGE_ANALYSIS.json').read_bytes()).hexdigest(),'mechanism_analysis_sha256':hashlib.sha256((ROOT/'results/EDGE_MECHANISM_ANALYSIS.json').read_bytes()).hexdigest()}
print(json.dumps(out,indent=2,sort_keys=True));raise SystemExit(0 if all(checks.values()) else 1)
