#!/usr/bin/env python3
"""Package the reviewed visual revision while retaining its formal baseline."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
INPUTS = WORKSPACE / 'visual_revision_inputs'
PARENT = INPUTS / 'Komorebi_Space_Publication_v1.13.0'
OUT = WORKSPACE / 'output'
PUB = 'Komorebi_Space_Publication_v1.13.0'
TECH = 'Komorebi_Space_Technical_Record_v1.13.0'
VISUAL = 'Komorebi_Space_Visual_Guide_v1.13.0.pdf'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def files_under(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def archive(path, prefix, payload):
    assert 'SHA256SUMS' not in payload
    sums = ''.join(f'{sha(data)}  {name}\n' for name, data in sorted(payload.items()))
    all_files = {**payload, 'SHA256SUMS': sums.encode()}
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(all_files.items()):
            assert not name.startswith('/') and '..' not in Path(name).parts
            info = zipfile.ZipInfo(prefix + '/' + name, (2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
    return {'file': path.name, 'sha256': sha(path.read_bytes()),
            'size_bytes': path.stat().st_size, 'payload_files': len(payload)}

def main():
    OUT.mkdir(exist_ok=True)
    pdf = ROOT / 'build/visual_02/visual/Komorebi_Space_Visual_Guide.pdf'
    render = json.loads((ROOT / 'build/visual_review_final/render_report.json').read_text())
    review = json.loads((ROOT / 'review/independent_visual_review.json').read_text())
    assert render['pdf_sha256'] == sha(pdf.read_bytes()) and render['pages'] == 19
    assert not render['outside_words']
    assert review['pdf_sha256'] == render['pdf_sha256']
    build = json.loads((ROOT / 'build/visual_02/build_report.json').read_text())
    assert build['source_unchanged']

    # Every original source except the guide, every Lean file, and both other
    # books must retain the exact bytes of the recovered publication.
    identity = {}
    for folder in ['source', 'lean', 'examples']:
        old = files_under(PARENT / folder)
        new = files_under(ROOT / folder)
        changed = [name for name, data in old.items() if new.get(name) != data]
        assert changed == (['Komorebi_Space_Visual_Guide.tex'] if folder == 'source' else [])
        identity[folder] = {'original_files': len(old), 'changed_original_files': changed,
                            'added_files': sorted(set(new) - set(old))}
    for name in ['Komorebi_Space_Monograph_v1.13.0.pdf', 'Komorebi_Space_Lean_Guide_v1.13.0.pdf']:
        assert (ROOT / 'books' / name).read_bytes() == (PARENT / 'books' / name).read_bytes()

    shutil.copyfile(pdf, ROOT / 'books' / VISUAL)
    shutil.copyfile(pdf, OUT / VISUAL)
    scenes = json.loads((ROOT / 'source/visual_companion/scenes.json').read_text())
    assert len(scenes) == 16
    generator_checks = [json.loads((ROOT / 'build' / name).read_text())
                        for name in ['foundations_checks.json', 'analysis_checks.json']]
    assert sum(len(c['checks']) for c in generator_checks) == 52
    assert all(x['passed'] for c in generator_checks for x in c['checks'])
    independent = json.loads((ROOT / 'review/independent_visual_review_checks.json').read_text())
    assert len(independent['checks']) == 23

    visual_record = {
        'scope': 'Sixteen worked visual investigations; finite computations and editorial review, not a new formal proof release.',
        'pages': 19, 'investigations': 16, 'new_figure_assets': 16,
        'reused_monograph_figure_assets': 0,
        'previous_guide': {'pages': 45, 'figures': 40, 'reused_monograph_figure_assets': 38},
        'pdf_sha256': render['pdf_sha256'],
        'generator_checks_passed': 52,
        'generator_check_scope': 'Finite formulas, displayed values, and typography checks; counts include font-size checks.',
        'independent_checks_passed': 23,
        'infinite_claim_scope': 'Explicit mathematical arguments and cited monograph results; never inferred from a finite plotting window.',
        'formal_scope': 'Production Lean, monograph, and Lean guide unchanged. No new Lean compilation claimed.',
        'source_identity': identity,
        'visual_review': {'physical_pages': list(range(1,20)), 'outside_page_words': 0,
                          'root_pages': list(range(1,11)), 'independent_pages': list(range(11,20))},
        'monograph_pointers': {s['id']: s['monograph_labels'] for s in scenes},
        'parent_publication_sha256': sha((INPUTS / (PUB + '.zip')).read_bytes()),
    }
    dump(ROOT / 'verification/VISUAL_GUIDE_REVIEW.json', visual_record)
    for name in ['foundations_checks.json', 'analysis_checks.json']:
        dest = ROOT / 'verification/visual' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'build' / name, dest)
    shutil.copyfile(ROOT / 'review/independent_visual_review_checks.json',
                    ROOT / 'verification/visual/independent_checks.json')
    edition = json.loads((ROOT / 'verification/EDITION_VERIFICATION.json').read_text())
    for book in edition['books']:
        book['sha256'] = sha((ROOT / book['file']).read_bytes())
    edition['visual_guide_revision'] = visual_record
    dump(ROOT / 'verification/EDITION_VERIFICATION.json', edition)
    dump(ROOT / 'records/VISUAL_REVISION_RESULT.json', visual_record)

    payload = {'README.md': (ROOT / 'README.md').read_bytes()}
    for folder in ['books', 'source', 'lean', 'examples', 'tools', 'verification']:
        payload.update({folder + '/' + name: data for name, data in files_under(ROOT / folder).items()})
    public_result = archive(OUT / (PUB + '.zip'), PUB, payload)

    with zipfile.ZipFile(INPUTS / (TECH + '.zip')) as z:
        prefix = TECH + '/'
        previous = {name[len(prefix):]: z.read(name) for name in z.namelist() if not name.endswith('/')}
    technical = {name: data for name, data in previous.items() if name not in ['README.md', 'SHA256SUMS']}
    technical['visual_revision/parent_technical_README.md'] = previous['README.md']
    technical['visual_revision/parent_technical_SHA256SUMS.txt'] = previous['SHA256SUMS']
    technical['visual_revision/parent/' + PUB + '.zip'] = (INPUTS / (PUB + '.zip')).read_bytes()
    parent_report = 'Komorebi_Space_Publication_Verification_v1.13.0.json'
    technical['visual_revision/parent/' + parent_report] = (INPUTS / parent_report).read_bytes()
    technical['README.md'] = (
        '# Komorebi Space — Technical Record\n\n'
        'This record accompanies publication edition 1.13.0 and its revised visual guide. '
        'The reader-facing books and reusable sources are in the Publication package.\n\n'
        'The accepted formal archives in `accepted_verification/` and the original publication '
        'evidence in `publication/` retain their original bytes. They establish the unchanged '
        'formal baseline; they do not describe the revised visual guide.\n\n'
        '`visual_revision/` contains the redesign contract, finite checks, independent '
        'mathematical and visual reviews, build receipts, rendering coverage, and the '
        'parent publication. Review notes retain failed attempts and their corrections. '
        'Its `records/VISUAL_REVISION_RESULT.json` describes the current guide. '
        'The original technical README and checksum list are retained there as provenance.\n\n'
        'The current guide has nineteen pages and sixteen new visual investigations. '
        'It refers to the monograph for proofs. Finite plotting checks are not universal '
        'proofs or new Lean verification.\n\n'
        '`SHA256SUMS` covers every other file in this archive. The separate '
        '`Komorebi_Space_Publication_Verification_v1.13.0.json` binds the final '
        'delivery archives to their independent integrity review.\n'
    ).encode()
    for folder in ['records', 'review', 'build/visual_checks', 'build/visual_01', 'build/visual_02',
                   'build/monograph_reference', 'source/visual_companion', 'tools/visual_companion']:
        for name, data in files_under(ROOT / folder).items():
            # PDFs of reference-only builds and TeX recorder files add no unique evidence.
            if Path(name).suffix in ['.pdf', '.fls']:
                continue
            technical['visual_revision/' + folder + '/' + name] = data
    for name in ['tools/build_visual_companion.py', 'tools/run_visual_checks.py',
                 'source/Komorebi_Space_Visual_Guide.tex', 'build/foundations_checks.json',
                 'build/analysis_checks.json', 'build/visual_review/render_report.json',
                 'build/visual_review_final/render_report.json']:
        technical['visual_revision/' + name] = (ROOT / name).read_bytes()
    technical_result = archive(OUT / (TECH + '.zip'), TECH, technical)
    result = {'public': public_result, 'technical': technical_result,
              'visual_pdf': {'file': VISUAL, 'sha256': render['pdf_sha256'], 'pages': 19}}
    dump(ROOT / 'build/package_visual_revision_result.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
