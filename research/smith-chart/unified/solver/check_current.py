"""Single current portable exact-check entry. Author: Komorebi P."""
from pathlib import Path
import json,subprocess,sys

ROOT=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run with assertions enabled')
rows=[]
for name in ('check_all.py','check_phase2.py','reactive_skeletons.py'):
    result=subprocess.run([sys.executable,'-B','-S',str(ROOT/name)],capture_output=True,
        text=True,check=True,timeout=240)
    report=json.loads(result.stdout)
    if report['status']!='PASS':raise RuntimeError('Exact check failed: '+name)
    rows.append({'script':name,'report':report})
print(json.dumps({'status':'PASS','checks':rows,
    'scope':'Current finite exact controls and source-bound certificate replay; formal proofs and external source implications have separate records. Optional mixed-NRA search is not part of this standard-library check.'},indent=2))
