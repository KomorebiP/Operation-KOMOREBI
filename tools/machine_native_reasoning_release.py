"""Publish the synchronized numbered edition and retain the historical reader."""
import hashlib,html,json,zipfile
from io import BytesIO
from pathlib import Path
PREFIX='publication/mnr-synchronized/v1.0.0/'
MANIFEST=PREFIX+'RELEASE.json'
PDF_SHA256='92f4a6aa03d0c9e5ef6bc5e9c24026090f3b3d9280576cf5d87c4f906ecc5e14'
SOURCE_SHA256='0a6b6120f3fd4900529ef696c49030fe621532695edfc68de6d83e16d5169c09'
HISTORICAL_RECORD='documents/mnr-reconstructed-2026-11-04.json'
HISTORICAL_BOOK='read/research-machine-native-reasoning-wider/book-2026-11-04.html'
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def load(root):
    from machine_native_reasoning_expanded import artifact_bytes
    root=Path(root);data=json.loads((root/MANIFEST).read_bytes())
    if data.get('edition')!='mnr-synchronized-v1.0.0' or data['version']!='1.0.0' or data['pages']!=977 or data['parts']!=13:raise ValueError('Unknown synchronized MNR edition')
    if [x['number'] for x in data['chapters']]!=list(range(1,98)):raise ValueError('Incomplete synchronized MNR chapter map')
    if (data['assets']['pdf']['sha256'],data['assets']['source']['sha256'])!=(PDF_SHA256,SOURCE_SHA256):raise ValueError('Synchronized release identity changed')
    if sha((root/data['html_manifest']).read_bytes())!=data['html_manifest_sha256']:raise ValueError('Synchronized web edition changed')
    for kind,asset in data['assets'].items():
        if not all(p['path'].startswith(PREFIX+'parts/'+kind+'-') for p in asset['parts']):raise ValueError('Mixed MNR edition assets')
        raw=artifact_bytes(root,asset)
        if kind=='source':
            with zipfile.ZipFile(BytesIO(raw)) as z:
                if z.testzip():raise ValueError('Source archive CRC failed')
                rows=json.loads(z.read('MANIFEST.json'))['files']
                if set(z.namelist())!={r['path'] for r in rows}|{'MANIFEST.json'}:raise ValueError('Source archive inventory changed')
                if any(sha(z.read(r['path']))!=r['sha256'] for r in rows):raise ValueError('Source archive file changed')
                edition=json.loads(z.read('EDITION.json'))
                if edition['pdf_sha256']!=PDF_SHA256:raise ValueError('Source archive names a different PDF')
                web=json.loads((root/data['html_manifest']).read_bytes())
                for source in web['sources']:
                    raw=z.read(source['path'].removeprefix('source/'))
                    if source.get('repository_path')!=PREFIX+source['path'] or sha(raw)!=source['sha256'] or (root/source['repository_path']).read_bytes()!=raw:raise ValueError('Online chapter source differs from synchronized ZIP')
    return data

def publish(site,previous,reader_body):
    from machine_native_reasoning_expanded import BOOK,RECORD,SCRIPT
    from build_reader_site import github,REPOSITORY
    data=load(site.root)
    historical=dict(previous,edition='reconstructed-editorial-2026-11-04',pdf_reader=HISTORICAL_BOOK)
    historical.pop('chapters',None)
    historical.update(source_archive=HISTORICAL_BOOK+'?download=source',chapter_map_manifest=previous['publication_manifest'])
    site.write(HISTORICAL_RECORD,json.dumps(historical,separators=(',',':')))
    old=reader_body
    old=old.replace(site.rel(RECORD,BOOK),site.rel(HISTORICAL_RECORD,HISTORICAL_BOOK))
    old=old.replace('<h1>Machine-Native Reasoning</h1>','<h1>Machine-Native Reasoning</h1><p>Historical reconstructed edition · 4 November 2026. <a href="book.html">Open the synchronized v1.0.0 edition</a>.</p>',1)
    site.page(HISTORICAL_BOOK,'Machine-Native Reasoning: historical reconstructed PDF and source',old,github(REPOSITORY,site.revision,previous['publication_manifest']))
    record=dict(previous,edition=data['edition'],version=data['version'],tag=data['tag'],pdf_sha256=PDF_SHA256,source_archive_sha256=SOURCE_SHA256,pages=data['pages'],chapters=data['chapters'],assets=data['assets'],publication_manifest=MANIFEST,publication_manifest_sha256=sha((site.root/MANIFEST).read_bytes()),historical_record=HISTORICAL_RECORD,historical_pdf_reader=HISTORICAL_BOOK,release_url='https://github.com/'+REPOSITORY+'/releases/tag/'+data['tag'],bridge_self_review=github(REPOSITORY,site.revision,data['focused_bridge_self_review']),bridge_review_kind='focused self-review; seven integration interfaces; not an independent whole-book audit',new_lean_execution=False,new_proof_review=False)
    site.write(RECORD,json.dumps(record,separators=(',',':')))
    e=html.escape
    book=(site.output/BOOK).read_text(encoding='utf-8')
    book=book.replace('<h1>Machine-Native Reasoning</h1>','<h1>Machine-Native Reasoning</h1><p class="eyebrow">Synchronized reconstructed edition · v1.0.0</p>',1)
    book=book.replace('Download editable TeX (30.6 MB)','Download editable TeX ('+f'{data["assets"]["source"]["bytes"]/1000000:.1f}'+' MB)')
    book=book.replace('<section id="mnr-delivery"','<p><a href="'+e(site.rel(HISTORICAL_BOOK,BOOK),quote=True)+'">Earlier PDF and full archival source</a> · <a href="'+e(record['release_url'],quote=True)+'">Version record</a></p><section id="mnr-delivery"',1)
    site.write(BOOK,book)
    return record

def verify(root):
    from machine_native_reasoning_expanded import RECORD,BOOK
    root=Path(root);r=json.loads((root/RECORD).read_bytes())
    if r.get('edition')!='mnr-synchronized-v1.0.0' or r['pdf_sha256']!=PDF_SHA256 or r['source_archive_sha256']!=SOURCE_SHA256:raise ValueError('Published synchronized release changed')
    if [c['number'] for c in r['chapters']]!=list(range(1,98)):raise ValueError('Synchronized chapter map incomplete')
    old=json.loads((root/HISTORICAL_RECORD).read_bytes())
    from machine_native_reasoning_expanded import PDF_SHA256 as OLD_PDF,SOURCE_SHA256 as OLD_SOURCE
    if old['pdf_sha256']!=OLD_PDF or old['source_archive_sha256']!=OLD_SOURCE:raise ValueError('Historical artifacts changed')
    if not (root/HISTORICAL_BOOK).is_file() or not (root/BOOK).is_file():raise ValueError('Missing MNR edition reader')
    return dict(pages=977,chapters=97,parts=13,pdf_sha256=PDF_SHA256,source_sha256=SOURCE_SHA256,version='1.0.0',historical_edition_preserved=True)
