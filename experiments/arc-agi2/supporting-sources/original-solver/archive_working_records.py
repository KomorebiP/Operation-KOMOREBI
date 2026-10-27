"""Preserve completed working records before reclaiming duplicate disk storage.
Author: Komorebi P.
"""
from pathlib import Path
import hashlib
import json
import zipfile
import engine

ROOT = Path(__file__).resolve().parent


def main():
    records = ROOT/'results/final_legacy_census.tasks'
    paths = sorted(records.glob('*.json'))
    expected = {engine.contract.digest(k)+'.json' for k in engine.read(ROOT/'data/challenges.json')}
    assert {p.name for p in paths} == expected and len(paths) == 1000
    output = ROOT.parent/'Komorebi_PR_LASM_Block17_1000_Task_Records.zip'
    manifest = {}
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in paths:
            data = path.read_bytes()
            manifest[path.name] = {'sha256':hashlib.sha256(data).hexdigest(), 'bytes':len(data)}
            info = zipfile.ZipInfo('task_records/'+path.name, (2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compresslevel=6)
        archive.writestr('manifest.json', json.dumps(manifest, sort_keys=True, indent=2)+'\n')
    with zipfile.ZipFile(output) as archive:
        for name, row in manifest.items():
            data = archive.read('task_records/'+name)
            assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    result = engine.seal({'author':'Komorebi P.', 'records':1000,
        'archive':output.name, 'archive_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'all_archived_record_bytes_verified':True, 'removed_working_records':False,
        'files':manifest})
    engine.write(ROOT/'results/working_record_archive.json', result)
    print(json.dumps({k:v for k,v in result.items() if k!='files'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
