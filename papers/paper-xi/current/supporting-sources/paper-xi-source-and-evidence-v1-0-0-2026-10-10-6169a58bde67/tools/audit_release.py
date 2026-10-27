#!/usr/bin/env python3
"""Source, conversion, reference and PDF integrity audit for the reading release.

This is an editorial and source-preservation audit. It neither invokes Lean nor
checks the universal arithmetic assertions. All output must be outside the package.
"""
from __future__ import annotations
import argparse, collections, difflib, hashlib, json, re, subprocess
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'publication/source'
BASE=ROOT/'predecessor/block06/publication/source'
PDF=ROOT/'publication/pdfs'
READERS={'Paper_XI_Traditional_v1.0.0.pdf':109,'Paper_XI_Visual_Guide_v1.0.0.pdf':53,
         'Paper_XI_Lean_Guide_v1.0.0.pdf':235,'Paper_XI_Conjecture66_Progress_v0.4.0.pdf':77,
         'Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf':36}
STATEMENTS=['theorem','proposition','lemma','corollary','definition','example','standardfact','remark','conjecture']
def digest(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def read_json(p:Path):return json.loads(p.read_text())
def blocks(text:str,kind:str)->list[str]:
    return re.findall(r'\\begin\{'+re.escape(kind)+r'\}.*?\\end\{'+re.escape(kind)+r'\}',text,re.S)
def normalize(text:str)->str:
    return re.sub(r'\s+','',text).replace('−','-').replace('–','-').replace('…','...')
def converted_superscripts(text:str)->list[str]:
    return re.findall(r'\\textsuperscript\{[^}]*\}',text)
def source_audit()->dict:
    errors=[];changes=[];preserved=[];patch=[]
    for p in sorted(BASE.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(BASE);q=SOURCE/rel
        if not q.is_file():errors.append({'missing':str(rel)});continue
        a,b=digest(p),digest(q)
        if a==b:preserved.append(str(rel))
        else:
            changes.append({'path':str(rel),'old_sha256':a,'new_sha256':b})
            if p.suffix in ('.tex','.md','.py','.sty','.bib'):
                patch.extend(difflib.unified_diff(p.read_text().splitlines(True),q.read_text().splitlines(True),fromfile='block06/'+str(rel),tofile='release/'+str(rel)))
    old=(BASE/'traditional/Paper_XI_Traditional_Final.tex').read_text();new=(SOURCE/'traditional/Paper_XI_Traditional_Final.tex').read_text()
    counts={kind:len(blocks(old,kind)) for kind in STATEMENTS}
    if blocks(old,'proof')!=blocks(new,'proof'):errors.append('main proof bodies changed')
    for kind in STATEMENTS:
        if blocks(old,kind)!=blocks(new,kind):errors.append('statement body changed: '+kind)
    repairs=read_json(ROOT/'evidence/block07/CONVERSION_REPAIRS.json')
    notes=read_json(ROOT/'evidence/block07/APPENDIX_SOURCE_MAP.json')['sources']
    clarifications=read_json(ROOT/'evidence/block07/EDITORIAL_CLARIFICATIONS.json')['changes']
    for e in notes:
        raw=ROOT/e['local_path']
        if digest(raw)!=e['sha256']:errors.append('raw-source hash mismatch: '+str(raw))
    for p in sorted((BASE/'traditional/appendices').glob('*.tex')):
        expected=p.read_text();q=SOURCE/'traditional/appendices'/p.name
        for e in repairs['repairs']:
            if e['appendix']!=p.name:continue
            if expected.count(e['before'])!=e['occurrences']:errors.append('repair occurrence mismatch '+p.name)
            if normalize(e['raw_expression']) not in normalize((ROOT/e['raw_source']).read_text()):errors.append('raw expression not found '+e['raw_expression'])
            expected=expected.replace(e['before'],e['after'])
        for e in clarifications:
            if e['path']=='traditional/appendices/'+p.name:expected=expected.replace(e['before'],e['after'])
        if expected!=q.read_text():errors.append('unexpected appendix change '+p.name)
        if converted_superscripts(q.read_text()):errors.append('converted superscript remains '+p.name)
        if blocks(p.read_text(),'Verbatim')!=blocks(q.read_text(),'Verbatim'):errors.append('literal appendix code changed '+p.name)
    return {'status':'passed' if not errors else 'failed','errors':errors,'baseline_files':len(preserved)+len(changes),
            'byte_preserved_files':len(preserved),'changed_files':changes,'proof_bodies':len(blocks(old,'proof')),
            'statement_bodies':sum(counts.values()),'statement_counts':counts,'raw_appendices':len(notes),
            'superscript_repairs':sum(e['occurrences'] for e in repairs['repairs']),
            'appendices_with_repairs':len({e['appendix'] for e in repairs['repairs']}),
            'separate_header_clarifications':len(clarifications),'patch':''.join(patch)}
def citation_audit()->dict:
    src=SOURCE/'traditional';bib=(src/'Paper_XI_Traditional_Final.bib').read_text()
    keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib);citations=[];labels=[];refs=[]
    # These are the actual .tex inputs in this reader tree, not historical archives.
    for p in sorted(src.rglob('*.tex')):
        t=p.read_text()
        for m in re.finditer(r'\\(?:cite\w*|nocite)\*?(?:\[[^\]]*\])*\{([^}]*)\}',t):
            citations.extend(k.strip() for k in m.group(1).split(',') if k.strip()!='*')
        labels.extend(re.findall(r'\\label\{([^}]+)\}',t))
        for m in re.finditer(r'\\(?:ref|eqref|pageref|autoref|cref|Cref)\*?\{([^}]+)\}',t):refs.extend(k.strip() for k in m.group(1).split(','))
    unresolved=sorted(set(citations)-set(keys));missing=sorted(set(refs)-set(labels))
    duplicates=[k for k,n in collections.Counter(keys).items() if n>1]
    return {'status':'passed' if not unresolved and not missing and not duplicates else 'failed','bibliography_entries':len(keys),
            'distinct_cited_keys':len(set(citations)),'citation_occurrences':len(citations),'undefined_keys':unresolved,
            'duplicate_bibliography_keys':duplicates,'local_labels':len(labels),'local_reference_occurrences':len(refs),
            'unresolved_local_references':missing,'scope':'Local source-key and label resolution, not a fresh proof audit of every cited work.'}
def pdf_audit()->dict:
    errors=[];readers=[];links=[]
    actual={p.name for p in PDF.glob('*.pdf')}
    if actual!=set(READERS):errors.append({'reader_filenames_mismatch':sorted(actual)})
    for name,count in READERS.items():
        path=PDF/name
        with fitz.open(path) as doc:
            if len(doc)!=count:errors.append({'page_count':name,'actual':len(doc),'expected':count})
            dests=doc.resolve_names()
            for i,page in enumerate(doc):
                for link in page.get_links():
                    row={'file':name,'page':i+1,'kind':link['kind']}
                    if link['kind']==fitz.LINK_GOTO:
                        ok=0<=link['page']<len(doc);row['target_page']=link['page']+1
                    elif link['kind']==fitz.LINK_NAMED:
                        d=dests.get(link.get('nameddest',''),{});ok='page' in d and 0<=d['page']<len(doc);row['destination']=link.get('nameddest')
                    elif link['kind']==fitz.LINK_GOTOR:
                        target=PDF/link['file'];ok=target.is_file()
                        if ok:
                            with fitz.open(target) as td:ok=0<=link['page']<len(td)
                        row.update(target_file=link['file'],target_page=link['page']+1)
                    else:ok=False;row['unexpected_link']=str(link)
                    row['valid']=ok;links.append(row)
                    if not ok:errors.append(row)
                for b in page.get_text('dict')['blocks']:
                    for line in b.get('lines',[]):
                        for span in line['spans']:
                            x0,y0,x1,y1=span['bbox']
                            if min(x0,y0)<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5 or '\ufffd' in span['text']:
                                errors.append({'file':name,'page':i+1,'span':span})
            readers.append({'filename':name,'pages':len(doc),'bytes':path.stat().st_size,'sha256':digest(path),'bookmarks':len(doc.get_toc())})
    return {'status':'passed' if not errors else 'failed','readers':readers,'total_pages':sum(d['pages'] for d in readers),
            'internal_links':sum(d['kind'] in [fitz.LINK_GOTO,fitz.LINK_NAMED] for d in links),
            'companion_links':sum(d['kind']==fitz.LINK_GOTOR for d in links),'links':links,'errors':errors}
def ast_audit()->dict:
    """Optional exact reconstruction of the historical Markdown parser hazards."""
    rows=[]
    for e in read_json(ROOT/'evidence/block07/APPENDIX_SOURCE_MAP.json')['sources']:
        raw=ROOT/e['local_path'];run=subprocess.run(['pandoc','-f','markdown+tex_math_single_backslash','-t','json',str(raw)],capture_output=True,text=True,timeout=30,check=True)
        counts=collections.Counter();nodes=[]
        def visit(x):
            if isinstance(x,dict):
                if x.get('t') in ('Superscript','Subscript','Link','Strikeout','Emph'):
                    counts[x['t']]+=1;nodes.append(x)
                for v in x.values():visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        visit(json.loads(run.stdout));rows.append({'source':e['local_path'],'sha256':digest(raw),'nodes':nodes,'counts':dict(counts)})
    totals=collections.Counter()
    for row in rows:totals.update(row['counts'])
    return {'status':'executed','pandoc_version':subprocess.check_output(['pandoc','--version'],text=True).splitlines()[0],
            'totals':dict(totals),'sources':rows,'scope':'All15 raw notes, selected syntactic hazard families only. Link loss repaired in B06; all44 superscripts restored in B07. Not proof that all mathematical source content is correct.'}
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--pandoc-ast',action='store_true');a=ap.parse_args()
    out=a.output.resolve()
    if out.is_relative_to(ROOT):raise SystemExit('Write audit outputs outside the package.')
    out.mkdir(parents=True,exist_ok=True);reports={'source':source_audit(),'references':citation_audit(),'pdf':pdf_audit()}
    if a.pandoc_ast:reports['markdown_ast']=ast_audit()
    for name,data in reports.items():
        if 'patch' in data:(out/'SOURCE_CHANGES.patch').write_text(data.pop('patch'))
        (out/(name.upper()+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    summary={'status':'passed' if all(v['status'] in ('passed','executed') for v in reports.values()) else 'failed',
             'audits':{k:v['status'] for k,v in reports.items()},'script_sha256':digest(Path(__file__))}
    (out/'AUDIT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return int(summary['status']!='passed')
if __name__=='__main__':raise SystemExit(main())
