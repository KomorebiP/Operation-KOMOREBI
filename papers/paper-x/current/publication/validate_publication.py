#!/usr/bin/env python3
"""Check reader structure, companion targets, atlas identity, and current locators."""
from pathlib import Path
import argparse,hashlib,json,re,sys
import fitz
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(pdf_dir: Path, write_locators: bool=False):
    wanted={row['file_name']:row['expected_pages'] for row in json.loads((ROOT/'publication/documents.json').read_text())}
    documents={n:fitz.open(pdf_dir/n) for n in wanted};report=[];remote=[];errors=[]
    for name,d in documents.items():
        if len(d)!=wanted[name]:errors.append((name,'page_count',len(d)))
        names=d.resolve_names();internal=0;external=0;outside=[]
        for pi,p in enumerate(d):
            if not p.get_text().strip():errors.append((name,pi+1,'empty_page_text'))
            rect=p.rect+(-2,-2,2,2)
            for block in p.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line.get('spans',[]):
                        if span['text'].strip() and not rect.contains(fitz.Rect(span['bbox'])):outside.append({'page':pi+1,'text':span['text'],'box':span['bbox']})
            for link in p.get_links():
                if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                    target=link.get('page',-1)
                    if 'nameddest' in link:
                        dest=names.get(link['nameddest']);target=dest.get('page',-1) if dest else -1
                    if not 0<=target<len(d):errors.append((name,pi+1,'unresolved_internal',link))
                    internal+=1
                elif link['kind'] in (fitz.LINK_LAUNCH,fitz.LINK_GOTOR):
                    f=d.xref_get_key(link['xref'],'A/F')[1];dest=d.xref_get_key(link['xref'],'A/D')[1]
                    if f not in documents or dest not in documents[f].resolve_names():errors.append((name,pi+1,'unresolved_companion',f,dest))
                    remote.append({'from':name,'page':pi+1,'file':f,'destination':dest});external+=1
                else:errors.append((name,pi+1,'unexpected_link_kind',link['kind']))
        if outside:errors.append((name,'outside_page_text',outside))
        report.append({'name':name,'pages':len(d),'sha256':sha(pdf_dir/name),'bookmarks':len(d.get_toc()),'named_destinations':len(names),'internal_links':internal,'companion_links':external,'outside_page_spans':len(outside)})
    m=documents['Paper_X_Traditional_Final.pdf'];v=documents['Paper_X_Visual_Guide_Final.pdf'];routes=[]
    # Only page content is compared here. Link targets were independently checked above.
    for i in range(30):
        if m[len(m)-30+i].get_text()!=v[3+i].get_text():errors.append(('atlas_text',i+1))
        if m[len(m)-30+i].get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False).samples != v[3+i].get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False).samples:errors.append(('atlas_render',i+1))
        routes.append({'atlas':'V'+str(i+1),'visual_pdf_page':i+4,'monograph_pdf_page':i+len(m)-29})
    records=json.loads((ROOT/'publication/CLAIM_RECORDS.json').read_text());n=m.resolve_names()
    for c in records:
        dest=n.get(c['pdf_destination']);assert dest,c
        c['monograph_pdf_page']=dest['page']+1;c['printed_page']=dest['page']
        assert any(x['destination']==c['pdf_destination'] for x in remote),c
    result={'status':'passed' if not errors else 'failed','documents':report,'total_pages':sum(x['pages'] for x in report),
      'internal_links_checked':sum(x['internal_links'] for x in report),'companion_links_checked':len(remote),
      'statement_routes_checked':len(records),'atlas_page_pairs_checked':30,'errors':errors}
    if write_locators:
        (ROOT/'CURRENT_PUBLICATION_LOCATORS.json').write_text(json.dumps({'edition':'2026-10-20','documents':report,'claims':records,'atlas':routes,'companion_links':remote},indent=2))
    for d in documents.values():d.close()
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf-directory',type=Path,default=ROOT/'publication/pdfs');p.add_argument('--write-locators',action='store_true');p.add_argument('--report',type=Path)
    a=p.parse_args();result=check(a.pdf_directory,a.write_locators);out=json.dumps(result,indent=2);print(out)
    if a.report:a.report.write_text(out)
    sys.exit(0 if result['status']=='passed' else 1)
