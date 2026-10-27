#!/usr/bin/env python3
"""Fail-closed AVOC v0.38 evidence collector."""
from __future__ import annotations
from pathlib import Path
import datetime,hashlib,json,platform,re,sys,time
ROOT=Path(__file__).resolve().parents[1]; RD=ROOT/'results/v0.38.0'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def require(x,msg):
    if not x: raise AssertionError(msg)
def current_build(f):
    rec=load(RD/f'clean_{Path(f).stem}.json'); out=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
    require(rec['returncode']==0 and not rec['timed_out'],f'bad build {f}')
    require(rec.get('source_unchanged') and rec.get('imports_unchanged'),f'changed build input {f}')
    require(rec['source_sha256']==sha(ROOT/f),f'source hash {f}')
    require(out.is_file() and rec['output_sha256']==sha(out),f'output hash {f}')
    current={}
    for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(ROOT/f).read_text(),re.M):
        q=ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean')
        current[name]=sha(q) if q.is_file() else None
    require(rec.get('import_outputs')==current,f'import output hash {f}')

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); tick=time.monotonic()
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/AVOC_Formal_v0.37.0.zip')
    require(baseline.is_file(),'missing baseline')
    order=load(RD/'build_order.json'); require(len(order)==len(set(order))==205,'build target count')
    for f in order: current_build(f)
    build=load(RD/'local_build_summary.json'); require(build['targets']==build['current_successes']==205 and not build['bad'],'local build summary')
    inv=load(RD/'declaration_inventory.json'); names={x['qualified_name'] for x in inv}
    require(len(inv)==len(names)==2044,'declaration inventory')
    counts=load(RD/'source_counts.json'); require(counts['inherited_theorems']==1920 and counts['new_theorems']==124 and counts['total_theorems']==2044,'source counts')
    require(counts['non_audit_modules']==180 and counts['source_lines']==30271,'module/line counts')
    ax=load(RD/'axiom_audit_summary.json'); require(ax['passed'] and ax['reports']==ax['unique_reports']==ax['expected']==2044,'axiom reports')
    require(ax['axiom_union']==['Classical.choice','Quot.sound','propext'] and not ax['unexpected'],'axiom union')
    neg=load(RD/'negative_all/summary.json'); require(neg['total']==neg['substantive_rejections']==111,'negative suite')
    require(all(x['expected_rejection'] for x in neg['records']),'negative record')
    scan=load(RD/'source_scan.json'); require(scan['hits']==[],'source scan')
    inherited=load(RD/'inherited_module_comparison.json'); require(inherited['baseline_modules']==inherited['byte_identical']==174 and not inherited['changed'],'inherited modules')
    pins=load(RD/'dependency_pins.json'); require(len(pins)==9 and all(x['passed'] for x in pins),'dependency pins')
    reg=load(RD/'robust_quote_regression.json'); require(reg['lean_plan_comparisons']==21 and reg['compatible_realization_checks']==1523 and reg['result']=='all exact comparisons passed','robust regression')
    wf=load(RD/'robust_quote_workflow_regression.json'); require(wf['result']=='selected-only normal workflows passed','workflow')
    require(wf['warm_selected']['external_calls']=={'warm':1,'cold':0} and wf['cold_selected']['external_calls']=={'warm':0,'cold':1},'selected-only calls')
    rec=load(RD/'robust_quote_recovery_regression.json'); require(rec['result']=='commit-before-ack recovery passed without another external operation','recovery')
    require(rec['after_recovery']['external_calls']=={'warm':1,'cold':0} and rec['duplicate_resume']==rec['after_recovery'],'recovery calls/idempotence')
    lazy=load(RD/'lazy_staged_regression.json'); require(lazy['passed']==4,'lazy regression')
    verification=ROOT/'results/VERIFICATION_v0.38.0.md'; development=ROOT/'results/DEVELOPMENT_FAILURES_v0.38.0.md'
    for p in [verification,development,ROOT/'FORMAL_THEORY.md',ROOT/'PROOF_BOUNDARY.md',ROOT/'GAP_LEDGER.md',ROOT/'REPRODUCE.md',ROOT/'THEOREM_INDEX.md']:
        require(p.is_file() and p.stat().st_size>100,'missing doc '+str(p))
    summary={
      'version':'0.38.0','status':'PASS','toolchain':'Lean 4.34.0-rc2',
      'lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
      'mathlib':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
      'theorem_declarations':2044,'new_theorem_declarations':124,
      'non_audit_modules':180,'lean_source_lines':30271,'local_targets':205,
      'axiom_reports':2044,'axiom_union':ax['axiom_union'],'negative_rejections':111,
      'inherited_modules_byte_identical':174,'source_scan_hits':0,
      'robust_quote_plan_comparisons':21,'compatible_realization_checks':1523,
      'selected_only_workflows':2,'recovery_scenarios':1,'inherited_lazy_regression_cases':4,
      'baseline_sha256':sha(baseline),
      'evidence_sha256':{
        'axiom_audit':sha(RD/'axiom_audit_summary.json'),
        'negative_summary':sha(RD/'negative_all/summary.json'),
        'source_scan':sha(RD/'source_scan.json'),
        'build_summary':sha(RD/'local_build_summary.json'),
        'robust_regression':sha(RD/'robust_quote_regression.json'),
        'workflow_regression':sha(RD/'robust_quote_workflow_regression.json'),
        'recovery_regression':sha(RD/'robust_quote_recovery_regression.json'),
        'verification_record':sha(verification),
      },
      'collector_seconds':round(time.monotonic()-tick,3),
      'limitations':['probability bands supplied, not empirically calibrated','pinned external caches retained','Python/SQLite/OS tested, not universally refined','controlled process interruption is not power-loss certification','missing complete v0.36 source remains an explicit provenance boundary']
    }
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',RD/'negative_all/summary.json',RD/'source_scan.json',RD/'local_build_summary.json',RD/'robust_quote_regression.json',RD/'robust_quote_workflow_regression.json',RD/'robust_quote_recovery_regression.json']
    manifest={
      'schema_version':1,'claim_id':'AVOC-v038-certified-quote-robust-planning',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v038.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
      'mathematics':{
        'assertion_tested':'Current formal library plus authority-bound quote intervals, robust finite-horizon Q/value bounds, whole-policy regret, selected artifact refinement, and quote-bound recovery.',
        'coefficient_domain':'exact natural and rational control quantities; exact GF(5) affine artifacts',
        'conventions':'setup upper/gross lower/probability lower nominal model; full-L1 binary transition width; stable v0.37 action ordering; faults are not reports',
        'inputs':['authoritative v0.37 source ZIP','six new proof modules','actual Lean robust quote entrypoint','independent exact Fraction oracle','selected-only SQLite workflow'],
        'bounds':{'local_targets':205,'theorems':2044,'negative_files':111,'plan_comparisons':21,'compatible_realizations':1523,'workflow_cases':3},
        'non_claims':['No empirical calibration','No arbitrary Lean backend','No universal Python/SQLite refinement','No power-loss or hostile rollback guarantee','No complete physical cost model','No LLM productivity claim']},
      'randomness':{'used':True,'generator':'deterministic seeded exact interval-grid regression','seed':20260918},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current source/import/output hashes','exact theorem axiom inventory','substantive complete negative suite','byte-identical inherited modules','independent exact Fraction regression','selected-only workflow','commit-before-ack recovery'],
      'result':'PASS within stated theorem and bounded implementation scopes',
      'residual_risks':['trusted Lean/compiler/cache/host','tested Python/JSON/SQLite adapters','uncalibrated quote evidence','single protected local workflow']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
