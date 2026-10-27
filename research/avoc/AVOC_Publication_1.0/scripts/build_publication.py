"""Build the three publication PDFs without altering AVOC formal source."""
from pathlib import Path
import argparse
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output'
OUTPUT.mkdir(exist_ok=True)
DOCUMENTS = [('main', 'AVOC_Traditional_Final'), ('visual', 'AVOC_Visual_Guide_Final'), ('lean', 'AVOC_Lean_Companion_Final')]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--documents', nargs='+', choices=['main', 'visual', 'lean'], default=['main', 'visual', 'lean'])
    args = parser.parse_args()
    previous = ROOT / 'reviews' / 'latex_build.json'
    records = json.loads(previous.read_text()) if previous.exists() else []
    for source, name in DOCUMENTS:
        if source not in args.documents:
            continue
        for iteration in range(3):
            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                   f'-output-directory={OUTPUT}', f'-jobname={name}', f'{source}.tex']
            run = subprocess.run(cmd, cwd=ROOT / 'manuscripts', capture_output=True, text=True)
            (OUTPUT / f'{name}.pass{iteration + 1}.txt').write_text(run.stdout + run.stderr)
            if run.returncode:
                raise RuntimeError(f'{name}: pass {iteration + 1} failed; inspect retained log')
        log = (OUTPUT / f'{name}.log').read_text(errors='replace')
        overfull = re.findall(r'Overfull \\[hv]box[^\n]*', log)
        undefined = re.findall(r'LaTeX Warning: (?:Reference|Citation)[^\n]*undefined[^\n]*', log)
        missing = re.findall(r'Missing character:[^\n]*', log)
        records = [record for record in records if record['name'] != name]
        records.append({'name': name, 'pdf': str(OUTPUT / f'{name}.pdf'),
                        'passes': 3, 'overfull_boxes': overfull,
                        'undefined_references': undefined, 'missing_glyphs': missing})
        print(name, 'built', 'overfull', len(overfull), 'undefined', len(undefined), 'missing', len(missing))
    (ROOT / 'reviews' / 'latex_build.json').write_text(json.dumps(records, indent=2) + '\n')

if __name__ == '__main__':
    main()
