#!/usr/bin/env python3
"""Deliberately invalid Lean claims must be rejected; none are active proof sources."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True)
a=ap.parse_args();root=Path(__file__).resolve().parents[1];rt=a.runtime.resolve();ws=rt/'workspace'
cases={
 'FalseEquality':'example : (1 : Nat) = 0 := by rfl\n',
 'Placeholder':'example : False := by sorry\n',
 'DroppedRoundingRadius':'import Komorebi.RationalBall\nexample : Komorebi.RoundedPosterior.Encloses ⟨0,0⟩ (1/1024) := by\n  unfold Komorebi.RoundedPosterior.Encloses\n  decide +kernel\n'}
results=[]
for name,text in cases.items():
    d=root/'results/negative_controls';d.mkdir(parents=True,exist_ok=True)
    source=d/(name+'.lean');source.write_text(text);staged=ws/('RoundedNegative'+name+'.lean');staged.write_text(text)
    argv=['bash',str(rt/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true',staged.name]
    t=time.monotonic();r=subprocess.run(argv,cwd=ws,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=25)
    (d/(name+'.log')).write_text(r.stdout)
    assert r.returncode!=0,(name,'unexpectedly accepted')
    results.append({'name':name,'argv':argv,'exit_status':r.returncode,'seconds':round(time.monotonic()-t,3),
      'expected_rejection':True,'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
      'log_sha256':hashlib.sha256(r.stdout.encode()).hexdigest()})
(root/'results/NEGATIVE_CONTROLS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
