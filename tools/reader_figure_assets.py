"""Verify and publish browser figures bound to retained PDFs or original PNGs."""
import hashlib
import io
import json
from pathlib import PurePosixPath
import posixpath
import re
from collections import Counter

def digest(raw): return hashlib.sha256(raw).hexdigest()


def dimensions(raw, path):
    """Read the actual supported image encoding; never infer sizes from receipts."""
    suffix=PurePosixPath(path).suffix.lower()
    if suffix=='.png':
        from reader_documents import png_dimensions
        return png_dimensions(raw)
    if suffix=='.webp':
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as image:
            if image.format!='WEBP' or getattr(image,'n_frames',1)!=1:
                raise ValueError('Expected one static WebP figure')
            image.load()
            return image.size
    raise ValueError('Unsupported reader figure image encoding')


def validate_encoding(root, record, directory):
    """Authenticate an optional lossless copy against retained original pixels."""
    suffix=PurePosixPath(record['image']).suffix.lower()
    if suffix=='.png':
        if any(key in record for key in ('original_png','original_png_sha256','source_rgba_sha256')):
            raise ValueError('Unexpected lossless receipt on legacy PNG')
        return
    if suffix!='.webp':
        raise ValueError('Unsupported reader figure image encoding')
    from PIL import Image
    group=PurePosixPath(directory).name
    name=PurePosixPath(record['source']).stem
    expected='verification/reader-figure-encoding/original/'+group+'/'+name+'.png'
    if record.get('original_png')!=expected:
        raise ValueError('Unexpected original PNG path')
    original=(root/expected).read_bytes()
    converted=(root/'website'/record['image']).read_bytes()
    if digest(original)!=record.get('original_png_sha256'):
        raise ValueError('Original PNG identity differs')
    if digest(converted)!=record['image_sha256']:
        raise ValueError('Rendered figure image differs')
    with Image.open(io.BytesIO(original)) as source_image, Image.open(io.BytesIO(converted)) as result_image:
        if source_image.format!='PNG' or result_image.format!='WEBP':
            raise ValueError('Lossless figure receipt has wrong image formats')
        source=source_image.convert('RGBA');result=result_image.convert('RGBA')
        if source.size!=result.size or source.tobytes()!=result.tobytes():
            raise ValueError('Lossless reader figure pixels differ')
        if digest(source.tobytes())!=record.get('source_rgba_sha256'):
            raise ValueError('Original reader figure pixel identity differs')
        if (record.get('width'),record.get('height'))!=source.size:
            raise ValueError('Lossless reader figure dimensions differ')

def candidates(config,spec,name):
    return [posixpath.normpath(config['base']+folder+name) for folder in spec.get('figure_roots',['figures/'])]

def prepare(reader,config,chapters):
    from build_reader_site import safe_path
    report=json.loads((reader.site.root/'website'/safe_path(config['figure_receipts'])).read_bytes())
    assets={}
    for record in report['figures']:
        source=record['source']
        directory=posixpath.dirname(config['figure_receipts'])
        suffix=PurePosixPath(record['image']).suffix.lower()
        if suffix not in {'.png','.webp'}:raise ValueError('Unsupported reader figure image encoding')
        expected=directory+'/'+PurePosixPath(source).stem+suffix
        if not source.startswith(config.get('figure_source_root',config['base'])) or record['image']!=expected:
            raise ValueError('Unexpected rendered figure path')
        if source in assets: raise ValueError('Duplicate rendered figure source')
        source_record=reader.add(source)
        if source_record is None and PurePosixPath(source).suffix.lower()=='.png':
            source_record=reader.owned.get(source)
            if source_record and source_record['mode'] not in {'100644','100755'}:
                source_record=None
        if not source_record or digest(reader.site.read_source(source_record))!=record['source_sha256']:
            raise ValueError('Rendered figure source differs: '+source)
        source_record['figure_source']=True
        if record.get('render_source'):
            rendered=reader.add(record['render_source'])
            if not rendered or digest(reader.site.read_source(rendered))!=record['render_source_sha256']:
                raise ValueError('Rendered figure parent differs: '+record['render_source'])
            if '/figures/' in record['render_source']:rendered['figure_source']=True
        if record.get('render_image'):
            image_entry=reader.owned.get(record['render_image'])
            if not image_entry or digest(reader.site.read_source(image_entry))!=record['render_image_sha256']:
                raise ValueError('Retained figure image differs: '+record['render_image'])
        raw=(reader.site.root/'website'/safe_path(record['image'])).read_bytes()
        if digest(raw)!=record['image_sha256']:
            raise ValueError('Rendered figure image differs: '+source)
        if PurePosixPath(source).suffix.lower()=='.png' and record['image_sha256']!=record['source_sha256']:
            raise ValueError('Retained PNG publication must be byte-identical: '+source)
        validate_encoding(reader.site.root,record,directory)
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
    expected={source:record.get('uses',1) for source,record in assets.items()}
    if any(type(count) is not int or count<1 for count in expected.values()) or Counter(used)!=expected:
        raise ValueError('Every rendered figure must appear its recorded number of times')
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
    width,height=dimensions(raw,record['image'])
    publication=dict(width=width,height=height,repository_path='website/'+record['image'],
        file_url=record['image'],size=len(raw),sha256=digest(raw),
        git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
        source=source,source_sha256=record['source_sha256'])
    if PurePosixPath(source).suffix.lower()=='.png':
        # The unchanged PNG is both the retained original and its browser asset.
        # Record both identities so the final audit can bind the publication to
        # an independently declared retained image, as it does for source PDFs.
        original={**reader.owned[source],**{k:v for k,v in publication.items() if k not in {'source','source_sha256'}}}
        original['repository_path']=source
        reader.images[source]=original
        reader.images[record['image']]=publication
    else:
        reader.images[source]=publication
    return source,reader.site.rel(record['image'],page),record['source_sha256']
