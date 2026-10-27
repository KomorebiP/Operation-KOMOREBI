#!/usr/bin/env python3
"""Validate accepted Paper II gates, write release status/checksums, and package."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REL = ROOT / 'release_package/Komorebi_Paper_II_Release_2026-10-15'
EV = REL / 'verification/release_2026-10-15'
OUT = ROOT / 'output'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def bound(path):
    path = Path(path)
    return {'path': path.relative_to(REL).as_posix(), 'sha256': sha(path)}

def release_files():
    for p in sorted(REL.rglob('*')):
        require(not p.is_symlink(), 'Release symlink: ' + str(p))
        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
            yield p

def archive(path, files):
    require(not path.exists(), 'Refusing to overwrite archive: ' + str(path))
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for file, name in files:
            z.write(file, name)
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, 'ZIP integrity failure: ' + str(path))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verification', type=Path, required=True)
    args = parser.parse_args()
    vp = args.verification.resolve()
    v = read(vp)
    require(v['status'] == 'PASS' and v['mode'] == 'fresh-complete-closure', 'Fresh closure PASS required')
    require(v['production_module_count'] == 62, 'Unexpected source denominator')
    require(v['negative_controls'] == 9 and v['replay_exact_name_match'], 'Audit controls/name match absent')
    require(v.get('upstream_duplicate_body_recheck_count') == 1 and v.get('upstream_duplicate_body_recheck_names') == ['Submodule.factor.eq_1'],
        'Reviewed upstream duplicate body check absent')
    require(v['replay_starting_environment_excludes_project_modules'], 'Replay starting environment not isolated')
    require(all(c['passed'] for c in v['checks']), 'Failed audit gate')
    for c in v['checks']:
        require(sha(vp.parent / c['log']) == c['log_sha256'], 'Audit log changed: ' + c['label'])
    for r in v['source_files']:
        require(r['origin'] == 'fresh_compile', 'Cached local source object')
        require(sha(REL / 'formal/current' / r['source']) == r['source_sha256'], 'Formal source drift')
    scope_path = REL / 'formal/coverage/Paper_II_Current_Correspondence_2026-10-15.json'
    scope = read(scope_path)
    require(scope['status'] == 'FINAL_SCOPED_CORRESPONDENCE_WITH_TWO_ANALYTIC_GAPS', 'Final scoped map required')
    require(scope['kernel_binding']['verification_sha256'] == sha(vp), 'Different verification receipt')
    require(scope['final_proof_counts'] == {'kernel_checked_semantically_accepted_scope': 51,
        'kernel_checked_partial_scope_open_bridge': 2}, 'Unexpected semantic scope counts')
    for rel, digest in scope['current_chapter_sha256'].items():
        require(sha(REL / rel) == digest, 'Manuscript drift: ' + rel)
    pub_path = REL / 'publication/FINAL_PUBLICATION_REVIEW.json'
    pub = read(pub_path)
    require(pub['state'] == 'READY_WITH_SCOPED_FORMAL_COVERAGE', 'Publication not accepted')
    require(pub['current_correspondence_sha256'] == sha(scope_path), 'Publication map mismatch')
    pm_path = REL / 'publication/CURRENT_PUBLICATION_MANIFEST.json'
    pm = read(pm_path)
    require(pm['state'] == pub['state'], 'Publication manifest not finalized')
    qa = read(REL / pub['page_qa']['path'])
    require(sha(REL / pub['page_qa']['path']) == pub['page_qa']['sha256'], 'QA record drift')
    require(qa['visual_review'] == 'PASS' and qa['all_pages_rendered'], 'All-page QA absent')
    by_pub = {d['path']: d for d in pub['pdfs']}
    by_pm = {d['path']: d for d in pm['documents']}
    by_qa = {d['file']: d for d in qa['documents']}
    require(len(by_pub) == len(pub['pdfs']) == len(by_pm) == len(pm['documents']) == len(by_qa) == len(qa['documents']) == 3,
        'Expected three distinct editions in each publication/QA record')
    require(set(by_pub) == set(by_pm) == set(by_qa), 'Publication/QA document sets differ')
    for d in pm['documents']:
        require(sha(REL / d['path']) == d['sha256'], 'Reviewed PDF drift')
        r, q = by_pub[d['path']], by_qa[d['path']]
        require(r['sha256'] == d['sha256'] == q['pdf_sha256'] and r['pages'] == d['pages'] == q['pages'],
            'Publication/QA PDF hash or page-count mismatch')
        require(q['visual_review'] == 'PASS' and not any(bool(x) for x in q['issues'].values()), 'Unresolved document QA')
        for rel, digest in d['actual_input_sha256'].items():
            require(sha(REL / rel) == digest, 'Publication input drift: ' + rel)
    nav = read(REL / 'publication/CURRENT_NAVIGATION_BUILD.json')
    require(not nav['destination_page_mismatches'] and not nav['updated_plate_sources'], 'Navigation incomplete')
    require(nav['traditional_pdf_sha256'] == next(d['sha256'] for d in pm['documents'] if d['role'] == 'traditional'),
        'Navigation bound to a different PDF')
    index_path = EV / 'EVIDENCE_INDEX.json'
    index = read(index_path)
    for r in index['files']:
        p = EV / r['packaged_path']
        require(sha(p) == r['sha256'] and p.stat().st_size == r['bytes'], 'Evidence copy drift')
    packaged_v = EV / vp.relative_to(ROOT)
    require(sha(packaged_v) == sha(vp), 'Accepted receipt absent from evidence package')
    comp_path = EV / 'paper2_work/computation_final/reviewed_evidence.json'
    comp = read(comp_path)
    require(comp['run']['exit_status'] == 0 and comp['input_hashes_unchanged'], 'Computation contract not accepted')
    require(all(r['verdict'] == 'PASS' for r in comp['fresh_evidence']), 'Computation component failed')
    computation_manifest = read(EV / 'paper2_work/computation_final/run_2026-10-15/manifest.json')
    for r in computation_manifest['input_artifacts']:
        require(sha(ROOT / r['path']) == r['sha256'] == r['sha256_after'], 'Computation input drift: ' + r['path'])
    status = {
        'schema': 'komorebi.paper-ii.reviewed-release/1', 'edition_date': '2026-10-15',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'state': 'READY_WITH_SCOPED_FORMAL_COVERAGE', 'fully_lean_formalized': False,
        'decision': 'The reviewed manuscript and both companion guides are ready for release with explicit partial formal coverage of two analytic statements.',
        'publication': {**bound(pub_path), 'total_pages': pub['total_pages'], 'all_page_visual_review': 'PASS',
            'documents': pub['pdfs']},
        'formal': {'verification': bound(packaged_v), 'correspondence': bound(scope_path),
            'toolchain': v['lean_version'], 'mathlib_revision': next(d['rev'] for d in v['dependencies'] if d['name'] == 'mathlib'),
            'fresh_production_modules': v['production_module_count'], 'owned_declarations': v['owned_total'],
            'kernel_replayed_logical_declarations': v['logical_checked_count'],
            'reviewed_runtime_helpers': v['generated_runtime_helper_count'], 'negative_controls': v['negative_controls'],
            'upstream_duplicate_fresh_body_rechecks': v['upstream_duplicate_body_recheck_count'],
            'manuscript_records': 81, 'proof_level_records': 53, 'accepted_complete_scopes': 51, 'partial_scopes': 2,
            'mapped_owned_and_replayed_names': scope['kernel_binding']['mapped_declaration_count'],
            'open_statements': ['thm:holomorphic_defect', 'cor:exact_compatibility (holomorphic part)'],
            'remaining_bridges': ['Geometric length equals the integral of velocity norm.',
                'Classical rectifiable contour integral agrees with the velocity integral, including monotone reparameterization invariance.',
                'General zero-winding Cauchy, admissible contour existence, and canonical holomorphic calculus/contour independence.'],
            'limitations': v['limits']},
        'bounded_computation': {**bound(comp_path), 'status': 'PASS_FOR_RECORDED_FINITE_CONTRACT',
            'final_current_input_hashes_rechecked': len(computation_manifest['input_artifacts']),
            'exact_visual_checks': 118, 'canonical_summary_rows': 9, 'figure_data_paths': 13,
            'byte_identical_atlas_sources': 22, 'expanded_mathematical_groups': 9,
            'historical_48_pytest_cases_freshly_rerun': False,
            'scope': 'Finite examples and stated numerical tolerances; no universal proof claim.'},
        'evidence_index': bound(index_path),
        'historical_evidence': 'Failed development checks and superseded status/maps are retained as history; they do not override this current accepted scoped status.',
        'integrity_manifest': 'MANIFEST_SHA256.json',
        'packaging_exclusions': ['__pycache__ directories', '*.pyc'],
    }
    write(REL / 'RELEASE_STATUS.json', status)
    rows = [{'path': p.relative_to(REL).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in release_files() if p.name != 'MANIFEST_SHA256.json' or p.parent != REL]
    write(REL / 'MANIFEST_SHA256.json', {'schema': 'komorebi.sha256_manifest.v1',
        'notice': 'Manifest excludes itself and the documented Python cache exclusions. All other release files, including retained historical manifests, are covered.',
        'edition_date': '2026-10-15', 'file_count': len(rows), 'files': rows})
    OUT.mkdir(exist_ok=True)
    for d in pub['pdfs']:
        shutil.copy2(REL / d['path'], OUT / Path(d['path']).name)
    main_zip = OUT / 'Komorebi_Paper_II_Reviewed_Release_2026-10-15.zip'
    archive(main_zip, [(p, REL.name + '/' + p.relative_to(REL).as_posix()) for p in release_files()])
    with zipfile.ZipFile(main_zip) as z:
        require(len(z.namelist()) == len(rows) + 1, 'Archive file count differs from manifest')
        for r in rows:
            require(hashlib.sha256(z.read(REL.name + '/' + r['path'])).hexdigest() == r['sha256'], 'Archive checksum mismatch')
    latest = OUT / 'Paper_II_Latest_2026-10-15.zip'
    checksum_file = OUT / 'Paper_II_Release_SHA256.txt'
    checksum_file.write_text(sha(main_zip) + '  ' + main_zip.name + '\n')
    archive(latest, [(main_zip, main_zip.name), (REL / 'READ_FIRST.txt', 'READ_FIRST.txt'),
        (REL / 'RELEASE_STATUS.json', 'RELEASE_STATUS.json'), (checksum_file, checksum_file.name)])
    result = {'status': 'PACKAGED_SCOPED_RELEASE', 'fully_lean_formalized': False,
        'release_file_count': len(rows) + 1, 'output_files': [
            {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in
            [*(OUT / Path(d['path']).name for d in pub['pdfs']), main_zip, latest]]}
    write(OUT / 'Paper_II_Packaging_Receipt.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
