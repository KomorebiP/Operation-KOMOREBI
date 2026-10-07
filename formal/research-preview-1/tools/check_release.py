#!/usr/bin/env python3
"""Read-only release checks. A PASS is not a Lean proof run or publication approval."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('README.md', 'THEOREM_NOTE.md', 'FUTURE_RESEARCH.md', 'CLAIMS.md',
            'ATTRIBUTION.md', 'REPRODUCE.md', 'REVIEW_GUIDE.md', 'KNOWN_LIMITATIONS.md',
            'PUBLICATION_STATUS.md', 'RELEASE_NOTES.md', 'RELEASE.json', 'CITATION.cff',
            'CONTRIBUTING.md', 'RIGHTS.md', 'ANNOUNCEMENT.md')

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unsealed', action='store_true',
                        help='Allow a development tree without FILE_HASHES.json.')
    args = parser.parse_args()
    errors: list[str] = []
    checks = 0
    def check(ok: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(message)
    for name in REQUIRED:
        check((ROOT / name).is_file(), f'Missing release document: {name}')
    if errors:
        print(json.dumps({'status': 'FAIL', 'errors': errors}, indent=2))
        return 1
    proc = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/check_candidate.py')],
                          cwd=ROOT, text=True, capture_output=True, timeout=120)
    try:
        source = json.loads(proc.stdout)
    except json.JSONDecodeError:
        source = {'status': 'FAIL', 'errors': ['Malformed source checker output', proc.stderr]}
    check(proc.returncode == 0 and source.get('status') == 'PASS',
          'Source/evidence checker failed: ' + str(source.get('errors')))
    release = json.loads((ROOT / 'RELEASE.json').read_text(encoding='utf-8'))
    check(release['version'] == 'research-preview-1-rc1', 'Unexpected release identifier')
    check(release['published'] is False, 'RC metadata must not claim publication')
    check(release['proof_source_changed'] is False, 'Frozen mathematical checkpoint changed')
    check(release['version'] in (ROOT / 'CITATION.cff').read_text(), 'Citation version differs')
    claims = json.loads((ROOT / 'claims.json').read_text())
    claim_text = (ROOT / 'CLAIMS.md').read_text()
    for item in claims:
        check(f"## {item['id']} " in claim_text, f"Missing public claim {item['id']}")
        for anchor in item['anchors']:
            check(anchor['declaration'] in claim_text,
                  f"Unlisted public anchor {anchor['declaration']}")
    links_checked = 0
    # Only the maintained public documents are link-reviewed here. Historical logs stay immutable.
    for doc in ROOT.glob('*.md'):
        text = doc.read_text(encoding='utf-8')
        check(text.count('```') % 2 == 0, f'Unbalanced fenced code: {doc.name}')
        for match in re.finditer(r'\[[^\]\n]+\]\(([^\s]+)\)', text):
            url = match.group(1)
            parts = urlsplit(url)
            if parts.scheme or url.startswith('#'):
                continue
            path = (doc.parent / unquote(parts.path)).resolve()
            check(path.is_relative_to(ROOT) and path.is_file(),
                  f'Broken/escaping local link in {doc.name}: {url}')
            if parts.fragment.startswith('L') and parts.fragment[1:].isdigit() and path.is_file():
                check(int(parts.fragment[1:]) <= len(path.read_text().splitlines()),
                      f'Invalid line anchor: {url}')
            links_checked += 1
        check(not re.search(r'\b(?:TODO|FIXME|TBD)\b|sandbox:/|/mnt/data/', text),
              f'Unresolved/local-only public prose in {doc.name}')
    future = (ROOT / 'FUTURE_RESEARCH.md').read_text()
    check('None of the targets below is claimed as a result' in future,
          'Future agenda lost its status boundary')
    check('## 7. Future research' in (ROOT / 'THEOREM_NOTE.md').read_text(),
          'Technical note lacks its future-research section')
    ledger_path = ROOT / 'FILE_HASHES.json'
    ledger_count = 0
    if ledger_path.is_file():
        ledger = json.loads(ledger_path.read_text())
        for name, digest in ledger.items():
            rel = Path(name)
            check(not rel.is_absolute() and '..' not in rel.parts, f'Unsafe ledger path: {name}')
            path = ROOT / rel
            check(path.is_file(), f'Missing sealed file: {name}')
            if path.is_file():
                check(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                      f'Sealed file changed: {name}')
            ledger_count += 1
    else:
        check(args.unsealed, 'Unsealed release: FILE_HASHES.json is missing')
    result = {'status': 'PASS' if not errors else 'FAIL', 'release': release['version'],
              'checks': checks, 'source_checks': source.get('checks'),
              'source_status': source.get('status'), 'local_links_checked': links_checked,
              'sealed_files_checked': ledger_count, 'errors': errors,
              'scope': 'Artifact identity, claim anchors, document links, and retained evidence consistency. NOT a Lean run, novelty audit, or publication approval.'}
    print(json.dumps(result, indent=2))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
