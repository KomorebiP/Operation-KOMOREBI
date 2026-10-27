#!/usr/bin/env python3
"""Build Paper XII in an isolated directory with deterministic PDF metadata."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, shutil, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
NAME = 'Paper_XII_Traditional_Final'
EPOCH = '1791244800'  # 2026-10-06 00:00:00 UTC

def run(command: list[str], work: pathlib.Path, env: dict[str, str], logs: list[str]) -> None:
    result = subprocess.run(command, cwd=work, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    logs.append('$ ' + ' '.join(command) + '\n' + result.stdout)
    if result.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(command) + '\n' + result.stdout[-7000:])

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True,
                        help='A new or empty directory; all compiler work is isolated and temporary.')
    args = parser.parse_args()
    target = args.output_dir.resolve()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        parser.error('--output-dir must be a new or empty directory')
    needed = ['pdflatex', 'bibtex', 'pdftotext', 'pdfinfo']
    missing = [x for x in needed if not shutil.which(x)]
    if missing:
        parser.error('Missing Linux prerequisites: ' + ', '.join(missing) + '; see README.md')
    target.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE='1', TZ='UTC', LC_ALL='C',
               TEXINPUTS='.:', BIBINPUTS='.:', BSTINPUTS='.:')
    logs: list[str] = []
    with tempfile.TemporaryDirectory(prefix='paper-xii-build-') as temp:
        work = pathlib.Path(temp)
        for suffix in ['tex', 'bib', 'bbl']:
            shutil.copyfile(ROOT / f'{NAME}.{suffix}', work / f'{NAME}.{suffix}')
        shutil.copytree(ROOT / 'figures', work / 'figures')
        latex = ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode',
                 '-halt-on-error', '-file-line-error', f'{NAME}.tex']
        run(latex, work, env, logs)
        run(['bibtex', NAME], work, env, logs)
        run(latex, work, env, logs)
        run(latex, work, env, logs)
        log = (work / f'{NAME}.log').read_text(errors='replace')
        forbidden = ['LaTeX Warning: There were undefined references', 'Citation ',
                     'Reference ', 'Rerun to get cross-references right']
        if any(token in log and ('undefined' in log or 'Rerun' in log) for token in forbidden):
            raise RuntimeError('Unresolved citations or cross-references in final LaTeX log')
        for suffix in ['pdf', 'bbl']:
            shutil.copyfile(work / f'{NAME}.{suffix}', target / f'{NAME}.{suffix}')
        (target / f'{NAME}.log').write_text(log)
    subprocess.run(['pdftotext', '-enc', 'UTF-8', '-layout', str(target / f'{NAME}.pdf'),
                    str(target / f'{NAME}.txt')], env=env, check=True)
    info = subprocess.run(['pdfinfo', str(target / f'{NAME}.pdf')], env=env, text=True,
                          stdout=subprocess.PIPE, check=True).stdout
    (target / 'PDF_INFO.txt').write_text(info)
    (target / 'BUILD_LOG.txt').write_text('\n'.join(logs))
    pages = int(next(x.split(':', 1)[1].strip() for x in info.splitlines() if x.startswith('Pages:')))
    pdf = target / f'{NAME}.pdf'
    text = target / f'{NAME}.txt'
    report = {'document': NAME, 'source_date_epoch': int(EPOCH), 'pages': pages,
              'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
              'text_sha256': hashlib.sha256(text.read_bytes()).hexdigest(),
              'isolated_build': True, 'latex_passes': 3, 'bibtex': True,
              'figure_count': len(list((ROOT / 'figures').glob('*.pdf')))}
    (target / 'BUILD_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
