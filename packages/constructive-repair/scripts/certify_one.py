#!/usr/bin/env python3
"""Construct and kernel-check a rational repair from a fixed JSON input.

Requires the pinned offline Lean kit. This creates only a local working folder.
No data are published or uploaded. Python/source parsing is not claimed formally
verified; hashes and a Lean-decoded echo check the external input binding.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,json,sys,os,shutil,hashlib,time,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from repair_certificates import read_json,construct,check_certificate,canonical,digest,emit_input,emit_certificate

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('--kit',type=Path,default=os.environ.get('KOMOREBI_LEAN_KIT'));ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.kit is None:ap.error('Supply --kit or KOMOREBI_LEAN_KIT')
    kit=args.kit.resolve();out=args.output.resolve()
    if out.exists():ap.error('Output must be a new directory; existing evidence is never overwritten')
    out.mkdir(parents=True);logs=out/'logs';logs.mkdir();result={'status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),'commands':[]}
    def save(): (out/'result.json').write_text(json.dumps(result,indent=2)+'\n', encoding="utf-8")
    def run(name,cmd,cwd):
        t=time.monotonic()
        try:
            q=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=150, encoding="utf-8");rc=q.returncode;txt=q.stdout+q.stderr
        except subprocess.TimeoutExpired as e:
            rc=None;txt=str(e)
        (logs/(name+'.log')).write_text(txt, encoding="utf-8")
        result['commands'].append({'label':name,'command':cmd,'returncode':rc,'seconds':round(time.monotonic()-t,4),'log':'logs/'+name+'.log'});save()
        if rc!=0:raise RuntimeError(name+' failed; see log')
        print('PASS '+name,flush=True);return txt
    try:
        p=read_json(args.input);trace=[];c=construct(p,trace);check_certificate(p,c)
        (out/'input.json').write_bytes(canonical(p));(out/'certificate.json').write_bytes(canonical(c));(out/'trace.txt').write_text('\n'.join(trace)+'\n', encoding="utf-8")
        result['problem_sha256']=digest(p);result['minimum_added_dimension']=c['t'];save()
        lean=out/'lean';(lean/'KomorebiRepair').mkdir(parents=True)
        for name in ['RationalCertificates','ConstructiveMatrix','Wire']:
            shutil.copy2(ROOT/'lean/KomorebiRepair'/(name+'.lean'),lean/'KomorebiRepair'/(name+'.lean'))
        for name in ['lakefile.toml','lake-manifest.json','lean-toolchain']:shutil.copy2(ROOT/'lean'/name,lean/name)
        # This local project only needs the certificate modules and fixed input.
        (lean/'KomorebiRepair.lean').write_text('import KomorebiRepair.Wire\n', encoding="utf-8")
        (lean/'Input.lean').write_text(emit_input(p,'UserRepair'), encoding="utf-8")
        (lean/'Certificate.lean').write_text(emit_certificate(p,c,'UserRepair','Input'), encoding="utf-8")
        inputsha=hashlib.sha256((lean/'Input.lean').read_bytes()).hexdigest();result['input_source_sha256']=inputsha
        certsha=hashlib.sha256((lean/'Certificate.lean').read_bytes()).hexdigest();result['certificate_source_sha256']=certsha
        (lean/'Echo.lean').write_text('import Input\nopen KomorebiRepair.RationalCertificates\n#eval IO.println ("{\\"D\\":" ++ matrixJson UserRepair.D ++ ",\\"R\\":" ++ matrixJson UserRepair.R ++ "}")\n', encoding="utf-8")
        records=json.loads((ROOT/'docs/theorem_registry.json').read_text(encoding="utf-8"))['theorems']
        names=[r['name'] for r in records if r['module'] in {'RationalCertificates','ConstructiveMatrix','Wire'}]+['UserRepair.'+x for x in ['input_encoding_valid','certificate_encoding_valid','certificate_checked','original_equations_checked','output_matches_construction','optimal']]
        (lean/'Audit.lean').write_text('import Certificate\nset_option pp.fullNames true\n'+''.join('#print axioms '+n+'\n' for n in names), encoding="utf-8")
        run('attach',['bash',str(kit/'run.sh'),'attach',str(lean)],lean)
        version=run('version',['bash',str(kit/'run.sh'),'lean','--version'],lean)
        if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise RuntimeError('Wrong Lean runtime pin')
        revision=run('mathlib_pin',['git','-C',str(lean/'.lake/packages/mathlib'),'rev-parse','HEAD'],lean)
        if revision.strip()!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':raise RuntimeError('Wrong Mathlib pin')
        def lake(*xs):return ['bash',str(kit/'run.sh'),'lake','env',*xs]
        mods=['KomorebiRepair.RationalCertificates','KomorebiRepair.ConstructiveMatrix','KomorebiRepair.Wire','Input','Certificate']
        for mod in mods+['Audit']:
            rel=Path(mod.replace('.','/')+'.lean');obj=lean/'.lake/build/lib/lean'/rel.with_suffix('.olean');obj.parent.mkdir(parents=True,exist_ok=True)
            text=run('compile_'+mod.replace('.','_'),lake('lean','-j1','-DwarningAsError=true','-DmaxHeartbeats=3000000','-o',str(obj),str(rel)),lean)
            if mod=='Audit':
                axioms={n:[x.strip() for x in b.split(',') if x.strip()] for n,b in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",text,re.S)}
                for n in re.findall(r"'([^']+)' does not depend on any axioms",text):axioms[n]=[]
                if set(axioms)!=set(names):raise RuntimeError('Incomplete axiom audit')
                if any(set(a)-{'propext','Classical.choice','Quot.sound'} for a in axioms.values()):raise RuntimeError('Disallowed axiom')
                result['axioms']=axioms
        for mod in mods:
            text=run('replay_'+mod.replace('.','_'),lake('leanchecker','--verbose',mod),lean)
            if 'replaying '+mod not in text:raise RuntimeError('Replay evidence absent')
        echo=run('input_echo',lake('lean','Echo.lean'),lean);rows=[json.loads(x) for x in echo.splitlines() if x.startswith('{')]
        if len(rows)!=1 or rows[0]['D']!=p['D']['entries'] or rows[0]['R']!=p['R']['entries']:raise RuntimeError('Original input echo mismatch')
        if hashlib.sha256((lean/'Input.lean').read_bytes()).hexdigest()!=inputsha:raise RuntimeError('Input source changed during verification')
        if hashlib.sha256((lean/'Certificate.lean').read_bytes()).hexdigest()!=certsha:raise RuntimeError('Certificate source changed during verification')
        result.update(status='KERNEL_CHECKED_OPTIMAL_REPAIR',input_echo_matches=True,finished_utc=datetime.now(timezone.utc).isoformat());save();print('KERNEL_CHECKED_OPTIMAL_REPAIR t='+str(c['t']),flush=True);return 0
    except Exception as e:
        result.update(status='UNRESOLVED_VERIFICATION_FAILURE',error=str(e),finished_utc=datetime.now(timezone.utc).isoformat());save();print(result['status']+': '+str(e),flush=True);return 1
if __name__=='__main__':raise SystemExit(main())
