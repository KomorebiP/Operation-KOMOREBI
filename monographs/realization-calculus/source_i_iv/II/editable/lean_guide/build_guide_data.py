#!/usr/bin/env python3
"""Generate Paper II guide data. Static checks only; never invokes Lean.

The default source is ../../source/canonical_v1.2.1 in the delivered package.
Use --source to read another preserved release. No source file is modified.
"""
from pathlib import Path
import argparse, hashlib, json, re

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--source',type=Path,default=HERE.parent.parent/'source/canonical_v1.2.1')
ap.add_argument('--baseline',type=Path,help='optional second release for byte identity')
a=ap.parse_args(); root=a.source.resolve(); lean=root/'formalization/lean'
gen=HERE/'generated'; gen.mkdir(exist_ok=True)
ex=HERE/'excerpts'; ex.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def writejson(name,obj): (gen/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def active_text(text):
    """Erase nested comments and strings while preserving source line numbers."""
    out=[]; i=0; depth=0; string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i): depth+=1; out.extend('  '); i+=2
            elif text.startswith('-/',i): depth-=1; out.extend('  '); i+=2
            else: out.append('\n' if text[i]=='\n' else ' '); i+=1
        elif string:
            if text[i]=='\\': out.extend('  '); i+=2
            elif text[i]=='"': string=False; out.append(' '); i+=1
            else: out.append('\n' if text[i]=='\n' else ' '); i+=1
        elif text.startswith('/-',i): depth=1; out.extend('  '); i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i); end=len(text) if end<0 else end
            out.extend(' '*(end-i)); i=end
        elif text[i]=='"': string=True; out.append(' '); i+=1
        else: out.append(text[i]); i+=1
    return ''.join(out)

manifest={}
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
    m=re.match(r'^([0-9a-f]{64})\s+\.?/?(.+)$',line)
    if m: manifest[m[2]]=m[1]
files={str(p.relative_to(lean)):p for p in sorted(lean.rglob('*')) if p.is_file() and '.lake' not in p.parts and '__pycache__' not in p.parts}
checks=[]
for n,p in files.items():
    key='formalization/lean/'+n
    checks.append({'path':key,'sha256':sha(p),'release_manifest_sha256':manifest.get(key),'manifest_match':sha(p)==manifest.get(key)})
assert all(c['manifest_match'] for c in checks),'release manifest mismatch'
sources={n:p for n,p in files.items() if n.endswith('.lean')}
baseline_checks=[]
if a.baseline:
    for n,p in files.items():
        q=a.baseline/'formalization/lean'/n
        baseline_checks.append({'path':n,'match':q.is_file() and sha(p)==sha(q)})
    assert all(c['match'] for c in baseline_checks),'baseline mismatch'
prefixes={}; rows=[]
mapfile=lean/'LEAN_THEOREM_MAP_v1.1.1.md'
for line in mapfile.read_text().splitlines():
    m=re.fullmatch(r'\| `([A-Z]+)` \| `([^`]+)` \|',line.strip())
    if m: prefixes[m[1]]=m[2]
    if re.match(r'^\|\s*\d+\s*\|',line):
        vals=[x.strip() for x in line.split('|')[1:-1]]
        r=dict(zip(['id','statement','classification','declarations_text','scope','boundary'],vals));r['id']=int(r['id'])
        r['short_declarations']=re.findall(r'`([^`]+)`',r.pop('declarations_text'))
        r['declarations']=[prefixes[n.split('.')[0]]+'.'+n.split('.',1)[1] for n in r['short_declarations']]
        rows.append(r)
assert [r['id'] for r in rows]==list(range(1,26))
names=sorted({n for r in rows for n in r['declarations']})
assert len(names)==160
# A lexical declaration index is useful navigation, not an elaborated-type check.
index={}
for n,p in sources.items():
    stack=[]
    for line_no,line in enumerate(active_text(p.read_text()).splitlines(),1):
        m=re.match(r'^\s*(namespace|section)\b\s*([^\s]*)',line)
        if m: stack.append((m[1],m[2])); continue
        if re.match(r'^\s*end\b',line):
            if stack: stack.pop()
            continue
        m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected)\s+)*(def|theorem|lemma|structure|abbrev|class)\s+([^\s({:]+)',line)
        if m:
            full='.'.join([v for k,v in stack if k=='namespace' and v]+[m[2]])
            index[full]={'file':n,'line':line_no,'kind':m[1]}
missing=[n for n in names if n not in index]
assert not missing,missing
for r in rows:r['source_locations']=[dict(name=n,**index[n]) for n in r['declarations']]
writejson('theorem_map.json',rows);writejson('namespace_prefixes.json',prefixes)
writejson('mapped_source_index.json',{n:index[n] for n in names})
bad=[]
for n,p in sources.items():
    for m in re.finditer(r'\b(?:sorry|admit|sorryAx|axiom|unsafe|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool',active_text(p.read_text())):
        bad.append({'file':n,'line':p.read_text()[:m.start()].count('\n')+1,'token':m.group()})
assert not bad,bad
audit=(lean/'KomorebiVerification/PaperII/KernelAudit.lean').read_text()
audit_sample=re.findall(r'^#print axioms\s+(\S+)',audit,re.M)
status={'schema':'komorebi.paper_ii.lean_guide.static_identity.v1','status':'PASS','lean_compiler_run':False,
 'evidence_level':'current static identity; inherited narrative verification report, not a raw compiler transcript',
 'historical_report_date':'2026-09-03','historical_report_claims':{'mapped_declarations':160,'audited_namespace_entries':1034,'contract_rows':25},
 'local_lean_files':len(sources),'local_lean_lines':sum(len(p.read_text().splitlines()) for p in sources.values()),
 'formal_component_files_checked':len(checks),'contract_rows':len(rows),'unique_mapped_names':len(names),
 'mapped_occurrences':sum(len(r['declarations']) for r in rows),'lexically_located_targets':len(names)-len(missing),
 'source_policy_hits':bad,'historical_audit_print_sample_count':len(audit_sample),
 'manifest_checks':checks,'optional_baseline_checks':baseline_checks,
 'not_performed':['fresh Lean compilation','compiled environment declaration resolution','fresh axiom traversal','formal verification of companion Python']}
writejson('static_identity_audit.json',status)
def esc(s):
    d={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}'}
    return ''.join(d.get(c,c) for c in s)
def prose(s):return ''.join(r'\code{'+p[1:-1]+'}' if p.startswith('`') else esc(p) for p in re.split(r'(`[^`]*`)',s))
out=[]
for r in rows:
    out += [r'\Needspace{7\baselineskip}',r'\subsection{Row '+str(r['id'])+': '+esc(r['statement'].replace('`',''))+'}',r'\label{row:'+str(r['id'])+'}',r'\textbf{Classification:} '+esc(r['classification'])+'.',r'\par\smallskip\textbf{Declaration targets}\par']
    for n,loc in zip(r['short_declarations'],r['source_locations']):
        out += [r'{\small\noindent\code{'+n+r'}\par}']
    out += [r'\smallskip\textbf{Checked scope.} '+prose(r['scope']),r'\par\smallskip\textbf{Boundary.} '+prose(r['boundary']),r'\medskip']
(gen/'theorem_map.tex').write_text('\n'.join(out)+'\n')
mods={'.'.join(Path(n).with_suffix('').parts):p for n,p in sources.items()}
imports={n:re.findall(r'^import\s+(\S+)',p.read_text(),re.M) for n,p in mods.items()}
writejson('imports.json',imports)
short=lambda n:n.removeprefix('KomorebiVerification.')
out=[r'\begin{longtable}{p{.31\textwidth}p{.59\textwidth}}',r'\toprule Module & Direct local imports \\ \midrule\endhead']
for n,ds in imports.items():out += [r'\code{'+short(n)+'} & '+(', '.join(r'\code{'+short(d)+'}' for d in ds if d in mods) or 'External imports only.')+r' \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'local_imports.tex').write_text('\n'.join(out)+'\n')
pins=json.loads((lean/'lake-manifest.json').read_text())['packages'];writejson('dependency_pins.json',pins)
out=[r'\begin{longtable}{p{.21\textwidth}p{.69\textwidth}}',r'\toprule Package & Exact revision \\ \midrule\endhead']
for p in pins:out += [esc(p['name'])+r' & \code{'+p['rev']+r'} \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'dependency_pins.tex').write_text('\n'.join(out)+'\n')
selections={
 'refinement':('PaperII/NestedRefinement',47,53),
 'packet_uniqueness':('PaperII/NestedRefinement',62,86),
 'coordinate_maps':('PaperII/NestedRefinement',289,298),
 'coordinate_inverses':('PaperII/NestedRefinement',335,355),
 'fourier_certificate':('PaperII/ResidueFourierCRT',114,120),
 'fourier_bridge':('PaperII/ResidueFourierCRT',137,149),
 'finite_inverse':('PaperII/WeightedTransfer',65,76),
 'filtration':('PaperII/WeightedTransfer',243,250),
 'precision':('PaperII/WeightedTransfer',273,288),
 'pruned_sum':('PaperII/WeightedTransfer',316,328),
 'diagonal_inverse':('PaperII/WeightedTransfer',544,565),
 'graph':('PaperII/TransferZeta',50,63),
 'enumerator':('PaperII/TransferZeta',113,128),
 'rationality':('PaperII/TransferZeta',759,765),
 'identify_series':('PaperII/TransferZeta',688,701),
 'recurrence':('PaperII/TransferZeta',732,740),
 'bezout_minimal':('PaperII/ResultantSeparation',93,108),
 'precision_delay':('PaperII/ResultantSeparation',477,490),
 'smith_fibre':('PaperII/SmithDyadic',44,60),
 'smith_count':('PaperII/SmithDyadic',113,133),
 'smith_global':('PaperII/SmithDyadic',307,316),
 'typed_defect':('PaperII/TypedLinearDefects',32,42),
 'zero_defect':('PaperII/TypedLinearDefects',102,108),
 'resolvent':('PaperII/TypedLinearDefects',476,492),
 'audit_gate':('PaperII/KernelAudit',149,164),
}
metadata=[]
for tag,(mod,first,last) in selections.items():
    src=lean/'KomorebiVerification'/f'{mod}.lean'
    text='\n'.join(src.read_text().splitlines()[first-1:last])+'\n'
    raw=ex/f'{tag}.lean.txt'; raw.write_text(text)
    replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'}
    for c in ['𝕜','⧸','𝓕','⦃','⦄','〖','〗']:replacements[c]=r'\CodeSymbol{'+format(ord(c),'X')+'}'
    display=ex/f'{tag}.render.txt';display.write_text(''.join(replacements.get(c,c) for c in text))
    metadata.append({'tag':tag,'source':'formalization/lean/KomorebiVerification/'+mod+'.lean','first_line':first,'last_line':last,'source_sha256':sha(src),'exact_excerpt':str(raw.relative_to(HERE)),'exact_excerpt_sha256':sha(raw),'display_file':str(display.relative_to(HERE)),'display_sha256':sha(display)})
writejson('excerpts.json',metadata)
print(json.dumps({k:status[k] for k in ['status','lean_compiler_run','local_lean_files','local_lean_lines','contract_rows','unique_mapped_names','mapped_occurrences','formal_component_files_checked']}))

# Companion navigation is editorial metadata, not additional formal coverage.
out=[r'\begin{longtable}{p{.12\textwidth}p{.79\textwidth}}',r'\toprule Prefix & Full namespace \\ \midrule\endhead']
for k,v in prefixes.items():out += [r'\code{'+k+r'} & \code{'+v+r'} \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'namespace_prefixes.tex').write_text('\n'.join(out)+'\n')
labels=['def:refinement-map','thm:nested-refinement','def:coordinate-refinement','prop:perfect-reconstruction','thm:transfer-block-refinement','prop:residue-algebra','thm:root-of-unity','thm:polyphase-refinement','thm:dyadic-odd','thm:weighted-inverse','cor:finite-precision','thm:transfer-zeta','cor:zeta-recurrence','thm:bezout-projector','def:separation-weight','thm:precision-delay','prop:dyadic-sign','thm:smith-solve','thm:power-defect','cor:defect-norm','thm:resolvent-defect','eq:smith-inversion','alg:residue','alg:weighted-inverse','alg:path-zeta']
nav=json.loads((HERE/'traditional_crosswalk.json').read_text())
out=[r'\begin{longtable}{p{.07\textwidth}p{.50\textwidth}p{.32\textwidth}}',r'\toprule Row & Canonical label & Final locator \\ \midrule\endhead']
for i,label in enumerate(labels,1):
    n=nav[label];locator=n.get('locator_text') or ('Statement '+str(n['number']))
    out += [str(i)+r' & \code{'+label+'} & '+esc(locator)+', p.~'+n['page']+r' \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'traditional_crosswalk.tex').write_text('\n'.join(out)+'\n')
