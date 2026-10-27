from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work13/Komorebi_LSM_Lean_0.13.0';out=b/'deliverables13';out.mkdir(exist_ok=True)
rep=json.loads((r/'verification/block13_release_run/report.json').read_text());assert rep['passed'] and rep['complete']
subprocess.run(['python3',str(b/'docs13.py')],check=True)
subprocess.run(['python3','scripts/build_inventory.py'],cwd=r,check=True)
subprocess.run(['python3','scripts/check_metadata.py','--out','verification/block13_metadata.json'],cwd=r,check=True)
(r/'verification/development_tools/package13.py').write_bytes((b/'package13.py').read_bytes())
paths=[p for p in sorted(r.rglob('*')) if p.is_file() and '.build' not in p.relative_to(r).parts and '__pycache__' not in p.relative_to(r).parts and p.suffix!='.pyc' and p.name!='MANIFEST.json']
manifest=dict(release='0.13.0',files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths})
(r/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');paths.append(r/'MANIFEST.json')
z=out/'Komorebi_Large_Signal_Model_Lean_0.13.0.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for p in paths: archive.write(p,r.name+'/'+str(p.relative_to(r)),compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED)
fresh=b/'fresh13';fresh.mkdir(exist_ok=True)
with zipfile.ZipFile(z) as archive:archive.extractall(fresh)
f=fresh/r.name
assert not (f/'.build').exists()
subprocess.run(['python3','scripts/verify_hashes.py'],cwd=f,check=True)
subprocess.run(['python3','scripts/build_inventory.py'],cwd=f,check=True)
subprocess.run(['python3','scripts/check_metadata.py'],cwd=f,check=True)
for src,suffix in [('LEAN_GUIDE.md','Guide.md'),('PROGRESS.md','Progress.md'),('AUDIT.md','Audit.md'),('COVERAGE.json','Coverage.json')]:shutil.copy2(r/src,out/('Komorebi_Large_Signal_Model_Lean_0.13.0_'+suffix))
receipt=dict(archive=str(z),archive_bytes=z.stat().st_size,archive_sha256=hashlib.sha256(z.read_bytes()).hexdigest(),declared_hashes=len(manifest['files']),archive_files=len(paths),source_report_sha256=hashlib.sha256((r/'verification/block13_release_run/report.json').read_bytes()).hexdigest(),fresh_extraction_had_no_project_objects=True)
(out/'packaging.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
