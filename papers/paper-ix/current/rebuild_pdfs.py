#!/usr/bin/env python3
"""Build the reading set in an empty external directory without changing the release.

Requires installed TeX fonts, pdfLaTeX, XeLaTeX and PyMuPDF. The comparison checks
exact per-page extracted text and page counts. PDF byte identity and equality
after trailer-ID normalization are reported separately. No Lean process runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ID = re.compile(rb'(/ID\s*\[\s*<)[0-9a-fA-F]{32}(>\s*<)[0-9a-fA-F]{32}(>\s*\])')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def without_id(data: bytes) -> bytes:
    return ID.sub(lambda match: match[1] + b'0' * 32 + match[2] + b'0' * 32 + match[3], data)


def main() -> None:
    documents = json.loads((ROOT / 'publication/documents.json').read_text())
    names = [row['file_name'] for row in documents if row['kind'] != 'essay']
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, help='An empty directory outside this release.')
    parser.add_argument('--document', choices=names, action='append',
                        help='Build only this reader. May be repeated. Default: all three readers.')
    parser.add_argument('--build-only', action='store_true',
                        help='Build a candidate without comparing it to the currently frozen PDFs.')
    args = parser.parse_args()
    selected = [name for name in names if not args.document or name in args.document]
    dest = args.work_dir.resolve() if args.work_dir else Path(tempfile.mkdtemp(prefix='paper_ix_rebuild_'))
    if dest == ROOT or dest.is_relative_to(ROOT):
        parser.error('use a build directory outside this frozen release')
    if dest.exists() and any(dest.iterdir()):
        parser.error('build directory must be empty')
    dest.mkdir(parents=True, exist_ok=True)
    for name in ('sources', 'figures', 'tools'):
        shutil.copytree(ROOT / name, dest / name,
                        ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
    (dest / 'publication/pdfs').mkdir(parents=True)
    shutil.copytree(ROOT / 'publication/house_style', dest / 'publication/house_style')
    for name in ('build_publication.py', 'documents.json'):
        shutil.copy2(ROOT / 'publication' / name, dest / 'publication' / name)
    argv = [sys.executable, '-B', str(dest / 'publication/build_publication.py'), *selected]
    run = subprocess.run(argv, cwd=dest, capture_output=True)
    (dest / 'BUILD_TRANSCRIPT.txt').write_bytes(run.stdout + run.stderr)
    report = {'schema': 'komorebi.paper-ix.pdf-replay/2',
              'status': 'FAIL', 'work_directory': str(dest),
              'build_only': args.build_only, 'argv': argv,
              'build_returncode': run.returncode, 'documents': [],
              'scope': 'Source-to-PDF compilation. Exact per-page extracted-text and page-count '
                       'comparison is separate from byte/ID-normalized comparison. '
                       'No fresh Lean execution or mathematical proof audit.'}
    if run.returncode == 0:
        import fitz
        for name in selected:
            frozen = ROOT / 'publication/pdfs' / name
            rebuilt = dest / 'publication/pdfs' / name
            data = rebuilt.read_bytes()
            row = {'file': name, 'rebuilt_sha256': digest(data), 'rebuilt_bytes': len(data)}
            with fitz.open(rebuilt) as fresh:
                row['pages'] = len(fresh)
                if not args.build_only:
                    old_data = frozen.read_bytes()
                    row.update(frozen_sha256=digest(old_data), frozen_bytes=len(old_data),
                               byte_identical=old_data == data,
                               identical_except_trailer_id=without_id(old_data) == without_id(data))
                    with fitz.open(frozen) as original:
                        row['page_count_match'] = len(original) == len(fresh)
                        row['extracted_text_match'] = row['page_count_match'] and all(
                            old.get_text() == new.get_text() for old, new in zip(original, fresh))
                        row['differing_text_pages'] = [
                            i + 1 for i, (old, new) in enumerate(zip(original, fresh))
                            if old.get_text() != new.get_text()]
            report['documents'].append(row)
        if args.build_only:
            report['status'] = 'BUILT_WITHOUT_COMPARISON'
        elif all(row['page_count_match'] and row['extracted_text_match']
                 for row in report['documents']):
            report['status'] = 'PASS'
    else:
        report['error'] = 'Compilation failed; see BUILD_TRANSCRIPT.txt in the work directory.'
    (dest / 'REBUILD_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(report['status'] == 'FAIL')


if __name__ == '__main__':
    main()
