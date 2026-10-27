"""Check the exact delivered file set and SHA-256 hashes (not scientific truth)."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent
SKIP={'__pycache__','.pytest_cache'}
def files(root):
    return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(root).parts) and p.name!='MANIFEST.json'}
def main():
    m=json.loads((ROOT/'MANIFEST.json').read_text());found=files(ROOT);expected=m['files']
    if set(found)!=set(expected):raise AssertionError({'missing':sorted(set(expected)-set(found)),'extra':sorted(set(found)-set(expected))})
    for name,p in found.items():
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected[name]['sha256'] or p.stat().st_size!=expected[name]['bytes']:raise AssertionError(name)
    print(json.dumps({'status':'PASS','exact_file_set':True,'verified_files':len(found),'scope':'delivery integrity relative to manifest, not scientific certification'},indent=2))
if __name__=='__main__':main()
