from pathlib import Path
import json,re,hashlib
import fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
PDF=ROOT/'output/Realization_Calculus_Quantum_and_Circuits.pdf'
P=fitz.open(PDF)
Q=ROOT/'qa';(Q/'pages').mkdir(exist_ok=True)
for previous in list((Q/'pages').glob('[0-9][0-9][0-9].png'))+list(Q.glob('all_pages_*.png')):
 previous.unlink()
issues=[];counts=[];thumbs=[];link_count=0
fonts=set()
for i,page in enumerate(P):
 for font in page.get_fonts():fonts.add(font[3].split('+')[-1])
 for link in page.get_links():
  link_count+=1
  if link.get('kind')==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(P):
   issues.append({'page':i+1,'issue':'invalid internal link','destination':link.get('page')})
 text=page.get_text(); counts.append(len(text.strip()))
 if not text.strip():issues.append({'page':i+1,'issue':'empty text page'})
 for b in page.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if min(x0,y0)<-0.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:issues.append({'page':i+1,'issue':'text outside page','bbox':span['bbox'],'text':span['text']})
 pix=page.get_pixmap(matrix=fitz.Matrix(.4,.4),alpha=False)
 im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 im.save(Q/'pages'/f'{i+1:03}.png')
 canvas=Image.new('RGB',(im.width,im.height+16),'#e4e8e8');canvas.paste(im,(0,16));ImageDraw.Draw(canvas).text((4,2),f'{i+1}',fill='black');thumbs.append(canvas)
for i in range(0,len(thumbs),24):
 w=thumbs[0].width;h=thumbs[0].height
 sheet=Image.new('RGB',(w*4,h*6),'#babbbb')
 for j,im in enumerate(thumbs[i:i+24]):sheet.paste(im,((j%4)*w,(j//4)*h))
 sheet.save(Q/f'all_pages_{i//24+1:02}.png')
log=(ROOT/'output/final_pass2.console').read_text()
critical=[x for x in log.splitlines() if any(t in x for t in ['undefined','Overfull','Missing character','multiply defined','Emergency stop'])]
r={'status':'PASS' if not issues and not critical else 'FAIL','pages':len(P),'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'layout_issues':issues,'compile_critical_warnings':critical,'minimum_page_text_characters':min(counts),'rendered_every_page':True,'render_scale':.4,'embedded_fonts':sorted(fonts),'links_checked':link_count,'visual_review':'All-page contact sheets plus enlarged representative mathematical, figure, table, and formal-code pages. See review/style/final_review.json for the presentation review.'}
(Q/'layout_checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
