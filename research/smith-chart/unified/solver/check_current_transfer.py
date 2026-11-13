"""Current exact replay, preserving all predecessor inputs. Author: Komorebi P."""
from pathlib import Path
import json,subprocess,sys

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    root=Path(__file__).resolve().parent;checks=[]
    for name,timeout in (('check_current_regular.py',630),('check_backbone_transfer.py',90),
      ('lossless_separator.py',60),('check_transfer_consumer.py',90)):
        run=subprocess.run([sys.executable,'-B','-S',str(root/name)],capture_output=True,text=True,timeout=timeout,check=True)
        report=json.loads(run.stdout)
        if report['status']!='PASS':raise RuntimeError('Exact suite did not pass:'+name)
        checks.append({'script':name,'report':report})
    print(json.dumps({'status':'PASS','checks':checks},indent=2))
