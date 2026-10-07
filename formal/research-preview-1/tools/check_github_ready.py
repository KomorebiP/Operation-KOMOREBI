#!/usr/bin/env python3
"""Check the sealed GitHub export and conservative workflow policy. Does not run Lean."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIRS = {'.git', '.lake', '__pycache__', '.venv', '_reports'}

def is_generated(path: Path) -> bool:
    return bool(set(path.parts) & GENERATED_DIRS) or (
        path.parts[:2] == ('padic', 'results') and path.as_posix() != 'padic/results/.gitkeep')

def workflow_errors(text: str, pins: dict[str, dict[str, str]]) -> list[str]:
    errors = []
    if 'pull_request_target' in text:
        errors.append('Privileged pull_request_target trigger is not permitted.')
    if re.search(r'\$\{\{\s*secrets\.', text):
        errors.append('Repository secrets are outside this preparation workflow.')
    if not re.search(r'(?m)^permissions:\s*\n  contents: read\s*$', text):
        errors.append('Workflow must declare read-only contents permission.')
    if re.search(r'(?m)^\s+[A-Za-z-]+:\s*write\s*$', text):
        errors.append('Write permission is not permitted.')
    if 'continue-on-error:' in text:
        errors.append('A failing verification step must not be converted into success.')
    for action, ref in re.findall(r'(?m)^\s*(?:-\s*)?uses:\s*([^\s@]+)@([^\s#]+)', text):
        if action not in pins or ref != pins[action]['sha'] or not re.fullmatch(r'[0-9a-f]{40}', ref):
            errors.append(f'Unverified action pin: {action}@{ref}')
    if 'persist-credentials: false' not in text:
        errors.append('Checkout must not persist credentials.')
    if 'timeout-minutes:' not in text:
        errors.append('Workflow lacks an explicit execution limit.')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-git', action='store_true', help='Also require the Git tracked file set and commit identities to match.')
    args = parser.parse_args()
    errors: list[str] = []
    checks = 0
    def check(ok: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not ok: errors.append(msg)
    try:
        prior = subprocess.run([sys.executable, '-B', str(ROOT/'tools/check_release.py')], cwd=ROOT,
                               text=True, capture_output=True, timeout=180)
        source = json.loads(prior.stdout)
        check(prior.returncode == 0 and source.get('status') == 'PASS', 'Underlying release check failed: '+str(source.get('errors')))
        ledger = json.loads((ROOT/'FILE_HASHES.json').read_text())
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not is_generated(p.relative_to(ROOT))}
        expected = set(ledger) | {'FILE_HASHES.json'}
        check(actual == expected, 'Sealed export differs: missing='+str(sorted(expected-actual))+'; extra='+str(sorted(actual-expected)))
        for name in sorted(actual):
            p=ROOT/name
            check(not p.is_symlink(), 'Export contains a symlink: '+name)
            check(p.stat().st_size < 10*1024*1024, 'Unexpected large artifact: '+name)
            check(p.suffix.lower() not in {'.zip','.bundle','.olean','.ilean','.ttf','.otf','.woff','.woff2','.pem','.key','.exe','.dll'}, 'Unapproved binary/archive/key file: '+name)
            check(not p.name.startswith('.env'), 'Environment file is not an approved export: '+name)
        config=json.loads((ROOT/'REPOSITORY.json').read_text())
        check(config['visibility_for_initial_upload']=='private', 'Initial upload must remain private.')
        check(config['owner_login']=='KomorebiP' and config['owner_id']==52508850, 'Owner identity differs.')
        check(config['published'] is False and config['license_selected'] is False, 'Preparation must not assert publication or select a license.')
        baseline=json.loads((ROOT/'provenance/RC1_BASELINE.json').read_text())
        modified=[]
        for name,digest in baseline['files'].items():
            if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
                modified.append(name)
        check(set(modified) <= {'README.md','.gitignore','FILE_HASHES.json','REPRODUCE.md','PUBLICATION_STATUS.md'}, 'Unexpected RC1 change: '+str(modified))
        pins=json.loads((ROOT/'.github/action-pins.json').read_text())['actions']
        workflows=sorted((ROOT/'.github/workflows').glob('*.yml'))
        check({p.name for p in workflows}=={'artifact-checks.yml','reference-audit.yml','lean-replay.yml'},'Workflow set differs.')
        for p in workflows:
            for error in workflow_errors(p.read_text(), pins): check(False,p.name+': '+error)
            if p.name != 'artifact-checks.yml':
                check('  workflow_dispatch:' in p.read_text() and not re.search(r'(?m)^  (push|pull_request|schedule):',p.read_text()), 'Expensive evidence workflows must remain manual.')
        lean=(ROOT/'.github/workflows/lean-replay.yml').read_text()
        check('tools/replay_lean.py --clean' in lean,'Missing clean proof replay.')
        check('tools/check_proof_receipt.py padic/results/github_lean_replay' in lean,
              'Missing full fresh-receipt validation.')
        check('tools/record_workflow_context.py' in lean and 'steps.bootstrap.outcome' in lean
              and 'steps.proof_replay.outcome' in lean, 'Missing bootstrap/replay outcome record.')
        check("use-github-cache: 'false'" in lean,'GitHub project cache must remain disabled for the fresh route.')
        link_count=0
        for p in list(ROOT.glob('*.md'))+list((ROOT/'github').glob('*.md'))+list((ROOT/'.github').rglob('*.md')):
            for match in re.finditer(r'\[[^\]\n]+\]\(([^\s]+)\)',p.read_text()):
                value=match.group(1); parsed=urlsplit(value)
                if parsed.scheme or value.startswith('#'): continue
                target=(p.parent/unquote(parsed.path)).resolve()
                check(target.is_relative_to(ROOT) and target.is_file(),'Broken local documentation link: '+p.name+': '+value)
                link_count+=1
        # Narrow secret-pattern scan, not an independent privacy/rights review.
        suspicious=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
        for name in sorted(actual):
            try: txt=(ROOT/name).read_text(encoding='utf-8')
            except UnicodeDecodeError: continue
            check(not suspicious.search(txt),'Possible secret in '+name)
        if args.check_git:
            from create_private_repo import require_identity_history
            proc=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
            tracked=set(filter(None,proc.stdout.decode().split('\0')))
            check(tracked==expected,'Git tracked files differ from sealed export.')
            history=subprocess.check_output(['git','log','--all','--format=%an%x00%ae%x00%cn%x00%ce'],cwd=ROOT,text=True)
            require_identity_history(history)
            check(True,'Git identity audit')
        result={'status':'PASS' if not errors else 'FAIL','checks':checks,'files':len(actual),
                'source_checks':source.get('source_checks'),'production_modules':92,
                'workflows':len(workflows),'local_links_checked':link_count,'modified_rc1_files':modified,
                'errors':errors,'scope':'Sealed artifact/source identity, workflow policy, local documentation, and narrow secret screening. NOT a Lean run, GitHub-hosted workflow result, or publication/privacy clearance.'}
        print(json.dumps(result,indent=2))
        return int(bool(errors))
    except (OSError,ValueError,KeyError,RuntimeError,subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'FAIL','errors':[str(exc)],'scope':'Preparation check did not complete.'},indent=2))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
