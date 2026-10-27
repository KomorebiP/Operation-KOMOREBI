#!/usr/bin/env python3
"""Recompile the explicit delivered Paper X source closure against its offline kit.

No network access, Lake update, inherited Paper X object, or production source
editing occurs. The external kit must be Lean 4.34.0-rc2 with the manifest's nine
dependency revisions. Every module compiles with warnings treated as errors.
"""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import time

BASE = Path(__file__).resolve().parent
LEAN_VERSION = 'Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)'
PINS = {
    'mathlib': 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
    'plausible': 'd9598f07b1bc701f1e3aae163d2681c1fd978793',
    'LeanSearchClient': 'ba67e212be1197b84c1f1f6299488a10a3002713',
    'importGraph': 'd8823026ac7ef130c253089d95685f9877b95323',
    'proofwidgets': 'a8acbfd87375ff4abe14ce09db5b7664d383bc7f',
    'aesop': '18889deb9e83ea7420ef51c160d6f88552e744e3',
    'Qq': '507746ab8f4b643ccdacb2ec4cdb5853fa9f8ab3',
    'batteries': '4cac2177c37f5530c4da76aa8e4307f3fc9e4dcb',
    'Cli': 'ab3a82db9fea14cf0fd7f5a2de650f4b534640af',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True, help='Absolute extracted offline-kit root.')
    parser.add_argument('--manifest', type=Path, default=BASE/'PUBLICATION_SOURCE_MANIFEST.json')
    parser.add_argument('--output', type=Path, required=True, help='New or empty independent build directory.')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--timeout-seconds', type=int, default=1800)
    args = parser.parse_args()
    if not args.runtime.is_absolute():
        parser.error('--runtime must be absolute')
    kit = args.runtime.resolve()
    manifest_path = args.manifest.resolve()
    data = json.loads(manifest_path.read_text())
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('--output must be new or empty; failed attempts are retained')
    out.mkdir(parents=True, exist_ok=True)
    objects = out/'objects'
    logs = out/'logs'
    objects.mkdir()
    logs.mkdir()
    env = os.environ.copy()
    for key in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME', 'LD_PRELOAD']:
        env.pop(key, None)
    env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env['PATH']
    lean = kit/'toolchain/bin/lean'
    startup = subprocess.run([str(lean), '--version'], env=env, capture_output=True, text=True)
    (logs/'unadapted_startup.log').write_text(startup.stdout+startup.stderr)
    adapter_used = False
    if startup.returncode and 'failed to locate application' in startup.stdout+startup.stderr:
        env['LD_PRELOAD'] = str(kit/'compat/app_path.so')
        adapter_used = True
        startup = subprocess.run([str(lean), '--version'], env=env, capture_output=True, text=True)
    if startup.returncode or startup.stdout.strip() != LEAN_VERSION:
        raise RuntimeError('Pinned Lean startup failed: ' + startup.stdout + startup.stderr)
    deps = []
    for name, expected in PINS.items():
        package = kit/'workspace/.lake/packages'/name
        actual = subprocess.check_output(['git', '-C', str(package), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise RuntimeError('Dependency mismatch: ' + name)
        lib = package/'.lake/build/lib/lean'
        deps.append({'name': name, 'expected_revision': expected, 'actual_revision': actual,
                     'compiled_module_root': str(lib) if lib.is_dir() else None,
                     'compiled_cache_present': lib.is_dir()})
    env['LEAN_PATH'] = os.pathsep.join([str(objects)] + [d['compiled_module_root'] for d in deps if d['compiled_module_root']])
    env['LEAN_ABORT_ON_PANIC'] = '1'
    records = {r['module']: r for r in data['modules']}
    if len(records) != data['count'] or data.get('missing'):
        raise RuntimeError('Invalid or incomplete explicit source selection')
    for rec in records.values():
        source = manifest_path.parent/rec['source_relative']
        if sha(source) != rec['source_sha256']:
            raise RuntimeError('Source hash mismatch: ' + str(source))
    results = []
    passed = set()
    failed = set()
    pending = set(records)
    running = {}
    start = time.monotonic()
    def save(complete=False):
        report = {'status': 'PASS' if complete and not failed and len(passed)==len(records) else ('FAIL' if failed else 'RUNNING'),
                  'scope': data['scope'], 'expected_modules': len(records), 'compiled_modules': len(results),
                  'passed_modules': len(passed), 'failed_modules': sorted(failed),
                  'blocked_modules': sorted(pending) if complete else [], 'complete': complete,
                  'production_objects_seeded': 0, 'mathlib_cold_rebuild': False,
                  'source_manifest': str(manifest_path), 'source_manifest_sha256': sha(manifest_path),
                  'runtime': str(kit), 'compiler': str(lean), 'compiler_sha256': sha(lean),
                  'lean_version': startup.stdout.strip(), 'compatibility_adapter_used': adapter_used,
                  'compatibility_adapter_environment': {'LD_PRELOAD': env.get('LD_PRELOAD')},
                  'dependencies': deps, 'LEAN_PATH_order': env['LEAN_PATH'].split(os.pathsep),
                  'source_unchanged': all(sha(manifest_path.parent/r['source_relative'])==r['source_sha256'] for r in records.values()),
                  'elapsed_seconds': round(time.monotonic()-start, 3), 'results': results}
        (out/'BUILD_REPORT.json').write_text(json.dumps(report, indent=2)+'\n')
    def compile_one(module):
        rec = records[module]
        source = manifest_path.parent/rec['source_relative']
        relative = Path(*module.split('.'))
        obj = objects/relative.with_suffix('.olean')
        interface = objects/relative.with_suffix('.ilean')
        obj.parent.mkdir(parents=True, exist_ok=True)
        cmd = [str(lean), '-j1', '-DwarningAsError=true', '-o', str(obj), '-i', str(interface), str(source)]
        began = time.monotonic()
        try:
            p = subprocess.run(cmd, cwd=manifest_path.parent/rec['source_relative'].split('/')[0], env=env,
                               text=True, capture_output=True, timeout=args.timeout_seconds)
            stdout, stderr, code, timeout = p.stdout, p.stderr, p.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b''
            stderr = exc.stderr or b''
            if isinstance(stdout, bytes): stdout = stdout.decode(errors='replace')
            if isinstance(stderr, bytes): stderr = stderr.decode(errors='replace')
            code, timeout = None, True
        log = logs/(module+'.log')
        log.write_text(stdout+stderr)
        row = {'module': module, 'source_relative': rec['source_relative'], 'source_sha256': rec['source_sha256'],
               'command': cmd, 'returncode': code, 'timed_out': timeout,
               'seconds': round(time.monotonic()-began, 3), 'stdout': stdout, 'stderr': stderr,
               'log': str(log.relative_to(out)), 'status': 'PASS' if code==0 and obj.is_file() else 'FAIL'}
        if code==0 and obj.is_file():
            row['outputs'] = [{'path': str(p.relative_to(out)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                              for p in [obj, interface] if p.is_file()]
        return row
    save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        while pending or running:
            for module in sorted(pending):
                local = set(records[module]['imports']) & records.keys()
                if local <= passed and len(running) < args.workers:
                    running[pool.submit(compile_one, module)] = module
                    pending.remove(module)
            if not running:
                break
            done, _ = concurrent.futures.wait(running, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                module = running.pop(future)
                row = future.result()
                results.append(row)
                (passed if row['status']=='PASS' else failed).add(module)
                print(json.dumps({'module': module, 'status': row['status'], 'seconds': row['seconds'],
                                  'passed': len(passed), 'total': len(records)}), flush=True)
                save()
    save(complete=True)
    return 0 if not failed and len(passed)==len(records) else 1

if __name__ == '__main__':
    raise SystemExit(main())
