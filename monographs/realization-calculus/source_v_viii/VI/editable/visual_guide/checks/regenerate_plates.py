#!/usr/bin/env python3
"""Regenerate the forty visual plates in a fresh stage and compare shipped geometry."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();stage=out/'working';(stage/'source').mkdir(parents=True);(stage/'graphics').mkdir()
 for n in ('models.py','generate_graphics.py','make_extension_plates.py'):shutil.copy2(ROOT/'source'/n,stage/'source'/n)
 for n in ('generate_graphics.py','make_extension_plates.py'):
  r=subprocess.run([sys.executable,'-B',str(stage/'source'/n)],cwd=stage,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);print(r.stdout,end='');r.check_returncode()
 target=out/'graphics';target.mkdir();rows=[]
 for source in sorted((ROOT/'graphics').glob('*.tex')):
  new=stage/'graphics'/source.name
  if not new.is_file():raise ValueError('Missing plate '+source.name)
  shutil.copy2(new,target/source.name)
  rows.append({'file':source.name,'shipped_sha256':h(source),'regenerated_sha256':h(new),'byte_identical':source.read_bytes()==new.read_bytes()})
 assert len(rows)==40
 assert set(n.name for n in (stage/'graphics').glob('*.tex'))==set(n['file'] for n in rows)
 for n in (stage/'graphics').glob('*.json'):shutil.copy2(n,target/n.name)
 report={'status':'PASS','plates':rows,'plate_count':len(rows),'byte_identical_count':sum(x['byte_identical'] for x in rows),'scope':'Regeneration checks supplied drawing geometry and labels; it is not an additional mathematical proof or numeric integration certificate.'}
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: regenerated all40vectorplates; byte-identical',report['byte_identical_count'])
if __name__=='__main__':main()
