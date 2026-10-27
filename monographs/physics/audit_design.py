#!/usr/bin/env python3
"""Document/layout checks; not a proof checker or physical-model validation."""
from pathlib import Path
import sys,re,json,hashlib,collections
import fitz
ROOT=Path(__file__).resolve().parent;A=ROOT/'audit';A.mkdir(exist_ok=True)
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else None

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if BASE:
 checks={};changes=[]
 patterns={
  'proof_environments':r'\\begin\{proof\}(?:\[[^]]*\])?.*?\\end\{proof\}',
  'numbered_display_environments':r'\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',
  'unnumbered_displays':r'\\\[.*?\\\]',
  'theorem_statement_environments':r'\\begin\{(theorem|lemma|proposition|corollary|definition)\}(?:\[[^]]*\])?.*?\\end\{\1\}'
 }
 for name,pattern in patterns.items():
  count=0;changed=[]
  for f in (BASE/'source').rglob('*.tex'):
   g=ROOT/f.relative_to(BASE)
   if not g.exists():changed.append({'file':str(f.relative_to(BASE)),'reason':'missing file'});continue
   before=[m.group(0) for m in re.finditer(pattern,f.read_text(errors='replace'),re.S)]
   after=[m.group(0) for m in re.finditer(pattern,g.read_text(errors='replace'),re.S)]
   count+=len(before)
   if before!=after:changed.append(str(f.relative_to(BASE)))
  checks[name]={'count_in_input':count,'ordered_bodies_identical_by_source_file':not changed,'differences':changed}
 assets=[];bad_assets=[]
 for f in (BASE/'source').rglob('*'):
  if f.is_file() and f.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.svg'}:
   rel=f.relative_to(BASE);g=ROOT/rel;ok=g.exists() and digest(f)==digest(g);assets.append(str(rel))
   if not ok:bad_assets.append(str(rel))
 checks['scientific_image_assets']={'count':len(assets),'all_byte_identical':not bad_assets,'differences':bad_assets}
 for f in (BASE/'source').rglob('*'):
  if f.is_file():
   g=ROOT/f.relative_to(BASE)
   if g.exists() and digest(f)!=digest(g):changes.append(str(f.relative_to(BASE)))
 formal=[]
 for f in (BASE/'formal').rglob('*'):
  if f.is_file():
   g=ROOT/f.relative_to(BASE);formal.append({'file':str(f.relative_to(BASE)),'identical':g.exists() and digest(f)==digest(g)})
 checks['formal_source_files']=formal
 checks['changed_source_files']=changes
 checks['boundary']='Textual invariants and file identity checks, not an independent proof or empirical audit.'
 (A/'source_preservation_checks.json').write_text(json.dumps(checks,indent=2))

# Inspect the compiled log of every source component.
logs=[]
for f in sorted((ROOT/'compiled').glob('*/*.log')):
 t=f.read_text(errors='replace')
 logs.append({'source':f.parent.name,'overfull_boxes':re.findall(r'Overfull [^\n]*',t),'undefined_references':re.findall(r"(?:LaTeX Warning: (?:Reference|Citation)[^\n]*undefined|There were undefined references)",t),'missing_glyphs':re.findall(r'Missing character:[^\n]*',t),'font_substitution_warnings':re.findall(r'LaTeX Font Warning:[^\n]*',t),'other_warnings':re.findall(r'(?:Package [^\n]* Warning:|LaTeX Warning:)[^\n]*',t)})
(A/'final_typography_logs.json').write_text(json.dumps(logs,indent=2))

p=ROOT/'Komorebi_Physics.pdf';D=fitz.open(p)
invalid=[];bounds=[];empty=[];replacement=[];links=collections.Counter();font_refs=set()
for i,page in enumerate(D):
 text=page.get_text()
 if not text.strip():empty.append(i+1)
 if '\ufffd' in text:replacement.append(i+1)
 for l in page.get_links():
  links[l['kind']]+=1
  if l['kind']==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(D):invalid.append({'page':i+1,'link':str(l)})
 for b in page.get_text('dict')['blocks']:
  if b.get('type')!=0:continue
  for line in b['lines']:
   r=fitz.Rect(line['bbox']);t=''.join(s['text'] for s in line['spans'])
   if t.strip() and (r.x0<-.5 or r.y0<-.5 or r.x1>page.rect.width+.5 or r.y1>page.rect.height+.5):bounds.append({'page':i+1,'bbox':list(r),'text':t[:160]})
 for f in page.get_fonts(full=True):font_refs.add(f[0])
fonts=[]
for xref in sorted(font_refs):
 try:
  name,ext,kind,raw=D.extract_font(xref);fonts.append({'xref':xref,'name':name,'type':kind,'embedded_program_bytes':len(raw),'extension':ext})
 except Exception as ex:fonts.append({'xref':xref,'error':str(ex)})
bad_toc=[t for t in D.get_toc() if not 1<=t[2]<=len(D)]
result={'pages':len(D),'file_size_bytes':p.stat().st_size,'sha256':digest(p),'bookmarks':len(D.get_toc()),'invalid_bookmarks':bad_toc,'links_by_kind':dict(links),'invalid_internal_destinations':invalid,'text_outside_media_box':bounds,'empty_text_pages':empty,'replacement_character_pages':replacement,'page_labels':D.get_page_labels(),'unique_font_resources':len(fonts),'fonts_without_extracted_program':[x for x in fonts if x.get('embedded_program_bytes')==0],'note':'Type 3 glyph programs, when present, are embedded drawing instructions rather than a separate font program.'}
(A/'pdf_design_checks.json').write_text(json.dumps(result,indent=2))
(A/'font_inventory.json').write_text(json.dumps(fonts,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('fonts_without_extracted_program',)},indent=2))
if invalid or bad_toc or bounds or empty or replacement:raise SystemExit('PDF check requires inspection')
if any(x['overfull_boxes'] or x['undefined_references'] or x['missing_glyphs'] or x['font_substitution_warnings'] for x in logs):raise SystemExit('TeX check requires inspection')
if BASE:
 if any(not checks[x]['ordered_bodies_identical_by_source_file'] for x in patterns):raise SystemExit('Source comparison requires inspection')
 if bad_assets or any(not x['identical'] for x in formal):raise SystemExit('Asset or formal-source identity mismatch')
