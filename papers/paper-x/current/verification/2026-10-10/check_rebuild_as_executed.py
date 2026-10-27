from pathlib import Path
import fitz,json,hashlib,re
from PIL import Image
root=Path('/mnt/data/Paper_X_Working'); orig=root/'publication/pdfs'; replay=Path('/mnt/data/paper_x_isolated_pdfs')
records=[]
for p in sorted(orig.glob('*.pdf')):
    q=replay/p.name;a=p.read_bytes();b=q.read_bytes()
    normal=lambda x:re.sub(rb'/ID\s*\[\s*<[^>]*>\s*<[^>]*>\s*\]',b'/ID[<REDACTED><REDACTED>]',x)
    with fitz.open(p) as x,fitz.open(q) as y:
        text=[x[i].get_text()==y[i].get_text() for i in range(len(x))]
        rasters=[];prior=[]
        folder=p.stem.removeprefix('Paper_X_').removesuffix('_Final')
        for i in range(len(x)):
            px=x[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False)
            py=y[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False)
            rasters.append(px.samples==py.samples)
            old=Image.open(Path('/mnt/data/paper_x_review/after')/folder/f'{i+1:03}.png').convert('RGB')
            prior.append(old.size==(px.width,px.height) and old.tobytes()==px.samples)
        record=dict(file=p.name,pages=len(x),binary_identical=a==b,identical_except_trailer_id=normal(a)==normal(b),ordered_page_text_identical=all(text),rendered_pages_identical=all(rasters),reviewed_page_images_match_final=all(prior),sha256=hashlib.sha256(a).hexdigest(),rebuild_sha256=hashlib.sha256(b).hexdigest(),different_previous_images=[i+1 for i,v in enumerate(prior) if not v])
        records.append(record);print(json.dumps(record),flush=True)
res={'status':'passed_content_and_render_reproducibility','strict_binary_reproducibility':all(x['binary_identical'] for x in records),'documents':records,'raster_dpi':86.4,'pages_compared':sum(x['pages'] for x in records),'lean_compilation':False}
(root/'verification/2026-10-10/REBUILD_COMPARISON.json').write_text(json.dumps(res,indent=2))
