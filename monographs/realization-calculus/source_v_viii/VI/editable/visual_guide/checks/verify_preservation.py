#!/usr/bin/env python3
"""Compare mathematical spans with archived immediately pre-monograph body sources."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def escaped(text,i):
 j=i-1
 while j>=0 and text[j]=='\\':j-=1
 return (i-j-1)%2==1

def spans(text):
 result=[];i=0
 while i<len(text):
  if text[i]=='%' and not escaped(text,i):
   j=text.find('\n',i);i=len(text) if j<0 else j+1;continue
  opener=None;closer=None
  if text[i]=='$' and not escaped(text,i):opener='$$' if text[i:i+2]=='$$' else '$';closer=opener
  elif text[i:i+2] in ('\\[','\\(') and not escaped(text,i):opener=text[i:i+2];closer='\\]' if opener=='\\[' else '\\)'
  if opener:
   j=i+len(opener)
   while True:
    j=text.find(closer,j)
    if j<0:raise ValueError('Unclosed mathematical span')
    if not escaped(text,j):break
    j+=len(closer)
   result.append((opener,text[i:j+len(closer)]));i=j+len(closer)
  else:i+=1
 return result

def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 for n in ('pages.tex','extensions.tex'):
  old=ROOT/'historical_assembly/source'/n;new=ROOT/'source'/n;a=spans(old.read_text());b=spans(new.read_text())
  assert a==b,(n,len(a),len(b))
  rows.append({'file':n,'mathematical_spans':len(a),'inline_dollar':sum(t=='$' for t,s in a),'displays':sum(t=='\\[' for t,s in a),'math_identical':True,'historical_sha256':h(old),'current_sha256':h(new)})
 plates=json.loads((ROOT/'checks/runs/plates/result.json').read_text())['plates']
 for plate in plates:
  assert h(ROOT/'graphics'/plate['file'])==plate['shipped_sha256']==plate['regenerated_sha256']
 report={'status':'PASS','body_source_files':rows,'total_mathematical_spans':sum(x['mathematical_spans'] for x in rows),'all_original_inline_and_display_math_identical':True,'vector_plates':plates,'plate_count':len(plates),'all_vector_plate_sources_byte_identical_after_regeneration':True,'renderer_adaptation':'vfig applies arraystretch1.5 locally for fraction-row readability; plate/model/data files are unchanged.','scope':'Exact delimiter-aware mathematical-span comparison against pre-monograph body sources, skipping TeX comments and escaped delimiters. Does not prove mathematical correctness.'}
 (ROOT/'PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',report['total_mathematical_spans'],'mathematical spans preserved.')
if __name__=='__main__':main()
