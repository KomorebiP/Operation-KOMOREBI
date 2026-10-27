#!/usr/bin/env python3
"""Compatibility entry point for the current three-companion PDF build."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
lookup={'Paper_I_Traditional_Final.pdf':'traditional','Paper_I_Lean_Guide_Final.pdf':'lean_guide','Paper_I_Machine_Native_Final.pdf':'machine'}
cmd=[sys.executable,str(root/'scripts/build_pdfs.py')]
for arg in sys.argv[1:]:
 if arg in lookup: cmd += ['--component',lookup[arg]]
 elif arg in ['core-I']: pass
 else: raise SystemExit('Use no arguments, core-I, or a current PDF filename.')
subprocess.run(cmd,cwd=root,check=True)
