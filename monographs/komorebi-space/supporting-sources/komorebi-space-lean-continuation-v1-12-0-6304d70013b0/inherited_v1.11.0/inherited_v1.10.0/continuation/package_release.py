#!/usr/bin/env python3
"""Package immutable predecessor plus accepted continuation without runtime caches."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

CONT = Path(__file__).resolve().parent
ROOT_DIR = CONT.parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tree_hashes(root):
    return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}

def validate_delivery_inputs(summary, predecessor):
    """Bind the packaged sources and evidence to the accepted terminal scopes."""
    integration = CONT/'integration'
    base = integration/'runs'/summary['base_label']
    overlay = integration/'runs'/summary['overlay_label']
    for path,key in ((base/'receipt.json','base_receipt_sha256'),
                     (base/'postflight.json','base_postflight_sha256'),
                     (overlay/'receipt.json','overlay_receipt_sha256')):
        if digest(path) != summary[key]:
            raise SystemExit(f'Accepted receipt identity changed: {path}')
    base_receipt = json.loads((base/'receipt.json').read_text())
    postflight = json.loads((base/'postflight.json').read_text())
    overlay_receipt = json.loads((overlay/'receipt.json').read_text())
    if any(record['status'] != 'PASS' for record in (base_receipt,postflight,overlay_receipt)):
        raise SystemExit('A required accepted execution or postflight is not PASS')
    if not base_receipt['clean_project_build'] or overlay_receipt['clean_project_build']:
        raise SystemExit('Clean-base versus incremental-overlay scope mismatch')
    if postflight['base_receipt_sha256'] != summary['base_receipt_sha256']:
        raise SystemExit('Postflight is bound to a different base receipt')
    if (overlay_receipt['base_receipt_sha256'] != summary['base_receipt_sha256']
            or overlay_receipt['base_postflight_sha256'] != summary['base_postflight_sha256']):
        raise SystemExit('Overlay is bound to a different accepted base or postflight')
    if tree_hashes(base/'source') != postflight['source_snapshot_sha256']:
        raise SystemExit('Accepted base source/control snapshot changed')
    if tree_hashes(overlay/'source') != overlay_receipt['source_snapshot_sha256']:
        raise SystemExit('Accepted final source/control/exporter snapshot changed')
    if tree_hashes(integration/'project') != base_receipt['project_file_sha256']:
        raise SystemExit('Reproduction project changed from the accepted base')
    if digest(integration/'inventory.json') != base_receipt['inventory_sha256']:
        raise SystemExit('Reproduction inventory changed')
    if tree_hashes(integration/'scripts') != base_receipt['verifier_input_sha256']:
        raise SystemExit('Frozen base verifier helpers changed')
    if tree_hashes(integration/'scripts') != overlay_receipt['input_sha256']['helpers']:
        raise SystemExit('Frozen overlay helper identities changed')
    if digest(integration/'overlay/verify_overlay.py') != overlay_receipt['input_sha256']['this_script']:
        raise SystemExit('Accepted hardened overlay verifier changed')
    if digest(integration/'postflight/validate.py') != postflight['validator_sha256']:
        raise SystemExit('Accepted independent postflight validator changed')
    if tree_hashes(CONT/'formal') != overlay_receipt['input_sha256']['overlay']:
        raise SystemExit('New source/control input tree changed after verification')
    for rel,expected in summary['new_source_sha256'].items():
        path = CONT/rel
        accepted = overlay/'source'/path.relative_to(CONT/'formal')
        if digest(path) != expected or digest(accepted) != expected:
            raise SystemExit(f'New formal source identity changed: {rel}')
    for directory,record in ((base,base_receipt),(overlay,overlay_receipt)):
        if digest(directory/'axioms.json') != record['axiom_report_sha256']:
            raise SystemExit(f'Axiom report changed: {directory}')
        for command in record['commands']:
            if not command['passed'] or digest(directory/command['log']) != command['log_sha256']:
                raise SystemExit(f'Accepted command evidence changed: {command["label"]}')
    checkpoint = json.loads((CONT/'BASE_CHECKPOINT.json').read_text())
    for rel,expected in checkpoint['source_hashes'].items():
        if digest(predecessor/rel) != expected:
            raise SystemExit(f'Inherited formal-tree source changed: {rel}')
    ledger = json.loads((CONT/'PROGRESS_LEDGER.json').read_text())
    if ledger['verification_summary_sha256'] != digest(CONT/'VERIFICATION_SUMMARY.json'):
        raise SystemExit('Progress ledger is bound to a different verification summary')

def main():
    summary = json.loads((CONT/'VERIFICATION_SUMMARY.json').read_text())
    if summary['status'] != 'PASS':
        raise SystemExit('No accepted final verification summary')
    publication = json.loads((CONT/'publication/PUBLICATION_VERIFICATION.json').read_text())
    if publication['status'] != 'PASS' or publication['pdf_sha256'] != digest(CONT/'publication/Continuation_Guide.pdf'):
        raise SystemExit('The current guide lacks an accepted publication review')
    predecessor = ROOT_DIR/'work/Komorebi_Space_Monograph_v1.7.0'
    validate_delivery_inputs(summary, predecessor)
    out = ROOT_DIR/'output'
    out.mkdir(exist_ok=True)
    name = 'Komorebi_Space_Formal_Continuation_v1.8.0'
    stage = out/name
    if stage.exists():
        raise SystemExit('Refusing to overwrite staged release')
    shutil.copytree(predecessor, stage/'inherited_v1.7.0')
    dest = stage/'continuation'
    for src in sorted(CONT.rglob('*')):
        rel = src.relative_to(CONT)
        if not src.is_file() or {'build','__pycache__'} & set(rel.parts):
            continue
        if src.suffix in {'.olean','.ilean','.o','.c','.pyc'}:
            continue
        if rel.parts[0] == 'publication' and src.suffix in {'.aux','.out','.toc'}:
            continue
        target = dest/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,target)
    final_source = CONT/'integration/runs'/summary['overlay_label']/'source'
    shutil.copytree(final_source,stage/'formal')
    for title in ('README.md','PROGRESS_LEDGER.md','PROGRESS_LEDGER.json','VERIFICATION_SUMMARY.json'):
        shutil.copyfile(CONT/title,stage/title)
    files = [p for p in sorted(stage.rglob('*')) if p.is_file()]
    manifest = {p.relative_to(stage).as_posix():digest(p) for p in files}
    (stage/'SHA256SUMS.txt').write_text(''.join(f'{h}  {rel}\n' for rel,h in manifest.items()))
    archive = out/(name+'.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                z.write(p,p.relative_to(out))
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise RuntimeError('ZIP CRC check failed')
        actual={n for n in z.namelist() if not n.endswith('/')}
        expected={name+'/'+rel for rel in manifest}|{name+'/SHA256SUMS.txt'}
        if actual != expected:
            raise RuntimeError('Manifest coverage is incomplete')
        for rel,h in manifest.items():
            if hashlib.sha256(z.read(name+'/'+rel)).hexdigest()!=h:
                raise RuntimeError('ZIP payload hash mismatch: '+rel)
    for src,newname in [(CONT/'publication/Continuation_Guide.pdf','Komorebi_Space_Formal_Continuation_Guide_v1.8.0.pdf'),(CONT/'PROGRESS_LEDGER.md','Komorebi_Space_Progress_Ledger_v1.8.0.md'),(CONT/'VERIFICATION_SUMMARY.json','Komorebi_Space_Formal_Verification_v1.8.0.json')]:
        shutil.copyfile(src,out/newname)
    receipt={'status':'PASS','zip':archive.name,'zip_bytes':archive.stat().st_size,'zip_sha256':digest(archive),'manifest_payload_files':len(manifest),'zip_entries':len(actual),'zip_crc_check':'PASS','complete_manifest_coverage':True,'every_payload_hash_matches':True,'runtime_included':False,'project_object_caches_included':False}
    (out/'Komorebi_Space_Delivery_Verification_v1.8.0.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
