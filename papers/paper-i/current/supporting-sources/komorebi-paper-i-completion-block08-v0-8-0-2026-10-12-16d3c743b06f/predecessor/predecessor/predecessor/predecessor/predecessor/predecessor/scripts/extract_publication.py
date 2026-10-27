#!/usr/bin/env python3
"""Extract all current Paper I stable statement and proof records with hashes.
Reads current split traditional TeX, never substitutes the old machine mirror.
No OCR, PDF parsing, or heuristic keyword assignment of theorem status.
"""
from pathlib import Path
import argparse,hashlib,json,re

def digest(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--publication',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 p=a.publication.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 old=json.loads((p/'COMPANION_CROSSWALK.json').read_text());records={}
 envs='definition|theorem|corollary|proposition|lemma|classicalinput|boundary|remark'
 for f in sorted((p/'editable/traditional').glob('*.tex')):
  text=f.read_text();starts=list(re.finditer(r'\\begin\{('+envs+r')\}',text))
  for m in re.finditer(r'\\RecordID\{(PSC-I-[^}]+)\}',text):
   rid=m.group(1);before=[s for s in starts if s.start()<m.start()]
   if not before:raise ValueError('No statement before '+rid)
   st=before[-1];endtoken='\\end{'+st.group(1)+'}';end=text.index(endtoken,st.end())+len(endtoken)
   if end>m.start():raise ValueError('Record id inside statement: '+rid)
   statement=text[st.start():end];rest=text[m.end():]
   pm=re.search(r'\\begin\{proof\}',rest);nm=re.search(r'\\RecordID\{',rest)
   proof=None;ps=None;pe=None
   if pm and (not nm or pm.start()<nm.start()):
    ps=m.end()+pm.start();pe=text.index('\\end{proof}',ps)+len('\\end{proof}');proof=text[ps:pe]
   if rid in records:raise ValueError('Duplicate '+rid)
   records[rid]={'file':str(f.relative_to(p)),'file_sha256':digest(f.read_bytes()),'kind':st.group(1),'record_id_line':text.count('\n',0,m.start())+1,'statement_start_line':text.count('\n',0,st.start())+1,'statement_end_line':text.count('\n',0,end)+1,'statement':statement,'statement_sha256':digest(statement.encode()),'proof':proof,'proof_start_line':None if ps is None else text.count('\n',0,ps)+1,'proof_end_line':None if pe is None else text.count('\n',0,pe)+1,'proof_sha256':None if proof is None else digest(proof.encode())}
 expected={r['stable_id'] for r in old['expanded_records']}
 if set(records)!=expected:raise ValueError({'missing':sorted(expected-set(records)),'unexpected':sorted(set(records)-expected)})
 targets=[r for r in records.values() if r['kind'] in {'theorem','proposition','corollary','lemma'}]
 if len(records)!=108 or len(targets)!=69 or any(r['proof'] is None for r in targets):raise ValueError('Inventory or attached source-proof mismatch')
 (out/'current_expanded_records.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
 receipt={'status':'PASS','scope':'Current source extraction and anchor checks, not Lean proof verification','stable_records':len(records),'proved_kind_records':len(targets),'source_proofs':sum(r['proof'] is not None for r in records.values()),'source_files':{r['file']:r['file_sha256'] for r in records.values()},'crosswalk_sha256':digest((p/'COMPANION_CROSSWALK.json').read_bytes()),'records_sha256':digest((out/'current_expanded_records.json').read_bytes())}
 (out/'extraction_verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
