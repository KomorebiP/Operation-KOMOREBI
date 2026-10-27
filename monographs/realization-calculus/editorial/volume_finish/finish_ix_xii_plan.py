from pathlib import Path
import json,fitz,copy
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');O=R/'editorial/volume_finish';P=O/'ix_xii_plan.json';j=json.loads(P.read_text());s=json.loads((R/'book/build_spec.json').read_text());c={x['id']:x for z in s['parts'] for x in z['components']};d={k:fitz.open(R/v['path']) for k,v in c.items() if v['paper'] in ['IX','X','XI','XII']}
replacements={
('IX_traditional',106):[('This\ncontrol-design limitation was identified and corrected before the release gate.','')],
('IX_traditional',113):[('A completed version of 13.3 must say','A full form of 13.3 must state')],
('IX_traditional',173):[('The\nsource proves this failure, and the release verifier separately attempts and rejects an invalid proof of\nthe even-length identity.','The source proves the failure of the even-length identity.')],
('IX_traditional',201):[('This release proves','This argument proves'),('while keeping item 7.5\npending.','under its stated hypotheses.')],
('IX_traditional',207):[('The all-residue Theorem 7.5 remains pending.','The all-residue proof appears in a later supplement.'),('This release proves','This argument proves')],
('IX_traditional',212):[('Those actual-family estimates and the full remaining\npropagation are not supplied by this release.','Those estimates and their propagation lie beyond this standard-window argument.')],
('X_traditional',77):[('The scalar/Mellin checkpoint','The scalar/Mellin construction'),('The later checked source','The checked source')],
('XI_traditional',36):[('The later constructions','The constructions'),('accompany this edition.','accompany the volume.')]
}
new=[];converted=[]
for x in j['changes']:
 key=(x['component_id'],x['source_page_1based'])
 math_target=key in replacements and x['new'] and x['action']=='replace_block'
 if math_target:
  if key==('IX_traditional',212) and not x['old'].startswith('The all-residue Theorem'):math_target=False
 if math_target:
  for old,nn in replacements[key]:
   assert old in x['old'],(key,old)
   y=copy.deepcopy(x);y.update({'old':old,'new':nn,'kind':'replace_phrase','action':'replace_phrase','context':'Matched prose fragment within mathematical paragraph; native mathematical glyphs and all other prose remain untouched.','reason':'Remove publication-history wording without retyping the neighboring mathematical content.'})
   rects=d[key[0]][key[1]-1].search_for(' '.join(old.split()))
   y['match_rects']=[list(z) for z in rects]
   if rects:
    b=fitz.Rect(rects[0])
    for z in rects[1:]:b|=z
    y['bbox']=list(b)
   else:y['bbox_hint_only']=True
   new.append(y)
  converted.append(key)
 else:
  y=copy.deepcopy(x)
  if y['action'] in ['remove_line','remove_block']:
   y['kind']='omit_region'
  elif y['action']=='replace_line':y['kind']='replace_phrase'
  else:y['kind']='replace_block'
  new.append(y)
j['changes']=new
j['status']='FROZEN_PROPOSAL_READ_ONLY'
j['display_adapter_notes']=['kind=omit_region uses its exact recorded line or block bbox; kind=replace_phrase must resolve the old prose within that context before removing characters.','All eight initially math-bearing paragraph rewrites were converted to14 minimal prose-fragment edits; original math spans must remain exact.','Whole-page and source relocation candidates are recommendations only. Source section boundaries should be validated against the current selection.','The source DOI/arXiv revision IDs and publication years remain bibliographic identity; move to sources. Technical compiler pins and commands can stay solely in package.']
j['prose_fragment_conversions']=[{'component_id':x[0],'source_page_1based':x[1]} for x in converted]
j['cautions']=[x for x in j['cautions'] if not x.startswith('The p201 rewrite')]
P.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
from collections import Counter
print(json.dumps({'status':j['status'],'actions':len(new),'kinds':dict(Counter(x['kind'] for x in new)),'math_paragraphs_converted':len(converted),'catalogue_metadata_lines':sum(x['component_id']=='XI_lean' and x['old'].startswith('Selected layer:') for x in new)},indent=2))
