from pathlib import Path
import json,unicodedata,re,hashlib,difflib
import fitz
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222');OUT=ROOT/'editorial/rhythm_review'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',s).casefold() if c.isalnum())
records=json.loads((OUT/'frontmatter_probe.json').read_text())['records'];paths={r['component_id']:r['path'] for r in records}
g=json.loads((ROOT/'editorial/book_revision/glossary.json').read_text());cache={};results=[];pending=[]
for term in g['terms']:
 for ref in term.get('references',term.get('refs',[])):
  cid=ref['component_id'];base={'term':term['term'],'component_id':cid,'previous_local_page':ref['local_page'],'anchor_quote':ref['anchor_quote']}
  if cid not in paths:pending.append(base);continue
  if cid not in cache:
   d=fitz.open(ROOT/paths[cid]);texts=[p.get_text(sort=True) for p in d];cache[cid]=(texts,[norm(t) for t in texts]);d.close()
  texts,normalized=cache[cid];needle=norm(ref['anchor_quote']);hits=[i+1 for i,t in enumerate(normalized) if needle in t]
  row={**base,'path':paths[cid],'matching_local_pages':hits,'unique':len(hits)==1}
  if len(hits)==1:
   row['new_local_page']=hits[0]
   # Produce an actual source quotation fragment with character provenance.
   text=texts[hits[0]-1];pieces=[];mapping=[]
   for i,c in enumerate(text):
    for v in unicodedata.normalize('NFKC',c).casefold():
     if v.isalnum():pieces.append(v);mapping.append(i)
   nn=''.join(pieces);assert nn==normalized[hits[0]-1],cid
   start=nn.index(needle);a=mapping[start];b=mapping[start+len(needle)-1]+1
   if ref['anchor_quote'].endswith(')') and text[b:b+1]==')':b+=1
   row['actual_pdf_quote_fragment']=text[a:b]
   row['actual_context']=text[max(0,a-70):min(len(text),b+110)]
  else:
   scores=[difflib.SequenceMatcher(None,needle,t).ratio() for t in normalized]
   row['nearby_page_text']={str(n):texts[n-1][:4000] for n in range(max(1,ref['local_page']-2),min(len(texts),ref['local_page']+2)+1)}
  results.append(row)
out={'status':'PASS' if not pending and all(r['unique'] for r in results) else 'PARTIAL' if pending and all(r['unique'] for r in results) else 'REVIEW_REQUIRED','total_references':len(results)+len(pending),'checked':len(results),'pending':pending,'references':results,'page_changes':[{'term':r['term'],'component_id':r['component_id'],'old':r['previous_local_page'],'new':r['new_local_page']} for r in results if r.get('new_local_page')!=r['previous_local_page']],'matching_rule':'Same as book_layout.norm: NFKC, casefold, retain alphanumeric characters; require one matching physical source page. Actual source quote fragments and contexts also extracted for punctuation review.'}
(OUT/'glossary_anchor_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['references','pending']},indent=2))
for r in results:
 if not r['unique']:print('UNRESOLVED',r['term'],r['component_id'],r['anchor_quote'],r['matching_local_pages'])
