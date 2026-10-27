"""Seal completed editorial and sampled visual reviews for the exact book bytes."""
from pathlib import Path
import hashlib,json
import fitz
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'editorial/volume_finish'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(p):return json.loads(p.read_text())
def record(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main():
 pdf=ROOT/'output/Realization_Calculus.pdf';digest=sha(pdf);spec=load(ROOT/'book/build_spec.json')
 audit=load(ROOT/'book/final_pdf_audit.json');assert audit['status']=='PASS' and audit['pdf_sha256']==digest
 visual_files=[D/n for n in ('root_final_visual_review.json','i_iv_final_visual_review.json','v_viii_final_visual_review.json','ix_xii_final_visual_review.json','reference_section_review.json')]
 reviews=[]
 for p in visual_files:
  j=load(p);assert j['status']=='PASS',(p,j.get('status'));assert j['pdf_sha256']==digest,(p,'stale PDF');reviews.append(j)
 components=[load(p) for p in sorted((D/'component_reports').glob('*.json'))]
 assert len(components)==41 and all(j['status']=='PASS' for j in components)
 omissions=load(D/'omission_preservation_review.json');assert omissions['status']=='PASS'
 preflight=load(D/'native_region_preflight.json');assert preflight['status']=='PASS' and not preflight['errors']
 plan=load(D/'display_edits.json');assert not plan['unresolved'];assert sum(map(len,plan['omit_pages_1based'].values()))==64
 candidates=load(D/'final_text_review.json');assert candidates['status']=='PASS' and candidates['pdf_sha256']==digest
 evidence=[D/n for n in ('display_edits.json','native_region_preflight.json','omission_preservation_review.json','final_text_review.json','i_iv_bookmark_titles.json','v_viii_bookmark_clean_map.json','ix_xii_bookmark_titles.json','prose_layout_plan.json')]
 evidence += sorted((D/'component_reports').glob('*.json'))
 evidence += [ROOT/'book/atlas_book_routes_report.json',ROOT/'book/glossary_anchor_resolution.json',ROOT/'book/final_pdf_audit.json']
 editorial={'schema':'realization-calculus.book-editorial-audit/4','status':'PASS','pdf_sha256':digest,'pages':spec['expected_total_pages'],
 'scope':'Final-volume presentation, reference consolidation and bounded prose review. Prior grammar and punctuation reviews remain historical supporting evidence. This is not a new proof audit, Lean replay, numerical experiment or benchmark.',
 'changes':{'native_display_edits':len(plan['edits']),'affected_component_pages':preflight['pages'],'prepared_native_regions':preflight['regions'],'production_only_whole_pages_omitted':64,'reference_groups':spec['references']['groups'],'reference_pages':spec['references']['source_pages'],'glossary_terms':73},
 'mathematical_token_changes':[],
 'preservation':{'original_readers':'All41 exact originals remain separately preserved and attached. Final independent audit verifies their identities.',
 'native_content':'The41 component preservation reports check mathematical glyphs/fonts/positions, outside-region text, source annotations, native scientific images and vector objects. Reviewed source-only table rules are removed within explicit metadata regions. Reviewed native prose placements preserve characters, fonts, ligatures and relative geometry, and join one sentence continuation to its preceding line. Mixed-reference splits preserve preceding arguments and route citations to their final fragments.',
 'pixel_exception':'One reviewed indexed heatmap on V traditional40 has edge-only resampling differences after native PDF processing. Exact image bytes/dimensions/placement and vector geometry remain unchanged. Two III Lean33 code wrap arrows are documented nonmathematical layout marks.',
 'omissions':'Independent page-by-page review confirms no unique theorem, proof body or essential current hypothesis is removed by the64 production-page omissions.',
 'pdf_objects':'Standard lossless object deduplication is used for the final PDF. Full structural/source audit verifies the actual assembled output.'},
 'mathematical_scope':{'chapter_x':'Target-family and recovered-carrier witnesses retain separate existential and nonzero-input requirements.','conjecture_66':'Open; same-candidate H5 and stronger native/full-character requirements remain explicit.','chapter_xii':'Conditional on the stated supplied arithmetic, patching, support, compatible Hecke, classicality and representation inputs.'},
 'sources':[record(p) for p in evidence],'unresolved_editorial_findings':[]}
 (ROOT/'book/book_editorial_audit.json').write_text(json.dumps(editorial,indent=2,ensure_ascii=False)+'\n')
 final={'status':'PASS','pdf':'output/Realization_Calculus.pdf','pdf_sha256':digest,'pages':spec['expected_total_pages'],'review_scope':'Sampled manual visual QA of the actual final PDF, supported by all affected-page native preservation checks. Overview sheets support layout review; focused renders support changed prose, table, code and reference review. This is not all-page manual reading or a mathematical correctness audit.','review_records':[record(p) for p in visual_files],'reviews':reviews,'findings':[]}
 (ROOT/'book/final_visual_review.json').write_text(json.dumps(final,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'PASS','pdf_sha256':digest,'pages':spec['expected_total_pages'],'visual_reviews':len(reviews),'component_preservation_reports':len(components)},indent=2))
if __name__=='__main__':main()
