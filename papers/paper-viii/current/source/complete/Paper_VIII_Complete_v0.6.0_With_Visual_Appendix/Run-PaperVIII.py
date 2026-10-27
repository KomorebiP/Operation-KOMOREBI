#!/usr/bin/env python3
"""Verify or rebuild the Paper VIII reader edition without modifying preserved sources."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def verify() -> None:
    data=json.loads((ROOT/'MANIFEST.json').read_text()); failures=[]
    for name,item in data['files'].items():
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            failures.append(f'{name}: invalid relative path');continue
        p=(ROOT/rel).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            failures.append(f'{name}: missing or unsafe path');continue
        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:
            failures.append(f'{name}: size or SHA-256 mismatch')
    print(json.dumps({'status':'FAIL' if failures else 'PASS','files_checked':len(data['files']),'failures':failures,'scope':'Integrity against packaged hashes, not an independent authenticity signature or a new proof run.'},indent=2))
    if failures:raise SystemExit(1)

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['verify','examples','appendix','original-tests','original-figures','original-paper'])
    ap.add_argument('--output-dir',type=Path)
    args=ap.parse_args()
    if args.action=='verify':verify();return
    out=(args.output_dir or ROOT/'rebuilt'/args.action).resolve()
    for protected in [ROOT/'original_snapshot',ROOT/'original_companion',ROOT/'visual_appendix',ROOT/'reading_editions',ROOT/'editorial_evidence']:
        if out==protected or out.is_relative_to(protected):raise SystemExit('Output must be outside shipped source/evidence trees.')
    out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    commands=[]
    def run(argv: list[str], cwd: Path, label: str) -> None:
        started=datetime.now(timezone.utc).isoformat(); t=time.monotonic()
        with (out/(label+'.log')).open('w') as f:
            result=subprocess.run(argv,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
        commands.append({'name':label,'argv':argv,'cwd':str(cwd),'started_utc':started,'seconds':time.monotonic()-t,'exit_code':result.returncode,'log':label+'.log'})
        (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
        print(label+': '+('PASS' if result.returncode==0 else 'FAIL'))
        if result.returncode:raise RuntimeError('Command failed; inspect '+str(out/(label+'.log')))
    if args.action=='appendix':
        run([sys.executable,str(ROOT/'visual_appendix/build.py'),'--output-dir',str(out)],ROOT,'appendix_build');return
    with tempfile.TemporaryDirectory(prefix='paper_viii_replay_') as td:
        w=Path(td)
        if args.action=='examples':
            shutil.copytree(ROOT/'visual_appendix/source',w/'source',ignore=shutil.ignore_patterns('__pycache__'))
            (w/'checks').mkdir();shutil.copy2(ROOT/'visual_appendix/checks/verify_examples.py',w/'checks/verify_examples.py')
            run([sys.executable,'-W','error','checks/verify_examples.py'],w,'exact_examples')
            shutil.copy2(w/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json');return
        shutil.copytree(ROOT/'original_companion',w/'companion')
        c=w/'companion'
        env['PYTHONPATH']=os.pathsep.join([str(c),str(c/'legacy')])
        if args.action=='original-tests':
            run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','verification/test_strengthened.py','legacy/tests'],c,'companion_tests')
            shutil.copytree(ROOT/'original_snapshot',w/'formal')
            run([sys.executable,'-m','unittest','discover','-s','scripts','-p','test_*.py','-v'],w/'formal','verifier_software_tests')
            run([sys.executable,'scripts/run_sixth_regressions.py','--out',str(out/'RECOMPRESSION_REPLAY.json')],w/'formal','small_core_numerical_mirror')
        elif args.action=='original-figures':
            run([sys.executable,'-m','psc_packet.make_figures'],c,'historical_figure_replay')
            shutil.copytree(c/'figures',out/'figures',dirs_exist_ok=True)
        elif args.action=='original-paper':
            tex=shutil.which('pdflatex');bib=shutil.which('bibtex.original') or shutil.which('bibtex')
            if not tex or not bib:raise RuntimeError('pdflatex and a working BibTeX executable are required.')
            name='PSC_Paper_VIII_Strengthened_Annals_Edition'
            run([tex,'-interaction=nonstopmode','-halt-on-error',name+'.tex'],c,'original_tex_pass1')
            run([bib,name],c,'original_bibtex')
            for j in [2,3]:run([tex,'-interaction=nonstopmode','-halt-on-error',name+'.tex'],c,f'original_tex_pass{j}')
            shutil.copy2(c/(name+'.pdf'),out/(name+'.pdf'));shutil.copy2(c/(name+'.bbl'),out/(name+'.bbl'))
    print('Replay outputs: '+str(out))
    print('No Lean compiler or GPU timing experiment was invoked.')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,RuntimeError,subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc)) from exc
