from pathlib import Path
import json,re,hashlib
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/rhythm_review'
iii=json.loads((R/'editorial/prose_review/iii_report.json').read_text())['coverage'];iv=json.loads((R/'editorial/prose_review/iv_coverage.json').read_text())
files=[x['file'] for x in iii+iv if '/generated/' not in x['file']];files+=['source_i_iv/III/guides/lean/generated/current_receipts.tex'];files=list(dict.fromkeys(files))
math=re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath|math|eqnarray\*?)\}.*?\\end\{\1\}|(?<!\\)\\\[.*?(?<!\\)\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$',re.S)
blocks=re.compile(r'\\begin\{(Verbatim|verbatim|lstlisting|minted|alltt|quote|tikzpicture)\}.*?\\end\{\1\}',re.S)
mac=re.compile(r'\\(?:code|leanname|path|url|nolinkurl|texttt|statusleanthree|statusleanprior|label|ref|eqref|cref|Cref|pageref|cite|citep|citet|input|include|includegraphics|bibliography|bibliographystyle|href|hyperlink|hypertarget)\b')
def mask(s):
 ranges=[m.span() for m in math.finditer(s)]+[m.span() for m in blocks.finditer(s)]+[m.span() for m in re.finditer(r'(?m)(?<!\\)%[^\n]*',s)]
 if '\\begin{document}' in s:ranges.append((0,s.index('\\begin{document}')))
 for m in mac.finditer(s):
  pos=m.end()
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos<len(s) and s[pos]=='[':pos=s.find(']',pos)+1
  while pos<len(s) and s[pos].isspace():pos+=1
  if pos>=len(s) or s[pos]!='{':continue
  depth=0;end=pos
  while end<len(s):
   if s[end] in '{}' and (end==0 or s[end-1]!='\\'):
    depth+=1 if s[end]=='{' else -1
    if depth==0:end+=1;break
   end+=1
  ranges.append((m.start(),end))
 chars=list(s)
 for a,b in ranges:
  for i in range(a,b):
   if chars[i]!='\n':chars[i]=' '
 return ''.join(chars)
rows=[];counts={}
for f in files:
 s=(R/f).read_text();m=mask(s);lines=s.splitlines()
 for typ,pat in [('semicolon',r';'),('dash',r'---|--|[—–]'),('hyphenated_modifier',r'(?<![A-Za-z\\])[A-Za-z]+(?:-[A-Za-z]+)+'),('formulaic_phrase',r'(?i)\b(?:it is (?:important|worth|useful|helpful)|in (?:summary|conclusion)|in short|serves as|provides a framework|we now|we next|the purpose of|a useful|most importantly|importantly|therefore makes|these boundaries leave)\b')]:
  for match in re.finditer(pat,m):
   n=m[:match.start()].count('\n')+1
   rows.append({'file':f,'line':n,'type':typ,'candidate':match.group(),'context':lines[n-1]})
 counts[f]={typ:sum(x['file']==f and x['type']==typ for x in rows) for typ in ['semicolon','dash','hyphenated_modifier','formulaic_phrase']}
(E/'iii_iv_candidates.json').write_text(json.dumps(rows,indent=2)+'\n');(E/'iii_iv_scope.json').write_text(json.dumps({'files':files,'counts':counts,'masking':'Math, literal blocks, exact quote blocks, TikZ, code/path/ref arguments, comments and entry preambles excluded. Generated exact declaration tables excluded; active authored current_receipts included.','total_candidates':len(rows)},indent=2)+'\n')
print('TOTAL',len(files),'FILES',len(rows),'CANDIDATES')
for typ in ['semicolon','dash','formulaic_phrase']:
 print('\nTYPE',typ)
 for i,x in enumerate(rows):
  if x['type']==typ: print(i,x['file'],x['line'],x['context'])
print('\nHYPHEN TYPES')
from collections import Counter
print(Counter(x['candidate'] for x in rows if x['type']=='hyphenated_modifier'))
