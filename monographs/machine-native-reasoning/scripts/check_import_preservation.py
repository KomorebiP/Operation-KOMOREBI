#!/usr/bin/env python3
"""Check that the verifier import optimization retains every other checker byte."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 rows=json.loads((ROOT/'checks/IMPORT_SCOPE_CHANGES.json').read_text())['changes'];checks={}
 for row in rows:
  old=(ROOT/row['original_path']).read_bytes();new=(ROOT/row['path']).read_bytes()
  prefix=('\n'.join('import '+s for s in row['new_imports'])+'\n').encode()
  checks[row['path']]={'original_hash':digest(old)==row['original_sha256'],
    'original_umbrella':old.startswith(b'import MachineTheory\n'),
    'exact_new_imports':new.startswith(prefix),
    'all_other_bytes_unchanged':new[len(prefix):]==old[len(b'import MachineTheory\n'):],
    'body_hash':digest(new[len(prefix):])==row['nonimport_sha256']}
 result={'schema':'komorebi.core24.checker-body-preservation.v1','status':'PASS' if all(v for row in checks.values() for v in row.values()) else 'FAIL','checker_files':len(rows),'checks':checks,'scope':'Import declarations only. Whole-library production compilation, actual axiom inventory, kernel replays and the complete control manifest remain required.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows),'checker bodies unchanged')
 return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
