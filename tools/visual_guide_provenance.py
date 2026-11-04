"""Bind new visual provenance revisions separately from frozen imported sources."""
import hashlib
import json
from pathlib import Path

RECORD='verification/visual-guide-provenance/2026-11-03.json'
IV_BASE='publication/paper-iv-visual-reconstruction/'
IV_SOURCE=IV_BASE+'pages.tex'
IV_PDF=IV_BASE+'Paper_IV_Visual_Guide_Reconstructed.pdf'
VIII_CROSSWALK='publication/paper-viii-visual-crosswalk/VISUAL_TO_TRADITIONAL_CROSSWALK_v2.json'


def validate_file(root, item):
    path=item['path']
    if path.startswith('/') or '..' in path.split('/'):
        raise ValueError('Unsafe visual provenance path: '+path)
    raw=(root/path).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if (len(raw),hashlib.sha256(raw).hexdigest(),blob)!=(item['size'],item['sha256'],item['git_blob_sha1']):
        raise ValueError('Visual provenance identity changed: '+path)
    return raw


def load(root):
    return json.loads((root/RECORD).read_bytes())


def register(reader, work):
    """Publish the reviewed supplement without changing the original import receipt."""
    section=load(reader.site.root)['works'][work]
    for item in section['published_files']:
        validate_file(reader.site.root,item)
        reader.owned[item['path']]=dict(item,repository_path=item['path'],work=work)
        reader.add(item['path'])
    return section


def check(root):
    record=load(root)
    for section in record['works'].values():
        for item in section['published_files']:
            validate_file(root,item)
    iv=record['works']['paper-iv']
    build=json.loads(validate_file(root,iv['build_record']))
    validate_file(root,iv['original_pdf'])
    if not (build['physical_pages']==28 and build['matching_content_pages']==27 and
            [row['physical_page'] for row in build['page_comparisons']]==list(range(1,29)) and
            all(row['text_equal_ignoring_whitespace_nfkc'] for row in build['page_comparisons'][1:]) and
            build['visual_review']['status']=='PASS' and build['visual_review']['pages']==list(range(1,29))):
        raise ValueError('Paper IV reconstruction review is incomplete')
    for item in build['visual_review']['artifacts']:
        validate_file(root,item)
    viii=record['works']['paper-viii']
    original=json.loads(validate_file(root,viii['original_crosswalk']))
    corrected=json.loads(validate_file(root,viii['source']))
    expected=dict(original,visual_pdf_sha256=viii['pdf']['sha256'])
    del corrected['provenance_revision']
    if corrected!=expected or len(corrected['pages'])!=32:
        raise ValueError('Paper VIII crosswalk changed beyond its reviewed PDF identity')
    validate_file(root,viii['pdf'])
    return record


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',action='store_true',help='Repeat all PDF text and page checks with pypdfium2')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    record=check(root)
    if args.pdf:
        import re
        import unicodedata
        import pypdfium2 as pdfium
        compact=lambda text:re.sub(r'\s+','',unicodedata.normalize('NFKC',text))
        iv=record['works']['paper-iv']
        with pdfium.PdfDocument(root/iv['original_pdf']['path']) as original, pdfium.PdfDocument(root/iv['pdf']['path']) as rebuilt:
            if len(original)!=28 or len(rebuilt)!=28:
                raise ValueError('Paper IV PDF page count changed')
            page=rebuilt[0];text=page.get_textpage()
            try:
                if 'Reconstructed3November2026' not in compact(text.get_text_range()):
                    raise ValueError('Paper IV cover does not identify the reconstruction')
            finally:text.close();page.close()
            for number in range(1,28):
                texts=[]
                for document in (original,rebuilt):
                    page=document[number];text=page.get_textpage()
                    try:texts.append(compact(text.get_text_range()))
                    finally:text.close();page.close()
                if texts[0]!=texts[1]:raise ValueError('Paper IV content differs on physical page '+str(number+1))
        from render_paper_viii_atlas import validate_pdf_pages
        if validate_pdf_pages(root)!=32:raise ValueError('Paper VIII page inventory changed')
    print(json.dumps({work:section['status'] for work,section in record['works'].items()},indent=2))
