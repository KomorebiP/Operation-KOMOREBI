#!/usr/bin/env python3
"""Check TeX/Markdown parity, source correspondence, and page geometry."""
from pathlib import Path
import re,json,hashlib
import fitz

ROOT=Path(__file__).resolve().parent
tex=(ROOT/'Sufficient_Resolution_Visual_Guide.tex').read_text()
md=(ROOT/'Sufficient_Resolution_Visual_Guide.md').read_text()
content=json.loads((ROOT/'guide_content.json').read_text())
anchors=json.loads((ROOT/'validation/source_anchors.json').read_text())
crosswalk=json.loads((ROOT/'validation/claim_crosswalk.json').read_text())
concordance=ROOT.parent/'traditional/Claim_Lean_Concordance.json'
claim_records=json.loads(concordance.read_text())['claims']
anchor_contract=[{'claim_id':c['claim_id'],'anchors':c['anchors']} for c in claim_records]
anchor_digest=hashlib.sha256(json.dumps(anchor_contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert anchor_digest==crosswalk['source_concordance_anchor_sha256']
assert crosswalk['traditional_groups_covered']==[f'SR-{i:02}' for i in range(1,65)]
examples=json.loads((ROOT/'validation/visual_example_checks.json').read_text())
eqs=re.findall(r'^\\\[\s*(.*?)\s*^\\\]',tex,re.S|re.M)
mdeqs=re.findall(r'^\$\$\s*(.*?)\s*^\$\$',md,re.S|re.M)
assert eqs==mdeqs,'TeX and Markdown display equations differ'
assert len(content)==len(re.findall(r'^## ',md,re.M))==42
assert len(re.findall(r'^\*\*Source anchors:',md,re.M))==42
assert len(re.findall(r'!\[.*?\]\(figures/',md))==18
for anchor in anchors:
    source=ROOT.parent/'formal/Komorebi/SufficientResolution'/f'{anchor["module"]}.lean'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==anchor['source_sha256']
for section in content:
    if section['figure']:
        name,caption=section['figure']
        assert (ROOT/'figures'/f'{name}.pdf').is_file()
        assert (ROOT/'figures'/f'{name}.svg').is_file()
        assert (ROOT/'figures'/f'{name}.png').is_file()
for name,expected in examples['figure_sha256'].items():
    assert hashlib.sha256((ROOT/'figures'/name).read_bytes()).hexdigest()==expected
pdf=ROOT/'Sufficient_Resolution_Visual_Guide.pdf'
doc=fitz.open(pdf)
bounds=[]
for number,page in enumerate(doc,1):
    for block in page.get_text('blocks'):
        if block[0]<-1 or block[1]<-1 or block[2]>page.rect.width+1 or block[3]>page.rect.height+1:
            bounds.append({'page':number,'bounds':block[:4]})
assert not bounds,'Text extends beyond page boundaries'
logfile=ROOT/'Sufficient_Resolution_Visual_Guide.log'
if logfile.exists():
    bad=[line for line in logfile.read_text().splitlines() if any(key in line for key in ['Overfull','Warning','Undefined'])]
    assert not bad,bad
else:
    bad=[]
report={'status':'PASS','pages':len(doc),'sections':len(content),'equations_tex_md_identical':len(eqs),'figure_links_captions_preserved':18,'source_anchor_blocks':42,'source_anchor_occurrences':len(anchors),'unique_source_declarations':len({(a['module'],a['name']) for a in anchors}),'traditional_claim_groups_cross_referenced':64,'original_figure_count':examples['figure_count'],'exact_rational_assertions':examples['assertions'],'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'no_text_outside_pages':True,'latex_warning_overfull_undefined_count':len(bad),'visual_inspection':'Creator: all18figurecontacts and PDFpages1,6,24,33,34,39,43,44,45; companion: all18rawfigures and earlier PDFpages1,6,11,16,24,27,33,36,42,43. New residual section and stable-ID rows checked after integration. Geometry annotations and source-existence sentence corrected and re-viewed.','scope':'Finite example checks and drawing QA, not universal proof or fresh Lean compilation.'}
(ROOT/'validation/visual_qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','pages','sections','equations_tex_md_identical','exact_rational_assertions']}))
