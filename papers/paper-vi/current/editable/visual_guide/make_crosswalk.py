#!/usr/bin/env python3
"""Refresh reading links after traditional pagination freezes.

All physical pages are read from actual PDF labels/bookmarks. Reading links do
not imply a shared formal contract or an additional proof-coverage count.
"""
from pathlib import Path
import argparse,csv,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parent
PATTERN=re.compile(r'\\vpage\{(\d+)\}\{([^\n]*?)\}\{([^\n]*?)\}\{([^\n]*?)\}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--traditional-map',type=Path,required=True);p.add_argument('--traditional-pdf',type=Path);p.add_argument('--refresh-source-locators',action='store_true');a=p.parse_args()
 data=json.loads(a.traditional_map.read_text());by_number={str(v['number']):v for v in data.values() if v.get('type')=='record'}
 visual=fitz.open(ROOT/'Paper_VI_Visual_Guide_Final.pdf');visual_physical={int(re.match(r'V(\d+)\.',title)[1]):page for level,title,page in visual.get_toc() if re.match(r'V\d+\.',title)}
 assert set(visual_physical)==set(range(1,43))
 traditional_pdf=a.traditional_pdf or ROOT.parent/'traditional/Paper_VI_Traditional_Final.pdf';traditional=fitz.open(traditional_pdf)
 rows=[]
 for source in ('pages.tex','extensions.tex'):
  path=ROOT/'source'/source;current=path.read_text();original=(ROOT/'historical_assembly/source'/source).read_text();replacements={}
  current_lines={int(m[1]):m[4] for m in PATTERN.finditer(current)}
  for m in PATTERN.finditer(original):
   n=int(m[1]);line=m[4];refs=[]
   for number in re.findall(r'(?<![\w.])E?\d+\.\d+(?!\d)',line):
    if number not in by_number:raise ValueError(f'Unresolved result {number} on V{n}')
    refs.append(by_number[number])
   for match in re.finditer(r'Sections? ([\d,\- and]+)',line):
    for token in re.findall(r'\d+(?:--\d+)?',match[1]):
     section_numbers=range(int(token.split('--')[0]),int(token.split('--')[1])+1) if '--' in token else [int(token)]
     for section in section_numbers:
      key=f'core:section:{section:02d}'
      if key not in data:raise ValueError(f'Unresolved section {section} on V{n}')
      refs.append(data[key])
   selected=[]
   for ref in refs:
    item={k:ref.get(k) for k in ('final_label','number','printed_page','physical_pdf_page','title_tex')}
    if item not in selected:selected.append(item)
    physical=int(ref['physical_pdf_page']);assert traditional[physical-1].get_label()==str(ref['printed_page']),(n,ref)
   printed=sorted(set(str(x['printed_page']) for x in selected),key=lambda x:int(x) if x.isdigit() else x)
   displayed_line=re.sub(r'^Traditional pp?\. [\d, ]+ / ','Traditional ',current_lines[n])
   new_line=displayed_line
   if printed:
    prefix='Traditional '+('p. ' if len(printed)==1 else 'pp. ')+', '.join(printed)+' / '
    new_line=prefix+re.sub(r'^Traditional ', '', displayed_line)
   replacements[n]=new_line
   physical=visual_physical[n]
   rows.append({'visual_page':n,'visual_printed_page':visual[physical-1].get_label(),'visual_physical_pdf_page':physical,'title':m[2],'source_line_original':line,'source_line_current':new_line,'traditional_targets':selected})
  if a.refresh_source_locators:
   current=PATTERN.sub(lambda m:'\\vpage{'+m[1]+'}{'+m[2]+'}{'+m[3]+'}{'+replacements[int(m[1])]+'}',current);path.write_text(current)
 assert len(rows)==42
 report={'traditional_map_sha256':sha(a.traditional_map),'traditional_pdf_sha256':sha(traditional_pdf),'traditional_source_sha256':sha(ROOT.parent/'traditional/Paper_VI_Traditional_Final.tex'),'traditional_source_records_sha256':sha(ROOT.parent/'traditional/SOURCE_RECORDS.json'),'visual_pdf_sha256':sha(ROOT/'Paper_VI_Visual_Guide_Final.pdf'),'scope':'Declared source reading links under page titles. Actual printed and physical pages come from PDF labels/bookmarks. Atlas omits these final PDF locators to avoid a circular pagination/source-hash dependency. No formal scope is inferred from a reading target.','pages':rows}
 (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json').write_text(json.dumps(report,indent=2)+'\n')
 with (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['visual_page','visual_printed_page','visual_pdf_page','title','traditional_record','traditional_printed_page','traditional_pdf_page'])
  for row in rows:
   for target in row['traditional_targets'] or [{}]:w.writerow([row['visual_page'],row['visual_printed_page'],row['visual_physical_pdf_page'],row['title'],target.get('number',''),target.get('printed_page',''),target.get('physical_pdf_page','')])
 print('Resolved all42visualpage source lines against actualPDFlabels.')
if __name__=='__main__':main()
