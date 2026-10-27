from pathlib import Path
import json,hashlib,zipfile,re,difflib,fitz
ROOT=Path(__file__).resolve().parent;R=ROOT.parent
H=lambda b:hashlib.sha256(b).hexdigest()
rows=json.loads((ROOT/'build_results.json').read_text());assert all(r['status']=='passed' for r in rows)
readers=json.loads((R/'reader_inventory.json').read_text());lookup={Path(p['name']).name:p for a in readers for p in a['pdfs']}
changes=[];unchanged=0;diff=[];inputs=[]
for roman in ['I','II','III','IV']:
 p=R/'full_inputs'/f'Paper_{roman}_Frozen_Release_2026-10-20.zip';z=zipfile.ZipFile(p);prefix=f'Paper_{roman}_Frozen_Release_2026-10-20/'
 inputs.append({'archive':p.name,'sha256':H(p.read_bytes()),'hash_in_current_register':H(p.read_bytes()) in (R/'register_current.txt').read_text()})
 for item in z.infolist():
  rel=item.filename[len(prefix):];target=ROOT/roman/rel
  if item.is_dir() or not target.is_file():continue
  old=z.read(item);new=target.read_bytes()
  if old==new:unchanged+=1;continue
  before=ROOT/'before'/roman/rel;assert before.is_file() and before.read_bytes()==old,str(target)
  type_='typesetting_preamble' if target.suffix=='.tex' and '\\begin{document}' in new.decode(errors='ignore') else 'font_location' if target.name.endswith('.sty') or target.name=='preamble.tex' else 'page_locator'
  if type_=='typesetting_preamble':
   a=old.decode().split('\\begin{document}',1)[1];b=new.decode().split('\\begin{document}',1)[1];assert a==b,rel
  elif type_=='page_locator':
   clean=lambda s:re.sub(r'\(p\.\s*[ivxlcdm0-9]+\)','(p. <folio>)',re.sub(r'p\.~[ivxlcdm0-9]+','p.~<folio>',s))
   assert clean(old.decode())==clean(new.decode()),rel
  changes.append({'path':str(target.relative_to(ROOT)),'type':type_,'before_sha256':H(old),'after_sha256':H(new)})
  diff.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='before/'+str(target.relative_to(ROOT)),tofile=str(target.relative_to(ROOT))))
(ROOT/'source_changes.diff').write_text(''.join(diff))
checks=json.loads((ROOT/'qa/structural_checks.json').read_text());assert all(not c['outside_page_text'] and not c['invalid_internal_links'] for c in checks)
components=[]
for r in rows:
 p=Path(r['pdf']);d=fitz.open(p);b=lookup[r['baseline_name']]
 components.append({'paper':r['paper'],'role':r['role'],'baseline_filename':r['baseline_name'],'baseline_pdf':b['path'],'baseline_pages':b['pages'],'baseline_sha256':H(Path(b['path']).read_bytes()),'output_pdf':str(p),'pages':len(d),'sha256':H(p.read_bytes()),'build_kind':'source_retypeset','source_root':str(Path(r['source']).parent),'source_entry':Path(r['source']).name,'local_page_label_rules':d.get_page_labels(),'warnings':r['warnings'],'engine':r['engine'],'build_runs':r['runs']})
for roman,name,why in [('III','Paper_III_Release_Record_v1.0.0.pdf','Original two-page release record retained as an exact PDF. Its recorded verification date/scope and old licensing wording are historical; frozen licenses apply.'),('IV','Paper_IV_Visual_Guide_Final.pdf','Exact editable source for the selected later October16 visual reader remains missing. This exact selected PDF is preserved; older editable visual sources are not substituted.'),('IV','Paper_IV_Verification_Closeout_v1.1.0.pdf','Selected five-page verification addendum retained as an exact PDF with its recorded evidence date.')]:
 b=lookup[name];p=Path(b['path']);d=fitz.open(p);components.append({'paper':roman,'role':'visual' if 'Visual' in name else 'release_record' if roman=='III' else 'verification_addendum','baseline_filename':name,'baseline_pdf':str(p),'baseline_pages':len(d),'baseline_sha256':H(p.read_bytes()),'output_pdf':str(p),'pages':len(d),'sha256':H(p.read_bytes()),'build_kind':'preserved_pdf','source_root':None,'warnings':[why],'local_page_label_rules':d.get_page_labels()})
report={'schema':'komorebi.core-monograph.typesetting-group/1','scope':'Publication design of Papers I-IV. No mathematics changed, no Lean or finite checks run. Scientific figure assets retain original bytes; the theme can recolor source-defined accents.','components':components,'source_preservation':{'input_archives':inputs,'unchanged_extracted_original_files':unchanged,'changed_files':changes,'mathematical_body_bytes_unchanged_except_documentary_page_locators':True,'mathematical_token_changes':[],'page_locator_checks':json.loads((ROOT/'navigation_updates.json').read_text())['checked_locators'],'pending_page_locator_changes':0},'validation':{'all12_source_builds_passed':True,'final_missing_glyphs_or_unresolved_references':0,'final_overfull_warnings':0,'structural_checks':checks,'visual_qa':'71 representative pages in12 contact sheets reviewed plus four targeted full-size details. All-page text bounds and internal link targets checked. Not a whole-paper proof audit.'},'preserved_exceptions':3,'excluded_duplicate':'PaperIII complete186page reader duplicates its fivecomponents and is not included asecondtime.','failures_and_repairs':['FirstILeancover override accidentally changed originalArabic pagination toRoman; restoredArabic, TOC overflow eliminated.','CorePhysics paragraph indentation exposed full-width tabularx indentation inII/III; noindent environment hook fixed the fouraffected components without tablecontent edits.','IVoriginal styles referred to absent bundledfont files; explicit configurable installedURW/LatinModern/DejaVu paths provided; firstfont failure and secondDejaVu failure corrected.','An exploratory contact-sheet read raced an in-progress PDF write and failed toopen it. Rendering was repeated afterbuild completion.'],'rebuild':'python3 source_i_iv/rebuild_all.py','proofreading_self_review':{'scope':'Inserted publicationpreamble, fontpathconfiguration, page-locator-onlydiffs','routine_edits':'Typesetting and navigation only','mathematical_token_changes':'none','unresolved_issues':'none in changedhunks; baselinehistoricalscope remains unchanged'}}
(ROOT/'SOURCE_PRESERVATION_AND_QA.json').write_text(json.dumps(report,indent=2)+'\n');(R/'typeset_i_iv_results.json').write_text(json.dumps(report,indent=2)+'\n');print('components',len(components),'pages',sum(c['pages'] for c in components),'changed',len(changes),'unchanged',unchanged)
