from pathlib import Path
import json
import fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'verification/figure_pass/final_render';O.mkdir(exist_ok=True)
p=fitz.open(R/'K_COS_Monograph.pdf')
for i,page in enumerate(p):
 pix=page.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False)
 pix.pil_save(O/f'page_{i+1:03d}.jpg',quality=88)
 if i%20==0:print('Rendered',i+1,flush=True)
# All pages, arranged 12 per contact sheet.
for b in range(0,len(p),12):
 canvas=Image.new('RGB',(1440,1580),'#e8e6e9');draw=ImageDraw.Draw(canvas)
 for j in range(min(12,len(p)-b)):
  im=Image.open(O/f'page_{b+j+1:03d}.jpg');im.thumbnail((345,490));x=(j%4)*360+7;y=(j//4)*525+25
  canvas.paste(im,(x,y));draw.text((x,y-18),str(b+j+1),fill='black')
 canvas.save(O/f'sheet_{b//12+1:02d}.jpg',quality=90)
# Dedicated figure-page sheets make the changed material easier to inspect.
fp=json.loads((R/'verification/figure_pass/publication_audit.json').read_text())['pdf']['identified_figure_pages']
for b in range(0,len(fp),6):
 canvas=Image.new('RGB',(1500,2050),'#e8e6e9');draw=ImageDraw.Draw(canvas)
 for j,n in enumerate(fp[b:b+6]):
  im=Image.open(O/f'page_{n:03d}.jpg');im.thumbnail((480,990));x=(j%3)*500+8;y=(j//3)*1025+25
  canvas.paste(im,(x,y));draw.text((x,y-18),str(n),fill='black')
 canvas.save(O/f'figures_{b//6+1:02d}.jpg',quality=92)
print('Finished',len(p),'pages;',len(fp),'identified figure pages.',flush=True)
