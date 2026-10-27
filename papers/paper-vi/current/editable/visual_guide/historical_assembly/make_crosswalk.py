#!/usr/bin/env python3
"""Resolve visual source references against the traditional final label map.
Run after traditional pagination freezes. No PDF is changed.
"""
from pathlib import Path
import argparse,hashlib,json,re,csv
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--traditional-map',type=Path,required=True);args=p.parse_args()
 data=json.loads(args.traditional_map.read_text());by_number={}
 for k,v in data.items():
  if v.get('type')=='record':by_number[str(v['number'])]=v
 rows=[]
 for source in ('pages.tex','extensions.tex'):
  text=(ROOT/'source'/source).read_text()
  for m in re.finditer(r'\\vpage\{(\d+)\}\{([^\n]*?)\}\{([^\n]*?)\}\{([^\n]*?)\}',text):
   n=int(m[1]);line=m[4];refs=[]
   # The displayed source line may contain both E and core record numbers.
   for num in re.findall(r'(?<![\w.])E?\d+\.\d+(?!\d)',line):
    if num not in by_number:raise ValueError(f'Unresolved result {num} on V{n}')
    a=by_number[num];refs.append({k:a.get(k) for k in ('final_label','number','printed_page','physical_pdf_page','title_tex')})
   for sm in re.finditer(r'Sections? ([\d,\- and]+)',line):
    for token in re.findall(r'\d+(?:--\d+)?',sm[1]):
     values=range(int(token.split('--')[0]),int(token.split('--')[1])+1) if '--' in token else [int(token)]
     for section in values:
      key=f'core:section:{section:02d}'
      if key in data:
       a=data[key];refs.append({k:a.get(k) for k in ('final_label','number','printed_page','physical_pdf_page','title_tex')})
   rows.append({'visual_page':n,'visual_physical_pdf_page':n+2,'title':m[2],'source_line':line,'traditional_targets':refs})
 assert len(rows)==42
 report={'traditional_map_sha256':hashlib.sha256(args.traditional_map.read_bytes()).hexdigest(),'scope':'Declared source references beneath visual page titles. A target is a reading link, not a claim of identical formal scope. V28/V42 refer to edition evidence and may have no result target.','pages':rows}
 (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json').write_text(json.dumps(report,indent=2)+'\n')
 with (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['visual_page','visual_pdf_page','title','traditional_record','traditional_printed_page','traditional_pdf_page'])
  for row in rows:
   for t in row['traditional_targets'] or [{}]:w.writerow([row['visual_page'],row['visual_physical_pdf_page'],row['title'],t.get('number',''),t.get('printed_page',''),t.get('physical_pdf_page','')])
 print('Resolved all 42 visual page source lines.')
if __name__=='__main__':main()
