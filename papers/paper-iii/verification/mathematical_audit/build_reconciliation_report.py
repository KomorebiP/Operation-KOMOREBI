#!/usr/bin/env python3
"""Serialize the completed bounded human proof review; not a proof checker."""
from pathlib import Path
import hashlib, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXP = ROOT / 'recovered/Paper_III/source/expanded/PSC_Paper_III_Annals_Human_Edition_Strengthened.tex'
FINAL = ROOT / 'traditional/Paper_III_Traditional_Final.tex'
PDF = ROOT / 'traditional/Paper_III_Traditional_Final.pdf'
FINITE = ROOT / 'recovered/Paper_III/source/finite'
EXPECTED = '492e7f39f676232d97dd8e73566215e4f1f976655b43df872e5542767794d8ff'
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(FINAL.read_bytes()) == EXPECTED, 'Frozen source changed; rereview required'
old, new = EXP.read_text(), FINAL.read_text()

reviews = [
('thm:exact_nonlinear_coordinates','Inverse analysis/synthesis identities cancel in reconstruction and composition; no linearity of the represented map is used.'),
('thm:jet_reconstruction','Finite multilinear expansion in all input slots and the output is exact; packet directions have the stated source types.'),
('cor:packet_taylor','C^(m+1) on a segment neighborhood supplies a continuous Bochner integrand; reduce to g(t)=F(x+th), then bounded output projection.'),
('thm:packet_faa','The partition chain rule is recovered inductively: the new direction either forms a singleton outer slot or joins exactly one existing block. Symmetry makes block enumeration harmless; finite packet insertion adds no factorial.'),
('thm:polynomial_tree_expansion','Closed radius-R ball is complete, invariant, and q-contracting. Finite bounded-height ordered trees equal Picard iterates; nonnegative scalar tree weights increase to a value at most R. This proves absolute convergence of unlabelled tree values.'),
('cor:quadratic_tree_expansion','For a,b>0 the smaller root obeys a+bR²=R and 2bR<1. Cases b=0 and a=0 are separated before dividing; uniqueness is local to the stated ball.'),
('thm:packet_tree_reconstruction','Each finite tree is reconstructed by finite sums at multilinear vertices. Infinite decorated expansions require grouping by the underlying tree; a flattened absolute convergence claim would be false.'),
('cor:tree_pruning','Zero vertex blocks kill the finite decorated value. Removing these zeros preserves each grouped finite sum and thus the grouped series.'),
('prop:packet_l_infinity','Continuity of the packet projectors, now explicit, justifies passage through the convergent arity series. Finite group-label sums occur inside each arity. Completeness by itself is insufficient.'),
('thm:defect_composition_identity','Add and subtract G_c(C_Y F_f(x)); its argument is exactly F_c(C_X x)+Delta_F(x). The Lipschitz estimate uses these two arguments.'),
('thm:iterated_orbit_defect','e_0=0 and e_(n+1)<=epsilon_n+q e_n yield the displayed powers in their correct order, including the empty n=0 sum.'),
('thm:fixed_point_stability','Both fixed-point identities give mismatch<=epsilon+q mismatch, hence the stated denominator for q<1.'),
('cor:multilevel_fixed_points','The sum telescopes through C_(0,l)x_l and uses bounded linear coarsenings. C_(a,a)=I supplies the first term and empty chain.'),
('thm:relative_obstruction_sequence','Checked connecting-lift independence and exactness at every kernel/cokernel term by representative chase; signs agree with D_f u_f=i_V v_0.'),
('thm:cone_obstruction','Cone differential squares to zero because D is a cochain map. Boundary (e,0)=d(eprime,c) means e=d_E eprime+D c and d_C c=0, exactly the cohomological image criterion.'),
('thm:right_inverse_correction','With explicitly bounded linear R and closed im D, range R is closed, Psi is q-Lipschitz, the radius condition gives invariance, and solutions inside range R are precisely fixed points.'),
('cor:correction_stability','Subtract the two fixed-point equations in the same invariant ball, use ||R|| and q, and divide by 1-q.'),
('thm:lyapunov_schmidt','Closed direct summands are Banach spaces with bounded projections. The derivative in X_1 is the stated Banach isomorphism; the local implicit graph supplies the range equation and zero first derivatives on K.'),
('cor:quadratic_reduced_obstruction','C² is explicit. All Dpsi(0) terms vanish, and pi_O L D²psi(0)=0 because im L=R.'),
('def:depth_obstruction','Filtration congruence preservation and L_m(F^(m+1)X) subset F^(m+1)Y make the defect and correction classes well typed; finite length is now distinguished from finite cardinality.'),
('thm:one_step_lifting','The first-order congruence is equivalent to Lbar_m[h]=-[Phi(x_m)]. A nonempty solution set is a kernel coset over modules, and an affine space only over a field.'),
('cor:finite_branch_count','Finite vector spaces over a finite field ensure actual finite cardinalities; the nonempty kernel coset has |ker Lbar_m| elements.'),
('lem:well_defined_lift_classes','Changing the parent representative translates its correction coordinate. Equality modulo F^(m+1)X is exactly equality of correction classes; congruence preservation keeps the child solution condition invariant.'),
('def:lift_tree','Vertices are solution congruence classes, not raw representatives; reduction gives a unique parent and fixes the root class.'),
('thm:finitely_branching_lift_tree','Finite branching and nonempty levels allow the successive infinite-descendant choice. Compatible representatives are Cauchy, and the separate complete-lifting argument applies.'),
('cor:unique_lift_branch','A zero kernel leaves at most one correction class at each stage; the proof now uses module coset terminology consistently.'),
('thm:complete_filtered_lifting','Compatibility gives eventual membership of differences in every F^rX; completeness gives a limit. Each F^rY is an open and closed subgroup; continuity and separatedness force Phi(limit)=0.'),
('prop:maurer_cartan_lifting','For degree-one eta,h, graded skew symmetry makes the mixed bracket equal [eta,h]. Since m>=1, F^(2m) lies in F^(m+1); the bracket/differential preserve the graded correction domain.'),
('fact:filtered_spectral_sequence','Finite decreasing filtration by subcomplexes agrees with the checked Stacks construction, E0/E1 indexing, functoriality, and convergence to graded cohomology.'),
('prop:fine_obstruction_survival','Survival means a nonzero permanent class modulo later boundaries. E1 degeneration detects zero total cohomology because the induced filtration is finite; it does not split extensions canonically.'),
('thm:exact_local_elimination','The corrected Banach setup includes F_Q(u0,v0)=0 and phi(u0)=v0. The implicit graph and retained equation are then equivalent to the full local zero equation.'),
('thm:schur_derivative','Differentiate the hidden equation through the basepoint graph: Dphi=-A^(-1)D_uF_Q. Substitution in the retained derivative gives the stated order of factors.'),
('thm:schur_second_derivative','Twice differentiating the hidden equation gives A D²phi=-D²F_Q[hhat,khat]. Substitution into the retained chain rule yields both displayed formulas without dropping D_vF_P.'),
('cor:reduced_packet_jets','Bounded packet projections on the retained/hidden Banach factors can be inserted into the verified first- and second-derivative formulas; no independent convergence claim is added.'),
]
assert len(reviews)==34

def block(text,label):
    marker='\\label{'+label+'}'
    pos=text.index(marker)
    start=text.rfind('\\begin{',0,pos)
    env=re.match(r'\\begin\{([^}]+)\}',text[start:]).group(1)
    end=text.index('\\end{'+env+'}',pos)+len('\\end{'+env+'}')
    tail=text[end:]
    if re.match(r'\s*\\begin\{proof\}',tail):
        end=text.index('\\end{proof}',end)+len('\\end{proof}')
    return {'sha256':sha(text[start:end].encode()),'line_start':text[:start].count('\n')+1,'line_end':text[:end].count('\n')+1}

claims=[]
for label,evidence in reviews:
    claims.append({'label':label,'reviewer':'paper3_audit','status':'passed after the recorded local repairs where applicable','evidence':evidence,'original_block':block(old,label),'final_block':block(new,label)})
smooth=json.loads((HERE/'smooth_transport_review.json').read_text())
for c in smooth['blocks']:
    claims.append({'label':c['label'],'reviewer':'smooth_transport_review','status':'passed after F1-F6 repairs where applicable','evidence':'Independent raw derivation recorded in smooth_transport_review.txt; local repair verification in its addendum and this final pin.','original_block':block(old,c['label']),'final_block':block(new,c['label'])})
assert len(claims)==56 and len({c['label'] for c in claims})==56

findings=[
{'id':'A1','labels':['thm:right_inverse_correction','cor:correction_stability'],'failure':'Bounded right inverse was not explicitly required to be linear although operator-norm estimates use linearity.','repair':'State bounded linear right inverse R.','status':'resolved'},
{'id':'A2','labels':['def:depth_obstruction','cor:finite_branch_count'],'failure':'Finite length was used to suggest finiteness of the obstruction class/cardinality. A one-dimensional vector space over R has finite length and infinite cardinality.','repair':'State finite length of the cokernel; reserve finite cardinality for finite graded pieces.','status':'resolved'},
{'id':'A3','labels':['prop:packet_l_infinity'],'failure':'Completeness alone does not permit discontinuous projections to commute with an infinite limit.','repair':'Require continuous packet projectors and use continuity in the proof.','status':'resolved'},
{'id':'A4','labels':['thm:packet_tree_reconstruction','cor:tree_pruning'],'failure':'The unlabelled absolute majorant cannot justify a flattened sum of all oblique packet decorations.','repair':'Keep the finite decoration sum grouped inside each underlying tree.','counterexample':{'space':'R² with Euclidean norm','B':'B(x,y)=(0,x1*y1)','s':'(1/8,0)','R':'1/4','majorant':'a=1/8,b=1, phi(R)=3/16<R, q=1/2','P1':'[[1,8],[0,0]]','P2':'I-P1','unlabelled_sum':'(1/8,1/64); every original tree with at least 3 leaves vanishes','flattened_failure':'Every left-comb tree decorated entirely by P1 has value (1/8,0), independent of the number of leaves, so the flattened terms do not tend to zero.'},'status':'resolved'},
{'id':'A5','labels':['sec:nonlinear_elimination','thm:exact_local_elimination','thm:schur_derivative','thm:schur_second_derivative','cor:reduced_packet_jets'],'failure':'The IFT setup omitted a zero value of the hidden equation at the designated basepoint.','counterexample':'F_Q(u,v)=exp(v) at (0,0) has invertible v derivative 1 and no zero anywhere.','repair':'Specify Banach source/target factors, F_Q(u0,v0)=0, A a Banach isomorphism, and phi(u0)=v0.','status':'resolved'},
{'id':'A6','labels':['cor:unique_lift_branch'],'failure':'The proof called a correction coset an affine space although the setting allows general modules.','repair':'Use a coset of the kernel.','status':'resolved'},
]
for item in smooth['findings']:
    item=dict(item); item['id']='S'+item['id'][1:]; item['status']='resolved'; findings.append(item)

required=[
'bounded linear right inverse',
'The cokernel below has finite length whenever the target graded piece has finite length',
'Assume the packet projectors are continuous for the topology',
'each underlying tree\'s finite sum of packet decorations is kept grouped',
'satisfies $F_Q(u_0,v_0)=0$',
'with $\\varphi(u_0)=v_0$',
'form a coset of $\\Ker\\overline L_m$',
'bounded self-adjoint projection',
'Zero projections are permitted in this section',
'every partition product is the empty product $I$',
'The continuous bounded generator has an evolution inverse',
'uniqueness of this bounded linear equation gives $UV=I$',
'first traverse $\\gamma_1$ and then $\\gamma_2$',
'Assume the complete packet family is twice continuously differentiable in operator norm on $[0,T]$. If',
]
assert all(s in new for s in required)
assert '\\max\\bigl(\\{0\\}\\cup' in new and '\\delta=\\max(\\{0\\}\\cup' in new

external=[
{'topic':'Banach implicit function theorem','status':'primary documented result checked; no new project formalization','url':'https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/ImplicitContDiff.html','source_revision':'be31cde2c2cb07d7562e5e891b302f9286cd0a68','source_url':'https://github.com/leanprover-community/mathlib4/blob/be31cde2c2cb07d7562e5e891b302f9286cd0a68/Mathlib/Analysis/Calculus/ImplicitContDiff.lean','translation':'Take the product factors as retained/hidden Banach variables. The implicit graph preserves the basepoint value, so a zero graph requires that value to be zero. Smoothness is inherited. This external source revision is not the Paper III pinned dependency.'},
{'topic':'Taylor remainder','status':'primary documented result checked','url':'https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/Taylor.html#taylor_integral_remainder','translation':'Apply the Banach-valued one-variable integral formula to t maps to F(x+th) on [0,1], with m+1 continuous derivatives. Finite packet projection is bounded.'},
{'topic':'Finite filtered complexes','status':'primary theorem construction/convergence checked','urls':['https://stacks.math.columbia.edu/tag/012K','https://stacks.math.columbia.edu/tag/012W'],'locators':['Lemmas 12.24.2, 12.24.4, 12.24.11'],'translation':'Use the abelian category of modules, K=C, the same decreasing filtration, and total degree n=p+q. The finite filtration ensures convergence to the induced graded cohomology. No extension splitting is inferred.'},
]

report={
'schema':'komorebi.paper_iii.scoped_reconciliation.v1','date':'2026-10-05',
'primary_verdict':'correct only after a stated restriction',
'verdict_target':'The recovered strengthened manuscript, with the explicit local repairs recorded here and implemented in the frozen traditional edition.',
'final_scoped_status':'All identified gaps and convention omissions are resolved at the pinned final source. No unresolved gap found within the 56 named blocks checked. This is not a global audit of all 95 proofs.',
'claim_card':{'objects':'Finite packet decompositions; Banach nonlinear maps and multilinear tree expansions; filtered correction problems; finite graph G-transports; finite self-adjoint Hilbert projector families.','conclusion':'The 56 explicitly named blocks below support their stated conclusions after the recorded restrictions and local proof completions.','hypotheses':'Finite packet sets; bounded linear maps where norm estimates use them; C^(m+1), C², closed range and complemented Banach domains where stated; continuous projections for convergent higher-operation series; congruence-preserving complete separated filtrations; specified G-valued gauges; self-adjoint projections and declared time regularity.','exceptional_cases':'Zero source/multilinear norm; m=0 empty iteration sum; zero module and empty packet family; zero projection members in the smooth section; T=0 identity products; finite length distinguished from finite cardinality.'},
'source_pins':{'recovered_expanded':{'path':str(EXP),'sha256':sha(EXP.read_bytes())},'final_traditional':{'path':str(FINAL),'sha256':EXPECTED},'final_pdf':{'path':str(PDF),'sha256':sha(PDF.read_bytes())},'finite_manuscript':{'path':str(FINITE/'paper/Projector_Resolved_Seed_Calculus_III.tex'),'sha256':sha((FINITE/'paper/Projector_Resolved_Seed_Calculus_III.tex').read_bytes())}},
'checked_named_blocks':56,'main_review_blocks':34,'complementary_review_blocks':22,'claims':claims,'findings':findings,
'dependency_graph':[
'Finite inverse analysis/synthesis -> exact coordinates -> finite jets -> partition composition.',
'Multilinear norm telescoping + invariant complete ball -> contraction fixed point; finite-height Picard trees + scalar nonnegative majorant -> unlabelled absolute series; finite packet insertion -> grouped decorated series.',
'Linear correction quotient -> associated graded cokernel test; congruence preservation -> representative-independent child classes; finite branching -> branch; completeness + continuity + separatedness -> exact limit solution.',
'Banach implicit function theorem + zero hidden basepoint + invertible hidden derivative -> local graph -> first/second Schur derivatives. Closed complementary range/kernel gives the Lyapunov Schmidt specialization.',
'Finite filtered-complex construction + finite convergence -> permanent classes and zero detection, without a canonical extension splitting.',
'Tree normalization + matching path order -> graph gauge classification. Self-adjoint packet identities -> skew generator -> invertible unitary evolution; positive two-sided overlaps -> direct polar rotation; C² local estimates + unitary telescoping -> O(mesh) convergence.'
],
'formal_reconciliation':{'contract_rows':41,'inherited_unique_mapped_declarations':143,'inherited_theorems':88,'inherited_constructions':55,'inherited_namespace_entries':468,'counts_evidence':'Inherited finite release contract and theorem map, not a fresh compiler execution.','raw_lean_read':'KomorebiPaperIII/NonlinearObstructions.lean: operation syntax/evaluation/locality and candidate-specific classical obstruction witness.','boundary':'Finite arbitrary-semantics unary/binary operation-tree locality is distinct from multilinear packet reconstruction, Banach tree convergence, Faà di Bruno, smooth transport, and filtered analytic existence. The expanded ordinary proofs do not enlarge the 41-row formal contract.','roadmap_reconciliation':'The final Part I roadmap statements are explicitly about formal coverage. Part II supplies the selected ordinary mathematical theorems with their own assumptions.'},
'external_source_checks':external,
'external_source_limitations':['The initial Caltech author-hosted AMR page returned 502; its book content was not treated as accessed.','A full page-by-page audit of the 15 inherited bibliography entries was not performed.','No novelty, priority, physical interpretation, or unrestricted existence claim was investigated.'],
'evidence_boundaries':{'fresh_lean_build':False,'new_numerical_runs':False,'source_metadata_as_proof':False,'global_95_proof_audit':False,'independent_external_peer_review':False,'original_source_edits':False},
'remaining_gap_in_checked_scope':None,
'strongest_safe_statement':'The frozen traditional Paper III supports the conclusions of the 56 specifically reviewed blocks with the stated repaired assumptions. Finite formal coverage remains exactly the inherited 41-row contract.',
'cheapest_next_check':'Preserve this final source hash during packaging; any later mathematical edit invalidates the corresponding block pin and requires a targeted rereview.',
'commands':'Read-only rg/sed raw-source inspection; SHA-256 source/block pinning; direct algebraic counterexample derivations; primary-source web reads. The serializer asserts the expected final hash and repair text, but is not a theorem prover.',
}
(HERE/'Paper_III_Scoped_Reconciliation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
lines=[
'PAPER III — BOUNDED MATHEMATICAL RECONCILIATION',
'Date: 2026-10-05',
'Primary verdict: correct only after a stated restriction.',
'Target: the recovered strengthened source and the local restrictions implemented in the final traditional edition.',
'',report['final_scoped_status'],'',
'FINAL SOURCE SHA-256: '+EXPECTED,
'FINAL PDF SHA-256: '+report['source_pins']['final_pdf']['sha256'],
'RECOVERED EXPANDED SHA-256: '+report['source_pins']['recovered_expanded']['sha256'],
'',
'SCOPE',
'34 selected nonlinear/filtered blocks plus 22 independently reviewed gauge/smooth blocks. Definitions and examples are included in this count; it is not a count of proofs. The final manuscript contains 95 retained proof environments. No whole-manuscript correctness certification is made.',
'',
'FINDINGS AND REPAIRS',
]
for f in findings:
    lines += [f['id']+' — '+', '.join(f['labels']),f.get('failure',f.get('issue','')), 'Repair: '+f.get('repair',f.get('minimal_repair','')), 'Final status: resolved.']
    if 'counterexample' in f: lines += ['Counterexample: '+(f['counterexample'] if isinstance(f['counterexample'],str) else json.dumps(f['counterexample'],ensure_ascii=False))]
    lines += ['']
lines += ['DEPENDENCY GRAPH']+report['dependency_graph']+['','OBLIGATION MATRIX']
for c in claims:
    lines += [c['label']+' — PASSED within the specified scope', c['evidence'], 'Final block SHA-256: '+c['final_block']['sha256']]
lines += ['','FORMAL BOUNDARY',report['formal_reconciliation']['boundary'],report['formal_reconciliation']['roadmap_reconciliation'],'The 41-row map reports 143 unique targets (88 theorems and 55 constructions), with 468 audited namespace entries. These are inherited release claims; this review did not compile Lean.','', 'EXTERNAL INPUT CHECKS']
for e in external: lines += [e['topic']+': '+e['translation'],e.get('url','; '.join(e.get('urls',[])))]
lines += ['', 'The initial Caltech author-hosted AMR page failed with HTTP 502. Official Mathlib documentation/source supplied the checked Banach IFT and Taylor interfaces instead. The full bibliography was not re-audited.','', 'NO REMAINING GAP FOUND IN THE CHECKED SCOPE',report['strongest_safe_statement'],report['cheapest_next_check'],'','METHOD AND LIMITS',report['commands'],'The exact counterexamples are analytic derivations, not bounded numerical experiments. Complementary review reports retain their original intermediate hashes; this report pins all 56 final blocks and the definitive edition.']
(HERE/'Paper_III_Scoped_Reconciliation.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'checked_blocks':56,'final_tex_sha256':EXPECTED,'findings_resolved':len(findings),'reports':['Paper_III_Scoped_Reconciliation.txt','Paper_III_Scoped_Reconciliation.json']}))
