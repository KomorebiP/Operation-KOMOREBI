#!/usr/bin/env python3
"""Attach an existing exact-pinned offline cache; never replace a real directory."""
from pathlib import Path
import argparse,json,subprocess
p=argparse.ArgumentParser();p.add_argument('runtime',type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[1]; runtime=a.runtime.resolve()
v=subprocess.check_output([str(runtime/'toolchain/bin/lean'),'--version'],text=True)
if '4.34.0-rc2' not in v or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in v:
    raise SystemExit('Wrong Lean identity: '+v)
manifest=json.loads((root/'lake-manifest.json').read_text())
packages=root/'.lake/packages';packages.mkdir(parents=True,exist_ok=True)
for d in manifest['packages']:
    src=runtime/'workspace/.lake/packages'/d['name']
    rev=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
    if rev != d['rev']: raise SystemExit('Dependency revision mismatch: '+d['name'])
    dst=packages/d['name']
    if dst.is_symlink():
        if dst.resolve()!=src.resolve(): dst.unlink()
    elif dst.exists():
        raise SystemExit('Refusing to replace directory: '+str(dst))
    if not dst.exists(): dst.symlink_to(src,target_is_directory=True)
    print(d['name'],rev)
print('Ready. Put '+str(runtime/'toolchain/bin')+' first on PATH before invoking Lake.')
