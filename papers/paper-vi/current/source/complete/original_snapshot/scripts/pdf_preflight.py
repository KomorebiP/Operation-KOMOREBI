"""Render final pages for human visual review; does not assign a visual pass."""
from pathlib import Path
import fitz,re,json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'provenance/fourth_checked_block';doc=fitz.open(R/'manuscript/Paper_VI_Reviewed.pdf');prev=fitz.open(O/'manuscript/Paper_VI_Reviewed.pdf');out=R/'verification/pdf_render';out.mkdir(exist_ok=True)
for p in out.glob('*.png'):p.unlink()
changed=[];outside=[];thumbs=[]
for i,page in enumerate(doc):
 pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
 same=i<len(prev) and pix.samples==prev[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).samples
 if not same:
  changed.append(i+1);page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(out/f'page_{i+1:02d}.png')
 for b in page.get_text('blocks'):
  if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:outside.append([i+1,b[:4]])
 im.thumbnail((290,410));thumb=Image.new('RGB',(310,440),'#dddddd');thumb.paste(im,((310-im.width)//2,20));ImageDraw.Draw(thumb).text((10,422),f'Page {i+1}',fill='black');thumbs.append(thumb)
for start in range(0,len(thumbs),12):
 sheet=Image.new('RGB',(1240,1320),'white')
 for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%4)*310,(j//4)*440))
 sheet.save(out/f'contact_{start//12+1}.png')
text='\n'.join(p.get_text() for p in doc)
tex=(R/'manuscript/Paper_VI_Reviewed.tex').read_text();records=re.findall(r'\\begin\{(theorem|lemma|corollary|proposition)\}',tex)
def labels(path):return dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',path.read_text()))
a=labels(R/'manuscript/Paper_VI_Reviewed.aux');b=json.loads((O/'manuscript/label_numbers.json').read_text());labelchanges={k:[v,a.get(k)] for k,v in b.items() if k in a and v!=a[k]};missing=[k for k in b if k not in a]
log=(R/'manuscript/Paper_VI_Reviewed.log').read_text();warnings=re.findall(r'^.*(?:Warning|Overfull|Underfull).*$',log,re.M)
result={'pages':len(doc),'changed_pages_compared_to_fourth_block':changed,'text_outside_page':outside,'theorem_like_records':len(records),'open_conjectures':tex.count(r'\begin{conjecture}'),'label_number_changes':labelchanges,'missing_labels':missing,'contains_missing_reference':'??' in text,'warnings':warnings,'pdf_sha256':hashlib.sha256((R/'manuscript/Paper_VI_Reviewed.pdf').read_bytes()).hexdigest()}
(R/'verification/pdf_preflight.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
