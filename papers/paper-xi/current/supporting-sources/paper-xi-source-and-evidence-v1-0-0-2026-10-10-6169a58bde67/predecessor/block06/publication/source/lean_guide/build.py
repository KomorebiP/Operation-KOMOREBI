#!/usr/bin/env python3
"""Compatibility entry point for the coordinated three-reader build.

All readers must be built together to resolve their cross-document links.
The original build driver is retained in predecessor/block05.
"""
from pathlib import Path
import argparse,subprocess,sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--font-dir',type=Path)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[3]
    cmd=[sys.executable,str(root/'tools/build_readers.py'),'--output',str(a.output_dir)]
    if a.font_dir:cmd += ['--font-dir',str(a.font_dir)]
    raise SystemExit(subprocess.run(cmd).returncode)
if __name__=='__main__':main()
