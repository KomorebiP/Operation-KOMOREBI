#!/usr/bin/env python3
"""Regenerate lesson figures and compile the expanded visual guide."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
FIGURE_SCRIPTS=['figures_foundations.py','figures_i_iii.py','figures_iv_vi.py','figures_vii_viii.py','figures_synthesis.py','figures_sequences.py','figures_polyphase.py','figures_taps.py','figures_bridges.py','figures_operators.py','figures_capstone.py']

def main():
    for name in FIGURE_SCRIPTS:
        subprocess.run([sys.executable,str(ROOT/name)],cwd=ROOT,check=True)
    for _ in range(3):
        subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],cwd=ROOT,check=True)
    result=ROOT/'Komorebi_Special_Functions_Expanded_Visual_Guide_v0.4.pdf'
    result.write_bytes((ROOT/'main.pdf').read_bytes())
    subprocess.run([sys.executable,str(ROOT/'validate_guide.py')],cwd=ROOT,check=True)
    print(json.dumps({'guide':str(result),'figure_scripts':len(FIGURE_SCRIPTS),'validated':True}))

if __name__=='__main__':main()
