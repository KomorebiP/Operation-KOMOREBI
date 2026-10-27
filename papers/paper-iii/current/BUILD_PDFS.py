#!/usr/bin/env python3
"""Build current Paper III PDFs from active authored sources, in a working copy.

Requires Python 3.11+, PyMuPDF, ReportLab, XeLaTeX, pdfLaTeX, BibTeX and the
fonts in metadata/REPRODUCTION.md. This does not run Lean or exact math tests.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def update_crosswalk(aux):
    target = ROOT / 'guides/lean/generated/traditional_crosswalk.tex'
    text = target.read_text()
    labels = {m[0]: (m[1], m[2]) for m in re.findall(
        r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}', aux.read_text())}
    seen = []

    def replace(match):
        label, kind = match.group(1), match.group(2)
        if label not in labels:
            raise RuntimeError('Missing compiled crosswalk label: ' + label)
        number, page = labels[label]
        seen.append(label)
        return '\\code{' + label + '} & ' + kind + ' ' + number + ', p.~' + page

    text = re.sub(r'\\code\{([^}]+)\} & ([A-Za-z ]+) [^,]+, p\.~[^ \\]+', replace, text)
    if not seen:
        raise RuntimeError('The monograph crosswalk matched no rows')
    target.write_text(text)
    record = {'release_version': '1.0.0',
              'scope': 'Navigation from the actual final TeX auxiliary file; not a formal coverage claim.',
              'row_count': len(seen), 'aux_sha256': sha(aux), 'crosswalk_sha256': sha(target),
              'traditional_source_files': {
                  str(p.relative_to(ROOT / 'manuscript')): sha(p)
                  for p in [ROOT / 'manuscript/Paper_III_Traditional_Final.tex',
                            *sorted((ROOT / 'manuscript/chapters').glob('*.tex'))]}}
    target.with_name('traditional_crosswalk_provenance.json').write_text(json.dumps(record, indent=2) + '\n')


def write_current_receipts():
    record = json.loads((ROOT / 'formal/verification/FINAL_VERIFICATION_SUMMARY.json').read_text())
    if record.get('status') != 'PASS':
        raise RuntimeError('Current formal verification is not marked PASS')
    text = (
        'The final release compiled \\textbf{' + str(record['production_module_count']) +
        ' production modules} from an initially empty owned object directory. '
        'The compiled ownership audit recorded \\textbf{' + str(record['owned_declarations']) +
        ' owned declarations}. The clean kernel replay accepted \\textbf{' +
        str(record['replayed_logical_declarations']) +
        ' logical declarations}, with \\textbf{' + str(record['generated_runtime_helpers']) +
        ' generated runtime helpers} separately inventoried. '
        'The full build, ownership audit, kernel replay, and control suite all passed.\n\n'
        'The exact compiler is Lean \\code{4.34.0-rc2}, commit '
        '\\code{6a10ac8c22beadecabdbb0919c2b50214762f91d}. Mathlib is pinned at '
        '\\code{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. '
        'The machine-readable summary is '
        '\\code{formal/verification/FINAL_VERIFICATION_SUMMARY.json}.\n')
    (ROOT / 'guides/lean/generated/current_receipts.tex').write_text(text)


def update_visual_locators(aux):
    display = {'section': 'Section', 'theorem': 'Theorem', 'proposition': 'Proposition',
               'lemma': 'Lemma', 'corollary': 'Corollary', 'definition': 'Definition',
               'roadmap': 'Formalization target'}
    locators = {}
    for line in aux.read_text().splitlines():
        head = re.match(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}', line)
        dest = re.search(r'\{(section|theorem|proposition|lemma|corollary|definition|roadmap)\.[^{}]+\}\{\}\}$', line)
        if head and dest and '@cref' not in head[1]:
            locators[(display[dest[1]], head[2])] = head[3]
    changed, details = False, []
    pattern = r'(Formalization target|Definition|Lemma|Theorem|Proposition|Corollary|Section)\s+(\d+(?:\.\d+)?)\s+\(p\.\s*(\d+)\)'
    for relative in ['manuscript/visual_atlas.tex', 'guides/visual/source/pages_final.tex',
                     'guides/visual/source/reading_bridge.tex']:
        path = ROOT / relative
        before = path.read_text()
        def replace(match):
            key = (match[1], match[2])
            if key not in locators:
                raise RuntimeError('Missing visual locator: ' + str(key))
            if match[3] != locators[key]:
                details.append({'file': relative, 'kind': match[1], 'number': match[2],
                                'old_page': match[3], 'new_page': locators[key]})
            return match[1] + ' ' + match[2] + ' (p. ' + locators[key] + ')'
        after = re.sub(pattern, replace, before)
        if before != after:
            path.write_text(after)
            if relative.startswith('manuscript/'):
                changed = True
    return changed, details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = (args.build_dir or Path(tempfile.mkdtemp(prefix='paper-iii-pdfs-'))).resolve()
    build.mkdir(parents=True, exist_ok=True)
    publication = ROOT / 'publication'
    publication.mkdir(exist_ok=True)
    evidence = ROOT / 'evidence/typesetting'
    evidence.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment['SOURCE_DATE_EPOCH'] = str(int(datetime.datetime(
        2026, 10, 20, tzinfo=datetime.timezone.utc).timestamp()))
    environment['FORCE_SOURCE_DATE'] = '1'
    runs = []

    def run(command, cwd, label):
        proc = subprocess.run(command, cwd=cwd, env=environment, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log = evidence / (label + '.log')
        log.write_text(proc.stdout)
        runs.append({'label': label, 'exit_code': proc.returncode,
                     'log': str(log.relative_to(ROOT)), 'log_sha256': sha(log)})
        if proc.returncode:
            print(proc.stdout[-10000:])
            raise RuntimeError('Build failed: ' + label)
        print(label + ': PASS', flush=True)

    write_current_receipts()
    aux = build / 'traditional/Paper_III_Traditional_Final.aux'
    locator_changes = []
    for iteration in range(3):
        run([sys.executable, 'build.py', '--output-directory', str(build / 'traditional')],
            ROOT / 'manuscript', 'traditional' if iteration == 0 else 'traditional_locators_' + str(iteration))
        changed, details = update_visual_locators(aux)
        locator_changes.extend(details)
        if not changed:
            break
    else:
        raise RuntimeError('Visual monograph locators did not stabilize')
    (evidence / 'VISUAL_LOCATOR_UPDATES.json').write_text(json.dumps({
        'status': 'PASS', 'aux_sha256': sha(aux), 'updates': locator_changes}, indent=2) + '\n')
    update_crosswalk(aux)
    run([sys.executable, 'tests/build_statement_register.py', '--aux', str(aux)], ROOT, 'statement_register')
    for kind in ['visual', 'lean']:
        run([sys.executable, 'build.py', '--output-directory', str(build / kind)],
            ROOT / 'guides' / kind, kind)
    supplement = build / 'supplement'
    supplement.mkdir(exist_ok=True)
    for name in ['Paper_III_Section17_Analytic_Closeout.tex', 'decorated_partition_terms.pdf']:
        shutil.copy2(ROOT / 'docs' / name, supplement / name)
    for number in [1, 2, 3]:
        run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
             'Paper_III_Section17_Analytic_Closeout.tex'], supplement, 'supplement_' + str(number))
    outputs = [
        ('traditional', 'Paper_III_Traditional_Final', 'Paper_III_Final_v1.0.0.pdf'),
        ('visual', 'Paper_III_Visual_Guide_Final', 'Paper_III_Visual_Guide_v1.0.0.pdf'),
        ('lean', 'Paper_III_Lean_Guide_Final', 'Paper_III_Lean_Guide_v1.0.0.pdf'),
        ('supplement', 'Paper_III_Section17_Analytic_Closeout', 'Paper_III_Analytic_Supplement_v1.0.0.pdf')]
    for directory, stem, name in outputs:
        shutil.copy2(build / directory / (stem + '.pdf'), publication / name)
        for suffix in ['log', 'aux', 'toc', 'bbl', 'blg']:
            source = build / directory / (stem + '.' + suffix)
            if source.is_file():
                shutil.copy2(source, evidence / (directory + '.' + suffix))
        final_log = (build / directory / (stem + '.log')).read_text(errors='replace')
        bad = [line for line in final_log.splitlines() if any(marker in line for marker in
               ['undefined references', 'undefined citations', 'Missing character:',
                'undefined on input', 'multiply defined'])]
        if bad:
            raise RuntimeError('Unresolved final typesetting diagnostics in ' + name + ': ' + str(bad))
    run([sys.executable, 'docs/build_reader.py'], ROOT, 'complete_reader')
    record = {'status': 'PASS', 'release_version': '1.0.0', 'runs': runs,
              'scope': 'Typesetting, compiled navigation and PDF assembly; mathematical verification is separate.',
              'build_environment': {'python': sys.version, 'source_date_epoch': environment['SOURCE_DATE_EPOCH']},
              'outputs': {p.name: sha(p) for p in sorted(publication.glob('*.pdf'))}}
    (evidence / 'BUILD_REPORT.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Reading PDFs built. Review rendered layout before distribution.')


if __name__ == '__main__':
    main()
