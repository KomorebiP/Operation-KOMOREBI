#!/usr/bin/env python3
"""Rebuild the three authored PDFs from packaged sources in isolated directories."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
SPECS = [('traditional', 'Paper_VI_Traditional_Final'),
         ('visual_guide', 'Paper_VI_Visual_Guide_Final'),
         ('lean_guide', 'Paper_VI_Lean_Guide_Final')]


def atomic_copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    oldmtime = destination.stat().st_mtime if destination.exists() else 0
    descriptor, temporary = tempfile.mkstemp(dir=destination.parent,
                                             prefix='.' + destination.name + '.')
    os.close(descriptor)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
        stamp = max(time.time(), oldmtime + 2)
        os.utime(destination, (stamp, stamp))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent,
                                             prefix='.' + path.name + '.')
    oldmtime = path.stat().st_mtime if path.exists() else 0
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    os.replace(temporary, path)
    stamp = max(time.time(), oldmtime + 2)
    os.utime(path, (stamp, stamp))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true',
                        help='Compare text and page counts without replacing shipped PDFs.')
    parser.add_argument('--report', type=Path, help='Write a JSON verification report here.')
    args = parser.parse_args()
    report = {'status': 'PASS', 'check_only': args.check_only, 'engine': 'xelatex',
              'documents': [],
              'boundary': 'PDF compilation and extracted-text/page comparison. No Lean compiler or mathematical tests are invoked.'}
    failure = None
    with tempfile.TemporaryDirectory(prefix='komorebi-paper-vi-') as temporary:
        work = Path(temporary)
        rebuilt_documents = []
        for folder, stem in SPECS:
            output = work / folder
            builder = ROOT / 'editable' / folder / 'build.py'
            run = subprocess.run([sys.executable, str(builder), '--output-directory', str(output)],
                                 cwd=builder.parent, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if run.returncode:
                print(run.stdout[-12000:])
                failure = f'{folder}: build failed with exit status {run.returncode}'
                report['documents'].append({'document': stem, 'build_returncode': run.returncode})
                break
            rebuilt = output / (stem + '.pdf')
            if not rebuilt.is_file():
                failure = f'{folder}: expected PDF is missing'
                break
            record = {'document': stem, 'build_returncode': 0,
                      'pdf_bytes': rebuilt.stat().st_size,
                      'pdf_sha256': hashlib.sha256(rebuilt.read_bytes()).hexdigest()}
            if args.check_only:
                try:
                    import fitz
                except ImportError:
                    failure = 'PyMuPDF is required for --check-only text/page comparison.'
                    break
                before = ROOT / 'papers' / (stem + '.pdf')
                if not before.is_file():
                    failure = f'{folder}: shipped PDF is missing: {before}'
                    break
                record["shipped_pdf_sha256"] = hashlib.sha256(before.read_bytes()).hexdigest()
                record["pdf_byte_identical"] = before.read_bytes() == rebuilt.read_bytes()
                record["comparison_method"] = "Exact extracted text and page count; PDF byte identity reported separately."
                with fitz.open(before) as original, fitz.open(rebuilt) as fresh:
                    record['pages'] = len(fresh)
                    record['page_count_match'] = len(original) == len(fresh)
                    record['extracted_text_match'] = record['page_count_match'] and all(
                        a.get_text() == b.get_text() for a, b in zip(original, fresh))
                if not (record['page_count_match'] and record['extracted_text_match']):
                    failure = f'{folder}: rebuilt page count or extracted text differs'
            report['documents'].append(record)
            rebuilt_documents.append((stem, rebuilt))
            if failure:
                break
        if not failure and not args.check_only:
            # Publish only after every document has compiled successfully.
            for stem, rebuilt in rebuilt_documents:
                for folder in ('papers', 'publication/pdfs'):
                    atomic_copy(rebuilt, ROOT / folder / (stem + '.pdf'))
    if failure:
        report['status'] = 'FAIL'
        report['error'] = failure
    if args.report:
        write_report(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2))
    if failure:
        raise SystemExit(failure)


if __name__ == '__main__':
    main()
