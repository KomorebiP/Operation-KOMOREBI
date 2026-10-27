"""Package a self-contained release with member hashes. Author: Komorebi P."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(data): return hashlib.sha256(data).hexdigest()


def main():
    files = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and not any(part in ['__pycache__', '.venv'] or part.startswith('rerun')
                               for part in p.relative_to(ROOT).parts)
                   and p.name not in ['RELEASE_MANIFEST.json', 'scoring_stdout.json']
                   and p.parent != ROOT/'models')
    manifest = {'author':'Komorebi P.', 'release':'JSpace learned primitives v0.5',
                'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in files}}
    path = ROOT/'RELEASE_MANIFEST.json'; path.write_text(json.dumps(manifest,indent=2)); files.append(path)
    archive = ROOT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files: z.write(p, str(p.relative_to(ROOT.parent)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, info in manifest['files'].items():
            data = z.read(ROOT.name+'/'+name)
            assert len(data) == info['bytes'] and digest(data) == info['sha256']
    print(json.dumps({'archive':str(archive),'members':len(files),'bytes':archive.stat().st_size,
                      'sha256':digest(archive.read_bytes()),'verified':True},indent=2))


if __name__ == '__main__': main()
