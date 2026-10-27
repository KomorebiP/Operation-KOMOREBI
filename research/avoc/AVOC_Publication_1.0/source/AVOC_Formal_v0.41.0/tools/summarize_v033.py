#!/usr/bin/env python3
"""Validate v0.33 proof/runtime evidence and write the release audit summary."""
from __future__ import annotations
import datetime,hashlib,json,platform,re,sys,time,zipfile
from pathlib import Path
from summarize_v029 import check_record,strip_comments_strings
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.33.0'
TD=RD/'multi_level_tests'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def compact(x): return json.dumps(x,separators=(',',':'),ensure_ascii=False)

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'AVOC_Formal_v0.32.0.zip'
    order=load(RD/'build_order.json');assert len(order)==len(set(order))==182
    for f in order:
        check_record(load(RD/f'clean_{Path(f).stem}.json'),f,
            ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
    inv=load(RD/'declaration_inventory.json');expected={x['qualified_name'] for x in inv}
    assert len(inv)==len(expected)==1752
    check_record(load(RD/'full_axiom_audit.json'),'AVOC/FullAudit.lean')
    text=(RD/'full_axiom_audit.log').read_text()
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    assert len(names)==len(expected) and set(names)==expected
    deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):
        deps.update(x.strip() for x in block.split(',') if x.strip())
    assert deps <= {'propext','Classical.choice','Quot.sound'}
    audit=load(RD/'axiom_audit_summary.json')
    assert audit['passed'] and audit['audited']==audit['expected']==1752

    negatives=sorted((ROOT/'tests/negative').glob('*.lean'));assert len(negatives)==94
    for f in negatives:
        rec=load(RD/f'negative_{f.stem}.json');log=(ROOT/rec['log']).read_text()
        assert rec['returncode']!=0 and not rec['timed_out'] and 'error' in log,f
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
        assert rec['source_unchanged'] and rec['imports_unchanged']
        assert rec['source_before_sha256']==rec['source_sha256']==sha(f)
        assert rec['log_sha256']==sha(ROOT/rec['log'])
        for name,d in rec['import_outputs'].items():
            assert sha(ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean'))==d

    same=0
    with zipfile.ZipFile(baseline) as z:
        assert z.testzip() is None
        prefix='AVOC_Formal_v0.32.0/'
        for name in z.namelist():
            rel=name.removeprefix(prefix)
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
                assert z.read(name)==(ROOT/rel).read_bytes(),rel;same+=1
    assert same==156

    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
    bad=[];census=[]
    for p in modules:
        source=strip_comments_strings(p.read_text())
        hits=re.findall(r'\b(?:sorry|native_decide|axiom|unsafe)\b|\bby\s+admit\b|^\s*admit\s*$',source,re.M)
        if hits:bad.append([p.name,hits])
        census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',source,re.M))
    assert not bad,bad
    assert len(census)==len(inv)

    diff=load(TD/'differential_summary.json');live=load(TD/'live_summary.json')
    assert diff['passed'] and diff['valid_requests']==320 and diff['invalid_requests_rejected']==8
    assert live['passed'] and live['live_cases']==4
    requests=load(TD/'differential_requests.json');outputs=load(TD/'differential_outputs.json')
    invalid=load(TD/'invalid_outputs.json');runs=load(TD/'differential_invocations.json')
    assert len(requests)==len(outputs)==320 and len(invalid)==8 and len(runs)==5
    cursor=0
    for rec in runs[:4]:
        batch=requests[cursor:cursor+80]
        raw=(compact(batch)+'\n').encode()
        stdout=''.join(compact(x)+'\n' for x in outputs[cursor:cursor+80]).encode()
        assert rec['returncode']==0 and not rec['stderr']
        assert rec['request_sha256']==hashlib.sha256(raw).hexdigest()
        assert rec['stdout_sha256']==hashlib.sha256(stdout).hexdigest()
        cursor+=80
    assert cursor==320
    invalid_requests=[
        ['bad'],
        ['multi-level-affine-f5-v1',2,2,[],[],[],False,[],[],1,[]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',2,0]],[[1,1]],False,[[0,1]],[[0,1]],1,[]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',0,0]],[],False,[[0,1]],[[0,1]],1,[]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',0,0]],[[-1,1]],False,[[0,1]],[[0,1]],1,[]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',0,0]],[[1,1]],False,[[0,1]],[[0,1]],9,[]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',0,0]],[[1,1]],False,[[0,1]],[[0,1]],1,[[0,False]]],
        ['multi-level-affine-f5-v1',2,2,[[[1,0],[0,1]]],[['entry',0,0]],[[1,0]],False,[[0,1]],[[0,1]],1,[]],
    ]
    raw=(compact(invalid_requests)+'\n').encode();stdout=''.join(compact(x)+'\n' for x in invalid).encode()
    assert runs[4]['request_sha256']==hashlib.sha256(raw).hexdigest()
    assert runs[4]['stdout_sha256']==hashlib.sha256(stdout).hexdigest()

    live_runs=load(TD/'live_invocations.json')
    paths=sorted((ROOT/'examples/multi_level').glob('*.json'));assert len(paths)==len(live_runs)==4
    for path,rec in zip(paths,live_runs):
        req=json.loads(path.read_text())
        out=load(TD/f'live_{path.stem}.json');out.pop('wrapper_seconds',None)
        assert rec['returncode']==0 and not rec['stderr']
        assert rec['request_sha256']==hashlib.sha256((compact(req)+'\n').encode()).hexdigest()
        assert rec['stdout_sha256']==hashlib.sha256((compact(out)+'\n').encode()).hexdigest()

    for stage in ['differential','live']:
        rec=load(TD/f'{stage}_source_record.json')
        assert rec['unchanged'] and rec['input_source_before']==rec['input_source_after']
        for name,d in rec['input_source_after'].items():assert sha(ROOT/name)==d

    pins=load(RD/'dependency_pins.json');assert len(pins)==9 and all(x['passed'] for x in pins)
    counts=load(RD/'source_counts.json')
    assert counts['new_theorems']==60 and counts['total_theorems']==1752
    summary=dict(passed=True,release='0.33.0',current_compilations=len(order),theorems=len(inv),
      new_theorems=60,axioms=sorted(deps),negative_rejections=len(negatives),
      inherited_unchanged=same,non_audit_modules=len(modules),
      non_audit_source_lines=counts['source_lines'],positive_source_scan_hits=bad,
      dependency_pins=9,differential_requests=320,wire_rejections=8,live_cases=4,
      action_counts={k:diff[k] for k in ['probe_choices','reuse_choices','cold_choices','stop_choices']},
      baseline_sha256=sha(baseline),scope='Fresh local compilation and whole-corpus axiom/negative audit against pinned caches; new exact finite-catalogue multi-level controller regression. Older live/cache/crash suites not rerun.')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',
          TD/'differential_summary.json',TD/'live_summary.json']
    manifest={'schema_version':1,'claim_id':'AVOC-v033-multi-level-affine-information-control',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v033.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current proof records plus exact GF(5) multi-level codec/evaluator regression. Universal Bellman optimality and rank-floor safety are separate Lean theorems.',
        'coefficient_domain':'Generic finite rational control; field-valued algebraic proofs; runtime GF(5)',
        'conventions':'Uniform retained catalogue; exact entry/minor reports; positive reports raise floor; negative reports only filter catalogue; declared rational terminal payoffs; first action wins ties',
        'inputs':['frozen v0.32 source ZIP','five new Lean modules','actual Lean JSON entrypoint','independent GF(5) rank and exact Fraction-DP oracle'],
        'bounds':{'local_targets':182,'theorems':1752,'negative_files':94,'valid_wire_requests':320,'invalid_wire_requests':8,'world_cap':32,'probe_cap':16,'horizon_cap':8,'seed':20260914},
        'non_claims':['No real catalogue/payoff calibration','No negative-report rank upper bound','No actual cache/search execution','No efficient large-state planner','No physical speedup or LLM productivity','No fresh mathlib source build']},
      'randomness':{'used':True,'generator':'random.Random for bounded exact differential catalogues','seed':20260914},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current source/import/output/log hashes','exact theorem axiom inventory','substantive negative failures','byte-identical inherited proof modules','raw request/output hashes','independent exact dynamic-programming and GF(5) rank oracle'],
      'result':'PASS within stated theorem and bounded runtime scopes',
      'residual_risks':['trusted Lean/compiler/cache/host','tested Python/JSON adapter','supplied catalogue/fees/payoffs','exhaustive planner scaling','v1 computation metadata is not proof']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
