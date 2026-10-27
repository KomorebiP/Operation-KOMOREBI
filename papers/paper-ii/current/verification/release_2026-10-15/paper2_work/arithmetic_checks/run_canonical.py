from pathlib import Path
import json,subprocess,sys
base=Path('/workspace/scratch/9f53d520971c')
checks=base/'paper2_work/arithmetic_checks'
source=base/'release_package/Komorebi_Paper_II_Release_2026-10-15/formal/current'
runtime=base/'release_work/runtime/Komorebi_Portable_Lean_4.34.0-rc2'
plan=[('ReleaseGluingDVR','dvr',['gluing']),('ReleaseGluingSmith','smith',['gluing']),('ReleaseGluingBinary','binary',['gluing']),('ReleasePrecisionQuotient','precision_quotient',['gluing']),('ReleaseGluingPrecisionBridge','precision_bridge',['dvr','precision']),('ReleaseGluingFinite','finite',['dvr','smith']),('ReleaseGluingEquivSmith','equiv_smith',['smith'])]
for module,key,deps in plan:
 for dep in deps:
  receipt=checks/f'canonical_{dep}_01/CHECK.json'
  if json.loads(receipt.read_text())['status']!='PASS':raise RuntimeError(str(receipt)+' not PASS')
 cmd=[sys.executable,str(base/'paper2_work/tools/check_module.py'),'--source-root',str(source),'--module','KomorebiVerification.PaperII.'+module,'--output',str(checks/f'canonical_{key}_01'),'--runtime',str(runtime),'--timeout','90']
 for dep in deps:cmd+=['--extra-objects',str(checks/f'canonical_{dep}_01/objects')]
 p=subprocess.run(cmd,capture_output=True,text=True)
 d=json.loads((checks/f'canonical_{key}_01/CHECK.json').read_text())
 print(module,d['status'],flush=True)
 if p.returncode:
  print((checks/f'canonical_{key}_01/compile.log').read_text(),flush=True)
  sys.exit(p.returncode)
