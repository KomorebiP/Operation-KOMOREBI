#!/usr/bin/env python3
"""Reconcile the Paper IV guide with immutable source. Never invokes Lean."""
from pathlib import Path
import argparse, hashlib, json, re
from data_helpers import active_text, esc, prose
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=HERE/'../../source/complete/original_snapshot/lean_release/PRSC_IV');ap.add_argument('--traditional',type=Path,default=HERE/'../traditional');a=ap.parse_args()
root=a.source.resolve();lean=root/'formalization/lean';gen=HERE/'generated';ex=HERE/'excerpts'
gen.mkdir(exist_ok=True);ex.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,o): (gen/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
manifest={}
for l in (root/'SHA256SUMS.txt').read_text().splitlines():
 m=re.match(r'^([0-9a-f]{64})\s+\*?\.?/?(.+)$',l)
 if m:manifest[m[2]]=m[1]
sources={str(p.relative_to(lean)):p for p in sorted(lean.rglob('*.lean')) if '.lake' not in p.parts}
checks=[{'file':'formalization/lean/'+n,'sha256':sha(p),'manifest_sha256':manifest.get('formalization/lean/'+n),'matches':sha(p)==manifest.get('formalization/lean/'+n)} for n,p in sources.items()]
assert all(x['matches'] for x in checks)
index={};short={}
for n,p in sources.items():
 stack=[]
 for ln,l in enumerate(active_text(p.read_text()).splitlines(),1):
  m=re.match(r'^\s*(?:noncomputable\s+)?(namespace|section)\b\s*([^\s]*)',l)
  if m:stack.append((m[1],m[2]));continue
  if re.match(r'^\s*end\b',l):
   if stack:stack.pop()
   continue
  m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected)\s+)*(def|theorem|lemma|structure|abbrev|class|inductive|instance)\s+([^\s({:]+)',l)
  if m:
   fullname='.'.join([v for k,v in stack if k=='namespace' and v]+[m[2]])
   loc={'file':n,'line':ln,'kind':m[1]};index[fullname]=loc;short.setdefault(m[2],[]).append(loc)
contract=json.loads((root/'verification/lean_contract_v1.0.0.json').read_text());targets=contract['targets'];ct={t['declaration']:t for t in targets}
for n,t in ct.items():
 if n not in index:
  matches=[v for k,vs in short.items() if n.endswith('.'+k) for v in vs]
  assert len(matches)==1,(n,matches)
  index[n]=matches[0]
 assert (index[n]['kind'] in ['theorem','lemma'])==(t['kind']=='theorem'),(n,index[n],t)
mapfile=lean/'LEAN_THEOREM_MAP_v1.0.0.md';rows=[]
for l in mapfile.read_text().splitlines():
 if re.match(r'^\|\s*\d+\s*\|',l):
  v=[x.strip() for x in l.split('|')[1:-1]]
  rows.append({'id':int(v[0]),'statement':v[1],'declarations':re.findall(r'`([^`]+)`',v[2]),'status_and_boundary':v[3]})
assert [r['id'] for r in rows]==list(range(1,152))
names=[n for r in rows for n in r['declarations']];assert len(names)==len(set(names))==1164 and set(names)==set(ct)
for r in rows:
 assert all(ct[n]['row_id']==r['id'] for n in r['declarations'])
 r['source_locations']=[dict(name=n,**index[n]) for n in r['declarations']]
 r['record_labels']=sorted({l for n in r['declarations'] for l in ct[n]['record_labels']})
audit=lean/'KomorebiPaperIV/KernelAudit.lean';audit_names=re.findall(r'^#print axioms\s+(\S+)',audit.read_text(),re.M)
assert len(audit_names)==1164 and set(audit_names)==set(names)
transcript=lean/'kernel_audit_output.txt';text=transcript.read_text();records=re.findall(r"^'(Komorebi[^']+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",text,re.M)
assert len(records)==1164 and {r[0] for r in records}==set(names)
axioms={n:[] if k.startswith('does') else [x.strip() for x in ax.split(',')] for n,k,ax in records};assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values())
assert text.rstrip().endswith('FAIL-CLOSED PAPER IV v1.0.0 KERNEL AUDIT PASS: 2234 declarations (1999 theoremInfo); 1164 explicit mapped targets; allowed axioms only: propext, Classical.choice, Quot.sound')
bad=[]
for n,p in sources.items():
 if n.endswith('KernelAudit.lean'):continue # audit necessarily names the prohibited axiom in its exclusion logic
 for m in re.finditer(r'\b(?:sorry|admit|sorryAx|axiom|unsafe|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool',active_text(p.read_text())):bad.append({'file':n,'line':p.read_text()[:m.start()].count('\n')+1,'token':m.group()})
assert not bad,bad
status={'status':'PASS','evidence':'Current static source, contract, map and inherited transcript reconciliation. No Lean execution.','fresh_lean_execution':False,'source_files':len(sources),'source_lines':sum(len(p.read_text().splitlines()) for p in sources.values()),'map_rows':151,'mapped_targets':1164,'theorem_targets':sum(t['kind']=='theorem' for t in targets),'construction_targets':sum(t['kind']!='theorem' for t in targets),'audit_directives':len(audit_names),'inherited_transcript_records':len(records),'inherited_namespace_count':2234,'inherited_namespace_theoremInfo_count':1999,'inherited_execution_date':'2026-09-05','manifest_checks':checks,'source_policy_hits':bad,'policy_scan_exclusion':'KernelAudit.lean implements and names the forbidden-axiom test; reviewed separately.','map_sha256':sha(mapfile),'contract_sha256':sha(root/'verification/lean_contract_v1.0.0.json'),'transcript_sha256':sha(transcript),'limits':['No elaboration or kernel traversal in this guide build','Lexical locations are navigation, not type checking','Historical namespace totals are inherited execution evidence']}
assert status['source_files']==119 and status['theorem_targets']==953 and status['construction_targets']==211
js('static_audit.json',status);js('theorem_map.json',rows);js('mapped_source_index.json',{n:index[n] for n in names});js('inherited_axiom_records.json',axioms)
mods={'.'.join(Path(n).with_suffix('').parts):p for n,p in sources.items()};imports={n:re.findall(r'^import\s+(\S+)',p.read_text(),re.M) for n,p in mods.items()};js('imports.json',imports)
out=[]
for n,ds in imports.items():
 out += [r'\Needspace{4\baselineskip}',r'\textbf{\code{'+n+r'}}\par',r'{\small Local: '+(', '.join(r'\code{'+d.removeprefix('KomorebiPaperIV.')+'}' for d in ds if d in mods) or 'none')+r'.\par}',r'{\footnotesize External: '+(', '.join(r'\code{'+d+'}' for d in ds if d not in mods) or 'none')+r'.\par}\medskip']
(gen/'imports.tex').write_text('\n'.join(out)+'\n')
pins=json.loads((lean/'lake-manifest.json').read_text())['packages'];js('dependency_pins.json',pins)
out=[r'\begin{longtable}{p{.20\textwidth}p{.70\textwidth}}',r'\toprule Package & Exact revision \\ \midrule\endhead']
for p in pins:out += [esc(p['name'])+r' & \code{'+p['rev']+r'} \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'pins.tex').write_text('\n'.join(out)+'\n')
# Excerpts are entire literal declarations, including proofs. Enclosing context is retained separately.
select=json.loads((HERE/'excerpt_selection.json').read_text());metadata=[]
for tag,s in select.items():
 n='Komorebi.PaperIV.'+s['name'];loc=index[n];src=lean/loc['file'];lines=src.read_text().splitlines();start=loc['line']-1;end=start+1
 while end<len(lines) and not re.match(r'^(?:@\[|omit\b|/--|/-!|end\b|namespace\b|(?:noncomputable )?section\b|variable\b|universe\b|(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected) )*(?:def|theorem|lemma|structure|abbrev|class|inductive|instance)\b)',lines[end]):end+=1
 while end>start and not lines[end-1].strip():end-=1
 content='\n'.join(lines[start:end])+'\n';raw=ex/f'{tag}.lean.txt';raw.write_text(content)
 replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'}
 for c in ['𝕜','⧸','𝓕','⦃','⦄','〖','〗','𝓝','𝓤','𝟙','𝕊','𝔼','𝓛','𝕂']:replacements[c]=r'\CodeSymbol{'+format(ord(c),'X')+'}'
 display=ex/f'{tag}.render.txt';display.write_text(''.join(replacements.get(c,c) for c in content))
 metadata.append({'tag':tag,'declaration':n,'source':str(src.relative_to(root)),'first_line':start+1,'last_line':end,'source_sha256':sha(src),'excerpt_sha256':sha(raw),'display_sha256':sha(display)})
js('excerpts.json',metadata)
# Full exact row catalog. Earlier exclusions are retained as historical row-local scope.
out=[]
for r in rows:
 out += [r'\Needspace{7\baselineskip}',r'\subsection{Row '+str(r['id'])+': '+esc(r['statement'])+'}',r'\label{row:'+str(r['id'])+'}',r'\textbf{Exact row scope.} '+prose(r['status_and_boundary'])+r'\par\smallskip',r'\textbf{Manuscript labels.} '+', '.join(r'\code{'+l+'}' for l in r['record_labels'])+r'\par\smallskip']
 for n,loc in zip(r['declarations'],r['source_locations']):
  out += [r'{\small\code{'+n+r'}\par}',r'{\footnotesize\color{muted}'+esc(ct[n]['kind'])+r'; \code{'+loc['file']+'}, line '+str(loc['line'])+r'.\par}\smallskip']
(gen/'theorem_map.tex').write_text('\n'.join(out)+'\n')
# Result ledger is not inferred from individual row wording.
ledger=[]
for l in (root/'provenance/COMPLETION_STATUS.md').read_text().splitlines():
 if re.match(r'^\|\s*\d+\.\d+\s*\|',l) and len(l.split('|'))==6:
  v=[x.strip() for x in l.split('|')[1:-1]];ledger.append({'record':v[0],'title':v[1],'status':v[2],'rows':[int(x.strip()) for x in v[3].split(',')]})
assert len(ledger)==68;js('completion_ledger.json',ledger)
out=[r'\begin{longtable}{p{.08\textwidth}p{.47\textwidth}p{.35\textwidth}}',r'\toprule Record & Full scoped result & Additive map rows \\ \midrule\endhead']
for r in ledger:out += [r['record']+' & '+esc(r['title']).replace(r'\$','$')+' & '+', '.join(str(x) for x in r['rows'])+r' \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'completion.tex').write_text('\n'.join(out)+'\n')
navfile=a.traditional/'canonical_label_to_final.json'
if navfile.exists():
 nav=json.loads(navfile.read_text());js('traditional_crosswalk.json',nav)
 out=[r'\begin{longtable}{p{.57\textwidth}p{.33\textwidth}}',r'\toprule Source label & Final traditional locator \\ \midrule\endhead']
 for l,v in nav.items():
  if l in {q for r in rows for q in r['record_labels']}:out.append(r'\code{'+l+'} & '+v.get('kind','Result').capitalize()+' '+str(v.get('number',''))+', p.~'+str(v.get('page',''))+r' \\ \addlinespace')
 out += [r'\bottomrule\end{longtable}'];(gen/'traditional_crosswalk.tex').write_text('\n'.join(out)+'\n');js('traditional_crosswalk_provenance.json',{'crosswalk_sha256':sha(navfile),'traditional_source_sha256':sha(a.traditional/'Paper_IV_Traditional_Final.tex'),'scope':'Navigation only; no extension to formal contract'})
else:(gen/'traditional_crosswalk.tex').write_text('The manuscript labels in the result catalog identify the source results exactly.\n')
print(json.dumps({k:status[k] for k in ['status','fresh_lean_execution','source_files','source_lines','map_rows','mapped_targets','theorem_targets','construction_targets']}))
