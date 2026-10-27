"""Bind the bounded I–VIII candidate and plate-outline review to the final book."""
from pathlib import Path
import json,hashlib,collections,re,fitz
ROOT=Path(__file__).resolve().parents[2]
review=ROOT/'editorial/volume_finish'
probe=json.loads((review/'final_text_candidates.json').read_text());pdf=ROOT/'output/Realization_Calculus.pdf'
expected='9f557736a27163e361170fcc969c3add4b9c01730c325305e4d987d076e45946'
assert probe['pdf_sha256']==hashlib.sha256(pdf.read_bytes()).hexdigest()==expected
prior=json.loads((review/'final_candidate_review_i_viii.json').read_text());scope={'I','II','III','IV','V','VI','VII','VIII'}
rows=[x for x in probe['matches'] if not x.get('component_id') or x['component_id'].split('_')[0] in scope]
doc=fitz.open(pdf);decisions=[]
for x in rows:
 row=dict(x);cid=x.get('component_id');text=x['text']
 if x['reference']:category='bibliographic_source_identity';reason='A scholarly edition, publication/access date or version of a cited documentation source identifies a reference in the final back matter. It does not identify a release of this book.'
 elif cid=='I_machine_native' and x['source_page']==17:category='protected_verbatim_source_statement';reason='Exact generated source-record statement beside stable ID and printed digest; retain its source wording. No numeric release identifier or date occurs here.'
 elif cid=='VI_lean' and text in {str(n) for n in range(2020,2030)}:
  footer=doc[x['book_page']-1].get_text(clip=fitz.Rect(0,750,612,792)).strip();assert footer==text==str(x['book_page']-10)
  row.update({'footer_bbox':[0,750,612,792],'verified_footer_text':footer});category='global_page_folio';reason='Direct final-PDF footer inspection confirms the global printed folio, equal to physical book page minus ten. It is neither a date nor a Lean declaration ID.'
 elif 'historical' in text.lower():category='scope_and_attribution_boundary';reason='Substantive limit on novelty, priority or certification claims; it is not production chronology.'
 elif cid=='III_analytic_supplement':category='mathematical_variable';reason='Directional derivative arguments v1,...,vr; these are mathematical variables, not release labels.'
 elif re.search(r'\bversions?\b',text,re.I):category='mathematical_variant';reason='Mathematical variant, formulation or specialization under stated hypotheses, with no release label or date.'
 else:raise ValueError('Unexpected final candidate: '+str(x))
 row.update({'decision':'retain','category':category,'reason':reason,'context_sha256':hashlib.sha256(json.dumps({k:x[k] for k in ['component_id','source_page','reference','text']},sort_keys=True,ensure_ascii=False).encode()).hexdigest()});decisions.append(row)
assert len(decisions)==76
spec=json.loads((ROOT/'book/build_spec.json').read_text());comps={c['id']:c for p in spec['parts'] for c in p['components']};toc=doc.get_toc();plate_checks=[]
for cid,mapname,prefix,count in [('IV_visual','i_iv_bookmark_titles.json','Plate IV.',26),('XI_research_atlas','ix_xii_bookmark_titles.json','Plate XI.',32)]:
 rawmap=json.loads((review/mapname).read_text());mp=rawmap.get('components',rawmap)[cid]
 mapping={old:new for old,new in mp.items() if isinstance(new,str) and new.startswith(prefix)};assert len(mapping)==count
 with fitz.open(ROOT/comps[cid]['path']) as source:source_toc=source.get_toc()
 for old,new in mapping.items():
  originals=[x for x in source_toc if x[1]==old];actual=[x for x in toc if x[1]==new];assert len(originals)==len(actual)==1,(cid,old,new,len(originals),len(actual))
  raw=originals[0][2]-1;page=comps[cid]['book_pages'][str(raw)]+1;assert actual[0][2]==page
  assert not any(x[1]==old for x in toc)
  plate_checks.append({'component_id':cid,'source_page':raw+1,'old_title':old,'final_title':new,'book_page':page,'qualified_title_present_once':True,'destination_matches_source_map':True,'old_title_absent':True})
assert len(plate_checks)==58
assert probe['bookmark_matches']==[]
quote=prior['protected_quote'];machine=comps['I_machine_native']
with fitz.open(ROOT/machine['path']) as m:txt=m[16].get_text()
q=txt.split('Statement.\n',1)[1].split('Formal correspondence.',1)[0].strip();normalize=lambda z:' '.join(re.sub(r'(?<=[A-Za-z])-\n(?=[A-Za-z])','',z).split());assert normalize(q)==normalize(quote['quote']);assert quote['record_id'] in txt and quote['printed_statement_digest'] in txt
quote['verified_against_final_component_sha256']=machine['sha256']
final={'status':'PASS','pdf_sha256':expected,'physical_pages':len(doc),'scope':'All76 I–VIII or outer text candidates in the final2714-page book, the protected I-machine source quotation, all26 IV visual and32 XI atlas qualified plate bookmarks, and final bookmark scan. IX–XII prose classified separately. No PDF or plan changes by this review.','candidate_count':len(decisions),'classifications':dict(collections.Counter(x['category'] for x in decisions)),'actionable_release_or_history_prose_findings':[],'outer_matches':sum(not x.get('component_id') for x in decisions),'protected_quote':quote,'text_decisions':decisions,'plate_bookmark_checks':plate_checks,'plate_bookmark_counts':{'IV_visual':26,'XI_research_atlas':32},'final_bookmark_candidate_count':0,'bibliography_case_and_wrap_review':'Four changed candidate lines on V source133 and VIII source121 were reread. The Gibbs phenomenon and CUDA C++ proper-case corrections and their new wraps preserve the bibliographic identities and remain entirely in the final source section.','rebound_from_probe_sha256':prior['pdf_sha256'],'new_unmatched_candidates':[],'mathematical_token_changes':'None.'}
(review/'final_candidate_review_i_viii.json').write_text(json.dumps(final,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:final[k] for k in ['status','pdf_sha256','physical_pages','candidate_count','classifications','plate_bookmark_counts','final_bookmark_candidate_count','actionable_release_or_history_prose_findings']},indent=2))
