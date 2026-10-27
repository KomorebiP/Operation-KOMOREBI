#!/usr/bin/env python3
"""Assemble the cumulative v0.4 reader, resolving named links before merging."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from pathlib import Path
import fitz

def resolved_link(link,source,offset):
 k=link['kind']
 if k==fitz.LINK_GOTO:
  return {'kind':fitz.LINK_GOTO,'from':link['from'],'page':link['page']+offset,'to':link.get('to',fitz.Point())}
 if k==fitz.LINK_NAMED and link.get('page',-1)>=0:
  point=link.get('to',fitz.Point())*source[link['page']].transformation_matrix
  return {'kind':fitz.LINK_GOTO,'from':link['from'],'page':link['page']+offset,'to':point}
 if k==fitz.LINK_URI:return {'kind':fitz.LINK_URI,'from':link['from'],'uri':link['uri']}
 raise ValueError(f'Unresolved source link: {link}')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--continuation',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);pred=root/'predecessor/block03'
 paths=[pred/'baseline/block02/Paper_XI_Conjecture66_Progress_v0.2.0.pdf',pred/'publication/pdfs/Paper_XI_Conjecture66_Block03_v0.3.0.pdf',a.continuation.resolve()]
 docs=[fitz.open(p) for p in paths];assert [len(x) for x in docs[:2]]==[33,19]
 tex=(root/'publication/source/Paper_XI_Cumulative_Map.tex').read_text().replace('PARTTHREECOUNT',str(len(docs[2]))).replace('TOTALCOUNT',str(54+len(docs[2])))
 wrapper=out/'Paper_XI_Cumulative_Map.tex';wrapper.write_text(tex)
 env=dict(os.environ,TEXINPUTS=str(root/'publication/source')+os.pathsep,SOURCE_DATE_EPOCH='1791648000',FORCE_SOURCE_DATE='1')
 for i in range(2):
  r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(out),str(wrapper)],cwd=out,env=env,text=True,capture_output=True,timeout=90)
  (out/f'map_build_{i+1}.txt').write_text(r.stdout+r.stderr)
  if r.returncode:raise SystemExit('Edition map failed to build')
 front=fitz.open(out/'Paper_XI_Cumulative_Map.pdf');assert len(front)==2
 result=fitz.open();expected=[];offsets=[];offset=0
 for source in [front]+docs:
  offsets.append(offset);result.insert_pdf(source,links=False)
  for i,page in enumerate(source):
   for link in page.get_links():
    item=resolved_link(link,source,offset);result[offset+i].insert_link(item)
    expected.append((offset+i,item))
  offset+=len(source)
 toc=[[1,'Edition map',2]]
 for name,doc,start in zip(['Part I: restricted arithmetic constructions','Part II: monomial routes, Clifford descent and obstructions','Part III: conductors, native markings and equal capacity'],docs,offsets[1:]):
  toc.append([1,name,start+1]);toc.extend([[l+1,t,p+start] for l,t,p in doc.get_toc() if p>0])
 result.set_toc(toc);result.set_metadata({'title':'Toward Arithmetic Packet Realization — v0.4.0','author':'Komorebi P.','subject':'Paper XI / Conjecture 66 working research companion'})
 dest=out/'Paper_XI_Conjecture66_Progress_v0.4.0.pdf';result.save(dest,garbage=4,deflate=True);result.close();result=fitz.open(dest)
 preservation=[]
 for label,source,start in zip(['Part I','Part II'],docs[:2],offsets[1:3]):
  for i,p in enumerate(source):
   t=result[start+i];preservation.append({'part':label,'source_page':i+1,'output_page':start+i+1,'text_equal':p.get_text()==t.get_text(),'render_100dpi_equal':p.get_pixmap(dpi=100).samples==t.get_pixmap(dpi=100).samples,'links_equal_count':len(p.get_links())==len(t.get_links())})
 linkchecks=[]
 for pno,wanted in expected:
  found=[x for x in result[pno].get_links() if abs(x['from'].x0-wanted['from'].x0)<.1 and abs(x['from'].y0-wanted['from'].y0)<.1]
  good=False
  for got in found:
   if got['kind']!=wanted['kind']:continue
   if got['kind']==fitz.LINK_URI:good=got['uri']==wanted['uri']
   else:good=got['page']==wanted['page'] and abs(got['to'].x-wanted['to'].x)<.1 and abs(got['to'].y-wanted['to'].y)<.1
   if good:break
  linkchecks.append({'page':pno+1,'status':'passed' if good else 'failed'})
 ok=all(x['text_equal'] and x['render_100dpi_equal'] and x['links_equal_count'] for x in preservation) and all(x['status']=='passed' for x in linkchecks)
 rec={'status':'passed' if ok else 'failed','pages':len(result),'map_pages':2,'part_pages':[len(d) for d in docs],'bookmarks':len(result.get_toc()),'links':len(expected),'source_pins':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'preserved_pages':preservation,'link_checks':linkchecks}
 (out/'ASSEMBLY_VERIFICATION.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items() if k not in ['preserved_pages','link_checks','source_pins']},indent=2))
 if not ok:raise SystemExit(1)
if __name__=='__main__':main()
