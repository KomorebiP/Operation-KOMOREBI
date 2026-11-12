"""Current portable phase checks, including the full shunt-L class extension."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Assertions must remain enabled')
rows=[]
for script in ('check_current.py','check_shunt_extension.py'):
    result=subprocess.run([sys.executable,'-B','-S',str(ROOT/script)],capture_output=True,text=True,check=True,timeout=240)
    report=json.loads(result.stdout)
    if report['status']!='PASS':raise RuntimeError('Failed check: '+script)
    rows.append({'script':script,'report':report})
print(json.dumps({'status':'PASS','checks':rows,'scope':'Portable exact implementation and certificate controls; selected formal proof, classical characterization and analytic arguments have separately declared coverage.'},indent=2))
