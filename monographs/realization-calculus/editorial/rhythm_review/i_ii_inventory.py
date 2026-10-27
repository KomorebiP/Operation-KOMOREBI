from pathlib import Path
import re,json,hashlib
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT=ROOT/'editorial/rhythm_review'
FILES=[x['file'] for x in json.loads((ROOT/'editorial/prose_review/i_ii_coverage.json').read_text())['files']]
CHILD={'source_i_iv/I/editable/lean_guide/Paper_I_Lean_Guide_Final.tex','source_i_iv/I/editable/machine/Paper_I_Machine_Native_Final.tex'}
EXACT={'theorem_map.tex','release_catalog.tex','current_traditional_crosswalk.tex','local_imports.tex','namespace_prefixes.tex','dependency_pins.tex','current_edition.tex'}
def blank(m):return re.sub(r'[^\n]',' ',m.group())
def mask(s):
 for p in [r'\\begin\{(lstlisting|verbatim|Verbatim|minted|tikzpicture)\}.*?\\end\{\1\}',r'\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|flalign\*?|displaymath|math)\}.*?\\end\{\1\}',r'(?<!\\)\\\(.*?\\\)',r'(?<!\\)\\\[.*?\\\]',r'(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$']:
  s=re.sub(p,blank,s,flags=re.S)
 s=re.sub(r'\\(?:code|texttt|nolinkurl|url|label|ref|eqref|cref|Cref|cite|RecordID|Depends|Exports|source|excerpt|includegraphics|input|include|field)(?:\[[^\]]*\])?\{[^{}]*\}',blank,s)
 s=re.sub(r'(?<!\\)%[^\n]*',blank,s)
 return s
inventory=[]; paras=[]
for f in FILES:
 p=ROOT/f
 b=OUT/'i_ii_before'/f
 s=b.read_text() if b.exists() else p.read_text()
 m=mask(s)
 exact='/generated/' in f and p.name in EXACT
 rows=[]
 for no,(raw,line) in enumerate(zip(s.splitlines(),m.splitlines()),1):
  kinds=[]
  if ';' in line:kinds.append('semicolon')
  if re.search(r'---|(?<!-)--(?!-)|[—–]|\\text(?:em|en)dash|\s-\s',line):kinds.append('dash')
  if re.search(r'(?<!-)-(?!-)',line):kinds.append('hyphen')
  if re.search(r'it is worth noting|importantly|in summary|in conclusion|crucial|genuinely|simply|clearly|obviously|we now turn|it should be noted',line,re.I):kinds.append('phrase')
  if kinds: rows.append({'line':no,'kinds':kinds,'text':raw})
 mode='delegated companion narrative' if f in CHILD else 'retained exact generated contract/identifier data' if exact else 'parent contextual narrative and punctuation review'
 inventory.append({'file':f,'mode':mode,'before_sha256':hashlib.sha256(s.encode()).hexdigest(),'current_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'candidate_lines':rows,'candidate_counts':{k:sum(k in r['kinds'] for r in rows) for k in ['semicolon','dash','hyphen','phrase']},'raw_whitespace_words':len(s.split())})
 if f in CHILD or exact:continue
 # Read complete remaining ordinary narrative independently of candidate terms.
 for n,block in enumerate(re.split(r'\n\s*\n',m)):
  if re.search(r'[A-Za-z]{3}',block) and not re.fullmatch(r'[\s\\{}\[\]0-9_.*=,/:;-]*',block):
   clean=re.sub(r'\\(?:begin|end|usepackage|documentclass|input|include|definecolor|hypersetup|newcommand|renewcommand|newtheorem|newaliascnt|aliascntresetthe|setlength|setlist|setstretch|titleformat|titlespacing|fancyhead|fancyfoot|fancyhf|pagestyle|graphicspath|lstset|PassOptionsToPackage|newfontfamily|setmonofont|pretocmd|newenvironment)[^\n]*','',block)
   clean='\n'.join(l for l in clean.splitlines() if l.strip())
   if re.search(r'[A-Za-z]{3}',clean):paras.append({'file':f,'paragraph':clean})
(OUT/'i_ii_inventory.json').write_text(json.dumps({'files':inventory,'note':'Broad candidate counts are line-based and include preamble false positives; exact generated contracts are separately classified. Child report supplies its eligible counts.'},indent=2)+'\n')
Path('/tmp/rhythm_remaining_prose.json').write_text(json.dumps(paras))
print('files',len(inventory),'parent narrative paragraphs',len(paras),'masked prose words',sum(len(x['paragraph'].split()) for x in paras))
print(json.dumps({k:sum(x['candidate_counts'][k] for x in inventory if x['mode']=='parent contextual narrative and punctuation review') for k in ['semicolon','dash','hyphen','phrase']}))
