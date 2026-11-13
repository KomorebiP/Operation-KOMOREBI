"""Current portable checks, preserving all predecessor evidence inputs.
Author: Komorebi P. Standard library only.
"""
from pathlib import Path
import json,subprocess,sys

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    root=Path(__file__).resolve().parent;reports=[]
    for name in ('check_breakthrough.py','check_coefficient_routes.py'):
        result=subprocess.run([sys.executable,'-B','-S',str(root/name)],check=True,
          capture_output=True,text=True,timeout=210)
        report=json.loads(result.stdout)
        if report['status']!='PASS':raise RuntimeError('Exact suite failed: '+name)
        reports.append({'script':name,'report':report})
    print(json.dumps({'status':'PASS','checks':reports},indent=2))
