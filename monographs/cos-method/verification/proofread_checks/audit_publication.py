"""Static PDF/source checks. Visual inspection and mathematical review are separate."""
from pathlib import Path
import json,re,zipfile,collections,shutil
import fitz
ROOT=Path(__file__).resolve().parents[2]
pdf=fitz.open(ROOT/'K_COS_Monograph.pdf')
outside=[];badlinks=[];blanks=[];replacement=[];link_count=0
texts=[]
for i,p in enumerate(pdf):
    text=p.get_text();texts.append(text)
    if not text.strip():blanks.append(i+1)
    if '\ufffd' in text:replacement.append(i+1)
    for w in p.get_text('words'):
        if w[0]<-1 or w[1]<-1 or w[2]>p.rect.width+1 or w[3]>p.rect.height+1:outside.append({'page':i+1,'word':w[4],'bounds':w[:4]})
    for link in p.get_links():
        link_count+=1
        if link.get('kind')==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(pdf):badlinks.append({'page':i+1,'link':str(link)})
sources=list((ROOT/'book').rglob('*.tex'))
text='\n'.join(p.read_text() for p in sources)
labels=re.findall(r'\\label\{([^}]+)\}',text)
refs=re.findall(r'\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}',text)
cites=[key for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',text) for key in group.split(',')]
bibs=re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',text)
envs=collections.Counter(re.findall(r'\\begin\{(theorem|lemma|proposition|corollary|remark|algorithm|proof)\}',text))
baseline=json.loads(Path(__file__).with_name('baseline_inventory.json').read_text())
original_labels=set(baseline['source_labels'])
old_envs=collections.Counter(baseline['environment_counts'])
import hashlib
lean_changed=[]
for rel,digest in baseline['lean_sha256'].items():
    p=ROOT/rel
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:lean_changed.append(rel)
log=(ROOT/'verification/typesetting/pass_3.txt').read_text()
report=dict(pages=len(pdf),bookmarks=len(pdf.get_toc()),links=link_count,pages_without_text=blanks,text_outside_page=outside,invalid_internal_links=badlinks,replacement_character_pages=replacement,duplicate_labels=[x for x,n in collections.Counter(labels).items() if n>1],undefined_source_references=sorted(set(refs)-set(labels)),undefined_source_citations=sorted(set(cites)-set(bibs)),original_labels_lost=sorted(original_labels-set(labels)),original_environment_counts=dict(old_envs),current_environment_counts=dict(envs),bibliography_entries=len(bibs),lean_files_changed=lean_changed,lean_compiler_available=bool(shutil.which('lean')),lake_available=bool(shutil.which('lake')),latex_overfull_boxes=len(re.findall('Overfull',log)),latex_underfull_boxes=len(re.findall('Underfull',log)),latex_undefined_warnings=len(re.findall('undefined',log)),latex_missing_glyph_warnings=len(re.findall('Missing character',log)),visual_review='Every page rendered with PDFium; all eight contact sheets and selected corrected pages inspected. This is a layout review, not an independent formal proof.')
assert not any([outside,badlinks,blanks,replacement,report['duplicate_labels'],report['undefined_source_references'],report['undefined_source_citations'],report['original_labels_lost'],lean_changed])
assert not any([report['latex_overfull_boxes'],report['latex_undefined_warnings'],report['latex_missing_glyph_warnings']])
Path(__file__).with_name('publication_audit.json').write_text(json.dumps(report,indent=2)+'\n')
Path(__file__).with_name('final_pdf_text.txt').write_text('\n\n'.join(f'PDF PAGE {i+1}\n'+t for i,t in enumerate(texts)))
print(json.dumps(report,indent=2))
