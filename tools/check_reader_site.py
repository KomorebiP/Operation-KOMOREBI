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
        self.images=[]
        self.iframes=[]
        self.navigation=0;self.menu_buttons=[];self.menu_panels=[]
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
        if tag=='img':self.images.append(a)
        if tag=='iframe':self.iframes.append(a)
        if tag=='nav' and a.get('aria-label')=='Main navigation':self.navigation+=1
        if a.get('id')=='site-menu-toggle':self.menu_buttons.append(a)
        if a.get('id')=='site-menu-panel':self.menu_panels.append(a)


def check_search_targets(index, pages):
    assert len(index)==len({x['url'] for x in index}),'Duplicate search targets'
    for item in index:
        target=urlsplit(item['url'])
        assert not target.scheme and not target.netloc and not target.query,item['url']
        path=unquote(target.path)
        assert path in pages,('Missing search page',item['url'])
        if target.fragment:
            assert unquote(target.fragment) in pages[path].ids,('Missing search fragment',item['url'])


def check_png_image_sizes(root,page,images):
    from reader_documents import png_dimensions
    for image in images:
        path=posixpath.normpath(posixpath.join(posixpath.dirname(page),unquote(urlsplit(image['src']).path)))
        if PurePosixPath(path).suffix.lower()!='.png':
            continue
        width,height=png_dimensions((root/path).read_bytes())
        assert (image.get('width'),image.get('height'))==(str(width),str(height)), (page,'Image dimensions differ from PNG',path)


def check_table_reading_aids(markup,aids):
    from readable_chapters import Chapter
    for identifier,aid in aids.items():
        section=re.search(r'<section id="'+re.escape(identifier)+r'">(.*?)</section>',markup,re.S)
        assert section,('Missing table section',identifier)
        table=re.search(r'<table>(.*?)</table>',section[1],re.S)
        assert table,('Missing table',identifier)
        caption=re.search(r'<caption>(.*?)</caption>',table[1],re.S)
        assert caption and caption[1].strip(),('Missing table caption',identifier)
        if 'caption' in aid:
            assert caption[1]==Chapter('',{}).inline(aid['caption']),('Table caption differs',identifier)
        assert table[1].count('scope="col"')==len(aid['headers']),('Missing column headers',identifier)
        body=re.search(r'<tbody>(.*?)</tbody>',table[1],re.S)
        assert body and body[1].count('<tr>')>0,('Missing table body',identifier)
        assert body[1].count('scope="row"')==body[1].count('<tr>'),('Missing row headers',identifier)


def check_readable_chapter(root, documents, pages):
    from readable_chapters import BOOKS, CHAPTERS, original_math, expand_math, manuscript_macros, chapter_text, validate_monolithic, table_reading_aid
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
        check_png_image_sizes(root,page,pages[page].images)
        main_path=BOOKS[spec['work']]['main']
        main=(root/records[main_path]['file_url']).read_text(encoding='utf-8-sig')
        if BOOKS[spec['work']].get('monolithic'):
            validate_monolithic(main,BOOKS[spec['work']])
            assert (report['start_line'],report['end_line'])==(spec['start_line'],spec['end_line'])
        assert report['macro_source']==main_path
        raw=(root/records[source]['file_url']).read_bytes()
        expressions=original_math(chapter_text(raw.decode('utf-8-sig'),spec))
        if BOOKS[spec['work']].get('custom_reader')=='proof_path':
            from proof_path_reading import source_math
            expressions=source_math(main,spec)
        assert report['source_sha256']==hashlib.sha256(raw).hexdigest()
        assert report['url']==page
        assert report['math_expressions']==len(expressions)
        assert report['math_sequence_sha256']==hashlib.sha256(json.dumps(expressions,ensure_ascii=False).encode()).hexdigest()
        assert report['macros']==manuscript_macros(main,BOOKS[spec['work']].get('required_macros'))
        assert not report['new_proof_review'] and not report['new_lean_execution']
        for node in report['nodes']:
            assert node['id'] in pages[page].ids
            assert 'L'+str(node['line']) in pages[records[source]['url']].ids
        markup=(root/page).read_text(encoding='utf-8')
        aids={}
        config=BOOKS[spec['work']]
        for node in report['nodes']:
            if node['kind'] in {'table','longtable','tabularx'}:
                _,aid=table_reading_aid(config,source,node['id'])
                if aid:aids[node['id']]=aid
        check_table_reading_aids(markup,aids)
        rendered=MathText()
        rendered.feed(markup)
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
        assert page.navigation==1 and len(page.menu_buttons)==len(page.menu_panels)==1,(path,'Main navigation')
        toggle,panel=page.menu_buttons[0],page.menu_panels[0]
        assert toggle.get('aria-controls')=='site-menu-panel' and toggle.get('aria-expanded')=='true',(path,'Navigation disclosure state')
        assert 'hidden' in toggle and 'hidden' not in panel,(path,'Navigation must work without JavaScript')
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
    from browser_python import EXAMPLES
    assert set(python['examples']) == set(EXAMPLES)
    assert python['packages'] == runtime['packages']
    assert python['plotly_js'] == runtime['plotly_js']
    assert python['helper_url'] == 'downloads/komorebi_browser.py'
    assert hashlib.sha256((root/python['helper_url']).read_bytes()).hexdigest() == python['helper_sha256']
    for name, example in python['examples'].items():
        assert example['url'] == 'downloads/python-'+name+'.py'
        assert hashlib.sha256((root/example['url']).read_bytes()).hexdigest() == example['sha256']
        assert example['expected_output'].endswith('\n')
        assert set(example['packages']) <= set(runtime['packages'])
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
    editions=json.loads((root/'editorial-editions.json').read_bytes()) if (root/'editorial-editions.json').is_file() else []
    assert len(editions)==len({item['work'] for item in editions}), 'Duplicate editorial reading edition'
    for edition in editions:
        assert edition['url'] in pages and edition['manuscript_url'] in pages
        assert len(pages[edition['url']].iframes)==1
        assert edition['file_url'].startswith('documents/files/') and edition['file_url'] in files
        assert hashlib.sha256((root/edition['file_url']).read_bytes()).hexdigest()==edition['pdf_sha256']
        assert hashlib.sha256((root/edition['source_archive']).read_bytes()).hexdigest()==edition['source_archive_sha256']
        with zipfile.ZipFile(root/edition['source_archive']) as archive:
            assert set(archive.namelist())=={item['path'] for item in edition['source_files']}
            assert len(archive.namelist())==len(edition['source_files'])
            for item in edition['source_files']:
                assert '..' not in PurePosixPath(item['path']).parts
                assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
        assert any(item['work']==edition['work'] and item['sha256']==edition['original_pdf_sha256'] for item in documents['files'])
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
        if record.get('source'):
            sources={r['repository_path']:r for r in documents['files']}
            assert sources[record['source']]['sha256']==record['source_sha256']
    readable_math = check_readable_chapter(root,documents,pages)
    from reader_atlas import verify as verify_atlas
    atlas = verify_atlas(root,documents,pages)
    from paper_vi_atlas import verify as verify_paper_vi_atlas
    paper_vi_atlas = verify_paper_vi_atlas(root,documents,pages)
    from notation_index import verify as verify_notation
    notation = verify_notation(root,documents,pages)
    demo=json.loads((root/'downloads/demonstration-source.json').read_bytes())
    assert demo['source']=='examples/komorebi_demonstrations.py'
    assert demo['url']=='downloads/komorebi_demonstrations.py'
    assert demo['source_revision']==json.loads((root/'build-info.json').read_bytes())['collection_revision']
    code=(root/demo['url']).read_bytes()
    assert len(code)==demo['size'] and hashlib.sha256(code).hexdigest()==demo['sha256']
    from reader_documents import source_lines
    assert source_lines(code.decode('utf-8')) in (root/demo['reader_url']).read_text(encoding='utf-8')
    from euler_case import verify_site as verify_euler_case
    euler_cases=verify_euler_case(root,pages)
    from factorial_case import verify_site as verify_factorial_case
    factorial_cases=verify_factorial_case(root,pages)
    from wavelet_case import verify_site as verify_wavelet_case
    wavelet_cases=verify_wavelet_case(root,pages)
    from quantum_case import verify_site as verify_quantum_case
    quantum_cases=verify_quantum_case(root,pages)
    from stirling_case import verify_site as verify_stirling_case
    stirling_cases=verify_stirling_case(root,pages)
    from roots_newton_case import verify_site as verify_roots_newton_case
    roots_newton_cases=verify_roots_newton_case(root,pages)
    from download_selector import verify as verify_selector
    download_selection=verify_selector(root,pages)
    from side_reader import check as check_side_reader
    side_reader=check_side_reader(root,pages)
    from special_functions_reading import verify as verify_special_functions
    special_functions=verify_special_functions(root,documents,pages)
    from reading_navigation import verify as verify_reading_navigation
    reading_navigation=verify_reading_navigation(root,pages,documents)
    return dict(status='PASS',html_pages=len(pages),local_links=links,fragments=fragments,euler_worked_examples=euler_cases,factorial_worked_examples=factorial_cases,wavelet_worked_examples=wavelet_cases,stirling_worked_examples=stirling_cases,roots_newton_worked_examples=roots_newton_cases,
                quantum_worked_examples=quantum_cases,search_pages=len(index),reading_bundles=len(bundles),checked_bundle_files=zipped_files,download_selection=download_selection,side_reader=side_reader,
                reading_documents=len(documents['files']),pdfs=pdf_count,editorial_editions=len(editions),readable_math_expressions=readable_math,atlas=atlas,paper_vi_atlas=paper_vi_atlas,notation=notation,special_functions=special_functions,reading_navigation=reading_navigation,
                scope='Static navigation, HTML structure and ZIP source identities. Not WCAG certification or mathematical review.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site',type=Path,required=True)
    args=p.parse_args()
    result=inspect_site(args.site)
    (args.site/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
