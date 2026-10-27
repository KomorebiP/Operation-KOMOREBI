#!/usr/bin/env python3
"""Assemble v0.3.0 while retaining all original v0.2.0 page content."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
import fitz

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--continuation',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 old=root/'baseline/block02/Paper_XI_Conjecture66_Progress_v0.2.0.pdf';new=a.continuation.resolve();d1=fitz.open(old);d2=fitz.open(new)
 # A separate editable wrapper describes the nonuniform source recovery status.
 tex=r'''\documentclass[11pt]{article}
\usepackage{amsmath,hyperref,komorebi-publication}
\renewcommand{\KomorebiTitle}{Toward Arithmetic Packet Realization}
\renewcommand{\KomorebiSubtitle}{Restricted constructions, failed routes, and the remaining obligations of Conjecture 66}
\renewcommand{\KomorebiSeries}{Paper XI / Research companion}
\renewcommand{\KomorebiKind}{Cumulative research reader}
\renewcommand{\KomorebiEdition}{Working paper v0.3.0 / Publication Block 03 / 10 October 2026}
\renewcommand{\KomorebiShortTitle}{Paper XI / Cumulative reader}
\KomorebiSetup
\begin{document}\KomorebiCover
\section*{Edition map}
This working edition joins the preserved construction paper with a new independently editable continuation. It does not replace the original Paper XI main, visual or Lean readers.

\textbf{Part I. Restricted arithmetic constructions.} The complete 33-page v0.2.0 reader is retained. It includes the odd-prime and weighted dyadic recursions, full-character induction, quotient obstructions and low-rank enlarged carriers. Its original cover and page numbering remain visible.

\textbf{Part II. Monomial routes, Clifford descent and exact obstructions.} The new CONTCOUNT-page continuation contains Sections 14--21. It reconciles the monomial lineage, genuine source multiplicities, characteristic-zero descent and occurrence, the full-extension scalar obstruction, and the compact and explicit binder routes.

\textbf{Source recovery.} The Block 02 PDF and ledger were recovered, but its complete editable source ZIP was not. Part I is therefore preserved rather than claimed to have been rebuilt. Part II, this edition map, the assembly program, tests and ledger are supplied as editable sources. The underlying research records come from the hash-verified Block 01 archive.

\textbf{Claim boundary.} General realization and same-candidate H5 remain separate unresolved obligations. Ordinary proofs, inherited arithmetic arguments, fresh bounded checks and historical formal evidence are distinguished in the source map. No fresh Lean compilation or external peer review occurred in Publication Block 03.

\textbf{Reading locations.} Part I occupies PDF pages OLDSTART--OLDEND. Part II occupies PDF pages NEWSTART--NEWEND. Use the PDF bookmarks for section navigation. The standalone Part II PDF is also supplied.

\textbf{Restart record.} The versioned progress ledger and continuation handoff specify the completed reconciliation and the exact next source queue for Publication Block 04. The compact source checkpoint preserves this block's editable work independently of the large inherited archive.
\end{document}
'''
 for k,v in {'CONTCOUNT':len(d2),'OLDSTART':3,'OLDEND':2+len(d1),'NEWSTART':3+len(d1),'NEWEND':2+len(d1)+len(d2)}.items():tex=tex.replace(k,str(v))
 wrapper=root/'publication/source/Paper_XI_Cumulative_Map.tex';wrapper.write_text(tex)
 env=dict(os.environ,TEXINPUTS=str(wrapper.parent)+os.pathsep,SOURCE_DATE_EPOCH='1791648000',FORCE_SOURCE_DATE='1')
 for i in range(2):
  r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(out),str(wrapper)],cwd=wrapper.parent,env=env,capture_output=True,text=True)
  (out/f'map_build_{i+1}.txt').write_text(r.stdout+r.stderr)
  if r.returncode:raise SystemExit('Edition map build failed')
 front=fitz.open(out/'Paper_XI_Cumulative_Map.pdf');assert len(front)==2
 result=fitz.open()
 # Named destinations are not carried by insert_pdf. Resolve them before merging.
 for source,offset in [(front,0),(d1,len(front)),(d2,len(front)+len(d1))]:
  result.insert_pdf(source,links=False)
  for i,page in enumerate(source):
   for link in page.get_links():
    kind=link['kind']
    if kind==fitz.LINK_GOTO:
     item={'kind':fitz.LINK_GOTO,'from':link['from'],'page':link['page']+offset,'to':link.get('to',fitz.Point(0,0))}
    elif kind==fitz.LINK_NAMED and link.get('page',-1)>=0:
     # Named destination coordinates are in PDF space, unlike ordinary GOTO.
     target=link['page'];point=link.get('to',fitz.Point(0,0))*source[target].transformation_matrix
     item={'kind':fitz.LINK_GOTO,'from':link['from'],'page':target+offset,'to':point}
    elif kind==fitz.LINK_URI:
     item={'kind':fitz.LINK_URI,'from':link['from'],'uri':link['uri']}
    else:raise RuntimeError(f'Unresolved link: {link}')
    result[offset+i].insert_link(item)
 toc=[[1,'Edition map',2],[1,'Part I: preserved v0.2.0 construction paper',3]]
 toc += [[l+1,t,p+2] for l,t,p in d1.get_toc() if p>0]
 toc += [[1,'Part II: monomial routes, Clifford descent and obstructions',3+len(d1)]]
 toc += [[l+1,t,p+2+len(d1)] for l,t,p in d2.get_toc() if p>0]
 result.set_toc(toc);result.set_metadata({'title':'Toward Arithmetic Packet Realization — v0.3.0','author':'Komorebi P.','subject':'Paper XI / Conjecture 66 working research companion'})
 dest=out/'Paper_XI_Conjecture66_Progress_v0.3.0.pdf';result.save(dest,garbage=4,deflate=True);result.close()
 result=fitz.open(dest);matches=[]
 for i,p in enumerate(d1):
  q=result[i+2];matches.append({'source_page':i+1,'output_page':i+3,'text_equal':p.get_text()==q.get_text(),'render_100dpi_equal':p.get_pixmap(dpi=100).samples==q.get_pixmap(dpi=100).samples,'links_before':len(p.get_links()),'links_after':len(q.get_links())})
 rec={'status':'passed' if all(x['text_equal'] and x['render_100dpi_equal'] and x['links_before']==x['links_after'] for x in matches) else 'failed','source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'pages':len(result),'partI_pages':len(d1),'partII_pages':len(d2),'map_pages':2,'partI_preservation':matches}
 (out/'ASSEMBLY_VERIFICATION.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items() if k!='partI_preservation'},indent=2))
 if rec['status']!='passed':raise SystemExit(1)
if __name__=='__main__':main()
