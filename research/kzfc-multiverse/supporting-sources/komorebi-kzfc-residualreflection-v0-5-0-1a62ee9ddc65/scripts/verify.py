#!/usr/bin/env python3
"""Rebuild, re-elaborate, audit axiom dependencies, and run compiler negative controls."""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, platform, re, shutil
import subprocess, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def uncomment(text: str) -> str:
    # Lean block comments nest. Also remove line comments and string contents.
    out = []; i = 0; depth = 0; string = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): depth += 1; i += 2
            elif text.startswith('-/', i): depth -= 1; i += 2
            else: i += 1
        elif string:
            if text[i] == '\\': i += 2
            elif text[i] == '"': string = False; i += 1
            else: i += 1
        elif text.startswith('/-', i): depth = 1; i += 2
        elif text.startswith('--', i):
            j = text.find('\n', i); i = len(text) if j < 0 else j
        elif text[i] == '"': string = True; i += 1
        else: out.append(text[i]); i += 1
    if depth or string: raise ValueError('Unclosed source comment or string')
    return ''.join(out)

def theorem_names(paths: list[pathlib.Path]) -> list[str]:
    """Enumerate declarations in this project's explicit namespace-only source format."""
    names = []
    for path in paths:
        if path.name == 'Audit.lean':
            continue
        stack = []
        for line in uncomment(path.read_text()).splitlines():
            m = re.match(r'^namespace\s+([A-Za-z_][\w.]*)\s*$', line)
            if m:
                stack.append(m.group(1))
                continue
            if re.match(r'^end(?:\s+[A-Za-z_][\w.]*)?\s*$', line):
                if stack:
                    stack.pop()
                continue
            m = re.match(r'^(?:protected\s+)?theorem\s+([A-Za-z_][\w.]*)', line)
            if m:
                name = m.group(1)
                names.append(name.removeprefix('_root_.') if name.startswith('_root_.')
                             else '.'.join(stack + [name]))
    if len(names) != len(set(names)):
        raise ValueError('Duplicate theorem name in source inventory')
    return sorted(names)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--sequential-build', action='store_true', help='Build project modules in topological order, one Lake target at a time')
    ap.add_argument('--clean', action='store_true', help='Delete only this project build cache')
    ap.add_argument('--timeout', type=int, default=240, help='Per-command timeout in seconds')
    args = ap.parse_args()
    v = ROOT / 'verification'; v.mkdir(exist_ok=True)
    # An interrupted rerun must not leave an earlier PASS at the active output path.
    for stale in ('RESULTS.json', 'audit_coverage.json'):
        (v / stale).unlink(missing_ok=True)
    start = time.monotonic(); started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    leanfiles = [ROOT / 'Komorebi.lean'] + sorted((ROOT / 'Komorebi').rglob('*.lean'))
    inputs = leanfiles + [ROOT / 'lakefile.toml', ROOT / 'lake-manifest.json', ROOT / 'lean-toolchain', ROOT / 'verification_contract.json', pathlib.Path(__file__)]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    records = []
    names = theorem_names(leanfiles)
    (v/'theorems.json').write_text(json.dumps(names, indent=2)+'\n')
    def run(name: str, argv: list[str], expect_zero: bool = True, match: str | None = None):
        st = time.monotonic()
        try:
            cp = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=args.timeout, check=False)
            code, text = cp.returncode, cp.stdout
        except subprocess.TimeoutExpired as e:
            code = 124
            text = (e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
            text += '\nCOMMAND TIMEOUT\n'
        path = v / (name + '.log'); path.write_text(text)
        passed = ((code == 0) if expect_zero else (code != 0 and code != 124))
        if match: passed = passed and match.lower() in text.lower()
        records.append({'name': name, 'argv': argv, 'exit_code': code, 'passed': passed,
                        'seconds': time.monotonic() - st, 'log': str(path.relative_to(ROOT))})
        print(('PASS ' if passed else 'FAIL ') + name, flush=True)
        return text
    if args.clean and (ROOT / '.lake/build').exists(): shutil.rmtree(ROOT / '.lake/build')
    lean_version = run('lean_version', ['lean', '--version'], match='4.34.0-rc2')
    lake_version = run('lake_version', ['lake', '--version'])
    if args.sequential_build:
        from graphlib import TopologicalSorter
        modules = {'.'.join(p.relative_to(ROOT).with_suffix('').parts): p
                   for p in leanfiles if p.name != 'Audit.lean'}
        graph = {m: {d for d in re.findall(r'^import\s+([\w.]+)', p.read_text(), re.M)
                     if d in modules} for m,p in modules.items()}
        for module in TopologicalSorter(graph).static_order():
            if module != 'Komorebi':
                run('build_' + module.split('.')[-1], ['lake', 'build', module])
    run('clean_build', ['lake', 'build', 'Komorebi'])
    for p in leanfiles:
        if p.name == 'Audit.lean': continue
        run('check_' + p.stem, ['lake','env','lean','-DwarningAsError=true',str(p.relative_to(ROOT))])
    axout = run('axiom_audit', ['lake','env','lean','-DwarningAsError=true','Komorebi/Foundation/Audit.lean'])
    audited_names = re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)", axout, re.M)
    audit_commands = re.findall(r'^#print axioms ([\w.]+)', (ROOT/'Komorebi/Foundation/Audit.lean').read_text(), re.M)
    coverage_ok = (set(names) == set(audited_names) == set(audit_commands) and
                   len(names) == len(audited_names) == len(audit_commands))
    coverage = {'passed': coverage_ok, 'theorem_count': len(names),
                'printed_count': len(audited_names),
                'missing': sorted(set(names)-set(audited_names)),
                'unexpected': sorted(set(audited_names)-set(names))}
    (v/'audit_coverage.json').write_text(json.dumps(coverage, indent=2)+'\n')
    records.append({'name':'complete_theorem_audit_coverage', **coverage})
    axioms = set()
    for content in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', axout):
        axioms.update(x.strip() for x in content.split(',') if x.strip())
    allowed = {'propext','Classical.choice','Quot.sound'}
    dependencies_ok = axioms <= allowed and 'sorryAx' not in axout
    records.append({'name':'axiom_allowlist','passed':dependencies_ok,'observed':sorted(axioms)})
    forbidden = re.compile(r'\b(?:axiom|sorry|admit|unsafe|implemented_by|native_decide|run_tac)\b')
    findings = {str(p.relative_to(ROOT)): forbidden.findall(uncomment(p.read_text())) for p in leanfiles}
    findings = {k:val for k,val in findings.items() if val}
    records.append({'name':'source_scan','passed':not findings,'findings':findings})
    with tempfile.TemporaryDirectory(prefix='kzfc_controls_') as td:
        path = pathlib.Path(td)
        falseproof = path / 'FalseProof.lean'
        falseproof.write_text('example : False := by\n  exact True.intro\n')
        run('negative_false_proof',['lake','env','lean','-DwarningAsError=true',str(falseproof)],False,'type mismatch')
        placeholder = path / 'Placeholder.lean'
        placeholder.write_text('example : False := by\n  sorry\n')
        run('negative_placeholder',['lake','env','lean','-DwarningAsError=true',str(placeholder)],False,'sorry')
    after = {str(p.relative_to(ROOT)):sha(p) for p in inputs}
    records.append({'name':'inputs_unchanged','passed':hashes == after})
    oldroot = ROOT / 'predecessor_sources'
    if oldroot.exists():
        preserved = [p for p in oldroot.rglob('*.lean') if p.name != 'Audit.lean' and p.name != 'Komorebi.lean']
        good = all((ROOT/p.relative_to(oldroot)).is_file() and sha(p) == sha(ROOT/p.relative_to(oldroot)) for p in preserved)
        records.append({'name':'predecessor_theorem_sources_preserved','passed':good,'files':len(preserved)})
    result = {'status':'PASS' if all(r['passed'] for r in records) else 'FAIL',
              'started_at':started,'runtime_seconds':time.monotonic()-start,'checks':records,
              'input_hashes_before':hashes,'input_hashes_after':after,
              'platform':platform.platform(),'cpu_count':os.cpu_count(),
              'lean_version':lean_version.strip(),'lake_version':lake_version.strip(),
              'theorem_count':len(names),'axioms_observed':sorted(axioms),'per_command_timeout_seconds':args.timeout,
              'build_strategy':'serial topological Lake targets' if args.sequential_build else 'parallel root target',
              'non_claims':['No new axiom of ZFC is proved or assumed.',
                            'The membership-only formula has a proved ZFSet interpretation, not an object-language ZFC derivation.',
                            'No arbitrary-model ZFC interpretation or regular-uncountable existence-guard formula is asserted.',
                            'No independence or relative-consistency theorem is asserted.',
                            'The explicit cokernel has not been identified with Mathlib right-derived limits.',
                            'No uncountable cardinal satisfying the classified principles is proved to exist.']}
    (v/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],flush=True)
    return 0 if result['status']=='PASS' else 1

if __name__ == '__main__': raise SystemExit(main())
