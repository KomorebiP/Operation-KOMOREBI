#!/usr/bin/env python3
"""Check preservation and PDF production, without claiming a new mathematical audit."""
from pathlib import Path
import hashlib, json, re
import fitz

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'source_release'
PUB=ROOT/'publication'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize_layout(text):
    edits=json.loads((ROOT/'verification/editorial_changes.json').read_text())
    text=text.replace(edits['inserted_block'],'')
    for edit in edits['changes']:
        text=text.replace(edit['new'],edit['old'])
    text=text.replace('\\phantomsection % Navigation correction: anchor the unnumbered heading.\n','')
    text=text.replace('\\clearpage % Monograph layout: keep glossary together.\n','')
    text=text.replace('\\clearpage % Monograph layout: keep the margin chart with its discussion.\n','')
    text=text.replace('\\begin{figure}[!htbp]\n\\centering\n\\includegraphics[width=.82\\linewidth]{figures/joint_enforcement_margin.pdf}',
                      '\\begin{figure}[t]\n\\centering\n\\includegraphics[width=.82\\linewidth]{figures/joint_enforcement_margin.pdf}')
    return text

old=(OLD/'Machine_Societies_v1.0.0.tex').read_text()
new=(PUB/'Machine_Societies_v1.0.0.tex').read_text()
start=r'\section*{About this edition}'
original_body=old[old.index(start):]
body_ok=original_body==normalize_layout(new[new.index(start):])
abstract=('A population of artificial agents'+old.split(r'\noindent A population of artificial agents',1)[1].split(r'\vfill',1)[0]).strip()
abstract_ok=abstract in new
scope=re.search(r'\\noindent\{\\color\{muted\}\\small \\textbf\{Scope\.\} (.*?)\}\s*\\end\{titlepage\}',old,re.S).group(1)
counts={env:len(re.findall(r'\\begin\{'+env+r'\}',new)) for env in ['theorem','proposition','proof','definition','counterexample','figure']}
counts['references']=len(re.findall(r'\\bibitem',new))
block_pattern=r'\\begin\{(theorem|proposition)\}\[([^\]]+)\]\\label\{([^}]+)\}(.*?)\\end\{\1\}\s*\\begin\{proof\}(.*?)\\end\{proof\}'
old_blocks={m.group(3):m.group() for m in re.finditer(block_pattern,old,re.S)}
new_blocks={m.group(3):m.group() for m in re.finditer(block_pattern,new,re.S)}
proofs_preserved=old_blocks==new_blocks and len(new_blocks)==62
assets=[]
for p in sorted((OLD/'figures').rglob('*')):
    if p.is_file():
        q=PUB/'figures'/p.relative_to(OLD/'figures')
        assets.append({'file':str(p.relative_to(OLD)),'sha256':sha(p),'unchanged':q.is_file() and sha(q)==sha(p)})
preservation={'status':'PASS' if body_ok and abstract_ok and proofs_preserved and scope in new and all(x['unchanged'] for x in assets) else 'FAIL',
 'original_source_sha256':sha(OLD/'Machine_Societies_v1.0.0.tex'),'current_source_sha256':sha(PUB/'Machine_Societies_v1.0.0.tex'),
 'main_body_preserved_after_registered_editorial_edits':body_ok,'all_62_statement_and_proof_blocks_byte_identical':proofs_preserved,'original_overview_preserved':abstract_ok,'original_scope_preserved':scope in new,
 'layout_edits':['Page break before the glossary','Page break before the common-monitor chart','Permit that chart to appear at its source location'],
 'navigation_edits':['Explicit anchor for About this edition','Explicit anchor for Notation and mathematical conventions'],
 'counts':counts,'figure_assets_and_generators':assets,
 'scope':'Source preservation and production checks. The targeted mathematical self-review and fresh exact computational replay have separate records. No Lean build is claimed.'}
(ROOT/'verification/content_preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')

doc=fitz.open(ROOT/'Machine_Societies_v1.0.0.pdf')
outside=[];markers=[];bad_links=[];fonts={};captions=[]
for i,page in enumerate(doc):
    text=page.get_text()
    if '??' in text or '\ufffd' in text:markers.append(i+1)
    captions.extend({'figure':int(m),'physical_page':i+1} for m in re.findall(r'Figure\s+(\d+)\.',text))
    for w in page.get_text('words'):
        if w[0]<0 or w[1]<0 or w[2]>page.rect.width or w[3]>page.rect.height:outside.append([i+1,*w[:5]])
    for link in page.get_links():
        if 'page' in link and not 0<=link['page']<len(doc):bad_links.append({'page':i+1,'link':link})
    for f in page.get_fonts(full=True):
        if f[0] in fonts:continue
        if f[2]=='Type3':
            kind,value=doc.xref_get_key(f[0],'CharProcs')
            glyphs=int(value.split()[0]) if kind=='xref' else None
            # A zero-glyph Type3 subset is a self-contained resource, not an
            # unembedded external font. Matplotlib can retain such a resource.
            embedded=bool(glyphs and doc.xref_object(glyphs).lstrip().startswith('<<'))
            embedding=f'embedded vector glyph dictionary ({len(doc.xref_get_keys(glyphs)) if glyphs else 0} entries)'
        else:
            embedded=bool(doc.extract_font(f[0])[3])
            embedding='embedded font program'
        fonts[f[0]]={'name':f[3],'type':f[2],'embedded':embedded,'embedding':embedding}
log=(ROOT/'verification/build_logs/xelatex_pass_3.txt').read_text(errors='replace')
diagnostics=[line for line in log.splitlines() if re.search(r'Overfull|undefined references|multiply defined|Missing character|^! ',line)]
def normalized_title(value): return re.sub('[^a-z0-9]','',value.casefold())
bookmark_mismatches=[]
for level,title,target in doc.get_toc():
    if not 1<=target<=len(doc) or normalized_title(title) not in normalized_title(doc[target-1].get_text()):
        bookmark_mismatches.append({'title':title,'physical_page':target})
frontmatter_links=[]
for title,following in [('About this edition','First edition.'),('Notation and mathematical conventions','The notation is local')]:
    matches=[i+1 for i,page in enumerate(doc) if title+'\n'+following in page.get_text()]
    if len(matches)!=1:raise ValueError('Cannot identify unique heading page: '+title)
    target=matches[0]
    matched=[]
    for page in [doc[2],doc[3]]:
        for link in page.get_links():
            rect=fitz.Rect(link['from']);rect.x0=0;rect.x1=page.rect.width;rect.y0-=2;rect.y1+=2
            if title in page.get_textbox(rect):matched.append(link.get('page',-1)+1)
    frontmatter_links.append({'title':title,'expected_physical_page':target,'actual_physical_pages':matched,'correct':bool(matched) and all(p==target for p in matched)})
aux=(ROOT/'verification/compiled_cross_references.aux').read_text()
label_rows={m.group(1):(m.group(2),m.group(3),m.group(4)) for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{([^}]+)\}\{.*?\}\{([^}]+)\}',aux)}
toc=doc.get_toc()
index_start=next(p for _,title,p in toc if title=='Theorem and proposition index')
index_end=next(p for _,title,p in toc if title=='Final edition and verification scope')
index_links=[link for page in doc[index_start-1:index_end-1] for link in page.get_links()]
index_records=[]
for m in re.finditer(block_pattern,new,re.S):
    kind,title,label=m.group(1,2,3)
    number,printed,destination=label_rows[label]
    links=[link for link in index_links if link.get('nameddest')==destination]
    targets=[link.get('page',-1) for link in links]
    needle=normalized_title(kind.title()+' '+number)
    correct=len(links)>=3 and all(0<=p<len(doc) and doc[p].get_label()==printed and needle in normalized_title(doc[p].get_text()) for p in targets)
    index_records.append({'statement':kind.title()+' '+number,'label':label,'printed_page':printed,'index_link_count':len(links),'target_physical_pages':sorted({p+1 for p in targets}),'correct':correct})
index_ok=len(index_records)==62 and all(x['correct'] for x in index_records)
ok=not(outside or markers or bad_links or diagnostics or bookmark_mismatches) and index_ok and all(x['correct'] for x in frontmatter_links) and all(f['embedded'] for f in fonts.values()) and sorted(x['figure'] for x in captions)==list(range(1,15))
report={'status':'PASS' if ok else 'FAIL','pages':len(doc),'pdf_sha256':sha(ROOT/'Machine_Societies_v1.0.0.pdf'),'out_of_page_words':outside,'unresolved_or_replacement_markers':markers,
 'bad_internal_links':bad_links,'compiler_diagnostics':diagnostics,'fonts':list(fonts.values()),'figure_captions':captions,
 'bookmarks_checked':len(doc.get_toc()),'bookmark_heading_mismatches':bookmark_mismatches,'frontmatter_contents_links':frontmatter_links,
 'theorem_index_entries':index_records,'theorem_index_complete_and_correct':index_ok,
 'scope':'PDF production and structural checks. Rendering and visual review are separately recorded.'}
(ROOT/'verification/pdf_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'preservation':preservation['status'],'pdf':report['status'],'pages':len(doc),'counts':counts,'diagnostics':diagnostics,'out_of_page_words':len(outside),'bad_internal_links':len(bad_links)},indent=2))
raise SystemExit(preservation['status']!='PASS' or not ok)
