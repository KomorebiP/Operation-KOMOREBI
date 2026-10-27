"""Inventory publication-history candidates in the actual reading sequence."""
from pathlib import Path
import collections,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[2]
PATTERN=re.compile(r"\b(?:v\d+(?:\.\d+)*|version(?:s|ing)?|edition|revision|release|historical|checkpoint|milestone|draft|work.in.progress|October|September|August|202[0-9])\b|(?:PRSC|Komorebi)[^\s]*_v\d|--release",re.I)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 spec=json.loads((ROOT/'book/build_spec.json').read_text());pdf=ROOT/'output/Realization_Calculus.pdf';doc=fitz.open(pdf)
 location={}
 for item in spec['sequence']:
  if item['kind']=='component':
   for offset,raw in enumerate(item['source_pages']):location[item['book_index']+offset]={'component_id':item['component_id'],'source_page':raw+1,'reference':item.get('unit_id','').startswith('references_')}
 matches=[]
 for i,page in enumerate(doc):
  for line in page.get_text().splitlines():
   if PATTERN.search(line):matches.append({'book_page':i+1,**location.get(i,{'component_id':'outer','reference':False}),'text':line})
 bookmarks=[{'level':level,'title':title,'book_page':pn} for level,title,pn in doc.get_toc() if PATTERN.search(title)]
 result={'status':'REVIEW_REQUIRED','pdf_sha256':sha(pdf),'pages':len(doc),'matches':matches,'bookmark_matches':bookmarks}
 (ROOT/'editorial/volume_finish/final_text_candidates.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'matches':len(matches),'bookmarks':len(bookmarks),'by_component':collections.Counter(x['component_id'] for x in matches)},indent=2))
if __name__=='__main__':main()
