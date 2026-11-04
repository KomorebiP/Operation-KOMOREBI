"""Publish the separately identified, rebuilt 97-chapter MNR edition.

The source payload is stored in bounded binary parts. The reader build joins
and authenticates them into ordinary, single-file PDF and ZIP downloads.
No imported manuscript, formal result map, or historical receipt is replaced.
"""
from __future__ import annotations
import hashlib
import html
import json
from pathlib import Path
import re
import zipfile
from io import BytesIO

CORE='monographs-machine-native-reasoning'
WORK='research-machine-native-reasoning-wider'
PAGE='read/'+WORK+'/reconstructed-edition.html'
MANIFEST='publication/machine-native-reasoning-reconstructed/2026-11-04/PUBLICATION.json'
RECORD='documents/machine-native-reasoning-reconstructed.json'
PDF_SHA256='65a0a736e3422102f83bfc96883dcb81d2a7dacc42663c78e002718ebb7278db'
SOURCE_SHA256='14e635a4e910ab3062e5618b084841eff2e0504f048130cfd336985a7c94ef25'
BOOK=PAGE.replace('reconstructed-edition.html','book.html')
SCRIPT='assets/machine-native-reasoning-download.mjs'

def digest(raw):return hashlib.sha256(raw).hexdigest()

def load_manifest(root):
    data=json.loads((Path(root)/MANIFEST).read_bytes())
    if data.get('schema')!=1 or data.get('edition')!='reconstructed-editorial-2026-11-04':
        raise ValueError('Unknown MNR reconstructed edition')
    if data['pages']!=977 or data['parts']!=13 or set(data['assets'])!={'pdf','source'}:
        raise ValueError('Changed MNR edition inventory')
    chapters=data['chapters']
    if [c['number'] for c in chapters]!=list(range(1,98)):
        raise ValueError('The expanded edition must contain all 97 chapters in order')
    pages=[c['physical_page'] for c in chapters]
    if pages!=sorted(set(pages)) or not all(1<=p<=977 for p in pages):
        raise ValueError('Invalid physical PDF chapter pages')
    if len(dict.fromkeys(c['part'] for c in chapters))!=13:
        raise ValueError('The expanded edition must retain thirteen parts')
    if data['assets']['pdf']['sha256']!=PDF_SHA256 or data['assets']['source']['sha256']!=SOURCE_SHA256:
        raise ValueError('Reconstruction differs from the admitted artifacts')
    return data

def artifact_bytes(root,asset):
    from build_reader_site import safe_path
    root=Path(root).resolve();parts=[];seen=set()
    for entry in asset['parts']:
        path=safe_path(entry['path'])
        if not path.startswith(str(Path(MANIFEST).parent.as_posix())+'/') or path in seen:
            raise ValueError('Unexpected or duplicate MNR artifact part')
        seen.add(path);target=root/path
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('MNR artifact part escapes the checkout')
        raw=target.read_bytes()
        if len(raw)!=entry['bytes'] or digest(raw)!=entry['sha256']:
            raise ValueError('MNR artifact part changed: '+path)
        parts.append(raw)
    raw=b''.join(parts)
    if len(raw)!=asset['bytes'] or digest(raw)!=asset['sha256']:
        raise ValueError('Reassembled MNR artifact differs from its verified release')
    return raw

def edition_link(site,page):
    return '<a href="'+html.escape(site.rel(PAGE,page),quote=True)+'">Read the reconstructed 97-chapter book</a>'

def teaser(site,page):
    return ('<aside class="reading-note" aria-label="Expanded Machine-Native Reasoning edition">'
      '<p><strong>The expanded book is available.</strong> '+edition_link(site,page)+
      ': 977 pages, thirteen parts, and a complete editable TeX package. '
      'Its component-specific assurance remains separate from the accepted 27-result core.</p></aside>')

def publish(site):
    from build_reader_site import blob,github,REPOSITORY
    data=load_manifest(site.root)
    pdf=artifact_bytes(site.root,data['assets']['pdf'])
    source=artifact_bytes(site.root,data['assets']['source'])
    with zipfile.ZipFile(BytesIO(source)) as z:
        if z.testzip():raise ValueError('MNR source ZIP CRC failed')
        files=json.loads(z.read('MANIFEST.json'))['files']
        if set(z.namelist())!={r['path'] for r in files}|{'MANIFEST.json'}:
            raise ValueError('MNR source ZIP inventory differs')
        if any(digest(z.read(r['path']))!=r['sha256'] for r in files):
            raise ValueError('MNR source ZIP payload changed')
    record=dict(work=WORK,pdf_reader=BOOK,pdf_sha256=PDF_SHA256,pages=977,url=PAGE,
      source_archive=BOOK+'?download=source',source_archive_sha256=SOURCE_SHA256,
      chapters=data['chapters'],assets=data['assets'],revision=site.revision,
      delivery='verified-browser-download-from-pinned-github-parts',
      delivery_script=SCRIPT,delivery_script_sha256=digest((site.root/'website'/SCRIPT).read_bytes()),
      publication_manifest=MANIFEST,publication_manifest_sha256=digest((site.root/MANIFEST).read_bytes()),
      original_tex_archive_recovered=False,new_lean_execution=False,new_proof_review=False)
    site.write(RECORD,json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    script=site.output/SCRIPT;script.parent.mkdir(parents=True,exist_ok=True)
    script.write_bytes((site.root/'website'/SCRIPT).read_bytes())
    e=html.escape
    def link(label,url,button=False):
        return '<a'+(' class="button"' if button else '')+' href="'+e(site.rel(url,PAGE),quote=True)+'">'+e(label)+'</a>'
    viewer=site.rel(BOOK,PAGE)
    body='<p class="eyebrow">Machine-Native Reasoning · Reconstructed editorial edition</p><h1>Machine-Native Reasoning</h1>'
    body+='<p>Read the expanded book on representation, inference, discovery, and self-correction: <strong>97 chapters in thirteen parts, 977 pages</strong>. This 4 November 2026 edition was rebuilt as editable TeX from retained component manuscripts and the recovered reading PDF.</p>'
    body+='<p><a class="button" href="'+e(viewer,quote=True)+'">Open the complete book</a> '+link('Download PDF',BOOK+'?download=pdf')+' · '+link('Download editable TeX and verification records (30.6 MB)',BOOK+'?download=source')+'</p>'
    body+='<p>'+link('Read the accepted nine-chapter core','read/'+CORE+'/index.html')+' · '+link('Inspect the core’s formal scope','read/'+CORE+'/formal-scope.html')+' · '+link('Earlier continuation and its records','collection/works/'+WORK+'.html')+'</p>'
    body+='<h2 id="reading-scope">Edition and assurance</h2><p>'+e(data['selected_core'])+' '+e(data['assurance'])+'</p>'
    body+='<p>The editable reconstruction is complete and builds without the missing historical TeX archive. It is a new typeset edition; its pagination and editorial text differ from the recovered 1,155-page reading copy. Use the PDF reader’s search for the full book text.</p>'
    body+='<h2 id="chapters">Contents: all 97 chapters</h2><p>Choose a part, then a chapter. Each chapter opens at its physical page in the book’s PDF reader.</p>'
    previous=None
    for chapter in data['chapters']:
        part=chapter['part']
        if part!=previous:
            if previous is not None:body+='</ol></details>'
            number=part.split(' ',1)[0].lower()
            body+='<details id="part-'+number+'"'+(' open' if previous is None else '')+'><summary>'+e(part)+'</summary><ol start="'+str(chapter['number'])+'">'
            previous=part
        target=site.rel(BOOK,PAGE)+'#page='+str(chapter['physical_page'])
        body+='<li id="chapter-'+str(chapter['number'])+'"><a href="'+e(target,quote=True)+'">'+e(chapter['title'])+'</a> <span class="muted">(printed page '+e(chapter['printed_page'])+')</span></li>'
        site.search.append(dict(title='Machine-Native Reasoning / Chapter '+str(chapter['number'])+'. '+chapter['title'],
          group='Collection',kind='Papers and source',work_ids=[WORK],url=PAGE+'#chapter-'+str(chapter['number']),
          text=chapter['title']+' '+part+' Expanded reconstructed monograph, PDF chapter and complete editable TeX source.'))
    body+='</ol></details><h2 id="verification">Build and source checks</h2>'
    body+='<p>The source package regenerates the active TeX exactly. A clean build reproduced all 977 pages in text, page geometry, content streams, and rendered pixels at 36 dpi, with matching outline trees. Page-boundary checks and all internal PDF links passed. These are reproduction and production checks, not an independent proof audit.</p>'
    body+='<p>'+link('Download the publication record',RECORD)+' · <a href="'+e(github(REPOSITORY,site.revision,MANIFEST),quote=True)+'">Source identities and full chapter map on GitHub</a></p>'
    body+='<details><summary>Artifact checksums</summary><dl><dt>PDF SHA-256</dt><dd><code>'+PDF_SHA256+'</code></dd><dt>Editable source ZIP SHA-256</dt><dd><code>'+SOURCE_SHA256+'</code></dd></dl></details>'
    site.page(PAGE,'Machine-Native Reasoning: the reconstructed 97-chapter book',body,github(REPOSITORY,site.revision,MANIFEST))
    site.search.append(dict(title='Machine-Native Reasoning / Expanded book and editable source',group='Collection',
      kind='Papers and source',work_ids=[WORK],url=PAGE,
      text='Machine Native Reasoning expanded reconstructed editorial edition 97 chapters 977 pages thirteen parts editable TeX source PDF component mathematical assurance reproducible book'))
    from urllib.parse import quote
    from fetch_pdf_runtime import RUNTIME_ID
    pdf_viewer=site.rel('assets/pdfjs/web/viewer.html',BOOK)+'?work='+quote(site.rel('collection/works/'+WORK+'.html','assets/pdfjs/web/viewer.html'),safe='')+'&v='+RUNTIME_ID
    reader_body='<h1>Machine-Native Reasoning</h1><p>'+link('All 97 chapters',PAGE)+'</p>'
    reader_body+='<section id="mnr-delivery" data-record="'+e(site.rel(RECORD,BOOK),quote=True)+'" data-viewer="'+e(pdf_viewer,quote=True)+'">'
    reader_body+='<p><button type="button" id="mnr-pdf">Download PDF (5.3 MB)</button> <button type="button" id="mnr-source">Download editable TeX (30.6 MB)</button> <button type="button" id="mnr-cancel" hidden>Cancel</button> <button type="button" id="mnr-retry" hidden>Retry</button></p>'
    reader_body+='<p id="mnr-status" role="status" aria-live="polite">Loading the book…</p><p><a id="mnr-save" class="button" hidden>Save verified download</a></p><div id="mnr-viewer"></div>'
    reader_body+='<noscript><p>The PDF reader and verified downloads require JavaScript. '+link('Return to the contents and artifact records',PAGE)+'</p></noscript></section>'
    reader_body+='<script type="module" src="'+e(site.rel(SCRIPT,BOOK),quote=True)+'?v='+record['delivery_script_sha256'][:12]+'"></script>'
    site.page(BOOK,'Machine-Native Reasoning: PDF reader and downloads',reader_body,github(REPOSITORY,site.revision,MANIFEST))
    return record

def verify(root):
    root=Path(root);record=json.loads((root/RECORD).read_bytes())
    if record['pdf_sha256']!=PDF_SHA256 or record['assets']['pdf']['sha256']!=PDF_SHA256:
        raise ValueError('Published MNR PDF changed')
    if record['source_archive_sha256']!=SOURCE_SHA256 or record['assets']['source']['sha256']!=SOURCE_SHA256:
        raise ValueError('Published MNR source ZIP changed')
    if [c['number'] for c in record['chapters']]!=list(range(1,98)):
        raise ValueError('Published MNR chapter map changed')
    if digest((root/SCRIPT).read_bytes())!=record['delivery_script_sha256']:
        raise ValueError('MNR download verifier changed')
    if not (root/BOOK).is_file():raise ValueError('Missing MNR PDF reader')
    page=(root/PAGE).read_text(encoding='utf-8')
    if len(re.findall(r'<li id="chapter-\d+"',page))!=97:
        raise ValueError('Published MNR chapter contents are incomplete')
    if record['new_lean_execution'] or record['new_proof_review']:
        raise ValueError('Reconstruction must not promote mathematical assurance')
    return dict(pages=977,chapters=97,parts=13,pdf_sha256=PDF_SHA256,source_sha256=SOURCE_SHA256)
