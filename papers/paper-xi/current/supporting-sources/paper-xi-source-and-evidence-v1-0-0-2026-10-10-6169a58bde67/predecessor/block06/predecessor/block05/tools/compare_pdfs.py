#!/usr/bin/env python3
"""Compare exact PDF bytes, extracted text, and rendered pixels separately."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import fitz


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('first',type=Path);ap.add_argument('second',type=Path)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--dpi',type=int,default=100)
    a=ap.parse_args()
    if a.dpi<30 or a.dpi>600:raise SystemExit('DPI must be between 30 and 600.')
    x=fitz.open(a.first);y=fitz.open(a.second);rows=[]
    for i in range(min(len(x),len(y))):
        p=x[i].get_pixmap(dpi=a.dpi,alpha=False);q=y[i].get_pixmap(dpi=a.dpi,alpha=False)
        rows.append({'page':i+1,'text_identical':x[i].get_text()==y[i].get_text(),
                     'pixels_identical':(p.width,p.height,p.samples)==(q.width,q.height,q.samples)})
    report={'first_sha256':hashlib.sha256(a.first.read_bytes()).hexdigest(),
            'second_sha256':hashlib.sha256(a.second.read_bytes()).hexdigest(),
            'bytes_identical':a.first.read_bytes()==a.second.read_bytes(),
            'page_counts':[len(x),len(y)],'dpi':a.dpi,'pages':rows,
            'text_identical':len(x)==len(y) and all(r['text_identical'] for r in rows),
            'renders_identical':len(x)==len(y) and all(r['pixels_identical'] for r in rows)}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='pages'},indent=2))
    return int(not(report['text_identical'] and report['renders_identical']))

if __name__=='__main__':raise SystemExit(main())
