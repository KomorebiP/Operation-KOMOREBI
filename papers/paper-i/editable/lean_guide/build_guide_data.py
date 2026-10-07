#!/usr/bin/env python3
"""Regenerate guide data from the byte-preserved Paper I formal component.

This performs static identity checks only. It never invokes Lean or changes
the preserved component. Run from this directory, or pass --source.
"""
from pathlib import Path
import argparse, hashlib, json, re, importlib.util

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--source',type=Path,default=HERE.parent.parent/'source/traditional_v1.3.1')
a=ap.parse_args(); root=a.source.resolve(); lean=root/'formalization/lean'
gen=HERE/'generated'; gen.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((root/'verification/lean/fresh_verification.json').read_text())
sources={str(p.relative_to(lean)):p for p in sorted(lean.rglob('*.lean')) if '.lake' not in p.parts}
source_checks=[{'path':n,'sha256':sha(p),'recorded_sha256':report['source_hashes'].get(n),'match':sha(p)==report['source_hashes'].get(n)} for n,p in sources.items()]
log_checks=[{'path':c['log'],'sha256':sha(root/'verification/lean'/c['log']),'recorded_sha256':c['log_sha256'],'match':sha(root/'verification/lean'/c['log'])==c['log_sha256']} for c in report['checks']]
spec=importlib.util.spec_from_file_location('preserved_verifier',root/'scripts/verify_lean.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
forbidden=r'\b(sorry|admit|sorryAx|axiom|unsafe|opaque|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool'
hits=[{'path':n,'token':m.group()} for n,p in sources.items() for m in re.finditer(forbidden,verifier.active_text(p.read_text()))]
rows=[]
for line in (lean/'LEAN_THEOREM_MAP_v1.0.2.md').read_text().splitlines():
    if re.match(r'^\|\s*\d+\s*\|',line):
        v=[x.strip() for x in line.split('|')[1:-1]]
        rows.append(dict(zip(['id','statement','classification','declarations_text','scope','exclusions'],v)))
for r in rows:r['id']=int(r['id']);r['declarations']=re.findall(r'`([^`]+)`',r.pop('declarations_text'))
names=[n for r in rows for n in r['declarations']]
audit_names=re.findall(r'^#print axioms\s+(\S+)\s*$',(lean/'KomorebiVerification/KernelAudit.lean').read_text(),re.M)
types=(root/'verification/lean/mapped_declarations.log').read_text()
axiom_rows=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",types)
allowed={'propext','Classical.choice','Quot.sound'}
bad_axioms=[(n,ax) for n,ax in axiom_rows if set(x.strip() for x in ax.split(',') if x.strip())-allowed]
stat={'schema':'komorebi.paper_i.lean_guide.static_identity.v1','status':'PASS','executed_check':'static source/log identity and map reconciliation','lean_compiler_run':False,'historical_execution_start':report['started_utc'],'historical_execution_end':report['finished_utc'],'historical_status':report['status'],'local_source_count':len(sources),'mapped_rows':len(rows),'mapped_targets':len(names),'historical_namespace_entries':report['namespace_declarations_audited'],'source_checks':source_checks,'log_checks':log_checks,'source_policy_hits':hits,'map_exactly_matches_audit_inventory':sorted(names)==sorted(audit_names),'map_matches_historical_axiom_reports':set(names)==set(n for n,_ in axiom_rows),'unexpected_historical_axioms':bad_axioms,'counts_are_not_independent_theorem_counts':True}
assert all(c['match'] for c in source_checks+log_checks)
assert not hits and not bad_axioms and sorted(names)==sorted(audit_names)
assert set(names)==set(n for n,_ in axiom_rows)
assert len(names)==len(set(names))==84 and len(rows)==35 and len(sources)==20
(gen/'static_identity_audit.json').write_text(json.dumps(stat,indent=2)+'\n')
(gen/'theorem_map.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
def esc(s):
    s=s.replace('\\','\\textbackslash{}')
    for x,y in [('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),('_',r'\_')]:s=s.replace(x,y)
    return s
def prose(s):
    parts=re.split(r'(`[^`]*`)',s)
    out=''.join(r'\code{'+p[1:-1]+'}' if p.startswith('`') else esc(p) for p in parts)
    for char,repl in [('ℓ',r'\ensuremath{\ell}'),('𝕂',r'\ensuremath{\mathbb{K}}')]:
        out=out.replace(char,'}'+repl+r'\code{')
    return out
maptex=[]
for r in rows:
    maptex += [r'\subsection{Row '+str(r['id'])+': '+esc(r['statement'])+'}',r'\label{row:'+str(r['id'])+'}',r'\textbf{Contract classification:} '+r['classification']+'.',r'\par\smallskip\textbf{Declaration targets}\par']
    for n in r['declarations']:maptex += [r'{\small\noindent\code{'+n+r'}\par}']
    maptex += [r'\medskip\noindent\textbf{Exact scope.} '+prose(r['scope']),r'\par\smallskip\noindent\textbf{Boundary.} '+prose(r['exclusions']),r'\medskip']
(gen/'theorem_map.tex').write_text('\n'.join(maptex)+'\n')
mods={'.'.join(Path(n).with_suffix('').parts):p for n,p in sources.items()}
dependencies={n:[d for d in re.findall(r'^import\s+(\S+)',p.read_text(),re.M) if d in mods] for n,p in mods.items()}
(gen/'local_imports.json').write_text(json.dumps(dependencies,indent=2)+'\n')
short=lambda x:x.removeprefix('KomorebiVerification.')
tab=[r'\begin{longtable}{p{.31\textwidth}p{.60\textwidth}}',r'\toprule Module & Direct local imports \\ \midrule\endhead']
for n,ds in dependencies.items():tab += [r'\code{'+short(n)+'} & '+(', '.join(r'\code{'+short(d)+'}' for d in ds) or 'None; external imports only.')+r' \\ \addlinespace']
tab += [r'\bottomrule\end{longtable}'];(gen/'local_imports.tex').write_text('\n'.join(tab))
pins=json.loads((lean/'lake-manifest.json').read_text())['packages']
tab=[r'\begin{longtable}{p{.22\textwidth}p{.68\textwidth}}',r'\toprule Package & Exact revision \\ \midrule\endhead']
for p in pins:tab += [esc(p['name'])+r' & \code{'+p['rev']+r'} \\ \addlinespace']
tab += [r'\bottomrule\end{longtable}'];(gen/'dependency_pins.tex').write_text('\n'.join(tab))
selections={
 'projector_structure':('ProjectorCore',171,182),
 'packet_space':('ExactCoordinates',22,44),
 'inverse_laws':('ExactCoordinates',61,80),
 'coordinate_equiv':('ExactCoordinates',82,90),
 'seed_definitions':('SeedRankBasics',29,55),
 'one_seed':('SeedRankBasics',79,96),
 'quotient':('SeedRankBasics',223,240),
 'full_matrix':('FullMatrixCyclicity',20,36),
 'primary_certificate':('SingleOperatorGraph',459,486),
 'topological_obstruction':('TopologicalCompletion',182,199),
 'algorithm':('EllipticAlgorithms',482,514),
 'audit_gate':('KernelAudit',175,196),
 'fibre_family':('FibreRefinement',38,47),
 'refinement':('KernelAudit',66,71),
}
# Locate two robust structural excerpts by names rather than assuming stale lines.
ps=(lean/'KomorebiVerification/ProjectorCore.lean').read_text().splitlines()
start=next(i for i,l in enumerate(ps) if l.startswith('structure LinearProjectorFamily'))
selections['projector_structure']=('ProjectorCore',start+1,start+7)
metadata=[]
for tag,(module,a,b) in selections.items():
    src=lean/'KomorebiVerification'/f'{module}.lean';lines=src.read_text().splitlines()
    out=HERE/'excerpts'/f'{tag}.lean.txt';out.write_text('\n'.join(lines[a-1:b])+'\n')
    replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'}
    for char in ['𝕜','⧸']:
        replacements[char]=r'\CodeSymbol{'+format(ord(char),'X')+'}'
    rendered=''.join(replacements.get(char,char) for char in out.read_text())
    (HERE/'excerpts'/f'{tag}.render.txt').write_text(rendered)
    metadata.append({'excerpt':str(out.relative_to(HERE)),'source':'formalization/lean/KomorebiVerification/'+module+'.lean','first_line':a,'last_line':b,'source_sha256':sha(src),'excerpt_sha256':sha(out)})
(gen/'excerpts.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps({k:stat[k] for k in ['status','lean_compiler_run','local_source_count','mapped_rows','mapped_targets']}))
