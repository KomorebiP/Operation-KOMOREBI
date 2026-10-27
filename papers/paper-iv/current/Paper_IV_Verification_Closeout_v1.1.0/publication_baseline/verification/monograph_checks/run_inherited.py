#!/usr/bin/env python3
"""Execute an unchanged inherited verifier, redirecting only its result write.

The mathematical code and all input files retain their original bytes. The
write-only interception sends the one expected historical result into the
fresh bounded-run output directory, leaving the historical evidence untouched.
"""
from pathlib import Path
import argparse, runpy, sys
p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('historical_result');p.add_argument('fresh_result');a=p.parse_args()
expected=Path(a.historical_result).resolve();target=Path(a.fresh_result).resolve()
original=Path.write_text;redirected=[]
def guarded_write(self,*args,**kwargs):
    resolved=self.resolve()
    if resolved!=expected:raise RuntimeError('Unexpected write attempted: '+str(resolved))
    redirected.append({'historical':str(resolved),'fresh':str(target)})
    return original(target,*args,**kwargs)
sys.dont_write_bytecode=True
Path.write_text=guarded_write
try:runpy.run_path(a.script,run_name='__main__')
finally:Path.write_text=original
if len(redirected)!=1:raise RuntimeError('Expected exactly one redirected result write')
print('Historical result writes redirected: '+str(len(redirected)))
