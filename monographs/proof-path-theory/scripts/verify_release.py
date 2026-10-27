"""Fail-closed full release verification. Requires the pinned offline Lean kit."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from xml.etree import ElementTree
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
LOGS=ROOT/'evidence/release_1.8.0'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path,default=os.environ.get('KOMOREBI_LEAN_RUNTIME'))
    args=parser.parse_args()
    if args.runtime is None: parser.error('--runtime or KOMOREBI_LEAN_RUNTIME is required for the full release verifier')
    LOGS.mkdir(parents=True,exist_ok=True)
    report={'publication_edition':'1.8.0','version':'1.6.0','status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),'commands':[]}
    out=DATA/'release_verification.json';out.write_text(json.dumps(report,indent=2)+'\n')
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    def run(command,label,cwd=ROOT,custom_env=None,timeout=120):
        start=time.monotonic(); command=list(map(str,command))
        p=subprocess.Popen(command,cwd=cwd,env=custom_env or env,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,text=True,start_new_session=True)
        try: text,_=p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGKILL);text,_=p.communicate()
            (LOGS/(label+'.log')).write_text(text)
            raise RuntimeError(f'{label} timed out')
        log=LOGS/(label+'.log');log.write_text(text)
        report['commands'].append(dict(label=label,command=command,exit_code=p.returncode,
            seconds=round(time.monotonic()-start,4),log=str(log.relative_to(ROOT)),log_sha256=sha(log)))
        print(f'{label}: exit {p.returncode}',flush=True)
        if p.returncode:raise RuntimeError(f'{label} failed: {text[-2000:]}')
        return text
    try:
        for program in ('pdflatex','pdfinfo'):
            if not shutil.which(program):raise RuntimeError(f'{program} is required; paper verification is not silently skipped')
        run([sys.executable,'-m','compileall','-q','src','tests','scripts'],'python_syntax')
        with TemporaryDirectory(prefix='ppt-tests-') as td:
            junit=Path(td)/'pytest.xml'
            run([sys.executable,'-m','pytest','--junitxml',junit],'pytest',timeout=180)
            root=ElementTree.parse(junit).getroot()
            suites=list(root.findall('.//testsuite')) if root.tag!='testsuite' else [root]
            counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
            if counts['tests']<=0 or any(counts[k] for k in ('failures','errors','skipped')):raise RuntimeError(f'test counts not clean: {counts}')
            report['tests']=counts
            shutil.copy2(junit,LOGS/'pytest.xml')
        for script in ('build_examples','deep_validation','build_bridge_examples','design_figures','check_recovery_extension','check_trace_exchange'):
            run([sys.executable,'scripts/'+script+'.py'],script,timeout=180)
        run([sys.executable,'examples/ambient_realization.py'],'ambient_example')
        run([sys.executable,'scripts/verify_lean.py','--runtime',args.runtime],'lean_verifier',timeout=900)
        lean=json.loads((ROOT/'evidence/formal_1.8.0/verification.json').read_text())
        if lean['status']!='PASS':raise RuntimeError('Lean result not PASS')
        report['lean']={key:lean[key] for key in ('named_theorems','named_declarations','status','replay_kind','compiler')}
        report['lean']['modules']=18
        report['lean']['negative_controls']=len(lean['negative_controls'])
        report['trace_json_conformance']=lean['trace_json_conformance']
        run([sys.executable,'scripts/verify_bridge.py'],'bridge_exhaustive',timeout=180)
        bridge=json.loads((DATA/'bridge_verification.json').read_text())
        if bridge['status']!='PASS':raise RuntimeError('bridge checks not PASS')
        report['bridge']=bridge
        for name,cmd in [
            ('cli_validate',['validate','examples/and_dag.json']),
            ('cli_core',['core','examples/and_dag.json']),
            ('cli_minimum',['minimum','examples/alternative_proofs.json']),
            ('cli_set_cover',['minimum','examples/set_cover_certificate.json']),
            ('cli_schema',['schema','proof-field']),
            ('cli_native',['validate','data/native_lean_field.json']),
            ('cli_wire_positive',['wire-check','examples/trace_exchange/andPositive.problem.json','examples/trace_exchange/andPositive.certificate.json']),
            ('cli_wire_negative',['wire-check','examples/trace_exchange/andNegative.problem.json','examples/trace_exchange/andNegative.certificate.json'])]:
            run([sys.executable,'-m','proof_path_theory',*cmd],name)
        for i in range(3):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Proof_Path_Theory.tex'],f'latex_{i+1}',cwd=ROOT/'docs',timeout=180)
        log=(ROOT/'docs/Proof_Path_Theory.log').read_text(errors='replace')
        markers=('LaTeX Warning','Package microtype Warning','Overfull ','Underfull ','undefined references','multiply defined')
        warnings=[l for l in log.splitlines() if any(m in l for m in markers)]
        if warnings:raise RuntimeError(f'LaTeX warnings: {warnings[:8]}')
        pdf=ROOT/'docs/Proof_Path_Theory.pdf'
        info=run(['pdfinfo',pdf],'pdfinfo')
        match=re.search(r'^Pages:\s*(\d+)',info,re.M)
        if not match:raise RuntimeError('PDF page count missing')
        report['paper']={'pages':int(match[1]),'sha256':sha(pdf),'latex_warnings':0}
        for ext in ('pdf','png'):
            count=len(list((ROOT/'docs/figures').glob('fig_*.'+ext)))
            if count!=25:raise RuntimeError(f'expected twenty-five {ext} figures, found {count}')
        report['figures']={'vector_pdf':25,'png':25}
        claims=list(csv.DictReader((DATA/'claim_ledger.csv').open()))
        if len(claims)!=47 or len({c['claim_id'] for c in claims})!=47:raise RuntimeError('claim ledger must have 47 unique records')
        report['claim_records']=len(claims)
        human_ledger=(ROOT/'docs/THEOREM_LEDGER.md').read_text()
        human_ids=re.findall(r'^\| (PPT-\d+) \|',human_ledger,re.M)
        if human_ids != [c['claim_id'] for c in claims]:raise RuntimeError('human and CSV theorem ledgers disagree')
        deep=json.loads((DATA/'deep_validation.json').read_text())
        if deep.get('status')!='passed':raise RuntimeError('inherited deep checks not passed')
        report['fresh_exact_checks']=deep
        report['recovery_extension']=json.loads((DATA/'recovery_extension_checks_1.8.0.json').read_text())
        run([sys.executable,'scripts/build_visual_sampler.py'],'visual_sampler')
        run([sys.executable,'scripts/build_release.py'],'package_build',timeout=180)
        wheel=list((ROOT/'dist').glob('*1.6.0*.whl'))
        if len(wheel)!=1:raise RuntimeError('unique 1.6.0 wheel missing')
        with TemporaryDirectory(prefix='ppt-installed-') as td:
            target=Path(td)/'installed'
            run([sys.executable,'-m','pip','install','--no-index','--no-deps','--target',target,wheel[0]],'wheel_install',cwd=Path(td))
            installed_env=env.copy();installed_env['PYTHONPATH']=str(target)
            smoke="import proof_path_theory as p; assert p.__version__ == '1.6.0'; f=p.load_proof_field(r'"+str(ROOT/'data/native_lean_field.json')+"'); assert f.targets <= p.ProofFieldViews(f).least_model(); assert p.FiniteViewSystem({},()).sections() == ({},); assert p.bundled_schema('proof-field')['properties']; print(p.__file__)"
            installed=run([sys.executable,'-c',smoke],'installed_smoke',cwd=Path(td),custom_env=installed_env)
            if str(target) not in installed:raise RuntimeError('smoke imported source tree instead of installed wheel')
            installed_junit=Path(td)/'installed-tests.xml'
            run([sys.executable,'-m','pytest','-c',ROOT/'pyproject.toml','--rootdir',Path(td),
                 '-o','addopts=','-q','--junitxml',installed_junit,ROOT/'tests'],
                'installed_full_tests',cwd=Path(td),custom_env=installed_env,timeout=180)
            x=ElementTree.parse(installed_junit).getroot()
            ss=list(x.findall('.//testsuite')) if x.tag!='testsuite' else [x]
            cc={key:sum(int(z.attrib.get(key,0)) for z in ss) for key in ('tests','failures','errors','skipped')}
            if cc!=report['tests']:raise RuntimeError(f'Installed/source test mismatch: {cc}')
            report['installed_tests']=cc
            shutil.copy2(installed_junit,LOGS/'installed_tests.xml')

        report['distributions']={p.name:sha(p) for p in (ROOT/'dist').iterdir() if p.is_file()}
        run([sys.executable,'scripts/verify_publication_edition.py'],'publication_audit',timeout=180)
        report['source_hashes']={str(p.relative_to(ROOT)):sha(p) for pattern in ('src/**/*.py','tests/*.py','scripts/*.py','formal/**/*.lean','docs/**/*.tex','schemas/*.json','docs/**/*.md','github-integration/**/*.yml','*.md','pyproject.toml','CITATION.cff','MANIFEST.in','Makefile','formal/*.json') for p in ROOT.glob(pattern)}
        report['status']='PASS'
    except Exception as e:
        report['status']='FAIL';report['failure']=str(e);print(str(e),file=sys.stderr)
    finally:
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('status','tests','claim_records','paper','lean') if k in report},indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
