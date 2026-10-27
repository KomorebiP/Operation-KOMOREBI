from pathlib import Path
import hashlib,json
import fitz

base=Path('/workspace/scratch/ea498747acd5')
mono=base/'monograph_v018'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent_body=(base/'monograph_v017/source/FOUNDATIONS.md').read_text()
body=(mono/'source/FOUNDATIONS.md').read_text()
old='The formal companion records 58 complete mappings, one partial mapping, and 28 propositions without a formalization.'
new='The formal companion records 66 complete mappings, one partial mapping, and 20 propositions without a formalization.'
assert parent_body.count(old)==body.count(new)==1
assert body.replace(new,old,1)==parent_body
status=json.loads((mono/'source/FORMAL_STATUS.json').read_text())
validation=json.loads((mono/'build/MONOGRAPH_VALIDATION.json').read_text())
assert validation['page_count']==174 and validation['output_bookmarks']==validation['original_bookmarks']==128
assert validation['out_of_page_text']==[] and validation['output_repack_diagnostics']==''
assert validation['output_sha256']==sha(mono/'build/Realization_Calculus_Large_Signal_Model.pdf')
groups=status['guide_entries'];ids=[n for g in groups for n in g['ids']]
assert len(ids)==len(set(ids))==28 and set(ids)=={e['id']for e in status['new_entries']}
text_changed=[];pixel_changed=[]
with fitz.open(base/'monograph_v017/build/Realization_Calculus_Large_Signal_Model.pdf') as p,fitz.open(mono/'build/Realization_Calculus_Large_Signal_Model.pdf')as q:
 assert len(p)==len(q)==174 and p.get_toc()==q.get_toc()
 for i in range(174):
  if p[i].get_text()!=q[i].get_text():text_changed.append(i+1)
  if p[i].get_pixmap(alpha=False).samples!=q[i].get_pixmap(alpha=False).samples:pixel_changed.append(i+1)
assert text_changed==pixel_changed==[7,145,146,147,153,167],(text_changed,pixel_changed)
report={'manuscript_scope_review':'PASS','accepted_execution':status['execution_status'],'body_sha256':sha(mono/'source/FOUNDATIONS.md'),'predecessor_body_sha256':sha(base/'monograph_v017/source/FOUNDATIONS.md'),'body_identity':'Exact predecessor corrected mathematical body after replacing the one current formal-count sentence with its predecessor counts. No mathematical token or figure changes.','formal_status_sha256':sha(mono/'source/FORMAL_STATUS.json'),'pdf_sha256':validation['output_sha256'],'original_pdf_sha256':validation['source_sha256'],'page_count':174,'bookmarks_exact':128,'pages_changed_from_predecessor':text_changed,'other_pages_text_and_pixel_identical':168,'guide_groups':len(groups),'guide_unique_ids':28,'guide_font_pt':10.4,'scope_checks':['Exact current complete/partial/unfinished IDs and inventories; kernel execution distinguished from internal review and archive integrity','P50 exact mass and initial coverage; predictive base norm not equated with ambient trace norm','P54 correct supplied dimension/degree and covered invertible core','P56 bin-measurable policies and positive-cell density-weighted posterior','P58 sharper Lh/3 restricted to equal uniform intervals','P59 common cone/reference/history policy; no stronger adjacent conditional-TV result claimed','P61 domain and initial checks retained; no degree discovery or empirical coverage claim','P62 orientation; P63 conditional proposal plus full-family verification','P64 true-degree-free positive approximation; P65 bias/coefficient/correction budgets separate','P66 remains partial in this checked checkpoint, notwithstanding later unaccepted development'],'visual_review':'Coordinator viewed all six changed pages at 1.6x: preface, all newly affected register pages, inventory/table/execution, and grouped scope notes. No clipping, overlap or navigation defect found. Final execution and guide pages must be re-rendered after their final text update.','publication_boundary':'Original full XeLaTeX source unavailable. Complete original PDF, corrected editable body, reproducible PDF update script and bundled fonts/licenses retained. No full XeLaTeX rebuild claimed.'}
(mono/'review/MANUSCRIPT_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'scope':'PASS','execution':status['execution_status'],'changed_pages':text_changed,'other_pages_identical':168,'body_sha256':report['body_sha256']}))
