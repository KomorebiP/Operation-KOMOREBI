#!/usr/bin/env python3
"""Replay original18 numerical toy checks without generating old figures.

These are deterministic float64 implementation illustrations with tolerances.
They are not exact certificates of algebraic cycles on a supplied variety.
"""
import argparse,importlib.util,json,sys
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    spec=importlib.util.spec_from_file_location('hodge_numeric_toys',a.source)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    checks,result=module.run_checks()
    assert all(c.passed for c in checks)
    result['series06_scope']='18 deterministic floating-point toy checks. No actual variety/cycle proof.'
    result['coefficient_domain']='IEEE float64, with declared tolerances'
    result['random_generators']='NumPy default_rng seeds7,11,17,23,29,3 in run_checks call paths'
    a.out.write_text(json.dumps(result,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')
    print('PASS:',len(checks),'numerical toy checks; no original figures generated')
if __name__=='__main__':main()
