#!/usr/bin/env python3
"""Build the three licensed Komorebi Space readers. Does not run Lean."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, os
ROOT = Path(__file__).resolve().parents[1]
BOOKS = {"monograph":("Komorebi_Space_Monograph","Komorebi_Space"), "lean":("Komorebi_Space_Lean_Guide","Komorebi_Space_Lean_Guide"), "visual":("Komorebi_Space_Visual_Guide","Komorebi_Space_Visual_Guide")}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source_pins(): return {str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/"publication").rglob("*")) if p.is_file()}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book",choices=[*BOOKS,"all"],default="all")
    ap.add_argument("--output",type=Path,default=ROOT/"build/readers")
    args=ap.parse_args()
    if not shutil.which("pdflatex"):ap.error("pdflatex with the imported TeX Live packages is required")
    before=source_pins();reports=[];out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env["SOURCE_DATE_EPOCH"]="1792886400";env["FORCE_SOURCE_DATE"]="1"
    for book,(stem,pdfname) in BOOKS.items():
        if args.book not in (book,"all"):continue
        dest=out/book;dest.mkdir(parents=True,exist_ok=True)
        argv=["pdflatex","-interaction=nonstopmode","-halt-on-error","-file-line-error","-recorder","-output-directory="+str(dest),stem+".tex"]
        item={"book":book,"argv":argv,"passes":[]};reports.append(item)
        for n in range(1,4):
            with (dest/f"pass{n}.console.log").open("wb") as log:r=subprocess.run(argv,cwd=ROOT/"publication/volume_i/source",stdout=log,stderr=subprocess.STDOUT,env=env)
            item["passes"].append({"pass":n,"exit_code":r.returncode})
            if r.returncode:
                (out/"BUILD_REPORT.json").write_text(json.dumps({"status":"FAIL","reports":reports,"source_pins":before},indent=2)+"\n")
                raise SystemExit(f"LaTeX failed for {book}; inspect {dest}")
        text=(dest/(stem+".log")).read_text(errors="replace")
        item["layout_or_reference_warnings"]=[line for line in text.splitlines() if re.search(r"Overfull|undefined|multiply defined|Missing character|Rerun to get",line)]
        pdf=dest/(stem+".pdf");target=ROOT/"books"/(pdfname+".pdf");target.parent.mkdir(exist_ok=True)
        shutil.copy2(pdf,target);item["pdf"] = str(target.relative_to(ROOT));item["pdf_sha256"]=digest(target)
    unchanged=before==source_pins();status="PASS" if unchanged and all(not r["layout_or_reference_warnings"] for r in reports) else "FAIL"
    report={"status":status,"source_unchanged":unchanged,"source_pins":before,"reports":reports,"scope":"Publication build only. No Lean proof run."}
    (out/"BUILD_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print(status,[(r["book"],len(r["layout_or_reference_warnings"])) for r in reports])
    if status!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
