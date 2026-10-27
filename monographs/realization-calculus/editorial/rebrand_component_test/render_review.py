from pathlib import Path
import fitz,json,hashlib,math
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[2];T=Path(__file__).resolve().parent;O=T/'crops';O.mkdir(exist_ok=True)
audit=json.loads((T/'audit.json').read_text());rows=[];pairs=[];covers=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for comp in audit['components']:
 bp=ROOT/comp['baseline_path'];ap=ROOT/comp['derivative_path']
 assert sha(bp)==comp['before_sha256'] and sha(ap)==comp['after_sha256']
 before=fitz.open(bp);after=fitz.open(ap)
 for j,e in enumerate(comp['edits']):
  pi=e['page_1based']-1;r=fitz.Rect(e['validation_region']);cx=(r.x0+r.x1)/2;cy=(r.y0+r.y1)/2
  width=max(256,r.width+20);height=max(44,r.height+20)
  clip=fitz.Rect(cx-width/2,cy-height/2,cx+width/2,cy+height/2)&before[pi].rect
  pix1=before[pi].get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False);pix2=after[pi].get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False)
  a=Image.frombytes('RGB',(pix1.width,pix1.height),pix1.samples);b=Image.frombytes('RGB',(pix2.width,pix2.height),pix2.samples)
  panelw=max(512,a.width);h=max(88,a.height)
  tile=Image.new('RGB',(panelw*2+24,h+26),'#e7e3e6');draw=ImageDraw.Draw(tile)
  title=f"{comp['component_id']} page {pi+1} label {j+1}"
  draw.text((8,5),title+' | before',fill='black');draw.text((panelw+20,5),'after',fill='black')
  tile.paste(a,(8+(panelw-a.width)//2,22));tile.paste(b,(panelw+16+(panelw-b.width)//2,22))
  n=len(rows)+1;fname=f'strip_{n:03d}.png';tile.save(O/fname)
  rows.append({'index':n,'component':comp['component_id'],'component_page':pi+1,'edit_index':j,'crop':str((O/fname).relative_to(ROOT)),'clip':list(clip),'scale':2,'before_sha256':comp['before_sha256'],'after_sha256':comp['after_sha256']});pairs.append(tile)
 # Six complete first pages, before and after side by side, 1x native page size.
 ims=[]
 for doc in [before,after]:
  pix=doc[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
 canvas=Image.new('RGB',(ims[0].width+ims[1].width+28,max(ims[0].height,ims[1].height)+28),'#e7e3e6');dr=ImageDraw.Draw(canvas);dr.text((8,5),'BEFORE: '+comp['component_id'],fill='black');dr.text((ims[0].width+20,5),'AFTER',fill='black');canvas.paste(ims[0],(8,22));canvas.paste(ims[1],(ims[0].width+20,22));name='cover_'+comp['component_id']+'.png';canvas.save(O/name);covers.append(str((O/name).relative_to(ROOT)))
 before.close();after.close()
sheets=[]
for start in range(0,len(pairs),12):
 chunk=pairs[start:start+12];width=max(x.width for x in chunk);height=sum(x.height+4 for x in chunk);sheet=Image.new('RGB',(width,height),'#cccccc');y=0
 for tile in chunk:sheet.paste(tile,(0,y));y+=tile.height+4
 name=f'contact_{start//12+1:02d}.png';sheet.save(O/name);sheets.append({'path':str((O/name).relative_to(ROOT)),'strips':[start+1,min(start+12,len(pairs))]})
index={'paired_strips':len(rows),'contact_sheets':sheets,'covers':covers,'rows':rows,'scope':'Before/after visual review renders only; no PDF changes. Native 2x glyph scale preserved in crop strips.'}
(T/'visual_index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps({'strips':len(rows),'sheets':len(sheets),'covers':len(covers)}))
