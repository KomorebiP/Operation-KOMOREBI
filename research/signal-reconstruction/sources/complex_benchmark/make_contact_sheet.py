from pathlib import Path
import subprocess
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parent
PDF=ROOT/'Complex_Signal_Image_Gibbs_Benchmark.pdf'
RENDER=ROOT/'rendered_contact'
RENDER.mkdir(exist_ok=True)
subprocess.run(['python','/home/oai/skills/pdfs/scripts/render_pdf.py',str(PDF),'--out_dir',str(RENDER),'--dpi','150'],check=True)
files=sorted(RENDER.glob('page-*.png'))
thumb=(240,310)
cols=4
rows=(len(files)+cols-1)//cols
margin=16
label=24
sheet=Image.new('RGB',(margin+cols*(thumb[0]+margin),margin+rows*(thumb[1]+label+margin)),(250,250,247))
draw=ImageDraw.Draw(sheet)
for i,path in enumerate(files):
    image=Image.open(path).convert('RGB')
    image.thumbnail(thumb)
    panel=Image.new('RGB',thumb,(255,255,255))
    panel.paste(image,((thumb[0]-image.width)//2,(thumb[1]-image.height)//2))
    panel=ImageOps.expand(panel,border=1,fill=(170,170,170))
    r=i//cols
    c=i%cols
    x=margin+c*(thumb[0]+margin)
    y=margin+r*(thumb[1]+label+margin)
    sheet.paste(panel,(x,y))
    draw.text((x+4,y+thumb[1]+3),f'page {i+1}',fill=(20,20,20))
out=ROOT/'Complex_Signal_Image_Gibbs_Benchmark_Contact_Sheet.png'
sheet.save(out)
print(out)
