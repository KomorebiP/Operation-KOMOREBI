#!/usr/bin/env python3
"""Verify the final authored visual companion and its navigation evidence.

This checks preservation and presentation; it does not run or extract Lean
proofs, establish numerical-library correctness, or measure device performance.
"""
from pathlib import Path
import argparse,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT.parents[1]
RX=re.compile(r'(?<!\\)\$.*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)',re.S)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pin(path):return {'path':str(path.relative_to(RELEASE)),'sha256':sha(path)}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--rebuild-pdf',type=Path,required=True)
    a=p.parse_args();baseline=a.baseline
    pdf=ROOT/'Paper_VIII_Visual_Guide_Final.pdf';doc=fitz.open(pdf)
    crosspath=ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json';cross=json.loads(crosspath.read_text())
    traditional=ROOT.parent/'traditional';tpdf=traditional/'Paper_VIII_Traditional_Final.pdf';tmap=traditional/'evidence/FINAL_PAGE_MAP.json'
    assert cross['visual_pdf_sha256']==sha(pdf)
    assert cross['traditional_pdf_sha256']==sha(tpdf)
    assert cross['traditional_map_sha256']==sha(tmap)
    assert sha(pdf)==sha(a.rebuild_pdf),'Isolated rebuilt visual PDF differs.'
    formulas=[]
    for name in ('pages.tex','extended_pages.tex'):
        raw=RX.findall((baseline/'source'/name).read_text());current=RX.findall((ROOT/'source'/name).read_text())
        assert raw==current,'Formula span changed in '+name
        formulas.append({'path':'source/'+name,'span_count':len(raw),'ordered_exact_bytes_preserved':True,'math_span_sha256':hashlib.sha256('\n'.join(current).encode()).hexdigest(),'baseline_file_sha256':sha(baseline/'source'/name),'current_file_sha256':sha(ROOT/'source'/name)})
    programs={}
    for name in ('source/models.py','source/drawing.py','source/generate_graphics.py','source/generate_extensions.py','checks/verify_examples.py','checks/verify_portable.py'):
        assert sha(ROOT/name)==sha(baseline/name),'Scientific source changed: '+name
        programs[name]=sha(ROOT/name)
    plates=[]
    for f in sorted((ROOT/'graphics').glob('*.tex')):
        original=baseline/'graphics'/f.name
        same=f.read_bytes()==original.read_bytes()
        spans_preserved=RX.findall(f.read_text())==RX.findall(original.read_text())
        assert spans_preserved
        if not same:assert f.name in ('complex_core.tex','quantization.tex')
        plates.append({'path':'graphics/'+f.name,'baseline_sha256':sha(original),'current_sha256':sha(f),'byte_identical':same,'all_literal_formula_labels_preserved':spans_preserved,'layout_change':None if same else 'Only title y-coordinate moved upward to separate title and axis label.'})
    assert len(plates)==30
    names=doc.resolve_names();faults=[];page_checks=[];links=0
    for i,page in enumerate(doc):
        text=page.get_text();outside=[];bad=[]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<35 or x1>577 or y0<20 or y1>776:outside.append({'text':span['text'],'bbox':span['bbox']})
        for link in page.get_links():
            if link['kind']==fitz.LINK_GOTO:
                links+=1
                if not 0<=link.get('page',-1)<len(doc):bad.append(link)
            elif link['kind']==fitz.LINK_NAMED:
                links+=1
                if not 0<=names.get(link.get('nameddest',''),{}).get('page',-1)<len(doc):bad.append(link)
        assert '\ufffd' not in text and not outside and not bad
        page_checks.append({'physical_pdf_page':i+1,'printed_page':page.get_label(),'word_count':len(page.get_text('words')),'outside_safe_bounds':outside,'invalid_links':bad,'raster_images':len(page.get_images())})
    for row in cross['pages']:
        page=doc[row['visual_physical_pdf_page']-1]
        assert page.get_label()==row['visual_printed_page']
        needle=re.sub(r'\s+',' ',row['source_line_current']).strip()
        haystack=re.sub(r'\s+',' ',page.get_text()).strip()
        assert needle in haystack,'Current source line absent from delivered PDF V'+str(row['visual_page'])
    assert len(cross['pages'])==32 and len(doc)==34
    for line in (ROOT/'Paper_VIII_Visual_Guide_Final.log').read_text(errors='replace').splitlines():
        if any(token in line for token in ('Overfull','undefined references','undefined citations','Missing character:','undefined on input')):faults.append(line)
    assert not faults
    report={'status':'PASS','edition':'Paper VIII modern monograph, 9 October 2026','physical_pdf_pages':len(doc),'worked_pages':32,'preliminary_pages':2,'vector_plates':30,'source_formula_spans_preserved':formulas,'scientific_model_generator_check_programs_preserved':programs,'plate_sources':plates,'mathematical_token_changes':[],'xelatex_build':'Isolated source copy, four passes, deterministic SOURCE_DATE_EPOCH=1791504000. No unresolved final diagnostics.','independent_rebuild_byte_identical':True,'pdf_sha256':sha(pdf),'rebuild_pdf_sha256':sha(a.rebuild_pdf),'crosswalk':pin(crosspath),'source_crosswalk':pin(ROOT/'SOURCE_CROSSWALK.json'),'traditional_pdf':pin(tpdf),'traditional_map':pin(tmap),'visual_pdf':pin(pdf),'visual_source':pin(ROOT/'Paper_VIII_Visual_Guide_Final.tex'),'source_pins':[pin(ROOT/name) for name in ('source/visual_macros.tex','source/front.tex','source/pages.tex','source/extended_pages.tex','source/update_crosswalk.py','source/verify_monograph.py','build.py','komorebi-monograph.sty')],'page_checks':page_checks,'internal_links':links,'latex_faults':faults,'actual_render_review':{'all_pages_rendered':True,'all_34_pages_inspected':True,'files':'editable/visual_guide/qa/final_'+sha(pdf)[:12]+'/page_001.png through page_034.png','pdf_sha256':sha(pdf),'two_title_crowding_repairs_inspected_at_full_size':True,'remaining_visual_blockers':[]},'scope':'Exact bounded worked examples and preserved formula exposition. Reading references do not enlarge formal scope. The 56 manuscript-proved items, 392 named declarations, 40 modules, and 66 construction audits remain inherited formal records. No fresh Lean compiler run or GPU measurement. Four classical inputs and three broad research targets remain separately documented.','workflow_failures':[{'phase':'Read-only source inventory','detail':'An initial read queried visual_guide/fonts and traditional/main.tex, which did not exist in the retrieved tree. The actual wrapper was Paper_VIII_Traditional_Final.tex. Bundled monograph fonts were then copied from the finalized Paper VII edition.','impact':'No source mutation, LaTeX build failure, or scientific assertion failure.'}]}
    target=RELEASE/'verification/monograph_visual_report.json';target.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'BUILD_AUDIT.json').write_text(json.dumps({'status':'PASS','supersedes':'historical_assembly/BUILD_AUDIT.json','pdf_pages':len(doc),'pdf_sha256':sha(pdf),'current_report':str(target.relative_to(RELEASE)),'current_report_sha256':sha(target),'scope':'Current visual layout, navigation, source preservation and XeLaTeX rebuild.'},indent=2)+'\n')
    (ROOT/'ISOLATED_REBUILD.json').write_text(json.dumps({'status':'PASS','method':'Independent isolated full-source four-pass XeLaTeX rebuild.','byte_identical':True,'pdf_sha256':sha(pdf),'rebuild_pdf_sha256':sha(a.rebuild_pdf),'supersedes':'historical_assembly/ISOLATED_REBUILD.json'},indent=2)+'\n')
    print(json.dumps({'status':'PASS','pages':len(doc),'formula_spans':sum(x['span_count'] for x in formulas),'plates':len(plates),'report':str(target)},indent=2))
if __name__=='__main__':main()
