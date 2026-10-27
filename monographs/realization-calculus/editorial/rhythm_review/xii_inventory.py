from pathlib import Path
import json,re,collections
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/rhythm_review'
ns={};exec((E/'iii_iv_inventory.py').read_text().split('rows=[];counts={}')[0],ns);base_mask=ns['mask']
statements=re.compile(r'\\begin\{(theorem|definition|proposition|corollary|lemma|standardfact)\}.*?\\end\{\1\}',re.S)
def mask(s):
 chars=list(base_mask(s))
 for m in statements.finditer(s):
  for i in range(m.start(),m.end()):
   if chars[i]!='\n':chars[i]=' '
 return ''.join(chars)
files=[f'source_ix_xii/XII/publication/source/{f}' for f in ['traditional/Paper_XII_Traditional_Final.tex','traditional/reading_route.tex','visual_guide/Paper_XII_Visual_Guide_Final.tex','visual_guide/source/pages.tex','lean_guide/Paper_XII_Lean_Guide_Final.tex','lean_guide/reading_route.tex']]
patterns=[('semicolon',r';'),('dash',r'---|--|[—–]'),('hyphenated_modifier',r'(?<![A-Za-z\\])[A-Za-z]+(?:-[A-Za-z]+)+'),('formulaic_phrase',r'(?i)\b(?:it is (?:important|worth|useful|helpful)|in (?:summary|conclusion)|in short|serves as|provides a framework|we now|we next|the purpose of|a useful|most importantly|importantly|these boundaries leave|the organization is as follows|the first correction concerns|the second correction concerns|the third correction concerns)\b')]
rows=[]
for f in files:
 s=(R/f).read_text();m=mask(s);lines=s.splitlines()
 for typ,pat in patterns:
  for x in re.finditer(pat,m):
   n=m[:x.start()].count('\n')+1;rows.append({'file':f,'line':n,'type':typ,'candidate':x.group(),'context':lines[n-1],'start':x.start(),'end':x.end()})
(E/'xii_candidates.json').write_text(json.dumps(rows,indent=2)+'\n');(E/'xii_scope.json').write_text(json.dumps({'files':files,'masking':'Math, literal/code/quote/TikZ regions and exact theorem/definition/proposition/corollary/lemma/standard-fact environments excluded. Generated catalog/crosswalk tables not included.','counts':dict(collections.Counter(x['type'] for x in rows))},indent=2)+'\n')
print(collections.Counter(x['type'] for x in rows))
for i,x in enumerate(rows):
 if x['type'] in ['semicolon','formulaic_phrase']:print(i,x['file'].split('/')[-1],x['line'],x['context'])
print('HYPHEN TYPES',collections.Counter(x['candidate'] for x in rows if x['type']=='hyphenated_modifier'))
print('PARENTHETICAL DASHES',[x for x in rows if x['type']=='dash' and x['candidate'] in ['---','—']])
