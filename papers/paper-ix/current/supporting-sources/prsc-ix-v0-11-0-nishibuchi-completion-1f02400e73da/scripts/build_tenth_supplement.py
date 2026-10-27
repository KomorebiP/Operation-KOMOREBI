#!/usr/bin/env python3
"""Rebuild the completion supplement into a new directory. Requires pdflatex, not Lean."""
from pathlib import Path
import argparse,shutil,subprocess,tempfile,re,sys,datetime
root=Path(__file__).resolve().parents[1]
name="Paper_IX_All_Residue_Completion_Supplement"
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir",type=Path)
args=parser.parse_args()
out=args.output_dir or root/"verification/document_rebuild"/datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
out.mkdir(parents=True,exist_ok=False)
shutil.copy2(root/"docs"/(name+".tex"),out)
for _ in range(2):
    result=subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error",name+".tex"],cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
    if result.returncode:
        print(result.stdout);sys.exit(result.returncode)
log=(out/(name+".log")).read_text()
if re.search(r"Overfull|Underfull|Warning|undefined references",log):
    print(log);raise SystemExit("PDF diagnostics require review")
print("Rebuilt PDF:",out/(name+".pdf"))
print("Render and visually inspect before distributing a replacement PDF.")
