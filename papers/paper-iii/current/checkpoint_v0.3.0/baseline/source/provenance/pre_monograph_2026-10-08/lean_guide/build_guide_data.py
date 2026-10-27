#!/usr/bin/env python3
"""Generate Paper III guide data and static provenance. Does not invoke Lean."""
from pathlib import Path
import argparse, hashlib, json, re
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--source',type=Path,default=HERE.parent.parent/'source/finite')
ap.add_argument('--traditional',type=Path,default=HERE.parent/'traditional',help='final traditional directory containing canonical_label_to_final.json')
a=ap.parse_args(); root=a.source.resolve(); lean=root/'formalization/lean'
gen=HERE/'generated'; ex=HERE/'excerpts';gen.mkdir(exist_ok=True);ex.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,o): (gen/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def active_text(text):
    out=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;out.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif string:
            if text[i]=='\\':out.extend('  ');i+=2
            elif text[i]=='"':string=False;out.append(' ');i+=1
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;out.extend('  ');i+=2
        elif text.startswith('--',i):
            e=text.find('\n',i);e=len(text) if e<0 else e;out.extend(' '*(e-i));i=e
        elif text[i]=='"':string=True;out.append(' ');i+=1
        else:out.append(text[i]);i+=1
    return ''.join(out)
def esc(s):
    d={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}'}
    return ''.join(d.get(c,c) for c in s)
def prose(s):return ''.join(r'\code{'+p[1:-1]+'}' if p.startswith('`') else esc(p) for p in re.split(r'(`[^`]*`)',s))
manifest={}
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
    m=re.match(r'^([0-9a-f]{64})\s+\.?/?(.+)$',line)
    if m:manifest[m[2]]=m[1]
files={str(p.relative_to(lean)):p for p in sorted(lean.rglob('*')) if p.is_file() and '.lake' not in p.parts and '__pycache__' not in p.parts}
checks=[{'path':'formalization/lean/'+n,'sha256':sha(p),'manifest_sha256':manifest.get('formalization/lean/'+n),'matches':sha(p)==manifest.get('formalization/lean/'+n)} for n,p in files.items()]
assert all(c['matches'] for c in checks),checks
sources={n:p for n,p in files.items() if n.endswith('.lean')}
index={}
for n,p in sources.items():
    stack=[]
    for ln,line in enumerate(active_text(p.read_text()).splitlines(),1):
        m=re.match(r'^\s*(namespace|section)\b\s*([^\s]*)',line)
        if m:stack.append((m[1],m[2]));continue
        if re.match(r'^\s*end\b',line):
            if stack:stack.pop()
            continue
        m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected)\s+)*(def|theorem|lemma|structure|abbrev|class|inductive)\s+([^\s({:]+)',line)
        if m:
            full='.'.join([v for k,v in stack if k=='namespace' and v]+[m[2]])
            index[full]={'file':n,'line':ln,'kind':m[1]}
mapfile=lean/'LEAN_THEOREM_MAP_v1.0.1.md';rows=[]
for line in mapfile.read_text().splitlines():
    if re.match(r'^\|\s*\d+\s*\|',line):
        v=[x.strip() for x in line.split('|')[1:-1]]
        rows.append({'id':int(v[0]),'statement':v[1],'declarations':re.findall(r'`([^`]+)`',v[2]),'status_and_boundary':v[3]})
assert [r['id'] for r in rows]==list(range(1,42))
names=[n for r in rows for n in r['declarations']];assert len(names)==len(set(names))==143
assert all(n in index for n in names),[n for n in names if n not in index]
assert sum(index[n]['kind']=='theorem' for n in names)==88
for r in rows:r['source_locations']=[dict(name=n,**index[n]) for n in r['declarations']]
js('theorem_map.json',rows);js('mapped_source_index.json',{n:index[n] for n in sorted(names)})
audit=sources['KomorebiPaperIII/KernelAudit.lean'].read_text()
audit_names=re.findall(r'^#print axioms\s+(\S+)',audit,re.M)
assert len(audit_names)==143 and set(audit_names)==set(names)
transcript=root/'kernel_audit_output.txt'; t=transcript.read_text()
records=re.findall(r"^'(Komorebi[^']+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",t,re.M)
assert len(records)==143 and {r[0] for r in records}==set(names)
axioms={n:[] if kind.startswith('does') else [x.strip() for x in ax.split(',')] for n,kind,ax in records}
assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values())
assert t.rstrip().endswith('FAIL-CLOSED PAPER III v1.0.1 KERNEL AUDIT PASS: 468 declarations (229 theoremInfo); 143 explicit mapped targets; allowed axioms only: propext, Classical.choice, Quot.sound')
report=root/'provenance/VERIFICATION_REPORT.md'
report_checks=[]
for p in [mapfile,transcript]:
    report_checks.append({'file':str(p.relative_to(root)),'sha256':sha(p),'recorded_in_inherited_report':sha(p) in report.read_text()})
assert all(c['recorded_in_inherited_report'] for c in report_checks)
bad=[]
for n,p in sources.items():
    for m in re.finditer(r'\b(?:sorry|admit|sorryAx|axiom|unsafe|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool',active_text(p.read_text())):
        bad.append({'file':n,'line':p.read_text()[:m.start()].count('\n')+1,'token':m.group()})
assert not bad,bad
status={'status':'PASS','evidence':'current lexical and checksum reconciliation against inherited release evidence','fresh_lean_execution':False,'source_files':len(sources),'source_lines':sum(len(p.read_text().splitlines()) for p in sources.values()),'formal_component_files':len(checks),'map_rows':41,'mapped_targets':143,'lexical_theorem_targets':88,'lexical_construction_targets':55,'audit_directives':143,'inherited_transcript_records':143,'inherited_namespace_count':468,'inherited_namespace_theoremInfo_count':229,'inherited_report_date':'2026-09-03','source_policy_hits':bad,'manifest_checks':checks,'report_hash_checks':report_checks,'transcript_sha256':sha(transcript),'limits':['No Lean compiler invoked','No fresh elaboration or kernel traversal','Generated namespace entries counted only in inherited transcript','Lexical locations do not independently certify elaborated types']}
js('static_audit.json',status);js('inherited_axiom_records.json',axioms)
# Printed contract retains full names, not ambiguous abbreviations.
out=[]
for r in rows:
    out += [r'\Needspace{7\baselineskip}',r'\subsection{Row '+str(r['id'])+': '+esc(r['statement'])+'}',r'\label{row:'+str(r['id'])+'}',r'\textbf{Status and boundary.} '+prose(r['status_and_boundary'])+r'\par\smallskip']
    for n,loc in zip(r['declarations'],r['source_locations']):
        out += [r'{\small\code{'+n+r'}\par}',r'{\footnotesize\color{muted}'+esc(loc['kind'])+r'; \code{'+loc['file']+'}, line '+str(loc['line'])+r'.\par}\smallskip']
(gen/'theorem_map.tex').write_text('\n'.join(out)+'\n')
mods={'.'.join(Path(n).with_suffix('').parts):p for n,p in sources.items()}
imports={n:re.findall(r'^import\s+(\S+)',p.read_text(),re.M) for n,p in mods.items()};js('imports.json',imports)
out=[r'\begin{longtable}{p{.35\textwidth}p{.55\textwidth}}',r'\toprule Module & Direct local imports \\ \midrule\endhead']
for n,ds in imports.items():out += [r'\code{'+n.removeprefix('KomorebiPaperIII.')+'} & '+(', '.join(r'\code{'+d.removeprefix('KomorebiPaperIII.')+'}' for d in ds if d in mods) or 'External imports only.')+r' \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'imports.tex').write_text('\n'.join(out)+'\n')
pins=json.loads((lean/'lake-manifest.json').read_text())['packages'];js('dependency_pins.json',pins)
out=[r'\begin{longtable}{p{.21\textwidth}p{.69\textwidth}}',r'\toprule Package & Exact revision \\ \midrule\endhead']
for p in pins:out += [esc(p['name'])+r' & \code{'+p['rev']+r'} \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'pins.tex').write_text('\n'.join(out)+'\n')
select={
'packet_matrix':('EdgeOperators','packetMatrix'),
'edge_product':('EdgeOperators','edgeOp_mul_edgeOp_of_composable'),
'word_operator':('EdgeOperators','wordOp'),
'word_append':('EdgeOperators','wordOp_append'),
'broken_word':('EdgeOperators','wordOp_eq_zero_of_not_composable'),
'explicit_successor':('EdgeOperators','explicitWordExpansion_succ'),
'walk_pruning':('EdgeOperators','explicitWordExpansion_eq_walkExpansion'),
'word_entry':('EdgeExtensions','wordOp_apply_eq_if_connects'),
'reachability':('EdgeExtensions','transferOp_pow_mulVec_apply_eq_zero_of_unreachable_support'),
'heterogeneous_two':('EdgeExtensions','heterogeneousPacketPathExpansion_two'),
'heterogeneous_three':('EdgeExtensions','heterogeneousPacketPathExpansion_three'),
'heterogeneous':('EdgeExtensions','heterogeneousPacketPathExpansion'),
'supported':('EdgeExtensions','heterogeneousPathSum_eq_zero_of_no_supportedPath'),
'exact_transport':('Transport','exactTransport'),
'exact_cocycle':('Transport','exactTransport_cocycle'),
'coordinate_transport':('CoordinateNaturality','exactCoordinateTransport'),
'coordinate_composition':('CoordinateNaturality','exactCoordinateMap_comp'),
'naturality':('CoordinateNaturality','exactCoordinateMap_naturality'),
'minimal_connection':('Transport','Connection'),
'minimal_defect':('Transport','cocycleDefect'),
'twisted_connection':('Transport','twistedThreePointConnection'),
'nontrivial_loop':('Transport','twisted_triangleHolonomy_ne_refl'),
'reversible':('ReversibleConnections','ReversibleConnection'),
'additive_defect':('ReversibleConnections','cocycleDefect'),
'defect_holonomy':('ReversibleConnections','triangleHolonomy_sub_id'),
'flat_criterion':('ReversibleConnections','flat_iff_triangleHolonomy_eq_refl'),
'flat_gauge':('ReversibleConnections','flatGauge'),
'flat_reconstruction':('ReversibleConnections','flat_isGaugeOfCanonical'),
'indexed_path':('ReversibleConnections','indexedPathTransport_eq_direct_of_flat'),
'gauge':('ReversibleConnections','gauge'),
'gauge_defect':('ReversibleConnections','gauge_cocycleDefect'),
'gauge_holonomy':('ReversibleConnections','gauge_triangleHolonomy'),
'packet_resolution':('ReversibleConnections','PacketResolution'),
'block_reconstruction':('ReversibleConnections','sum_blocks'),
'block_detection':('ReversibleConnections','blocks_zero_iff'),
'packet_witness':('ReversibleConnections','exists_packetWitness_of_block_ne_zero'),
'packet_preserving':('HolonomyBlocks','PacketPreserving'),
'block_gauge':('HolonomyBlocks','block_gauge_of_commutes'),
'operation_tree':('NonlinearObstructions','OperationTree'),
'inputs':('NonlinearObstructions','inputs'),
'locality':('NonlinearObstructions','eval_congr_on_inputs'),
'obstruction_packet':('NonlinearObstructions','ObstructionPacket'),
'candidate_failure':('NonlinearObstructions','not_isSolution_iff_nonempty_obstructionPacket')}
metadata=[]
for tag,(mod,name) in select.items():
    src=lean/'KomorebiPaperIII'/f'{mod}.lean';lines=src.read_text().splitlines()
    starts=[i for i,l in enumerate(lines) if re.match(r'^(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?(?:def|theorem|abbrev|structure|inductive)\s+'+re.escape(name)+r'(?=\s|[({:]|$)',l)]
    assert len(starts)==1,(tag,starts)
    start=starts[0];end=start+1
    while end<len(lines) and not re.match(r'^(?:/--|/-!|end\b|namespace\b|section\b|variable\b|universe\b)',lines[end]):end+=1
    while end>start and not lines[end-1].strip():end-=1
    content='\n'.join(lines[start:end])+'\n';raw=ex/f'{tag}.lean.txt';raw.write_text(content)
    replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'}
    for c in ['𝕜','⧸','𝓕','⦃','⦄','〖','〗']:replacements[c]=r'\CodeSymbol{'+format(ord(c),'X')+'}'
    display=ex/f'{tag}.render.txt';display.write_text(''.join(replacements.get(c,c) for c in content))
    metadata.append({'tag':tag,'source':str(src.relative_to(root)),'first_line':start+1,'last_line':end,'source_sha256':sha(src),'excerpt_sha256':sha(raw),'display_sha256':sha(display)})
# Namespace gate printed separately, exact source lines.
src=lean/'KomorebiPaperIII/KernelAudit.lean';lines=src.read_text().splitlines();start=next(i for i,l in enumerate(lines) if l=='run_cmd do')
raw=ex/'kernel_gate.lean.txt';raw.write_text('\n'.join(lines[start:])+'\n')
replacements={'\\':r'\textbackslash{}','{':r'\{','}':r'\}'};display=ex/'kernel_gate.render.txt';display.write_text(''.join(replacements.get(c,c) for c in raw.read_text()))
metadata.append({'tag':'kernel_gate','source':str(src.relative_to(root)),'first_line':start+1,'last_line':len(lines),'source_sha256':sha(src),'excerpt_sha256':sha(raw),'display_sha256':sha(display)})
js('excerpts.json',metadata)
print(json.dumps({k:status[k] for k in ['status','fresh_lean_execution','source_files','source_lines','formal_component_files','map_rows','mapped_targets','inherited_transcript_records']}))

# Companion navigation and inherited names are editorial appendices.
inherited=(lean/'INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md').read_text();out=[]
for line in inherited.splitlines():
    if re.match(r'^\|\s*\d+\s*\|',line):
        number,name,role=[x.strip() for x in line.split('|')[1:-1]]
        out += [r'\Needspace{4\baselineskip}',r'\textbf{'+number+'. '+esc(role)+r'}\par',r'{\small\code{'+name.strip('`')+r'}\par}\medskip']
(gen/'inherited.tex').write_text('\n'.join(out)+'\n')
navfile=a.traditional/'canonical_label_to_final.json'
nav=json.loads(navfile.read_text());(HERE/'traditional_crosswalk.json').write_text(json.dumps(nav,indent=2)+'\n')
out=[r'\begin{longtable}{p{.54\textwidth}p{.36\textwidth}}',r'\toprule Canonical label & Final printed locator \\ \midrule\endhead']
for label,v in nav.items():
    if v['kind'] in ['section','definition','theorem','lemma','proposition','corollary']:
        out += [r'\code{'+label+'} & '+v['kind'].capitalize()+' '+v['number']+', p.~'+v['page']+r' \\ \addlinespace']
out += [r'\bottomrule\end{longtable}'];(gen/'traditional_crosswalk.tex').write_text('\n'.join(out)+'\n')
tex=a.traditional/'Paper_III_Traditional_Final.tex'
js('traditional_crosswalk_provenance.json',{'crosswalk_sha256':sha(navfile),'traditional_source_sha256':sha(tex),'scope':'Navigation only; no extension of finite formal contract'})
