from pathlib import Path
import json,hashlib,subprocess,os,re,concurrent.futures,argparse,shutil
ROOT=Path(__file__).resolve().parent
def prepare_fonts(output_root=None):
 """Restore omitted local font payloads from exact installed-font hashes."""
 target_root=(output_root or ROOT).resolve()
 manifest=json.loads((ROOT/'MONOGRAPH_FONT_DEPENDENCIES.json').read_text())
 resolved={};rows=[]
 for item in manifest['files']:
  key=(item['name'],item['sha256'])
  if key not in resolved:
   query=subprocess.run(['kpsewhich',item['name']],capture_output=True,text=True,check=True)
   name=query.stdout.strip();source=Path(name)
   if not name or not source.is_file():raise RuntimeError('Install external font: '+item['name'])
   actual=hashlib.sha256(source.read_bytes()).hexdigest()
   if actual!=item['sha256']:raise RuntimeError('External font version differs: '+item['name']+'; expected '+item['sha256']+', found '+actual)
   resolved[key]=source
  destination=target_root/item['relative_path'];destination.parent.mkdir(parents=True,exist_ok=True)
  if destination.is_symlink():destination.unlink()
  if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest()!=item['sha256']:
   shutil.copyfile(resolved[key],destination)
  if hashlib.sha256(destination.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('Font copy verification failed: '+str(destination))
  rows.append({'relative_path':item['relative_path'],'installed_source':str(resolved[key]),'sha256':item['sha256']})
 record={'status':'PASS','fonts':rows,'font_files':len(rows),'unique_installed_fonts':len(resolved),'no_tex_compilation':True}
 target_root.mkdir(parents=True,exist_ok=True)
 (target_root/'FONT_PREPARATION.json').write_text(json.dumps(record,indent=2)+'\n')
 return record
def build(e):
 p=Path(e['source']);d=ROOT/'compiled'/e['paper']/e['role'];d.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,TMPDIR=str(ROOT),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1');env['TEXINPUTS']=str(p.parent)+':';env['BIBINPUTS']=str(p.parent)+':';env['BSTINPUTS']=str(p.parent)+':'
 cmd=[e['engine'],'-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(d),p.name]
 runs=[]
 for i in range(4):
  proc=subprocess.run(cmd,cwd=p.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  (d/f'pass_{i+1}.txt').write_text(proc.stdout);runs.append(proc.returncode)
  if proc.returncode:break
  aux=d/(p.stem+'.aux')
  if i==0 and '\\bibdata' in aux.read_text(errors='replace'):
   b=subprocess.run(['bibtex',p.stem],cwd=d,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(d/'bibtex.txt').write_text(b.stdout);runs.append(b.returncode)
   if b.returncode:break
 pdf=d/(p.stem+'.pdf');log=d/(p.stem+'.log');txt=log.read_text(errors='replace') if log.exists() else ''
 warnings=[ln for ln in txt.splitlines() if re.search('Overfull|Missing character|undefined references|undefined citations|undefined on input|LaTeX Error|^!',ln)]
 result={**e,'runs':runs,'status':'passed' if all(x==0 for x in runs) else 'failed','pdf':str(pdf),'warnings':warnings}
 if result['status']=='passed':
  import fitz
  doc=fitz.open(pdf);result['pages']=len(doc);result['sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest()
 print(json.dumps({k:result[k] for k in ['paper','role','status','runs','warnings']},ensure_ascii=False),flush=True)
 return result

if __name__=='__main__':
 import sys
 parser=argparse.ArgumentParser(description='Build I-IV source components with exact installed-font dependencies.')
 parser.add_argument('components',nargs='*',help='Optional paper:role selectors.')
 parser.add_argument('--prepare-fonts-only',action='store_true',help='Resolve, hash-check and restore font files without running TeX.')
 parser.add_argument('--font-output-root',type=Path,help='For --prepare-fonts-only: stage fonts in a separate initially empty directory.')
 args=parser.parse_args()
 if args.font_output_root is not None and not args.prepare_fonts_only:parser.error('--font-output-root requires --prepare-fonts-only')
 font_record=prepare_fonts(args.font_output_root)
 if args.prepare_fonts_only:
  print(json.dumps({k:font_record[k] for k in ['status','font_files','unique_installed_fonts','no_tex_compilation']}));raise SystemExit(0)
 entries=json.loads((ROOT/'selected_sources.json').read_text())
 if args.components:entries=[e for e in entries if e['paper']+':'+e['role'] in args.components]
 # Resolve retained metadata paths against this package for portability.
 for e in entries:
  p=Path(e['source']);suffix=p.parts[p.parts.index('source_i_iv')+1:];e['source']=str(ROOT.joinpath(*suffix))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(build,entries))
 prior=json.loads((ROOT/'build_results.json').read_text())
 keys={(e['paper'],e['role']) for e in out};out+=[e for e in prior if (e['paper'],e['role']) not in keys]
 (ROOT/'build_results.json').write_text(json.dumps(out,indent=2))
