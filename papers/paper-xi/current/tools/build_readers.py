#!/usr/bin/env python3
"""Build the three synchronized Paper XI readers without modifying checkpoint files.

Requires XeLaTeX, pdfLaTeX, BibTeX (bibtex.original is accepted), PyMuPDF,
and locally installed URW P052/Nimbus Sans and DejaVu fonts. No font files are
bundled. --font-dir may identify a locally installed URW OTF directory.
No network, shell escape, Lean compiler or figure generator is invoked.

Full build: python tools/build_readers.py --output /absolute/new-directory
Bounded stages: use --stage traditional, visual_guide, lean_guide, then assemble
against the same output directory. Repeating a compiled stage is refused.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
import fitz
KINDS={'traditional':'Paper_XI_Traditional_Final','visual_guide':'Paper_XI_Visual_Guide_Final','lean_guide':'Paper_XI_Lean_Guide_Final'}
PREFIX='https://komorebi.invalid/b07/'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint(root:Path)->str:
    h=hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if p.is_file():h.update(str(p.relative_to(root)).encode()+b'\0'+bytes.fromhex(sha(p)))
    return h.hexdigest()
def group(s:str,start:int)->tuple[str,int]:
    if s[start]!='{':raise ValueError('Expected brace')
    level=1;i=start+1
    while level:
        if i>=len(s):raise ValueError('Unbalanced auxiliary label')
        if s[i]=='{' and s[i-1]!='\\':level+=1
        if s[i]=='}' and s[i-1]!='\\':level-=1
        i+=1
    return s[start+1:i-1],i

def labels(aux:Path)->dict:
    result={}
    for line in aux.read_text(errors='strict').splitlines():
        if not line.startswith('\\newlabel{'):continue
        key,end=group(line,len('\\newlabel'));value,end=group(line,end)
        fields=[];i=0
        while i<len(value) and value[i]=='{':
            field,i=group(value,i);fields.append(field)
        if len(fields)>=4:result[key]={'number':fields[0],'printed_page':fields[1],'destination':fields[3]}
    return result

def font_directory(given:Path|None)->Path:
    if given is not None:p=given.resolve()
    else:
        fc=shutil.which('fc-match')
        if not fc:raise SystemExit('Supply --font-dir pointing to installed URW OTF fonts')
        q=subprocess.run([fc,'-f','%{file}','P052:style=Roman'],capture_output=True,text=True,check=True)
        p=Path(q.stdout).resolve().parent
    required=['P052-Roman.otf','P052-Italic.otf','P052-Bold.otf','P052-BoldItalic.otf','NimbusSans-Regular.otf','NimbusSans-Bold.otf','NimbusSans-Italic.otf','NimbusSans-BoldItalic.otf']
    if any(not (p/n).is_file() for n in required):raise SystemExit('URW OTF family incomplete in '+str(p))
    return p

def compile_one(root:Path,out:Path,kind:str,fontdir:Path|None)->dict:
    receipt=out/f'COMPILE_{kind}.json'
    if receipt.exists():raise SystemExit(f'{kind} already compiled. Use a new output directory to rebuild')
    stem=KINDS[kind];work=out/'build'/kind
    if work.exists():raise SystemExit('Staging directory already exists: '+str(work))
    shutil.copytree(root/'publication/source'/kind,work)
    fdir=font_directory(fontdir) if kind!='visual_guide' else None
    if fdir:
        (work/'komorebi-font-paths.tex').write_text(r'\providecommand{\KomorebiFontDirectory}{'+fdir.as_posix()+'/}\n')
    engine=shutil.which('pdflatex' if kind=='visual_guide' else 'xelatex')
    bib=shutil.which('bibtex') or shutil.which('bibtex.original')
    if not engine or (kind=='traditional' and not bib):raise SystemExit('Required TeX engine not found')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',SOURCE_DATE_EPOCH='1792281600',FORCE_SOURCE_DATE='1',TZ='UTC')
    latex=[engine,'-no-shell-escape','-recorder','-interaction=nonstopmode','-halt-on-error',stem+'.tex']
    cmds=[latex]
    if kind=='traditional':cmds.append([bib,stem])
    cmds += [latex]*2
    runs=[];t=time.monotonic()
    for i,cmd in enumerate(cmds,1):
        q=subprocess.run(cmd,cwd=work,env=env,capture_output=True,text=True,timeout=180)
        (work/f'pass_{i}.stdout.log').write_text(q.stdout+q.stderr)
        runs.append({'command':cmd,'returncode':q.returncode})
        if q.returncode:raise SystemExit(f'{kind} step {i} failed; inspect {work}/pass_{i}.stdout.log')
    log=(work/(stem+'.log')).read_text(errors='replace')
    diag=[x for x in log.splitlines() if any(t in x for t in ['Warning:','Overfull','Underfull','Missing character'])]
    local=[]
    for line in (work/(stem+'.fls')).read_text(errors='replace').splitlines():
        if not line.startswith('INPUT '):continue
        p=Path(line[6:]);p=(work/p).resolve() if not p.is_absolute() else p.resolve()
        if p.is_relative_to(work) and p.is_file():
            rp=str(p.relative_to(work))
            if rp not in local:local.append(rp)
    with fitz.open(work/(stem+'.pdf')) as pdf:pages=len(pdf)
    rec={'status':'compiled','kind':kind,'source_fingerprint':fingerprint(root/'publication/source'/kind),'commands':runs,'pages':pages,'diagnostics':diag,'local_inputs':local,'raw_sha256':sha(work/(stem+'.pdf')),'font_directory':str(fdir) if fdir else None,'seconds':round(time.monotonic()-t,3)}
    receipt.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2),flush=True)
    return rec

def assemble(root:Path,out:Path)->None:
    manifest=json.loads((root/'evidence/release_1_1/READING_ROUTES.json').read_text());names=manifest['pdfs'];docs={};parsed={};records={}
    for kind,stem in KINDS.items():
        rec=json.loads((out/f'COMPILE_{kind}.json').read_text())
        if rec['source_fingerprint']!=fingerprint(root/'publication/source'/kind):raise SystemExit('Source changed after compilation: '+kind)
        work=out/'build'/kind
        if sha(work/(stem+'.pdf'))!=rec['raw_sha256']:raise SystemExit('Raw PDF changed: '+kind)
        docs[kind]=fitz.open(work/(stem+'.pdf'));parsed[kind]=labels(work/(stem+'.aux'));records[kind]=rec
    resolved={}
    for key,entry in manifest['routes'].items():
        if 'label' in entry:
            kind=entry['source_kind'];label=parsed[kind].get(entry['label'])
            if label is None:raise SystemExit('Missing label: '+str(entry))
            dest=docs[kind].resolve_names().get(label['destination'])
            if dest is None:raise SystemExit('Missing PDF destination: '+str(label))
            resolved[key]={**entry,**label,'page':dest['page']+1}
        else:resolved[key]=entry.copy()
    links=[]
    for kind,doc in docs.items():
        for pi,page in enumerate(doc):
            for link in page.get_links():
                uri=link.get('uri','')
                if not uri.startswith(PREFIX):continue
                key=uri[len(PREFIX):]
                if key not in resolved:raise SystemExit('Unknown route: '+uri)
                target=resolved[key];page.delete_link(link)
                page.insert_link({'kind':fitz.LINK_GOTOR,'from':link['from'],'file':target['file'],'page':target['page']-1,'to':fitz.Point(0,0),'zoom':0})
                links.append({'source':names[kind],'source_page':pi+1,'key':key,**target})
        target=out/names[kind];doc.save(target,garbage=4,deflate=True,no_new_id=True);doc.close();records[kind]['sha256']=sha(target)
    for p in (root/'publication/pdfs').glob('Paper_XI_Conjecture66*.pdf'):shutil.copy2(p,out/p.name)
    result={'status':'passed','checkpoint':'P11-RELEASE-1.1.0','records':records,'reading_routes':resolved,'companion_links':links,'lean_compilation_by_pdf_builder':'not_run','formal_verification_scope':'Separate executed compiler and axiom-audit receipts are under verification/lean; this PDF builder does not invoke Lean.','figure_regeneration':'not_run_preserved_assets'}
    (out/'BUILD_RECORD.json').write_text(json.dumps(result,indent=2)+'\n');print('Assembled:',{k:v['pages'] for k,v in records.items()},'links',len(links),flush=True)

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--stage',choices=['all',*KINDS,'assemble'],default='all');ap.add_argument('--font-dir',type=Path);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];out=a.output.resolve()
    if out.is_relative_to(root):raise SystemExit('Output must be outside the checkpoint')
    if a.stage=='all' and out.exists() and any(out.iterdir()):raise SystemExit('Use a new output directory')
    out.mkdir(parents=True,exist_ok=True)
    if a.stage=='all':
        for kind in KINDS:compile_one(root,out,kind,a.font_dir)
        assemble(root,out)
    elif a.stage=='assemble':assemble(root,out)
    else:compile_one(root,out,a.stage,a.font_dir)
if __name__=='__main__':main()
