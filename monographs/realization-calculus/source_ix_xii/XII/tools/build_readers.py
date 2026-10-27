#!/usr/bin/env python3
"""Build and cross-link the Paper XII reader trio outside the release tree.
Requires TeX Live, PyMuPDF and installed fonts. Never invokes Lean/Lake.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
DOCS={'traditional':('Paper_XII_Traditional_Final','Paper_XII_Traditional_v1.0.0.pdf','pdflatex'),
 'visual_guide':('Paper_XII_Visual_Guide_Final','Paper_XII_Visual_Guide_v1.0.0.pdf','pdflatex'),
 'lean_guide':('Paper_XII_Lean_Guide_Final','Paper_XII_Lean_Guide_v1.0.0.pdf','xelatex')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def braces(s):
 vals=[];i=0
 while i<len(s):
  if s[i]!='{':i+=1;continue
  start=i+1;depth=1;i+=1
  while i<len(s) and depth:
   if s[i]=='{' and (i==0 or s[i-1]!='\\'):depth+=1
   if s[i]=='}' and (i==0 or s[i-1]!='\\'):depth-=1
   i+=1
  vals.append(s[start:i-1])
 return vals

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--stage',choices=['all','compile','links'],default='all');a=ap.parse_args();out=a.output.resolve()
 if out==ROOT or ROOT in out.parents:raise ValueError('Use an external build directory')
 out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1791590400',FORCE_SOURCE_DATE='1',TZ='UTC',PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',MPLBACKEND='Agg')
 report={'source_root':str(ROOT),'fresh_lean':False,'builds':{}}
 def run(cmd,cwd,log,timeout=150):
  t=time.time();p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout);log.write_text(p.stdout+'\n'+p.stderr)
  if p.returncode:raise RuntimeError(f'Command failed ({p.returncode}): {cmd}\n{p.stdout[-3000:]}\n{p.stderr[-1000:]}')
  return round(time.time()-t,3)
 if a.stage in ['all','compile']:
  for role,(stem,name,engine) in DOCS.items():
   work=out/role
   if work.exists():shutil.rmtree(work)
   shutil.copytree(ROOT/'publication/source'/role,work)
   # Remove stale auxiliary outputs if inherited copies contained any.
   for suffix in ['.aux','.out','.toc','.log','.blg']:(work/(stem+suffix)).unlink(missing_ok=True)
   enginebin=shutil.which(engine)
   if not enginebin:raise RuntimeError('Missing '+engine)
   if role=='traditional':run([sys.executable,str(ROOT/'tools/generate_architecture.py'),'--output',str(work/'figures/17_final_completion.pdf')],work,work/'architecture.log')
   if role=='visual_guide':run([sys.executable,str(work/'source/generate_graphics.py'),'--output-dir',str(work/'graphics')],work,work/'graphics.log')
   for n in range(1,4):
    run([enginebin,'-interaction=nonstopmode','-halt-on-error','-file-line-error','-no-shell-escape',stem+'.tex'],work,work/f'pass{n}.stdout.log')
    if role=='traditional' and n==1:
     # Debian runtime has a stale /usr/bin/bibtex launcher. Use a working executable.
     candidates=[shutil.which('bibtex'),shutil.which('bibtex.original'),shutil.which('bibtex8')]
     bib=None
     for cand in candidates:
      if not cand:continue
      try:
       pp=subprocess.run([cand,'--version'],capture_output=True,env=env,timeout=10)
       if pp.returncode==0:bib=cand;break
      except OSError:continue
     if not bib:raise RuntimeError('No working BibTeX executable')
     run([bib,stem],work,work/'bibliography.stdout.log')
     report['bibtex']=bib
   log=(work/(stem+'.log')).read_text(errors='replace')
   diagnostics={'overfull':re.findall(r'Overfull[^\n]*',log),'underfull':re.findall(r'Underfull[^\n]*',log),
    'missing_characters':re.findall(r'Missing character[^\n]*',log),'warnings':re.findall(r'(?:LaTeX|Package [\w-]+) Warning:[^\n]*',log)}
   report['builds'][role]={'engine':enginebin,'raw_pdf_sha256':sha(work/(stem+'.pdf')),'pages':len(fitz.open(work/(stem+'.pdf'))),'diagnostics':diagnostics}
   print(role,report['builds'][role]['pages'],'pages', {k:len(v) for k,v in diagnostics.items()},flush=True)
  (out/'COMPILE.json').write_text(json.dumps(report,indent=2)+'\n')
 if a.stage in ['all','links']:
  routes=json.loads((ROOT/'evidence/block01/ROUTES.json').read_text());docs={};names={};labels={};locators=[]
  for role,(stem,_,_) in DOCS.items():
   docs[role]=fitz.open(out/role/(stem+'.pdf'));names[role]=docs[role].resolve_names();labels[role]={}
   for line in (out/role/(stem+'.aux')).read_text(errors='replace').splitlines():
    if line.startswith('\\newlabel{'):
     b=braces(line);v=braces(b[1]) if len(b)>1 else []
     if len(v)>=4:labels[role][b[0]]={'number':v[0],'printed_page':v[1],'anchor':v[3]}
  counts={k:len(d) for k,d in docs.items()}; heights={k:[pg.rect.height for pg in d] for k,d in docs.items()}
  for role,doc in docs.items():
   seen=[]
   for pg in doc:
    for link in pg.get_links():
     uri=link.get('uri','')
     if not uri.startswith('p12-route:'):continue
     ident=uri.split(':',1)[1];r=routes[ident]
     if r['source']!=role:raise ValueError('Wrong source '+ident)
     target=r['target'];an=r['anchor'];an=labels[target].get(an,{}).get('anchor',an)
     if an not in names[target]:raise ValueError(f'Unknown target {an} for {ident}')
     dst=names[target][an];page=dst['page']
     if page<0 or page>=counts[target]:raise ValueError('Bad page '+ident)
     # Remote /XYZ destinations require the original PDF bottom-left coordinates.
     # Unlike local links, PyMuPDF writes these remote coordinates without conversion.
     xy=dst.get('to',(0,heights[target][page]));pos=fitz.Point(xy[0],xy[1])
     pg.delete_link(link);pg.insert_link({'kind':fitz.LINK_GOTOR,'from':link['from'],'file':DOCS[target][1],'page':page,'to':pos,'zoom':0})
     seen.append(ident);locators.append({'id':ident,'source':role,'source_pdf_page':pg.number+1,'target_file':DOCS[target][1],'target_pdf_page':page+1,'target_point':[pos.x,pos.y],'anchor':an,'text':r['text']})
   expected={i for i,r in routes.items() if r['source']==role}
   if set(seen)!=expected:raise ValueError(f'Missing routes {expected-set(seen)}')
   md=doc.metadata;md.update({'creationDate':'D:20261010000000Z','modDate':'D:20261010000000Z','author':'Komorebi P.','subject':'Paper XII / reading release 1.0.0 / conditional automorphic completion'})
   doc.set_metadata(md);outfile=out/DOCS[role][1];outfile.unlink(missing_ok=True);doc.save(outfile,garbage=4,deflate=True,no_new_id=True);doc.close()
  (out/'LOCATORS.json').write_text(json.dumps({'registered_routes':len(routes),'annotations':len(locators),'routes':locators},indent=2)+'\n')
  if (out/'COMPILE.json').exists():report=json.loads((out/'COMPILE.json').read_text())
  report['outputs']={role:{'file':name,'sha256':sha(out/name),'pages':len(fitz.open(out/name))} for role,(_,name,_) in DOCS.items()}
  report['registered_routes']=len(routes);report['companion_annotations']=len(locators)
  (out/'BUILD.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['outputs'],indent=2))
if __name__=='__main__':main()
