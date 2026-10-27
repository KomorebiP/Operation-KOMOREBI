from pathlib import Path
import json,hashlib,zipfile,io,datetime,re
import fitz
W=Path('/dev/shm/komorebi_paper_xii_freeze_fbc994080222');B=W/'baseline';A=W/'audit_licenses'
def h(x):return hashlib.sha256(x).hexdigest()
def name(s):return re.sub(r'^[A-Z]{6}\+','',s or '').removesuffix('-Identity-H')
def pdfrow(data,path):
 r={'path':path,'bytes':len(data),'sha256':h(data)}
 try:
  with fitz.open(stream=data,filetype='pdf') as d:r.update({'pages':len(d),'resource_font_names':sorted({name(f[3]) for i in range(len(d)) for f in d.get_page_fonts(i,full=True)})})
 except Exception as e:r['error']=str(e)
 return r
loose=[];archives=[];font_files=[];pdfmembers=[];errors=[]
font_ext={'.ttf','.otf','.ttc','.pfb','.pfa','.woff','.woff2'}
def archive(data,path,depth=0):
 if depth>8:raise RuntimeError('archive recursion exceeded bounded audit limit')
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  r={'path':path,'bytes':len(data),'sha256':h(data),'member_count':len(z.infolist()),'standalone_fonts':[],'nested_archives':[],'pdf_members':0};archives.append(r)
  for i in z.infolist():
   if i.is_dir():continue
   ext=Path(i.filename).suffix.lower();p=path+'!/'+i.filename
   if ext in font_ext:
    row={'path':p,'bytes':i.file_size,'sha256':h(z.read(i))};font_files.append(row);r['standalone_fonts'].append(row)
   elif ext=='.pdf':pdfmembers.append(pdfrow(z.read(i),p));r['pdf_members']+=1
   elif ext=='.zip':r['nested_archives'].append(p);archive(z.read(i),p,depth+1)
for p in sorted(B.rglob('*')):
 if not p.is_file():continue
 ext=p.suffix.lower();rel=p.relative_to(B).as_posix()
 if ext=='.pdf':loose.append(pdfrow(p.read_bytes(),rel))
 elif ext in font_ext:font_files.append({'path':rel,'bytes':p.stat().st_size,'sha256':h(p.read_bytes())})
 elif ext=='.zip' and not rel.startswith('outer/'):
  try:archive(p.read_bytes(),rel)
  except Exception as e:errors.append({'path':rel,'error':str(e)})
# The outer three nested archives are exact containers of the extracted core,
# reader set and receipts already inventoried above. Scan those as raw retained
# containers too, preserving separate occurrence counts instead of deduplicating.
for p in sorted((B/'outer').glob('*.zip')):
 try:archive(p.read_bytes(),'outer/'+p.name)
 except Exception as e:errors.append({'path':'outer/'+p.name,'error':str(e)})
r={'audit':'All selected baseline loose PDFs and recursively retained ZIP PDF/font members','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Resource inventory and parseability; no exact historical font-program origin certification. Current three-reader program metadata is separate. Repeated extracted/container occurrences are counted separately.','loose_pdfs':loose,'archives':archives,'archive_pdf_occurrences':pdfmembers,'standalone_font_files':font_files,'archive_errors':errors,'counts':{'loose_pdf_paths':len(loose),'zip_occurrences':len(archives),'archive_pdf_occurrences':len(pdfmembers),'standalone_font_occurrences':len(font_files),'pdf_parse_errors':sum('error' in x for x in loose+pdfmembers)},'resource_name_union':sorted({n for x in loose+pdfmembers for n in x.get('resource_font_names',[])})}
(A/'HISTORICAL_FONT_INVENTORY.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['counts']));print('resource_names',r['resource_name_union']);print('archive_errors',errors)
