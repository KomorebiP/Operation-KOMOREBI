from pathlib import Path
import fitz,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent; Q=R/'qa';Q.mkdir(exist_ok=True)
pdf=fitz.open(R/'Paper_II_Traditional_Final.pdf'); bounds=[]
for st in range(0,len(pdf),18):
 sheet=Image.new('RGB',(1000,6*470),'#dfe8e6');draw=ImageDraw.Draw(sheet)
 for i in range(st,min(st+18,len(pdf))):
  p=pdf[i];pix=p.get_pixmap(matrix=fitz.Matrix(.62,.62),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((312,436))
  x=12+(i-st)%3*330;y=24+(i-st)//3*470;sheet.paste(im,(x,y));draw.text((x,y-15),f'PDF page {i+1}',fill='black')
  for b in p.get_text('dict')['blocks']:
   if b['type']!=0:continue
   x0,y0,x1,y1=b['bbox']
   if x0<15 or x1>p.rect.width-15 or y0<12 or y1>p.rect.height-12:bounds.append({'pdf_page':i+1,'bbox':b['bbox']})
 sheet.save(Q/f'contact_{st//18+1}.jpg',quality=85)
for i in [0,1,2,8,11,17,23,28,36,39,41,49,51,53]:
 p=pdf[i];p.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(Q/f'detail_{i+1:02d}.png')
report={'pages':len(pdf),'bookmarks':len(pdf.get_toc()),'links':sum(len(p.get_links()) for p in pdf),'text_margin_flags':bounds,'full_contact_sheets':3,'detail_pages':[1,2,3,9,12,18,24,29,37,40,42,50,52,54]}
(Q/'PDF_LAYOUT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
