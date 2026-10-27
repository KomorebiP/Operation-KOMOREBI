#!/usr/bin/env python3
"""Regenerate the 37 current visual figures in an isolated source tree.

The 24 core TikZ figures and 12 extension TikZ figures retain their exact
models. The one Matplotlib PDF retains its sampled illustration scope.
No manuscript prose, mathematical proofs, or Lean sources are modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true',
                        help='Compare regenerated figures without changing delivered assets.')
    args = parser.parse_args()
    environment = dict(os.environ, SOURCE_DATE_EPOCH='1791504000',
                       FORCE_SOURCE_DATE='1', MPLBACKEND='Agg')
    commands = ['source/generate_graphics.py', 'source/generate_extension_graphics.py',
                'source/annals_figure_source/generate_figures.py']
    with tempfile.TemporaryDirectory(prefix='paper-v-figure-models-') as temporary:
        stage = Path(temporary)
        shutil.copytree(ROOT / 'source', stage / 'source')
        (stage / 'graphics').mkdir()
        for command in commands:
            result = subprocess.run([sys.executable, command], cwd=stage,
                                    env=environment, text=True, capture_output=True)
            if result.returncode:
                print(result.stdout + result.stderr)
                raise SystemExit('Figure regeneration failed: ' + command)
        core_index = json.loads((stage / 'graphics/PLATE_INDEX.json').read_text())
        extension_index = json.loads((stage / 'graphics/EXTENSION_PLATE_INDEX.json').read_text())
        core = core_index.get('plates', core_index.get('generated_tikz'))
        if core is None:
            core = core_index['figures']
        extension = extension_index['generated_tikz']
        names = list(core) + list(extension)
        assert len(core) == 24 and len(extension) == 12
        generated_pdf = stage / 'source/figures/12_gibbs_comparison.pdf'
        shutil.copy2(generated_pdf, stage / 'graphics/annals_gibbs_comparison.pdf')
        names = [name + '.tex' for name in names] + ['annals_gibbs_comparison.pdf']
        records = []
        for name in names:
            generated = stage / 'graphics' / name
            current = ROOT / 'graphics' / name
            equal = generated.read_bytes() == current.read_bytes()
            if args.check_only and not equal:
                raise SystemExit('Regenerated figure differs: graphics/' + name)
            records.append({'path': 'graphics/' + name,
                            'sha256': digest(generated),
                            'equal_before_regeneration': equal})
            if not args.check_only:
                shutil.copy2(generated, current)
        report = {'status': 'PASS', 'regenerated_figure_count': len(records),
                  'core_exact_model_tikz_figures': 24,
                  'extension_exact_coordinate_tikz_figures': 12,
                  'sampled_matplotlib_vector_figures': 1,
                  'source_date_epoch': environment['SOURCE_DATE_EPOCH'],
                  'commands': commands, 'figures': records,
                  'model_scope': 'Exact formulas and rational/algebraic labels are preserved. '
                  'Trigonometric and Fourier curve samples remain illustrations. '
                  'Finite plotting output supplies no universal recovery or Lean proof.'}
        if not args.check_only:
            (ROOT / 'checks/FIGURE_REGENERATION_MONOGRAPH.json').write_text(
                json.dumps(report, indent=2) + '\n')
        print(f'PASS: {len(records)} figures regenerated from current source models.')


if __name__ == '__main__':
    main()
