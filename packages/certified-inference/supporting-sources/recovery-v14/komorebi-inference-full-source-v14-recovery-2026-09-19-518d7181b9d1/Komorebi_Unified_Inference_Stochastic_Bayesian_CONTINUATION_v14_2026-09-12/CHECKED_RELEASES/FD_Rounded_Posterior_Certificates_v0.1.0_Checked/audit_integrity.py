#!/usr/bin/env python3
"""Validate final source/compiled-output/dependency hashes and every axiom audit.

This checks recorded successful runs and their current outputs. It does not
replace running Lean, and it never promotes an incomplete or failed run.
"""
from pathlib import Path
import argparse,collections,datetime as dt,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--seal',action='store_true')
    a=ap.parse_args();rt=a.runtime.resolve();cache=rt/'workspace/.lake/build/lib/lean/Komorebi'
    mods=json.loads((ROOT/'MODULE_ORDER.json').read_text());decls=json.loads((ROOT/'DECLARATIONS.json').read_text())
    records=[];incomplete=[]
    for d in sorted((ROOT/'audit').glob('20*')):
        for s in d.glob('*.lean'):
            j=s.with_suffix('.json')
            if j.exists():
                r=json.loads(j.read_text());r['receipt_path']=str(j.relative_to(ROOT));records.append(r)
            else:incomplete.append(str(s.relative_to(ROOT)))
    final=[]
    for n in mods:
        source=ROOT/'Komorebi'/f'{n}.lean';h=sha(source)
        assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',source.read_text()),n
        rs=[r for r in records if r['module']==n and r['exit_status']==0 and r['source_sha256_before']==h and r['source_sha256_after']==h and r['staged_source_sha256']==h]
        assert rs,('No successful final-source receipt',n)
        r=rs[-1];assert sha(cache/f'{n}.olean')==r['output_sha256'],('Changed compiled output',n)
        log=ROOT/Path(r['receipt_path']).with_suffix('.log');assert sha(log)==r['log_sha256']
        for dep,dh in r['dependencies'].items():
            dn=dep.rsplit('.',1)[1]
            assert sha(ROOT/'Komorebi'/f'{dn}.lean')==dh['source_sha256'],(n,dep,'source')
            assert sha(cache/f'{dn}.olean')==dh['olean_sha256'],(n,dep,'compiled')
        final.append(r)
    ar=next(r for r in final if r['module']=='RoundedAxiomAudit')
    text=(ROOT/Path(ar['receipt_path']).with_suffix('.log')).read_text()
    parsed={name:[x.strip() for x in axioms.split(',') if x.strip()] for name,axioms in re.findall(r"'([^']+)' depends on axioms:\s*\[(.*?)\]",text,re.S)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",text):parsed[name]=[]
    assert set(parsed)=={d['name'] for d in decls},('Audit coverage mismatch',len(parsed),len(decls))
    allowed={'propext','Classical.choice','Quot.sound'}
    assert all(set(v)<=allowed for v in parsed.values()),'Unexpected axiom'
    details=[{**d,'axioms':parsed[d['name']],'source_sha256':sha(ROOT/'Komorebi'/f"{d['module']}.lean")} for d in decls]
    audit={'status':'PASS','covered':len(details),'allowed_axioms':sorted(allowed),'declarations':details,'audit_log_sha256':ar['log_sha256']}
    if a.seal:(ROOT/'AXIOM_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    inherited=json.loads((ROOT/'INHERITED_SOURCES.json').read_text())
    assert all(sha(ROOT/'Komorebi'/f'{n}.lean')==h['previous_sha256'] for n,h in inherited.items())
    try:commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    tests=json.loads((ROOT/'results/exact_rounding_tests.json').read_text())
    negatives=json.loads((ROOT/'results/NEGATIVE_CONTROLS.json').read_text())
    assert tests['status']=='PASS' and all(n['expected_rejection'] and n['exit_status']!=0 for n in negatives)
    result={'status':'PASS','sealed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_commit':commit,
      'scope':'Outward-rounded dyadic residual and packet-energy evaluation to actual Gaussian posterior tolerances',
      'environment':{'lean':ar['lean_version'],'mathlib':ar['mathlib_commit'],'warning_as_error':True,'threads':1},
      'active_modules':len(mods),'inherited_modules_freshly_rebuilt':len(inherited),'new_declarations':sum(d['group']=='new' for d in decls),
      'total_active_declarations':len(decls),'forbidden_active_tokens':0,'axiom_audit_covered':len(parsed),
      'successful_final_modules':final,'failed_completed_checks':[r for r in records if r['exit_status']!=0],
      'incomplete_attempt_source_snapshots':incomplete,'exact_diagnostics':tests,'negative_controls':negatives,
      'accumulated_final_compile_seconds':round(sum(r['elapsed_seconds'] for r in final),3),
      'verification_boundary':'This seal verifies receipts and current sources/compiled outputs; successful Lean processes are listed separately. The pinned Mathlib cache was reused.',
      'non_claims':['Not IEEE-754 hardware or bounded-integer arithmetic','Not uncertain model input semantics','No verified parser/exporter fidelity',
       'No general precision-search success or monotone-precision theorem','No rounded Richardson termination theorem',
       'No global performance, optimality, literature priority or full historical-program rebuild']}
    if a.seal:(ROOT/'FINAL_VERIFICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','active_modules','inherited_modules_freshly_rebuilt','new_declarations','total_active_declarations','axiom_audit_covered','accumulated_final_compile_seconds']},indent=2))
if __name__=='__main__':main()
