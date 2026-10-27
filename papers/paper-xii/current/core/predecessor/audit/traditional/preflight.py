from pathlib import Path
import fitz, hashlib, json, re, subprocess, sys
from PIL import Image, ImageDraw

pdf=Path(sys.argv[1]).resolve()
out=Path(__file__).resolve().parent
renders=out/'page_renders';renders.mkdir(exist_ok=True)
doc=fitz.open(pdf);pages=[];thumbs=[]
for idx,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
    image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    image.save(renders/f'page_{idx+1:03d}.png')
    # Analyze every full-page raster, text span and coordinate, not only samples.
    spans=[]
    for block in page.get_text('dict')['blocks']:
        if block.get('type')==0:
            for line in block['lines']:
                spans.extend(line['spans'])
    clipped=[{'text':s['text'][:100],'bbox':s['bbox']} for s in spans
             if s['bbox'][0]<-0.2 or s['bbox'][1]<-0.2 or s['bbox'][2]>page.rect.width+0.2 or s['bbox'][3]>page.rect.height+0.2]
    marginal=[{'text':s['text'][:100],'bbox':s['bbox']} for s in spans
              if s['bbox'][0]<54 or s['bbox'][2]>page.rect.width-54]
    gray=image.convert('L')
    binary=gray.point(lambda x:255 if x<235 else 0)
    ink_bbox=binary.getbbox()
    hist=gray.histogram();ink=sum(hist[:235])/(pix.width*pix.height)
    text=page.get_text()
    pages.append({'page':idx+1,'width_pt':page.rect.width,'height_pt':page.rect.height,
                  'text_characters':len(text),'text_spans':len(spans),'clipped_spans':clipped,
                  'side_margin_spans':marginal,'ink_bbox_pixels':ink_bbox,'ink_fraction':round(ink,5),
                  'fullpage_pixel_sha256':hashlib.sha256(pix.samples).hexdigest(),
                  'page_text_sha256':hashlib.sha256(text.encode()).hexdigest(),
                  'replacement_characters':text.count('\ufffd')})
    image.thumbnail((320,430))
    thumb=Image.new('RGB',(350,460),'#e9edf0');thumb.paste(image,((350-image.width)//2,22))
    ImageDraw.Draw(thumb).text((10,3),f'Page {idx+1}',fill='black')
    thumbs.append(thumb)
for start in range(0,len(thumbs),6):
    subset=thumbs[start:start+6];sheet=Image.new('RGB',(1050,920),'white')
    for i,im in enumerate(subset):sheet.paste(im,((i%3)*350,(i//3)*460))
    sheet.save(out/f'contact_{start+1:02d}_{min(start+6,len(thumbs)):02d}.png')
figures=[]
for p in sorted((out.parents[1]/'traditional/figures').glob('*.pdf')):
    fig=fitz.open(p)
    figures.append({'name':p.name,'pages':len(fig),'raster_images':sum(len(x.get_images()) for x in fig),'vector_drawing_paths':sum(len(x.get_drawings()) for x in fig),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
font_report=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True).stdout
(out/'PDF_FONTS.txt').write_text(font_report)
report={'pdf':pdf.name,'pages':len(doc),'fullpage_render_scale':1.4,
        'blank_pages':[p['page'] for p in pages if p['text_characters']==0],
        'pages_with_clipped_spans':[p['page'] for p in pages if p['clipped_spans']],
        'pages_with_side_margin_spans':[p['page'] for p in pages if p['side_margin_spans']],
        'replacement_characters':sum(p['replacement_characters'] for p in pages),
        'page_results':pages,'figure_results':figures}
(out/'FULL_PAGE_PREFLIGHT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['page_results','figure_results']},indent=2))
print('Contact sheets:',len(list(out.glob('contact_*.png'))))
