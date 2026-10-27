from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work14/Komorebi_LSM_Lean_0.14.0';out=b/'deliverables14';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rep=json.loads((r/'verification/block14_release_run/report.json').read_text());assert rep['passed'] and rep['complete']
base=b/'deliverables13/Komorebi_Large_Signal_Model_Lean_0.13.0.zip'
assert sha(base)=='7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5'
refs=[]
with zipfile.ZipFile(base) as z:
 for p in sorted((r/'history').glob('*.zip')):
  if p.name=='PREDECESSOR_0.13.0_Source_Snapshot.zip':continue
  member='Komorebi_LSM_Lean_0.13.0/'+str(p.relative_to(r))
  digest=sha(p);assert hashlib.sha256(z.read(member)).hexdigest()==digest
  refs.append(dict(path=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=digest,original_archive_member=member))
 # Every removed payload has just been compared byte-for-byte to the saved base.
 for item in refs:(r/item['path']).unlink()
refdoc=dict(reason='Avoid repeated nested-archive payloads and disk exhaustion; all current sources, current and predecessor diagnostics, non-archive history, and the immediate predecessor source snapshot remain included.',source_archive=dict(name=base.name,sha256=sha(base),library_file_id='libfile_729eaed94db48191b7d4bdbc4ae19fea'),archived_payloads=refs)
(r/'HISTORY_ARCHIVE_REFERENCES.json').write_text(json.dumps(refdoc,indent=2)+'\n')
subprocess.run(['python3',str(b/'docs14.py')],check=True)
subprocess.run(['python3','scripts/build_inventory.py'],cwd=r,check=True)
subprocess.run(['python3','scripts/check_metadata.py','--out','verification/block14_metadata.json'],cwd=r,check=True)
(r/'verification/development_tools/package14.py').write_bytes((b/'package14.py').read_bytes())
paths=[p for p in sorted(r.rglob('*')) if p.is_file() and '.build' not in p.relative_to(r).parts and '__pycache__' not in p.relative_to(r).parts and p.suffix!='.pyc' and p.name!='MANIFEST.json']
manifest=dict(release='0.14.0',files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths})
(r/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');paths.append(r/'MANIFEST.json')
z=out/'Komorebi_Large_Signal_Model_Lean_0.14.0.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for p in paths:archive.write(p,r.name+'/'+str(p.relative_to(r)),compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED)
fresh=b/'fresh14';fresh.mkdir(exist_ok=True)
with zipfile.ZipFile(z) as archive:archive.extractall(fresh)
f=fresh/r.name;assert not (f/'.build').exists()
subprocess.run(['python3','scripts/verify_hashes.py'],cwd=f,check=True)
subprocess.run(['python3','scripts/build_inventory.py'],cwd=f,check=True)
subprocess.run(['python3','scripts/check_metadata.py'],cwd=f,check=True)
for src,suffix in [('LEAN_GUIDE.md','Guide.md'),('PROGRESS.md','Progress.md'),('AUDIT.md','Audit.md'),('COVERAGE.json','Coverage.json')]:shutil.copy2(r/src,out/('Komorebi_Large_Signal_Model_Lean_0.14.0_'+suffix))
receipt=dict(archive=str(z),archive_bytes=z.stat().st_size,archive_sha256=sha(z),declared_hashes=len(manifest['files']),archive_files=len(paths),source_report_sha256=sha(r/'verification/block14_release_run/report.json'),fresh_extraction_had_no_project_objects=True,older_nested_archive_payloads_referenced=len(refs))
(out/'packaging.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
