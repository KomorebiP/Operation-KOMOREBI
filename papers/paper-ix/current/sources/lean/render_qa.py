#!/usr/bin/env python3
"""Render every current guide page and assemble visual-review contact sheets."""
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent
out=H/'qa/current_renders';out.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-r','55','-png',str(H/'Paper_IX_Lean_Guide_Final.pdf'),str(out/'page')],check=True)
files=sorted(out.glob('page-*.png'))
for start in range(0,len(files),24):
    subset=files[start:start+24]
    sheet=Image.new('RGB',(1500,1400),'white')
    for i,f in enumerate(subset):
        im=Image.open(f).convert('RGB');im.thumbnail((230,325))
        tile=Image.new('RGB',(250,350),'#edf1f1');tile.paste(im,((250-im.width)//2,8))
        ImageDraw.Draw(tile).text((12,334),f.stem,fill='black')
        sheet.paste(tile,((i%6)*250,(i//6)*350))
    sheet.save(H/'qa'/f'contact_{start+1:03d}_{start+len(subset):03d}.png')
subprocess.run(['pdftoppm','-f','7','-l','10','-r','130','-png',str(H/'Paper_IX_Lean_Guide_Final.pdf'),str(out/'review')],check=True)
print(f'Rendered {len(files)} current pages and full-size reviewed strengthening pages.')
