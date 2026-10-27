#!/usr/bin/env python3
"""Package all surviving Euler research and the immutable latest checkpoint."""
from pathlib import Path
import argparse,hashlib,json,zipfile

DIRECTORIES=[
 'Euler_Address_One_Continuation_2026-10-05',
 'Euler_Regular_Address_and_Critical_Phases_2026-10-05',
 'audit_helpers','carry_audit','independent_review','inputs',
 'local_parameter','next','recovered','sources','transversality',
]
FILES=[
 'Euler_Address_One_Continuation_2026-10-05.zip',
 'Euler_Regular_Address_and_Critical_Phases_2026-10-05.zip',
 'FINAL_ARTIFACT.json',
]
EXPECTED_LATEST='19878d2553a5a5cbada8791e7751b37fdbe73422b6c0da9893a9d9e178c49c96'

def digest(path):
 with path.open('rb') as stream:
  return hashlib.file_digest(stream,'sha256').hexdigest()

def eligible(path,root):
 parts=path.relative_to(root).parts
 return path.is_file() and not path.is_symlink() and '__pycache__' not in parts \
  and not any(part.startswith('.') for part in parts) and path.suffix!='.pyc'

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--root',type=Path,required=True)
 parser.add_argument('--latest',type=Path,required=True)
 parser.add_argument('--coverage',type=Path,required=True)
 parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args()
 root=args.root.resolve();latest=args.latest.resolve()
 assert digest(latest)==EXPECTED_LATEST
 name='Euler_Complete_Work_2026-10-05'
 items={}
 for directory in DIRECTORIES:
  base=root/directory
  assert base.is_dir(),str(base)
  for path in sorted(base.rglob('*')):
   if eligible(path,root):items['WORKSPACE/'+str(path.relative_to(root))]=path
 for relative in FILES:
  path=root/relative
  assert path.is_file(),str(path)
  items['WORKSPACE/'+relative]=path
 items['LATEST/'+latest.name]=latest
 for path in sorted(args.coverage.resolve().rglob('*')):
  if eligible(path,args.coverage.resolve()):
   items['PACKAGING/coverage/'+str(path.relative_to(args.coverage.resolve()))]=path
 items['PACKAGING/build_complete_euler.py']=Path(__file__).resolve()

 # Require all local research files in the independent snapshot, rather
 # than merely trusting a hand-picked list of directory names.
 inventory=json.loads((args.coverage/'local_inventory.json').read_text())
 if isinstance(inventory,dict):
  entries=inventory.get('files',inventory.get('entries',inventory.get('records')))
 else:entries=inventory
 assert isinstance(entries,list),type(inventory)
 for entry in entries:
  relative=entry.get('path',entry.get('relative_path'))
  assert 'WORKSPACE/'+relative in items,relative
  assert digest(items['WORKSPACE/'+relative])==entry['sha256'],relative

 records={relative:{'sha256':digest(path),'bytes':path.stat().st_size}
          for relative,path in sorted(items.items())}
 manifest={
  'bundle':name,'scope':'Complete surviving Euler workspace plus immutable latest checkpoint and its full archive ancestry',
  'latest_checkpoint':'LATEST/'+latest.name,'latest_sha256':EXPECTED_LATEST,
  'mathematical_goal_status':'open; no mathematical claim changed by packaging',
  'workspace_files':len([p for p in records if p.startswith('WORKSPACE/')]),
  'files':records,
  'excluded':'Private file-transfer helpers, private metadata, Python caches, and filesystem placeholders',
 }
 start='''# Complete Euler work\n\n
This archive collects the latest stationary-separation checkpoint and every
surviving Euler research file from this workspace, including older Lean
sources, Python code, proofs, figures, papers, stored results, audits, and
historical releases. Original research files and archives are unchanged.

## Latest work

Extract `LATEST/Euler_Stationary_Separation_2026-10-05.zip` first. Read its
`stationary_separation/README.md` and `SYNTHESIS.md`. That self-contained
checkpoint includes its immutable parent archives, exact computations,
independent reviews, and reproduction instructions.

The Euler simplicity goal remains open. The latest checkpoint records
proved reductions and approximation results, with the remaining actual
stationary-discriminant nonvanishing obligation stated explicitly.

## All earlier work

`WORKSPACE/` retains the original layouts of the surviving working files.
It includes earlier Address One and Critical Phases checkpoints, all
recovered releases, the four original input archives, the standalone
recenter package, and stored Lean sources and results. Run historical
scripts from their original working roots. Their stored mathematical and
verification status is unchanged; Lean was not rerun for this packaging.

`PACKAGING/coverage/` explains why the latest checkpoint alone was
insufficient. It identifies the additional historical files by content
hash, and retains the read-only coverage audit and recursive archive index.

## Verify

Run `python3 verify_bundle.py` from this extracted directory. It checks
the saved content hashes. The outer ZIP was also CRC-tested after creation.
The latest checkpoint's own verifier and reproduction instructions remain
inside its unchanged archive.
'''
 verifier='''#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
data=json.loads((root/'MANIFEST.json').read_text())
for relative,record in data['files'].items():
 with (root/relative).open('rb') as stream:
  actual=hashlib.file_digest(stream,'sha256').hexdigest()
 if actual!=record['sha256']:raise SystemExit('Hash mismatch: '+relative)
print(str(len(data['files']))+' research and provenance files verified.')
'''
 extra={'START_HERE.md':start.encode(),'verify_bundle.py':verifier.encode()}
 for relative,data in extra.items():
  manifest['files'][relative]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 metadata=json.dumps(manifest,indent=2).encode()+b'\n'
 (args.output.parent/'Euler_Complete_Packaging_Manifest.json').write_bytes(metadata)
 with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as bundle:
  for relative,path in sorted(items.items()):
   compression=zipfile.ZIP_STORED if path.suffix.lower() in {'.zip','.pdf','.png','.jpg','.jpeg','.gif'} else zipfile.ZIP_DEFLATED
   bundle.write(path,name+'/'+relative,compress_type=compression)
  for relative,data in extra.items():bundle.writestr(name+'/'+relative,data)
  bundle.writestr(name+'/MANIFEST.json',metadata)
 with zipfile.ZipFile(args.output) as bundle:
  assert bundle.testzip() is None
  for relative,record in manifest['files'].items():
   with bundle.open(name+'/'+relative) as stream:
    actual=hashlib.file_digest(stream,'sha256').hexdigest()
   assert actual==record['sha256'],relative
  members=len(bundle.namelist())
 report={'status':'passed','archive':str(args.output.resolve()),
  'sha256':digest(args.output),'bytes':args.output.stat().st_size,
  'members':members,'workspace_files':manifest['workspace_files'],
  'latest_preserved_unchanged':True,'all_snapshot_files_included':True,
  'validation':'Every included content hash checked, ZIP CRC passed',
  'mathematical_goal_status':'open'}
 (args.output.parent/'Euler_Complete_Packaging_Result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
