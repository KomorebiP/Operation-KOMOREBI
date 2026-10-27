#!/usr/bin/env python3
"""Audit preserved sources, vector assets, labels and PDF geometry.

These checks concern presentation and finite source correspondence, not proof
validity, interval-library correctness, or fresh engine/Lean execution.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={}
expected=json.loads((HERE/'baseline_source_hashes.json').read_text())
changed=[s for s,h in expected.items() if not (ROOT/s).is_file() or sha(ROOT/s)!=h]
result['preserved_source_files']={'counts':dict(collections.Counter(Path(s).parts[0] for s in expected)),'changed_or_missing':changed}
assert not changed,changed

# Compare literal theorem-family and proof environments, not just their counts.
pattern=re.compile(r'\\begin\{(theorem|corollary|proposition|lemma|remark|algorithm|proof)\}(.*?)\\end\{\1\}',re.S)
previous=HERE/'baseline_book_source'
old_env=[];new_env=[];old_labels=set();new_labels=set()
for old in sorted(previous.rglob('*.tex')):
 rel=old.relative_to(previous);new=ROOT/'book'/rel
 a=old.read_text();b=new.read_text()
 old_env.extend((str(rel),m.group(1),m.group(0)) for m in pattern.finditer(a))
 new_env.extend((str(rel),m.group(1),m.group(0)) for m in pattern.finditer(b))
 old_labels.update(re.findall(r'\\label\{([^}]+)\}',a));new_labels.update(re.findall(r'\\label\{([^}]+)\}',b))
assert old_env==new_env,'A numbered statement or proof environment changed.'
assert not old_labels-new_labels,old_labels-new_labels
result['mathematical_source']={'literal_environments_unchanged':True,'counts':dict(collections.Counter(t for p,t,b in new_env)),'baseline_labels_preserved':len(old_labels),'new_labels':sorted(new_labels-old_labels)}

inc=[]
for p in sorted((ROOT/'book').rglob('*.tex')):
 if 'figures_' in str(p):continue
 inc.extend(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',p.read_text()))
assert len(inc)==50,(len(inc),inc)
assert len(set(inc))==50
manifest=json.loads((HERE/'figure_manifest.json').read_text())
lookup={r['figure']:r for r in manifest}
assets=[]
for path in inc:
 p=ROOT/'book'/path;assert p.is_file(),p
 record=lookup[p.stem];assert record['text_bounds']=='pass' and record['data_bounds']=='pass'
 for src in record['sources']:
  assert sha(ROOT/src['path'])==src['sha256'],src['path']
 d=fitz.open(p);assert len(d)==1
 assert sum(len(page.get_images()) for page in d)==0,p
 assert p.with_suffix('.svg').is_file() and p.with_suffix('.png').is_file()
 assets.append({'file':path,'sha256':sha(p),'raster_images':0,'line_scatter_points_checked':record['line_scatter_points_checked'],'scope':record['scope']})
result['figures']={'count':len(assets),'all_single_page_vector':True,'assets':assets}

# The three restored packet tables must match their retained ZIP members byte-for-byte.
z=ROOT/'provenance/K-COS_Query_Adaptive_Spectral_Packetization_v0.1_Source.zip'
recovered=[]
with zipfile.ZipFile(z) as archive:
 for name in ['adaptive_certificate_accuracy.csv','adaptive_runtime_scaling.csv','adaptive_tolerance_ladder.csv']:
  matches=[n for n in archive.namelist() if n.endswith('/'+name)]
  assert len(matches)==1,matches
  raw=archive.read(matches[0]);p=ROOT/'illustrations/publication_data'/name
  assert raw==p.read_bytes(),name
  recovered.append({'name':name,'archive_member':matches[0],'sha256':sha(p)})
result['recovered_packet_tables']=recovered

pdf=fitz.open(ROOT/'K_COS_Monograph.pdf');bad_links=[];outside=[];empty=[];raster=[];figure_pages=[]
for i,page in enumerate(pdf):
 txt=page.get_text()
 if not txt.strip():empty.append(i+1)
 for w in page.get_text('words'):
  if w[0]<-.5 or w[1]<-.5 or w[2]>page.rect.width+.5 or w[3]>page.rect.height+.5:
   outside.append({'page':i+1,'word':w[4],'bounds':list(w[:4])})
 for link in page.get_links():
  if link.get('kind')==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(pdf):bad_links.append({'page':i+1,'link':link})
 if page.get_images():raster.append(i+1)
 if any(tag in txt for tag in ['RECORDED CONTROL','DECLARED VISUAL STUDY','METHOD MAP','RETAINED PACKET','DIRECTED WORKED','EXACT GEOMETRY','EXACT REPRESENTATION','STORAGE MODEL','TIMING MODEL','EXECUTION MODEL','DECLARED WORKED','DIRECTED CONTROL RECORD','RETAINED CPU']):figure_pages.append(i+1)
result['pdf']={'pages':len(pdf),'bookmarks':len(pdf.get_toc()),'links':sum(len(p.get_links()) for p in pdf),'raster_image_pages':raster,'empty_text_pages':empty,'out_of_page_words':outside,'invalid_internal_links':bad_links,'identified_figure_pages':figure_pages}
assert not outside,outside[:10]
assert not empty,empty
assert not bad_links,bad_links
assert not raster,raster
log=(ROOT/'verification/typesetting/pass_3.txt').read_text(errors='replace')
checks={'undefined_references':r'undefined references|Reference .* undefined','undefined_citations':r'Citation .* undefined','overfull_boxes':r'Overfull \\[hv]box','underfull_boxes':r'Underfull \\[hv]box','missing_characters':r'Missing character','multiply_defined_labels':r'multiply defined'}
result['typesetting']={k:len(re.findall(pattern,log,re.I)) for k,pattern in checks.items()}
assert not any(result['typesetting'].values()),result['typesetting']
result['scope']={'engine_tests_rerun':False,'lean_rerun':False,'new_benchmarks':False,'claim':'Source-preservation, figure-data, geometry and navigation checks only.'}
(HERE/'publication_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['figures','recovered_packet_tables']},indent=2))
print('PASS:',len(assets),'vector figures;',len(pdf),'pages.')
