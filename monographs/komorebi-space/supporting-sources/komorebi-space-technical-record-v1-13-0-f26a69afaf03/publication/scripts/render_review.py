from pathlib import Path
import fitz
from PIL import Image, ImageDraw
import argparse,json,hashlib
p=argparse.ArgumentParser();p.add_argument('pdf',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
d=fitz.open(a.pdf);thumbs=[];outliers=[]
for i,page in enumerate(d):
    pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im.save(a.output/f'page-{i+1:03}.png')
    im.thumbnail((306,396));tile=Image.new('RGB',(326,430),'#deded8');tile.paste(im,((326-im.width)//2,24));ImageDraw.Draw(tile).text((12,6),f'PDF page {i+1}',fill='black');thumbs.append(tile)
    for w in page.get_text('words'):
        if w[0]<0 or w[1]<0 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:outliers.append({'page':i+1,'word':w})
for start in range(0,len(thumbs),12):
    sheet=Image.new('RGB',(326*3,430*4),'#d2d2ce')
    for j,t in enumerate(thumbs[start:start+12]):sheet.paste(t,((j%3)*326,(j//3)*430))
    sheet.save(a.output/f'contact-{start+1:03}-{min(start+12,len(thumbs)):03}.png')
(a.output/'render_report.json').write_text(json.dumps({'pdf':str(a.pdf.resolve()),'sha256':hashlib.sha256(a.pdf.read_bytes()).hexdigest(),'pages':len(d),'outside_page_words':outliers},indent=2)+'\n')
print(json.dumps({'pages':len(d),'outliers':len(outliers),'sheets':len(list(a.output.glob('contact-*.png')))}))
