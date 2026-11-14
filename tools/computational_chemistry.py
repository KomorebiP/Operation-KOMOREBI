"""Publish the hash-bound fixed-spin chemistry checkpoint and focused replay."""
from __future__ import annotations
from fractions import Fraction
import hashlib
import html
import json
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import quote,urlsplit
import zipfile

MANIFEST='manifests/chemistry-stage14.json'
EDITION='manifests/chemistry-reading-edition.json'
VALIDATION='manifests/chemistry-stage14-validation.json'
OVERVIEW='collection/COMPUTATIONAL_CHEMISTRY.html'
ASSETS='assets/chemistry/stage14/'
READING_ASSETS='assets/chemistry/reading-edition/'
VALIDATION_ASSETS='assets/chemistry/validation-v1/'
PAGES={
    'reading-edition/notation.md':('notation.html','Notation, units and reading routes'),
    'chemistry_stage14/NORMAL_FORM.md':('normal-form.html','The 21-parameter molecular normal form'),
    'chemistry_stage14/RECOVERY_THEOREM.md':('three-queries.html','Exactly three action queries'),
    'chemistry_stage14/ROBUST_SPIN_COMPARISON.md':('spin-comparison.html','Information beyond total spin'),
    'chemistry_stage14/FROZEN_CORE_CONTRACT.md':('frozen-core.html','The declared H10 frozen-core model'),
    'reading-edition/model-error.md':('model-error.html','A conditional full-model error bound'),
    'chemistry_stage14/PROOF_AUDIT.md':('review.html','Proof self-review and its scope'),
    'chemistry_stage14/LITERATURE.md':('literature.html','Sources and unresolved priority'),
    'README.md':('reproduce.html','Replay the fixed-spin chemistry checkpoint'),
}


def digest(raw):return hashlib.sha256(raw).hexdigest()


def load(root):
    record=json.loads((root/MANIFEST).read_bytes());raw=(root/record['archive']).read_bytes()
    if digest(raw)!=record['sha256'] or len(raw)!=record['bytes']:raise ValueError('Chemistry archive identity mismatch')
    prefix=record['prefix'];files={}
    with zipfile.ZipFile(root/record['archive']) as archive:
        infos=archive.infolist()
        if len(infos)!=record['file_count'] or len({item.filename for item in infos})!=len(infos):raise ValueError('Unexpected chemistry archive entries')
        if sum(item.file_size for item in infos)>2_000_000:raise ValueError('Unexpected chemistry archive size')
        for item in infos:
            path=PurePosixPath(item.filename)
            if item.is_dir() or path.is_absolute() or '..' in path.parts or '\\' in item.filename or ':' in item.filename or not item.filename.startswith(prefix) or (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe chemistry archive entry')
            name=item.filename[len(prefix):];content=archive.read(item)
            expected=record['files'].get(name)
            if expected is None or digest(content)!=expected['sha256'] or len(content)!=expected['bytes']:raise ValueError('Chemistry member identity mismatch: '+name)
            files[name]=content
    if set(files)!=set(record['files']):raise ValueError('Chemistry export coverage mismatch')
    checksums={}
    for line in files['PUBLIC_SHA256SUMS'].decode().splitlines():
        match=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
        if not match or match[2] in checksums:raise ValueError('Invalid chemistry checksum index')
        checksums[match[2]]=match[1]
    if set(checksums)!=set(files)-{'PUBLIC_SHA256SUMS'} or any(digest(files[name])!=value for name,value in checksums.items()):raise ValueError('Chemistry checksum coverage mismatch')
    exact=json.loads(files['chemistry_stage14/exact-audit-001/checks.json'])
    molecular=json.loads(files['chemistry_stage14/molecular-audit-001/qualification.json'])
    certificate=json.loads(files['chemistry_stage14/molecular-audit-001/molecular_certificate.json'])
    toy=json.loads(files['chemistry_stage14/exact-audit-001/example_certificate.json'])
    if exact['status']!='passed' or exact['check_count']!=82 or exact['summed_cases']!=260:raise ValueError('Unexpected chemistry audit scope')
    if molecular['status']!='passed' or not molecular['projection_equal_exactly'] or not certificate['all_compatible_positive_integral']:raise ValueError('Unexpected molecular qualification')
    radius=Fraction(certificate['response_radius_rational_upper'])
    if not Fraction(molecular['response_error_squared_exact'])<=radius**2 or not radius<Fraction(9314,10**14):raise ValueError('Molecular saved response bound failed')
    if not Fraction(toy['response_radius_rational_upper'])<Fraction(exact['pi_scaled_ldos_gap']):raise ValueError('Spin-preserving separation failed')
    fixture=json.loads(files['FIXTURE_VIEW.json'])
    if fixture!=record['fixture_view'] or digest(files['chemistry_checkpoint/molecular_fixtures/h10_1.4.npz'])!=fixture['view_container_sha256'] or molecular['fixture_sha256']!=fixture['original_container_sha256']:raise ValueError('Fixture-view provenance mismatch')
    for cert_name,input_name in [('chemistry_stage14/exact-audit-001/example_certificate.json','chemistry_stage14/example_cache.json'),('chemistry_stage14/molecular-audit-001/molecular_certificate.json','chemistry_stage14/molecular-audit-001/molecular_cache.json')]:
        if json.loads(files[cert_name])['input_sha256']!=digest(files[input_name]):raise ValueError('Saved chemistry input link mismatch')
    return record,files


def load_edition(root, original=None):
    original=original if original is not None else load(root)[0]
    record=json.loads((root/EDITION).read_bytes())
    if record['based_on_archive_sha256']!=original['sha256']:raise ValueError('Reading edition has a different source archive')
    if len(record['pages'])!=len(PAGES) or {page['key'] for page in record['pages']}!=set(PAGES):raise ValueError('Reading edition page coverage mismatch')
    for page in record['pages']:
        raw=(root/page['source']).read_bytes()
        if digest(raw)!=page['sha256']:raise ValueError('Reading edition source changed: '+page['source'])
        if page.get('original_member'):
            if page['original_sha256']!=original['files'][page['original_member']]['sha256']:raise ValueError('Reading edition source correspondence changed')
    if digest((root/record['overview']['source']).read_bytes())!=record['overview']['sha256']:raise ValueError('Chemistry overview differs from its reviewed edition')
    return record


def caption_tables(rendered, captions):
    count=len(re.findall(r'<table\b',rendered))
    if count!=len(captions):raise ValueError('Chemistry table-caption coverage mismatch')
    labels=iter(captions)
    return re.sub(r'<table\b[^>]*>',lambda match:match[0]+'<caption>'+html.escape(next(labels))+'</caption>',rendered)


def overview_rendering(site, rendered):
    return caption_tables(rendered,load_edition(site.root)['overview']['table_captions'])


def load_validation(root):
    record=json.loads((root/VALIDATION).read_bytes());raw=(root/record['archive']).read_bytes()
    if record['based_on_archive_sha256']!=json.loads((root/MANIFEST).read_bytes())['sha256']:raise ValueError('Validated replay historical-source mismatch')
    if set(record['validation_runs'])!={'validation/'+name+'-001' for name in ['exact','molecular','extensions']} or len(record['validation_runs'])!=3:raise ValueError('Validated run coverage mismatch')
    if digest(raw)!=record['sha256'] or len(raw)!=record['bytes']:raise ValueError('Validated replay archive identity mismatch')
    files={}
    with zipfile.ZipFile(root/record['archive']) as archive:
        infos=archive.infolist()
        if len(infos)!=record['file_count'] or len({x.filename for x in infos})!=len(infos) or sum(x.file_size for x in infos)>3_000_000:raise ValueError('Validated replay coverage/size mismatch')
        for item in infos:
            path=PurePosixPath(item.filename)
            if item.is_dir() or path.is_absolute() or '..' in path.parts or '\\' in item.filename or ':' in item.filename or not item.filename.startswith(record['prefix']) or (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe validated replay member')
            name=item.filename[len(record['prefix']):];content=archive.read(item);expected=record['files'].get(name)
            if expected is None or digest(content)!=expected['sha256'] or len(content)!=expected['bytes']:raise ValueError('Validated replay member changed: '+name)
            files[name]=content
    if set(files)!=set(record['files']):raise ValueError('Validated replay member-set mismatch')
    if json.loads(files['BUNDLE_CONTENTS.json'])['files']!=sorted(files):raise ValueError('Validated bundle contents mismatch')
    sums={}
    for line in files['VALIDATION_SHA256SUMS'].decode().splitlines():
        match=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
        if not match or match[2] in sums:raise ValueError('Invalid validation checksum index')
        sums[match[2]]=match[1]
    if set(sums)!=set(files)-{'VALIDATION_SHA256SUMS'} or any(digest(files[name])!=value for name,value in sums.items()):raise ValueError('Validated replay checksum coverage mismatch')
    for folder in record['validation_runs']:
        manifest=json.loads(files[folder+'/manifest.json'])
        if manifest['schema_version']!=2 or manifest['run']['status']!='completed':raise ValueError('Unsuccessful public validation run')
        if set(manifest['execution_artifacts'])!={x['path'] for x in manifest['input_artifacts']}:raise ValueError('Validation input declaration mismatch')
        for item in manifest['input_artifacts']:
            if item['sha256']!=item['sha256_after'] or digest(files[item['path']])!=item['sha256']:raise ValueError('Validation input hash mismatch')
        for item in manifest['outputs']:
            if digest(files[item['path']])!=item['sha256']:raise ValueError('Validation output hash mismatch')
    qual=json.loads(files['validation/molecular-001/qualification.json']);cert=json.loads(files['validation/molecular-001/molecular_certificate.json'])
    radius=Fraction(cert['response_radius_rational_upper'])
    if Fraction(qual['response_error_squared_exact'])>radius**2 or cert['input_sha256']!=digest(files['validation/molecular-001/molecular_cache.json']):raise ValueError('Validated molecular certificate failed')
    if qual['fixture_sha256']!=digest(files['chemistry_checkpoint/molecular_fixtures/h10_1.4.npz']):raise ValueError('Validated fixture identity mismatch')
    extension=json.loads(files['validation/extensions-001/checks.json'])
    if extension['status']!='passed' or extension['check_count']!=62 or extension['conditional_truncation_grid_cases']!=108:raise ValueError('Reading-extension check scope mismatch')
    return record,files


def publish(site):
    import markdown
    from build_reader_site import Rewriter,math_fences,page_contents
    if not re.fullmatch(r'[0-9a-f]{40}',site.revision):raise ValueError('Full chemistry source revision required')
    record,files=load(site.root);edition=load_edition(site.root,record);validated,validated_files=load_validation(site.root)
    archive=site.output/ASSETS/'Stage14_Fixed_Spin_Recovery.zip';archive.parent.mkdir(parents=True,exist_ok=True)
    archive.write_bytes((site.root/record['archive']).read_bytes())
    for name,raw in files.items():
        target=site.output/ASSETS/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    site.write(ASSETS+'export.json',json.dumps(record,indent=2)+'\n')
    for name,raw in validated_files.items():
        target=site.output/VALIDATION_ASSETS/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    target=site.output/VALIDATION_ASSETS/'Stage14_Validated_Replay.zip';target.write_bytes((site.root/validated['archive']).read_bytes())
    site.write(VALIDATION_ASSETS+'export.json',json.dumps(validated,indent=2)+'\n')
    site.write(READING_ASSETS+'manifest.json',json.dumps(edition,indent=2)+'\n')
    base='read/computational-chemistry/'
    edition_pages={page['key']:page for page in edition['pages']}
    filenames={PurePosixPath(page['source']).name:base+PAGES[page['key']][0] for page in edition['pages']}
    order=list(PAGES)
    for source,(name,title) in PAGES.items():
        page_record=edition_pages[source];source_file=page_record['source'];source_name=PurePosixPath(source_file).name
        path=base+name
        def resolve(target,image=False):
            parts=urlsplit(target)
            if parts.scheme or parts.netloc:return target
            if not parts.path:return target
            resolved=posixpath.normpath(parts.path)
            if resolved in filenames:destination=filenames[resolved]
            elif resolved in validated_files:destination=VALIDATION_ASSETS+resolved
            elif resolved in files:destination=ASSETS+resolved
            else:raise ValueError('Unpublished chemistry reference: '+target)
            return site.rel(destination,path)+('#'+parts.fragment if parts.fragment else '')
        text=(site.root/source_file).read_text(encoding='utf-8')
        raw_source=site.output/READING_ASSETS/source_name;raw_source.parent.mkdir(parents=True,exist_ok=True);raw_source.write_bytes((site.root/source_file).read_bytes())
        rendered=markdown.markdown(text,extensions=['tables','fenced_code','toc','pymdownx.arithmatex'],extension_configs={'pymdownx.arithmatex':{'generic':True}})
        rendered=caption_tables(math_fences(rendered),page_record['table_captions'])
        rewritten=Rewriter(resolve);rewritten.feed(rendered);body=''.join(rewritten.out)
        contents=page_contents(body);body=re.sub(r'(</h1>)',lambda match:match[1]+contents,body,count=1)
        nav='<details class="chemistry-reading-nav"><summary>Explore the chemistry notes</summary><nav aria-label="Chemistry checkpoint"><ul><li><a href="'+site.rel(OVERVIEW,path)+'">Research overview</a></li>'
        for _,(target,label) in PAGES.items():nav+='<li><a href="'+target+'"'+(' aria-current="page"' if target==name else '')+'>'+html.escape(label)+'</a></li>'
        nav+='</ul></nav></details>'
        provenance='<details class="chemistry-provenance"><summary>Source identity and downloads</summary><p>This is a reviewed reading edition with corrected prose, explicit derivations and source correspondence. It is distinct from the retained original checkpoint.</p><p><a href="'+site.rel(READING_ASSETS+source_name,path)+'">Read the current Markdown source</a> · <a href="'+site.rel(READING_ASSETS+'manifest.json',path)+'">Edition correspondence and hashes</a> · <a href="'+site.rel(VALIDATION_ASSETS+'Stage14_Validated_Replay.zip',path)+'">Download the validated replay bundle</a></p>'
        if page_record.get('original_member'):provenance+='<p><a href="'+site.rel(ASSETS+page_record['original_member'],path)+'">Read the original checkpoint member</a>. Its bytes remain unchanged.</p>'
        provenance+='<pre tabindex="0" role="group" aria-label="Current source SHA256; scroll horizontally if needed"><code>'+page_record['sha256']+'</code></pre></details>'
        index=order.index(source);pagination='<nav class="chemistry-pagination" aria-label="Previous and next chemistry notes">'
        if index:target,label=PAGES[order[index-1]];pagination+='<a rel="prev" href="'+target+'">Previous: '+html.escape(label)+'</a>'
        if index+1<len(order):target,label=PAGES[order[index+1]];pagination+='<a rel="next" href="'+target+'">Next: '+html.escape(label)+'</a>'
        pagination+='</nav>'
        site.page(path,title,nav+'<article class="chemistry-note">'+body+provenance+'</article>'+pagination,'https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/'+quote(source_file,safe='/'))
        plain=html.unescape(re.sub(r'<[^>]+>',' ',rendered))
        kind='Written proofs' if name in {'normal-form.html','three-queries.html','spin-comparison.html','model-error.html'} else 'Guides'
        site.search.append(dict(title=title,group='Collection',kind=kind,url=path,work_ids=[],text=re.sub(r'\s+',' ',plain)[:50000]))
    return {'archive_sha256':record['sha256'],'export_files':len(files),'validated_files':len(validated_files),'reading_pages':len(PAGES),'new_scientific_execution':False}
