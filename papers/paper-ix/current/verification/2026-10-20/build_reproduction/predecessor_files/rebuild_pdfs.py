#!/usr/bin/env python3
"""Rebuild the frozen reading set in a separate directory, without changing the archive.
Requires installed TeX Live fonts, pdfLaTeX, XeLaTeX, and PyMuPDF. Does not download
anything, regenerate arithmetic figures, or compile Lean. PDF trailer identifiers
may differ by build location. All other bytes are compared against the release.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ID=re.compile(rb'(/ID\s*\[\s*<)[0-9a-fA-F]{32}(>\s*<)[0-9a-fA-F]{32}(>\s*\])')
def without_id(b:bytes)->bytes:
    return ID.sub(lambda m:m[1]+b'0'*32+m[2]+b'0'*32+m[3],b)
def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work-dir',type=Path);args=ap.parse_args()
    dest=args.work_dir.resolve() if args.work_dir else Path(tempfile.mkdtemp(prefix='paper_ix_rebuild_'))
    if dest==ROOT or dest.is_relative_to(ROOT):raise SystemExit('Use a build directory outside this frozen release.')
    if dest.exists() and any(dest.iterdir()):raise SystemExit('Build directory must be empty.')
    dest.mkdir(parents=True,exist_ok=True)
    for name in ('sources','figures','tools'):shutil.copytree(ROOT/name,dest/name)
    (dest/'publication/pdfs').mkdir(parents=True)
    shutil.copytree(ROOT/'publication/house_style',dest/'publication/house_style')
    for name in ('build_publication.py','documents.json'):shutil.copy2(ROOT/'publication'/name,dest/'publication'/name)
    run=subprocess.run([sys.executable,str(dest/'publication/build_publication.py')],cwd=dest,capture_output=True)
    (dest/'BUILD_TRANSCRIPT.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise SystemExit(f'Build failed. See {dest / "BUILD_TRANSCRIPT.txt"}')
    rows=[]
    for p in sorted((ROOT/'publication/pdfs').glob('*.pdf')):
        a=p.read_bytes();b=(dest/'publication/pdfs'/p.name).read_bytes()
        rows.append({'file':p.name,'byte_identical':a==b,'identical_except_trailer_id':without_id(a)==without_id(b),'frozen_sha256':hashlib.sha256(a).hexdigest(),'rebuilt_sha256':hashlib.sha256(b).hexdigest()})
    ok=all(x['identical_except_trailer_id'] for x in rows)
    report={'status':'PASS' if ok else 'FAIL','work_directory':str(dest),'documents':rows,'scope':'Every PDF byte except its generated trailer identifier. No fresh Lean execution. Original manifests identify frozen released PDFs, not these rebuilt files.'}
    (dest/'REBUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(not ok)
if __name__=='__main__':main()
