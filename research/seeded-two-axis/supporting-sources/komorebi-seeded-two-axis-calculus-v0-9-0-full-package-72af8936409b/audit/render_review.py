#!/usr/bin/env python3
"""Render with PyMuPDF for repeatable contact-sheet and geometry review."""
from pathlib import Path
import json, argparse
import fitz
from PIL import Image, ImageDraw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-dir', type=Path, default=Path('/mnt/data/k09_work/final_renders'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.render_dir; output.mkdir(parents=True, exist_ok=True)
    pdf = fitz.open(root/'Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.pdf')
    contact = root/'audit/contact_sheets'; contact.mkdir(exist_ok=True)
    for old in contact.glob('*.png'): old.unlink()
    paths=[]; flagged=[]
    for index,page in enumerate(pdf,1):
        path=output/f'page-{index:02d}.png';page.get_pixmap(dpi=105).save(path);paths.append(path)
        for word in page.get_text('words'):
            x0,y0,x1,y1,*_=word
            if x0<10 or y0<10 or x1>page.rect.width-10 or y1>page.rect.height-10:
                flagged.append([index,word])
    w,h=306,426
    for start in range(0,len(paths),16):
        sheet=Image.new('RGB',(4*w,4*(h+24)),'white');draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(paths[start:start+16]):
            image=Image.open(path).convert('RGB');image.thumbnail((w-8,h-8))
            x=(j%4)*w+(w-image.width)//2;y=(j//4)*(h+24)+22
            sheet.paste(image,(x,y));draw.text(((j%4)*w+8,(j//4)*(h+24)+5),f'Page {start+j+1}',fill='black')
        sheet.save(contact/f'contact_{start+1:02d}_{min(start+16,len(paths)):02d}.png')
    result={'pages':len(pdf),'rendered_pages':len(paths),'renderer':f'PyMuPDF {fitz.VersionBind}',
            'render_dpi':105,'words_within_10pt_of_page_edge':flagged,
            'note':'Geometry and rendering checks are not a substitute for visual inspection.'}
    (root/'audit/layout_geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    for index in [1,4,*range(47,57),71,72,84,85,86,87]:
        if index <= len(pdf):
            pdf[index-1].get_pixmap(dpi=145).save(output/f'detail_{index:02d}.png')
if __name__=='__main__': main()
