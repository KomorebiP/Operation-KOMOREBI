#!/usr/bin/env python3
"""Regenerate all 171 lesson figures and rebuild the guide in a fresh directory."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCRIPTS=("figures_foundations.py","figures_i_iii.py","figures_iv_vi.py","figures_vii_viii.py","figures_synthesis.py","figures_sequences.py","figures_polyphase.py","figures_taps.py","figures_bridges.py","figures_operators.py","figures_capstone.py")
def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,help='New directory, relative to this guide or absolute. Existing paths are refused.')
    args=parser.parse_args()
    if sys.flags.optimize:parser.error('Run without -O: mathematical assertions must remain enabled.')
    target=Path(args.output_dir)
    if not target.is_absolute():target=ROOT/target
    target=target.resolve()
    if target.exists():parser.error(f'Refusing existing path: {target}')
    if ROOT.is_relative_to(target):parser.error('Output may not be an ancestor of the source directory.')
    target.mkdir(parents=True)
    for glob in ('*.py','*.tex'):
        for p in ROOT.glob(glob):shutil.copyfile(p,target/p.name)
    for rel in ('source_data','source_context','evidence/synthesis_authority'):
        shutil.copytree(ROOT/rel,target/rel)
    (target/'evidence').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'evidence/OEIS_SOURCE_RECORDS.json',target/'evidence/OEIS_SOURCE_RECORDS.json')
    inputs={str(p.relative_to(target)):digest(p) for p in target.rglob('*') if p.is_file()}
    logs=target/'run_logs';logs.mkdir()
    env={**os.environ,'MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1','PYTHONOPTIMIZE':'','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
    record={'status':'running','scope':'Finite computation and figure rebuild, not universal theorem or Lean certification.','input_hashes':inputs,'steps':[]}
    stages=list(SCRIPTS)+['build.py','validate_guide.py']
    for name in stages:
        start=time.monotonic()
        try:
            p=subprocess.run([sys.executable,name],cwd=target,env=env,text=True,capture_output=True,timeout=300)
            (logs/(name+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
            step={'script':name,'exit_code':p.returncode,'seconds':time.monotonic()-start}
        except (OSError,subprocess.TimeoutExpired) as e:
            step={'script':name,'exit_code':None,'error':str(e),'seconds':time.monotonic()-start}
        record['steps'].append(step);print(json.dumps(step),flush=True)
        if step['exit_code']!=0:
            record['status']='failed';(target/'rebuild_summary.json').write_text(json.dumps(record,indent=2));return 1
    changed=[n for n,h in inputs.items() if not (target/n).is_file() or digest(target/n)!=h]
    figures={ext:len(list((target/'figures').glob('*.'+ext))) for ext in ('pdf','png')}
    record.update(source_inputs_unchanged=not changed,changed_inputs=changed,figures=figures)
    record['status']='passed' if not changed and figures=={'pdf':171,'png':171} else 'failed'
    record['output_hashes']={str(p.relative_to(target)):digest(p) for d in ('figures','build','evidence') for p in (target/d).rglob('*') if p.is_file() and p.suffix in {'.pdf','.png','.json','.csv'}}
    (target/'rebuild_summary.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':record['status'],'figures':figures,'output':str(target)}))
    return 0 if record['status']=='passed' else 1
if __name__=='__main__':raise SystemExit(main())
