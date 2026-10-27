#!/usr/bin/env python3
"""Check the current PDF navigation, source pins, proof register and ledger contract."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
import fitz

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[1];errors=[];pdfs=[]
 for name,n in [('Paper_XI_Conjecture66_Block04_v0.4.0.pdf',23),('Paper_XI_Conjecture66_Progress_v0.4.0.pdf',77)]:
  p=root/'publication/pdfs'/name;doc=fitz.open(p);bad=[];links=0
  for i,page in enumerate(doc):
   for link in page.get_links():
    links+=1
    if link['kind'] in [fitz.LINK_GOTO,fitz.LINK_NAMED] and not 0<=link.get('page',-1)<len(doc):bad.append({'page':i+1,'link':str(link)})
  if len(doc)!=n or bad:errors.append({'pdf':name,'expected_pages':n,'actual':len(doc),'bad_links':bad})
  pdfs.append({'name':name,'pages':len(doc),'bookmarks':len(doc.get_toc()),'links':links,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 ledger=json.loads((root/'PROGRESS_LEDGER.json').read_text());old=json.loads((root/'predecessor/block03/PROGRESS_LEDGER.json').read_text())
 oldids={t['id'] for t in old['tasks']};ids=[t['id'] for t in ledger['tasks']]
 if not oldids<=set(ids) or len(ids)!=len(set(ids)) or len(ids)!=23:errors.append('ledger ID preservation/count failure')
 if ledger['history'][:-1]!=old['history']:errors.append('ledger history not preserved')
 for entry in json.loads((root/'evidence/block04/SOURCE_MAP.json').read_text())['sources']:
  p=root/entry['path']
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append({'source_pin':entry['id']})
 source='\n'.join(p.read_text() for p in (root/'publication/source/block04').glob('*.tex'))
 proofs=source.count('\\begin{proof}')
 labels=re.findall(r'\\label\{([^}]+)\}',source);refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',source)
 if proofs!=13 or len(labels)!=len(set(labels)) or set(refs)-set(labels):errors.append('proof/reference register mismatch')
 result={'status':'passed' if not errors else 'failed','pdfs':pdfs,'ledger_tasks':len(ids),'previous_ids_preserved':len(oldids),'ordinary_proof_bodies':proofs,'source_labels':len(labels),'resolved_reference_occurrences':len(refs),'source_pins':10,'errors':errors}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
