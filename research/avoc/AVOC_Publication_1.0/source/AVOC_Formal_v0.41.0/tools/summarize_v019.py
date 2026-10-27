#!/usr/bin/env python3
"""Fail-closed collector for final v0.19 source, build, axiom and test evidence.

Run after verify_release.py and checks/test_live_workflow.py. No proof execution
is replaced by this collector. Requires Python 3.10+ and the current .olean files.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import platform
import re
import subprocess
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / 'results/v0.19.0'

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text())

def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2) + '\n')

def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)

def uncomment(text: str) -> str:
    """Preserve newlines while removing nested Lean and line comments."""
    out: list[str] = []
    i = depth = 0
    while i < len(text):
        if text.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and text.startswith('-/', i):
            depth -= 1; i += 2; continue
        if not depth and text.startswith('--', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
            continue
        if not depth or text[i] == '\n':
            out.append(text[i])
        i += 1
    require(depth == 0, 'Unclosed Lean block comment')
    return ''.join(out)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', type=Path,
                    default=Path('/mnt/data/AVOC_Formal_v0.18.0.zip'))
    ap.add_argument('--demo-dir', type=Path, default=RD / 'live_success_final')
    args = ap.parse_args()
    order = load(RD / 'build_order.json')
    records = []
    for rel in order:
        src = ROOT / rel
        recpath = RD / ('clean_' + src.stem + '.json')
        rec = load(recpath)
        require(rec['returncode'] == 0 and not rec['timed_out'], 'Unsuccessful build: ' + rel)
        require(rec.get('source_unchanged') is True, 'Source changed during build: ' + rel)
        require(rec['source_sha256'] == digest(src), 'Stale source build: ' + rel)
        require(rec['source_before_sha256'] == digest(src), 'Wrong pre-build source: ' + rel)
        require('-DwarningAsError=true' in rec['command'], 'Warnings were not errors: ' + rel)
        log = ROOT / rec['log']
        require(digest(log) == rec['log_sha256'], 'Build log changed: ' + rel)
        output = ROOT / '.lake/build/lib/lean' / Path(rel).with_suffix('.olean')
        require(output.is_file() and digest(output) == rec['output_sha256'], 'Missing/stale output: ' + rel)
        records.append(dict(source=rel, record=str(recpath.relative_to(ROOT)),
                            source_sha256=digest(src), output_sha256=digest(output), returncode=0))
    save(RD / 'final_local_build_summary.json', records)

    negatives = []
    failure_pattern = r'unknown (?:module|constant|identifier)|object file .*does not exist|failed to locate|has been deprecated|unexpected token|maximum (?:recursion|number of heartbeats)|failed to synthesize'
    for src in sorted((ROOT / 'tests/negative').glob('*.lean')):
        recpath = RD / ('negative_' + src.stem + '.json')
        rec = load(recpath)
        log = ROOT / rec['log']
        text = log.read_text()
        require(rec['returncode'] != 0 and not rec['timed_out'], 'No substantive rejection: ' + src.name)
        require(rec['source_sha256'] == digest(src) and rec['source_unchanged'], 'Stale negative: ' + src.name)
        require(rec['log_sha256'] == digest(log), 'Changed negative log: ' + src.name)
        require('error:' in text and not re.search(failure_pattern, text, re.I), 'Setup/parser failure: ' + src.name)
        negatives.append(dict(source=str(src.relative_to(ROOT)), record=str(recpath.relative_to(ROOT)),
                              expected_rejection=True, log_sha256=digest(log)))
    save(RD / 'negative_summary.json', negatives)

    inventory = load(RD / 'declaration_inventory.json')
    expected_names = {e['qualified_name'] for e in inventory}
    require(len(expected_names) == len(inventory), 'Duplicate declaration inventory')
    sources = sorted(p for p in (ROOT / 'AVOC').glob('*.lean')
                     if p.name not in ['Audit.lean', 'FullAudit.lean'])
    source_scan = []
    declaration_count = 0
    for src in sources + [ROOT / 'AVOC.lean']:
        text = uncomment(src.read_text())
        for match in re.finditer(r'\b(sorry|native_decide)\b|^\s*(?:axiom|unsafe)\b|\bby\s+admit\b|^\s*admit(?:\s|$)', text, re.M):
            source_scan.append(dict(source=str(src.relative_to(ROOT)), text=match.group()))
        if src.name != 'AVOC.lean':
            found = len(re.findall(r'^\s*(?:@\[[^\]]+\]\s*)*(?:private\s+)?(?:protected\s+)?(?:theorem|lemma)\s+', text, re.M))
            indexed = sum(e['module'] == str(src.relative_to(ROOT)) for e in inventory)
            require(found == indexed, f'Declaration mismatch {src.name}: source {found}, inventory {indexed}')
            declaration_count += found
    require(not source_scan, 'Forbidden positive source shortcuts: ' + repr(source_scan))
    require(declaration_count == len(inventory), 'Total census mismatch')
    save(RD / 'source_scan.json', dict(passed=True, hits=[], declarations_counted=declaration_count,
                                      declaration_count_method='comment-aware per-module census checked against complete names'))

    ar = load(RD / 'full_axiom_audit.json')
    require(ar['returncode'] == 0 and not ar['timed_out'], 'Axiom audit did not execute')
    require(ar['source_sha256'] == digest(ROOT / 'AVOC/FullAudit.lean'), 'Stale audit source')
    require(ar['log_sha256'] == digest(ROOT / ar['log']), 'Axiom log changed')
    text = (ROOT / ar['log']).read_text()
    names = re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)", text, re.M)
    require(len(names) == len(inventory) and set(names) == expected_names, 'Incomplete axiom name set')
    axioms: set[str] = set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]', text, re.S):
        axioms.update(x.strip() for x in block.split(',') if x.strip())
    require(axioms <= {'propext', 'Classical.choice', 'Quot.sound'}, 'Unexpected axioms: ' + repr(axioms))
    save(RD / 'axiom_audit_summary.json', dict(passed=True, expected=len(inventory), audited=len(names),
                                             axioms=sorted(axioms), unexpected=[]))

    pins = load(RD / 'dependency_pins.json')
    require(len(pins) == 9 and all(p['passed'] for p in pins), 'Dependency pin verification incomplete')
    kit = Path(os.environ.get('AVOC_LEAN_KIT', '/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
    dependency_checks = []
    for pin in pins:
        folder = kit / 'workspace/.lake/packages' / pin['name']
        cmd = ['git', '-c', f'safe.directory={folder}', '-C', str(folder)]
        actual = subprocess.check_output(cmd + ['rev-parse', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(cmd + ['status', '--porcelain', '--untracked-files=no'], text=True).strip()
        require(actual == pin['expected'] and not dirty, 'Changed tracked dependency: ' + pin['name'])
        dependency_checks.append(dict(name=pin['name'], expected=pin['expected'], actual=actual,
                                      tracked_changes=dirty, passed=True))
    save(RD / 'dependency_checkout_audit.json', dependency_checks)

    # Live tests use actual Lean calls and fresh protected stores. Temporary raw
    # stores are not retained; current source hashes and result records are.
    import ast
    test_source = ROOT / 'checks/test_live_workflow.py'
    cases = None
    for node in ast.parse(test_source.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CASES' for t in node.targets):
            cases = ast.literal_eval(node.value)
    require(cases is not None and len(cases) == 22, 'Unexpected live regression inventory')
    live_results = []
    for case in cases:
        path = RD / 'live_tests' / (case + '.json')
        row = load(path)
        require(row.get('passed') is True and row['case'] == case, 'Live test failed: ' + case)
        require(row['test_source_sha256'] == digest(test_source), 'Stale test program: ' + case)
        for rel, sha in row['result'].get('source_sha256', {}).items():
            require(sha == digest(ROOT / rel), 'Stale live source: ' + case + ' / ' + rel)
        live_results.append(dict(case=case, passed=True, record=str(path.relative_to(ROOT)),
                                 record_sha256=digest(path), seconds=row['seconds']))
    require(load(RD/'live_tests/uncertain_commit.json')['result']['real_store_committed_but_unconfirmed'],
            'Post-commit ambiguity case missing')
    for case,field in [('checker_timeout','checker_processes'),('planner_timeout','monitor_processes')]:
        require(any(c['timed_out'] for c in load(RD/'live_tests'/f'{case}.json')['result'][field]),
                'Expected real process timeout missing: ' + case)
    save(RD / 'live_regression_summary.json', dict(status='PASS', cases=live_results,
         case_count=len(live_results), test_source_sha256=digest(test_source),
         evidence_scope='Fresh single-root protected-store runs, explicit operational fault injection, and rejected interfaces. Not empirical LLM measurements or universal filesystem refinement.'))

    demo_dir = args.demo_dir.resolve()
    require(demo_dir.is_relative_to(ROOT), 'Demo must be inside the project for portable evidence')
    demo = load(demo_dir / 'run.json')
    require(demo['status'] == 'admitted' and demo['confirmed_steps'] == 3, 'Live demonstration not admitted')
    require([s['action']['kind'] for s in demo['stage_attempts']] == ['register','verify','admit'], 'Wrong stage trace')
    require(demo['stage_attempts'][0]['action']['candidate'] == 1, 'Wrong candidate selected')
    require(demo['confirmed_state']['completed'] is True and demo['confirmed_state']['research_spent'] == 3,
            'Wrong confirmed completion/budget')
    require(demo['confirmed_state']['posterior_true'] == '1/2', 'Unexpected evidence inference')
    require(demo['planning_tree_work_total'] == 838 and demo['declared_planning_charge'] == '419/500',
            'Changed demo work accounting')
    require(demo['nominal_fees_debited_including_unconfirmed_attempts'] == 3, 'Wrong live debit count')
    for rel, sha in demo['source_sha256'].items():
        require(sha == digest(ROOT / rel), 'Stale demonstration source: ' + rel)
    expected_work = 0
    for call in demo['planner_monitor_processes']:
        require(call['returncode'] == 0 and not call['timed_out'], 'Demonstration planner call failed')
        require(call['entrypoint_sha256'] == digest(ROOT/'tools/LivePlannerMain.lean'), 'Stale demonstration executable source')
        require(call['request_sha256'] == digest(demo_dir/call['request']), 'Changed planner request')
        result = json.loads(call['stdout'])
        require(result['status'] == 'ok' and result['matched_external'], 'Unmatched demonstrated state')
        if call['mode'] == 'observe':
            require(result['new_planning_work'] == 0 and result['recommendation'] is None, 'Hidden replanning during replay')
        else:
            expected_work += result['new_planning_work']
    require(expected_work == 838, 'Search accounting mismatch')
    checks = demo['checker_processes']
    require([c['phase'] for c in checks] == ['verify','admit','admit'], 'Actual checker stages missing')
    for call in checks:
        require(call['returncode'] == 0 and not call['timed_out'], 'Live checker failure')
        require(call['request_file_sha256'] == digest(demo_dir/call['request_file']), 'Changed checker request')
        require(json.loads(call['stdout'])['accepted'] is True, 'Checker did not actually accept')
    store = load(demo_dir/'store/state.json')
    require(store['pending'] is None and len(store['admitted']) == 1, 'No physical retained admission')
    retained = next(iter(store['admitted'].values()))['ticket']
    require(retained['candidate_bytes'] == (ROOT/'examples/live/identity.proof.json').read_text(), 'Wrong actual proof bytes')
    require(retained['target_bytes'] == (ROOT/'examples/live/identity.target.json').read_text(), 'Wrong actual target bytes')
    live_demo = dict(status=demo['status'], confirmed_steps=3, selected_candidate=1,
        research_spend=3, tree_work=838, declared_planning_charge='419/500', checker_calls=3,
        planner_monitor_calls=len(demo['planner_monitor_processes']), posterior_true='1/2',
        measured=demo['measured'], record=str((demo_dir/'run.json').relative_to(ROOT)),
        record_sha256=digest(demo_dir/'run.json'),
        timing_boundary='Single local prototype execution; includes process startup, repeated checking and snapshot capture. Timing categories overlap and are not summed. No portable benchmark or optimal-cost guarantee.')
    save(RD/'live_demo_summary.json', live_demo)

    provenance = load(ROOT / 'SOURCE_PROVENANCE.json')
    require(args.baseline.is_file(), 'This fresh collector requires the frozen baseline ZIP')
    require(digest(args.baseline) == provenance['baseline_zip_sha256'], 'Baseline archive differs')
    unchanged = provenance['unchanged_inherited_modules']
    comparison = []
    with zipfile.ZipFile(args.baseline) as archive:
        require(archive.testzip() is None, 'Corrupt baseline ZIP')
        for rel in unchanged:
            matches = [n for n in archive.namelist() if n.endswith('/' + rel)]
            require(len(matches) == 1, 'Ambiguous baseline path: ' + rel)
            old = hashlib.sha256(archive.read(matches[0])).hexdigest()
            require(old == digest(ROOT / rel), 'Inherited source modified: ' + rel)
            comparison.append(dict(source=rel, baseline_sha256=old, current_sha256=old, identical=True))
    save(RD/'inherited_source_identity.json', comparison)
    counts = load(RD/'source_counts.json')
    require(counts['total_theorems'] == len(inventory) == 983, 'Count mismatch')
    require(counts['non_audit_modules'] == len(sources) == 96, 'Module count mismatch')
    require(counts['source_lines'] == sum(len(p.read_text().splitlines()) for p in sources), 'Line count mismatch')
    require(len(records) == 101 and len(negatives) == 40 and len(comparison) == 94, 'Incomplete final verification')
    # Include trusted entrypoints in the no-shortcuts scan, without inflating theorem counts.
    for src in (ROOT/'tools').glob('*.lean'):
        text = uncomment(src.read_text())
        require(not re.search(r'\b(sorry|native_decide)\b|^\s*(?:axiom|unsafe)\b|\bby\s+admit\b', text, re.M),
                'Forbidden trusted-entrypoint shortcut: ' + src.name)
    summary = dict(status='PASS', checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        version='0.19.0', lean='4.34.0-rc2', lean_commit='6a10ac8c22beadecabdbb0919c2b50214762f91d',
        mathlib='aeb72f1e9981b6d35b426b16dca7759be3e7ba06', **counts,
        local_compilations=len(records), full_axiom_declarations=len(names),
        axiom_dependencies=sorted(axioms), negative_tests_rejected=len(negatives),
        source_scan_hits=0, unchanged_inherited_module_count=len(comparison),
        dependencies_checked=len(dependency_checks),
        build_scope='Local build directory began empty; all final local source/output/log hashes checked. Pinned external binary caches retained, not rebuilt.',
        live_regression_cases=len(live_results), live_demonstration=live_demo,
        evidence_boundary='Kernel-checked monitor and conditional trace transport. Actual Python/filesystem operations independently tested, not universally formally refined. Operational aborts receive no inherited optimality/performance guarantee.',
        previous_evidence='All inherited versioned records are historical, not relabeled as current reruns.',
        environment=dict(platform=platform.platform(), python=platform.python_version()),
        evidence_dir='results/v0.19.0')
    save(RD/'final_audit.json', summary)
    save(ROOT/'AUDIT.json', summary)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
