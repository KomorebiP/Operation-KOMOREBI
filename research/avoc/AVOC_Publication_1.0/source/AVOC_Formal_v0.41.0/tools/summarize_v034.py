#!/usr/bin/env python3
"""Validate v0.34 proof/runtime evidence and write the release audit summary."""
from __future__ import annotations
import datetime,hashlib,json,platform,re,sys,time,zipfile
from pathlib import Path
from summarize_v029 import check_record,strip_comments_strings
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.34.0';OD=RD/'operational'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'AVOC_Formal_v0.33.0.zip'
    order=load(RD/'build_order.json');assert len(order)==len(set(order))==188
    for f in order:
        check_record(load(RD/f'clean_{Path(f).stem}.json'),f,
            ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
    inv=load(RD/'declaration_inventory.json');expected={x['qualified_name'] for x in inv}
    assert len(inv)==len(expected)==1812
    check_record(load(RD/'full_axiom_audit.json'),'AVOC/FullAudit.lean')
    text=(RD/'full_axiom_audit.log').read_text()
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    assert len(names)==len(expected) and set(names)==expected
    deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):
        deps.update(x.strip() for x in block.split(',') if x.strip())
    assert deps <= {'propext','Classical.choice','Quot.sound'}
    audit=load(RD/'axiom_audit_summary.json');assert audit['passed'] and audit['audited']==audit['expected']==1812

    negatives=sorted((ROOT/'tests/negative').glob('*.lean'));assert len(negatives)==97
    for f in negatives:
        rec=load(RD/f'negative_{f.stem}.json');log=(ROOT/rec['log']).read_text()
        assert rec['returncode']!=0 and not rec['timed_out'] and 'error' in log,f
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
        assert rec['source_unchanged'] and rec['imports_unchanged']
        assert rec['source_before_sha256']==rec['source_sha256']==sha(f)
        assert rec['log_sha256']==sha(ROOT/rec['log'])

    same=0
    with zipfile.ZipFile(baseline) as z:
        assert z.testzip() is None
        prefix='AVOC_Formal_v0.33.0/'
        for name in z.namelist():
            rel=name.removeprefix(prefix)
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
                assert z.read(name)==(ROOT/rel).read_bytes(),rel;same+=1
    assert same==161,same

    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
    bad=[];census=[]
    for p in modules:
        source=strip_comments_strings(p.read_text())
        # Avoid matching the legitimate `.admit` action label by requiring tactic-like admit.
        hits=re.findall(r'\bsorry\b|\bnative_decide\b|^\s*axiom\s|^\s*unsafe\s+(?:theorem|lemma|def)|\bby\s+admit\b|^\s*admit\s*$',source,re.M)
        if hits:bad.append([p.name,hits])
        census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',source,re.M))
    assert not bad,bad
    assert len(census)==len(inv)

    bridge=load(OD/'bridge_regression.json');policy=load(OD/'policy_oracle.json')
    cold=load(OD/'cold_catalogue.json');warm=load(OD/'warm_catalogue.json')
    assert bridge['status']=='pass' and bridge['requests']==120 and bridge['input_vector_comparisons']==208
    assert bridge['counts']=={'norm':32,'cold':32,'warm':20,'probe':30,'invalid':6}
    assert policy['status']=='pass' and len(policy['cases'])==2
    assert cold['status']==warm['status']=='executed_checked_multi_level_policy'
    assert cold['planner_expected_net']=='391/2' and cold['fixed_cold_expected']=='257/2'
    assert cold['trace'][0]['choice']=={'kind':'probe','index':0} and cold['actual_decision_net']=='-1'
    assert warm['trace'][0]['choice']=={'kind':'reuse'} and warm['planner_expected_net']=='14867'
    assert warm['actual_decision_net']=='14867' and warm['fixed_cold_expected']=='14804'
    assert warm['fixed_warm_expected']=='14867'
    assert cold['catalogue_preparation_charge']==286 and warm['catalogue_preparation_charge']==658

    pins=load(RD/'dependency_pins.json');assert len(pins)==9 and all(x['passed'] for x in pins)
    counts=load(RD/'source_counts.json')
    assert counts['new_theorems']==60 and counts['total_theorems']==1812 and counts['non_audit_modules']==166
    summary=dict(passed=True,release='0.34.0',current_compilations=len(order),theorems=len(inv),
      new_theorems=60,axioms=sorted(deps),negative_rejections=len(negatives),
      inherited_unchanged=same,non_audit_modules=len(modules),non_audit_source_lines=counts['source_lines'],
      positive_source_scan_hits=bad,dependency_pins=9,terminal_requests=bridge['requests'],
      vector_comparisons=bridge['input_vector_comparisons'],controller_cases=2,
      cold_root_value=cold['planner_expected_net'],warm_root_value=warm['planner_expected_net'],
      baseline_sha256=sha(baseline),
      scope='Fresh local compilation and whole-corpus axiom/negative audit against pinned caches; proof-derived affine warm/cold terminal bridge and independent exact runtime oracle. Older live/cache/crash suites not rerun.')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',
          OD/'bridge_regression.json',OD/'policy_oracle.json',OD/'cold_catalogue.json',OD/'warm_catalogue.json']
    manifest={'schema_version':1,'claim_id':'AVOC-v034-proof-derived-terminal-operations',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v034.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current proof records plus exact affine terminal checker, proof-derived multi-level payoffs, and independent runtime regression. Universal statements are separate Lean theorems.',
        'coefficient_domain':'Generic finite rational control; field-valued algebraic proofs; runtime exact GF(5)',
        'conventions':'Uniform supplied catalogue; exact reports; warm/cold payoffs derived from checked deployments; catalogue preparation charged outside Bellman objective; faults are not reports',
        'inputs':['frozen v0.33 source ZIP','five new proof modules','actual Lean terminal and planner entrypoints','independent GF(5) affine and Fraction-DP oracles'],
        'bounds':{'local_targets':188,'theorems':1812,'negative_files':97,'terminal_requests':120,'input_vectors':208,'world_cap':32,'probe_cap':16,'horizon_cap':8,'seed':20260914},
        'non_claims':['No real workload calibration','No staged cache/generation actions','No persistent cache/recovery integration','No physical cost model','No arbitrary Lean backend','No LLM productivity claim']},
      'randomness':{'used':True,'generator':'random.Random exact finite-field adapter regression','seed':20260914},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current source/import/output/log hashes','exact theorem axiom inventory','substantive negative failures','byte-identical inherited proof modules','terminal batch oracle','independent exact controller dynamic programming'],
      'result':'PASS within stated theorem and bounded runtime scopes',
      'residual_risks':['trusted Lean/compiler/cache/host','tested Python/JSON adapter','supplied catalogue probabilities/fees/calls','precomputed all-world terminal alternatives','v1 computation metadata is not proof']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
