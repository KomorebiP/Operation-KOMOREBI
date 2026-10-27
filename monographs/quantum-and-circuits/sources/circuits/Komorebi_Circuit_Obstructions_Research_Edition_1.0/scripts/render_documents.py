"""Render every finished page and make contact sheets for human inspection."""
from pathlib import Path
import argparse,json
import fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
DOCS={'main':'Komorebi_Circuit_Obstructions_Main_Paper.pdf',
      'visual':'Komorebi_Circuit_Obstructions_Visual_Guide.pdf',
      'lean':'Komorebi_Circuit_Obstructions_Lean_Guide.pdf'}

def render(name):
    d=fitz.open(ROOT/'output'/DOCS[name]);dest=ROOT/'reviews'/('render_'+name)
    dest.mkdir(exist_ok=True)
    for pattern in ['page-*.png','contact-*.png']:
        for p in dest.glob(pattern):p.unlink()
    for i,page in enumerate(d):
        page.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(dest/f'page-{i+1:03}.png')
    for k in range((len(d)+15)//16):
        sheet=Image.new('RGB',(1600,2280),'#dbe3df');draw=ImageDraw.Draw(sheet)
        for j in range(16):
            idx=16*k+j
            if idx>=len(d):break
            im=Image.open(dest/f'page-{idx+1:03}.png');im.thumbnail((376,518))
            x=12+(j%4)*400;y=30+(j//4)*565
            sheet.paste(im,(x,y));draw.text((x,y-18),str(idx+1),fill='#173238')
        sheet.save(dest/f'contact-{k+1}.png')
    return {'document':name,'pages':len(d),'rendered_pages':len(d),
            'contact_sheets':(len(d)+15)//16}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('names',nargs='*',choices=list(DOCS))
    args=p.parse_args();results=[render(x) for x in (args.names or DOCS)]
    print(json.dumps(results,indent=2))
