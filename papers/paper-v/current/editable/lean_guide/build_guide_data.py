#!/usr/bin/env python3
"""Reconcile a guide with the immutable Paper V release. Does not execute Lean."""
from pathlib import Path
import argparse,hashlib,json,re,collections,datetime
from data_helpers import active_text,esc
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--traditional',type=Path);a=p.parse_args()
r=a.source.resolve();lean=r/'formalization/lean';gen=H/'generated';ex=H/'excerpts'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,o):(gen/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
contract=json.loads((r/'verification/candidate_contract.json').read_text());targets=contract['theorem_targets'];scope=json.loads((r/'verification/scope_contract.json').read_text());ledger=json.loads((r/'THEOREM_LEDGER.json').read_text())
assert len(targets)==len({t['declaration'] for t in targets})==225 and len(ledger)==len(scope['results'])==20
sources={str(p.relative_to(lean)):p for p in lean.rglob('*.lean')};assert len(sources)==25
checks=[]
for path,digest in contract['source_sha256'].items():checks.append({'file':path,'sha256':sha(r/path),'expected':digest,'matches':sha(r/path)==digest})
assert all(c['matches'] for c in checks)
index={}
for file,src in sources.items():
 for ln,line in enumerate(active_text(src.read_text()).splitlines(),1):
  m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected)\s+)*(def|theorem|lemma|abbrev|structure|inductive)\s+([^\s({:]+)',line)
  if m:index[(Path(file).stem,m[2])]={'file':file,'line':ln,'kind':m[1]}
for t in targets:
 loc=index[(Path(t['file']).stem,t['declaration'].split('.')[-1])];assert loc['line']==t['line'] and loc['kind']=='theorem',t
allnames={t['declaration'] for t in targets}
for row,led in zip(scope['results'],ledger):
 assert row['number']==led['number'];assert set(row['targets'])<=allnames
 row['label']='result:'+str(scope['results'].index(row)+1).zfill(2)
 row['source_page']=led['page'];row['kind']=led['kind']
audit=(lean/'KernelAudit.lean').read_text();directives=re.findall(r'^#print axioms (\S+)',audit,re.M)
assert set(directives)==allnames and len(directives)==225
trans=(r/'verification/lean_axiom_audit.log').read_text();records=re.findall(r"^'(Komorebi[^']+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",trans,re.M)
assert len(records)==225 and {x[0] for x in records}==allnames
axioms={n:[] if k.startswith('does') else [v.strip() for v in ax.split(',')] for n,k,ax in records};assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values())
assert 'PAPER_V_CANDIDATE_TARGET_AUDIT_PASS: 225 theorem targets; 827 namespace declarations' in trans
policy=[]
for name,p in sources.items():
 if name=='KernelAudit.lean':continue
 clean=active_text(p.read_text())
 for m in re.finditer(r'\b(?:sorry|admit|sorryAx|axiom|unsafe|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool',clean):policy.append({'file':name,'line':clean[:m.start()].count('\n')+1,'token':m.group()})
assert not policy
imports={name:re.findall(r'^import\s+(\S+)',p.read_text(),re.M) for name,p in sorted(sources.items())}
js('targets.json',targets);js('result_ledger.json',scope['results']);js('imports.json',imports);js('inherited_axiom_records.json',axioms)
status={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','scope':'Current static reconciliation only; inherited kernel evidence was not rerun.','fresh_lean_execution':False,'proof_modules':23,'lean_files':25,'lean_source_lines':sum(len(p.read_text().splitlines()) for p in sources.values()),'targets':225,'manuscript_results':20,'inherited_namespace_declarations':827,'inherited_execution_utc':'2026-09-06T03:17:59.699176+00:00','source_policy_hits':policy,'source_hash_checks':checks,'candidate_contract_sha256':sha(r/'verification/candidate_contract.json'),'scope_contract_sha256':sha(r/'verification/scope_contract.json'),'theorem_ledger_sha256':sha(r/'THEOREM_LEDGER.json'),'toolchain_sha256':sha(lean/'lean-toolchain'),'lake_manifest_sha256':sha(lean/'lake-manifest.json'),'dependency_packages':len(json.loads((lean/'lake-manifest.json').read_text())['packages']),'formal_project_bytes':{str(p.relative_to(lean)):sha(p) for p in sorted(lean.rglob('*')) if p.is_file()},'transcript_sha256':sha(r/'verification/lean_axiom_audit.log'),'audit_directives':len(directives),'inherited_transcript_records':len(records),'limits':['Source locations and hashes do not perform elaboration or kernel checking.','The 827 count includes definitions and generated declarations.','English-to-Lean correspondence is reviewed manually.','The two edge-recovery conjectures have no completed formalization claim.']}
js('static_reconciliation.json',status)
# Literal declarations are preserved in raw files. Renderer escapes TeX metacharacters only.
selection=json.loads((H/'excerpt_selection.json').read_text());metadata=[]
for tag,s in selection.items():
 loc=index[(s['module'],s['name'])];src=lean/loc['file'];lines=src.read_text().splitlines();start=loc['line']-1;end=start+1
 while end<len(lines) and not re.match(r'^(?:@\[|omit\b|/--|/-!|end\b|namespace\b|(?:noncomputable )?section\b|variable\b|universe\b|(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected) )*(?:def|theorem|lemma|structure|abbrev|class|inductive|instance)\b)',lines[end]):end+=1
 while end>start and not lines[end-1].strip():end-=1
 raw=ex/f'{tag}.lean.txt';raw.write_text('\n'.join(lines[start:end])+'\n')
 rep={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'}
 for c in ['𝕜','⧸','𝓕','⦃','⦄','〖','〗','𝓝','𝓤','𝟙','𝕊','𝔼','𝓛','𝕂','ℓ','⟦','⟧']:rep[c]=r'\CodeSymbol{'+format(ord(c),'X')+'}'
 display=ex/f'{tag}.render.txt';display.write_text(''.join(rep.get(c,c) for c in raw.read_text()))
 metadata.append({'tag':tag,'name':s['name'],'module':s['module'],'source':'formalization/lean/'+loc['file'],'first_line':start+1,'last_line':end,'source_sha256':sha(src),'excerpt_sha256':sha(raw),'display_sha256':sha(display),'standalone_compilable':False})
js('excerpts.json',metadata)
# Exact source import inventory and target index grouped by actual source file.
out=[]
for name,ds in imports.items():
 out += [r'\Needspace{5\baselineskip}',r'\subsection{\texorpdfstring{\code{'+name+'}}{'+esc(name)+'}}',r'{\small '+', '.join(r'\code{'+d+'}' for d in ds)+r'\par}']
(gen/'imports.tex').write_text('\n'.join(out)+'\n')
out=[]
for file in sorted({t['file'] for t in targets}):
 ts=[t for t in targets if t['file']==file];out += [r'\Needspace{7\baselineskip}',r'\subsection{'+esc(Path(file).stem)+': '+str(len(ts))+' targets}',r'\source{formalization/lean/'+file+'}']
 for t in ts:out += [r'{\small\code{'+t['declaration']+r'}\par}',r'{\footnotesize\color{muted}Source line '+str(t['line'])+r'; theorem.\par}\smallskip']
(gen/'target_catalog.tex').write_text('\n'.join(out)+'\n')
pins=json.loads((lean/'lake-manifest.json').read_text())['packages'];js('dependency_pins.json',pins)
out=[r'\begin{longtable}{>{\raggedright\arraybackslash}p{.20\textwidth}>{\raggedright\arraybackslash}p{.70\textwidth}}',r'\toprule Package & Exact revision \\ \midrule\endhead']
for x in pins:out += [esc(x['name'])+r' & \code{'+x['rev']+r'} \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'pins.tex').write_text('\n'.join(out)+'\n')
nav={}
if a.traditional and (a.traditional/'canonical_label_to_final.json').exists():nav=json.loads((a.traditional/'canonical_label_to_final.json').read_text())
if a.traditional and not nav:raise SystemExit('The final traditional map is required for supplied --traditional.')
if nav:
 assert all(row['label'] in nav for row in scope['results']), 'Missing core result locator'
 assert all('physical_pdf_page' in d and 'printed_page' in d for d in nav.values()), 'Traditional page convention is incomplete'
js('traditional_crosswalk.json',nav)
out=[]
for row in scope['results']:
 dest=nav.get(row['label'],{});page=dest.get('page',row['source_page']);row['final_page']=page
 out += [r'\Needspace{8\baselineskip}',r'\subsection{'+row['number']+' '+esc(row['title'])+'}',r'\label{result:'+row['number']+'}',r'\textbf{Traditional locator.} '+row['kind']+' '+row['number']+', '+('final' if dest else 'source')+' paper p.~'+str(page)+r'; \code{'+row['label']+r'}.',r'\textbf{Exact reviewed scope.} '+esc(row['scope'])]
 for t in row['targets']:
  loc=next(tg for tg in targets if tg['declaration']==t);out += [r'{\small\code{'+t+r'}\par}',r'{\footnotesize\color{muted}\code{'+loc['file']+'}, line '+str(loc['line'])+r'.\par}\smallskip']
(gen/'result_ledger.tex').write_text('\n'.join(out)+'\n');js('result_ledger.json',scope['results'])
js('navigation_provenance.json',{'traditional_map_sha256':sha(a.traditional/'canonical_label_to_final.json') if nav else None,'traditional_source_sha256':sha(a.traditional/'Paper_V_Traditional_Final.tex') if nav else None,'source_records_sha256':sha(a.traditional/'SOURCE_RECORDS.json') if nav else None,'traditional_map_entries':len(nav),'crosswalk_uses_final_pages':bool(nav),'locator_convention':'Printed Arabic page is the navigation locator; physical PDF index is separately preserved.','guide_only_covers_formal_core':True,'broader_prose_records_are_navigation_only':True})
print(json.dumps({k:v for k,v in status.items() if k not in ['source_hash_checks','limits']},indent=2));print('Excerpts:',len(metadata))
# Broader manuscript inventory: navigation only, no new formalization claim.
if nav:
 records=json.loads((a.traditional/'SOURCE_RECORDS.json').read_text())
 extension=[x for x in records if x['source']=='annals_extension' and x['kind'] in ['theorem','proposition','corollary','lemma']]
 assert len(extension)==63
 def nearest(ordinal):
  if ordinal<=3:return '1.1'
  if ordinal<=8:return '2.1–2.3'
  if ordinal<=14:return '3.1'
  if ordinal<=24:return '4.1'
  if ordinal==25:return '4.2'
  if ordinal==26:return '4.3'
  if ordinal<=31:return '5.1, 11.2'
  if ordinal<=34:return '11.3–11.5'
  if ordinal<=41:return '6.1–6.2'
  if ordinal<=47:return '7.1'
  if ordinal<=62:return '7.1, 11.5'
  if ordinal<=67:return '4.2; edge context'
  if ordinal<=74:return '6.1–7.1'
  if ordinal<=78:return '12.1'
  if ordinal<=82:return '13.2–13.3'
  return '14.1'
 out=[r'\subsection{All sixty-three Part II proof records}',r'Every row below has status: prose proof; no additional Lean claim. The final E-prefixed result number and page refer to the combined traditional paper. The nearest-core column identifies related reading only.',r'\begin{longtable}{>{\raggedright\arraybackslash}p{.14\textwidth}>{\raggedright\arraybackslash}p{.48\textwidth}>{\raggedright\arraybackslash}p{.23\textwidth}}',r'\toprule Final locator & Part II statement & Nearby core reading \\ \midrule\endhead']
 inv=[]
 for x in extension:
  assert len(x['label'])==1
  label=x['label'][0];dest=nav[label];row=dict(x,final_number=dest['number'],final_page=dest['page'],nearest_core=nearest(x['ordinal']),formal_status='No additional Lean claim; prose proof')
  inv.append(row)
  out += [esc(dest['number'])+', p.~'+str(dest['page'])+' & '+x['kind'].capitalize()+': '+x['title_tex']+' & '+esc(row['nearest_core'])+r' \\ \addlinespace']
 out += [r'\bottomrule\end{longtable}',r'\subsection{Open conjecture locators}']
 for x in records:
  if x['source']=='formal_core' and x['kind']=='conjecture':
   label=x['label'][0] if x['label'] else 'core:record:'+str(x['ordinal']).zfill(2);dest=nav[label]
   out += [r'\textbf{'+x['title_tex']+'}. Conjecture '+dest['number']+', final traditional p.~'+str(dest['page'])+r'; \code{'+label+r'}. Open; excluded from the twenty-result formal contract.\par']
 (gen/'extension_crosswalk.tex').write_text('\n'.join(out)+'\n');js('extension_crosswalk.json',inv)
