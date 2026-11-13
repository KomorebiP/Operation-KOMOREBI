"""Rasterize only the 17 atlas PDFs not already authenticated by the Physics reader."""
from pathlib import Path
import hashlib,json,re
from physics_visual import BASE,RECEIPTS,metadata

def main():
    import pypdfium2 as pdfium
    root=Path(__file__).resolve().parents[1]
    old={}
    for path in (root/'website/assets/figures').glob('physics-*/figures.json'):
        if path.parent.name=='physics-visual-extra':continue
        for row in json.loads(path.read_bytes())['figures']:old[row['source']]=row
    records=[]
    for atlas in metadata()['atlases']:
        for name in re.findall(r'\\atlasfigure\{([^{}]+)\}',(root/atlas['body']).read_text(encoding='utf-8')):
            source=BASE+atlas['figures']+'/'+name+'.pdf'
            if source in old:continue
            raw=(root/source).read_bytes();document=pdfium.PdfDocument(raw)
            if len(document)!=1:raise ValueError('Expected one-page Physics plate')
            page=document[0];bitmap=page.render(scale=2.5);image=bitmap.to_pil()
            published='assets/figures/physics-visual-extra/'+name+'.png';target=root/'website'/published
            target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
            records.append(dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),image=published,
                image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),width=image.width,height=image.height,scale=2.5))
            image.close();bitmap.close();page.close();document.close()
    if len(records)!=17 or len({r['image'] for r in records})!=17:raise ValueError('Review Physics extra plate inventory')
    (root/'website'/RECEIPTS).write_text(json.dumps(dict(figures=records),indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered 17 additional Physics vector plates; 43 existing publications are reused.')

if __name__=='__main__':main()
