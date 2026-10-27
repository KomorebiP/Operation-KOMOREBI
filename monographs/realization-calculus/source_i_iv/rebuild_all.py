#!/usr/bin/env python3
"""Rebuild styled I-IV texts and refresh only local page locators. No Lean or science run."""
from pathlib import Path
import subprocess,sys,json,os
R=Path(__file__).resolve().parent
env=dict(os.environ);env.setdefault('TMPDIR',str(R))
def run(name,*args):subprocess.run([sys.executable,str(R/name),*args],cwd=R,env=env,check=True)
run('build_components.py','I:traditional','I:lean','I:machine','III:analytic')
for attempt in range(4):
 run('build_components.py','II:traditional','III:traditional','IV:traditional')
 run('sync_navigation.py')
 if not json.loads((R/'navigation_updates.json').read_text())['changes']:break
else:raise SystemExit('Page locators did not stabilize.')
run('build_components.py','II:visual','II:lean','III:visual','III:lean','IV:lean')
run('inspect_components.py')
