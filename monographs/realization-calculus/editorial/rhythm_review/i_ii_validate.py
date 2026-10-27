from pathlib import Path
import re,json,hashlib,difflib
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT=ROOT/'editorial/rhythm_review'
j=json.loads((OUT/'i_ii_journal.json').read_text())
checks=[]
patterns={
'inline_dollar_math':r'(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$',
'paren_math':r'(?<!\\)\\\(.*?\\\)',
'bracket_math':r'(?<!\\)\\\[.*?\\\]',
'math_environments':r'\\begin\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|flalign\*?|displaymath|math)\}.*?\\end\{(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|flalign\*?|displaymath|math)\}',
'literal_environments':r'\\begin\{(?:lstlisting|verbatim|Verbatim|minted|tikzpicture)\}.*?\\end\{(?:lstlisting|verbatim|Verbatim|minted|tikzpicture)\}',
'control_sequence_order':r'\\(?:[A-Za-z]+|[^A-Za-z\s])',
'environment_order':r'\\(?:begin|end)\{[^{}]+\}',
'bibliography':r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}',
}
def macros(s,names):
 found=[]
 for m in re.finditer(r'\\(?:'+names+r')(?![A-Za-z])',s):
  start=m.start();pos=m.end()
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos<len(s) and s[pos]=='[':
   n=s.find(']',pos)
   if n<0:raise ValueError('unclosed optional argument')
   pos=n+1
   while pos<len(s) and s[pos].isspace():pos+=1
  if pos>=len(s) or s[pos]!='{':continue
  depth=1;pos+=1
  while pos<len(s) and depth:
   if s[pos]=='\\':pos+=2;continue
   if s[pos]=='{':depth+=1
   if s[pos]=='}':depth-=1
   pos+=1
  found.append(s[start:pos])
 return found
for f in dict.fromkeys(c['file'] for c in j['changes']):
 b=(OUT/'i_ii_before'/f).read_text();a=(ROOT/f).read_text();replay=b
 cs=[c for c in j['changes'] if c['file']==f]
 for c in cs:
  assert replay.count(c['old'])==1,(f,c['old'])
  replay=replay.replace(c['old'],c['new'],1)
 cats={}
 for k,p in patterns.items():
  v=re.findall(p,b,re.S);w=re.findall(p,a,re.S)
  cats[k]={'equal':v==w,'count_before':len(v),'count_after':len(w)}
 for k,names in {
  'literal_macros':'code|texttt|nolinkurl|url|VerbatimInput|lstinputlisting|source|excerpt',
  'structural_destinations':'label|ref|eqref|cref|Cref|cite|RecordID|Depends|Exports|hypertarget|hyperlink|input|include|includegraphics|bibliography|bibliographystyle|pageref',
 }.items():
  v=macros(b,names);w=macros(a,names)
  cats[k]={'equal':v==w,'count_before':len(v),'count_after':len(w)}
 checks.append({'file':f,'before_sha256':hashlib.sha256(b.encode()).hexdigest(),'after_sha256':hashlib.sha256(a.encode()).hexdigest(),'journal_replay_exact':replay==a,'line_count_unchanged':len(b.splitlines())==len(a.splitlines()),'categories':cats})
 fail=[(c['file'],k) for c in checks for k,v in c['categories'].items() if not v['equal']]
 assert not fail,fail
 assert all(c['journal_replay_exact'] and c['line_count_unchanged'] for c in checks)
report={'status':'PASS','changed_files':len(checks),'journal_replacements':len(j['changes']),'checks':checks,'atlas_duplicate_equal':(ROOT/'source_i_iv/II/editable/traditional/visual_atlas.tex').read_bytes()==(ROOT/'source_i_iv/II/editable/visual_guide/source/pages_final.tex').read_bytes(),'scope':'Source-text preservation checks, not a mathematical correctness audit or PDF layout verification.'}
assert report['atlas_duplicate_equal']
(OUT/'i_ii_preservation.json').write_text(json.dumps(report,indent=2)+'\n')
# Print protected-span totals, not source code.
print(json.dumps({'status':report['status'],'changed_files':len(checks),'journal_replacements':len(j['changes']),'atlas_duplicate_equal':report['atlas_duplicate_equal'],'protected_counts':{k:sum(c['categories'][k]['count_before'] for c in checks) for k in patterns}|{k:sum(c['categories'][k]['count_before'] for c in checks) for k in ['literal_macros','structural_destinations']}},indent=2))
