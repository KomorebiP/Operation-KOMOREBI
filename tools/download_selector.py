"""Publish exact, individually selectable reader files and their provenance."""
import hashlib
import html
import json
from pathlib import PurePosixPath

SCOPE = 'Selected files from the reading website. Dependencies may be missing. This is not a complete Lean or software build.'


def category(path):
    suffix=PurePosixPath(path).suffix.lower()
    if suffix=='.pdf':return 'PDFs'
    if suffix in {'.tex','.bib','.sty','.cls'}:return 'Manuscript sources'
    if suffix=='.lean':return 'Lean sources'
    if suffix in {'.py','.c','.h','.cpp','.js','.sh','.ipynb'}:return 'Code'
    return 'Guides and records'


def is_notice(path):
    return PurePosixPath(path).name.lower().startswith(('license','copying','notice'))


def build(site):
    from build_reader_site import blob, document_url, safe_path
    files={}
    defaults={(r['work'],f['repository_path']) for r in site.bundle_records for f in r['files']}
    works=[dict(id=c['id'],title=site.components[c['id']]['title'],
                url='collection/works/'+c['id']+'.html') for c in site.registry['components']]
    def add(work,path,source,raw,reader_url=None,required=False,kind=None):
        safe_path(path)
        archive_path=(work+'/' if work else 'collection-notices/')+path
        identifier=archive_path
        if identifier in files:return
        url='documents/files/'+blob(raw)+'/'+PurePosixPath(path).name
        target=site.output/url
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==raw,url
        else:target.write_bytes(raw)
        files[identifier]=dict(id=identifier,work=work,path=path,archive_path=archive_path,
            repository_path=source,url=url,reader_url=reader_url,size=len(raw),
            sha256=hashlib.sha256(raw).hexdigest(),category=kind or category(path),
            required=required,reading=(work,source) in defaults)
    for record in site.reader.records.values():
        add(record['work'],record['path'],record['repository_path'],site.read_source(record),
            record['url'],is_notice(record['path']))
    for bundle in site.bundle_records:
        for record in bundle['files']:
            add(bundle['work'],record['path'],record['repository_path'],site.read_source(record),
                required=is_notice(record['path']))
    for work,edition in site.editorial_editions.items():
        for record in edition['source_files']:
            path=record['path']
            raw=(site.root/path).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==record['sha256'],path
            add(work,'reading-edition/'+path,path,raw,edition['url'],is_notice(path))
    for topic in site.reader.learning.get('learning_topics',[]):
        for work in topic['works']:
            path=topic['example']
            add(work,'worked-examples/'+PurePosixPath(path).name,path,(site.root/path).read_bytes(),
                document_url('collection',path),kind='Worked examples')
    for work,assessment in site.assessments.items():
        if work not in {w['id'] for w in works} or not assessment.get('worked_example'):continue
        binding=assessment['worked_example']
        raw=(site.root/binding['record']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==binding['sha256']
        for record in json.loads(raw)['files']:
            path=record['path']
            data=(site.root/path).read_bytes()
            assert hashlib.sha256(data).hexdigest()==record['sha256'],path
            add(work,'worked-examples/'+path,path,data,kind='Worked examples')
    for path in ('LICENSE.md','CITATION.md','docs/PROJECT_STATEMENT.md'):
        add(None,PurePosixPath(path).name,path,(site.root/path).read_bytes(),required=True)
    catalog=dict(version=1,source_revision=site.revision,scope=SCOPE,works=works,
                 files=sorted(files.values(),key=lambda f:f['id']))
    site.write('downloads/selection.json',json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    return catalog


def interface(site):
    e=html.escape
    options=''.join('<option value="'+e(c['id'])+'">'+e(site.components[c['id']]['title'])+'</option>'
                    for c in site.registry['components'])
    return '''<section class="zip-builder" id="build-a-zip" aria-labelledby="zip-heading">
<h2 id="zip-heading">Build your own ZIP</h2>
<p>Combine files from several works. Start with a reading selection or PDFs, then choose individual files.</p>
<p class="status">Available reading files, manuscript sources, Lean files, code and worked examples. A selection may need other files to compile or run. <a href="collection/DOWNLOADS.html#obtain-a-full-component">Get complete sources</a>.</p>
<p id="zip-load-status" role="status">Use the custom selector, or choose a ready-made ZIP below.</p>
<form id="zip-form" hidden data-index="downloads/selection.json?v='''+site.revision+'''" data-worker="assets/download-worker.js?v='''+site.revision+'''" data-revision="'''+site.revision+'''">
<fieldset id="zip-controls"><legend>Choose your files</legend>
<div class="zip-picker"><div><label for="zip-work">Work</label><select id="zip-work"><option value="">Choose a work</option>'''+options+'''</select></div>
<div><label for="zip-preset">Start with</label><select id="zip-preset"><option value="reading">Reading selection</option><option value="pdf">PDFs only</option><option value="all">All available files</option></select></div>
<button id="zip-add" type="button">Add work</button></div>
<button id="zip-core-papers" type="button" class="zip-secondary">Add all core papers</button>
<p class="status">You can add more works and change every selection below. License notices are included automatically.</p>
<div id="zip-works"></div><button id="zip-clear" type="button" class="zip-secondary">Clear selection</button>
</fieldset>
<div class="zip-checkout"><p id="zip-summary" role="status" aria-live="polite" aria-atomic="true">No files selected.</p>
<p class="status">Up to 200 MiB of source files per ZIP. The ZIP is prepared in your browser. Selected files are fetched from this site.</p>
<button id="zip-build" type="submit" disabled>Prepare ZIP</button><button id="zip-cancel" type="button" hidden>Cancel</button>
<a id="zip-save" class="button" hidden download>Save ZIP</a>
<p id="zip-progress" role="status" aria-live="polite" aria-atomic="true"></p>
</div></form><noscript><p>The custom selector needs JavaScript. The ready-made ZIPs below remain available.</p></noscript>
</section>'''+''.join('<script defer src="assets/'+name+'?v='+site.revision+'"></script>' for name in ('download-core.js','download-selector.js'))


def verify(root,pages):
    catalog=json.loads((root/'downloads/selection.json').read_bytes())
    assert catalog['version']==1
    assert catalog['source_revision']==json.loads((root/'build-info.json').read_bytes())['collection_revision']
    works={w['id'] for w in catalog['works']}
    ids=set();paths=set()
    from build_reader_site import safe_path
    for record in catalog['files']:
        assert record['id'] not in ids and record['archive_path'] not in paths
        ids.add(record['id']);paths.add(record['archive_path'])
        safe_path(record['archive_path']);safe_path(record['url'])
        assert record['work'] is None or record['work'] in works
        assert record['url'].startswith('documents/files/')
        raw=(root/record['url']).read_bytes()
        assert len(raw)==record['size'] and hashlib.sha256(raw).hexdigest()==record['sha256']
        if record['reader_url']:assert record['reader_url'] in pages
    assert {r['work'] for r in catalog['files'] if not r['required']}==works
    assert len([r for r in catalog['files'] if r['work'] is None and r['required']])==3
    vendor=root/'assets/vendor'
    for record in json.loads((vendor/'fflate-SOURCE.json').read_bytes())['files']:
        assert hashlib.sha256((vendor/record['path']).read_bytes()).hexdigest()==record['sha256']
    return dict(works=len(works),files=len(catalog['files']),source_bytes=sum(r['size'] for r in catalog['files']))
