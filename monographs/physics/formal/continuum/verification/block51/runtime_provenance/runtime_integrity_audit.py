from pathlib import Path
import datetime, hashlib, json, os
base=Path(__file__).resolve().parent
kit=base/'runtime/Komorebi_Portable_Lean_4.34.0-rc2'
manifest=kit/'verification/file-manifest.json'
data=json.loads(manifest.read_text())
result={'schema':'komorebi.runtime.integrity-audit.v1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'rows':len(data['files']),'mismatches':[],'unstable_during_read':[],'checked_bytes':0}
for row in data['files']:
 p=kit/row['path']
 if 'symlink' in row:
  actual=os.readlink(p) if p.is_symlink() else None
  if actual!=row['symlink']:result['mismatches'].append({'path':row['path'],'expected_symlink':row['symlink'],'actual_symlink':actual})
 elif not p.is_file():result['mismatches'].append({'path':row['path'],'error':'missing regular file'})
 else:
  before=p.stat()
  with p.open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
  after=p.stat();result['checked_bytes']+=after.st_size
  if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):result['unstable_during_read'].append(row['path'])
  if actual!=row['sha256']:result['mismatches'].append({'path':row['path'],'expected_sha256':row['sha256'],'actual_sha256':actual,'bytes':after.st_size})
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
result['all_declared_rows_match']=not result['mismatches'] and not result['unstable_during_read']
result['concurrency_note']='Parent baseline project compilation ran against symlinked dependencies during this audit. Git index or other changes are listed, not silently normalized.'
(base/'runtime_integrity_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
