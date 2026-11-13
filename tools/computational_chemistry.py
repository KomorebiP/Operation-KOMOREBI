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
OVERVIEW='collection/COMPUTATIONAL_CHEMISTRY.html'
ASSETS='assets/chemistry/stage14/'
PAGES={
    'chemistry_stage14/NORMAL_FORM.md':('normal-form.html','The 21-parameter molecular normal form'),
    'chemistry_stage14/RECOVERY_THEOREM.md':('three-queries.html','Exactly three action queries'),
    'chemistry_stage14/ROBUST_SPIN_COMPARISON.md':('spin-comparison.html','Information beyond total spin'),
    'chemistry_stage14/FROZEN_CORE_CONTRACT.md':('frozen-core.html','The declared H10 frozen-core model'),
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


def publish(site):
    import markdown
    from build_reader_site import Rewriter,math_fences,page_contents
    if not re.fullmatch(r'[0-9a-f]{40}',site.revision):raise ValueError('Full chemistry source revision required')
    record,files=load(site.root)
    archive=site.output/ASSETS/'Stage14_Fixed_Spin_Recovery.zip';archive.parent.mkdir(parents=True,exist_ok=True)
    archive.write_bytes((site.root/record['archive']).read_bytes())
    for name,raw in files.items():
        target=site.output/ASSETS/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    site.write(ASSETS+'export.json',json.dumps(record,indent=2)+'\n')
    base='read/computational-chemistry/'
    for source,(name,title) in PAGES.items():
        path=base+name
        def resolve(target,image=False):
            parts=urlsplit(target)
            if parts.scheme or parts.netloc:return target
            if not parts.path:return target
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(source),parts.path))
            if resolved in PAGES:destination=base+PAGES[resolved][0]
            elif resolved in files:destination=ASSETS+resolved
            else:raise ValueError('Unpublished chemistry reference: '+target)
            return site.rel(destination,path)+('#'+parts.fragment if parts.fragment else '')
        text=files[source].decode('utf-8')
        rendered=markdown.markdown(text,extensions=['tables','fenced_code','toc','pymdownx.arithmatex'],extension_configs={'pymdownx.arithmatex':{'generic':True}})
        rewritten=Rewriter(resolve);rewritten.feed(math_fences(rendered));body=''.join(rewritten.out)
        contents=page_contents(body);body=re.sub(r'(</h1>)',lambda match:match[1]+contents,body,count=1)
        nav='<nav class="document-routes" aria-label="Chemistry checkpoint"><a href="'+site.rel(OVERVIEW,path)+'">Research overview</a>'
        for _,(target,label) in PAGES.items():nav+='<a href="'+target+'"'+(' aria-current="page"' if target==name else '')+'>'+html.escape(label)+'</a>'
        nav+='</nav>'
        provenance='<details><summary>Source identity and download</summary><p>This reading renders the retained export member <code>'+html.escape(source)+'</code>. The replay export retains the declared distinction between the original fixture container and its selected-array view.</p><p><a href="'+site.rel(ASSETS+source,path)+'">Read this member as source</a> · <a href="'+site.rel(ASSETS+'Stage14_Fixed_Spin_Recovery.zip',path)+'">Download the replay bundle</a></p><pre tabindex="0" role="group" aria-label="Source SHA256; scroll horizontally if needed"><code>'+record['files'][source]['sha256']+'</code></pre></details>'
        site.page(path,title,nav+'<article>'+body+provenance+'</article>','https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/'+record['archive'])
        plain=html.unescape(re.sub(r'<[^>]+>',' ',rendered))
        site.search.append(dict(title=title,group='Physics and chemistry',kind='Research checkpoint',url=path,work_ids=[],text=re.sub(r'\s+',' ',plain)[:50000]))
    return {'archive_sha256':record['sha256'],'export_files':len(files),'reading_pages':len(PAGES),'new_scientific_execution':False}
