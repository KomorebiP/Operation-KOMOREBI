#!/usr/bin/env python3
"""Package the reviewed book, revised reading sources and exact selected originals.

Review records must identify the current PDF bytes. This command does not run
proofs, computations, or editorial review. Use --check-only before packaging.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
STAGE = ROOT/'package_stage'/'Realization_Calculus_Publication_Package'
TREES = ('source_i_iv', 'source_v_viii', 'source_ix_xii', 'compiled',
         'frozen_readers', 'publication_notices', 'LICENSES', 'book', 'editorial')
ROOT_FILES = (
    'README.md', 'LICENSE.txt', 'requirements.txt', 'publisher-layout.tex',
    'prepare_book.py', 'book_layout.py', 'book_component_adapter.py',
    'atlas_book_routes.py',
    'preserved_pdf_proofread.py', 'render_book_matter.py', 'render_outer.py',
    'assemble_monograph.py', 'audit_monograph.py', 'rebrand_components.py',
    'audit_rebranding.py', 'make_preview.py', 'rebuild_monograph.py',
    'package_publication.py', 'component_builds.json',
    'typeset_i_iv_results.json', 'typeset_v_viii_results.json',
    'typeset_ix_x_results.json', 'typeset_ix_xii_results.json',
    'MONOGRAPH_LEDGER_v1.0.0.txt', 'REALIZATION_CALCULUS_EDITORIAL_LEDGER_v1.1.0.txt',
    'register_current.txt', 'register_metadata.json', 'reader_inventory.json',
)
FONT_EXTENSIONS = {'.otf', '.ttf', '.pfb', '.pfa', '.t1', '.afm', '.woff', '.woff2'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def load(path):
    if not path.is_file():
        raise ValueError('Required publication record is missing: '+str(path))
    return json.loads(path.read_text())


def validate_reviews(root=ROOT):
    """Bind every delivery gate to the actual book and dynamic reading sequence."""
    import fitz
    book_pdf = root/'output/Realization_Calculus.pdf'
    pdf_hash = sha(book_pdf)
    spec = load(root/'book/build_spec.json')
    if spec.get('schema') != 'realization-calculus.book-spec/2':
        raise ValueError('Packaging requires the chapter/formal-companion/glossary book specification.')
    cursor = spec['front_pages']
    if not isinstance(cursor, int) or cursor < 1:
        raise ValueError('Invalid preliminary-page count.')
    for entry in spec['sequence']:
        if entry['book_index'] != cursor:
            raise ValueError('The reading sequence has a gap or overlap.')
        if entry['kind'] == 'leaf':
            cursor += 1
        elif entry['kind'] == 'component':
            cursor += len(entry['source_pages'])
        elif entry['kind'] == 'glossary':
            cursor += entry['pages']
        else:
            raise ValueError('Unknown reading-sequence kind: '+entry['kind'])
    with fitz.open(book_pdf) as document:
        actual_pages = len(document)
    if cursor != spec['expected_total_pages'] or actual_pages != cursor:
        raise ValueError('The PDF page count does not match the selected reading sequence.')

    reviews = {}
    for key, filename in (
        ('pdf', 'final_pdf_audit.json'),
        ('visual', 'final_visual_review.json'),
        ('editorial', 'book_editorial_audit.json'),
    ):
        record = load(root/'book'/filename)
        if record.get('status') != 'PASS' or record.get('pdf_sha256') != pdf_hash:
            raise ValueError(filename+' must pass and identify the current book bytes.')
        reviews[key] = record
    for field, filename in (('build_spec_sha256', 'build_spec.json'),
                            ('page_map_sha256', 'page_map.json')):
        if reviews['pdf'].get(field) != sha(root/'book'/filename):
            raise ValueError('The final PDF audit is stale for '+filename+'.')
    preview = load(root/'book/preview_manifest.json')
    if (preview.get('source_sha256') != pdf_hash or
            preview.get('preview_sha256') != sha(root/'output/Realization_Calculus_Design_Preview.pdf')):
        raise ValueError('The preview record must identify the current book and preview bytes.')
    return {'pdf_sha256': pdf_hash, 'pages': actual_pages, 'spec': spec,
            'reviews': reviews, 'preview': preview}


def exclusion_reason(relative):
    """Exclude generated caches, test renders and external font programs only."""
    if '__pycache__' in relative.parts or relative.suffix == '.pyc':
        return 'Reproducible Python bytecode cache.'
    if relative.parts[0].startswith('source_') and relative.suffix.lower() in {
            '.aux', '.toc', '.fls', '.fdb_latexmk', '.xdv'}:
        return 'Reproducible TeX build cache; editable inputs, PDFs and verification logs are retained.'
    if (relative.parts[0].startswith('source_') and relative.suffix.lower() == '.out'
            and (ROOT/relative).with_suffix('.aux').is_file()):
        return 'Reproducible TeX bookmark cache identified by its sibling auxiliary file.'
    if relative.parts[0].startswith('source_') and (
            relative.suffix.lower() in FONT_EXTENSIONS):
        return 'External font dependency; version and licensing records are retained.'
    if (relative.parts[:3] == ('editorial', 'rhythm_review', 'final_visual_samples')
            and relative.suffix.lower() in IMAGE_EXTENSIONS):
        return 'Reproducible review-page render; exact book, sampler, selections and review record are retained.'
    if relative.parts[0] in ('book', 'editorial'):
        is_test = any(part.endswith('_test') for part in relative.parts[:-1])
        if is_test and relative.suffix.lower() == '.pdf':
            return 'Generated test PDF; its sources and review records are retained.'
        if relative.suffix.lower() in IMAGE_EXTENSIONS and 'contact' in relative.stem.casefold():
            return 'Generated contact sheet; individual reviewed-page images and selection records are retained.'
    return None


def select_files(root=ROOT):
    """Preserve every selected input, editable source, backup and editorial record."""
    selected, excluded = [], []
    for name in TREES:
        tree = root/name
        if not tree.is_dir():
            raise FileNotFoundError(tree)
        for path in sorted(tree.rglob('*')):
            if path.is_symlink():
                raise ValueError('Unexpected source symlink: '+str(path.relative_to(root)))
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            reason = exclusion_reason(relative)
            if reason:
                excluded.append({'path': relative.as_posix(), 'reason': reason})
            else:
                selected.append((path, relative))
    for name in ROOT_FILES:
        path = root/name
        if not path.is_file():
            raise FileNotFoundError(path)
        selected.append((path, Path(name)))
    # Keep the prior readme as historical evidence without presenting obsolete
    # page counts or rebuild instructions as the current package guide.
    old_readme = root/'README.txt'
    if old_readme.is_file():
        selected.append((old_readme, Path('editorial/revision_history/README_before_book_revision.txt')))
    for path in sorted((root/'scripts').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            selected.append((path, path.relative_to(root)))
    for name in ('Realization_Calculus.pdf', 'Realization_Calculus_Design_Preview.pdf'):
        selected.append((root/'output'/name, Path('output')/name))
    # Deduplicate only superseded build PDFs with an exact retained byte copy.
    # Original files, scientific figure assets and active component PDFs remain.
    ordinary, candidates = [], []
    for item in selected:
        path, relative = item
        superseded = relative.suffix.lower() == '.pdf' and any(
            p in ('failed_initial', 'layout_first') for p in relative.parts)
        (candidates if superseded else ordinary).append(item)
    retained_hashes = {}
    for path, relative in ordinary:
        if path.suffix.lower() == '.pdf':
            retained_hashes.setdefault(sha(path), relative.as_posix())
    for path, relative in candidates:
        digest = sha(path)
        if digest in retained_hashes:
            excluded.append({'path': relative.as_posix(),
                             'reason': 'Byte-identical superseded build PDF.',
                             'retained_copy': retained_hashes[digest], 'sha256': digest})
        else:
            ordinary.append((path, relative))
            retained_hashes[digest] = relative.as_posix()
    destinations = [relative.as_posix() for _, relative in ordinary]
    if len(destinations) != len(set(destinations)):
        raise ValueError('Duplicate package destination.')
    return ordinary, excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true',
                        help='Validate the review gates and file selection without staging or writing a ZIP.')
    args = parser.parse_args()
    try:
        checked = validate_reviews()
        selected, excluded = select_files()
    except (ValueError, FileNotFoundError, KeyError) as error:
        raise SystemExit(str(error)) from error
    if args.check_only:
        print(json.dumps({'status': 'PASS', 'pdf_sha256': checked['pdf_sha256'],
                          'pages': checked['pages'], 'selected_files': len(selected),
                          'excluded_generated_or_dependency_files': len(excluded)}, indent=2))
        return
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for path, relative in selected:
        target = STAGE/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    components = [c for part in checked['spec']['parts'] for c in part['components']]
    dump(STAGE/'editorial/package_selection.json', {
        'excluded': excluded,
        'policy': 'Retain selected original readers, editable sources, exact pre-edit backups, scientific assets, all editorial records and active build dependencies. Exclude external font programs, generated caches/test PDFs/contact sheets, and byte-identical superseded build PDFs only.',
        'original_reader_pdfs': len(components),
        'book_pages': checked['pages'], 'book_pdf_sha256': checked['pdf_sha256'],
        'full_formal_archives': 'Preserved separately in their existing durable distributions; not duplicated in this reading-publication package.',
    })
    rows = [{'path': p.relative_to(STAGE).as_posix(), 'bytes': p.stat().st_size,
             'sha256': sha(p)} for p in sorted(STAGE.rglob('*')) if p.is_file()]
    manifest = {
        'schema': 'komorebi.strict_manifest.v1',
        'checkpoint': 'Realization Calculus book publication',
        'scope': 'Exact publication file membership and bytes; not mathematical verification.',
        'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'files': rows,
    }
    dump(STAGE/'MANIFEST_SHA256.json', manifest)
    verify = subprocess.run([sys.executable, '-B', str(STAGE/'scripts/verify_integrity.py'), '--strict'],
                            capture_output=True, text=True)
    (ROOT/'PACKAGE_STAGE_VERIFICATION.txt').write_text(verify.stdout+verify.stderr)
    if verify.returncode:
        raise SystemExit('Staging integrity verification failed.')
    target = ROOT/'output/Realization_Calculus_Publication_Package.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(STAGE.rglob('*')):
            if path.is_file():
                archive.write(path, str(Path(STAGE.name)/path.relative_to(STAGE)))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip():
            raise ValueError('ZIP CRC failure')
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP path')
        for row in rows:
            data = archive.read(STAGE.name+'/'+row['path'])
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError(row['path'])
        manifest_bytes = archive.read(STAGE.name+'/MANIFEST_SHA256.json')
        if hashlib.sha256(manifest_bytes).hexdigest() != sha(STAGE/'MANIFEST_SHA256.json'):
            raise ValueError('Manifest stream mismatch')
    record = {
        'status': 'PASS', 'package_bytes': target.stat().st_size, 'package_sha256': sha(target),
        'regular_members': len(rows)+1, 'manifest_rows': len(rows), 'zip_crc': 'PASS',
        'all_member_bytes_and_hashes': 'PASS', 'stage_strict_integrity': 'PASS',
        'font_binaries_excluded': True, 'book_pages': checked['pages'],
        'book_pdf_sha256': checked['pdf_sha256'],
        'source_pdf_audit_status': checked['reviews']['pdf']['status'],
        'book_editorial_audit_status': checked['reviews']['editorial']['status'],
        'final_visual_review_status': checked['reviews']['visual']['status'],
    }
    dump(ROOT/'PACKAGE_DELIVERY_VERIFICATION.json', record)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
