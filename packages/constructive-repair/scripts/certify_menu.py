#!/usr/bin/env python3
"""Construct and kernel-check a costed rational-menu result in a new local folder.

Supports an optimal admissible menu or a proof of no admissible repair.
Rejected data and timeouts return UNRESOLVED. Requires the pinned offline kit.
No file is published and no service is contacted by this command.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,json,sys,os,shutil,hashlib,time,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from repair_certificates import read_json,canonical,digest
import rational_menu as M
PIN='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
MODULES=['RationalCertificates','ConstructiveMatrix','Wire','RationalMenuCover']

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--certificate',type=Path)
    ap.add_argument('--kit',type=Path,default=os.environ.get('KOMOREBI_LEAN_KIT'))
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--max-trials',type=int,default=256)
    args=ap.parse_args()
    if args.kit is None:ap.error('Supply --kit or KOMOREBI_LEAN_KIT')
    kit=args.kit.resolve();out=args.output.resolve()
    if out.exists():ap.error('Output must be a new directory; existing evidence is not overwritten')
    out.mkdir(parents=True);logs=out/'logs';logs.mkdir()
    result={'schema':'komorebi.repair.menu-verification.v0.4.0','status':'RUNNING',
            'started_utc':datetime.now(timezone.utc).isoformat(),'commands':[]}
    def save():(out/'result.json').write_text(json.dumps(result,indent=2)+'\n', encoding="utf-8")
    def run(name,cmd,cwd,timeout=180):
        t=time.monotonic();expired=False
        try:
            p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=timeout, encoding="utf-8");rc=p.returncode;txt=p.stdout+p.stderr
        except subprocess.TimeoutExpired as e:
            rc=None;expired=True
            def text(x):return x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
            txt=text(e.stdout)+text(e.stderr)
        (logs/(name+'.log')).write_text(txt, encoding="utf-8")
        result['commands'].append({'label':name,'command':cmd,'cwd':str(cwd),'returncode':rc,'timed_out':expired,
                                  'seconds':round(time.monotonic()-t,4),'log':'logs/'+name+'.log'});save()
        if rc!=0:raise RuntimeError(name+' failed; inspect retained log')
        print('PASS '+name,flush=True);return txt
    save()
    try:
        p=read_json(args.input);M.parse_problem(p);trace=[]
        c=read_json(args.certificate) if args.certificate else M.construct(p,trace,max_trials=args.max_trials)
        checked=M.check_certificate(p,c)
        result.update(certificate_kind=c['kind'],problem_sha256=digest(p),python_check=checked,
                      selected_mask=c.get('selection'),minimum_cost=c.get('cost'))
        if checked['admissible_menus']==0:result['scope_note']='No subset is admitted by the fixed input table; rejection is vacuous.'
        (out/'input.json').write_bytes(canonical(p));(out/'certificate.json').write_bytes(canonical(c))
        (out/'trace.txt').write_text('\n'.join(trace)+'\n', encoding="utf-8")
        lean=out/'lean';(lean/'KomorebiRepair').mkdir(parents=True)
        for mod in MODULES:shutil.copy2(ROOT/'lean/KomorebiRepair'/(mod+'.lean'),lean/'KomorebiRepair'/(mod+'.lean'))
        for f in ['lakefile.toml','lake-manifest.json','lean-toolchain']:shutil.copy2(ROOT/'lean'/f,lean/f)
        (lean/'KomorebiRepair.lean').write_text('import KomorebiRepair.RationalMenuCover\n', encoding="utf-8")
        (lean/'Input.lean').write_text(M.emit_input(p,'UserMenu'), encoding="utf-8")
        (lean/'Certificate.lean').write_text(M.emit_certificate(p,c,'UserMenu','Input'), encoding="utf-8")
        (lean/'Echo.lean').write_text(M.emit_echo(p,'UserMenu','Input'), encoding="utf-8")
        input_hash=hashlib.sha256((lean/'Input.lean').read_bytes()).hexdigest()
        cert_hash=hashlib.sha256((lean/'Certificate.lean').read_bytes()).hexdigest()
        result.update(input_source_sha256=input_hash,certificate_source_sha256=cert_hash)
        # Extract exact top-level theorem names in the fixed namespace.
        names=[]
        for mod in MODULES:
            names += ['KomorebiRepair.RationalCertificates.'+x for x in
                      re.findall(r'^theorem\s+(\w+)',(lean/'KomorebiRepair'/(mod+'.lean')).read_text(encoding="utf-8"),re.M)]
        for f in ['Input.lean','Certificate.lean']:
            names += ['UserMenu.'+x for x in re.findall(r'^theorem\s+(\w+)',(lean/f).read_text(encoding="utf-8"),re.M)]
        (lean/'Audit.lean').write_text('import Certificate\nset_option pp.fullNames true\n'+''.join('#print axioms '+x+'\n' for x in names), encoding="utf-8")
        run('attach',['bash',str(kit/'run.sh'),'attach',str(lean)],lean)
        ver=run('version',['bash',str(kit/'run.sh'),'lean','--version'],lean)
        if '4.34.0-rc2' not in ver or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in ver:raise RuntimeError('Wrong Lean runtime')
        rev=run('mathlib_pin',['git','-C',str(lean/'.lake/packages/mathlib'),'rev-parse','HEAD'],lean)
        if rev.strip()!=PIN:raise RuntimeError('Wrong Mathlib pin')
        def lake(*x):return ['bash',str(kit/'run.sh'),'lake','env',*x]
        mods=['KomorebiRepair.'+m for m in MODULES]+['Input','Certificate']
        for mod in mods+['Audit']:
            rel=Path(mod.replace('.','/')+'.lean');obj=lean/'.lake/build/lib/lean'/rel.with_suffix('.olean');obj.parent.mkdir(parents=True,exist_ok=True)
            txt=run('compile_'+mod.replace('.','_'),lake('lean','-j1','-DwarningAsError=true','-DmaxHeartbeats=5000000','-o',str(obj),str(rel)),lean)
            if mod=='Audit':
                ax={n:[x.strip() for x in body.split(',') if x.strip()] for n,body in
                    re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",txt,re.S)}
                for n in re.findall(r"'([^']+)' does not depend on any axioms",txt):ax[n]=[]
                if set(ax)!=set(names):raise RuntimeError('Incomplete axiom coverage')
                if any(set(a)-{'propext','Classical.choice','Quot.sound'} for a in ax.values()):raise RuntimeError('Disallowed proof axiom')
                result['axioms']=ax
        for mod in mods:
            txt=run('replay_'+mod.replace('.','_'),lake('leanchecker','--verbose',mod),lean)
            if 'replaying '+mod not in txt:raise RuntimeError('Missing replay diagnostic')
        txt=run('input_echo',lake('lean','Echo.lean'),lean)
        rows=[json.loads(x) for x in txt.splitlines() if x.startswith('{')]
        if len(rows)!=1:raise RuntimeError('Bad echo record count')
        M.check_echo(p,rows[0]);result['original_matrices_and_constraints_echo_match']=True
        if hashlib.sha256((lean/'Input.lean').read_bytes()).hexdigest()!=input_hash:raise RuntimeError('Input source changed')
        if hashlib.sha256((lean/'Certificate.lean').read_bytes()).hexdigest()!=cert_hash:raise RuntimeError('Certificate source changed')
        status='KERNEL_CHECKED_OPTIMAL_MENU' if c['kind']=='optimal_menu' else 'KERNEL_CHECKED_NO_ADMISSIBLE_MENU'
        result.update(status=status,finished_utc=datetime.now(timezone.utc).isoformat());save()
        print(status+(f' cost={c["cost"]}; selected={M.members(c["selection"],len(p["costs"]))}' if c['kind']=='optimal_menu' else ''),flush=True)
        return 0
    except Exception as e:
        result.update(status='UNRESOLVED',error=str(e),finished_utc=datetime.now(timezone.utc).isoformat());save()
        print('UNRESOLVED: '+str(e),flush=True);return 2

if __name__=='__main__':raise SystemExit(main())
