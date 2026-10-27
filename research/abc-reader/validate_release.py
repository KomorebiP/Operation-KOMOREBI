"""Check frozen reader sources and rendered layouts. Revision hashes are not proofs."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, re
import fitz

ROOT = Path(__file__).resolve().parent
QA = ROOT.parent / 'tmp/pdfs/abc_qa'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def uncomment(s): return re.sub(r'(?<!\\)%[^\n]*', '', s)

parser=argparse.ArgumentParser()
parser.add_argument('--manual-reviewed',action='store_true')
args=parser.parse_args()
pins=json.loads((ROOT/'evidence/REVIEW_PINS.json').read_text())
assert pins['review_status']=='math_passed_for_stated_scope'
assert pins['source_pins']
matches={name:sha(ROOT/name)==value for name,value in pins['source_pins'].items()}
assert all(matches.values()),matches
report=pins['report_pin']
assert sha(ROOT/report['path'])==report['sha256']
texts={str(p.relative_to(ROOT)):uncomment(p.read_text()) for folder in ['paper','shared','visual'] for p in (ROOT/folder).rglob('*.tex')}
queue=list(texts)
while queue:
 name=queue.pop()
 for target in re.findall(r'\\(?:input|include)\{([^{}]+)\}',texts[name]):
  if '#' in target:continue
  p=(ROOT/name).parent/target
  if p.suffix!='.tex':p=p.with_suffix('.tex')
  p=p.resolve()
  assert p.is_relative_to(ROOT) and p.is_file(),(name,target)
  key=str(p.relative_to(ROOT))
  if key not in texts:texts[key]=uncomment(p.read_text());queue.append(key)
combined='\n'.join(texts.values())
labels=[x for x in re.findall(r'\\label\{([^{}]+)\}',combined) if '#' not in x]
refs=[x.strip() for group in re.findall(r'\\(?:eqref|ref|pageref)\*?\{([^{}]+)\}',combined) for x in group.split(',') if '#' not in x]
keys=re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}',combined)
cites=[x.strip() for group in re.findall(r'\\cite\*?(?:\[[^\]]*\])*\{([^{}]+)\}',combined) for x in group.split(',')]
duplicates=[x for x,n in Counter(labels).items() if n>1]
missing_refs=sorted(set(refs)-set(labels));missing_cites=sorted(set(cites)-set(keys))
assert not duplicates and not missing_refs and not missing_cites,(duplicates,missing_refs,missing_cites)
environments={}
for name,text in texts.items():
 stack=[];errors=[]
 for m in re.finditer(r'\\(begin|end)\{([^{}]+)\}',text):
  action,env=m.groups()
  if action=='begin':stack.append(env)
  elif not stack or stack.pop()!=env:errors.append(m.start())
 environments[name]={'unclosed':stack,'mismatches':errors}
assert all(not x['unclosed'] and not x['mismatches'] for x in environments.values())
source={'date':'2026-10-08','status':'passed','review_revision_matches':matches,'review_report_matches':True,'source_sha256':{name:sha(ROOT/name) for name in texts},'duplicate_labels':duplicates,'missing_references':missing_refs,'missing_citations':missing_cites,'environments':environments,'general_abc':'not established by this work','limitation':'Static checks and hash pins authenticate a reviewed revision, not a mathematical proof.'}
(ROOT/'evidence/SOURCE_VALIDATION.json').write_text(json.dumps(source,indent=2)+'\n')
layout={'date':'2026-10-08','documents':{},'manual_visual_review':'passed, every page inspected' if args.manual_reviewed else 'pending'}
for project,filename in [('paper','Komorebi_ABC_Conjecture_Piece_v1.0.pdf'),('visual','Komorebi_ABC_Visual_Guide_v1.0.pdf')]:
 p=ROOT/'pdf'/filename;doc=fitz.open(p);text='\n'.join(page.get_text() for page in doc);outside=[]
 for i,page in enumerate(doc,1):
  for w in page.get_text('words'):
   x0,y0,x1,y1,token=w[:5]
   if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:outside.append({'page':i,'word':token})
 log=(ROOT/project/'main.log').read_text(errors='replace')
 warnings=[s for s in log.splitlines() if re.search(r'Overfull|undefined|LaTeX Error|Missing character|destination with the same identifier|Label\(s\) may have changed',s)]
 rendered=len(list((QA/project).glob('page-*.png')))
 assert not outside and not warnings,(project,outside,warnings)
 assert '\ufffd' not in text and not re.search(r'\bTODO\b|Figure pending|PLACEHOLDER',text)
 assert rendered==len(doc),(project,rendered,len(doc))
 assert not re.search(r'^Abstract\s*$',text,re.M)
 layout['documents'][project]={'path':'pdf/'+filename,'sha256':sha(p),'pages':len(doc),'rendered_pages':rendered,'extracted_words':len(text.split()),'outside_page_words':outside,'unresolved_tex_warnings':warnings,'replacement_characters':0,'page_size_points':[doc[0].rect.width,doc[0].rect.height]}
fig=json.loads((ROOT/'visual/FIGURE_LAYOUT_CHECK.json').read_text())
comp=json.loads((ROOT/'visual/COMPUTATION_REPORT.json').read_text())
assert comp['status']=='bounded exact data verified'
assert sha(ROOT/'visual/figures.py')==comp['script_sha256']
assert fig['all_passed'] and len(fig['figures'])==24
assert all(x['text_bounds_passed'] and x['card_text_bounds_passed'] for x in fig['figures'])
layout.update(figure_count=24,native_figure_text_bounds='passed',figure_card_text_bounds='passed',status='passed' if args.manual_reviewed else 'manual inspection pending')
(ROOT/'evidence/LAYOUT_VALIDATION.json').write_text(json.dumps(layout,indent=2)+'\n')
print(json.dumps({'sources':source['status'],'layout':layout['status'],'pages':{k:v['pages'] for k,v in layout['documents'].items()}},indent=2))
