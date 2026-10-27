#!/usr/bin/env python3
"""Render the final PDF and twelve-page contact sheets for visual review."""
from pathlib import Path
import argparse
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    doc=pdfium.PdfDocument(ROOT/'K_COS_Monograph.pdf')
    for i in range(len(doc)):
        page=doc[i];bitmap=page.render(scale=1.25)
        bitmap.to_pil().convert('RGB').save(args.output/f'page_{i+1:03d}.jpg',quality=90)
        page.close()
    for b in range(0,len(doc),12):
        canvas=Image.new('RGB',(1800,1900),'#e8e6e9');draw=ImageDraw.Draw(canvas)
        for j in range(min(12,len(doc)-b)):
            im=Image.open(args.output/f'page_{b+j+1:03d}.jpg');im.thumbnail((430,600))
            x=(j%4)*450+10;y=(j//4)*630+25
            canvas.paste(im,(x,y));draw.text((x,y-18),f'PDF {b+j+1}',fill='black')
        canvas.save(args.output/f'sheet_{b//12+1:02d}.jpg',quality=94)
    print(f'Rendered {len(doc)} pages.')
if __name__=='__main__':main()
