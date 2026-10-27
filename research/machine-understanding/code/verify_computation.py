#!/usr/bin/env python3
"""Check the filled project-local computation manifest and its pinned files.
This checks record integrity and completeness, not the truth of mathematical claims.
"""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path,nargs='?',default=Path('validation/final/computation_manifest.json'))
    a=p.parse_args();m=json.loads((ROOT/a.manifest).read_text());errors=[]
    for k in ['schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks']:
        if k not in m:errors.append('Missing '+k)
    if m.get('run',{}).get('exit_status')!=0:errors.append('Execution did not succeed.')
    if m.get('group_count')!=38 or m.get('assertions')!=252669:errors.append('Unexpected finite inventory.')
    for group in ('outputs','input_artifacts'):
        if not m.get(group):errors.append('Empty '+group)
        for item in m.get(group,[]):
            name=Path(item['path']);q=(ROOT/name).resolve()
            if name.is_absolute() or not q.is_relative_to(ROOT):errors.append('Unsafe '+str(name));continue
            expected=item.get('sha256')
            if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):errors.append('Invalid hash '+str(name));continue
            if not q.is_file():errors.append('Missing '+str(name))
            elif hashlib.sha256(q.read_bytes()).hexdigest()!=expected:errors.append('Changed '+str(name))
            if group=='input_artifacts' and expected!=item.get('sha256_after'):errors.append('Changed during run '+str(name))
    print(json.dumps({'status':'passed' if not errors else 'failed','errors':errors,
                      'scope':'Project-local schema and checksum validation, not independent attestation.'},indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
