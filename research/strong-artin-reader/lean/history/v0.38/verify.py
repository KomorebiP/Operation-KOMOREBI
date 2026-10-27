#!/usr/bin/env python3
"""Fresh replay of the seven new source modules, using the pinned Mathlib cache.
The preserved v0.37 archive is hash authenticated, not freshly replayed here.
"""
import argparse,hashlib,json,os,re,shutil,subprocess,time,zipfile
from pathlib import Path
from datetime import datetime,timezone

MODULES=['NCPowerEstimates','NCPowerLocalImage','PadicMatrixNorm','MatrixInverseCertificate','EffectiveMatrixRoot','FiniteMatrixCriterion','EffectiveMatrixControls']
LEAN='6a10ac8c22beadecabdbb0919c2b50214762f91d'
MATHLIB='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
PARENT='Strong_Artin_Lean_v0.37.0_Effective_Resonant_Scalar_Horizon_Checked.zip'
PARENT_SHA='71eb1f38502ce089e9a5ae58bea8fc831f875d6bd83144fe0f4663328e77c689'
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit',type=Path,required=True)
    ap.add_argument('--label',default='fresh')
    args=ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.label):raise ValueError('Invalid replay label')
    root=Path(__file__).resolve().parent;kit=args.kit.resolve();ws=kit/'workspace'
    env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so')
    lean=kit/'toolchain/bin/lean'
    version=subprocess.check_output([str(lean),'--version'],env=env,text=True).strip()
    assert '4.34.0-rc2' in version and LEAN in version,version
    rev=subprocess.check_output(['git','-C',str(ws/'.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    assert rev==MATHLIB,rev
    parent=root/'base'/PARENT
    assert sha(parent)==PARENT_SHA,'Parent SHA mismatch'
    with zipfile.ZipFile(parent) as z:
        assert z.testzip() is None,'Corrupt parent ZIP'
    out=root/'verification'/args.label
    if out.exists():shutil.rmtree(out)
    for d in ['src','olean','logs']:(out/d).mkdir(parents=True)
    decls=[];hashes={}
    for m in MODULES:
        p=root/'src'/f'{m}.lean';raw=p.read_text()
        # This new-source convention has no strings or nested comments.
        code=re.sub(r'/\-.*?\-/','',raw,flags=re.S)
        code=re.sub(r'--[^\n]*','',code)
        forbidden=re.findall(r'\b(sorry|admit|axiom|opaque|native_decide|unsafe)\b',code)
        assert not forbidden,(m,forbidden)
        prefix='Komorebi.StrongArtin.MatrixHensel'+('.Controls' if m.endswith('Controls') else '')
        for kind,name in re.findall(r'(?m)^(theorem|def|abbrev)\s+(\w+)',code):
            decls.append(dict(module=m,kind=kind,name=prefix+'.'+name))
        hashes[m]=sha(p)
        shutil.copy2(p,out/'src'/p.name)
    audit='\n'.join('import '+m for m in MODULES)+'\n\n'+'\n'.join('#print axioms '+d['name'] for d in decls)+'\n'
    (root/'audit/AxiomAudit.lean').write_text(audit)
    (root/'DECLARATIONS.json').write_text(json.dumps(decls,indent=2)+'\n')
    (out/'src/AxiomAudit.lean').write_text(audit)
    lp=subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=ws,text=True).strip()
    # Keep package caches, omit the unrelated project build directory.
    paths=[s for s in lp.split(':') if '/.lake/packages/' in s]
    env['LEAN_PATH']=str(out/'olean')+':'+':'.join(paths)
    report=dict(status='IN_PROGRESS',started_utc=datetime.now(timezone.utc).isoformat(),
        lean=version,mathlib=rev,parent_sha256=PARENT_SHA,parent_freshly_replayed=False,
        scope='Seven new modules and all their new-source dependencies; pinned Mathlib cache reused',
        declarations=decls,source_hashes=hashes,module_results=[],axioms=[])
    dest=out/'RESULT.json'
    for m in MODULES+['AxiomAudit']:
        source=out/'src'/f'{m}.lean';obj=out/'olean'/f'{m}.olean'
        cmd=[str(lean),'-j1','-DwarningAsError=true','-R',str(out/'src'),'-o',str(obj),str(source)]
        start=time.monotonic()
        proc=subprocess.run(cmd,cwd=ws,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        log=out/'logs'/f'{m}.log';log.write_text(proc.stdout)
        rec=dict(module=m,command=cmd,returncode=proc.returncode,seconds=time.monotonic()-start,
                 source_sha256=sha(source),log_sha256=sha(log),object_sha256=sha(obj) if obj.exists() else None)
        report['module_results'].append(rec)
        dest.write_text(json.dumps(report,indent=2)+'\n')
        print(m,proc.returncode,flush=True)
        if proc.returncode or 'sorryAx' in proc.stdout:
            report['status']='FAIL';dest.write_text(json.dumps(report,indent=2)+'\n')
            raise RuntimeError(proc.stdout)
    text=(out/'logs/AxiomAudit.log').read_text()
    reports=re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",text,re.S)
    empty=re.findall(r"'([^']+)' does not depend on any axioms",text)
    named={n for n,_ in reports}|set(empty)
    assert named=={d['name'] for d in decls},'Incomplete axiom audit'
    axioms={a.strip() for _,chunk in reports for a in chunk.split(',') if a.strip()}
    assert axioms<=ALLOWED,axioms
    assert all(sha(root/'src'/f'{m}.lean')==h for m,h in hashes.items()),'Sources changed during replay'
    report.update(status='PASS',axioms=sorted(axioms),finished_utc=datetime.now(timezone.utc).isoformat(),
                  source_lines=sum(len((root/'src'/f'{m}.lean').read_text().splitlines()) for m in MODULES))
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(MODULES),'modules;',len(decls),'named declarations')

if __name__=='__main__':main()
