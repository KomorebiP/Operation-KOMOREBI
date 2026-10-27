#!/usr/bin/env python3
"""Rebuild, audit, replay, and exercise the Realization Boundaries Lean companion.

Requires the pinned Linux portable kit. No network requests or dependency upgrades.
Production modules are compiled serially to avoid parallel-import memory spikes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

MODULES = ['Ambient', 'Quotient', 'Preimages', 'FiniteQuotients', 'Extensions', 'Sections', 'Cocycle', 'PairedPrimes', 'NormalForms', 'PureCorrespondence', 'Countability', 'ProductTopology', 'FiniteTargets', 'ProfiniteCompletion', 'CompletionConsequences', 'TailSignature', 'SelectorClassification', 'HomomorphismObstruction', 'NormalFormTransport', 'ClassificationConsequences', 'DiagonalHomomorphisms', 'DiagonalRealization', 'EndomorphismScalars', 'DiagonalAutomorphisms', 'CompletionReflection', 'DirectSumEndomorphisms', 'SeedGeneration', 'SeedObstructions', 'GenerationRanks', 'Procyclic', 'GenerationConsequences', 'RootFibers', 'RadicalCounts', 'CyclicQuotients', 'CyclicFiniteTargets', 'RootConsequences', 'Reachability', 'SubgroupSpectrum', 'UnarySelectors', 'ObservationPatternClosure', 'GrammarEscape', 'RationalFG', 'StructuralClosure', 'PrimeComputability', 'ComputablePresentations', 'RootAlgorithm', 'ObservationSystems', 'RootAlgorithmCost', 'SubgroupTopology', 'RationalComputability', 'ComputableQuotientCodes', 'OracleCopyOperations', 'SpectrumComputability', 'DirectSumPresentation', 'ComputableNormalCodes', 'SearchEnumerableSpectrum', 'ListingSearchEquivalence', 'OraclePartialRecursionTraces', 'OraclePartialMinimizationTraces', 'OracleEnumerationNormalForm', 'EnumerationClosure', 'ComputableFiniteObservations', 'DegreeVariation', 'CanonicalOperationDegree', 'AdditionGraphDegree', 'LocalCocycleQueries']
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
ROOT = Path(__file__).resolve().parent.parent


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(p: Path, obj: object) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def source_snapshot() -> dict[str, str]:
    files = list((ROOT / 'RealizationBoundaries').glob('*.lean'))
    files += list((ROOT / 'tests').rglob('*.lean')) + list((ROOT / 'scripts').glob('*.py')) + list((ROOT / 'scripts').glob('*.sh'))
    files += [ROOT / n for n in ['RealizationBoundaries.lean', 'lakefile.toml',
                                'lake-manifest.json', 'lean-toolchain', 'tests/controls.json']]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(files)}


def parse_audit(log: Path) -> tuple[list[dict], list[dict], dict]:
    rows = [json.loads(s) for s in log.read_text().splitlines() if s.startswith('{')]
    decls = [r for r in rows if r.get('record') == 'declaration']
    imports = [r for r in rows if r.get('record') == 'import']
    summaries = [r for r in rows if r.get('record') == 'summary']
    if not decls or len(summaries) != 1 or summaries[0].get('status') != 'PASS':
        raise RuntimeError('Missing or unsuccessful declaration audit')
    if summaries[0]['declarations'] != len(decls):
        raise RuntimeError('Audit count mismatch')
    for d in decls:
        if d['unsafe'] or d['kind'] == 'axiom' or not set(d['axioms']) <= ALLOWED:
            raise RuntimeError('Forbidden declaration or axiom: ' + d['name'])
    return sorted(decls, key=lambda d: d['name']), imports, summaries[0]


def cache_snapshot(imports: list[dict], kit: Path) -> dict[str, dict]:
    paths: set[Path] = set()
    for row in imports:
        if row['module'].startswith('RealizationBoundaries'):
            continue
        path = Path(row['path']).resolve()
        for candidate in [path, Path(str(path)+'.server'), Path(str(path)+'.private'),
                          path.with_suffix('.ir'), path.with_suffix('.ilean')]:
            if candidate.is_file():
                paths.add(candidate)
    for rel in ['toolchain/bin/lean', 'toolchain/bin/lake', 'toolchain/bin/leanchecker',
                'toolchain/lib/lean/libleanshared.so', 'compat/app_path.so', 'workspace/lake-manifest.json']:
        path = kit / rel
        if path.is_file():
            paths.add(path.resolve())
    for adapter in os.environ.get('LD_PRELOAD', '').split(':'):
        if adapter and Path(adapter).is_file():
            paths.add(Path(adapter).resolve())
    return {str(p): {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(paths)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit', default=os.environ.get('KOMOREBI_LEAN_KIT'))
    ap.add_argument('--output', required=True, type=Path,
                    help='New directory for immutable verification evidence')
    ap.add_argument('--timeout', type=int, default=180,
                    help='Per-command limit; a timeout is a failed check')
    args = ap.parse_args()
    if not args.kit:
        ap.error('Supply --kit or set KOMOREBI_LEAN_KIT to the pinned offline runtime')
    kit = Path(args.kit).expanduser().resolve()
    out = args.output.expanduser().resolve()
    if out.exists():
        ap.error('Output directory already exists; choose a new one')
    if not (kit / 'toolchain/bin/lean').is_file():
        ap.error('Pinned compiler not found inside the supplied kit')
    out.mkdir(parents=True)
    (out/'logs').mkdir()
    env = os.environ.copy()
    env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env.get('PATH','')
    for k in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME']:
        env.pop(k, None)
    report: dict = {'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat(),
                    'commands': [], 'kit': str(kit), 'scope': 'project-only kernel replay; imported caches trusted'}
    start = time.monotonic()

    def run(name: str, argv: list[str], expected: list[str] | None = None) -> Path:
        log = out/'logs'/f'{name}.log'
        t = time.monotonic()
        with log.open('w') as f:
            p = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            timed_out = False
            try:
                rc = p.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(p.pid, signal.SIGKILL)
                rc = p.wait()
        text = log.read_text(errors='replace')
        passed = not timed_out and ((rc == 0) if expected is None else
                 (rc != 0 and all(s.lower() in text.lower() for s in expected)))
        row = {'name': name, 'argv': argv, 'returncode': rc, 'seconds': time.monotonic()-t,
               'timeout': timed_out, 'expected_diagnostics': expected, 'pass': passed,
               'log': str(log.relative_to(out)), 'log_sha256': digest(log)}
        report['commands'].append(row)
        write_json(out/'run.json', report)
        print(f'{name}: {"PASS" if passed else "FAIL"} ({row["seconds"]:.2f}s)', flush=True)
        if not passed:
            raise RuntimeError(f'{name} failed; see {log}')
        return log

    def lean(name: str, source: str, expected: list[str] | None = None) -> Path:
        src = Path(source)
        target = ROOT/'.lake/build/lib/lean'/src.with_suffix('.olean')
        target.parent.mkdir(parents=True, exist_ok=True)
        return run(name, [str(kit/'toolchain/bin/lake'), 'env', 'lean',
                         '-DwarningAsError=true', '-DautoImplicit=false',
                         '-o', str(target), str(src)], expected)

    try:
        # Attach only the already present pinned package cache. Never silently replace a checkout.
        packages = ROOT/'.lake/packages'
        packages.parent.mkdir(exist_ok=True)
        desired = kit/'workspace/.lake/packages'
        if not packages.exists():
            packages.symlink_to(desired, target_is_directory=True)
        if packages.resolve() != desired.resolve():
            raise RuntimeError('Existing dependency directory is not the supplied kit; left unchanged')
        pins = json.loads((ROOT/'lake-manifest.json').read_text())['packages']
        pin_results=[]
        for pin in pins:
            path = desired/pin['name']
            result = subprocess.run(['git','-C',str(path),'rev-parse','HEAD'],
                                    capture_output=True,text=True,timeout=30)
            actual=result.stdout.strip()
            if result.returncode or actual != pin['rev']:
                raise RuntimeError('Dependency revision mismatch: '+pin['name'])
            pin_results.append({'name':pin['name'],'expected':pin['rev'],'actual':actual})
        report['dependency_pins']=pin_results
        version_log=run('compiler_version',[str(kit/'toolchain/bin/lean'),'--version'])
        report['compiler_version']=version_log.read_text().strip()
        if '4.34.0-rc2' not in report['compiler_version'] or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in report['compiler_version']:
            raise RuntimeError('Unexpected compiler identity')
        before=source_snapshot()
        write_json(out/'source_before.json',before)
        for rel in ['RealizationBoundaries.lean']+[f'RealizationBoundaries/{m}.lean' for m in MODULES]:
            text=(ROOT/rel).read_text()
            text=re.sub(r'/\-.*?\-/','',text,flags=re.S)
            text=re.sub(r'--[^\n]*','',text)
            if re.search(r'\b(sorry|admit|axiom|unsafe)\b',text):
                raise RuntimeError('Forbidden production source token in '+rel)
        # A preflight import snapshot is possible when previous checked objects are present.
        # A first-time checkout obtains the same baseline after compiling; this is recorded explicitly.
        if (ROOT/'.lake/build/lib/lean/RealizationBoundaries.olean').is_file():
            log=lean('preflight_audit','tests/Audit.lean')
            _,imports,_=parse_audit(log)
            cache_before=cache_snapshot(imports,kit)
            report['cache_baseline']='before_clean_rebuild'
        else:
            cache_before=None
            report['cache_baseline']='after_initial_clean_build'
        build=ROOT/'.lake/build'
        if build.exists():
            shutil.rmtree(build)
        for m in MODULES:
            lean('build_'+m,f'RealizationBoundaries/{m}.lean')
        lean('build_entrypoint','RealizationBoundaries.lean')
        auditlog=lean('production_audit','tests/Audit.lean')
        decls,imports,summary=parse_audit(auditlog)
        write_json(out/'declarations.json',decls)
        write_json(out/'imported_modules.json',imports)
        report['declaration_count']=len(decls)
        report['axioms']=sorted({a for d in decls for a in d['axioms']})
        if cache_before is None:
            cache_before=cache_snapshot(imports,kit)
        write_json(out/'dependency_before.json',cache_before)
        lean('positive_contracts','tests/Contracts.lean')
        lean('closure_contracts','tests/ClosureContracts.lean')
        lean('root_runtime','tests/RootRuntime.lean')
        lean('normal_runtime','tests/NormalRuntime.lean')
        controls=json.loads((ROOT/'tests/controls.json').read_text())
        for c in controls:
            lean('negative_'+c['name'],c['file'],c['diagnostics'])
        report['negative_controls']=len(controls)
        # Sequential replay: never launch one memory-heavy import process per module concurrently.
        for m in MODULES:
            run('replay_'+m,[str(kit/'toolchain/bin/lake'),'env','leanchecker','--verbose',
                             'RealizationBoundaries.'+m])
        after=source_snapshot()
        write_json(out/'source_after.json',after)
        if before != after:
            raise RuntimeError('Sources changed during verification')
        cache_after=cache_snapshot(imports,kit)
        write_json(out/'dependency_after.json',cache_after)
        if cache_before != cache_after:
            raise RuntimeError('Imported cache/compiler bytes changed during verification')
        report.update(status='PASS', source_identity='PASS',dependency_identity='PASS',
                      production_modules=len(MODULES),entrypoints=1,
                      replay='same-kernel project-module replay; not an independent kernel',
                      duration_seconds=time.monotonic()-start,
                      finished_utc=datetime.now(timezone.utc).isoformat())
        write_json(out/'run.json',report)
        print(json.dumps({k:report[k] for k in ['status','production_modules','declaration_count',
                          'negative_controls','axioms','duration_seconds']},indent=2),flush=True)
        return 0
    except Exception as e:
        report.update(status='FAIL',error=str(e),duration_seconds=time.monotonic()-start,
                      finished_utc=datetime.now(timezone.utc).isoformat())
        write_json(out/'run.json',report)
        print('VERIFICATION FAILED:',e,file=sys.stderr,flush=True)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
