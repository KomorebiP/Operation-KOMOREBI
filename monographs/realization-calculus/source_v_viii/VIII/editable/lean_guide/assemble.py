#!/usr/bin/env python3
"""Source-bound Paper VIII guide assembly. No Lean compiler is invoked."""
from pathlib import Path
import argparse,collections,hashlib,json,re,shutil,subprocess
from data_helpers import inventory,active_text,excerpt,esc
from fontTools.ttLib import TTFont
HERE=Path(__file__).resolve().parent
suffix=Path('source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot')
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=next((p/suffix for p in (HERE.parent,HERE.parent.parent) if (p/suffix).is_dir()),HERE.parent/suffix));args=ap.parse_args()
SRC=args.source.resolve();GEN=HERE/'generated';GEN.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
mods=sorted((SRC/'formalization').glob('*.lean'))
theorems=[r for p in mods for r in inventory(p)]
saved=json.loads((SRC/'verification/theorem_inventory.json').read_text())
report_path=SRC/'verification/sixth_final/SUMMARY.json'
report=json.loads(report_path.read_text());ledger=json.loads((SRC/'verification/coverage_ledger.json').read_text())
if len(mods)!=40 or len(theorems)!=392 or len({r['declaration']for r in theorems})!=392:raise RuntimeError('Unexpected theorem source counts')
tnames={r['declaration']for r in theorems};allnames={n for ns in saved.values()for n in ns}
records={r['declaration']:{**r,'kind':'theorem'}for r in theorems}
for p in mods:
    active=active_text(p.read_text());stack=[]
    for line_no,line in enumerate(active.splitlines(),1):
        ns=re.match(r'^namespace\s+(\S+)',line);sec=re.match(r'^(?:noncomputable\s+)?section(?:\s+(\S+))?\s*$',line);end=re.match(r'^end(?:\s+(\S+))?\s*$',line)
        if ns:stack.append(('namespace',ns.group(1)))
        elif sec:stack.append(('section',sec.group(1)))
        elif end:
            if stack:stack.pop()
        m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?(?:private\s+)?(def|abbrev|structure|inductive)\s+([^\s(:]+)',line)
        if m:
            name=m.group(2);namespace='.'.join(v for k,v in stack if k=='namespace');full=namespace+'.'+name if namespace else name
            records[full]={'declaration':full,'name':name,'kind':m.group(1),'line':line_no,'module':p.stem,'file':'formalization/'+p.name}
if allnames-set(records):raise RuntimeError('Unresolved audited names '+str(allnames-set(records)))
audited=[records[n]for p in mods for n in saved[p.stem]]
if len(audited)!=458 or len(allnames-tnames)!=66:raise RuntimeError('Construction count differs')
audits={k:v for m in report['modules']for k,v in m['axiom_audits'].items()}
if set(audits)!=allnames or not report['complete'] or not report['pass']:raise RuntimeError('Inherited audit mismatch')
evidence=[]
for p in mods:
    m=next(m for m in report['modules']if m['module']==p.stem);log=SRC/'verification/sixth_final'/m['log']
    if sha(p)!=m['sha256'] or sha(log)!=m['log_sha256']:raise RuntimeError('Inherited source/log hash '+p.stem)
    parsed={}
    for x in re.finditer(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",log.read_text(),re.M):
        if x.group(1) in parsed:raise RuntimeError('Duplicate log audit')
        parsed[x.group(1)]=[] if x.group(2)is None else[a.strip()for a in x.group(2).split(',')if a.strip()]
    if parsed!=m['axiom_audits'] or set(parsed)!=set(saved[p.stem]):raise RuntimeError('Compiler text/summary audit mismatch '+p.stem)
    if any(set(v)-{'propext','Classical.choice','Quot.sound'}for v in parsed.values()):raise RuntimeError('Unexpected axiom')
    evidence.append({'module':p.stem,'source_sha256':sha(p),'log':str(log.relative_to(SRC)),'log_sha256':sha(log),'theorems':m['theorem_declarations'],'construction_audits':len(m['construction_audits']),'exit_code':m['exit_code']})
for c in report['negative_controls']:
    if sha(SRC/c['source'])!=c['sha256'] or sha(SRC/'verification/sixth_final'/c['log'])!=c['log_sha256'] or c['exit_code']!=1 or not c['pass']:raise RuntimeError('Negative-control evidence identity')
selections={
'packet_family':('QuantumPacketCore','PacketFamily'),
'active_evaluation':('PacketIR','exact_active_evaluation'),
'support_inclusion':('PacketIR','product_support_inclusion'),
'adjoint':('PacketIR','exact_adjoint_block'),
'batch':('PacketIR','exact_matrix_batch'),
'bdlr_count':('PacketCostModels','bdlr_application_count'),
'roofline':('PacketCostModels','roofline_time_bound'),
'band_count':('BandedCount','banded_block_count'),
'bdlr_product':('LowRankAlgebra','bdlr_product'),
'chain_factors':('LowRankChains','chainFactors_correct'),
'woodbury':('LowRankAlgebra','bdlr_woodbury'),
'kronecker':('StructuredTensor','kronecker_modewise'),
'tensor_apply':('StructuredTensor','tensor_apply_correct'),
'walsh_apply':('WalshTransform','walsh_apply_correct'),
'toeplitz_apply':('ToeplitzEmbedding','toeplitz_embedding_action'),
'fourier':('CirculantFourier','circulant_spectral_representation'),
'power_paths':('TransferSupport','power_path_expansion'),
'nilpotent':('TransferSupport','nilpotent_of_path_bound'),
'inverse_support':('InverseSupport','inverse_block_zero_of_no_path'),
'schur_support':('SchurSupport','schur_support_inclusion'),
'solve_correct':('TriangularSolve','solve_correct'),
'schedule_depth':('GraphSchedules','optimal_depth'),
'packet_error':('PacketPerturbation','packet_perturbation_bound'),
'chain_error':('ProductChainError','product_chain_error_bound'),
'recompression_error':('ProductChainError','repeated_recompression_bound'),
'continuous_precision':('ContinuousPrecision','precision_allocation_optimal'),
'clipped_precision':('ClippedPrecision','clipped_unique_minimizer'),
'discrete_recurrence':('DiscretePrecision','discreteTable'),
'discrete_endpoint':('DiscretePrecision','discreteBudget_some_iff'),
'candidate_tree':('ExactTreeCompiler','CandidateTree'),
'cut':('ExactTreeCompiler','Cut'),
'tree_recurrence':('ExactTreeCompiler','optimalValue'),
'compile_attains':('ExactTreeCompiler','compile_attains'),
'tree_exact':('ExactTreeCompiler','exact_tree_compiler'),
'budget_recurrence':('QuantizedTreeCompiler','budgetTable'),
'budget_endpoint':('QuantizedTreeCompiler','compileBudget_some_iff'),
'budget_none':('QuantizedTreeCompiler','compileBudget_none_iff'),
'stored_tree':('StoredBudgetCompiler','storedTree'),
'stored_correct':('StoredBudgetCompiler','storedTree_correct'),
'pseudo_polynomial':('StoredBudgetCompiler','tabulation_pseudopolynomial'),
'compiler_stability':('TreeCompilerUpdates','compiler_stability'),
'local_update':('TreeCompilerUpdates','local_recompilation'),
'contract':('SchedulingContracts','contract_conversion'),
'grouping':('SchedulingContracts','grouped_execution_output'),
'amortization':('SchedulingContracts','integer_amortization_threshold'),
'krylov':('KrylovPackets','invariant_packet_krylov'),
'approx_krylov':('KrylovPackets','approximate_packet_krylov_distance'),
'jacobi':('BlockJacobi','block_jacobi_condition'),
'cg_bound':('BlockJacobi','certified_energy_error'),
'discovery':('DiscoveryCertificate','discovery_frobenius_certificate'),
'compact_factor':('CompactRangeFactors','compact_factorization'),
'best_rank':('SmallCoreTransfer','BestRank'),
'ambient_transfer':('SmallCoreTransfer','spectral_best_lift'),
'ordered_svd':('SmallCoreRecompression','OrderedThinSVD'),
'kernel_witness':('SpectralOptimality','prefix_kernel_witness'),
'spectral_best':('SpectralOptimality','diagonal_spectral_best'),
'weighted_tail':('FrobeniusOptimality','weighted_tail_lower'),
'frobenius_lower':('FrobeniusOptimality','diagonal_frobenius_lower'),
'recompression_optimal':('SmallCoreRecompression','recompression_optimality'),
'small_core_endpoint':('SmallCoreRecompression','small_core_optimal_recompression'),
'full_retention':('RecompressionEndpoints','recompression_full')}
# The source has theorems, definitions and two inductive excerpts. The extractor
# changes no source bytes; expand its declaration keyword set for the latter.
font=TTFont(str(HERE/'fonts/DejaVuSansMono.ttf'));cmap={k for t in font['cmap'].tables for k in t.cmap}
mathfont=TTFont(str(HERE/'fonts/latinmodern-math.otf'));mathcmap={k for t in mathfont['cmap'].tables for k in t.cmap}
excerpts=[];fallback=set()
for tag,(mod,name)in selections.items():
    p=SRC/'formalization'/(mod+'.lean');raw,start=excerpt(p,name);rendered=''
    for c in raw:
        if c in '\\{}':rendered+=r'\CodeChar{'+str(ord(c))+'}'
        elif ord(c)>127 and ord(c)not in cmap:
            fallback.add(ord(c))
            if ord(c)not in mathcmap and ord(c)not in{0x29F8,0x2B1D}:raise RuntimeError('No code glyph '+hex(ord(c)))
            rendered+=r'\CodeSymbol{'+f'{ord(c):X}'+'}'
        else:rendered+=c
    (HERE/'excerpts'/f'{tag}.lean.txt').write_text(raw);(HERE/'excerpts'/f'{tag}.render.txt').write_text(rendered)
    x={'tag':tag,'module':mod,'name':name,'source_file':'formalization/'+p.name,'start_line':start,'end_line':start+raw.count('\n')-1,'source_sha256':sha(p),'excerpt_sha256':hashlib.sha256(raw.encode()).hexdigest()};excerpts.append(x)
    (GEN/f'excerpt_{tag}.tex').write_text(r'\source{'+x['source_file']+'}\n'+r'{\footnotesize\color{muted}Exact lines '+str(start)+'--'+str(x['end_line'])+r'. Excerpt \code{'+tag+r'}. SHA-256 in Section~\ref{sec:excerpts}.}\par\smallskip'+'\n')
reverse=collections.defaultdict(list)
for r in ledger['records']:
    for n in r.get('lean_theorems',[]):
        if n not in records:raise RuntimeError('Unresolved coverage target '+n)
        reverse[n].append(r['number'])
out=[]
for r in ledger['records']:
    if not r.get('formal_scope') and r.get('lean_status')=='definition_or_expository_record':continue
    out.append(r'\subsection{'+esc(r['number']+' — '+r['title'])+'}\n'+r'\label{result:'+r['number']+'}\n')
    out.append(r'\textbf{Recorded status.} '+esc(r['lean_status'])+'.\n\n'+r'\textbf{Recorded hypotheses and scope.} '+esc(r.get('formal_scope','Classical input tracked separately; see the boundary discussion.'))+'\n\n')
    if r.get('lean_theorems'):
        out.append(r'\begin{itemize}'+'\n')
        for n in r['lean_theorems']:
            x=records[n];out.append(r'\item \code{'+n+'}; '+r'\code{'+x['module']+'.lean}, line '+str(x['line'])+'.\n')
        out.append(r'\end{itemize}'+'\n')
(GEN/'result_map.tex').write_text(''.join(out))
out=[]
for p in mods:
    rs=[r for r in audited if r['module']==p.stem];nt=sum(r['kind']=='theorem'for r in rs)
    out.append(r'\subsection{'+p.stem+': '+str(nt)+' theorems; '+str(len(rs)-nt)+' construction audits}\n'+r'\source{formalization/'+p.name+'}\n'+r'\begin{longtable}{@{}p{.75\linewidth}p{.18\linewidth}@{}}\toprule Audited declaration & Kind; line\\\midrule\endhead'+'\n')
    for r in rs:out.append(r'\code{'+r['declaration']+'} & '+esc(r['kind'])+'; '+str(r['line'])+r'\\'+'\n')
    out.append(r'\bottomrule\end{longtable}'+'\n')
(GEN/'catalog.tex').write_text(''.join(out))
imports=[]
for p in mods:
    xs=sorted(set(re.findall(r'(?m)^\s*(?:public\s+)?import\s+(?:all\s+)?([\w.]+)\s*$',active_text(p.read_text()))))
    imports.append({'module':p.stem,'source_sha256':sha(p),'imports':xs,'local_imports':[x for x in xs if x in saved]})
out=[r'\subsection{Direct local dependencies}'+'\n'+r'\begin{longtable}{@{}p{.34\linewidth}p{.59\linewidth}@{}}\toprule Module & Direct local imports\\\midrule\endhead'+'\n']
for r in imports:out.append(r'\code{'+r['module']+'} & '+('; '.join(r'\code{'+x+'}'for x in r['local_imports'])or'Mathlib / Init only')+r'\\'+'\n')
out.append(r'\bottomrule\end{longtable}\subsection{Source and compiler-log identities}'+'\n')
for e in evidence:out.append(r'\textbf{'+e['module']+r'}\par'+'\n'+r'{\footnotesize Source SHA-256: \code{'+e['source_sha256']+r'}.\par'+'\n'+r'Log SHA-256: \code{'+e['log_sha256']+r'}.}\par'+'\n')
out.append(r'\subsection{Pinned inherited run}'+'\n'+r'Lean version: \code{4.34.0-rc2}; saved compiler commit: \code{6a10ac8c22beadecabdbb0919c2b50214762f91d}; Mathlib revision: \code{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. The source archive does not include the separately supplied runtime kit. A new replay must obtain that kit and validate its actual revisions.\par'+'\n'+r'Summary SHA-256: \code{'+sha(report_path)+r'}.\par'+'\n'+r'Inventory SHA-256: \code{'+sha(SRC/'verification/theorem_inventory.json')+r'}.\par'+'\n')
(GEN/'dependencies.tex').write_text(''.join(out))
out=[]
for x in excerpts:out.append(r'\subsection*{'+esc(x['tag'])+'}\n'+r'\source{'+x['source_file']+'}\n'+'Lines '+str(x['start_line'])+'--'+str(x['end_line'])+'; '+r'\code{'+x['name']+r'}.\par'+'\n'+r'{\footnotesize Source SHA-256: \code{'+x['source_sha256']+r'}.\par'+'\n'+r'Excerpt SHA-256: \code{'+x['excerpt_sha256']+r'}.}\par'+'\n')
(GEN/'excerpt_register.tex').write_text(''.join(out))
dump(GEN/'targets.json',audited);dump(GEN/'source_declarations.json',list(records.values()));dump(GEN/'coverage_ledger.json',ledger);dump(GEN/'imports.json',imports);dump(GEN/'excerpts.json',excerpts);dump(GEN/'inherited_axiom_records.json',audits);dump(GEN/'compiler_evidence.json',evidence)
checks={'status':'PASS','source_modules':40,'theorem_declarations':392,'paper_viii_theorems':373,'reused_foundation_theorems':19,'construction_audits':66,'audited_names':458,'fully_checked_manuscript_items':56,'separate_classical_inputs':4,'exact_excerpts':len(excerpts),'excerpt_lines':sum(x['end_line']-x['start_line']+1 for x in excerpts),'inherited_summary_sha256':sha(report_path),'inherited_run_completed_utc':report['updated_utc'],'fresh_lean_kernel_run':False,'current_lean_executable':shutil.which('lean'),'current_lake_executable':shutil.which('lake'),'glyph_fallbacks':[f'U+{x:04X}'for x in sorted(fallback)],'scope':'Fresh static documentation reconciliation. Inherited compiler evidence is source- and log-bound, not a new kernel run.'}
chapter_text='\n'.join(p.read_text()for p in(HERE/'chapters').glob('*.tex'))
used=re.findall(r'\\excerpt\{[^{}]*\}\{([^{}]+)\}',chapter_text)
if set(used)!=set(selections)or len(used)!=len(selections):raise RuntimeError('Teaching excerpt use differs from selection register')
checks['all_exact_excerpts_taught_once']=True
dump(GEN/'documentation_reconciliation.json',checks);print(json.dumps(checks,indent=2))
