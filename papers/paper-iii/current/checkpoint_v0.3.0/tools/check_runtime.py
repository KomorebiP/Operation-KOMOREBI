#!/usr/bin/env python3
"""Authenticate exact runtime binaries and the nine pinned package revisions."""
from pathlib import Path
import argparse,hashlib,json,subprocess

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--kit',type=Path,required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1]
 expected={
 'toolchain/bin/lean':'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550',
 'toolchain/bin/lake':'6f53827dab18010d6c690d14c8401cacabc1db958edb3552a877ed4cf1dd995d',
 'toolchain/src/lean/LeanChecker.lean':'2d18ec111d73c536b0bdee2533556bb9548c349f386797d3d3837b1f84d55dae'}
 checks=[]
 for f,h in expected.items():
  got=sha(a.kit/f);checks.append({'file':f,'expected_sha256':h,'actual_sha256':got,'pass':h==got})
 manifest=json.loads((r/'formal/current/lake-manifest.json').read_text());pins=[]
 for package in manifest['packages']:
  git=a.kit/'workspace/.lake/packages'/package['name']
  run=subprocess.run(['git','-C',str(git),'rev-parse','HEAD'],capture_output=True,text=True)
  actual=run.stdout.strip();pins.append({'package':package['name'],'expected':package['rev'],'actual':actual,'pass':actual==package['rev'] and run.returncode==0})
 version=subprocess.check_output([str(a.kit/'toolchain/bin/lean'),'--version'],text=True).strip()
 result={'schema':'paper-iii.runtime-identity/1','status':'PASS' if all(x['pass'] for x in checks+pins) and len(pins)==9 else 'FAIL','lean_version':version,'binary_checks':checks,'dependency_pins':pins,'upstream_rebuilt':False,'archive_receipt':'verification/RUNTIME_ARCHIVE.json'}
 (r/'verification/RUNTIME_IDENTITY.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(checks),len(pins));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
