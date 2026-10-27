from pathlib import Path
import json,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'editorial/rhythm_review'
COV=json.loads((ROOT/'editorial/prose_review/vii_viii_coverage.json').read_text())
FILES=[x['file'] for x in COV['files']]
ENV=r'(?:equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|flalign\*?|displaymath|math|verbatim\*?|Verbatim|lstlisting|minted|tikzpicture|figure\*?)'
PAT=re.compile(r'\\begin\{('+ENV+r')\}[\s\S]*?\\end\{\1\}|(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|(?<!\\)\$(?!\$)[\s\S]*?(?<!\\)\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\\(?:verb\*?)([^A-Za-z\s])[\s\S]*?\2|\\(?:texttt|path|url|href|detokenize)\{(?:[^{}]|\{[^{}]*\})*\}|(?<!\\)%[^\n]*')
def spans(s):return [(m.start(),m.end(),m.group()) for m in PAT.finditer(s)]
def masked(s):
 a=list(s)
 for x,y,_ in spans(s):
  for i in range(x,y):
   if a[i]!='\n':a[i]=' '
 return ''.join(a)
def init():
 rec=[]
 for f in FILES:
  p=ROOT/f;s=p.read_text();b=OUT/'vii_viii_before'/f
  b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(p,b)
  rec.append({'file':f,'sha256':hashlib.sha256(s.encode()).hexdigest()})
 (OUT/'vii_viii_inputs.json').write_text(json.dumps(rec,indent=2)+'\n')
def scan():
 res=[];summary={}
 for f in FILES:
  s=(ROOT/f).read_text();ms=masked(s);lines=s.splitlines();ml=ms.splitlines()
  for i,(a,b) in enumerate(zip(lines,ml),1):
   types=[]
   if ';' in b:types.append('semicolon')
   if re.search(r'---|--|[—–]',b):types.append('dash')
   if re.search(r'[A-Za-z]-[A-Za-z]',b):types.append('hyphen')
   if re.search(r'\b(?:not merely|not just|In other words|It is worth|important to note|key point|crucial|This is not|rather than|not a|not the|purpose|payoff|reader|bottleneck|boundary|route|checkpoint|workflow|new|now)\b',b,re.I):types.append('phrasing')
   if types:res.append({'file':f,'line':i,'types':types,'text':a,'eligible':b.strip()})
 (OUT/'vii_viii_candidates.json').write_text(json.dumps(res,indent=2)+'\n')
 for c in res:
  for t in c['types']:summary[t]=summary.get(t,0)+1
 print(summary,'candidate lines',len(res))
 for ch in ['VII','VIII']:
  q=[c for c in res if f'/{ch}/' in c['file']]
  (OUT/f'vii_viii_{ch}_candidates.txt').write_text('\n'.join(f"{c['file']}:{c['line']} [{','.join(c['types'])}]\n{c['text']}\n" for c in q)+'\n')
if __name__=='__main__':init();scan()
