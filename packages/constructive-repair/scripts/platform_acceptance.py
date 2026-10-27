#!/usr/bin/env python3
"""Offline installed-wheel acceptance in a fresh local environment.

Run this script using each Python interpreter/platform being evaluated.
It never downloads Python, contacts a package index, or certifies Lean proofs.
The source archive and bundled wheel are required. The output directory must
not already exist. Receipts report only the platform actually executing them.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wheel', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    try:
        out.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        print(json.dumps({'status':'UNRESOLVED','error':str(exc)})); return 2
    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    wheel = (args.wheel or ROOT/'dist'/f'komorebi_constructive_repair-{version}-py3-none-any.whl').resolve()
    result = {'schema':'komorebi.repair.platform-acceptance.v1', 'status':'RUNNING',
              'started_utc':datetime.now(timezone.utc).isoformat(), 'version':version,
              'python':platform.python_version(), 'platform':platform.platform(),
              'implementation':platform.python_implementation(), 'machine':platform.machine(),
              'commands':[], 'checks':[], 'network_access_requested':False,
              'scope':'Python installed-wheel acceptance only, not Lean acceptance'}
    def save():
        (out/'platform_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    def check(name, condition):
        result['checks'].append({'name':name,'pass':bool(condition)}); save()
        if not condition:raise AssertionError(name)
    env = os.environ.copy()
    for k in ('PYTHONPATH','PYTHONHOME','VIRTUAL_ENV'):
        env.pop(k,None)
    env.update(PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1', PYTHONDONTWRITEBYTECODE='1')
    work = out/'working directory with spaces'; work.mkdir()
    def run(name, argv, expected=0, extra=None, timeout=180):
        start=time.monotonic();child_env=env.copy();child_env.update(extra or {})
        try:
            proc=subprocess.run([str(x) for x in argv],cwd=work,env=child_env,
                capture_output=True,text=True,encoding='utf-8',timeout=timeout)
            rc=proc.returncode;stdout=proc.stdout;stderr=proc.stderr;expired=False
        except subprocess.TimeoutExpired as exc:
            rc=None;expired=True
            def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
            stdout=txt(exc.stdout);stderr=txt(exc.stderr)
        (out/(name+'.log')).write_text(stdout+'\nSTDERR\n'+stderr,encoding='utf-8')
        result['commands'].append({'name':name,'argv':[str(x) for x in argv],
            'cwd':str(work),'returncode':rc,'expected_returncode':expected,'timed_out':expired,
            'seconds':round(time.monotonic()-start,3),'log':name+'.log'})
        save();check(name, rc==expected)
        return stdout
    try:
        check('wheel_exists',wheel.is_file())
        result['wheel_sha256']=hashlib.sha256(wheel.read_bytes()).hexdigest()
        prefix=out/'isolated Python environment'
        run('create_venv',[sys.executable,'-m','venv',prefix])
        exe=prefix/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        run('install_offline',[exe,'-m','pip','install','--no-index','--no-deps','--no-cache-dir',wheel])
        run('installed_probe',[exe,'-I',ROOT/'scripts/installed_probe.py','--fixtures',ROOT/'examples',
            '--prefix',prefix,'--version',version,'--output',out/'installed_probe.json'])
        report=json.loads((out/'installed_probe.json').read_text(encoding='utf-8'))
        result['installed_cases']=len(report['cases']);result['installed_checks']=len(report['checks'])
        check('installed_probe_status',report['status']=='PASS')
        doctor=json.loads(run('doctor',[exe,'-I','-m','komorebi_repair','doctor']))
        check('doctor_no_kernel_claim',doctor['kernel_checked'] is False)
        check('doctor_version',doctor['version']==version)
        entry=prefix/('Scripts/komorebi-repair.exe' if os.name=='nt' else 'bin/komorebi-repair')
        entry_doctor=json.loads(run('console_entry',[entry,'doctor']))
        check('console_entry_version',entry_doctor['version']==version)
        inp=ROOT/'examples/branch_corpus/Branch018_input.json'
        paths=work/'donn\u00e9es and \u7814\u7a76'; paths.mkdir()
        special=paths/'entr\u00e9e.json'; shutil.copyfile(inp,special)
        solved=json.loads(run('unicode_path_solve',[exe,'-I','-m','komorebi_repair','solve',special,'--output',paths/'r\u00e9sultat']))
        check('unicode_path_status',solved['status']=='PYTHON_CERTIFICATE_VALID')
        run('unicode_path_check',[exe,'-I','-m','komorebi_repair','check',special,paths/'r\u00e9sultat/certificate.json','--output',paths/'v\u00e9rification'])
        run('no_overwrite',[exe,'-I','-m','komorebi_repair','solve',special,'--output',paths/'r\u00e9sultat'],expected=2)
        run('no_repair',[exe,'-I','-m','komorebi_repair','solve',ROOT/'examples/branch_corpus/Branch019_input.json','--output',work/'no repair'])
        cert=json.loads((work/'no repair/certificate.json').read_text(encoding='utf-8'))
        check('no_repair_scoped',cert['kind']=='no_admissible_repair')
        run('budget',[exe,'-I','-m','komorebi_repair','solve',inp,'--max-nodes','0','--output',work/'budget'],expected=2)
        budget=json.loads((work/'budget/result.json').read_text(encoding='utf-8'))
        check('budget_unresolved',budget['status']=='UNRESOLVED' and budget['error_code']=='RESOURCE_LIMIT')
        corrupt=json.loads((paths/'r\u00e9sultat/certificate.json').read_text(encoding='utf-8'));corrupt['cost']+=1
        (work/'corrupt.json').write_text(json.dumps(corrupt),encoding='utf-8')
        run('corrupted_certificate',[exe,'-I','-m','komorebi_repair','check',inp,work/'corrupt.json','--output',work/'corrupt check'],expected=2)
        (work/'bad.json').write_bytes(b'\xff')
        run('invalid_utf8',[exe,'-I','-m','komorebi_repair','solve',work/'bad.json','--output',work/'bad input'],expected=2)
        # POSIX C locale is a specific test environment, not a Windows surrogate.
        if os.name=='posix':
            cenv={'LC_ALL':'C','LANG':'C','PYTHONCOERCECLOCALE':'0','PYTHONUTF8':'0'}
            raw=run('ascii_environment',[exe,'-X','utf8=0','-c',
                'import locale,sys,json; print(json.dumps({"encoding":locale.getpreferredencoding(False),"utf8_mode":sys.flags.utf8_mode}))'],extra=cenv)
            observed=json.loads(raw);result['ascii_environment']=observed
            check('ascii_default_observed',observed['encoding'].lower() in ('ascii','ansi_x3.4-1968','us-ascii') and observed['utf8_mode']==0)
            run('ascii_export',[exe,'-X','utf8=0','-m','repair_certificates','export',ROOT/'examples/worked_input.json',
                ROOT/'examples/worked_certificate.json',work/'ascii_export'],extra=cenv)
            lean=(work/'ascii_export/Certificate.lean').read_text(encoding='utf-8')
            check('utf8_lean_bytes', '\u2227' in lean)
        else:
            result['ascii_environment']={'status':'NOT_APPLICABLE','reason':'POSIX C-locale probe'}
        result.update(status='PASS',finished_utc=datetime.now(timezone.utc).isoformat());save()
        print(json.dumps({'status':'PASS','version':version,'python':result['python'],'platform':result['platform'],
            'installed_cases':result['installed_cases'],'receipt':str(out/'platform_report.json')}))
        return 0
    except Exception as exc:
        result.update(status='FAIL',error=repr(exc),finished_utc=datetime.now(timezone.utc).isoformat());save()
        print(json.dumps({'status':'FAIL','error':str(exc),'receipt':str(out/'platform_report.json')}));return 1


if __name__=='__main__':
    raise SystemExit(main())
