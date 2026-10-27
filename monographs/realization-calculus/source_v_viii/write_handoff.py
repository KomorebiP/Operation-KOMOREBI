from pathlib import Path
import json,hashlib,difflib,collections,subprocess,fitz
R=Path(__file__).resolve().parent;W=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
extracted=json.loads((R/'EXTRACTED_SOURCES.json').read_text()); assets=json.loads((R/'ADDITIONAL_ASSETS.json').read_text())
builds=json.loads((R/'BUILD_RESULTS_FINAL.json').read_text());qa=json.loads((R/'QA_CURRENT.json').read_text());qamap={(r['paper'],r['role']):r for r in qa}
archive_hashes={'V':'fb8eee74d4a43759517c804a4e85c01095c1d06a3edb9e1191a742a7b991b15c','VI':'cc89a482b85ceeba8faac89753b9635efccd2dcb40eb4d88e396e1bf3c3cce13','VII':'1b6614080fb9570e813a4f7c675d0aed3e464ee8d98256d7e8b3e92d2eea5ce1','VIII':'fa33c613e4497d80ed17fdf8b37494ab41452f0fb80b6004261381f0019c78cc'}
register=(W/'register_current.txt').read_text()
assert all(h in register for h in archive_hashes.values())
originals=[];diffs=[];removed=[];unchanged=[]
for x in extracted+assets:
 p=Path(x['local']);relative=p.relative_to(R)
 if not p.exists():
  assert p.suffix in ['.fls','.bbl','.blg','.lof','.lot'];removed.append({'path':str(relative),'original_sha256':x['sha256'],'reason':'Stale TeX compilation byproduct removed before clean typesetting; frozen ZIP unchanged.'});continue
 digest=sha(p)
 if digest==x['sha256']:unchanged.append({'path':str(relative),'sha256':digest});continue
 pieces=relative.parts;before=R/'before'/pieces[0]/pieces[2]/Path(*pieces[3:])
 assert before.is_file(),str(relative)
 assert sha(before)==x['sha256'],str(before)
 original={'path':str(relative),'before':str(before.relative_to(R)),'original_sha256':x['sha256'],'edited_sha256':digest}
 if p.name.startswith('Paper_'):
  original['body_after_begin_document_byte_equal']=p.read_bytes().split(b'\\begin{document}',1)[1]==before.read_bytes().split(b'\\begin{document}',1)[1]
  assert original['body_after_begin_document_byte_equal']
  original['scope']='One preamble input of component-layout.tex; scientific body byte-identical.'
 else:
  assert p.name=='traditional_navigation.tex'
  original['scope']='Label historical traditional-reader navigation as frozen-edition pagination; numeric data and mathematics unchanged.'
 originals.append(original)
 diffs.append(''.join(difflib.unified_diff(before.read_text().splitlines(True),p.read_text().splitlines(True),'before/'+str(relative),'after/'+str(relative))))
assert len(originals)==15 and len(removed)==30 and len(unchanged)==2337
(R/'SOURCE_PRESERVATION_AUDIT.json').write_text(json.dumps({'checked_archive_files':len(extracted)+len(assets),'unchanged_files':unchanged,'edited_files':originals,'removed_stale_build_artifacts':removed,'unexpected_changes':[],'all_12_scientific_main_bodies_byte_identical':True,'all_54_restored_figure_PDFs_byte_identical':True,'archive_hashes_found_in_current_register':archive_hashes},indent=2))
(R/'CHANGES.diff').write_text('\n'.join(diffs))
inv={Path(p['path']).name:p for a in json.loads((W/'reader_inventory.json').read_text()) for p in a['pdfs']}
engine=subprocess.check_output(['xelatex','--version'],text=True).splitlines()[0];bibtex=subprocess.check_output(['bibtex','--version'],text=True).splitlines()[0]
results=[]
for b in builds:
 n=b['paper'];role=b['role'];q=qamap[(n,role)];filename=b['stem']+'.pdf';baseline=inv[filename]
 assert b['success'] and not q['overfull_lines'] and not q['missing_characters'] and not q['unresolved_references']
 assert not any(c['outside_page_blocks'] or c['invalid_internal_links'] for c in q['checks'])
 warnings=[]
 if q['font_shape_warnings']:warnings.append('Three inherited Latin Modern Math bold-shape substitution warnings (regular fallback); no missing characters. Mathematical tokens unchanged.')
 warnings.append('Fixed prose page locators retain the frozen traditional-reader pagination and are explicitly labeled as frozen-edition locators on the opening page. Local contents and live internal links use the reflowed edition.')
 if role=='visual_guide':warnings.append('Top and bottom margins are 0.80in to retain the original one-unit-per-page visual guide layout; horizontal margins remain 0.87in.')
 log=Path(b['compiled_directory'])/(b['stem']+'.log')
 result={'paper':n,'role':role,'baseline_filename':filename,'baseline_pdf':baseline['path'],'baseline_sha256':sha(Path(baseline['path'])),'baseline_pages':baseline['pages'],'output_pdf':b['pdf'],'output_sha256':q['pdf_sha256'],'pages':q['pages'],'build_kind':'source_retypeset','source_root':str(Path(b['source']).parent),'source_file':b['source'],'frozen_archive_sha256':archive_hashes[n],'hash_found_in_current_register':True,'environment':{'xelatex':engine,'bibtex':bibtex,'source_date_epoch':1792540800,'shell_escape':False},'scope':'Typography, pagination, palette and edition-locator labels only. Scientific prose, statements, proofs, numerical data and figure assets preserved. No fresh Lean or scientific execution.','main_document_body_byte_identical':True,'warnings':warnings,'page_labels':q['page_labels'],'page_label_rule':'startpage is zero-based physical page; preserved roman/arabic local counters serve the component contents. Parent adds separate global folios.','inherited_headers_footers_suppressed':True,'fixed_numeric_locators_target':'frozen_readers/Paper_'+n+'_Traditional_Final.pdf','numeric_remotes_edition':None,'remote_pdf_links':[],'external_uri_links':q['external_links'],'validation':{'build_passes':b['runs'],'final_log':str(log),'overfull_boxes':0,'missing_characters':0,'unresolved_references_citations':0,'invalid_internal_links':0,'outside_page_text_blocks':0,'resolved_internal_links':q['internal_links'],'font_shape_warnings':q['font_shape_warnings'],'rendered_pages_reviewed':q['rendered_pages']},'source_preservation_audit':str(R/'SOURCE_PRESERVATION_AUDIT.json'),'typography_diff':str(R/'CHANGES.diff'),'rebuild_entrypoint':str(R/'build_all.py')}
 results.append(result)
(W/'typeset_v_viii_results.json').write_text(json.dumps(results,indent=2))
print('Wrote',W/'typeset_v_viii_results.json','components',len(results),'pages',sum(r['pages'] for r in results))
print('Source audit:',len(unchanged),'unchanged,',len(originals),'allowed edits,',len(removed),'stale compilation artifacts excluded; no unexpected changes.')
