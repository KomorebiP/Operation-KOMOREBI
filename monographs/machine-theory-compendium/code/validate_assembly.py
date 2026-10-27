#!/usr/bin/env python3
"""Check assembly preservation and navigation, not inherited mathematical claims."""
from __future__ import annotations
import hashlib,json,re,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    t=time.perf_counter();maps=json.loads((ROOT/'ASSEMBLY_MAP.json').read_text());cat=json.loads((ROOT/'SOURCE_CATALOG.json').read_text());result={'scope':'Assembly and new editorial checks only. No inherited research suite, Lean project or statistical experiment was rerun.','errors':[],'source_checks':[],'readers':[],'pixel_comparisons':[]}
    for s in cat['source_documents']:
        ok=sha(ROOT/s['path'])==s['sha256'];result['source_checks'].append({'code':s['code'],'original_sha256_unchanged':ok})
        if not ok:result['errors'].append('Source hash mismatch '+s['code'])
    text_pages=0;geometry_pages=0;new_bounds=[];links_checked=0
    for m in maps:
        with fitz.open(ROOT/m['file']) as d:
            if len(d)!=m['pages']:result['errors'].append('Page count '+m['file'])
            bookmark_errors=[];link_errors=[];counts={'goto':0,'remote':0,'uri':0,'other':0}
            for level,title,page in d.get_toc():
                if not 1<=page<=len(d):bookmark_errors.append([title,page])
            for i,page in enumerate(d):
                for link in page.get_links():
                    kind=link['kind']
                    if kind==fitz.LINK_GOTO:
                        counts['goto']+=1;links_checked+=1
                        if not 0<=link.get('page',-1)<len(d):link_errors.append({'page':i+1,'link':str(link)})
                    elif kind==fitz.LINK_GOTOR:
                        counts['remote']+=1
                        # Our generated cross-volume links have one declared relative filename.
                        if link.get('file')=='Komorebi_Machine_Theory_Compendium_v1.0.0.pdf':
                            links_checked+=1
                            if not 0<=link.get('page',-1)<maps[0]['pages']:link_errors.append({'page':i+1,'link':str(link)})
                    elif kind==fitz.LINK_URI:counts['uri']+=1
                    else:counts['other']+=1
            records=[]
            for s in m['documents']:
                with fitz.open(ROOT/s['path']) as src:
                    off=s['source_start']-1;bad_text=[];bad_geometry=[]
                    for j,p in enumerate(src):
                        q=d[off+j];text_pages+=1;geometry_pages+=1
                        if p.get_text()!=q.get_text():bad_text.append(j+1)
                        if tuple(p.rect)!=tuple(q.rect) or p.rotation!=q.rotation:bad_geometry.append(j+1)
                    records.append({'code':s['code'],'pages':len(src),'text_equal':not bad_text,'geometry_equal':not bad_geometry,'text_mismatches':bad_text,'geometry_mismatches':bad_geometry})
                    if bad_text or bad_geometry:result['errors'].append('Page preservation '+m['file']+' '+s['code'])
                    if m is maps[0]:
                        for j in sorted({0,len(src)//2,len(src)-1}):
                            a=src[j].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False);b=d[off+j].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
                            eq=a.width==b.width and a.height==b.height and a.samples==b.samples
                            result['pixel_comparisons'].append({'code':s['code'],'source_page':j+1,'compiled_page':off+j+1,'pixels_equal':eq})
                            if not eq:result['errors'].append('Pixel mismatch '+s['code']+':'+str(j+1))
            if m is maps[0]:
                for i in m['new_page_indices']:
                    page=d[i];outside=[]
                    for word in page.get_text('words'):
                        if not fitz.Rect(-.5,-.5,page.rect.width+.5,page.rect.height+.5).contains(fitz.Rect(word[:4])):outside.append(word[4])
                    if outside:new_bounds.append({'page':i+1,'outside_words':outside})
            if bookmark_errors or link_errors:result['errors'].append('Navigation error '+m['file'])
            result['readers'].append({'file':m['file'],'pages':len(d),'bookmarks':len(d.get_toc()),'bookmark_errors':bookmark_errors,'link_counts':counts,'invalid_internal_links':link_errors,'source_preservation':records})
    with fitz.open(ROOT/'editorial/connected_synthesis.pdf') as d:
        texts=[p.get_text() for p in d];markers=[i+1 for i,s in enumerate(texts) if '\ufffd' in s or '??' in s]
        result['synthesis']={'pages':len(d),'unresolved_or_replacement_markers':markers,'all_new_text_within_page_bounds':not new_bounds}
        if markers:result['errors'].append('Synthesis unresolved text')
    log=(ROOT/'editorial/connected_synthesis.log')
    diagnostics=[]
    if log.exists():
        diagnostics=[x for x in log.read_text(errors='replace').splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character',x)]
    result['synthesis']['latex_diagnostics']=diagnostics
    if diagnostics:result['errors'].append('Synthesis LaTeX diagnostics')
    if new_bounds:result['errors'].append('New-page bounds')
    result.update(unique_original_pages=cat['source_pages'],source_page_text_checks_including_split_readers=text_pages,source_page_geometry_checks_including_split_readers=geometry_pages,internal_destinations_checked=links_checked,new_page_bounds_issues=new_bounds,new_pages_in_master=len(maps[0]['new_page_indices']),runtime_seconds=time.perf_counter()-t,status='PASS' if not result['errors'] else 'FAIL')
    (ROOT/'validation/assembly_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_checks','readers','pixel_comparisons']},indent=2))
    if result['errors']:raise SystemExit(1)
if __name__=='__main__':main()
