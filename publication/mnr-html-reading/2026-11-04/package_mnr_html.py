"""Package authenticated semantic chapter bodies separately from Pages storage."""
from pathlib import Path
import gzip,hashlib,html,json,re,shutil
import pypdfium2 as pdf
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'output/mnr-html-work'
SOURCE=ROOT/'output/MNR'
PREFIX='publication/mnr-html-reading/2026-11-04'
OUT=ROOT/'site'/PREFIX
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    figures=json.loads((WORK/'figures.json').read_bytes())
    for n in (1,2):
        page=pdf.PdfDocument(ROOT/f'output/mnr-figure-work/diagram-{n}.pdf')[0]
        image=page.render(scale=1600/page.get_width()).to_pil().convert('RGB')
        path=WORK/f'figures/diagram-{n}.webp';image.save(path,lossless=True,method=6)
        figures.append(dict(file=path.name,width=image.width,height=image.height,bytes=path.stat().st_size,sha256=sha(path.read_bytes()),display_width=round(page.get_width()*96/72)))
    lookup={x['file']:x for x in figures}
    for folder in ['figures','source/chapters','source/definitions','parts']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    sources=[]
    for path in [SOURCE/'main.tex',SOURCE/'definitions/components.tex',*sorted((SOURCE/'chapters').glob('*.tex'))]:
        name=path.relative_to(SOURCE).as_posix();target=OUT/'source'/name;shutil.copyfile(path,target)
        sources.append(dict(path='source/'+name,sha256=sha(path.read_bytes())))
    for row in figures:shutil.copyfile(WORK/'figures'/row['file'],OUT/'figures'/row['file'])
    meta=json.loads((WORK/'reading-metadata.json').read_bytes());packed=[];buffers=[bytearray()]
    for entry in meta['pages']:
        body=(WORK/'pages'/entry['file']).read_text(encoding='utf-8')
        def size(m):
            tag=m[0];name=re.search(r'mnr-figure/([^" ]+)',tag)[1];f=lookup[name]
            display=f.get('display_width',760)
            return tag.replace('<img ','<img loading="lazy" decoding="async" style="max-width:'+str(min(760,display))+'px" ',1)
        body=re.sub(r'<img\b[^>]*>',size,body)
        def caption(m):
            block=m[0];image=re.search(r'mnr-figure/(figure-\d+\.webp)',block)
            if image:
                number=lookup[image[1]].get('number','')
                if number:block=block.replace('<figcaption','<figcaption',1).replace('<figcaption>','<figcaption><strong>Figure '+html.escape(number)+'.</strong> ',1)
            return block
        body=re.sub(r'<figure\b.*?</figure>',caption,body,flags=re.S)
        raw=body.encode();compressed=gzip.compress(raw,compresslevel=9,mtime=0)
        if len(buffers[-1])+len(compressed)>512*1024:buffers.append(bytearray())
        part=len(buffers);offset=len(buffers[-1]);buffers[-1].extend(compressed)
        preview=next((p for p in re.findall(r'<p>.*?</p>',body,re.S) if len(re.sub('<[^>]+>','',p))>35),'<p>'+html.escape(entry['title'])+'</p>')
        source='source/main.tex';line=1
        if entry.get('chapter'):
            token=r'\label{'+entry['id']+'}'
            for s in sources:
                text=(OUT/s['path']).read_text(encoding='utf-8')
                if token in text:
                    source=s['path'];pos=text.index(token);line=text.count('\n',0,max(0,text.rfind(r'\chapter',0,pos)))+1;break
        packed.append(dict(**entry,payload=dict(part=f'parts/{part:03}.bin',offset=offset,bytes=len(compressed),html_sha256=sha(raw),html_bytes=len(raw)),preview=preview,source=source,line=line))
    parts=[]
    for i,buffer in enumerate(buffers,1):
        name=f'parts/{i:03}.bin';(OUT/name).write_bytes(buffer);parts.append(dict(path=name,bytes=len(buffer),sha256=sha(buffer)))
    partmap={p['path']:p for p in parts}
    for p in packed:p['payload']['part_sha256']=partmap[p['payload']['part']]['sha256']
    result={k:v for k,v in meta.items() if k not in ('pages','aliases')};result.update(pages=packed,payload_parts=parts,images=figures,sources=sources,prefix=PREFIX,converter='Pandoc 3.13',mathjax_validation=json.loads((WORK/'MATHJAX_AUDIT.json').read_bytes()))
    (OUT/'READING.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    # A contact sheet is a local visual QA artifact, not a website asset.
    sheet=Image.new('RGB',(1200,((len(figures)+4)//5)*150),'#ecece8');draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(figures):
        im=Image.open(WORK/'figures'/f['file']);im.thumbnail((230,125));x=(i%5)*240;y=(i//5)*150
        sheet.paste(im,(x+(240-im.width)//2,y));draw.text((x+5,y+127),f['file'],fill='black')
    sheet.save(WORK/'figure-contact-sheet.jpg')
    (OUT/'.gitattributes').write_text('*.bin binary\n*.webp binary\n*.tex -text\n*.json -text\n',encoding='ascii')
    print(json.dumps(dict(pages=len(packed),parts=parts,images=len(figures),html_bytes=sum(p['payload']['html_bytes'] for p in packed))))
if __name__=='__main__':main()
