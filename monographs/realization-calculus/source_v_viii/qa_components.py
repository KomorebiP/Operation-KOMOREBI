from pathlib import Path
import fitz,json,re,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'qa_current';OUT.mkdir(exist_ok=True)
records=json.loads((ROOT/'BUILD_RESULTS_FINAL.json').read_text());results=[]
for rec in records:
 p=Path(rec['pdf']);d=fitz.open(p);name=rec['paper']+'_'+rec['role'];log=(Path(rec['compiled_directory'])/(rec['stem']+'.log')).read_text(errors='replace')
 checks=[];render_pages=set([0,2,min(len(d)-1,8),len(d)//2,len(d)-1]);mathpages=[];tablepages=[]
 for i,page in enumerate(d):
  txt=page.get_text();bounds=[]
  for b in page.get_text('blocks'):
   if b[4].strip() and (b[0]<-.2 or b[1]<-.2 or b[2]>page.rect.width+.2 or b[3]>page.rect.height+.2):bounds.append(list(b[:4]))
  bad=[x for x in page.get_links() if (x['kind']==1 or (x['kind']==4 and 'page' in x)) and not 0<=x.get('page',-1)<len(d)]
  checks.append({'page':i+1,'text_characters':len(txt),'outside_page_blocks':bounds,'invalid_internal_links':bad})
  if 'Theorem' in txt and len(txt)>2000:mathpages.append((len(txt),i))
  if len(page.get_drawings())>40:tablepages.append((len(page.get_drawings()),i))
 render_pages.update(i for _,i in sorted(mathpages,reverse=True)[:1]);render_pages.update(i for _,i in sorted(tablepages,reverse=True)[:1])
 if rec['role']=='visual_guide':render_pages=set(range(len(d)))
 thumbs=[]
 for i in sorted(render_pages):
  pix=d[i].get_pixmap(matrix=fitz.Matrix(.55,.55),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);thumbs.append((i,im))
  if i in [0,len(d)//2] or (rec['role']=='traditional' and i in [x[1] for x in sorted(mathpages,reverse=True)[:1]]):
   d[i].get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(OUT/f'{name}_detail_{i+1:03}.png')
 w=342;h=458;cols=4 if rec['role']=='visual_guide' else 3;rows=(len(thumbs)+cols-1)//cols;sheet=Image.new('RGB',(w*cols,h*rows),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for j,(i,im) in enumerate(thumbs):
  x=(j%cols)*w;y=(j//cols)*h;sheet.paste(im,(x+3,y+17));draw.text((x+5,y+2),f'{name} / PDF {i+1}',fill='black')
 sheet.save(OUT/(name+'_contact.png'))
 result={'paper':rec['paper'],'role':rec['role'],'pages':len(d),'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'page_labels':d.get_page_labels(),'bookmarks':len(d.get_toc()),'links':sum(len(x.get_links()) for x in d),'internal_links':sum(sum(z['kind']==1 or (z['kind']==4 and 'page' in z) for z in x.get_links()) for x in d),'external_links':[{'page':i+1,'link':{k:str(v) if k in ['from','to'] else v for k,v in z.items()}} for i,x in enumerate(d) for z in x.get_links() if not (z['kind']==1 or (z['kind']==4 and 'page' in z))],'overfull_lines':[x for x in log.splitlines() if 'Overfull' in x],'missing_characters':[x for x in log.splitlines() if 'Missing character' in x],'unresolved_references':[x for x in log.splitlines() if any(y in x for y in ['undefined references','undefined citations','undefined on input'])],'font_shape_warnings':[x for x in log.splitlines() if 'Font shape' in x and 'undefined' in x],'checks':checks,'rendered_pages':[i+1 for i in sorted(render_pages)]}
 results.append(result);print(name,len(d),'issues',sum(bool(c['outside_page_blocks'] or c['invalid_internal_links']) for c in checks),flush=True)
(ROOT/'QA_CURRENT.json').write_text(json.dumps(results,indent=2))
