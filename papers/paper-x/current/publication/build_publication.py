#!/usr/bin/env python3
"""Build clean reader PDFs; return nonzero on any failed document or unresolved warning.
Requires Python, PyMuPDF, pdfLaTeX, XeLaTeX and the source's TeX packages.
No Lean compiler is invoked. Build the visual guide before embedding its atlas.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
import fitz
ROOT = Path(__file__).resolve().parents[1]
PDFS = ROOT / 'publication/pdfs'
BUILD = ROOT / 'publication/build'

def build_document(doc: dict, output_base: Path) -> dict:
    start = time.monotonic()
    source = ROOT / doc['main']
    key = Path(doc['file_name']).stem
    out = output_base / key
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    env = dict(os.environ)
    env.update(SOURCE_DATE_EPOCH='1791633600', FORCE_SOURCE_DATE='1', TZ='UTC')
    env['TEXINPUTS'] = str(out)+os.pathsep+str(ROOT/'publication/house_style')+os.pathsep+env.get('TEXINPUTS','')
    command = [doc['engine'],'-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),'-jobname='+key,source.name]
    logs=[]; status='failed'; errors=[]; passes=0
    for n in range(5):
        try:
            run=subprocess.run(command,cwd=source.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
            text=run.stdout.decode(errors='replace'); logs.append(text); passes+=1
        except (OSError,subprocess.TimeoutExpired) as exc:
            errors=[repr(exc)];break
        if run.returncode:
            errors=text.splitlines()[-30:];break
        if n>=2 and not re.search(r'Rerun to get cross-references right|Label\(s\) may have changed|Rerun to get outlines right',text):
            status='passed';break
    (out/'build_transcript.txt').write_text('\n'.join(logs))
    warnings=[]; pages=None; pdf=out/(key+'.pdf')
    if status=='passed':
        log=(out/(key+'.log')).read_text(errors='replace')
        warnings=[l for l in log.splitlines() if re.search(r'Warning:|Overfull|Missing character',l)]
        fatal=[l for l in warnings if re.search(r'Overfull|Missing character|undefined|multiply defined',l,re.I)]
        if fatal: status='failed'; errors=fatal
        elif not pdf.exists(): status='failed'; errors=['No PDF output']
        else:
            with fitz.open(pdf) as f: pages=len(f)
    return {'file_name':doc['file_name'],'status':status,'pages':pages,'passes':passes,'seconds':round(time.monotonic()-start,2),'errors':errors,'warnings':warnings,'pdf':str(pdf.relative_to(ROOT)) if pdf.is_relative_to(ROOT) else str(pdf)}

def append_atlas(main: Path, visual: Path, destination: Path) -> dict:
    with fitz.open(main) as m, fitz.open(visual) as v:
        base=len(m); source_pages=list(range(3,len(v)))
        assert len(source_pages)==30,'Expected exactly thirty atlas pages'
        bookmarks=m.get_toc()
        m.insert_pdf(v,from_page=3,to_page=len(v)-1,links=True,annots=True)
        # insert_pdf omits named-destination links; restore them as explicit internal targets.
        restored_links=0
        destinations=v.resolve_names()
        for vi in source_pages:
            for link in v[vi].get_links():
                name=link.get('nameddest')
                if name and name in destinations:
                    dest=destinations[name]; target=dest['page']
                    if target in source_pages:
                        point=fitz.Point(*dest['to'])*v[target].transformation_matrix
                        m[base+vi-3].insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],
                            'page':base+target-3,'to':point})
                        restored_links+=1
        for lev,title,page in v.get_toc():
            if page>=4: bookmarks.append([2,title,base+page-3])
        m.set_toc(bookmarks)
        m.set_page_labels([{'startpage':0,'prefix':'Cover'},{'startpage':1,'style':'D','firstpagenum':1},{'startpage':base,'prefix':'V','style':'D','firstpagenum':1}])
        m.save(destination,garbage=3,deflate=True,no_new_id=True)
        return {'base_pages':base,'appended_atlas_pages':len(source_pages),'total_pages':len(m),'restored_named_links':restored_links}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-directory',type=Path,default=BUILD)
    parser.add_argument('--output-directory',type=Path,default=PDFS)
    args=parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    docs=json.loads((ROOT/'publication/documents.json').read_text())
    order={'visual':0,'traditional':1,'lean':2};docs.sort(key=lambda x:order[x['kind']])
    results=[];atlas=None
    for d in docs:
        target=args.output_directory/d['file_name']
        if target.exists():target.unlink() # Never leave a stale success-shaped output.
        result=build_document(d,args.build_directory);results.append(result)
        if result['status']=='passed':
            src=Path(result['pdf']);src=src if src.is_absolute() else ROOT/src
            if d['kind']=='traditional':
                vp=args.output_directory/'Paper_X_Visual_Guide_Final.pdf'
                if not vp.exists():result['status']='failed';result['errors']=['Visual predecessor failed; atlas not appended']
                else:
                    atlas=append_atlas(src,vp,target);result['pages']=atlas['total_pages']
            else:shutil.copy2(src,target)
            if target.exists():result['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        print(json.dumps(result),flush=True)
    record={'documents':results,'atlas':atlas,'all_passed':all(x['status']=='passed' for x in results),'lean_compiler_invoked':False}
    args.build_directory.mkdir(parents=True,exist_ok=True)
    (args.build_directory/'BUILD_RESULTS.json').write_text(json.dumps(record,indent=2))
    if args.build_directory==BUILD:(ROOT/'publication/build_results.json').write_text(json.dumps(record,indent=2))
    return 0 if record['all_passed'] else 1
if __name__=='__main__':sys.exit(main())
