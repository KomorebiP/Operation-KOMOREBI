"""Current exact suites including the finite mixed-loss certificate.
Author: Komorebi P. Standard library only; predecessor inputs stay unchanged.
"""
from pathlib import Path
import json,subprocess,sys

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    root=Path(__file__).resolve().parent
    reports=[]
    for name in ('check_all_systematic.py','check_loss_tolerance.py','check_two_reactive_margin.py'):
        result=subprocess.run([sys.executable,'-B','-S',str(root/name)],check=True,
          capture_output=True,text=True,timeout=200)
        report=json.loads(result.stdout)
        if report['status']!='PASS':raise RuntimeError('Exact suite failed: '+name)
        reports.append({'script':name,'report':report})
    print(json.dumps({'status':'PASS','checks':reports},indent=2))
