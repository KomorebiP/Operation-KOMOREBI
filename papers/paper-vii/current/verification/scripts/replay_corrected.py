#!/usr/bin/env python3
"""Replay the isolated two-endpoint corrected strengthened verifier."""
from __future__ import annotations
import argparse,difflib,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,r):p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--corrected',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();source=a.source.resolve();corrected=a.corrected.resolve();out=a.out.resolve()
    if out==source or source in out.parents:raise ValueError('Output must be outside protected source')
    out.mkdir(parents=True,exist_ok=True)
    raw=source/'strengthened/PSC_Paper_VII_Strengthened_Annals_Edition_Final'
    rpath=raw/'verification/verify_paper_vii.py';rtxt=rpath.read_text();ctxt=corrected.read_text()
    assert rtxt.count('np.arange(-N//2,')==2 and ctxt==rtxt.replace('np.arange(-N//2,','np.arange(-(N//2),')
    before={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
    import numpy as np
    representatives=[]
    for n in range(4,33):
        reps=np.arange(-(n//2),n-n//2)
        checks={'count':len(reps)==n,'unique_residue_classes':len(set(int(k)%n for k in reps))==n,
                'bound':bool(np.all(np.abs(reps)<=n/2))}
        assert all(checks.values()),(n,reps,checks)
        representatives.append({'N':n,'reps':[int(k) for k in reps],'checks':checks})
    write(out/'representative_assertions.json',{'integers_tested':29,'assertions':87,'status':'passed','records':representatives})
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    with tempfile.TemporaryDirectory(prefix='paper_vii_corrected_') as td:
        work=Path(td)/'strengthened';shutil.copytree(raw,work)
        shutil.copy2(corrected,work/'verification/verify_paper_vii.py')
        argv=[sys.executable,'verification/verify_paper_vii.py']
        with (out/'corrected_suite.log').open('w') as h:
            proc=subprocess.run(argv,cwd=work,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=240)
        assert proc.returncode==0,proc.returncode
        fresh=json.loads((work/'verification/verification_results.json').read_text())
    inherited=json.loads((raw/'verification/verification_results.json').read_text())
    assert fresh['status']=='passed'
    after={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
    assert before==after
    write(out/'corrected_numerical_results.json',fresh)
    diff=''.join(difflib.unified_diff(rtxt.splitlines(keepends=True),ctxt.splitlines(keepends=True),fromfile='preserved_raw',tofile='corrected_edition'))
    (out/'exact_source_diff.patch').write_text(diff)
    results={'scope':'Separate corrected edition finite bookkeeping replay; no raw-source edit, Lean invocation or universal claim',
        'correction':{'raw_sha256':sha(rpath),'corrected_sha256':sha(corrected),'occurrences_changed':2,
            'only_change':'-N//2 -> -(N//2) at both lower endpoints'},
        'command':argv,'source_files_preserved':len(after),'source_bytes_preserved':before==after,
        'representative_assertions':87,'N_min':4,'N_max':32,'fresh_corrected':fresh,
        'inherited_raw_check_count':inherited['total_checks'],
        'raw_fresh_check_count_reference':18049,
        'count_change':fresh['total_checks']-inherited['total_checks'],
        'nonclaims':['Does not change or certify the preserved raw verifier.',
            'Does not establish a continuum limit or universal theorem.'],
        'artifact_hashes':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name not in ('manifest.json','stdout.txt','stderr.txt','results.json')}}
    write(out/'results.json',results)
    print(json.dumps({'corrected_checks':fresh['total_checks'],'groups':len(fresh['groups']),
        'representative_assertions':87,'count_change':results['count_change'],'source_bytes_preserved':True},indent=2))

if __name__=='__main__':main()
