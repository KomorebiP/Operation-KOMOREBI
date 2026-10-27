#!/usr/bin/env python3
"""Refresh visual reading locators only after traditional pagination freezes.

Exact label targets come from the retrieved crosswalk. Printed and physical
pages are read from the current canonical map and verified against PDF labels.
The integrated atlas never receives these locators, avoiding circular pagination.
"""
from pathlib import Path
import argparse,csv,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parent
PATTERN=re.compile(r'\\vpage\{(\d+)\}\{([^\n]*?)\}\{([^\n]*?)\}\{([^\n]*?)\}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--traditional-map',type=Path,required=True);p.add_argument('--traditional-pdf',type=Path);p.add_argument('--refresh-source-locators',action='store_true');a=p.parse_args()
 raw=json.loads(a.traditional_map.read_text());data=raw.get('labels',raw);traditional_pdf=a.traditional_pdf or ROOT.parent/'traditional/Paper_VII_Traditional_Final.pdf';traditional=fitz.open(traditional_pdf)
 inherited={r['visual_page']:r for r in json.loads((ROOT/'historical_assembly/SOURCE_CROSSWALK.json').read_text())}
 visual=fitz.open(ROOT/'Paper_VII_Visual_Guide_Final.pdf');physical={int(re.match(r'V(\d+)\.',title)[1]):page for level,title,page in visual.get_toc() if re.match(r'V\d+\.',title)}
 assert set(physical)==set(range(1,41)),physical
 rows=[]
 for name in ['pages.tex','extended_pages.tex']:
  source=ROOT/'source'/name;s=source.read_text();replacements={}
  for m in PATTERN.finditer(s):
   n=int(m[1]);selected=[]
   for target in inherited[n]['targets']:
    label=target.get('final_label',target['label']);entry=data.get(label)
    if entry is None:raise ValueError(f'Missing current traditional label {label} for V{n}')
    number=str(entry['number']);assert number==str(target['number']),(label,number,target['number'])
    pdfpage=int(entry.get('physical_pdf_page',entry.get('physical_page')));printed=str(entry['printed_page']);assert traditional[pdfpage-1].get_label()==printed,(label,pdfpage,printed)
    selected.append({'final_label':label,'number':number,'printed_page':printed,'physical_pdf_page':pdfpage,'title_tex':entry.get('title_tex',entry.get('title','')),'kind':target['kind']})
   pages=sorted({t['printed_page'] for t in selected},key=lambda x:int(x) if x.isdigit() else x)
   line=re.sub(r'^Traditional edition:\s*','',m[4])
   line=re.sub(r'^Traditional pp?\. [0-9, ]+ / ','',line)
   line='Traditional '+('p. ' if len(pages)==1 else 'pp. ')+', '.join(pages)+' / '+line
   replacements[n]=line;vphysical=physical[n]
   rows.append({'visual_page':n,'visual_physical_pdf_page':vphysical,'visual_printed_page':visual[vphysical-1].get_label(),'title':m[2],'source_line_original':inherited[n]['source_line'],'source_line_current':line,'traditional_targets':selected})
  if a.refresh_source_locators:
   source.write_text(PATTERN.sub(lambda m:'\\vpage{'+m[1]+'}{'+m[2]+'}{'+m[3]+'}{'+replacements[int(m[1])]+'}',s))
 assert len(rows)==40
 traditional_root=ROOT.parent/'traditional'
 report={'status':'PASS','traditional_map_sha256':sha(a.traditional_map),'traditional_pdf_sha256':sha(traditional_pdf),'traditional_source_sha256':sha(traditional_root/'Paper_VII_Traditional_Final.tex'),'visual_pdf_sha256':sha(ROOT/'Paper_VII_Visual_Guide_Final.pdf'),'scope':'Exact declared reading labels under40visualpage titles, checked against actual printed and physical PDF labels. The atlas omits final locators. Reading references do not expand formal scope.','pages':sorted(rows,key=lambda r:r['visual_page'])}
 records=traditional_root/'current_source_records.json'
 if not records.exists():records=traditional_root/'SOURCE_RECORDS.json'
 if records.exists():report['traditional_source_records_sha256']=sha(records)
 (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json').write_text(json.dumps(report,indent=2)+'\n')
 # Compatibility source crosswalk uses the same current checked targets.
 (ROOT/'SOURCE_CROSSWALK.json').write_text(json.dumps([{'visual_page':r['visual_page'],'title':r['title'],'source_line':r['source_line_current'],'targets':[dict(t,label=t['final_label'],traditional_page=t['printed_page'],physical_page=t['physical_pdf_page']) for t in r['traditional_targets']]} for r in report['pages']],indent=2)+'\n')
 with (ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['visual_page','visual_printed_page','visual_pdf_page','title','traditional_label','traditional_number','traditional_printed_page','traditional_pdf_page'])
  for r in report['pages']:
   for t in r['traditional_targets']:w.writerow([r['visual_page'],r['visual_printed_page'],r['visual_physical_pdf_page'],r['title'],t['final_label'],t['number'],t['printed_page'],t['physical_pdf_page']])
 (ROOT/'SOURCE_CROSSWALK.md').write_text('# Paper VII visual reading crosswalk\n\nCurrent printed traditional pages are verified against actual PDF labels. Physical pages are recorded separately in the JSON and CSV. These references do not enlarge formal scope.\n\n| Worked page | Title | Source line |\n|---|---|---|\n'+'\n'.join(f"| V{r['visual_page']} | {r['title']} | {r['source_line_current']} |" for r in report['pages'])+'\n')
 print('PASS: all40 visual reading lines resolve to current traditional PDF labels.')
if __name__=='__main__':main()
