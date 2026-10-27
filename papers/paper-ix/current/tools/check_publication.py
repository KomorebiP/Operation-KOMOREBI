#!/usr/bin/env python3
"""Check current PDF mirrors, navigation and physical page limits. Requires PyMuPDF."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);args=ap.parse_args()
    release=json.loads((ROOT/'RELEASE.json').read_text());errors=[];records=[]
    for row in release['documents']:
        p=ROOT/row['file'];q=ROOT/row['mirror'];digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=row['sha256'] or q.read_bytes()!=p.read_bytes():errors.append('PDF hash/mirror: '+p.name)
        with fitz.open(p) as doc:
            if len(doc)!=row['pages']:errors.append('Page count: '+p.name)
            links=0;names=doc.resolve_names()
            for n,page in enumerate(doc,1):
                for link in page.get_links():
                    if link.get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                        links+=1
                        if not 0<=link.get('page',-1)<len(doc):errors.append(f'Link out of range: {p.name}:{n}')
                        if link.get('kind')==fitz.LINK_NAMED and link.get('nameddest') not in names:errors.append(f'Unresolved named link: {p.name}:{n}')
                for w in page.get_text('words'):
                    if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:errors.append(f'Word out of page: {p.name}:{n}')
            records.append({'file':p.name,'pages':len(doc),'internal_links_checked':links})
    loc=json.loads((ROOT/'CURRENT_PUBLICATION_LOCATORS.json').read_text());main_pdf=ROOT/'publication/pdfs'/loc['file_name']
    if hashlib.sha256(main_pdf.read_bytes()).hexdigest()!=loc['pdf_sha256']:errors.append('Stale page-map hash')
    with fitz.open(main_pdf) as doc:
        names=doc.resolve_names()
        for key,row in loc['labels'].items():
            actual=names.get(row['pdf_destination'])
            if actual is None or actual['page']+1!=row['physical_page']:errors.append('Stale page-map label '+key)
    current=json.loads((ROOT/'sources/lean/audit/CURRENT_CROSSWALK.json').read_text())
    old=json.loads((ROOT/'sources/lean/audit/CROSSWALK.json').read_text())
    if len(current)!=len(old):errors.append('Crosswalk size changed')
    for a,b in zip(current,old):
        key=a['manuscript_label'];mapped=loc['labels'][key]
        if a['source_links']!=b['source_links']:errors.append('Source links changed '+key)
        if a['traditional_physical_page']!=mapped['physical_page'] or a['traditional_number']!=mapped['number']:errors.append('Crosswalk stale '+key)
        if a['traditional_pdf_sha256']!=loc['pdf_sha256']:errors.append('Crosswalk hash stale '+key)
    report={'status':'PASS' if not errors else 'FAIL','documents':records,'pdf_copies':2*len(records),'main_labels_checked':len(loc['labels']),'inherited_statement_rows':len(current),'retained_source_links':sum(len(x['source_links'])for x in current),'errors':errors,'scope':'Publication metadata and source-link preservation only. Page-bound checks do not establish absence of every visual overlap.'}
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));raise SystemExit(bool(errors))
if __name__=='__main__':main()
