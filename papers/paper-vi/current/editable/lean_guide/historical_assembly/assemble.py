#!/usr/bin/env python3
"""Generate documentation from immutable Paper VI source contracts; does not run Lean."""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, re
from data_helpers import active_text, esc

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=HERE.parent/'source/complete/original_snapshot')
parser.add_argument('--verification', type=Path, default=HERE.parent/'verification/run/CURRENT_VERIFICATION.json')
args = parser.parse_args()
SRC = args.source.resolve(); LEAN = SRC/'formalization/lean'
GEN = HERE/'generated'; GEN.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dump = lambda p,x: p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
contract = json.loads((SRC/'verification/source_contract.json').read_text())
ledger = json.loads((SRC/'THEOREM_LEDGER.json').read_text())
targets = contract['theorem_targets']
inherited = json.loads((SRC/'verification/verification_status.json').read_text())
pins = json.loads((LEAN/'lake-manifest.json').read_text())['packages']
fresh = json.loads(args.verification.read_text())
selection = json.loads((HERE/'excerpt_selection.json').read_text())
names = {t['declaration'] for t in targets}
if len(names)!=341 or len(ledger)!=33: raise RuntimeError('Unexpected contract counts')
source_hashes = {p:sha(SRC/p) for p in contract['source_sha256']}
if source_hashes!=contract['source_sha256']:raise RuntimeError('Source contract mismatch')
modules = sorted((LEAN/'KomorebiPaperVI').glob('*.lean'))
if len(modules)!=47:raise RuntimeError('Unexpected module count')
reverse = collections.defaultdict(list)
for row in ledger:
 for target in row['targets']:
  if target not in names: raise RuntimeError('Missing ledger target '+target)
  reverse[target].append(row['number'])
imports = []
for p in modules:
 text=p.read_text()
 imports.append({'module':p.stem,'file':p.relative_to(LEAN).as_posix(),
 'sha256':sha(p),'imports':re.findall(r'(?m)^import (\S+)',active_text(text)),
 'theorem_count':sum(t['file']==p.relative_to(LEAN).as_posix() for t in targets)})
dump(GEN/'imports.json',imports);dump(GEN/'targets.json',targets);dump(GEN/'result_ledger.json',ledger)
dump(GEN/'dependency_pins.json',[{'name':p['name'],'revision':p['rev'],'url':p['url']} for p in pins])
axioms=[]
for name,vals in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",(SRC/'verification/lean_axiom_audit.log').read_text()):
 axioms.append({'declaration':name,'axioms':[v.strip() for v in vals.split(',') if v.strip()]})
if len(axioms)!=341 or {a['declaration'] for a in axioms}!=names:raise RuntimeError('Inherited axiom records mismatch')
dump(GEN/'inherited_axiom_records.json',axioms)
dump(GEN/'evidence_provenance.json',{
 'edition_date':'2026-10-05','edition_timezone':'America/Chicago',
 'documentation_generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'fresh_report_relative_to_package':'verification/run/CURRENT_VERIFICATION.json',
 'fresh_report_sha256':sha(args.verification),'fresh_started_utc':fresh['started_utc'],
 'fresh_finished_utc':fresh['finished_utc'],'fresh_gates':fresh['fresh'],
 'not_run':fresh['not_run'],'inherited_verification':inherited,
 'inherited_evidence_files':{p:sha(SRC/p) for p in ['verification/verification_status.json','verification/lean_build.log','verification/lean_axiom_audit.log','verification/source_contract.json','THEOREM_LEDGER.json']},
 'current_documentation_checks':{'source_hashes':len(source_hashes),'all_source_hashes_match':True,'ledger_targets_resolve':True,'inherited_axiom_target_set_matches':True},
 'lean_kernel_checked_in_current_edition':False})

# The raw excerpt is a contiguous source block through the first blank line.
# The rendered file differs only by explicit font fallback escapes for glyphs
# absent from DejaVu Sans Mono and by escaping TeX command characters.
from fontTools.ttLib import TTFont
import subprocess
font_path=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans Mono'],text=True).strip()
font=TTFont(font_path); cmap={k for table in font['cmap'].tables for k in table.cmap}
excerpts=[]
for tag,sel in selection.items():
 p=LEAN/'KomorebiPaperVI'/f"{sel['module']}.lean";text=p.read_text()
 pattern=r'(?m)^(?:noncomputable )?(?:theorem|def|instance) '+re.escape(sel['name'])+r'\b'
 m=re.search(pattern,text)
 if not m:raise RuntimeError('Excerpt not found '+tag)
 end=text.find('\n\n',m.start());end=len(text) if end<0 else end
 raw=text[m.start():end]+'\n'
 start_line=text[:m.start()].count('\n')+1
 (HERE/'excerpts'/f'{tag}.lean.txt').write_text(raw)
 rendered=''
 for c in raw:
  if c in '\\{}':rendered+=r'\char'+str(ord(c))+'{}'
  elif ord(c)>127 and ord(c) not in cmap:rendered+=r'\CodeSymbol{'+f'{ord(c):X}'+'}'
  else:rendered+=c
 (HERE/'excerpts'/f'{tag}.render.txt').write_text(rendered)
 excerpts.append({'tag':tag,**sel,'source_file':p.relative_to(SRC).as_posix(),'source_sha256':sha(p),
 'start_line':start_line,'end_line':start_line+raw.count('\n')-1,
 'excerpt_sha256':hashlib.sha256(raw.encode()).hexdigest(),'mode':'full contiguous source declaration block'})
dump(GEN/'excerpts.json',excerpts)

out=[]
for row in ledger:
 out.append(r'\subsection{'+esc(row['number']+' — '+row['title'])+'}\n')
 out.append(r'\label{result:'+row['number']+'}\n')
 out.append(r'\textbf{Recorded status.} Complete scoped statement (inherited v0.5.0 ledger).\par\n')
 out.append(esc(row['checked_scope'])+'\n\n')
 out.append(r'\textbf{Declared targets.}\begin{itemize}'+'\n')
 for target in row['targets']:
  record=next(t for t in targets if t['declaration']==target)
  out.append(r'\item \code{'+target+r'}; source line '+str(record['line'])+'.\n')
 out.append(r'\end{itemize}'+'\n')
(GEN/'result_ledger.tex').write_text(''.join(out).replace('\\n','\n'))

out=[]
for p in modules:
 ts=[t for t in targets if t['file']==p.relative_to(LEAN).as_posix()]
 out.append(r'\subsection{'+esc(p.stem)+': '+str(len(ts))+' theorem declarations}\n')
 out.append(r'\source{KomorebiPaperVI/'+p.name+'}\n')
 out.append(r'\begin{longtable}{@{}p{.75\linewidth}p{.19\linewidth}@{}}\toprule Declaration & Line; ledger\\\midrule\endhead'+'\n')
 for t in ts:
  refs=', '.join(reverse[t['declaration']]) or 'support'
  out.append(r'\code{'+t['declaration']+'} & '+str(t['line'])+'; '+refs+r'\\'+'\n')
 out.append(r'\bottomrule\end{longtable}'+'\n')
(GEN/'target_catalog.tex').write_text(''.join(out).replace('\\n','\n'))

out=[r'\begin{longtable}{@{}p{.32\linewidth}p{.61\linewidth}@{}}\toprule Module (targets) & Local imports\\\midrule\endhead'+'\n']
for row in imports:
 local=[i.replace('KomorebiPaperVI.','') for i in row['imports'] if i.startswith('KomorebiPaperVI.')]
 out.append(r'\code{'+row['module']+'} ('+str(row['theorem_count'])+') & '+('; '.join(r'\code{'+x+'}' for x in local) if local else 'Mathlib only')+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n');(GEN/'imports.tex').write_text(''.join(out))
out=[r'\begin{longtable}{@{}p{.21\linewidth}p{.72\linewidth}@{}}\toprule Dependency & Locked revision\\\midrule\endhead'+'\n']
for p in pins:out.append(esc(p['name'])+r' & \code{'+p['rev']+r'}\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n');(GEN/'pins.tex').write_text(''.join(out))
dump(GEN/'documentation_reconciliation.json',{'status':'PASS','ledger_records':len(ledger),'theorem_targets':len(targets),'modules':len(modules),'selected_excerpts':len(excerpts),'source_hash_entries':len(source_hashes),'dependency_pins':len(pins),'inherited_axiom_records':len(axioms),'fresh_kernel_run':False})
print(json.dumps({'targets':len(targets),'ledger_records':len(ledger),'modules':len(modules),'excerpts':len(excerpts)}))
