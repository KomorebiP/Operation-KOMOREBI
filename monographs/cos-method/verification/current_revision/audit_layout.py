"""Check PDF geometry and navigation; render with PDFium when --render is set.
A geometrical check is not a substitute for visual review.
"""
from pathlib import Path
import argparse,json
import fitz
p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--output',type=Path,default=Path('verification/new_layout_check'));a=p.parse_args()
root=Path(__file__).resolve().parents[2];pdf=root/'K_COS_Monograph.pdf';a.output.mkdir(parents=True,exist_ok=True)
d=fitz.open(pdf);out={'pages':len(d),'bookmarks':len(d.get_toc()),'links':0,'out_of_page_words':[],'invalid_internal_links':[],'empty_pages':[]}
for i,page in enumerate(d):
 if len(page.get_text().strip())<10:out['empty_pages'].append(i+1)
 for w in page.get_text('words'):
  if w[0]<-.8 or w[1]<-.8 or w[2]>page.rect.width+.8 or w[3]>page.rect.height+.8:out['out_of_page_words'].append([i+1,w])
 for l in page.get_links():
  out['links']+=1
  if l.get('kind')==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(d):out['invalid_internal_links'].append([i+1,l])
if a.render:
 import pypdfium2 as pdfium
 r=pdfium.PdfDocument(str(pdf))
 for i in range(len(r)):
  page=r[i];page.render(scale=1.5).to_pil().save(a.output/f'page_{i+1:03}.png');page.close()
(a.output/'inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
