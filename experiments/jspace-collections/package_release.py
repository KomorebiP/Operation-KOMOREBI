"""Build and verify a complete machinery archive. Author: Komorebi P."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(data): return hashlib.sha256(data).hexdigest()


def main():
    files = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and not any(part in ['__pycache__','.venv','runs'] for part in p.relative_to(ROOT).parts)
                   and p.name!='RELEASE_MANIFEST.json')
    manifest = {'author':'Komorebi P.','release':'J-space collections and actions v0.7',
                'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files}}
    path = ROOT/'RELEASE_MANIFEST.json';path.write_text(json.dumps(manifest,indent=2));files.append(path)
    archive = ROOT.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files: z.write(p,str(p.relative_to(ROOT.parent)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,info in manifest['files'].items():
            data = z.read(ROOT.name+'/'+name)
            assert len(data)==info['bytes'] and sha(data)==info['sha256']
    receipt = {'archive':str(archive),'members':len(files),'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'verified':True}
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
