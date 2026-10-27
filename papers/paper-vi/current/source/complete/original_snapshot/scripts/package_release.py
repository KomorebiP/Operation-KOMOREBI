"""Author: Komorebi P. Freeze and verify a source-only distributable release."""
from pathlib import Path
import argparse,hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def include(p):
    rel=p.relative_to(R)
    if any(x in ('.lake','__pycache__','.pytest_cache') for x in rel.parts):return False
    if p.suffix in ('.pyc','.aux','.out','.toc','.lof','.lot','.fls','.fdb_latexmk','.synctex.gz'):return False
    if 'manuscript' in rel.parts and p.suffix=='.log':return False
    return p.is_file() and p.name!='RELEASE_MANIFEST.json'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args()
    report=json.loads((R/'verification/verification_status.json').read_text())
    if report['status']!='LEAN_FIFTH_BLOCK_CHECKS_PASS':raise RuntimeError('Missing successful Lean report')
    import importlib.util
    spec=importlib.util.spec_from_file_location('release_verify',R/'verification/verify.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    if verifier.static_checks(R)!=report['gates']['source']:
        raise RuntimeError('Source check differs from the audited report')
    pdf=json.loads((R/'verification/pdf_validation.json').read_text())
    if pdf['visual_review']!='PASS' or pdf['pdf_sha256']!=digest(R/'manuscript/Paper_VI_Reviewed.pdf'):
        raise RuntimeError('PDF validation missing or stale')
    # Skip cache directories before walking, including the mathlib dependency symlink.
    import os
    files=[]
    for root,dirs,names in os.walk(R,followlinks=False):
        dirs[:]=[d for d in dirs if d not in ('.lake','__pycache__','.pytest_cache')]
        for name in names:
            p=Path(root)/name
            if include(p):files.append(p)
    files.sort()
    manifest={'release':'0.5.0-checked-fifth-block','author':'Komorebi P.','sha256':{p.relative_to(R).as_posix():digest(p) for p in files}}
    m=R/'RELEASE_MANIFEST.json';m.write_text(json.dumps(manifest,indent=2)+'\n')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in files+[m]:z.write(p,arcname=R.name+'/'+p.relative_to(R).as_posix())
    with zipfile.ZipFile(args.output) as z:
        if z.testzip() is not None:raise RuntimeError('Archive CRC check failed')
        for rel,expected in manifest['sha256'].items():
            if hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()!=expected:raise RuntimeError('Archive hash mismatch: '+rel)
        if len(z.namelist())!=len(files)+1:raise RuntimeError('Unexpected archive member')
    print(json.dumps({'zip':str(args.output.resolve()),'members':len(files)+1,'bytes':args.output.stat().st_size,'sha256':digest(args.output),'manifest_verified':True}))
if __name__=='__main__':main()
