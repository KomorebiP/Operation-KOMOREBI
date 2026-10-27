#!/usr/bin/env python3
"""Build the consolidated Paper IX PDF with a local TeX installation."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which('pdflatex')
    if compiler is None:
        raise SystemExit('pdflatex is required to build this manuscript.')
    main_file = 'Paper_IX_Consolidated.tex'
    def source_hashes():
        return {str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(source.rglob('*.tex'))}
    before = source_hashes()
    runs = []
    for index in range(1, 4):
        command = [compiler, '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', '-output-directory=' + str(output), main_file]
        result = subprocess.run(command, cwd=source, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=120)
        (output / ('latex_pass_' + str(index) + '.txt')).write_text(result.stdout)
        runs.append({'pass': index, 'exit_code': result.returncode, 'command': command})
        if result.returncode != 0:
            print(result.stdout[-10000:])
            (output / 'BUILD_REPORT.json').write_text(json.dumps({'status':'FAIL', 'runs':runs},indent=2)+'\n')
            raise SystemExit(result.returncode)
    log = (output / 'Paper_IX_Consolidated.log').read_text(errors='replace')
    warnings = [line for line in log.splitlines() if any(term in line for term in
        ['Overfull', 'Underfull', 'undefined', 'multiply defined', 'Missing character', 'Rerun to get', 'Rerun LaTeX'])]
    hard_issues = [line for line in warnings if any(term in line for term in
        ['Overfull', 'undefined', 'multiply defined', 'Missing character', 'Rerun to get', 'Rerun LaTeX'])]
    report = {'status':'PASS' if not hard_issues else 'REVIEW_REQUIRED',
              'runs':runs, 'warnings':warnings, 'hard_issues':hard_issues,
              'pdf':str(output / 'Paper_IX_Consolidated.pdf'),
              'pdf_sha256':hashlib.sha256((output / 'Paper_IX_Consolidated.pdf').read_bytes()).hexdigest(),
              'source_hashes':before, 'sources_unchanged_during_build':before == source_hashes()}
    if not report['sources_unchanged_during_build']:
        report['status'] = 'SOURCE_CHANGED_DURING_BUILD'
    (output / 'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
