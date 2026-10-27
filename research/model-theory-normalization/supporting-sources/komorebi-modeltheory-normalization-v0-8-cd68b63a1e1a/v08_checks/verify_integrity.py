#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 data=json.loads((ROOT/'FILE_MANIFEST.json').read_text());bad=[]
 for item in data['files']:
  p=ROOT/item['path']
  if not p.is_file() or p.stat().st_size!=item['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:bad.append(item['path'])
 print(json.dumps({'status':'PASS' if not bad else 'FAIL','files_checked':len(data['files']),'failures':bad}))
 if bad:sys.exit(1)
if __name__=='__main__':main()
