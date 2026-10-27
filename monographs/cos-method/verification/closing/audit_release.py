#!/usr/bin/env python3
"""Check release correspondence, recorded executions, and PDF structure.

This audit does not establish mathematical validity or interval-library correctness.
It reads, but does not execute, the separately recorded numerical controls.
"""
from pathlib import Path
from collections import Counter
import difflib,hashlib,json,re,sys,zipfile
import fitz
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
readjson=lambda p:json.loads(p.read_text(encoding='utf-8'))
result={}
expected=readjson(ROOT/'verification/figure_pass/baseline_source_hashes.json')
changed=[s for s,h in expected.items() if not (ROOT/s).is_file() or sha(ROOT/s)!=h]
assert not changed,changed
result['engine_and_lean_preservation']={'file_counts':dict(Counter(Path(s).parts[0] for s in expected)),'changed_or_missing':changed}
# Preserve the inventory, while recording every edited statement/proof explicitly.
pattern=re.compile(r'\\begin\{(theorem|corollary|proposition|lemma|remark|algorithm|proof)\}(.*?)\\end\{\1\}',re.S)
old_labels=set();new_labels=set();counts=Counter();env_changes=[];source_changes=[];diff=[]
for old in sorted((HERE/'baseline_book').rglob('*')):
 if old.suffix not in {'.tex','.sty'}:continue
 rel=old.relative_to(HERE/'baseline_book');new=ROOT/'book'/rel
 assert new.is_file(),str(rel)
 a=old.read_text();b=new.read_text()
 assert not any(ord(c)<32 and c not in '\t\n\r' for c in b),f'Control character in {rel}'
 old_labels.update(re.findall(r'\\label\{([^}]+)\}',a));new_labels.update(re.findall(r'\\label\{([^}]+)\}',b))
 oldenv=list(pattern.finditer(a));newenv=list(pattern.finditer(b))
 assert [m.group(1) for m in oldenv]==[m.group(1) for m in newenv],f'Environment inventory changed: {rel}'
 counts.update(m.group(1) for m in newenv)
 for i,(x,y) in enumerate(zip(oldenv,newenv),1):
  if x.group(0)!=y.group(0):env_changes.append({'file':str(rel),'environment':y.group(1),'local_index':i,'label':re.findall(r'\\label\{([^}]+)\}',y.group(0)),'before_sha256':hashlib.sha256(x.group(0).encode()).hexdigest(),'after_sha256':hashlib.sha256(y.group(0).encode()).hexdigest()})
 if a!=b:
  source_changes.append(str(rel));diff.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='baseline/book/'+str(rel),tofile='final/book/'+str(rel)))
assert not old_labels-new_labels,sorted(old_labels-new_labels)
assert counts['proof']==39 and sum(v for k,v in counts.items() if k!='proof')==61,dict(counts)
(HERE/'source_changes.patch').write_text(''.join(diff))
result['mathematical_source']={'environment_counts':dict(counts),'numbered_environments':61,'proofs':39,'baseline_labels':len(old_labels),'missing_labels':sorted(old_labels-new_labels),'new_labels':sorted(new_labels-old_labels),'edited_environments':env_changes,'edited_files':source_changes,'scope':'Inventory preservation and explicit change record, not independent proof verification.'}
# References and assets: check the actual source used to typeset this volume.
texts='\n'.join(p.read_text() for p in (ROOT/'book').rglob('*.tex'))
refs=set()
for x in re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',texts):refs.add(x)
assert not refs-new_labels,refs-new_labels
bib=set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}',texts))
citations=set(y.strip() for x in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',texts) for y in x.split(','))
assert not citations-bib,citations-bib
result['references']={'labels':len(new_labels),'referenced_labels':len(refs),'bibliography_entries':len(bib),'unresolved':[]}
inc=re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',texts)
assert len(inc)==len(set(inc))==50
manifest=readjson(ROOT/'verification/figure_pass/figure_manifest.json');lookup={x['figure']:x for x in manifest};assets=[]
for path in inc:
 p=ROOT/'book'/path;assert p.is_file(),path
 record=lookup[p.stem]
 for src in record['sources']:assert sha(ROOT/src['path'])==src['sha256'],src['path']
 d=fitz.open(p);assert len(d)==1 and not d[0].get_images(),path
 assert p.with_suffix('.svg').is_file() and p.with_suffix('.png').is_file()
 assets.append({'path':path,'sha256':sha(p),'source_hashes_match':True})
result['figures']={'count':len(assets),'single_page_vector_pdfs':True,'editable_svg_and_png_available':True,'assets':assets,'scope':'Published figures and their source/data correspondence are retained; no new benchmark.'}
# Freshly executed records, not historical evidence.
numerical=HERE/'numerical';groups=[readjson(p) for p in sorted(numerical.glob('*_result.json'))]
assert len(groups)==6
for g in groups:assert g['successful'] and g['failures']==0 and g['errors']==0 and g['skipped']==0,g
assert sum(g['testsRun'] for g in groups)==60
status=readjson(numerical/'replay_status.json');assert status['sources_unchanged']
assert status['source_hashes_before']==status['source_hashes_after']
for run in status['runs']:assert run['status']=='completed' and run['exit_code']==0,run
controls=readjson(numerical/'controls.json');assert controls['all_passed'] and len(controls['controls'])==2
worked=readjson(HERE/'worked_example.json')
assert worked['exact_algebra_assertions_passed'] and worked['independent_interval_contained'] and worked['fixed_enclosure_rejects_0_001']
assert not worked['refinements'][0]['accuracy']['accepted'] and worked['refinements'][1]['accuracy']['accepted']
finite=readjson(HERE/'finite/exact_algebra_results.json');extra=readjson(HERE/'finite/closing_controls.json')
assert finite['all_passed'] and len(finite['checks'])==8 and extra['all_passed']
result['executed_checks']={'regression_groups':[{k:g[k] for k in ['group','testsRun','failures','errors','skipped','successful']} for g in groups],'total_tests':60,'independent_controls_passed':2,'worked_example_passed':True,'retained_exact_controls_passed':8,'additional_finite_control_groups':3,'sources_unchanged_during_replay':True,'scope':'Separate executions on stated finite inputs; not a universal correctness proof.'}
# Structure, geometry, and navigation. Visual inspection is a separate recorded step.
pdf=fitz.open(ROOT/'K_COS_Monograph.pdf');outside=[];empty=[];bad_links=[];raster=[];bad_toc=[]
for i,page in enumerate(pdf,1):
 if not page.get_text().strip():empty.append(i)
 for w in page.get_text('words'):
  if w[0]<-.5 or w[1]<-.5 or w[2]>page.rect.width+.5 or w[3]>page.rect.height+.5:outside.append({'page':i,'word':w[4],'bounds':list(w[:4])})
 for link in page.get_links():
  if link.get('kind')==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(pdf):bad_links.append({'page':i,'link':link})
 if page.get_images():raster.append(i)
for item in pdf.get_toc():
 if not 1<=item[2]<=len(pdf):bad_toc.append(item)
assert not (outside or empty or bad_links or bad_toc or raster),(outside,empty,bad_links,bad_toc,raster)
result['pdf']={'pages':len(pdf),'bookmarks':len(pdf.get_toc()),'links':sum(len(p.get_links()) for p in pdf),'raster_image_pages':raster,'empty_pages':empty,'out_of_page_words':outside,'invalid_internal_links':bad_links,'invalid_bookmarks':bad_toc,'sha256':sha(ROOT/'K_COS_Monograph.pdf')}
log=(ROOT/'verification/typesetting/pass_3.txt').read_text(errors='replace')
checks={'warnings':r'Warning:','undefined_references':r'undefined references|Reference .* undefined','undefined_citations':r'Citation .* undefined','overfull_boxes':r'Overfull \\[hv]box','underfull_boxes':r'Underfull \\[hv]box','missing_characters':r'Missing character','duplicate_labels':r'multiply defined'}
result['typesetting']={k:len(re.findall(pattern,log,re.I)) for k,pattern in checks.items()};assert not any(result['typesetting'].values()),result['typesetting']
fonts=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa'}];assert not fonts,fonts
result['font_binaries_supplied']=fonts
result['scope']={'fresh_engine_tests':True,'fresh_independent_controls':True,'fresh_running_example':True,'fresh_lean_compilation':False,'new_benchmarks':False,'end_to_end_formal_proof':False}
(HERE/'publication_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['references','pdf','typesetting','executed_checks','scope']},indent=2))
print(f"PASS: {len(pdf)} pages, 50 vector figures, 61 numbered environments, 39 proofs; 60 recorded regression tests and 2 independent controls passed.")
