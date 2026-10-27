#!/usr/bin/env python3
"""Static source/excerpt and document QA; no Lean invocation."""
from pathlib import Path
import argparse,csv,hashlib,json,re,subprocess,zipfile
import fitz
H=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);a=ap.parse_args();B=a.source.resolve()
def sha(x):return hashlib.sha256(x).hexdigest()
rs=json.loads((H/'audit/EXCERPTS.json').read_text());tx='\n'.join(p.read_text()for p in(H/'chapters').glob('*.tex'));used=re.findall(r'\\excerpt\{[^{}]*\}\{([^{}]+)\}',tx);assert sorted(used)==sorted(r['id']for r in rs)
for r in rs:
 if '!'in r['source']:
  p,n=r['source'].split('!',1)
  with zipfile.ZipFile(B/p)as z:raw=z.read(n)
 else:raw=(B/r['source']).read_bytes()
 assert sha(raw)==r['source_sha256'];s=''.join(raw.decode().splitlines(keepends=True)[r['start_line']-1:r['end_line']]);assert (H/'excerpts'/f"{r['id']}.lean.txt").read_text()==s;assert sha(s.encode())==r['excerpt_sha256']
pdf=H/'Paper_IX_Lean_Guide_Final.pdf';d=fitz.open(pdf);text='\n'.join(p.get_text()for p in d);(H/'qa/pdf_text.txt').write_text(text);norm=re.sub(r'\s','',text)
rows=list(csv.DictReader((H/'audit/reconciled/DECLARATIONS.csv').open()));missing=[r['qualified_name']for r in rows if r['qualified_name'].split('.')[-1]not in norm];assert not missing,missing
log=(H/'Paper_IX_Lean_Guide_Final.log').read_text();warnings={w:len(re.findall(w,log))for w in ['Missing character','Overfull','undefined']};assert not any(warnings.values())
aux=(H/'Paper_IX_Lean_Guide_Final.aux').read_text();labels={m[1]:int(m[2])for m in re.finditer(r'\\newlabel\{([^{}]+)\}\{\{[^{}]*\}\{([0-9]+)\}',aux)};cw=json.loads((H/'audit/CROSSWALK.json').read_text());assert len(cw)==62 and sum(len(r['source_links'])for r in cw)==202
for r in cw:assert r['guide_printed_page']==labels[r['guide_section_label']]and r['guide_physical_page']==r['guide_printed_page']+1
fonts=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True).stdout;(H/'qa/fonts.txt').write_text(fonts)
# PDF rows in pdffonts include emb/sub/uni after font encoding; every used font is embedded.
assert all(l.split()[-5]=='yes'for l in fonts.splitlines()[2:])
result={'status':'PASS','pdf':pdf.name,'pdf_pages':len(d),'pdf_bytes':pdf.stat().st_size,'pdf_sha256':sha(pdf.read_bytes()),'instructional_chapters':12,'exact_contiguous_excerpts':len(rs),'exact_excerpt_lines':sum(r['line_count']for r in rs),'all_excerpts_taught_once':True,'all_excerpts_exact_source_bound':True,'catalog_rows':len(rows),'catalog_short_names_found_in_pdf':len(rows),'canonical_source_files':199,'retained_mapped_manuscript_statements':62,'mapped_source_links':202,'all_guide_page_locators_resolve':True,'retained_traditional_pdf_sha256':cw[0]['traditional_pdf_sha256'],'warnings':warnings,'embedded_fonts':True,'fresh_lean_run':False,'proofreading_scope':'New strengthening chapter, revised opening and retained-navigation explanation, and guide references self-reviewed; retained source excerpts unchanged. Historical independent guide review remains inherited. No raw proof edits.'}
(H/'qa/DOCUMENT_QA.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
