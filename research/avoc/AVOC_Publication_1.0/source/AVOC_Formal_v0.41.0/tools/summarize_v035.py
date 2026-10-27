#!/usr/bin/env python3
"""Validate v0.35 proof/runtime evidence and write the release audit summary."""
from __future__ import annotations
import datetime,hashlib,json,platform,re,sys,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.35.0';SD=RD/'staged_affine'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def check_record(r,source,out=None):
    p=ROOT/source
    assert r['returncode']==0 and not r['timed_out'] and r.get('source_unchanged') and r.get('imports_unchanged'),source
    assert r['source_sha256']==sha(p),source
    assert r['log_sha256']==sha(ROOT/r['log']),source
    if out is not None:assert Path(out).is_file() and r['output_sha256']==sha(out),source
    current={}
    for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',p.read_text(),re.M):
        q=ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean')
        current[name]=sha(q) if q.is_file() else None
    assert r.get('import_outputs')==current,source

def strip(text):
    text=re.sub(r'/\*.*?\*/','',text,flags=re.S);text=re.sub(r'--.*','',text)
    return text

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/AVOC_Formal_v0.34.0.zip')
    order=load(RD/'build_order.json');assert len(order)==len(set(order))==193
    for f in order:check_record(load(RD/f'clean_{Path(f).stem}.json'),f,ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
    inv=load(RD/'declaration_inventory.json');expected={x['qualified_name'] for x in inv};assert len(inv)==len(expected)==1860
    check_record(load(RD/'full_axiom_audit.json'),'AVOC/FullAudit.lean')
    text=(RD/'full_axiom_audit.log').read_text();names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    assert len(names)==len(expected) and set(names)==expected
    deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):deps.update(x.strip() for x in block.split(',') if x.strip())
    assert deps <= {'propext','Classical.choice','Quot.sound'}
    audit=load(RD/'axiom_audit_summary.json');assert audit['passed'] and audit['audited']==audit['expected']==1860
    neg=sorted((ROOT/'tests/negative').glob('*.lean'));assert len(neg)==100
    for f in neg:
        r=load(RD/f'negative_{f.stem}.json');log=(ROOT/r['log']).read_text()
        assert r['returncode']!=0 and not r['timed_out'] and 'error' in log,f
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
        assert r['source_unchanged'] and r['imports_unchanged'] and r['source_sha256']==sha(f)
    same=0
    with zipfile.ZipFile(baseline) as z:
        assert z.testzip() is None;prefix='AVOC_Formal_v0.34.0/'
        for name in z.namelist():
            rel=name.removeprefix(prefix)
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
                assert z.read(name)==(ROOT/rel).read_bytes(),rel;same+=1
    assert same==166,same
    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
    bad=[];census=[]
    for p in modules:
        s=strip(p.read_text())
        hits=re.findall(r'\bsorry\b|\bnative_decide\b|^\s*axiom\s|^\s*unsafe\s+(?:theorem|lemma|def)|\bby\s+admit\b|^\s*admit\s*$',s,re.M)
        if hits:bad.append([p.name,hits])
        census += re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',s,re.M)
    assert not bad,bad;assert len(census)==len(inv)
    regression=load(SD/'regression.json');assert regression['status']=='pass' and regression['valid_cases']==96 and regression['invalid_cases']==8
    assert regression['headline']['certain']['choice']=='inspect_warm' and regression['headline']['certain']['value']=='14867'
    assert regression['headline']['risky_warm']['choice']=='generate_cold' and regression['headline']['risky_warm']['value']=='14804'
    assert regression['headline']['one_step']['choice']=='stop'
    assert regression['headline']['after_warm_success']['choice']=='deploy_warm' and regression['headline']['after_warm_success']['value']=='15000'
    for name in ['certain','risky_warm','one_step','after_warm_success','insufficient_budget','warm_failure']:
        out=load(SD/f'{name}.json');assert out['status']=='optimal_staged_affine_policy'
    pins=load(RD/'dependency_pins.json');assert len(pins)==9 and all(x['passed'] for x in pins)
    counts=load(RD/'source_counts.json');assert counts['new_theorems']==48 and counts['total_theorems']==1860 and counts['non_audit_modules']==170
    summary=dict(passed=True,release='0.35.0',current_compilations=len(order),theorems=len(inv),new_theorems=48,
      axioms=sorted(deps),negative_rejections=len(neg),inherited_unchanged=same,non_audit_modules=len(modules),
      non_audit_source_lines=counts['source_lines'],positive_source_scan_hits=bad,dependency_pins=9,
      staged_valid_cases=regression['valid_cases'],staged_invalid_cases=regression['invalid_cases'],
      headline=regression['headline'],baseline_sha256=sha(baseline),
      scope='Fresh local compilation and whole-corpus axiom/negative audit against pinned caches; exact staged affine Bellman model and independent Fraction-DP executable regression. Physical candidate validation remains eager model construction.')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',SD/'regression.json']+[SD/f'{n}.json' for n in ['certain','risky_warm','one_step','after_warm_success','insufficient_budget','warm_failure']]
    manifest={'schema_version':1,'claim_id':'AVOC-v035-staged-affine-control','repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v035.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current proof records plus proof-carrying staged cache/generation controller and independent exact dynamic-programming regression.',
        'coefficient_domain':'finite-horizon rational control; runtime exact GF(5) affine deployments',
        'conventions':'setup actions paid before deployment; Boolean declared success; faults are not reports; common natural budget envelope; stable action tie order',
        'inputs':['frozen v0.34 source ZIP','four new proof modules','actual Lean staged entrypoint','independent Fraction-DP oracle'],
        'bounds':{'local_targets':193,'theorems':1860,'negative_files':100,'valid_requests':96,'invalid_requests':8,'horizon_cap':8,'seed':20260915},
        'non_claims':['No lazy physical validation','No calibrated success probabilities','No persistent recovery integration','No complete physical cost model','No arbitrary Lean backend','No LLM productivity claim']},
      'randomness':{'used':True,'generator':'random.Random exact request sampler','seed':20260915},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current source/import/output/log hashes','exact theorem axiom inventory','substantive negative failures','byte-identical inherited proof modules','actual Lean staged runtime','independent exact Fraction dynamic programming'],
      'result':'PASS within stated theorem and bounded runtime scopes',
      'residual_risks':['trusted Lean/compiler/cache/host','tested Python/JSON adapter','supplied success probabilities and tariffs','eager physical certificate validation','v1 computation metadata is not proof']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
