from pathlib import Path
import json,re,hashlib,collections
import fitz
R=Path(__file__).resolve().parent;W=R.parent
pdf=R/'Komorebi_Physics_Collected_Monograph.pdf';d=fitz.open(pdf)
report={'pages':len(d),'bookmarks':len(d.get_toc()),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'empty_pages':[],'invalid_destinations':[],'text_outside_page':[],'development_labels_in_reading_parts':[],'internal_links':0,'external_links':0}
for i,p in enumerate(d):
 t=p.get_text()
 if len(t.strip())<30:report['empty_pages'].append(i+1)
 if i<470:
  for ln in t.splitlines():
   if re.search(r'\b(?:v\d+\.\d+|(?:edition|version)\s+\d+\.\d+|Block\s*\d+|this edition|next phase|new in this|restart point|previous release|in this session|handoff)',ln,re.I):report['development_labels_in_reading_parts'].append([i+1,ln])
 for l in p.get_links():
  if l['kind']==fitz.LINK_GOTO:
   report['internal_links']+=1
   if not 0<=l.get('page',-1)<len(d):report['invalid_destinations'].append([i+1,dict(l)])
  elif l['kind']==fitz.LINK_URI:report['external_links']+=1
 for b in p.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   bb=fitz.Rect(l['bbox'])
   if bb.x0<-.5 or bb.x1>p.rect.width+.5 or bb.y0<-.5 or bb.y1>p.rect.height+.5:report['text_outside_page'].append([i+1,''.join(s['text'] for s in l['spans']),list(bb)])
for level,title,page in d.get_toc():
 if not 1<=page<=len(d):report['invalid_destinations'].append(['bookmark',title,page])
(R/'audit/pdf_text_and_navigation_scan.json').write_text(json.dumps(report,indent=2))
logs=[]
for pdf in sorted((R/'compiled').glob('*/*.pdf')):
 log=pdf.with_suffix('.log').read_text(errors='replace')
 logs.append({'document':pdf.stem,'pages':len(fitz.open(pdf)),'successful_output_line':bool(re.search(r'Output written on',log)),'overfull':re.findall(r'Overfull[^\n]*',log),'undefined_references':bool(re.search(r'(undefined references|Reference .* undefined|Citation .* undefined)',log)), 'missing_glyphs':re.findall('Missing character[^\n]*',log)})
(R/'audit/latex_all_final_logs.json').write_text(json.dumps(logs,indent=2))
# A textual invariant check, not a mathematical review. Record all differences.
pairs=[(W/'physics_monograph_v0.5.0/source',R/'source/monographs'),(W/'backreaction',R/'source/backreaction'),(W/'cosmology/Projector_Refinement_Physics_Volume_II_Source_and_Reproducibility',R/'source/cosmology')]
# Generator is a single manuscript.
proof_pat=re.compile(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',re.S)
protected=[];different=[]
for a,b in pairs:
 for orig in sorted(a.rglob('*.tex')):
  dest=b/orig.relative_to(a)
  if not dest.exists():continue
  x=orig.read_text();y=dest.read_text();px=proof_pat.findall(x);py=proof_pat.findall(y)
  if not px and not py:continue
  rec={'file':str(dest.relative_to(R)),'original_proof_environments':len(px),'edited_proof_environments':len(py),'identical_ordered_proof_bodies':px==py}
  protected.append(rec)
  if px!=py:different.append(rec)
old=W/'Komorebi_Physics_Collected_v0.6.0/manuscript/Block50_Spectral_Generator_Bridge.tex';new=R/'source/generator/Block50_Spectral_Generator_Bridge.tex'
if old.exists():
 px=proof_pat.findall(old.read_text());py=proof_pat.findall(new.read_text());rec={'file':str(new.relative_to(R)),'original_proof_environments':len(px),'edited_proof_environments':len(py),'identical_ordered_proof_bodies':px==py};protected.append(rec)
 if px!=py:different.append(rec)
(R/'audit/proof_environment_text_comparison.json').write_text(json.dumps({'scope':'LaTeX proof environments only. Does not cover manually marked proofs or independently validate correctness.','files':protected,'differences':different},indent=2))
print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},indent=2))
print('lists',{k:len(v) for k,v in report.items() if isinstance(v,list)})
print('log warnings',sum(len(x['overfull'])+len(x['missing_glyphs'])+int(x['undefined_references']) for x in logs))
print('proof files',len(protected),'proof environments',sum(x['original_proof_environments'] for x in protected),'changed files',different)
