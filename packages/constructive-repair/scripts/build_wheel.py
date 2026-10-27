#!/usr/bin/env python3
"""Build one offline wheel in a fresh build process; needs local setuptools."""
from pathlib import Path
import argparse,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'dist');a=ap.parse_args()
    env=os.environ.copy();env.setdefault('SOURCE_DATE_EPOCH','1792368000')
    # A new interpreter avoids setuptools command state surviving a prior build.
    p=subprocess.run([sys.executable,'-c','import setuptools.build_meta as b; import sys; print(b.build_wheel(sys.argv[1]))',str(a.output.resolve())],cwd=ROOT,env=env)
    return p.returncode
if __name__=='__main__':raise SystemExit(main())
