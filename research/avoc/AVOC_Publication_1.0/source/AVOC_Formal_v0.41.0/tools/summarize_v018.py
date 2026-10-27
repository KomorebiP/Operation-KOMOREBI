#!/usr/bin/env python3
"""Fail-closed collector for final v0.16 source, build, axiom and test evidence.

Run after verify_release.py and checks/test_costed_planner.py. No proof execution
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
RD = ROOT / 'results/v0.18.0'

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
                    default=Path('/mnt/data/AVOC_Formal_v0.17.0.zip'))
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

    regression = load(RD / 'planner_regression.json')
    require(regression['status'] == 'PASS', 'Planner regression failure')
    for source,sha in regression['source_hashes'].items():
        require(sha == digest(ROOT / source), 'Stale regression input: ' + source)
    execution = load(ROOT / regression['execution_record'])
    require(execution['returncode'] == 0 and not execution['timed_out'], 'Planner execution failed')
    require(execution['stdout_sha256'] == digest(RD / 'planner_stdout.jsonl'), 'Planner output changed')
    for stem in ['demo_success','demo_limited','demo_no_search','demo_rejection']:
        result = load(RD / (stem + '.json'))
        run = load(RD / (stem + '_run.json'))
        require(result['status'] == 'ok' and run['returncode'] == 0 and not run['timed_out'], 'Demo failed: '+stem)
        require(run['entrypoint_sha256'] == digest(ROOT/'tools/PlannerMain.lean'), 'Demo source changed')

    provenance = load(ROOT / 'SOURCE_PROVENANCE.json')
    unchanged = provenance['unchanged_inherited_modules']
    comparison = []
    if args.baseline.is_file():
        require(digest(args.baseline) == provenance['baseline_zip_sha256'], 'Baseline archive differs')
        with zipfile.ZipFile(args.baseline) as archive:
            require(archive.testzip() is None, 'Corrupt baseline ZIP')
            for rel in unchanged:
                hits = [n for n in archive.namelist() if n.endswith('/' + rel)]
                require(len(hits) == 1, 'Ambiguous baseline path: ' + rel)
                old = hashlib.sha256(archive.read(hits[0])).hexdigest()
                require(old == digest(ROOT / rel), 'Inherited source modified: ' + rel)
                comparison.append(dict(source=rel, baseline_sha256=old, current_sha256=old, identical=True))
        save(RD / 'inherited_source_identity.json', comparison)
        baseline_mode = 'fresh byte comparison to frozen v0.17 ZIP'
    else:
        saved = load(RD / 'inherited_source_identity.json')
        require({x['source'] for x in saved} == set(unchanged), 'Incomplete inherited evidence')
        for x in saved:
            require(x['baseline_sha256'] == digest(ROOT / x['source']), 'Inherited source changed')
        comparison = saved
        baseline_mode = 'current bytes checked against delivered baseline-hash record; ZIP not rechecked in this rerun'
    counts = load(RD / 'source_counts.json')
    require(counts['total_theorems'] == len(inventory), 'Count mismatch')
    require(counts['non_audit_modules'] == len(sources), 'Module count mismatch')
    require(counts['source_lines'] == sum(len(p.read_text().splitlines()) for p in sources), 'Line count mismatch')
    summary = dict(status='PASS', checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   version='0.18.0', lean='4.34.0-rc2', lean_commit='6a10ac8c22beadecabdbb0919c2b50214762f91d',
                   mathlib='aeb72f1e9981b6d35b426b16dca7759be3e7ba06', **counts,
                   local_compilations=len(records), full_axiom_declarations=len(names),
                   axiom_dependencies=sorted(axioms), negative_tests_rejected=len(negatives),
                   source_scan_hits=0, unchanged_inherited_module_count=len(comparison),
                   inherited_verification_scope=baseline_mode,
                   build_scope='Local build directory began empty. All final current-source local targets have successful records; unchanged inherited targets were built first and finalized new targets plus aggregate afterward. External dependency caches retained, not rebuilt.',
                   planner_regression={k:v for k,v in regression.items() if k != 'source_hashes'},
                   legacy_filesystem_tests='Inherited historical evidence retained, not rerun in v0.18; new tests concern the planner and modeled workflow.',
                   environment=dict(platform=platform.platform(), python=platform.python_version()),
                   evidence_dir='results/v0.18.0')
    save(ROOT / 'AUDIT.json', summary)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
