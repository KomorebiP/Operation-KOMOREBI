#!/usr/bin/env python3
"""Invoke the exact guide checker and copy its actual result into a bounded run."""
from pathlib import Path
import argparse, importlib.util, json, sys
sys.dont_write_bytecode=True
def main():
    p=argparse.ArgumentParser();p.add_argument('--guide',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    checker=args.guide.resolve()/'checks/verify_portable.py'
    spec=importlib.util.spec_from_file_location('paper_viii_visual_exact',checker)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    mod.main()
    data=json.loads((args.guide/'checks/PORTABLE_CHECKS.json').read_text())
    assert data['status']=='PASS'
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
