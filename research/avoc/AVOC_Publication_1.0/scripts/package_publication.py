"""Package user-facing documents and reproducible source; retain baseline ZIP."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / 'AVOC_Complete_Publication_Set.zip'
BASELINE_SHA = '04efab87010b3b88c9a119275e190423a2465da32ba1e526edb7e6d2e0cd077e'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    original = ROOT / 'inputs/AVOC_Formal_v0.41.0.zip'
    if sha(original) != BASELINE_SHA:
        raise RuntimeError('Formal baseline archive changed')
    pdfs = list((ROOT / 'output').glob('*.pdf'))
    if len(pdfs) != 3:
        raise RuntimeError('Expected exactly three final publication PDFs')
    files = [ROOT / 'README.md', ROOT / 'requirements-publication.txt', original]
    for folder in ['manuscripts', 'figures', 'scripts', 'reviews']:
        for path in (ROOT / folder).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.suffix in ['.pyc', '.lock'] or path.name == 'PACKAGE_MANIFEST.json':
                continue
            if folder == 'manuscripts' and path.suffix != '.tex':
                continue
            files.append(path)
    files.extend(pdfs)
    files = sorted(set(files), key=lambda p: str(p.relative_to(ROOT)))
    manifest = [{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in files]
    manifest_path = ROOT / 'PACKAGE_MANIFEST.json'
    manifest_path.write_text(json.dumps({'publication':'AVOC publication edition 1.0',
                                        'baseline_sha256':BASELINE_SHA,'files':manifest},indent=2)+'\n')
    with ZipFile(DESTINATION, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files + [manifest_path]:
            archive.write(path, 'AVOC_Publication_1.0/' + str(path.relative_to(ROOT)))
    with ZipFile(DESTINATION) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP CRC validation failed')
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise RuntimeError('Duplicate ZIP member')
        for record in manifest:
            data = archive.read('AVOC_Publication_1.0/' + record['path'])
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise RuntimeError('ZIP payload hash mismatch: ' + record['path'])
    report = {'archive':str(DESTINATION),'bytes':DESTINATION.stat().st_size,'sha256':sha(DESTINATION),
              'payload_files':len(files)+1,'zip_integrity':'PASS','payload_hashes':'PASS',
              'original_formal_archive_sha256':BASELINE_SHA,'fresh_lean_compilation':'NOT_RUN'}
    (ROOT.parent / 'AVOC_Publication_Package_Verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
