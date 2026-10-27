#!/usr/bin/env python3
"""Assemble a checked chart release while preserving every recovered prior file."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'polynomial_charts'
STAGE = ROOT / 'release_staging/PRSC_IX_Complete_Parameter_Charts'
RELEASE = STAGE.name
VERIFY = Path('/dev/shm/paper9_charts_recovered_04')
PRIOR = ROOT / 'recovery/PRSC_IX_Complete_Perturbation.zip'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_text())

def permitted(path, root):
    return (path.is_file() and not path.is_symlink()
            and not any(x in {'build', '__pycache__', '.lake', '.git'} for x in path.relative_to(root).parts)
            and path.suffix in {'.lean', '.py', '.md', '.json', '.log', '.txt', '.tex'})

def copy_group(source, destination):
    for path in sorted(source.rglob('*')):
        if permitted(path, source):
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            assert digest(target.read_bytes()) == digest(path.read_bytes()), target

def main():
    report_path = VERIFY / 'polynomial_charts_verification.json'
    report = read(report_path)
    reconciliation = read(PROJECT / 'audit/reconciliation.json')
    release_audit = read(STAGE / 'RELEASE_AUDIT.json')
    assert report['status'] == reconciliation['status'] == release_audit['status'] == 'PASS'
    assert release_audit['report_sha256'] == digest(report_path.read_bytes())
    assert reconciliation['report_sha256'] == digest(report_path.read_bytes())
    assert read(PROJECT / 'PROOFREAD_REVIEW.json')['status'] == 'PASS'
    assert (PROJECT / 'INDEPENDENT_PROOF_AUDIT.md').stat().st_size > 0
    assert digest(PRIOR.read_bytes()) == '61322b5b58a43def882cb77eff8dd00d8af44f803c99f97cce27c2e7f909f4e9'

    target = STAGE / 'polynomial_charts'
    if target.exists():
        shutil.rmtree(target)
    for group in ('formalization', 'scripts', 'contracts', 'controls', 'audit'):
        copy_group(PROJECT / group, target / group)
    copy_group(PROJECT / 'dev', target / 'development')
    copy_group(PROJECT / 'replay_recovered_01', target / 'development/interrupted_replay_recovered_01')
    copy_group(PROJECT / 'replay_recovered_02', target / 'development/interrupted_replay_recovered_02')
    copy_group(Path('/dev/shm/paper9_charts_recovered_03'), target / 'development/interrupted_replay_recovered_03')
    copy_group(VERIFY, target / 'verification')
    for path in sorted(PROJECT.iterdir()):
        if path.is_file() and path.suffix in {'.md', '.json'} and path.name != 'ARCHIVE_VALIDATION.json':
            shutil.copy2(path, target / path.name)
    assembly_target = STAGE / 'historical/recovered_charts_assembly'
    assembly_target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), assembly_target / Path(__file__).name)

    inventory = read(PROJECT / 'inventory.json')
    for group in ('modules', 'control_support', 'contracts', 'negative_controls'):
        for item in inventory[group]:
            assert digest((target / item['source']).read_bytes()) == item['sha256'], item['source']
    assert digest((target / 'inventory.json').read_bytes()) == report['inventory_sha256']
    for name, key in [('verify_polynomial_charts.py','verifier_sha256'),
                      ('source_audit.py','source_audit_sha256'),
                      ('check_source_audit.py','source_audit_regression_sha256'),
                      ('generate_inventory.py','inventory_generator_sha256'),
                      ('check_low_memory.py','runner_sha256')]:
        assert digest((target / 'scripts' / name).read_bytes()) == report[key], name
    for run in report['runs']:
        assert digest((target / 'verification' / run['log']).read_bytes()) == run['log_sha256']
    for path in [STAGE / 'replay_paper9_charts.py', *(target/'scripts').glob('*.py')]:
        ast.parse(path.read_text())

    current_hashes = {digest(path.read_bytes()) for path in STAGE.rglob('*') if path.is_file()}
    with zipfile.ZipFile(PRIOR) as archive:
        assert archive.testzip() is None
        old_entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        missing = [entry.filename for entry in old_entries if digest(archive.read(entry)) not in current_hashes]
        assert not missing, missing
    completeness = {
        'status':'PASS',
        'preserved_prior_archive':PRIOR.name,
        'preserved_prior_sha256':digest(PRIOR.read_bytes()),
        'prior_files':len(old_entries),
        'all_prior_uncompressed_file_hashes_covered':True,
        'missing_prior_file_hashes':0,
        'scope':'Recovered prior cumulative release plus fresh chart sources, verification, audits, and recovery provenance.',
        'historical_coverage':'Prior archive coverage records preserved; older ZIPs not independently downloaded and compared again during recovery.',
        'excluded':['Separate Lean runtime','Compiled outputs and caches','Incomplete recovery checkpoint ZIP','Lost pre-maintenance logs'],
        'limitations':['Historical manuscript not consolidated with every continuation','Older partial edge-source windows remain partial','Analyticity and weighted nonunit-Jacobian formalization remain open']
    }
    (STAGE/'PACKAGE_COMPLETENESS.json').write_text(json.dumps(completeness,indent=2)+'\n')
    rows=[]
    for path in sorted(STAGE.rglob('*')):
        assert not path.is_symlink(), path
        if not path.is_file() or path.name == 'MANIFEST.json' and path.parent == STAGE:
            continue
        assert not any(x in {'build','__pycache__','.lake','.git'} for x in path.relative_to(STAGE).parts), path
        assert not path.name.endswith(('.olean','.olean.server','.olean.private','.ir','.ir.sig','.pyc')), path
        rows.append({'path':str(path.relative_to(STAGE)),'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())})
    manifest={'release':RELEASE,'manifest_excludes_itself':True,'algorithm':'SHA-256',
              'file_count_excluding_manifest':len(rows),'files':rows}
    (STAGE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    output=ROOT/'output'/(RELEASE+'.zip')
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(STAGE.rglob('*')):
            if path.is_file():
                archive.write(path,str(Path(RELEASE)/path.relative_to(STAGE)))
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        expected={RELEASE+'/'+row['path'] for row in rows}|{RELEASE+'/MANIFEST.json'}
        assert len(archive.infolist()) == len(expected) and set(archive.namelist()) == expected
        for row in rows:
            data=archive.read(RELEASE+'/'+row['path'])
            assert len(data)==row['bytes'] and digest(data)==row['sha256']
        assert archive.read(RELEASE+'/MANIFEST.json') == (STAGE/'MANIFEST.json').read_bytes()
    result={'status':'PASS','archive':str(output),'bytes':output.stat().st_size,
            'sha256':digest(output.read_bytes()),'files':len(rows)+1,
            'prior_files_preserved':len(old_entries),'zip_crc':'PASS','all_entry_hashes':'PASS'}
    (PROJECT/'ARCHIVE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
