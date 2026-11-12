"""Run the two current exact suites. Author: Komorebi P."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
if not __debug__:
    raise RuntimeError('Run with assertions enabled')
reports = []
for name in ('check_deterministic_family.py','check_boundary_limits.py'):
    result = subprocess.run([sys.executable,'-B','-S',str(ROOT/name)],capture_output=True,text=True,check=True,timeout=180)
    report = json.loads(result.stdout)
    if report['status'] != 'PASS':
        raise RuntimeError('Unsuccessful exact check: '+name)
    reports.append({'script':name,'report':report})
print(json.dumps({'status':'PASS','suites':reports,'scope':'The declared exact finite checks; no universal proof verification'},indent=2))
