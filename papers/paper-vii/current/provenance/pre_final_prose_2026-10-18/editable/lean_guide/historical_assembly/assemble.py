#!/usr/bin/env python3
"""Derive guide evidence from immutable Paper VII source; never invokes Lean."""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, re, subprocess
from data_helpers import inventory,active_text,excerpt,esc
from fontTools.ttLib import TTFont

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
source_suffix=Path('source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot')
default_source=next((p/source_suffix for p in (HERE.parent,HERE.parent.parent) if (p/source_suffix).is_dir()),HERE.parent/source_suffix)
ap.add_argument('--source',type=Path,default=default_source)
args=ap.parse_args(); SRC=args.source.resolve(); GEN=HERE/'generated'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
modules=sorted((SRC/'formalization').glob('*.lean')); rows=[r for p in modules for r in inventory(p)]
saved=json.loads((SRC/'verification/theorem_inventory.json').read_text())
ledger=json.loads((SRC/'THEOREM_LEDGER.json').read_text())
report=json.loads((SRC/'verification/final_finite_release_run/SUMMARY.json').read_text())
names={r['declaration'] for r in rows}
all_declarations={r['declaration']:r for r in rows}
covariant_source=SRC/'formalization/GlobalProjectedConnection.lean'
covariant_line=next(i for i,l in enumerate(covariant_source.read_text().splitlines(),1) if l.startswith('def covariant '))
all_declarations['KomorebiPaperVII.GlobalConnection.covariant']={'declaration':'KomorebiPaperVII.GlobalConnection.covariant','module':'GlobalProjectedConnection','line':covariant_line,'kind':'definition'}
if len(modules)!=25 or len(rows)!=323 or len(names)!=323 or len(ledger)!=19:raise RuntimeError('Unexpected source counts')
if names!={n for ns in saved.values() for n in ns}:raise RuntimeError('Inventory names differ')
audits={k:v for m in report['modules'] for k,v in m['axiom_audits'].items()}
if set(audits)!=names:raise RuntimeError('Saved axiom report names differ')
for p in modules:
    sm=next(m for m in report['modules'] if m['module']==p.stem)
    if sha(p)!=sm['sha256']:raise RuntimeError('Source hash differs '+p.name)
    log=SRC/'verification/final_finite_release_run'/sm['log']
    if sha(log)!=sm['log_sha256']:raise RuntimeError('Saved compiler log hash differs '+p.name)
    parsed={}
    for m in re.finditer(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",log.read_text(),re.M):
        if m.group(1) in parsed:raise RuntimeError('Duplicate axiom record')
        parsed[m.group(1)]=[] if m.group(2) is None else [a.strip() for a in m.group(2).split(',') if a.strip()]
    if parsed!=sm['axiom_audits']:raise RuntimeError('Log/summary axiom mismatch '+p.name)
    if any(set(x)-{'propext','Classical.choice','Quot.sound'} for x in parsed.values()):raise RuntimeError('Unexpected axiom')

# Extra endpoint mappings are editorial navigation, explicitly distinguished
# from the source ledger's own main_declaration field.
extra={
'4.1':['KomorebiPaperVII.PacketFamily.circuit_path_expansion','KomorebiPaperVII.PacketFamily.circuit_reconstruction'],
'4.2':['KomorebiPaperVII.PacketFamily.unitarity_columns','KomorebiPaperVII.PacketFamily.unitarity_rows','KomorebiPaperVII.matrix_unitarity_columns','KomorebiPaperVII.matrix_unitarity_rows'],
'5.1':['KomorebiPaperVII.PacketFamily.symmetry_exponential_no_transfer','KomorebiPaperVII.PacketFamily.symmetry_exponential_diagonal'],
'7.1':['KomorebiPaperVII.measurement_invariance','KomorebiPaperVII.dephase_trace_preserving'],
'9.1':['KomorebiPaperVII.SchurFeshbach.projected_resolvent','KomorebiPaperVII.SchurFeshbach.schur_invertible'],
'11.1':['KomorebiPaperVII.LowModeConvergence.low_mode_error']}
endpoints={}
for r in ledger:
    ep=([r['main_declaration']] if r.get('main_declaration') else extra[r['item']])
    ep+=r.get('supporting_declarations',[])+r.get('additional_main_declarations',[])
    if any(n not in all_declarations for n in ep):raise RuntimeError('Unresolved ledger endpoint')
    endpoints[r['item']]=ep
reverse=collections.defaultdict(list)
for item,ns in endpoints.items():
    for n in ns:reverse[n].append(item)

selections={
'row_equiv':('SeedOrbit','orbitRowEquiv'),
'orbit_dimension':('SeedOrbit','span_orbit_dimension'),
'cyclic_rank':('SeedOrbit','cyclic_iff_full_rank'),
'seed_generate':('SeedOrbit','Generates'),
'stack_rank':('SeedOrbit','generates_iff_rank'),
'full_column':('SeedOrbit','exists_full_column_rank'),
'seed_minimum':('SeedOrbit','quantum_seed_rank'),
'schmidt_definition':('SeedOrbit','schmidtRank'),
'schmidt_minimum':('SeedOrbit','product_length_minimum'),
'local_action':('SeedOrbit','local_tensor_action'),
'reduced_support':('SeedOrbit','local_orbit_reduced_support'),
'seed_basis':('ComputationalSeed','circuit_seed_basis'),
'seed_translation':('ComputationalSeed','circuit_eq_translation'),
'cyclic_character':('CyclicProjectors','character_sum'),
'cyclic_mul':('CyclicProjectors','packet_mul'),
'cyclic_matrix':('CyclicProjectors','finite_cyclic_projectors'),
'tensor_mul':('TensorRefinement','tensor_mul'),
'tensor_refinement':('TensorRefinement','tensor_polyphase_refinement'),
'packet_structure':('QuantumPacketCore','PacketFamily'),
'compose_blocks':('QuantumPacketCore','compose_blocks'),
'circuit_path':('QuantumPacketCore','circuit_path_expansion'),
'unitarity_columns':('QuantumPacketCore','unitarity_columns'),
'symmetry_exp':('QuantumPacketCore','symmetry_exponential_no_transfer'),
'measurement':('QuantumPacketCore','measurement_invariance'),
'transport_derivative':('LeakageBound','transported_derivative'),
'transport_lipschitz':('LeakageBound','transported_lipschitz'),
'leakage_matrix':('LeakageBound','matrix_commutator_leakage_bound'),
'leakage_perturbation':('LeakageBound','perturbation_leakage_bound'),
'frame_product':('MovingFrames','matrix_vector_derivative'),
'moving_coordinates':('MovingFrames','moving_frame_coordinates'),
'connection_jet':('CanonicalConnection','differentiated_orthogonality'),
'canonical_connection':('CanonicalConnection','canonical_connection_of_hasDerivAt'),
'sandwich_zero':('ProjectedCurvature','jet_sandwich_zero'),
'local_curvature':('LocalProjectedCurvature','projected_connection_curvature'),
'range_transport':('GlobalRangeBundle','transport'),
'range_intertwines':('GlobalRangeBundle','transport_intertwines'),
'range_product':('GlobalRangeBundle','localProduct'),
'range_atlas':('GlobalRangeBundle','smooth_range_bundle_atlas'),
'global_nabla':('GlobalProjectedConnection','nabla'),
'global_leibniz':('GlobalProjectedConnection','nabla_leibniz'),
'global_glue':('GlobalProjectedConnection','local_connections_glue'),
'manifold_curvature':('ManifoldProjectedCurvature','projected_connection_curvature'),
'smooth_section':('ProjectedBundleCompletion','smooth_section_iff'),
'gauge_law':('ProjectedBundleCompletion','local_connections_gauge'),
'kraus_amplify':('KrausChannels','amplification_eq_kraus'),
'kraus_cp':('KrausChannels','channel_completely_positive'),
'syndrome_structure':('SyndromeRecovery','OrthogonalSyndromes'),
'syndrome_complete':('SyndromeRecovery','recoveryKraus_complete'),
'syndrome_cross':('SyndromeRecovery','decoder_cross_error'),
'kl_data':('KnillLaflammeSufficiency','Data'),
'kl_diagonal':('KnillLaflammeSufficiency','diagonal'),
'kl_null':('KnillLaflammeSufficiency','zero_weight_error'),
'kl_corrects':('KnillLaflammeSufficiency','recovery_corrects'),
'kl_rigidity':('KnillLaflammeNecessity','rank_one_gram_rigidity'),
'kl_necessity':('KnillLaflammeNecessity','gram_of_recovery'),
'density_bridge':('QuantumStateBridge','density_corrects_iff_operators'),
'kl_criterion':('QuantumStateBridge','state_correctable_iff_gram'),
'kl_reference':('QuantumStateBridge','recovery_with_reference'),
'kl_span':('ErrorSpanRecovery','recovery_span_channel'),
'kl_family':('ErrorSpanRecovery','error_family_correctable_iff_gram'),
'feshbach':('SchurFeshbach','projected_resolvent'),
'feshbach_counterexample':('SchurFeshbach','eliminated_invertible_full_singular'),
'euclidean_cfc':('EuclideanTransfer','transfer_cfc'),
'euclidean_endpoint':('EuclideanTransfer','finite_euclidean_transfer'),
'low_mode':('LowModeConvergence','low_mode_error'),
'constraint_kernel':('ConstraintAudit','compressed_anomaly_zero'),
'constraint_nonclosure':('ConstraintAudit','commutator_nonzero')}
font=TTFont(subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans Mono'],text=True).strip())
cmap={k for t in font['cmap'].tables for k in t.cmap}
mathfont=TTFont(subprocess.check_output(['fc-match','-f','%{file}','Latin Modern Math'],text=True).strip())
mathcmap={k for t in mathfont['cmap'].tables for k in t.cmap}
excerpts=[]; fallback=set()
for tag,(module,name) in selections.items():
    p=SRC/'formalization'/f'{module}.lean';raw,start=excerpt(p,name)
    rendered=''
    for c in raw:
        if c in '\\{}':rendered+=r'\CodeChar{'+str(ord(c))+'}'
        elif ord(c)>127 and ord(c) not in cmap:
            fallback.add(ord(c))
            if ord(c) not in mathcmap and ord(c) not in {0x29F8,0x2B1D}:raise RuntimeError('No fallback for '+hex(ord(c)))
            rendered+=r'\CodeSymbol{'+f'{ord(c):X}'+'}'
        else:rendered+=c
    (HERE/'excerpts'/f'{tag}.lean.txt').write_text(raw)
    (HERE/'excerpts'/f'{tag}.render.txt').write_text(rendered)
    record={'tag':tag,'module':module,'name':name,'source_file':'formalization/'+p.name,'start_line':start,'end_line':start+raw.count('\n')-1,'source_sha256':sha(p),'excerpt_sha256':hashlib.sha256(raw.encode()).hexdigest()}
    excerpts.append(record)
    (GEN/f'excerpt_{tag}.tex').write_text(r'\source{'+record['source_file']+r'}'+'\n'+r'{\footnotesize\color{muted}Exact lines '+str(record['start_line'])+'--'+str(record['end_line'])+r'; excerpt \code{'+tag+r'}. Hash in Section~\ref{sec:excerpts}.}\par\smallskip'+'\n')

out=[]
for r in ledger:
    out.append(r'\subsection{'+esc(r['item']+' — '+r['title'])+'}\n'+r'\label{result:'+r['item']+'}\n')
    out.append(r'\textbf{Preserved ledger scope.} '+esc(r['scope'])+'\n\n')
    out.append(r'\textbf{Formal endpoints.}\begin{itemize}'+'\n')
    for n in endpoints[r['item']]:
        rr=all_declarations[n]
        out.append(r'\item \code{'+n+'}; '+r'\code{'+rr['module']+'.lean}, line '+str(rr['line'])+'.\n')
    out.append(r'\end{itemize}'+'\n')
    if not r.get('main_declaration'):out.append('The endpoint pointers here are source-derived navigation added by this guide; the preserved JSON ledger supplies the module and scope but no principal-declaration field.\n\n')
    out.append('The scope is mathematical and finite where stated. The recorded status is inherited release coverage under these assumptions; it does not assert that every sentence of the preserved paper is separately formalized.\n\n')
(GEN/'result_map.tex').write_text(''.join(out))

out=[]
for p in modules:
    rs=[r for r in rows if r['module']==p.stem]
    out.append(r'\subsection{'+p.stem+': '+str(len(rs))+' theorem declarations}\n'+r'\source{formalization/'+p.name+'}\n')
    out.append(r'\begin{longtable}{@{}p{.76\linewidth}p{.17\linewidth}@{}}\toprule Named declaration & Source line\\\midrule\endhead'+'\n')
    for r in rs:
        state=('Core '+', '.join(reverse[r['declaration']])) if reverse[r['declaration']] else 'support'
        out.append(r'\code{'+r['declaration']+'} & '+str(r['line'])+'; '+state+r'\\'+'\n')
    out.append(r'\bottomrule\end{longtable}'+'\n')
(GEN/'catalog.tex').write_text(''.join(out))

imports=[]
for p in modules:
    imps=re.findall(r'(?m)^\s*(?:public\s+)?import\s+(?:all\s+)?([\w.]+)\s*$',active_text(p.read_text()))
    imports.append({'module':p.stem,'sha256':sha(p),'imports':sorted(set(imps)),'local_imports':sorted({x for x in imps if x in saved})})
out=[r'\subsection{Current local module graph}'+'\n'+'The dependencies below are read from both public imports and import-all commands. Duplicate imports count once. Import-all is significant in this Lean module edition because private implementation details can be needed by downstream proofs. A module with no local import still imports the pinned Mathlib files named in its source.\n'+r'\begin{longtable}{@{}p{.36\linewidth}p{.57\linewidth}@{}}\toprule Module & Direct current local imports\\\midrule\endhead'+'\n']
for r in imports:out.append(r'\code{'+r['module']+'} & '+('; '.join(r'\code{'+v+'}' for v in r['local_imports']) or 'Mathlib only')+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}\subsection{Current source SHA-256 identities}'+'\n')
for r in imports:out.append(r'\textbf{'+r['module']+r'}\par{\footnotesize\code{'+r['sha256']+r'}}\par'+'\n')
pins=json.loads((SRC/'provenance/lake-manifest.json').read_text())['packages']
out.append(r'\subsection{Pinned compiler and dependency revisions}'+'\n'+r'Compiler: \code{leanprover/lean4:v4.34.0-rc2}. Saved runtime commit: \code{6a10ac8c22beadecabdbb0919c2b50214762f91d}. The following are the nine manifest packages; replay should use the locked revisions, including inherited dependencies.\par'+'\n'+r'\begin{longtable}{@{}p{.23\linewidth}p{.70\linewidth}@{}}\toprule Package & Locked revision\\\midrule\endhead'+'\n')
for p in pins:out.append(esc(p['name'])+r' & \code{'+p['rev']+r'}\\'+'\n')
out.append(r'\bottomrule\end{longtable}'+'\n')
(GEN/'dependencies.tex').write_text(''.join(out))

out=[]
for r in excerpts:
    out.append(r'\subsection*{'+esc(r['tag'])+'}\n'+r'\source{'+r['source_file']+'}\n'+'Lines '+str(r['start_line'])+'--'+str(r['end_line'])+'; declaration '+r'\code{'+r['name']+r'}.\par'+'\n')
    out.append(r'{\footnotesize Source SHA-256: \code{'+r['source_sha256']+r'}.\par'+'\nExcerpt SHA-256: '+r'\code{'+r['excerpt_sha256']+r'}.}\par'+'\n')
(GEN/'excerpt_register.tex').write_text(''.join(out))
dump(GEN/'targets.json',rows);dump(GEN/'result_ledger.json',ledger);dump(GEN/'endpoint_navigation.json',endpoints)
dump(GEN/'imports.json',imports);dump(GEN/'dependency_pins.json',pins);dump(GEN/'excerpts.json',excerpts)
dump(GEN/'inherited_axiom_records.json',audits)
dump(GEN/'documentation_reconciliation.json',{'status':'PASS','source_modules':25,'named_theorems':323,'finite_items':19,'contiguous_exact_excerpts':len(excerpts),'excerpt_lines':sum(r['end_line']-r['start_line']+1 for r in excerpts),'inherited_axiom_sets':323,'inherited_run_started_utc':report['started_utc'],'inherited_run_updated_utc':report['updated_utc'],'fresh_lean_kernel_run':False,'font_fallback_codepoints':[f'U+{x:04X}' for x in sorted(fallback)],'scope':'source-bound static documentation checks, not new proof evidence'})
print(json.dumps({'modules':25,'theorems':323,'finite_items':19,'excerpts':len(excerpts),'fallbacks':[hex(x) for x in sorted(fallback)]}))
