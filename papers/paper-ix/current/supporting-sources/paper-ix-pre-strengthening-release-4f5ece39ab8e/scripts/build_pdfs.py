#!/usr/bin/env python3
"""Rebuild the three Paper IX companions in isolation and compare the shipped PDFs."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, tempfile

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only', action='store_true')
parser.add_argument('--report', type=Path)
parser.add_argument('--roles', nargs='+', choices=('traditional', 'visual_guide', 'lean_guide'),
                    default=('traditional', 'visual_guide', 'lean_guide'))
args = parser.parse_args()
specs = [('traditional', 'Paper_IX_Traditional_Final'),
         ('visual_guide', 'Paper_IX_Visual_Guide_Final'),
         ('lean_guide', 'Paper_IX_Lean_Guide_Final')]
records = []
with tempfile.TemporaryDirectory(prefix='komorebi-paper-ix-build-') as temp:
    for folder, stem in specs:
        if folder not in args.roles:
            continue
        stage = Path(temp) / folder
        # Figure PDFs are editable source assets and must be retained.
        shutil.copytree(root/'editable'/folder, stage,
                        ignore=shutil.ignore_patterns('__pycache__', 'qa', '*.aux', '*.log',
                                                     '*.out', '*.toc', '*.xdv', '*.synctex.gz'))
        (stage/(stem+'.pdf')).unlink(missing_ok=True)
        command = [sys.executable, 'build.py']
        if folder == 'visual_guide':
            command += ['--output-dir', '.']
        proc = subprocess.run(command, cwd=stage, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode:
            print(proc.stdout[-16000:])
            raise SystemExit(f'{folder}: isolated PDF build failed')
        fresh = stage/(stem+'.pdf')
        if not fresh.is_file():
            raise SystemExit(f'{folder}: expected PDF missing')
        shipped = root/'papers'/(stem+'.pdf')
        import fitz
        with fitz.open(shipped) as old, fitz.open(fresh) as new:
            record = dict(document=stem, pages=len(new),
                          page_count_match=len(old)==len(new),
                          extracted_text_match=len(old)==len(new) and
                            all(a.get_text()==b.get_text() for a,b in zip(old,new)),
                          byte_identical=shipped.read_bytes()==fresh.read_bytes(),
                          sha256=hashlib.sha256(fresh.read_bytes()).hexdigest())
        if args.check_only and not (record['page_count_match'] and record['extracted_text_match']
                                    and record['byte_identical']):
            raise SystemExit(f'{folder}: PDF bytes, page count or extracted text differs')
        if not args.check_only:
            shutil.copy2(fresh, shipped)
        records.append(record)
report = dict(status='PASS', check_only=args.check_only, documents=records,
              scope='Isolated PDF compilation with page count and extracted text comparison. No Lean execution or new mathematical validation.')
if args.report:
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
