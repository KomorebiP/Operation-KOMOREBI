#!/usr/bin/env python3
"""Fresh isolated Std-only verification with all-theorem axiom audit.
No inherited Mathlib build, analytic theorem, or scalar gamma equality is implied.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,hashlib,json,re,shutil,os,time,platform
ROOT=Path(__file__).resolve().parents[1]
MODS=['H12ExplicitDescent','H12DescentPacket']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',type=Path,required=True);args=ap.parse_args();lean=args.lean.resolve()
    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    assert '4.34.0-rc2' in version
    assert len(MODS)==2
    build=ROOT/'.lean-check';logs=ROOT/'evidence/lean';logs.mkdir(parents=True,exist_ok=True)
    if build.exists():shutil.rmtree(build)
    build.mkdir();names=[];src={};records=[]
    for mod in MODS:
        p=ROOT/'formalization'/f'{mod}.lean';text=p.read_text()
        code=re.sub(r'/\-.*?\-/','',text,flags=re.S);code=re.sub(r'--[^\n]*','',code)
        assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',code)
        ns=re.search(r'^namespace (\S+)',text,re.M).group(1)
        names += [ns+'.'+x for x in re.findall(r'^theorem (\w+)',text,re.M)]
        src[p.name]=hashlib.sha256(p.read_bytes()).hexdigest();shutil.copy2(p,build/p.name)
    audit=''.join(f'import {m}\n' for m in MODS)+'\n'+''.join(f'#print axioms {n}\n' for n in names)
    (build/'Audit.lean').write_text(audit);(ROOT/'formalization/Audit.lean').write_text(audit)
    env=os.environ.copy();env['LEAN_PATH']=str(build)
    started=datetime.now(timezone.utc).isoformat();tic=time.monotonic()
    for mod in MODS+['Audit']:
        cmd=[str(lean),'-j1','-DwarningAsError=true','-o',mod+'.olean',mod+'.lean']
        tm=time.monotonic();p=subprocess.run(cmd,cwd=build,env=env,capture_output=True,text=True,timeout=90)
        text=p.stdout+p.stderr;(logs/f'{mod}.log').write_text(text)
        records.append({'module':mod,'argv':cmd,'returncode':p.returncode,'seconds':time.monotonic()-tm})
        print(mod,p.returncode,round(records[-1]['seconds'],3),flush=True)
        if p.returncode:raise RuntimeError(text)
    text=(logs/'Audit.log').read_text()
    found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",text)+[(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",text)]
    assert set(names)=={n for n,_ in found}
    for n,deps in found:assert {d.strip() for d in deps.split(',') if d.strip()} <= {'propext','Classical.choice','Quot.sound'},n
    (build/'FalseControl.lean').write_text('import Std\nexample : (0 : Int)=1 := by decide\n')
    p=subprocess.run([str(lean),'-j1','-DwarningAsError=true','FalseControl.lean'],cwd=build,env=env,capture_output=True,text=True,timeout=20)
    text=p.stdout+p.stderr;(logs/'FalseControl.log').write_text(text)
    assert p.returncode!=0 and 'error' in text
    result={'started_at':started,'runtime_seconds':time.monotonic()-tic,'exit_status':0,'theorem_count':len(names),'theorems':names,'axioms':dict(found),'source_hashes':src,'lean_version':version,'lean_binary_sha256':hashlib.sha256(lean.read_bytes()).hexdigest(),'dependencies':'Bundled Std only. No Mathlib is imported.','compiled_modules':records,'negative_control_exit':p.returncode,'scope':'New explicit integer cocycle, cochain, Hodge-coordinate, projective-matrix and common-invariance certificates. No formal holomorphic gerbes, actual gamma descent, or inherited full replay.'}
    (ROOT/'evidence/lean_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(names),'theorems; complete dependency audit; false control rejected')
if __name__=='__main__':main()
