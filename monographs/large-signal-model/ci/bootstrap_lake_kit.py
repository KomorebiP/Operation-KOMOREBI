#!/usr/bin/env python3
"""Provision pinned Lake dependencies and adapt them to the unchanged verifier.
This creates a layout adapter to an installed elan toolchain and real Lake
checkout directories. It does not fetch or claim to restore a portable kit.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, shlex, subprocess, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINNED_INPUTS=('lean-toolchain','lake-manifest.json','lakefile.toml')
def sha(path: Path) -> str:return hashlib.sha256(path.read_bytes()).hexdigest()
def safe_link(link: Path,target: Path) -> None:
    target=target.resolve()
    if not target.is_dir():raise ValueError(f'Adapter target is not a directory: {target}')
    link.parent.mkdir(parents=True,exist_ok=True)
    if link.is_symlink() and link.resolve()==target:return
    if link.exists() or link.is_symlink():raise ValueError(f'Refusing to replace existing adapter path: {link}')
    link.symlink_to(target,target_is_directory=True)

def make_layout(kit: Path,prefix: Path,packages: Path) -> None:
    for rel in ('bin/lean','bin/leanchecker','src/lean/LeanChecker.lean'):
        if not (prefix/rel).is_file():raise ValueError(f'Installed toolchain lacks {rel}; no verifier run was performed.')
    safe_link(kit/'toolchain',prefix)
    safe_link(kit/'workspace/.lake/packages',packages)

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=Path('Lean'))
    ap.add_argument('--kit',type=Path,required=True)
    ap.add_argument('--mode',choices=['cache','source'],default='cache')
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,default=HERE/'frozen_lean_release.json')
    args=ap.parse_args();project=args.project.resolve();kit=args.kit.resolve();receipt=args.receipt.resolve()
    if kit.is_relative_to(project) or receipt.is_relative_to(project):
        ap.error('Adapter and new receipts must be outside the immutable Lean/ payload.')
    receipt.parent.mkdir(parents=True,exist_ok=True)
    logs=receipt.parent/'bootstrap-logs';logs.mkdir(parents=True,exist_ok=True)
    baseline=json.loads(args.baseline.read_text())
    env=os.environ.copy()
    for key in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LD_PRELOAD','ELAN_TOOLCHAIN','KOMOREBI_LEAN_KIT'):
        env.pop(key,None)
    env['GIT_TERMINAL_PROMPT']='0'
    report={'kind':'Lake/elan verifier layout adapter','passed':False,'fresh_project_lean_verification':False,
            'dependency_mode':args.mode,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stages':[]}
    def run(argv: list[str],capture: bool=False) -> str:
        log=logs/f'{len(report["stages"])+1:02d}.log';start=time.monotonic()
        print(shlex.join(argv),flush=True)
        with log.open('w') as out:
            proc=subprocess.run(argv,cwd=project,env=env,stdout=out,stderr=subprocess.STDOUT,text=True)
        report['stages'].append({'command':argv,'returncode':proc.returncode,'seconds':round(time.monotonic()-start,3),
                                'log':str(log.relative_to(receipt.parent)),'log_sha256':sha(log)})
        if proc.returncode!=0:raise RuntimeError(f'Bootstrap command failed with exit {proc.returncode}; see {log.name}')
        return log.read_text().strip() if capture else ''
    try:
        before={name:sha(project/name) for name in PINNED_INPUTS}
        if before!=baseline['pinned_input_sha256']:raise ValueError('Pinned project inputs differ from the frozen release.')
        if (project/'lean-toolchain').read_text().strip()!=baseline['lean_toolchain']:
            raise ValueError('Unexpected Lean toolchain selection.')
        if before['lake-manifest.json']!=baseline['lake_manifest_sha256']:
            raise ValueError('The dependency lock differs from the frozen release.')
        version=run(['lean','--version'],capture=True)
        if baseline['lean_commit'] not in version:raise ValueError('Installed Lean compiler commit differs from the release.')
        prefix=Path(run(['lean','--print-prefix'],capture=True)).resolve()
        run(['lake','--version'])
        # Lake consumes the existing lock. Never run `lake update` here.
        run(['lake','exe','cache','get'] if args.mode=='cache' else ['lake','build','@mathlib/Mathlib'])
        after={name:sha(project/name) for name in PINNED_INPUTS}
        if after!=before:raise ValueError('Lake changed a pinned project input; aborting before proof verification.')
        manifest=json.loads((project/'lake-manifest.json').read_text())
        packages=project/manifest['packagesDir'];dependencies=[]
        for package in manifest['packages']:
            path=packages/package['name']
            actual=run(['git','-C',str(path),'rev-parse','HEAD'],capture=True)
            if actual!=package['rev']:raise ValueError(f'Dependency revision mismatch: {package["name"]}')
            artifacts=path/'.lake/build/lib/lean'
            if not artifacts.is_dir():raise ValueError(f'Missing dependency Lean artifacts: {package["name"]}')
            dependencies.append({'name':package['name'],'revision':actual})
        make_layout(kit,prefix,packages)
        report.update(passed=True,lean_version=version,toolchain_prefix=str(prefix),dependencies=dependencies,
                      input_hashes=after,adapter_path=str(kit),portable_kit_restored=False)
    except Exception as exc:
        report['failure']=str(exc)
    finally:
        report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        receipt.write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:
        print('BOOTSTRAP FAILED: '+report['failure'],file=sys.stderr);return 1
    print('Pinned dependencies and verifier layout ready. Project proof verification has not run yet.')
    return 0
if __name__=='__main__':raise SystemExit(main())
