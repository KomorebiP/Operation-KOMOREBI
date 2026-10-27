from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EXCLUDE={"package_manifest.json"}
IGNORE_PREFIXES={".pytest_cache/","__pycache__/","block23/__pycache__/","block23/external/__pycache__/","tests/__pycache__/"}
IGNORE_SUFFIXES={".pyc",".aux",".fdb_latexmk",".fls",".log",".out",".toc",".synctex.gz"}

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()

def main():
    files={}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or any(rel.startswith(x) for x in IGNORE_PREFIXES) or any(rel.endswith(x) for x in IGNORE_SUFFIXES):
            continue
        files[rel]={"sha256":sha(p),"size_bytes":p.stat().st_size}
    payload={"schema":"sric.package-manifest.v1","files":files}
    (ROOT/'package_manifest.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(f"BLOCK23_MANIFEST_FILES={len(files)}")
    print(f"BLOCK23_MANIFEST_SHA256={sha(ROOT/'package_manifest.json')}")
if __name__=='__main__':main()
