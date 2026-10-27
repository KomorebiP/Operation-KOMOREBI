#!/usr/bin/env python3
"""Freeze current guide evidence after manuscript and reading-locator review.

Historical source and execution records are retained separately. This does not
run Lean or convert any finite assertion into a universal theorem.
"""
from pathlib import Path
import hashlib,json,re,platform
import fitz,sympy
ROOT=Path(__file__).resolve().parent
R=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def spans(s):return re.findall(r'\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)',s,re.S)
def main():
 preserved=[]
 for name in ['pages.tex','extended_pages.tex']:
  current=spans((ROOT/'source'/name).read_text());original=spans((ROOT/'historical_assembly/source'/name).read_text());assert current==original
  preserved.append({'path':'source/'+name,'span_count':len(current),'ordered_exact_bytes_preserved':True,'sha256':hashlib.sha256('\n'.join(current).encode()).hexdigest()})
 sourcepins={}
 for path in ['source/models.py','source/generate_graphics.py','source/generate_extensions.py','checks/verify_examples.py','checks/verify_extended.py']:
  assert (ROOT/path).read_bytes()==(ROOT/'historical_assembly'/path).read_bytes();sourcepins[path]=sha(ROOT/path)
 plates=[]
 for directory in ['graphics','graphics_extended']:
  for p in sorted((ROOT/directory).glob('*.tex')):
   assert p.read_bytes()==(ROOT/'historical_assembly'/p.relative_to(ROOT)).read_bytes();plates.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
 assert len(plates)==38
 original=load(ROOT/'checks/runs/monograph-original/EXACT_CHECKS.json');extended=load(ROOT/'checks/runs/monograph-extended/EXTENDED_CHECKS.json');plate=load(ROOT/'checks/runs/monograph-plates/PLATE_REPLAY.json')
 assert original['status']=='PASS' and original['checks_passed']==180 and len(original['invalid_controls_rejected'])==9
 assert extended['status']=='PASS' and extended['positive_assertions']==373 and extended['negative_controls_rejected']==12
 assert plate['status']=='PASS' and plate['plate_count']==38 and plate['exact_regeneration']
 runs=[]
 for kind in ['original','extended','plates']:
  path=ROOT/'checks/runs'/('monograph-'+kind)/'manifest.json';m=load(path);assert m['run']['status']=='completed';runs.append({'path':str(path.relative_to(R)),'sha256':sha(path),'schema_version':m['schema_version'],'status':'completed'})
 qa=load(ROOT/'PDF_QA.json');cross=load(ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json');pdf=ROOT/'Paper_VII_Visual_Guide_Final.pdf'
 assert qa['status']=='PASS' and qa['pdf_sha256']==sha(pdf) and cross['visual_pdf_sha256']==sha(pdf)
 assert len(cross['pages'])==40
 report={'status':'PASS','edition':'Paper VII modern monograph,9October2026','physical_pdf_pages':len(fitz.open(pdf)),'worked_pages':40,'preliminary_pages':2,'vector_plates':38,'original_plates':26,'extended_plates':12,'all_source_formula_spans_preserved':preserved,'model_generator_check_programs_preserved':sourcepins,'plate_sources_preserved':plates,'current_computations':{'original':{'total_assertions':180,'positive_assertions':171,'negative_controls_rejected':9,'arithmetic':'SymPy1.14.0 exact finite/symbolic arithmetic and rational Taylor enclosures'},'extended':{'positive_assertions':373,'negative_controls_rejected':12,'arithmetic':'Python Fraction and exact Gaussian rational matrices'},'plates':{'byte_identical_regenerated_sources':38},'manifests':runs,'scope':'The two example suites have separate, overlapping coverage. Counts are not theorem coverage. Coordinate sampling is presentation data, not analytic proof.'},'traditional_reading_targets':sum(len(r['traditional_targets']) for r in cross['pages']),'source_crosswalk_sha256':sha(ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json'),'traditional_pdf_sha256':cross['traditional_pdf_sha256'],'traditional_map_sha256':cross['traditional_map_sha256'],'traditional_source_sha256':cross['traditional_source_sha256'],'pdf_sha256':sha(pdf),'guide_tex_sha256':sha(ROOT/'Paper_VII_Visual_Guide_Final.tex'),'pdf_qa_sha256':sha(ROOT/'PDF_QA.json'),'manual_visual_review_record_sha256':sha(ROOT/'VISUAL_REVIEW.txt'),'atlas_body_sha256':sha(ROOT.parent/'traditional/monograph_atlas.tex'),'atlas_definitions_sha256':sha(ROOT.parent/'traditional/atlas_definitions.tex'),'scope':{'inherited_finite_formal_items':19,'fresh_lean_kernel_execution':False,'continuum_physical_targets_open':5,'integrated_atlas_omits_final_traditional_page_locators':True},'scientific_run_failures':[],'environment_events':[{'action':'Final source locator refresh and build','event':'Executor transport disconnected before process creation.','resolution':'Retry succeeded. No scientific program or TeX process ran during the failed tool request.'}],'setup_corrections':['The atlas local \u005c\u005cAA adapter now renews the built-in letter command to the intended calligraphic algebra macro.','Historical absent-SymPy wording was replaced with the actual current replay scope.','The evidence reader uses the version 2 manifest run.status field.'],'changes':'Bundled-font book typography, cover and routes, final checked reading locators, and fresh-versus-inherited evidence prose. Mathematical spans, models, all38plate sources and check programs unchanged.','runtime':{'python':platform.python_version(),'sympy':sympy.__version__,'pymupdf':fitz.VersionBind}}
 report['edition']='Paper VII modern monograph, 9 October 2026';report['changes']=report['changes'].replace('all38plate','all 38 plate');report['current_computations']['original']['arithmetic']=report['current_computations']['original']['arithmetic'].replace('SymPy1.14.0','SymPy 1.14.0')
 (ROOT/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 (ROOT/'FINAL_READINESS.json').write_text(json.dumps({'status':'PASS','pdf_sha256':sha(pdf),'build_audit_sha256':sha(ROOT/'BUILD_AUDIT.json'),'physical_pages':report['physical_pdf_pages'],'worked_pages':40,'original_symbolic_suite_fresh':True,'lean_execution':'Inherited compiler evidence; no fresh Lean run.','open_continuum_physical_targets':5},indent=2)+'\n')
 (R/'verification/monograph_visual_report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: frozen guide PDF, crosswalk, preservation, and current bounded evidence.')
if __name__=='__main__':main()
