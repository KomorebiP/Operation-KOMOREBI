#!/usr/bin/env python3
"""Regenerate the reader bibliography from the corrected source using BibTeX plain."""
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
def main():
    source = ROOT/'manuscript/references.bib'
    destination = ROOT/'manuscript/references.tex'
    with tempfile.TemporaryDirectory(prefix='paper-x-bibliography-') as directory:
        work = Path(directory)
        shutil.copyfile(source, work/'references.bib')
        (work/'references.aux').write_text('\\relax\n\\citation{*}\n\\bibstyle{plain}\n\\bibdata{references}\n')
        run = subprocess.run(['bibtex','references'], cwd=work, capture_output=True, text=True, timeout=60)
        print(run.stdout, end='')
        if run.returncode:
            print(run.stderr, end='')
            raise SystemExit(run.returncode)
        data = (work/'references.bbl').read_bytes()
        if data.count(b'\\bibitem{') != 23:
            raise SystemExit('The bibliography must preserve all 23 original entry keys.')
        destination.write_bytes(data)
        print(json.dumps({'entries':23,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render_source_sha256':hashlib.sha256(data).hexdigest()}))
if __name__ == '__main__':
    main()
