#!/usr/bin/env python3
"""Build this atlas with XeLaTeX without downloading dependencies."""
from pathlib import Path
import shutil,subprocess,sys,re
ROOT=Path(__file__).resolve().parent
NAME="Expanded_Visual_Guide"
def main():
    engine=shutil.which("xelatex")
    if not engine:
        print("XeLaTeX is required. Install a TeX distribution with the packages used in main.tex.",file=sys.stderr);return 1
    out=ROOT/"build";out.mkdir(exist_ok=True)
    for n in range(1,4):
        result=subprocess.run([engine,"-interaction=nonstopmode","-halt-on-error","-file-line-error",f"-jobname={NAME}",f"-output-directory={out}","main.tex"],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/f"pass_{n}.txt").write_text(result.stdout,encoding="utf-8")
        if result.returncode: print(result.stdout[-9000:],file=sys.stderr);return result.returncode
    log=(out/(NAME+".log")).read_text(errors="replace")
    errors=[x for x in ("Undefined control sequence", "Missing character:", "There were undefined references", "Overfull ") if x in log]
    if errors: print("Layout review required: "+", ".join(errors),file=sys.stderr);return 2
    print(out/(NAME+".pdf"));return 0
if __name__=="__main__":raise SystemExit(main())
