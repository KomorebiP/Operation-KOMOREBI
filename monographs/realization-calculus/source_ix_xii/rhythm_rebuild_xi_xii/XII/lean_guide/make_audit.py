#!/usr/bin/env python3
"""Read-only source census and reproducible guide data; no Lean compilation."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, re, shutil
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release'
AUDIT=ROOT.parent/'audit/lean'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):
 p=ROOT/'data'/name;p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def stripped(s):
 out=[];i=0;depth=0;string=False
 while i<len(s):
  if depth:
   if s[i:i+2]=='/-':depth+=1;out+=[' ',' '];i+=2
   elif s[i:i+2]=='-/':depth-=1;out+=[' ',' '];i+=2
   else:out.append('\n' if s[i]=='\n' else ' ');i+=1
  elif string:
   if s[i]=='\\' and i+1<len(s):out+=[' ',' '];i+=2
   elif s[i]=='"':string=False;out.append(' ');i+=1
   else:out.append('\n' if s[i]=='\n' else ' ');i+=1
  elif s[i:i+2]=='/-':depth=1;out+=[' ',' '];i+=2
  elif s[i:i+2]=='--':
   j=s.find('\n',i);j=len(s) if j<0 else j;out.extend(' '*(j-i));i=j
  elif s[i]=='"':string=True;out.append(' ');i+=1
  else:out.append(s[i]);i+=1
 if depth:raise ValueError('unclosed comment')
 return ''.join(out)
def esc(s):
 for a,b in [('\\','\\textbackslash{}'),('_','\\_'),('&','\\&'),('%','\\%'),('#','\\#'),('{','\\{'),('}','\\}')]:s=s.replace(a,b)
 return s
def main():
 AUDIT.mkdir(parents=True,exist_ok=True);(ROOT/'data').mkdir(exist_ok=True)
 conf=json.loads((SOURCE/'checks/modules.json').read_text());mods=conf['modules']
 ver=json.loads((SOURCE/'verification.json').read_text());rev=json.loads((SOURCE/'REVISED_COVERAGE.json').read_text())
 inherited={d['name']:d for d in ver['axioms']}
 decls=[];catalog=[];edges=[];prohibited=[];private=[]
 pat=re.compile(r'^(?:@\[[^\]]*\]\s*)*((?:(?:private|protected|noncomputable)\s+)*)(theorem|lemma|def|abbrev|structure|instance)\s+([\w.\']+)',re.M)
 paths=sorted((SOURCE/'lean').rglob('*.lean'))
 assert set(p.relative_to(SOURCE/'lean').as_posix() for p in paths)==set(m.replace('.','/')+'.lean' for m in mods)
 for index,mod in enumerate(mods):
  rel=mod.replace('.','/')+'.lean';p=SOURCE/'lean'/rel;s=p.read_text();clean=stripped(s)
  ns=re.findall(r'^namespace\s+(\S+)',clean,re.M);assert len(ns)==1,(mod,ns)
  ds=[]
  for ma in pat.finditer(clean):
   modifiers,kind,name=ma.groups();row={'name':ns[0]+'.'+name,'kind':kind,'module':mod,'source':rel,'line':clean[:ma.start()].count('\n')+1,'private':'private' in modifiers,'reused_from_paper_x':ns[0].startswith('PaperX.')}
   if row['private']:private.append(row)
   else:
    assert row['name'] in inherited,row;row['inherited_axioms']=inherited[row['name']]['axioms'];ds.append(row);decls.append(row)
  imports=[]
  for line in clean.splitlines():
   if line.startswith('import '):imports.extend(line.split()[1:])
  for dep in imports:edges.append({'module':mod,'import':dep,'internal':dep in mods})
  bad=re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe)\b',clean)
  if bad:prohibited.append({'module':mod,'tokens':bad})
  catalog.append({'module':mod,'order':index+1,'source':rel,'sha256':sha(p),'lines':len(s.splitlines()),'bytes':p.stat().st_size,'imports':imports,'public_named_declarations':len(ds),'public_theorems':sum(d['kind'] in ('theorem','lemma') for d in ds),'reused_from_paper_x':ns[0].startswith('PaperX.')})
 names={d['name'] for d in decls};assert len(names)==len(decls);assert names==set(inherited)
 assert all(e['import'] in mods or not e['import'].startswith(('PaperX.','PaperXII.')) for e in edges)
 position={m:i for i,m in enumerate(mods)}
 topo=all(position[e['import']]<position[e['module']] for e in edges if e['internal']);assert topo
 targets={t for c in rev['claims'] for t in c['checked_targets']};assert targets<=names
 assert targets==set(json.loads((SOURCE/'checks/ClaimTargets.json').read_text()))
 own=sum(d['kind'] in ('theorem','lemma') and not d['reused_from_paper_x'] for d in decls)
 reused=sum(d['kind'] in ('theorem','lemma') and d['reused_from_paper_x'] for d in decls)
 before=ver['source_hashes_before'];assert before=={p.relative_to(SOURCE/'lean').as_posix():sha(p) for p in paths}
 assert before==ver['source_hashes_after'];assert not prohibited
 report={'date':'2026-10-06','kind':'independent lexical and inherited-record audit; no new Lean execution','production_modules':len(mods),'own_modules':sum(not c['reused_from_paper_x'] for c in catalog),'reused_modules':sum(c['reused_from_paper_x'] for c in catalog),'module_directory_counts':{'PaperXII':sum(m.startswith('PaperXII.') for m in mods),'PaperX':sum(m.startswith('PaperX.') for m in mods)},'public_named_declarations':len(decls),'private_helpers':private,'own_public_theorems':own,'reused_public_theorems':reused,'declaration_kind_census':dict(Counter(d['kind'] for d in decls)),'distinct_claim_targets':len(targets),'revised_claims':len(rev['claims']),'claim_status_census':dict(Counter(c['status'] for c in rev['claims'])),'amended_claims':[c['number'] for c in rev['claims'] if c['amendment']],'internal_import_edges':sum(e['internal'] for e in edges),'external_direct_imports':sorted({e['import'] for e in edges if not e['internal']}),'registered_import_order_valid':topo,'prohibited_production_tokens':prohibited,'all_inherited_source_hashes_match':True,'inherited_report_status':ver['status'],'inherited_report_sha256':sha(SOURCE/'verification.json'),'reverification_sha256':sha(SOURCE/'REVERIFICATION.json'),'manuscript_sha256':sha(SOURCE/'paper/Paper_XII_Revised_Formalization_Complete_v0.17.0.tex'),'lexical_method':'Nested block comments, line comments and strings blanked preserving lines; anchored named theorem/lemma/def/abbrev/structure/instance declarations in the unique namespace of each module. Private helpers excluded from public census. Not an elaborated environment census.'}
 assert (len(mods),len(decls),own,reused,len(targets),len(rev['claims']))==(96,1229,748,81,291,49)
 save('census.json',report);save('source_catalog.json',catalog);save('declarations.json',decls);save('import_audit.json',edges)
 for filename,rows in [('source_catalog.csv',catalog),('declarations.csv',decls),('import_audit.csv',edges)]:
  with (ROOT/'data'/filename).open('w',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in d.items()} for d in rows)
 original=json.loads((SOURCE/'coverage.json').read_text());cross=[]
 for c in rev['claims']:
  original_status='complete' if c['number'] in original['checked_claims'] else ('partial' if c['number'] in original['partial_claims'] else 'unchecked')
  c['original_status']=original_status
  c['target_source_locations']=[{k:next(d for d in decls if d['name']==t)[k] for k in ['name','kind','module','source','line']} for t in c['checked_targets']]
  cross.append({'number':c['number'],'label':c['label'],'status':c['status'],'original_status':original_status,'amendment':c['amendment'],'targets':len(c['checked_targets']),'modules':'; '.join(sorted({next(d['module'] for d in decls if d['name']==t) for t in c['checked_targets']}))})
 save('claim_crosswalk.json',rev)
 with (ROOT/'data/claim_crosswalk.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(cross[0]));w.writeheader();w.writerows(cross)
 tex=['\\begin{longtable}{p{.37\\textwidth}r r p{.35\\textwidth}}','\\toprule Module & Lines & Thm. & Source SHA-256 (prefix)\\\\','\\midrule\\endhead']
 for c in catalog:tex.append('\\code{'+c['module']+'}'+f" & {c['lines']} & {c['public_theorems']} & \\texttt{{{c['sha256'][:24]}}}\\\\")
 tex+=['\\bottomrule\\end{longtable}'];(ROOT/'data/catalog.tex').write_text('\n'.join(tex)+'\n')
 tex=['\\begin{longtable}{l p{.34\\textwidth} l l r}','\\toprule Claim & Manuscript label & Revised & Original & Targets\\\\','\\midrule\\endhead']
 for c in cross:tex.append(esc(c['number'])+' & \\code{'+c['label']+'} & '+('amended' if c['amendment'] else 'complete')+' & '+c['original_status']+' & '+str(c['targets'])+'\\\\')
 tex+=['\\bottomrule\\end{longtable}'];(ROOT/'data/crosswalk.tex').write_text('\n'.join(tex)+'\n')
 destination=ROOT/'formal_release';destination.mkdir(exist_ok=True)
 shutil.copytree(SOURCE/'lean',destination/'lean',dirs_exist_ok=True)
 for dirname in ['checks','logs']:shutil.copytree(SOURCE/dirname,destination/dirname,dirs_exist_ok=True)
 for f in ['Run-Reverified.sh','Run-Portable.sh','verification.json','REVERIFICATION.json','final_claims_check.json','REVISED_COVERAGE.json','coverage.json','claim_roadmap.json','CLAIM_DELTA.json','UPSTREAM_PRESERVATION.json','START_HERE.md','LATEST_STATUS.md','CURRENT_REPLAY_REVIEW.md','MATHEMATICAL_REVIEW.md','FINAL_TWO_THEOREMS.md','CURRENT_FAILURES.md','README.md','CONTINUE_HERE.md','LICENSE','MATHLIB_LICENSE']:
  shutil.copy2(SOURCE/f,destination/f)
 (destination/'upstream').mkdir(exist_ok=True)
 for f in ['v0.15_VERIFICATION.json','v0.16_FRESH_REPLAY.json']:shutil.copy2(SOURCE/'upstream'/f,destination/'upstream'/f)
 # Compiled consumer object is unnecessary for a source package and never counted as fresh evidence.
 for p in (destination/'checks').glob('*.olean'):p.unlink()
 hashes=''.join(f"{c['sha256']}  formal_release/lean/{c['source']}\n" for c in sorted(catalog,key=lambda c:c['source']))
 (ROOT/'data/SOURCE_SHA256SUMS.txt').write_text(hashes)
 (AUDIT/'SOURCE_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:report[k] for k in ['production_modules','public_named_declarations','own_public_theorems','reused_public_theorems','distinct_claim_targets','internal_import_edges']}))
if __name__=='__main__':main()
