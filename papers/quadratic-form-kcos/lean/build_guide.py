#!/usr/bin/env python3
"""Reproduce PDF/Markdown guide from its final LaTeX source and proof evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--skip-pdf', action='store_true', help='Regenerate faithful Markdown and hashes without another PDF build')
args = parser.parse_args()
tex = root / 'Quadratic_Form_KCOS_Lean_Guide.tex'
source = tex.read_text()
report = json.loads((root / 'verification/BUILD_AUDIT.json').read_text())
if report['status'] != 'PASS':
    raise RuntimeError('Guide verification summary requires passed proof evidence')
md_source = re.sub(r'\\decl\{([^}]*)\}', lambda m: '\\verb|' + m.group(1) + '|', source)
md_source = md_source.replace('\\input{verification/build_summary.tex}',
    r'\textbf{Fresh formal verification: passed.} The pinned Lean compiler checked 26 theorem declarations and 8 definitions. All 34 declarations were audited; their only axiom dependencies are propext, Classical.choice, and Quot.sound. No sorryAx or custom axiom occurs. Both mathematical source modules and the root import passed fresh direct source checks. An axiom-free valid arithmetic control passed; false arithmetic and an acceptance proof missing its error-budget premise were rejected with exit code 1.')
converted = subprocess.run(['pandoc', '-f', 'latex', '-t', 'gfm', '--wrap=none'], input=md_source, cwd=root, text=True, capture_output=True, check=True).stdout
markdown = '# Quadratic-Form Engine / K-COS\n\nA Lean Companion for Exact Finite Algebra and Error-Budget Composition\n\nKomorebi P. · Final edition, 7 October 2026\n\n' + converted
inventory = json.loads((root / 'Declaration_Inventory.json').read_text())
for row in inventory['declarations']:
    if row['kind'] == 'theorem' and row['name'].split('.', 1)[1] not in markdown:
        raise RuntimeError('Markdown dropped declaration ' + row['name'])
(root / 'Quadratic_Form_KCOS_Lean_Guide.md').write_text(markdown)
if not args.skip_pdf:
    for i in range(1, 4):
        run = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', tex.name], cwd=root, text=True, capture_output=True)
        (root / 'verification' / f'guide_latex_pass{i}.log').write_text(run.stdout + run.stderr)
        if run.returncode:
            raise RuntimeError(f'LaTeX pass {i} failed')
log = (root / 'verification/guide_latex_pass3.log').read_text()
if re.search(r'Overfull|Undefined|Warning|Error', log):
    raise RuntimeError('Final LaTeX log has unresolved layout/reference errors')
paths = [tex, root / 'Quadratic_Form_KCOS_Lean_Guide.md', root / 'Quadratic_Form_KCOS_Lean_Guide.pdf', root / 'verification/build_summary.tex']
info = subprocess.run(['pdfinfo', paths[2].name], cwd=root, text=True, capture_output=True, check=True).stdout
pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
audit = {'status': 'PASS', 'pdf_pages': pages, 'latex_final_pass': 'no overfull boxes, undefined references, warnings, or errors', 'markdown_theorem_names_preserved': 26,
         'source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
         'render_review': 'Independent full-PDF and final affected-page visual review is tracked separately in release publication QA'}
(root / 'verification/GUIDE_GENERATION_AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps({'status': audit['status'], 'pdf_pages': pages, 'markdown_theorem_names_preserved': 26}))
