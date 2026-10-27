#!/usr/bin/env python3
"""Rebuild the book, then audit its assembly and produce the design preview.

The default uses supplied components: prepare -> assemble -> audit -> preview.
Optional source compilation preserves the selected original readers. No Lean
project, mathematical computation, or figure generator is run. A rebuilt PDF
requires new hash-bound editorial and visual reviews before it can be packaged.
"""
from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-sources', action='store_true',
                        help='Recompile the available edited LaTeX components before assembling the book.')
    args = parser.parse_args()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

    def run(path, *command_args):
        subprocess.run([sys.executable, '-B', str(ROOT/path), *map(str, command_args)],
                       cwd=ROOT, env=env, check=True)

    if args.from_sources:
        run(Path('source_i_iv/rebuild_all.py'))
        run(Path('source_v_viii/build_all.py'))
        run(Path('source_ix_xii/typeset_ix_x.py'))
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        rebuilt = ROOT/'source_ix_xii'/('rebuild_'+stamp)
        run(Path('source_ix_xii/rebuild_xi_xii.py'), '--output', rebuilt)
        record = json.loads((ROOT/'component_builds.json').read_text())
        for component in record['components']:
            if component['paper'] in ('XI', 'XII') and component['build_kind'] == 'source_retypeset':
                path = rebuilt/component['paper']/component['baseline_filename']
                if not path.is_file():
                    raise FileNotFoundError(path)
                component['output_pdf'] = str(path.relative_to(ROOT))
        (ROOT/'component_builds.json').write_text(json.dumps(record, indent=2)+'\n')

    run(Path('prepare_book.py'))
    spec = json.loads((ROOT/'book/build_spec.json').read_text())
    if spec.get('schema') != 'realization-calculus.book-spec/3':
        raise SystemExit('The rebuilt volume must use the current book reading sequence.')
    run(Path('assemble_monograph.py'))
    run(Path('audit_monograph.py'), '--render-samples')
    run(Path('make_preview.py'))
    print(json.dumps({'status': 'ASSEMBLED_AND_AUDITED',
                      'pages': spec['expected_total_pages'],
                      'review_boundary': 'The structural audit and preview do not create a new editorial or visual review. Packaging requires those reviews to identify the rebuilt PDF bytes.',
                      'fresh_lean_or_scientific_execution': False}, indent=2))


if __name__ == '__main__':
    main()
