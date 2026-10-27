#!/usr/bin/env python3
"""Compare all inherited lesson bodies against the inspected v0.3 baseline."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('baseline_renders',type=Path)
    parser.add_argument('current_renders',type=Path)
    args=parser.parse_args()
    baseline=json.loads((ROOT/'evidence/edition_v0.3/lesson_index.json').read_text())
    current=json.loads((ROOT/'evidence/lesson_index.json').read_text())
    oldqa=json.loads((ROOT/'evidence/edition_v0.3/FINAL_QA.json').read_text())
    basepdf=ROOT/'Komorebi_Special_Functions_Expanded_Visual_Guide_v0.3.pdf'
    newpdf=ROOT/'Komorebi_Special_Functions_Expanded_Visual_Guide_v0.4.pdf'
    assert digest(basepdf)==oldqa['final_pdf_sha256']
    assert len(baseline)==158 and len(current)==171
    rows=[]
    for i,item in enumerate(baseline):
        new=current[i]
        assert item['lesson']==new['lesson'] and item['figure']==new['figure'] and item['title']==new['title']
        a=args.baseline_renders/f"page-{item['physical_page']:03}.png"
        b=args.current_renders/f"page-{new['physical_page']:03}.png"
        old=Image.open(a).convert('RGB');final=Image.open(b).convert('RGB')
        assert old.size==final.size
        box=(0,62,old.width,old.height)
        difference=ImageChops.difference(old.crop(box),final.crop(box))
        rows.append({'lesson':item['lesson'],'baseline_page':item['physical_page'],'current_page':new['physical_page'],'baseline_png_sha256':digest(a),'current_png_sha256':digest(b),'body_footer_pixels_identical':difference.getbbox() is None})
    changed=[r['lesson'] for r in rows if not r['body_footer_pixels_identical']]
    result={'status':'PASS' if not changed else 'NEEDS_REVIEW','baseline_pdf_sha256':digest(basepdf),'final_pdf_sha256':digest(newpdf),'inherited_lessons':158,'render_dpi':110,'header_crop_top_pixels':62,'mismatched_lessons':changed,'scope':'All 158 inherited lesson bodies and footers compared to the inspected v0.3 edition. The changed edition header is inspected separately.','lessons':rows}
    (ROOT/'evidence/V04_INHERITED_RENDER_BRIDGE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='lessons'}))
    raise SystemExit(0 if not changed else 1)

if __name__=='__main__':main()
