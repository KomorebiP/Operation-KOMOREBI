"""Build an exhaustive, statement-anchored coverage map, not a theorem counter.
Statuses are a reviewed semantic crosswalk. This script checks inventory,
anchors and declaration spelling; it does not certify equivalence of prose.
"""
from pathlib import Path
import json, hashlib, collections, argparse
ap=argparse.ArgumentParser(); ap.add_argument('--work',type=Path,required=True); ap.add_argument('--publication',type=Path,required=True); a=ap.parse_args()
W=a.work.resolve(); P=a.publication.resolve()
old=json.loads((P/'COMPANION_CROSSWALK.json').read_text())
current=json.loads((W/'current_expanded_records.json').read_text())
contracts={r['id']:r for r in old['journal_formal_contract']}
# C = whole mathematical statement mapped; P = partial or restricted; U = no
# complete mapped declaration; R = definition represented; D = documentary;
# B = boundary; I = classical input not yet integrated at the printed scope.
# Entries deliberately retain missing clauses even where a bridge is routine.
data={
1:('D',[], 'Regime declarations are distributed through Lean typeclass hypotheses, not one encoded regime object.'),
2:('D',[], 'Publication metadata. JSON records are not Lean proof declarations.'),
3:('B',[], 'Scope exclusion, not an additional positive theorem.'),
4:('U',[], 'General quiver path algebra, relation ideal, realizations and their morphisms are not encoded in this tranche.'),
5:('P',[15], 'Finite packet coordinates exist for supplied projectors. The collapse of an arbitrary typed grammar is not constructed.'),
6:('U',[], 'Missing category definitions, the two functors, and natural inverse isomorphisms for arbitrary typed grammars.'),
7:('P',[5,13], 'Actual range algebras and k[T] exist. The range of an arbitrary grammar action still needs the grammar construction.'),
8:('P',[5,28], 'Image-algebra rank invariance and exact-image hull naturality are proved. The general grammar-action factorization is not assembled.'),
9:('P',[1,2,15], 'Modules, seeds and packets are encoded separately. A full seeded-system object with topology and declared grammar is absent.'),
10:('P',[2,29], 'Algebraic span and normed operator hulls exist. The full Hausdorff topological-vector-space version is not encoded.'),
11:('D',[], 'A methodological criterion rather than a decidable Lean predicate.'),
12:('U',[], 'The general regular-module seed-rank-one corollary still needs a mapped wrapper. It is not the field-only full-matrix result.'),
13:('B',[], 'Target-independence restriction remains documentary.'),
14:('R',[2], 'multiSeedMap is the actual Finsupp linear combination map; finite families give the stated finite free module.'),
15:('C',[2], 'Actual range/span equality, quotient equivalence and generation/surjectivity equivalence are present.'),
16:('C',[2], 'seedFinrank_isLeast_free_surjection proves the finite minimum, not an executable basis algorithm.'),
17:('C',[1], 'oneSeedMap has the stated annihilator kernel and its quotient is the literal cyclic range.'),
18:('P',[], 'New polynomial-module cyclic-annihilator equality is proved. The arbitrary noncommutative ring two-sidedness criterion is not yet proved.'),
19:('P',[1], 'The normed isometry/dense-completion theorem is proved from supplied input maps. Constructing the transported locally convex topology and its action remains.'),
20:('P',[3,31], 'General algebraic cardinal rank is encoded, including zero. General topological cardinal rank is not; the bilateral-shift finite minimum is a separate example.'),
21:('C',[3], 'The nontriviality hypothesis agrees with the current publication.'),
22:('P',[4], 'Algebraic rank monotonicity follows through the semilinear identity specialization. General topological rank and a combined wrapper remain.'),
23:('P',[4,29], 'The full algebraic semilinear inequality is proved. The printed general topological-rank clause is broader than the normed dense-hull result.'),
24:('P',[5,28], 'Algebraic isomorphism invariance is proved. The general topological cardinal-rank clause is not encoded.'),
25:('P',[4], 'The quotient lower bound is available. Lifting generators through an arbitrary exact sequence for the upper bound remains.'),
26:('P',[4,6], 'The upper bound is explicit; projection lower bounds have the needed ingredients but the whole two-sided statement has no dedicated wrapper yet.'),
27:('C',[7], 'Actual product-algebra action and the maximum formula are proved.'),
28:('C',[8], 'The genuine tensor-product action and cardinal product upper bound are proved.'),
29:('B',[8], 'No universal tensor equality is exported. This boundary is not counted as a positive theorem.'),
30:('P',[8], 'General tensor generation gives a route. The scalar-extension specialization and the literal 1 tensor S generating family are not assembled.'),
31:('D',[4], 'A named use of the quotient lower bound, not a new proof target.'),
32:('C',[9], 'The character, surjective semilinear map and finite scalar dimension match the printed hypotheses.'),
33:('I',[], 'The printed noncommutative Nakayama input is not yet connected by a checked declaration here. Do not silently substitute only a commutative version.'),
34:('U',[], 'Need the quotient action, radical lifting of generators, and equality of canonical ranks.'),
35:('U',[], 'Need module-top equality and the residue division-ring dimension bridge.'),
36:('I',[], 'The existence of an abstract Wedderburn decomposition is not supplied by the certificate transport theorem.'),
37:('P',[10], 'Concrete split-field matrix models exist. The general division-ring regular-module equivalence is not supplied.'),
38:('P',[10], 'Split-field certificate transport is proved. Division-ring factors, abstract decomposition existence and the radical/top reduction remain.'),
39:('P',[10], 'The formula on a supplied split model is proved. The printed top quotient requires the module-top bridge.'),
40:('P',[11], 'Proved for positive matrix size over a field. Arbitrary division-ring scalars remain. Positive size is still required.'),
41:('P',[12], 'Proved for field-valued multiplicity matrices and positive block size, not arbitrary division rings.'),
42:('I',[], 'Mathlib has a proven PID torsion-module decomposition. This block uses its annihilator-attainment consequence, but does not yet instantiate all printed primary components of T.'),
43:('P',[13], 'General certificate assembly is retained; the self-adjoint case now constructs the data. General irreducible-polynomial residue quotients and intrinsic primary multiplicities remain.'),
44:('P',[13], 'The cyclic one-generator case now has a genuine minpoly quotient construction. The minimum for a general invariant-factor chain remains.'),
45:('P',[13,32], 'Intrinsic eigenspace dimensions and the exact maximum are now proved for self-adjoint operators. Arbitrary non-diagonalizable operators over an algebraically closed field remain.'),
46:('P',[14], 'Cyclicity iff minpoly=charpoly is now unconditional over any field; on nonzero spaces it also equals seed rank one. The primary, invariant-factor and scalar-extension geometric clauses remain.'),
47:('R',[15], 'LinearProjectorFamily encodes the actual finite completeness, idempotence and annihilation laws.'),
48:('P',[26], 'Packet coordinate support is used in reachability arguments. A general packet-purity predicate and its cardinal rank are not encoded.'),
49:('P',[], 'The coordinate-fibre refinement example is proved. Aggregating an arbitrary finite projector family and identifying every grouped range remain.'),
50:('R',[15], 'Analysis and synthesis use genuine projector ranges, not unconstrained packet slots.'),
51:('C',[15], 'Both inverse identities and the linear equivalence are proved.'),
52:('C',[16], 'Exact equality iff every projected coordinate agrees.'),
53:('P',[15,23], 'Coordinate equivalence and all-Hom block equivalence supply ingredients. The two arbitrary-domain/codomain universal properties and uniqueness wrappers remain.'),
54:('U',[], 'No general tensor projector family, range tensor equivalence, or resulting decomposition is mapped.'),
55:('U',[], 'The algebraic dual family and canonical dual-range identification are not mapped.'),
56:('P',[17], 'Closed ranges and bounded inverse maps in the canonical product norm are proved. The universal quantification over all equivalent finite-product norms needs explicit transport.'),
57:('R',[], 'New conditionNumber is the product of actual operator norms. packetConditionNumber identifies the literal analysis/synthesis norms.'),
58:('C',[], 'New proofs give the lower bound for nonzero X and both operator norm inequalities for an arbitrary bounded coordinate equivalence, hence any declared packet-coordinate norm.'),
59:('P',[18], 'The range/closure identity is fully proved. The printed unique extension of the whole split to completion still needs an explicit wrapper.'),
60:('U',[], 'The unconditional packet-sum space and its signed-sum norm are not encoded.'),
61:('U',[], 'Completeness of that specifically defined normed sequence space remains.'),
62:('U',[], 'Countable unconditional synthesis, the inverse maps and the quantitative norm bounds remain.'),
63:('D',[], 'A uniform-boundedness explanation. No instance for the signed packet partial-sum family is mapped.'),
64:('B',[], 'Convergence modes remain separate; finite identities are not used as infinite sums.'),
65:('R',[19,23], 'Ambient compositions and their genuinely range-restricted packet Hom maps are both encoded.'),
66:('C',[19], 'The existing result is more general: source and target can have different finite packet systems.'),
67:('C',[20], 'The output-first block product is proved for three possibly different modules.'),
68:('P',[21], 'All natural powers, including zero, are proved. Arbitrary nonidentical word products still need the iterated wrapper.'),
69:('C',[22], 'The result is proved for bounded self-adjoint outer maps, more generally than orthogonal packet projectors.'),
70:('U',[], 'Tensor-block factorization and the general tensor packet construction are not mapped.'),
71:('P',[20,28], 'Individual intertwining blocks and composition identities are proved. The complete arbitrary-source/target block-equation iff remains.'),
72:('C',[23], 'Full dependent packet Hom families and their multiplication are identified with the actual endomorphism algebra.'),
73:('P',[26], 'Orbit support obstructions exist. The one-step exact support statement with noncancellation equality conditions is not completely mapped.'),
74:('C',[24], 'The two dimension equalities are explicitly proved.'),
75:('U',[], 'The diagonal projection, its range, idempotence and the three-way commutant criterion remain.'),
76:('P',[25], 'A supported full-block predicate exists. The ambient operator support subspace still needs a named transported definition.'),
77:('P',[25], 'The two hard converses, identity/reflexivity and multiplication/transitivity, are proved. The complete ambient support-subalgebra equivalence is not assembled.'),
78:('P',[22], 'Adjoint reversal is proved. Bounded supported operators, the converse rank-one construction and star-subalgebra equivalence remain.'),
79:('U',[], 'The class quotient, nilpotent ideal, height bound and diagonal-class quotient algebra are not mapped.'),
80:('P',[26], 'Transfer edges and reflexive-transitive reachability are encoded. The exact generating-algebra presentation still needs the projector-generator comparison.'),
81:('P',[26], 'Word-hull support is proved. The full generated-algebra block-support statement requires the explicit span/adjoin bridge.'),
82:('P',[26], 'The complete orbit-hull obstruction is proved. Aligning that word hull with the printed algebra generated also by packet projectors is a remaining wrapper.'),
83:('U',[], 'Packet-pure cardinal seed rank and local corner ranks are not encoded.'),
84:('U',[], 'Need packet-pure rank and corner-algebra generator assembly.'),
85:('U',[], 'The general edge-surjectivity predicate and pure-block surjection data are not encoded.'),
86:('U',[], 'Need condensation components, local packet-pure ranks and the source propagation/lower-bound proof.'),
87:('U',[], 'The combined edge-surjectivity and corner-cyclicity predicate is not encoded.'),
88:('U',[], 'Depends on the general source-component theorem and local cyclicity reduction.'),
89:('B',[7], 'The unrestricted mixed-seed example is consistent with the proved product-algebra formula. The packet-pure rank calculation is not separately formalized.'),
90:('P',[27,28], 'Conjugation of projectors/blocks and graph/reachability invariance are proved. The full packet-dimension and support-preorder wrapper remains.'),
91:('P',[28], 'Strict injective-label morphisms are encoded. Arbitrary label maps and fibre aggregation remain.'),
92:('U',[], 'The seeded morphism condition and topological seeded category are not encoded.'),
93:('P',[28], 'Exact image-algebra hull naturality and strict block naturality are proved. Noninjective label aggregation and the seeded corollary remain.'),
94:('U',[], 'General packet and seeded categories, identities and composition laws are not mapped.'),
95:('U',[], 'Restriction and quotient packet construction, the packetwise short exact sequences and their assembly remain.'),
96:('U',[], 'The quotient family must be constructed from invariance, not supplied as an independent family.'),
97:('P',[27,28], 'Intertwining of supplied families is available. The invariant-subspace restrictions and actual quotient family remain.'),
98:('U',[], 'Need bounded quotient projectors, closed packet kernels and Banach exact-sequence maps.'),
99:('P',[29], 'The normed continuous-surjection density/range theorem is proved. General Hausdorff TVS and arbitrary fibre aggregation remain.'),
100:('P',[1,29], 'Dense isometric completion is proved in normed spaces. General quotient topology identification and locally convex realization remain.'),
101:('B',[], 'The quotient-map requirement is preserved; no open-map theorem is inferred from continuity alone.'),
102:('D',[], 'The declared preservation profile is metadata, not an instantiated Lean functor with all listed preservation proofs.'),
103:('U',[], 'Need formal typed expression/diagram transport for additive or linear functors and the claimed preserved constructions.'),
104:('U',[], 'Proof-profile transport remains a semantic theorem target, not a blanket consequence of matching names.'),
105:('D',[], 'A methodology and scope checklist, not automatic formal certification.'),
106:('D',[30,31,32,33,34,35], 'Example slots are editorial. Existing examples and algorithm specifications remain outside the 69 proved-record denominator.'),
107:('D',[], 'An export catalogue, not one additional kernel theorem or a completed formal package object.'),
108:('B',[], 'No discoverability, conditioning, identifiability or later-paper existence claim follows automatically from finite packet identities.')}
assert set(data)==set(range(1,109))
status={'C':'covered','P':'partial','U':'not_mapped','R':'definition_represented','D':'documentary','B':'scope_boundary','I':'classical_input_not_fully_integrated'}
extra={
18:['Komorebi.PaperICompletion.CyclicClassification.orbitMap_ker_eq_annihilator_of_surjective'],
42:['Komorebi.PaperICompletion.CyclicClassification.exists_full_annihilator_vector'],
43:['Komorebi.PaperICompletion.SpectralCertificates.selfAdjoint_operatorAlgebra_seedRanks'],
44:['Komorebi.PaperICompletion.CyclicClassification.minpolyQuotientEquivOrbit'],
45:['Komorebi.PaperICompletion.SpectralCertificates.selfAdjoint_seedRank_eq_max_eigenspace_finrank'],
46:['Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly','Komorebi.PaperICompletion.CyclicClassification.operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly','Komorebi.PaperICompletion.CyclicClassification.cyclic_four_way_without_polynomial_certificate'],
49:['Komorebi.Packet.fibreLinearProj_refinement'],
57:['Komorebi.PaperICompletion.ConditionedCoordinates.conditionNumber','Komorebi.PaperICompletion.ConditionedCoordinates.packetConditionNumber_eq'],
58:['Komorebi.PaperICompletion.ConditionedCoordinates.one_le_conditionNumber','Komorebi.PaperICompletion.ConditionedCoordinates.norm_coordinateOperator_le','Komorebi.PaperICompletion.ConditionedCoordinates.norm_le_conditionNumber_mul_coordinateOperator','Komorebi.PaperICompletion.ConditionedCoordinates.packet_conditioned_coordinate_bounds']}
rows=[]
for i,r in enumerate(old['expanded_records'],1):
 c=current[r['stable_id']];code,cr,note=data[i]
 decls=list(dict.fromkeys([d for n in cr for d in contracts[n]['declarations']]+extra.get(i,[])))
 rows.append({'ordinal':i,'stable_id':r['stable_id'],'kind':c['kind'],'title':r['title'],'status':status[code], 'old_contract_rows':cr,'mapped_declarations':decls,'scope_and_remaining_work':note,'current_source':{k:v for k,v in c.items() if k not in ('statement','proof')},'statement':c['statement'],'source_proof':c['proof'],'new_block_contribution':extra.get(i,[])})
counts=collections.Counter(x['status'] for x in rows)
proved={'theorem','corollary','proposition','lemma'}
proofrows=[r for r in rows if r['kind'] in proved]
report={'schema':'paper-i-coverage/0.2.0','status':'SEMANTIC_CROSSWALK_WITH_EXPLICIT_GAPS','inventory_complete':len(rows)==108,'proof_acceptance':'See final VERIFICATION.json; this file is not a compiler receipt.', 'policy':['Current traditional split TeX is the statement authority. Archived machine source is not allowed to override later corrected hypotheses.','Covered means a complete statement is mapped at the recorded scope. Partial includes both substantive missing proofs and unassembled consequences of existing declarations.','Not mapped does not claim impossibility or novelty; it means no complete declaration is established in this source closure.','Definitions, boundaries, classical inputs and editorial records are not counted as new proved theorems.','A correspondence map is a reviewed semantic artifact, not a kernel proof that English or TeX means the Lean type.'], 'counts':dict(counts),'proved_record_count':len(proofrows),'proved_record_status_counts':dict(collections.Counter(x['status'] for x in proofrows)),'records':rows}
assert len(proofrows)==69
out=W/'coverage';out.mkdir(exist_ok=True)
(out/'COVERAGE_108.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
lines=['# Paper I: expanded publication-to-Lean coverage, Block 02','',f'All **108** current stable records are accounted for. The proof-level denominator is **69**, not 108.','', 'This is a semantic crosswalk, not a new kernel pass for every publication claim. Partial records include missing constructions as well as outstanding wrappers around existing results. No aggregate completion percentage is asserted.','', '## Status counts','', json.dumps(report['proved_record_status_counts'],indent=2), '', 'The remaining 39 records are definitions, classical inputs, boundaries and a remark. Their separate statuses are retained in JSON.', '', '## Record-by-record map','']
for r in rows:
 lines.extend([f"### {r['ordinal']:03d} · {r['stable_id']}",f"**{r['title']}** · {r['kind']} · **{r['status']}**",'',r['scope_and_remaining_work'],'',f"Source: `{r['current_source']['file']}:{r['current_source']['statement_start_line']}-{r['current_source']['statement_end_line']}`.",''])
 if r['old_contract_rows']:lines.extend(['Existing contract rows: '+', '.join(map(str,r['old_contract_rows']))+'.',''])
 if r['mapped_declarations']:lines.extend(['Declarations: '+', '.join('`'+d+'`' for d in r['mapped_declarations'])+'.',''])
(out/'COVERAGE_108.md').write_text('\n'.join(lines))
print(json.dumps({k:report[k] for k in ('counts','proved_record_count','proved_record_status_counts')},indent=2))
