from pathlib import Path
import json,hashlib,re,unicodedata,argparse
import fitz
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222');OUT=ROOT/'editorial/rhythm_review'
parser=argparse.ArgumentParser();parser.add_argument('--groups',nargs='*',default=['i_iv','v_viii','ix_x','xi_xii']);parser.add_argument('--skip',nargs='*',default=[]);a=parser.parse_args()
old=json.loads((ROOT/'editorial/book_revision/frontmatter_keep_overrides.json').read_text())
builds=json.loads((OUT/'build_run/REBUILD_ALL_COMPONENTS.json').read_text())
selected=json.loads((ROOT/'component_builds.json').read_text())['components']
old_by_path={c['source_path']:c for c in old['components']}
cid_by_name=json.loads((OUT/'frontmatter_component_identity.json').read_text())
updates={cid_by_name[e['baseline_filename']]:e for e in builds['components'] if e['group'] in a.groups}
preserved={'IV_visual':'editorial/rhythm_review/preserved_outputs/IV_visual.pdf','XI_research_progress':'editorial/rhythm_review/preserved_outputs/XI_research_progress.pdf','XI_research_atlas':'editorial/rhythm_review/preserved_outputs/XI_research_atlas.pdf'}
records=[]
for c in old['components']:
 cid=c['component_id']
 if cid in a.skip:continue
 if cid in updates:
  e=updates[cid];p=e.get('component_pdf',{}).get('path',e['output_pdf']);provenance=e['group']
 elif cid in preserved and (ROOT/preserved[cid]).exists():p=preserved[cid];provenance='root sealed preserved output'
 elif cid in ['III_release_record','IV_verification_closeout']:p=c['source_path'];provenance='frozen documentary input'
 else:continue
 doc=fitz.open(ROOT/p);pages=len(doc);sha=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
 if cid in updates:
  assert sha==updates[cid]['component_pdf']['sha256'],(cid,'hash changed while reading')
 end=min(pages,max(6,max([n for n in c['exclude_pages_1based'] if n<15],default=0)+2))
 inspect=set(range(1,end+1))
 for n in c['exclude_pages_1based']:
  if n>=15:inspect.update(range(max(1,n-1),min(pages,n+1)+1))
 profiles=[];mixed=[]
 for n in sorted(inspect):
  page=doc[n-1];text=page.get_text(sort=True);lines=[]
  for b in page.get_text('dict')['blocks']:
   for l in b.get('lines',[]):
    t=''.join(s['text'] for s in l['spans'])
    lines.append({'text':t,'bbox':list(l['bbox'])})
  lines.sort(key=lambda l:(round(l['bbox'][1],3),l['bbox'][0]));heads=[l for l in lines if l['text'].strip()=='Contents']
  if heads:
   h=heads[0];prefix='\n'.join(l['text'] for l in lines if l['bbox'][3]<=h['bbox'][1]).strip()
   nav='\n'.join(l['text'] for l in lines if l['bbox'][1]>=h['bbox'][1]).strip()
   if n not in c['exclude_pages_1based'] and prefix and len(re.findall('[A-Za-z]',prefix))>40:
    mixed.append({'page_1based':n,'remove_bbox':[0,h['bbox'][1]-.5,page.rect.width,page.rect.height],'preserve_prefix_exact':prefix,'navigation_text_exact':nav,'rationale':'Keep every unique introductory/scope paragraph above Contents; remove only the actual local navigation suffix. Boundary is current Contents heading y0 minus 0.5 pt.'})
  profiles.append({'page_1based':n,'prior_decision':'exclude' if n in c['exclude_pages_1based'] else 'keep','text':text,'line_count':len(lines),'contents_heading_bboxes':[h['bbox'] for h in heads],'first_lines':text.splitlines()[:5],'last_lines':text.splitlines()[-3:]})
 records.append({'component_id':cid,'path':p,'provenance':provenance,'sha256':sha,'pages':pages,'previous_pages':c['pages'],'previous_exclude_pages_1based':c['exclude_pages_1based'],'front_pages_inspected':sorted(inspect),'profiles':profiles,'mixed_toc_regions':mixed})
 doc.close()
(OUT/'frontmatter_probe.json').write_text(json.dumps({'records':records,'groups':a.groups,'skip':a.skip,'scope':'Read-only source-PDF probe. Proposed keep/drop decisions require contextual page review; no root map changed.'},indent=2)+'\n')
print(json.dumps({'records':len(records),'page_counts_changed':[(r['component_id'],r['previous_pages'],r['pages']) for r in records if r['pages']!=r['previous_pages']],'mixed_toc_regions':[(r['component_id'],[(m['page_1based'],m['remove_bbox'][1]) for m in r['mixed_toc_regions']]) for r in records if r['mixed_toc_regions']]},indent=2))
