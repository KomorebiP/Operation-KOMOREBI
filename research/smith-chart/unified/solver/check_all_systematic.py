"""One current replay entry preserving prior byte-bound consumers and records."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Assertions must remain enabled')
rows=[]
for script in ('check_systematic.py','check_cap_shunt_extension.py'):
    result=subprocess.run([sys.executable,'-B','-S',str(ROOT/script)],capture_output=True,text=True,check=True,timeout=240)
    report=json.loads(result.stdout)
    if report['status']!='PASS':raise RuntimeError('Failed check: '+script)
    rows.append({'script':script,'report':report})
print(json.dumps({'status':'PASS','checks':rows,'scope':'Exact finite controls, two quantified shunt-class refutation rules and preserved predecessor checks. Physical characterization and analytic bridges have separately scoped written proofs.'},indent=2))
