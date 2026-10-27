#!/usr/bin/env python3
"""Package the accepted budget release, preserving historical source/evidence bytes."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def copy(src, dst, exclude_renders=False):
    patterns = ['__pycache__', '*.pyc', 'build', '*.olean', '*.ilean', '*.olean.private', '*.olean.server']
    if exclude_renders:
        patterns.append('renders')
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*patterns))

def deliverable_tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and not any(x in {'build','__pycache__'} for x in p.relative_to(root).parts)
            and not p.name.endswith(('.pyc','.olean','.ilean','.olean.private','.olean.server'))}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    rec = json.loads((run/'receipt.json').read_text())
    post = json.loads((run/'postflight.json').read_text())
    if rec['status'] != 'PASS' or post['status'] != 'PASS':
        raise SystemExit('Formal acceptance gates have not passed')
    receipt_hash = sha(run/'receipt.json')
    if post['run_receipt_sha256'] != receipt_hash:
        raise SystemExit('Postflight does not bind this receipt')
    accepted_source = tree(run/'source')
    if accepted_source != rec['source_snapshot_sha256'] or accepted_source != post['source_snapshot_sha256']:
        raise SystemExit('Accepted source snapshot changed')
    assembly = Path(rec['assembly_path'])
    if sha(assembly/'inventory.json') != rec['inventory_sha256'] or rec['inventory_sha256'] != post['inventory_sha256']:
        raise SystemExit('Assembly inventory changed')
    inv = json.loads((assembly/'inventory.json').read_text())
    if tree(ROOT/'formal') != inv['overlay_input_sha256']:
        raise SystemExit('Current budget sources/controls differ from accepted overlay')
    if deliverable_tree(ROOT/'integration/scripts') != rec['verifier_input_sha256']:
        raise SystemExit('Verification helpers changed after acceptance')
    review = json.loads((ROOT/'reviews/reviewed_helpers.json').read_text())
    if sha(ROOT/'integration/postflight/validate.py') != review['postflight_sha256']:
        raise SystemExit('Postflight helper changed after review')
    if sha(ROOT/'reviews/reviewed_helpers.json') != post['review_manifest_sha256']:
        raise SystemExit('Helper review changed after acceptance')
    if sha(run/'axioms.json') != rec['axiom_report_sha256'] or rec['axiom_report_sha256'] != post['axiom_report_sha256']:
        raise SystemExit('Axiom evidence changed')
    for command in rec['commands']:
        if sha(run/command['log']) != command['log_sha256']:
            raise SystemExit('Compiler command log changed')
    ledger = json.loads((ROOT/'PROGRESS_LEDGER.json').read_text())
    if ledger['status'] != 'ACCEPTED':
        raise SystemExit('Release ledger is not accepted')
    if ledger['formal_receipt_sha256'] != receipt_hash or ledger['postflight_sha256'] != sha(run/'postflight.json'):
        raise SystemExit('Ledger is not bound to this accepted run')
    if any(sha(ROOT/p) != h for p,h in ledger['acceptance_evidence_sha256'].items()):
        raise SystemExit('Acceptance review or control evidence changed')
    pub = WORK/'monograph_v1.10.0'
    pv = json.loads((pub/'PUBLICATION_VERIFICATION.json').read_text())
    pdf = pub/'publication/Komorebi_Space_Monograph.pdf'
    if pv['status'] != 'PASS' or pv['pdf_sha256'] != sha(pdf) or pv['source_sha256'] != tree(pub/'source'):
        raise SystemExit('Publication gate has not passed for current source/PDF')
    if pv['formal_receipt_sha256'] != receipt_hash:
        raise SystemExit('Publication describes a different formal run')
    before = deliverable_tree(ROOT)
    previous = WORK/'output/Komorebi_Space_Monograph_v1.9.0'
    base = json.loads((ROOT/'records/BASE_CHECKPOINT.json').read_text())
    parent_zip = WORK/base['parent_archive']
    if sha(parent_zip) != base['parent_archive_sha256']:
        raise SystemExit('Pinned predecessor archive changed')
    with zipfile.ZipFile(parent_zip) as z:
        prefix = previous.name+'/'
        parent_tree = {n[len(prefix):]:hashlib.sha256(z.read(n)).hexdigest()
                       for n in z.namelist() if n.startswith(prefix) and not n.endswith('/')}
    if tree(previous) != parent_tree:
        raise SystemExit('Extracted predecessor differs from pinned archive')
    dest = WORK/'output/Komorebi_Space_Monograph_v1.10.0'
    if dest.exists():
        raise SystemExit('Refusing to overwrite a release')
    dest.mkdir()
    for name in ['source', 'scripts', 'reviews', 'audit']:
        copy(pub/name, dest/name, exclude_renders=(name == 'audit'))
    shutil.copy2(pub/'PUBLICATION_VERIFICATION.json', dest/'PUBLICATION_VERIFICATION.json')
    copy(run/'source', dest/'formal')
    copy(ROOT, dest/ROOT.name)
    inherited = {}
    for name in ['continuation', 'inherited_v1.7.0', 'examples', 'history']:
        shutil.copytree(previous/name, dest/name)
        if tree(previous/name) != tree(dest/name):
            raise SystemExit('Historical tree identity failed: '+name)
        inherited[name] = True
    old = dest/'history/v1.9.0'
    old.mkdir()
    for name in ['source', 'formal', 'reviews', 'audit', 'publication', 'scripts']:
        shutil.copytree(previous/name, old/name)
        if tree(previous/name) != tree(old/name):
            raise SystemExit('Previous edition identity failed: '+name)
    for p in previous.iterdir():
        if p.is_file(): shutil.copy2(p, old/p.name)
    for name in ['README.md', 'PROGRESS_LEDGER.md', 'PROGRESS_LEDGER.json', 'VERIFICATION_SUMMARY.json']:
        shutil.copy2(ROOT/name, dest/name)
    (dest/'publication').mkdir()
    pdfname = 'Komorebi_Space_Monograph_v1.10.0.pdf'
    shutil.copy2(pdf, dest/'publication'/pdfname)
    if tree(run/'source') != tree(dest/'formal'):
        raise SystemExit('Current formal source identity failed')
    if before != deliverable_tree(ROOT) or before != tree(dest/ROOT.name):
        raise SystemExit('Budget records changed or were incompletely copied')
    if pv['source_sha256'] != tree(dest/'source') or pv['pdf_sha256'] != sha(dest/'publication'/pdfname):
        raise SystemExit('Publication copy identity failed')
    payload = tree(dest)
    (dest/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in payload.items()))
    archive = dest.parent/(dest.name+'.zip')
    if archive.exists(): raise SystemExit('Refusing to overwrite archive')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(dest.rglob('*')):
            if p.is_file(): z.write(p, (Path(dest.name)/p.relative_to(dest)).as_posix())
    with zipfile.ZipFile(archive) as z:
        if z.testzip(): raise SystemExit('ZIP CRC failure')
        for name,digest in payload.items():
            if hashlib.sha256(z.read((Path(dest.name)/name).as_posix())).hexdigest() != digest:
                raise SystemExit('ZIP payload SHA failure: '+name)
    standalone = dest.parent/pdfname
    shutil.copy2(pdf, standalone)
    progress = dest.parent/'Komorebi_Space_Progress_v1.10.0.md'
    shutil.copy2(ROOT/'PROGRESS_LEDGER.md', progress)
    result = {'status':'PASS', 'archive':str(archive), 'archive_sha256':sha(archive),
              'archive_bytes':archive.stat().st_size, 'payload_files':len(payload),
              'crc':'PASS', 'payload_sha256':'PASS', 'historical_trees_byte_identical':inherited,
              'parent_archive_sha256':base['parent_archive_sha256'],
              'historical_identity_checked_against_pinned_archive':True,
              'current_formal_source_byte_identical':True, 'pdf':str(standalone),
              'pdf_sha256':sha(standalone), 'progress':str(progress), 'progress_sha256':sha(progress),
              'compiled_objects_included':False, 'portable_runtime_included':False}
    result['reproducible_publication_page_renders_included'] = False
    (dest.parent/'Komorebi_Space_Delivery_Verification_v1.10.0.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
