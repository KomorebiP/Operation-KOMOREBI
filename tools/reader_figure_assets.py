"""Verify and publish browser images rendered from retained single-page PDFs."""
import hashlib
import json
from pathlib import PurePosixPath
import posixpath
import re

def digest(raw): return hashlib.sha256(raw).hexdigest()

def candidates(config,spec,name):
    return [config['base']+folder+name for folder in spec.get('figure_roots',['figures/'])]

def prepare(reader,config,chapters):
    from build_reader_site import safe_path
    report=json.loads((reader.site.root/'website'/safe_path(config['figure_receipts'])).read_bytes())
    assets={}
    for record in report['figures']:
        source=record['source']
        expected=posixpath.dirname(config['figure_receipts'])+'/'+PurePosixPath(source).stem+'.png'
        if not source.startswith(config['base']) or record['image']!=expected:
            raise ValueError('Unexpected rendered figure path')
        if source in assets: raise ValueError('Duplicate rendered figure source')
        source_record=reader.add(source)
        if not source_record or digest(reader.site.read_source(source_record))!=record['source_sha256']:
            raise ValueError('Rendered figure source differs: '+source)
        source_record['figure_source']=True
        raw=(reader.site.root/'website'/safe_path(record['image'])).read_bytes()
        if digest(raw)!=record['image_sha256']:
            raise ValueError('Rendered figure image differs: '+source)
        assets[source]=record
    used=[]
    for spec,_,chapter in chapters:
        for node in chapter.nodes:
            if node['kind']!='figure': continue
            match=re.search(r'\\includegraphics\[[^\]]+\]\{([^{}]+)\}',node['body'])
            if not match: raise ValueError('Missing figure source')
            found=[p for p in candidates(config,spec,match[1]) if p in assets]
            if len(found)!=1: raise ValueError('Unresolved rendered figure: '+match[1])
            used+=found
    if len(used)!=len(set(used)) or set(used)!=set(assets):
        raise ValueError('Every rendered figure must appear once')
    return assets

def image(reader,config,spec,assets,name,page):
    found=[p for p in candidates(config,spec,name) if p in assets]
    if len(found)!=1: raise ValueError('Unresolved rendered figure: '+name)
    source=found[0]; record=assets[source]
    raw=(reader.site.root/'website'/record['image']).read_bytes()
    if digest(raw)!=record['image_sha256']: raise ValueError('Rendered figure image differs')
    target=reader.site.output/record['image']
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
    reader.images[source]=dict(repository_path='website/'+record['image'],
        file_url=record['image'],size=len(raw),sha256=digest(raw),
        git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
        source=source,source_sha256=record['source_sha256'])
    return source,reader.site.rel(record['image'],page),record['source_sha256']
