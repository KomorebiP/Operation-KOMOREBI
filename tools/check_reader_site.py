#!/usr/bin/env python3
"""Check generated reader links, basic HTML access features and reading ZIPs."""
import argparse
import collections
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
from urllib.parse import parse_qs, unquote, urlsplit
import zipfile


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.ids=[];self.links=[];self.inputs=[];self.labels=set()
        self.h1=0;self.main=0;self.language=None;self.title=False;self.skip=False
        self.images_without_alt=0
        self.iframes=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.language=a.get('lang')
        if tag=='title':self.title=True
        if tag=='h1':self.h1+=1
        if tag=='main':self.main+=1
        if tag in {'a','link','script','img','iframe'}:
            target=a.get('href',a.get('src'))
            if target:self.links.append(target)
        if tag=='a' and a.get('href')=='#main':self.skip=True
        if tag in {'input','select','textarea'} and a.get('type') not in {'submit','hidden'}:self.inputs.append(a)
        if tag=='label' and a.get('for'):self.labels.add(a['for'])
        if tag=='img' and 'alt' not in a:self.images_without_alt+=1
        if tag=='iframe':self.iframes.append(a)


def inspect_site(root):
    files={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    # The pinned third-party viewer has its own interface and localization markup.
    # Verify its integrity separately, while checking every link into it below.
    pages={p:Page((root/p).read_text(encoding='utf-8')) for p in files if p.endswith('.html') and not p.startswith('assets/pdfjs/')}
    links=0;fragments=0
    for path,page in pages.items():
        assert page.language=='en',(path,'Language')
        assert page.title and page.h1==1 and page.main==1 and page.skip,(path,'Document structure',page.h1,page.main)
        assert len(page.ids)==len(set(page.ids)),(path,'Duplicate IDs',[x for x,n in collections.Counter(page.ids).items() if n>1])
        assert page.images_without_alt==0,(path,'Image without alt attribute')
        assert all(f.get('title') for f in page.iframes),(path,'Frame without a title')
        for control in page.inputs:
            assert control.get('id') in page.labels or control.get('aria-label'),(path,'Unlabeled control')
        for target in page.links:
            parts=urlsplit(target)
            if parts.scheme or parts.netloc:continue
            relative=unquote(parts.path)
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(path),relative)) if relative else path
            assert not resolved.startswith('../'),(path,target,'Escapes site')
            assert resolved in files,(path,target,'Missing local file')
            links+=1
            if resolved=='assets/pdfjs/web/viewer.html':
                from fetch_pdf_runtime import RUNTIME_ID
                query=parse_qs(parts.query)
                assert query.get('v')==[RUNTIME_ID],(path,target,'Stale PDF reader URL')
                assert len(query.get('file',[]))==1,(path,target,'Missing PDF target')
                pdf=urlsplit(query['file'][0])
                assert not pdf.scheme and not pdf.netloc,(path,target,'External PDF target')
                local=posixpath.normpath(posixpath.join(posixpath.dirname(resolved),unquote(pdf.path)))
                assert local in files and local.startswith('documents/files/') and local.lower().endswith('.pdf'),(path,target,'Invalid local PDF')
            if parts.fragment and resolved in pages:
                assert unquote(parts.fragment) in pages[resolved].ids,(path,target,'Missing fragment')
                fragments+=1
    index=json.loads((root/'search-index.json').read_bytes())
    assert len(index)==len({x['url'] for x in index}),'Duplicate search pages'
    assert all(x['url'] in pages for x in index)
    bundles=json.loads((root/'downloads/index.json').read_bytes())
    zipped_files=0
    for bundle in bundles:
        path=root/bundle['url']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==bundle['archive_sha256']
        with zipfile.ZipFile(path) as z:
            assert len(z.namelist())==len(set(z.namelist()))
            for name in z.namelist():
                assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
            manifest=json.loads(z.read('CONTENTS.json'))
            assert manifest['source_revision']==bundle['source_revision']
            for f in manifest['files']:
                assert hashlib.sha256(z.read('files/'+f['path'])).hexdigest()==f['sha256']
                zipped_files+=1
            assert 'collection-notices/LICENSE.md' in z.namelist()
    from fetch_pdf_runtime import verify
    verify(root/'assets/pdfjs')
    documents=json.loads((root/'documents/index.json').read_bytes())
    assert len(documents['files'])==len({r['repository_path'] for r in documents['files']})
    pdf_count=0
    for record in documents['files']:
        assert record['url'] in pages
        assert record['file_url'] in files
        raw=(root/record['file_url']).read_bytes()
        assert len(raw)==record['size'] and hashlib.sha256(raw).hexdigest()==record['sha256'],record['repository_path']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==record['git_blob_sha1']
        if record['format']=='pdf':
            assert raw.startswith(b'%PDF-')
            assert len(pages[record['url']].iframes)==1
            pdf_count+=1
    for record in documents.get('images',[]):
        assert record['file_url'] in files
        raw=(root/record['file_url']).read_bytes()
        assert len(raw)==record['size'] and hashlib.sha256(raw).hexdigest()==record['sha256'],record['repository_path']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==record['git_blob_sha1']
    return dict(status='PASS',html_pages=len(pages),local_links=links,fragments=fragments,
                search_pages=len(index),reading_bundles=len(bundles),checked_bundle_files=zipped_files,
                reading_documents=len(documents['files']),pdfs=pdf_count,
                scope='Static navigation, HTML structure and ZIP source identities. Not WCAG certification or mathematical review.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site',type=Path,required=True)
    args=p.parse_args()
    result=inspect_site(args.site)
    (args.site/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
