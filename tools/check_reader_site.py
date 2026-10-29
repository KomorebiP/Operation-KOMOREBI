#!/usr/bin/env python3
"""Check generated reader links, basic HTML access features and reading ZIPs."""
import argparse
import collections
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
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


def check_search_targets(index, pages):
    assert len(index)==len({x['url'] for x in index}),'Duplicate search targets'
    for item in index:
        target=urlsplit(item['url'])
        assert not target.scheme and not target.netloc and not target.query,item['url']
        path=unquote(target.path)
        assert path in pages,('Missing search page',item['url'])
        if target.fragment:
            assert unquote(target.fragment) in pages[path].ids,('Missing search fragment',item['url'])


def check_readable_chapter(root, documents, pages):
    from readable_chapters import BOOKS, CHAPTERS, original_math, expand_math, manuscript_macros
    records = {r['repository_path']:r for r in documents['files']}
    reports = json.loads((root/'documents/readable-chapters.json').read_bytes())
    assert [r['source'] for r in reports] == [c['source'] for c in CHAPTERS]
    class MathText(HTMLParser):
        def __init__(self):
            super().__init__()
            self.depth=0; self.expressions=[]
        def handle_starttag(self,tag,attrs):
            if self.depth: self.depth+=1
            elif 'arithmatex' in dict(attrs).get('class','').split():
                self.depth=1
                self.expressions.append('')
        def handle_endtag(self,tag):
            if self.depth: self.depth-=1
        def handle_data(self,data):
            if self.depth: self.expressions[-1]+=data
    count=0
    for report,spec in zip(reports,CHAPTERS):
        source,page=spec['source'],spec['url']
        main_path=BOOKS[spec['work']]['main']
        main=(root/records[main_path]['file_url']).read_text(encoding='utf-8-sig')
        assert report['macro_source']==main_path
        raw=(root/records[source]['file_url']).read_bytes()
        expressions=original_math(raw.decode('utf-8-sig'))
        assert report['source_sha256']==hashlib.sha256(raw).hexdigest()
        assert report['url']==page
        assert report['math_expressions']==len(expressions)
        assert report['math_sequence_sha256']==hashlib.sha256(json.dumps(expressions,ensure_ascii=False).encode()).hexdigest()
        assert report['macros']==manuscript_macros(main)
        assert not report['new_proof_review'] and not report['new_lean_execution']
        for node in report['nodes']:
            assert node['id'] in pages[page].ids
            assert 'L'+str(node['line']) in pages[records[source]['url']].ids
        rendered=MathText()
        rendered.feed((root/page).read_text(encoding='utf-8'))
        assert [x[2:-2] for x in rendered.expressions]==[expand_math(x,report['macros']) for x in expressions], ('HTML mathematical sequence differs from source',source)
        count+=len(expressions)
    return count


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
    check_search_targets(index, pages)
    bundles=json.loads((root/'downloads/index.json').read_bytes())
    works={r['work'] for r in bundles}
    for item in index:
        assert isinstance(item.get('work_ids'),list),('Missing search work list',item['url'])
        assert len(item['work_ids'])==len(set(item['work_ids'])) and set(item['work_ids']) <= works,('Unknown or repeated search work',item['url'])
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
    from fetch_python_runtime import verify as verify_python
    runtime = verify_python(root/'assets/python')
    assert json.loads((root/'assets/python/SOURCE.json').read_bytes()) == runtime
    python = json.loads((root/'downloads/python-playground.json').read_bytes())
    build = json.loads((root/'build-info.json').read_bytes())
    assert python['collection_revision'] == build['collection_revision']
    assert python['library_revision'] == build['library_revisions']['math']
    assert python['runtime_version'] == runtime['version']
    assert set(python['examples']) == {'packets', 'refinement', 'recovery', 'library'}
    for name, example in python['examples'].items():
        assert example['url'] == 'downloads/python-'+name+'.py'
        assert hashlib.sha256((root/example['url']).read_bytes()).hexdigest() == example['sha256']
        assert example['expected_output'].endswith('\n')
    assert python['library_url'] == 'downloads/komorebi-math-browser.zip'
    library = root/python['library_url']
    assert hashlib.sha256(library.read_bytes()).hexdigest() == python['library_sha256']
    with zipfile.ZipFile(library) as archive:
        assert set(archive.namelist()) == {f['archive_path'] for f in python['library_files']}
        assert len(archive.namelist()) == len(python['library_files'])
        for entry in python['library_files']:
            name = entry['archive_path']
            assert name == entry['path'].removeprefix('src/')
            assert name == 'LICENSE.md' or name.startswith('komorebi_math/')
            assert '..' not in PurePosixPath(name).parts and '\\' not in name
            raw = archive.read(name)
            assert hashlib.sha256(raw).hexdigest() == entry['sha256']
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == entry['git_blob_sha1']
    class Editors(HTMLParser):
        def __init__(self, text):
            super().__init__(); self.current = None; self.codes = {}; self.feed(text)
        def handle_starttag(self, tag, attrs):
            if tag == 'textarea':
                self.current = dict(attrs)['id']; self.codes[self.current] = ''
        def handle_data(self, text):
            if self.current: self.codes[self.current] += text
        def handle_endtag(self, tag):
            if tag == 'textarea': self.current = None
    editors = Editors((root/'playground.html').read_text(encoding='utf-8')).codes
    for name, entry in python['examples'].items():
        assert editors['code-'+name] == (root/entry['url']).read_text(encoding='utf-8')
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
    readable_math = check_readable_chapter(root,documents,pages)
    demo=json.loads((root/'downloads/demonstration-source.json').read_bytes())
    assert demo['source']=='examples/komorebi_demonstrations.py'
    assert demo['url']=='downloads/komorebi_demonstrations.py'
    assert demo['source_revision']==json.loads((root/'build-info.json').read_bytes())['collection_revision']
    code=(root/demo['url']).read_bytes()
    assert len(code)==demo['size'] and hashlib.sha256(code).hexdigest()==demo['sha256']
    from reader_documents import source_lines
    assert source_lines(code.decode('utf-8')) in (root/demo['reader_url']).read_text(encoding='utf-8')
    return dict(status='PASS',html_pages=len(pages),local_links=links,fragments=fragments,
                search_pages=len(index),reading_bundles=len(bundles),checked_bundle_files=zipped_files,
                reading_documents=len(documents['files']),pdfs=pdf_count,readable_math_expressions=readable_math,
                scope='Static navigation, HTML structure and ZIP source identities. Not WCAG certification or mathematical review.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site',type=Path,required=True)
    args=p.parse_args()
    result=inspect_site(args.site)
    (args.site/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
