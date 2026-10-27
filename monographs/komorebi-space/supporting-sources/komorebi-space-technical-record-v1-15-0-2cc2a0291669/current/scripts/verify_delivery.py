"""Compare freshly materialized saved files against canonical release outputs."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'publication_v115_output'
inputs=json.loads(Path(sys.argv[1]).read_text())
receipt_path=OUT/'Komorebi_Space_Delivery_Verification_v1.15.0.json'
receipt=json.loads(receipt_path.read_text())
assert receipt['distribution_status']=='PENDING_ACTUAL_DOWNLOAD_VERIFICATION'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def links(page):
    return [{k:(list(v) if isinstance(v,(fitz.Rect,fitz.Point)) else v)
             for k,v in link.items() if k not in {'xref','id'}} for link in page.get_links()]
results=[]
for item in inputs['files']:
    original=OUT/item['file_name']
    downloaded=Path(item['local_path'])
    assert downloaded.resolve()!=original.resolve()
    assert original.exists() and downloaded.exists()
    row={'file':original.name,'library_file_id':item['library_file_id'],'file_id':item.get('file_id'),
         'version':item.get('version'),'canonical_sha256':sha(original),'canonical_bytes':original.stat().st_size,
         'downloaded_sha256':sha(downloaded),'downloaded_bytes':downloaded.stat().st_size,
         'downloaded_bytes_identical':sha(original)==sha(downloaded)}
    if original.suffix=='.zip':
        assert row['downloaded_bytes_identical'],row
        row['verification']='Exact downloaded archive identity; canonical CRC and all manifest entries already checked.'
    elif original.suffix=='.pdf':
        a,b=fitz.open(original),fitz.open(downloaded)
        assert len(a)==len(b)
        checked=[]
        for i in range(len(a)):
            text_same=a[i].get_text()==b[i].get_text()
            rect_same=a[i].rect==b[i].rect
            raster_same=a[i].get_pixmap(dpi=72).samples==b[i].get_pixmap(dpi=72).samples
            links_same=links(a[i])==links(b[i])
            assert text_same and rect_same and raster_same and links_same,(original.name,i+1,text_same,rect_same,raster_same,links_same)
            checked.append(i+1)
        row.update(pages=len(a),all_page_text_identical=True,all_page_dimensions_identical=True,
                   all_page_rasters_identical=True,raster_dpi=72,all_page_link_targets_identical=True,
                   checked_pages=checked,embedded_objects=b.embfile_names(),
                   content_credentials_signature_authenticated=False,
                   verification='Every page of the actual downloaded PDF compared against the canonical archived PDF. Byte rewriting is recorded separately from unchanged text, rendered page pixels, dimensions, and link targets.')
    else:raise ValueError(original)
    results.append(row)
assert len(results)==5
assert sum(r['file'].endswith('.pdf') for r in results)==3
receipt.update(distribution_status='PASS',distribution_verification={'files':results,
    'method':'Fresh materialization of saved Library identities after upload, into a distinct directory; not rehashing the pre-upload originals.',
    'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope':'Both actual downloaded archives and all pages of all three actual downloaded standalone PDFs. The delivery receipt itself is replaced after this comparison and verified separately to avoid a circular self-hash.'})
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
(ROOT/'records/delivery_comparison.json').write_text(json.dumps(receipt['distribution_verification'],indent=2)+'\n')
print(json.dumps({'distribution_status':'PASS','files':[{'file':r['file'],'byte_identical':r['downloaded_bytes_identical'],'pages':r.get('pages')} for r in results]},indent=2))
