"""Independent guide-byte, source-range and navigation inspection.

No Lean invocation, no mathematical theorem-verification inference from hashes.
"""
from pathlib import Path
import collections, csv, hashlib, json, re, zipfile
import fitz

ROOT=Path(__file__).resolve().parents[2]
B=ROOT/'source/consolidated/PRSC_IX_Consolidated_Manuscript'
D=ROOT/'lean_guide'
V=ROOT/'visual_guide'
OUT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
cache={}
def raw(s):
    if s not in cache:
        if '!' in s or '::' in s:
            z,n=re.split('!|::',s,maxsplit=1)
            with zipfile.ZipFile(B/z) as f:cache[s]=f.read(n)
        else:cache[s]=(B/s).read_bytes()
    return cache[s]
inventory=D/'audit/EXCERPTS.json'
records=json.loads(inventory.read_text())
uses=collections.Counter()
for p in (D/'chapters').glob('*.tex'):
    uses.update(re.findall(r'\\excerpt\{[^}]*\}\{([^}]+)\}',p.read_text()))
checks=[];ranges=set();fallback=collections.Counter()
for r in records:
    data=raw(r['source'])
    excerpt=''.join(data.decode().splitlines(keepends=True)[r['start_line']-1:r['end_line']]).encode()
    render=(D/f'excerpts/{r["id"]}.render.txt').read_text()
    fallback.update(re.findall(r'\\CodeSymbol\{([0-9A-F]+)\}',render))
    decoded=re.sub(r'\\CodeSymbol\{([0-9A-F]+)\}',lambda m:chr(int(m[1],16)),render)
    decoded=re.sub(r'\\CodeChar\{(\d+)\}',lambda m:chr(int(m[1])),decoded)
    item=dict(id=r['id'],source_sha256=sha(data),source_matches=sha(data)==r['source_sha256'],excerpt_matches=excerpt==(D/f'excerpts/{r["id"]}.lean.txt').read_bytes(),excerpt_hash_matches=sha(excerpt)==r['excerpt_sha256'],render_decodes_to_exact_source=decoded.encode()==excerpt,source=r['source'],lines=[r['start_line'],r['end_line']],line_count=r['line_count'],instructional_uses=uses[r['id']])
    assert item['source_matches'] and item['excerpt_matches'] and item['excerpt_hash_matches'] and item['render_decodes_to_exact_source'] and item['instructional_uses']==1,item
    assert r['line_count']==r['end_line']-r['start_line']+1
    ranges.update((r['source'],n) for n in range(r['start_line'],r['end_line']+1))
    checks.append(item)
assert set(uses)=={r['id'] for r in records}
result={'fresh_lean_run':False,'excerpt_inventory_sha256':sha(inventory.read_bytes()),'excerpt_check':checks,'source_files_checked':len(set(r['source'] for r in records)),'excerpt_count':len(records),'exact_raw_lines':sum(r['line_count'] for r in records),'distinct_source_line_addresses':len(ranges),'metadata_ambient_variable_line_entries':sum(len(r['ambient_variable_lines']) for r in records),'ambient_context_note':'These are recorded earlier variable lines; they are not extra raw excerpt lines or claims of a minimal elaborated dependency set. Guide contracts state the hypotheses.','render_glyph_fallback_occurrences':dict(fallback),'all_excerpt_checks_pass':True,'scope':'Independent exact source-byte, extraction-range, render-escape decoding and once-only instructional inclusion checks; no typechecking or universal mathematical theorem follows from hash identity.'}
(OUT/'FINAL_SOURCE_AND_EXCERPT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')

old=ROOT/'source/complete/Paper_IX_Complete_Consolidated_With_Visual_Appendix/visual_appendix'
def spans(s):return collections.Counter(re.findall(r'\$[^$]*\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)',s))
a=spans((old/'source/pages.tex').read_text());b=spans((V/'source/pages.tex').read_text())
plates=[dict(name=p.name,same_bytes=p.read_bytes()==(V/'graphics'/p.name).read_bytes()) for p in sorted((old/'graphics').glob('*.tex'))]
assert not a-b
assert all(p['same_bytes'] for p in plates)
source_preservation={'original_math_spans':sum(a.values()),'original_math_spans_missing':sum((a-b).values()),'original_plates':plates,'scope':'Exact source preservation, not theorem correctness.'}
(OUT/'FINAL_VISUAL_PRESERVATION_CHECKS.json').write_text(json.dumps(source_preservation,indent=2)+'\n')

v=json.loads((B/'polynomial_regularity/verification/polynomial_regularity_verification.json').read_text())
module_records=v['source_inventory']['modules']
names={r['module'] for r in module_records}
dependencies={}
for r in module_records:
    data=(B/'polynomial_regularity'/r['source']).read_bytes()
    assert sha(data)==r['sha256']
    imports=re.findall(r'^(?:public\s+)?import\s+([^\n]+)',data.decode(),re.M)
    dependencies[r['module']]=[s for s in imports if not s.startswith('Mathlib.')]
    assert set(dependencies[r['module']])<=names
table=(D/'generated/dependencies.tex').read_text()
display={name:re.findall(r'\\code\{([^}]+)\}',imports) for name,imports in re.findall(r'\\code\{([^}]+)\}\s*&\s*([^\n]+)',table)}
assert display==dependencies
remaining=set(names);order=[]
while remaining:
    ready=sorted(n for n in remaining if not set(dependencies[n])&remaining)
    assert ready,'Cycle in direct-import graph'
    order.extend(ready);remaining.difference_update(ready)
(OUT/'FINAL_DEPENDENCY_MAP_CHECKS.json').write_text(json.dumps({'proof_modules':len(names),'direct_imports_match_raw_sources':True,'acyclic':True,'topological_order':order,'dependencies':dependencies,'scope':'Direct raw project imports only; imported Mathlib theorem correctness is not reverified by this graph check.'},indent=2)+'\n')

def aux_pages(path):
    return {label:int(page) for label,number,page in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{(\d+)\}',path.read_text()) if not label.endswith('@cref')}
guide_aux=aux_pages(D/'Paper_IX_Lean_Guide_Final.aux')
crosswalk=json.loads((D/'audit/CROSSWALK.json').read_text())
pd=fitz.open(D/'Paper_IX_Lean_Guide_Final.pdf')
for r in crosswalk:
    n=guide_aux[r['guide_section_label']]
    assert r['guide_printed_page']==n and r['guide_physical_page']==n+1,r
    assert 0<n<len(pd)
nav={'lean_pdf_sha256':sha((D/'Paper_IX_Lean_Guide_Final.pdf').read_bytes()),'lean_physical_pages':len(pd),'lean_printed_pages':len(pd)-1,'lean_crosswalk_rows':len(crosswalk),'all_lean_crosswalk_pages_match_aux':True,'lean_crosswalk_note':'Teaching-chapter start pages, not exact theorem-local page references. Printed pages lag physical PDF pages by one title page.'}
pd.close()

traditional=ROOT/'traditional/Paper_IX_Traditional_Final.pdf'
tp=aux_pages(ROOT/'traditional/build/Paper_IX_Traditional_Final.aux')
labels=json.loads((V/'source/crosswalk_targets.json').read_text())
vf=V/'Paper_IX_Visual_Guide_Final.pdf'
vd=fitz.open(vf);count=0
for n,page in enumerate(vd,1):
    expected=[tp[s]-1 for s in labels[str(n)]]
    links=[x for x in page.get_links() if x['kind']==fitz.LINK_GOTOR]
    assert [x['page'] for x in links]==expected,(n,links,expected)
    assert all(x['file']=='Paper_IX_Traditional_Final.pdf' for x in links)
    count+=len(links)
nav.update({'visual_pdf_sha256':sha(vf.read_bytes()),'visual_physical_pages':len(vd),'traditional_pdf_sha256':sha(traditional.read_bytes()),'traditional_aux_sha256':sha((ROOT/'traditional/build/Paper_IX_Traditional_Final.aux').read_bytes()),'visual_remote_page_links':count,'visual_unique_target_labels':len({s for rr in labels.values() for s in rr}),'all_visual_GoToR_pages_match_traditional_aux':True,'visual_note':'GoToR pages are zero-based physical target pages; printed traditional pages currently coincide with physical pages.'})
vd.close()
(OUT/'FINAL_NAVIGATION_CHECKS.json').write_text(json.dumps(nav,indent=2)+'\n')
print({'excerpts':result['excerpt_count'],'raw_lines':result['exact_raw_lines'],'source_files':result['source_files_checked'],'render_decoding':'PASS','original_visual_spans':sum(a.values()),'original_plates':len(plates),'navigation':nav})
