"""Current portable checks preserving every predecessor replay.
Author: Komorebi P. Standard library only.
"""
from pathlib import Path
import json,subprocess,sys

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    root=Path(__file__).resolve().parent;reports=[]
    for name in ('check_stable_energy.py','check_global_typed.py'):
        run=subprocess.run([sys.executable,'-B','-S',str(root/name)],capture_output=True,text=True,check=True,timeout=260)
        report=json.loads(run.stdout)
        if report['status']!='PASS':raise RuntimeError('Exact suite failed: '+name)
        reports.append({'script':name,'report':report})
    print(json.dumps({'status':'PASS','checks':reports},indent=2))
