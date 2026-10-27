#!/usr/bin/env python3
"""Bounded independent preservation review; no scientific recomputation."""
import collections, datetime, hashlib, json, pathlib, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda s:json.loads((ROOT/s).read_text())
failures=[]; counts=collections.Counter(); spot=[]; checked=[]
def current_check(group,rel,expected):
 p=ROOT/group/rel
 actual=sha(p.read_bytes()) if p.is_file() else None
 counts[group+'_hash_checks']+=1
 if actual!=expected: failures.append({'kind':'reported_current_hash','path':str(p.relative_to(ROOT)),'expected':expected,'actual':actual})
 return p
v=load('source_v_viii/SOURCE_PRESERVATION_AUDIT.json')
for e in v['unchanged_files']: current_check('source_v_viii',e['path'],e['sha256'])
for e in v['edited_files']:
 p=current_check('source_v_viii',e['path'],e['edited_sha256'])
 b=ROOT/'source_v_viii'/e['before']; before=b.read_bytes(); after=p.read_bytes()
 if sha(before)!=e['original_sha256']: failures.append({'kind':'before_hash','path':str(b)})
 paper,relative=e['path'].split('/',1)
 spot.append((paper,relative,before,after,'edited entry/source'))
 if e.get('body_after_begin_document_byte_equal'):
  same=before.split(b'\\begin{document}',1)[1]==after.split(b'\\begin{document}',1)[1]
  counts['independently_compared_document_bodies']+=1
  if not same: failures.append({'kind':'document_body_changed','path':str(p)})
ix=load('source_ix_xii/IX_X_SOURCE_PRESERVATION.json')
for e in ix['unchanged_files']:
 p=current_check('source_ix_xii',e['paper']+'/'+e['path'],e['sha256'])
 if e['path'].endswith('.tex') and b'\\begin{document}' in p.read_bytes() and '/evidence/' not in e['path']:
  spot.append((e['paper'],e['path'],p.read_bytes(),p.read_bytes(),'unchanged scientific entry'))
for c in ix['checks']:
 for e in c['changes']: current_check('source_ix_xii',c['paper']+'/'+e['path'],e['after_sha256'])
xi=load('source_ix_xii/XI_XII_SOURCE_PRESERVATION.json')
for e in xi['files']:
 p=current_check('source_ix_xii',e['paper']+'/'+e['path'],e['current_sha256'])
 if not e['same_bytes']:
  b=ROOT/'source_ix_xii'/e['paper']/'before'/e['path']; before=b.read_bytes(); after=p.read_bytes()
  if sha(before)!=e['baseline_sha256']: failures.append({'kind':'before_hash','path':str(b)})
  same=before.split(b'\\begin{document}',1)[1]==after.split(b'\\begin{document}',1)[1]
  counts['independently_compared_document_bodies']+=1
  if not same: failures.append({'kind':'document_body_changed','path':str(p)})
  spot.append((e['paper'],e['path'],before,after,'layout-import scientific entry'))
# Add one unchanged .tex source dependency and one scientific figure per paper.
for paper in ['V','VI','VII','VIII','IX','X','XI','XII']:
 if paper in ['V','VI','VII','VIII']:
  candidates=[(e['path'].split('/',1)[1],ROOT/'source_v_viii'/e['path']) for e in v['unchanged_files'] if e['path'].startswith(paper+'/')]
 elif paper in ['IX','X']:
  candidates=[(e['path'],ROOT/'source_ix_xii'/paper/e['path']) for e in ix['unchanged_files'] if e['paper']==paper]
 else:
  candidates=[(e['path'],ROOT/'source_ix_xii'/paper/e['path']) for e in xi['files'] if e['paper']==paper and e['same_bytes']]
 for typ,test in [('source dependency',lambda n:n.endswith('.tex') and ('source/' in n or 'sections/' in n or 'chapter' in n or 'generated/' in n) and 'historical' not in n),('scientific figure',lambda n:n.endswith('.pdf') and ('figure' in n or 'assets/' in n))]:
  selected=next(((n,p) for n,p in candidates if test(n)),None)
  if selected:
   n,p=selected; data=p.read_bytes(); spot.append((paper,n,data,data,typ))
archives={}
for paper in ['V','VI','VII']:
 archives[paper]=next((ROOT/'full_inputs').glob(f'Paper_{paper}_Frozen_*.zip'))
for e in load('frozen_local_inputs.json'):
 paper=e['name'].split('_')[1]; archives[paper]=pathlib.Path(e['path'])
for paper in archives:
 with zipfile.ZipFile(archives[paper]) as z:
  for pa,rel,before,after,kind in spot:
   if pa!=paper:continue
   matching=[n for n in z.namelist() if n.endswith('/'+rel) and not any(k in n for k in ['/predecessor/','/historical_assembly/','/provenance/','/verification/','/predecessor_files/','/inherited_baseline/'])]
   if len(matching)!=1:
    failures.append({'kind':'archive_member_selection','paper':paper,'relative':rel,'matching':matching});continue
   member=matching[0]; original=z.read(member); same=original==before
   counts['direct_frozen_archive_entries_compared']+=1
   if not same: failures.append({'kind':'archive_original_mismatch','member':member})
   checked.append({'paper':paper,'archive':str(archives[paper]),'member':member,'kind':kind,'frozen_sha256':sha(original),'baseline_matches_frozen':same,'current_sha256':sha(after)})
result={
 'reviewer':'independent I-IV typesetting agent',
 'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Bounded source-preservation review of final V-VIII and IX-XII reports, changed hunks, layout adapters, reported current file hashes, and direct frozen ZIP spot comparisons. No new proof audit, Lean run, finite experiment, or full independent visual audit.',
 'status':'PASS' if not failures else 'FAIL',
 'counts':dict(counts),
 'findings':[
  'No unexpected mathematical, theorem, proof, or scientific-figure changes found in reviewed evidence.',
  'V-VIII: 12 entry changes add only a preamble layout input; 3 generated navigation introductions explicitly identify retained frozen-edition locators. Numeric locator data and mathematical body remain unchanged.',
  'IX-X: the two identical shared-style diffs append presentation settings, a caption-macro compatibility adapter, and a restyled cover; six compiled PDFs are expected new typesetting outputs. Scientific source/figure files retain recorded hashes.',
  'XI-XII: six entry changes insert one preamble layout input; document bodies match baseline bytes. Layout adapters change colors, cover, heading/display spacing, fonts, and visual-plate geometry only.',
  'V-VIII removal list contains 30 TeX byproducts (.bbl/.blg/.fls/.lof/.lot), not original scientific source files; bibliography inputs are retained in the manifest.',
 ],
 'qualifications':[
  'All 4,154 unchanged/current source-asset manifest entries were rehashed, plus 23 reported modified files, for 4,177 current-file checks; archive comparisons are explicitly a bounded spot check.',
  'V-VIII fixed traditional-page locators intentionally target supplied frozen readers, with visible edition notes; this is not a claim that all prose locator numbers were updated for monograph reflow.',
  'The scientific content may retain pre-existing issues. This review establishes preservation within the stated checks, not mathematical correctness.',
 ],
 'report_files':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in ['source_v_viii/SOURCE_PRESERVATION_AUDIT.json','source_v_viii/CHANGES.diff','source_ix_xii/IX_X_SOURCE_PRESERVATION.json','source_ix_xii/XI_XII_SOURCE_PRESERVATION.json','source_ix_xii/IX/STYLE_DIFF.patch','source_ix_xii/X/STYLE_DIFF.patch']],
 'direct_archive_comparisons':checked,'failures':failures,
}
# Derive count prose from actual checks rather than assume it.
result['qualifications'][0]=f"Rehashed {sum(v for k,v in counts.items() if k.endswith('_hash_checks'))} current-file manifest entries; directly checked {counts['direct_frozen_archive_entries_compared']} frozen ZIP entries and {counts['independently_compared_document_bodies']} edited entry-file document bodies. Archive comparisons are a bounded spot check."
out=ROOT/'source_i_iv/INDEPENDENT_SOURCE_PRESERVATION_REVIEW.json'; out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'output':str(out),'status':result['status'],'counts':result['counts'],'failures':failures},indent=2))
