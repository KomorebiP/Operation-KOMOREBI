from pathlib import Path
import json, hashlib, re, shutil, zipfile, importlib.util

ROOT=Path('/mnt/data/Strong_Artin_Audit_2026-09-11')
inv=json.loads((ROOT/'inventory.json').read_text())
sources=json.loads((ROOT/'sources.json').read_text())
release=ROOT/'replay/Strong_Artin_Lean_v0.25.0_Graded_Compatibility_Lifting'
fresh=json.loads((release/'RESULT.json').read_text())
partial=json.loads((ROOT/'lineage_replay_current/progress.json').read_text())
checks=json.loads((ROOT/'negative_checks.json').read_text())
assert fresh['status']=='PASS' and fresh['all_exit_codes_zero']
assert len(partial['module_results'])==30 and all(x['returncode']==0 for x in partial['module_results'])

# Repeat a narrow textual trust-boundary scan without evaluating project code.
def mask(text):
 out=list(text);i=0
 while i<len(text):
  if text.startswith('/-',i):
   a=i;dep=1;i+=2
   while i<len(text) and dep:
    if text.startswith('/-',i): dep+=1;i+=2
    elif text.startswith('-/',i): dep-=1;i+=2
    else:i+=1
   for j in range(a,i):
    if out[j]!='\n':out[j]=' '
  elif text.startswith('--',i):
   j=text.find('\n',i);j=len(text) if j<0 else j
   for z in range(i,j):out[z]=' '
   i=j
  elif text[i]=='"':
   a=i;i+=1
   while i<len(text):
    if text[i]=='\\':i+=2
    elif text[i]=='"':i+=1;break
    else:i+=1
   for j in range(a,min(i,len(text))):
    if out[j]!='\n':out[j]=' '
  else:i+=1
 return ''.join(out)
patterns=['debug.skipKernelTC','skipKernel','addDecl','run_elab','implemented_by','native_decide','unsafe','Lean.ofReduceBool','sorryAx']
trust=[]
for sh,s in sources.items():
 text=mask((ROOT/s['audit_path']).read_text())
 for pat in patterns:
  for m in re.finditer(r'(?<![\w])'+re.escape(pat)+r'(?![\w])',text):
   trust.append({'source':s['basename'],'pattern':pat,'line':text[:m.start()].count('\n')+1})
(ROOT/'trust_scan.json').write_text(json.dumps({'scope':'178 exact-byte-deduplicated active Lean source files; comments and strings masked','patterns':patterns,'occurrences':trust,'limitation':'Static screening is not a proof of the absence of all possible unsafe metaprogramming; the pinned Lean kernel and Mathlib cache remain trusted.'},indent=2))

current=set(inv['current_v025_ancestor_archives'])
rows=[]
for r in inv['by_root']:
 rows.append('| '+r['archive'].replace('Strong_Artin_Lean_','').replace('_Checked.zip','')+' | '+str(r['own']['proof_declarations'])+' | '+str(r['closure']['proof_declarations'])+' | '+('Yes' if r['archive'] in current else 'Sibling')+' | `'+r['sha256'][:16]+'…` |')
branch_table='\n'.join(rows)

findings=[
 {'id':'A1','severity':'critical to application','finding':'Auxiliary augmentation does not imply descent to original equations','status':'Shortcut refuted by an exact example; latest v0.25 boundary correctly excludes it','action':'Prove factorization through the auxiliary-zero quotient, genuine level descent, or a separate original-equation lifting theorem.'},
 {'id':'A2','severity':'critical to application','finding':'Bare H1Cotangent is not automatically the arithmetic obstruction or dual Selmer space','status':'Comparison remains an assumed Datum; latest boundary corrects earlier overbroad wording','action':'Specify the actual deformation functor, coefficient ideal, derived cotangent/Selmer complex, base change, duality and cohomological degrees.'},
 {'id':'A3','severity':'critical to scope','finding':'Absolutely irreducible prime-to-p finite image forces p not dividing rank','status':'Elementary averaging/Schur proof supplied in this audit; not newly Lean-formalized','action':'Do not count this specialization as coverage of the p-dividing-rank sector; identify an actual difficult representation covered by the hypotheses.'},
 {'id':'A4','severity':'major arithmetic comparison','finding':'One-dimensional normalization does not identify a general full local H1 pairing','status':'Current-ancestry source assumes its entire compared H1 is one-dimensional; rank-two norm-zero example has dimension two','action':'Construct the correct unramified subspace or local quotient line and prove compatibility, not merely abstract nondegeneracy.'},
 {'id':'A5','severity':'major inference','finding':'Residual collapse proves uniqueness/comparison, not residual automorphic occurrence','status':'Earlier root-is-occupied prose was unsupported','action':'Keep Galois residual uniqueness separate from a nonzero determinant-bearing automorphic complex.'},
 {'id':'A6','severity':'major interpretation','finding':'Determinant selection inside a torsor does not prove membership or attachment','status':'Local reducible-restriction example has equal determinants and cube data without a scalar twist','action':'State irreducibility/membership hypotheses explicitly; do not label all p-not-dividing-rank attachment steps solved.'},
 {'id':'A7','severity':'major nonlinear condition','finding':'Residual syzygies do not give exact moving identities or correction exactness','status':'v0.24 negatives and v0.25 assumptions correctly address this boundary','action':'Construct B(x)F(x)=0 and prove image(Jbar)=kernel(Bbar) for the actual problem; compatibility alone is insufficient.'},
 {'id':'A8','severity':'major evidence management','finding':'Same version labels denote multiple unmerged branches','status':'741 declarations in v0.25 ancestry versus 960 in all-branch union','action':'Identify checkpoints by branch title and full SHA-256; do not count the union as a single compiled release.'},
 {'id':'A9','severity':'verification scope','finding':'A complete whole-ancestry fresh replay was not obtained','status':'v0.25 direct closure PASS; 30 additional ancestor modules PASS; broader run INCOMPLETE after two interrupted wrappers','action':'Preserve module-level evidence and rerun outstanding modules before declaring the whole ancestry freshly checked.'},
 {'id':'A10','severity':'interpretation','finding':'Minimal scalar labels need not equal the number of arithmetic primes','status':'Abstract finite selection is valid; primes/local components and changing arithmetic conditions are additional inputs','action':'Distinguish labels, scalar functionals, places, local tangent dimensions and arithmetic auxiliary sets.'},
 {'id':'A11','severity':'scope/strategy','finding':'A quotient by the scalar coefficient module is not automatically quotienting H1 by one global cyclic class','status':'No general cohomological identification established','action':'Use the long exact sequence or the actual fixed-restriction Selmer complex, including the connecting morphism.'},
]
summary={
 'title':'Strong Artin / Komorebi–Langlands audit through v0.25',
 'date':'2026-09-11',
 'review_type':'self-review of mathematical applications plus fresh machine replay; not an independent human/third-party referee audit',
 'primary_verdict':'incomplete, with the smallest missing implication',
 'verdict_scope':'The proposed end-to-end Strong Artin deduction, not the correctness of every individual conditional algebra theorem.',
 'current_checkpoint':inv['current_root'],
 'current_checkpoint_sha256':'cf9669502a2cfa332e4c6d9da5b40d51f98b226e2099a5593017287cfdbb492c',
 'current_ancestor_source_inventory':inv['current_v025_ancestor_closure'],
 'all_available_branch_source_inventory':inv['available_union'],
 'archive_nodes':inv['distinct_archives'],
 'archive_crc_failures':inv['archive_crc_failures'],
 'fresh_latest_replay':{'status':fresh['status'],'source_modules':17,'axiom_audit_modules':1,'new_named_constants_axiom_audited':55,'all_exit_codes_zero':fresh['all_exit_codes_zero'],'result':'replay_evidence/v025_RESULT.json'},
 'additional_ancestor_replay':{'status':'INCOMPLETE','observed_successful_source_modules':30,'observed_Lean_failures':0,'outer_interruptions_without_complete_module_verdict':['StrongArtinFiniteCore','PreChebotarevSelector'],'result':'replay_evidence/partial_ancestry_progress.json','note':'The original partial manifest summary field passed_modules is stale after outer interruption. This audit counts its 30 persisted module_results, not that summary field.'},
 'unique_source_modules_freshly_replayed_this_audit':47,
 'not_claimed':['All 128 current-ancestry modules freshly replayed','All 178 branch-union modules build together','Full Mathlib source rebuild','Independent kernel implementation check','New unconditional Strong Artin or relative arithmetic automorphy theorem','Universal novelty of the algebraic synthesis','Percentage completion of an open conjecture'],
 'exact_negative_examples':checks,
 'findings':findings,
 'source_count_qualification':'Counts are source theorem/lemma declaration occurrences after exact file-byte deduplication, not independent discoveries or a Lean-environment declaration export.',
}
(ROOT/'AUDIT_SUMMARY.json').write_text(json.dumps(summary,indent=2))

report=r'''# Strong Artin / Komorebi–Langlands audit through v0.25

**Date:** 11 September 2026  
**Scope:** the available Strong Artin Lean archive family and its application claims, not the entire twelve-paper Komorebi corpus.  
**Review type:** self-review with source inspection, exact counterexamples and fresh compiler replay. This is not an independent human referee report.

## 1. Verdict

**Primary verdict for the proposed end-to-end Strong Artin argument: incomplete, with essential arithmetic comparison and existence implications missing.**

The archive family contains a substantial collection of precise, conditional algebraic theorems. The latest v0.25 result was freshly reproduced from an extracted copy. Its main nonlinear lifting theorem survives this review under its stated hypotheses. What does not survive is the stronger interpretation that repeated abstract algebraic extensions have already completed most of an arithmetic automorphy theorem.

Several earlier messages conflated four different accomplishments:

1. a valid theorem in algebra, representation theory or cohomology;
2. a proved consequence of an assumed arithmetic comparison interface;
3. construction of that interface for the intended Galois/Hecke objects;
4. an unconditional new Langlands application.

The work has substantial evidence for (1) and (2). It has not established a full passage through (3) to (4). Earlier percentage estimates for progress toward solvable or unrestricted Strong Artin are withdrawn: neither the theorem count nor the number of checklist entries supports such percentages.

The meaningful current description is a **branching, formally checked algebraic lifting and resolution library motivated by a cyclic Strong Artin strategy**, with important missing arithmetic instantiations.

## 2. What was actually checked

### Archive and source audit

The audit traversed 22 mounted top-level release archives and 23 distinct archive nodes after resolving embedded ancestors. Every scanned ZIP passed CRC integrity testing. Source files were retained only from active `src` paths, excluding verification extracts, scratch files and generated build copies. Files were deduplicated by exact SHA-256 byte identity. Nested comments, line comments and strings were masked before counting explicit declarations.

| Scope | Source files | Theorems | Lemmas | Proof declarations | Definitions | Abbreviations | Structures | Instances |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current v0.25 ancestor closure | 128 | 740 | 1 | **741** | 214 | 20 | 8 | 7 |
| All available branches, byte-deduplicated union | 178 | 959 | 1 | **960** | 331 | 30 | 16 | 7 |

There is one inductive declaration in each scope. The current closure contains 18,759 lines under this audit's `splitlines()` convention; the union contains 24,771. These are not counts of independent mathematical discoveries or a single compiled Lean environment. In particular, conditionals and helper lemmas count as proof declarations.

No active occurrences of `sorry`, `admit`, custom `axiom`, custom `opaque`, or `sorryAx` were found. Additional screening found none of the specifically checked kernel-bypass/metaprogramming markers listed in `trust_scan.json`. Static screening is not a substitute for compilation and does not eliminate the ordinary Lean/Mathlib trust boundary.

### Fresh verification

The portable runtime was reconstructed from the seven supplied parts and its assembled SHA-256 matched `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

The authoritative new v0.25 replay compiled seven unchanged dependency modules, ten v0.25 modules, and an all-new-constant axiom audit. All 18 compiler invocations returned zero. The 55 named new constants were axiom-audited; only `propext`, `Classical.choice` and `Quot.sound` were reported. The final release verifier returned `PASS`.

Pinned environment:

```text
Lean 4.34.0-rc2
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

An expanded attempt to rebuild the full current ancestry obtained 30 additional successful, disjoint source-module compilations. Two outer execution wrappers interrupted the broader run, during `StrongArtinFiniteCore` and `PreChebotarevSelector`, before a complete module verdict was captured. No Lean theorem failure was observed in those interrupted runs, but they are not passes. The complete 128-module ancestor replay was **not** obtained. The partial manifest's `passed_modules` summary field is stale; its 30 persisted module records are the evidence used here.

Thus 47 unique source modules were freshly compiled in this audit. This is not a fresh check of all 741 declarations in the current ancestry, nor a combined build of all 960 declarations. Mathlib's pinned compiled cache was reused rather than rebuilt, and no independent implementation of the Lean kernel was used.

## 3. Branch lineage is not a straight version ladder

Version numbers were reused for distinct releases at v0.14, v0.18, v0.21, v0.22 and v0.23. The exact v0.25 root is:

```text
Strong_Artin_Lean_v0.25.0_Graded_Compatibility_Lifting_Checked.zip
cf9669502a2cfa332e4c6d9da5b40d51f98b226e2099a5593017287cfdbb492c
```

Its ancestry takes the **v0.18 Cyclic H1 Tate Normalization**, **v0.21 Completed Formal Presentation**, **v0.22 Cotangent Obstruction**, and **v0.23 Intrinsic Syzygy** branches. It does not contain every sibling result discussed in the conversation.

The 219 additional declarations in the available union come from six sibling branches: alternate v0.14 (44), alternate v0.18 (32), v0.21 auxiliary integration (24), v0.21 Taylor–Wiles polynomial presentation (30), v0.22 presented-algebra tangent (50), and v0.23 representation-deformation H1 (39).

In particular, the representation-tangent/gauge-to-H1 branch is available but is not part of v0.25's ancestor closure. It should not be silently described as merged into that release.

The older 492-declaration audit is reproduced for its explicitly named v0.18 **Finite Cyclic H1 Local Comparison** lineage. It was not the same v0.18 branch used by subsequent v0.19–v0.25 releases. The old and new line-count conventions differ by whether a terminal newline contributes an additional line; theorem counts are unaffected.

### Archive table

“Own” counts include any production source copied into that archive, so ancestor copies must not be summed without deduplication. “Closure” is the exact source-union count through its embedded ancestors.

| Archive branch | Own proof declarations | Ancestor closure | In current ancestry? | SHA-256 prefix |
|---|---:|---:|---|---|
''' + branch_table + r'''

## 4. Mathematical inventory and precise scope

| Family | Mathematical content present in source | Surviving scope | Missing application |
|---|---|---|---|
| Finite cyclic representation theory | Twist torsors, spectral/Fourier/coefficient selectors, modular comparison and finite-image recovery ingredients | Finite algebra under explicit field, semisimplicity, restriction and representation hypotheses | Existence and alignment of the automorphic parameter is not supplied by a selector |
| Cyclic defect algebra | Monic quotient, characteristic-p fibre `k[u]/u^p`, generic roots and cyclic action | An exact finite-flat algebra model and branch symmetry | Realizing this model as the relevant arithmetic/Hecke object |
| Equivariant support | A nonempty transitive-invariant branch support is all branches | Module/support statements under an actual equivariant action | Constructing a nonzero automorphic module, correct generic identification and equivariance |
| Projector detection | Trace probes, centering, conjugation covariance, finite extraction | Separation under spectral hypotheses; some clean-image specializations | Actual residual-image coverage and local arithmetic realizability |
| Cohomological survival / affine quotient | Finite-group averaging, cocycle selection, finite semidirect packaging, conjugacy-stable data | Finite/discrete algebra and conditional use of suitable quotient data | Continuous Galois instantiation and Chebotarev/local condition comparison |
| Finite auxiliary selection | Exactly dimension-many independent scalar labels; adaptive kernel reduction | Correct linear-algebra theorem | Labels must become compatible local conditions at actual primes |
| Jacobian completion | Dual annihilator criteria, column representation and minimal count | Equation-space linear algebra | Chosen columns need not be actual arithmetic deformation variables |
| Local pairing | Perfect centralizer/Frobenius-coinvariant trace pairing; finite cyclic H1 with norm zero | Algebraic finite cyclic cohomology, plus conditional comparison data | Continuous local H1, selected subquotients, Tate twist and pairing identification |
| Nilpotent Hensel lifting | Polynomial Taylor gain, nilpotent right-inverse correction, exact finite-level roots | Principal nilpotent residue kernel and stated rank/compatibility hypotheses | The actual arithmetic equations must satisfy those hypotheses |
| Formal and presented algebras | Nilpotent substitution, completed quotient points; sibling functor-of-points and dual-number tangent results | Finite-level algebraic presentation results | Representation of the intended locally constrained arithmetic functor |
| Cotangent/syzygy correction | Raw relation kernel surjects onto presentation cotangent H1 with redundancy kernel | Valid presentation exact sequence; Selmer identification remains assumed | Correct derived arithmetic obstruction, coefficients, degrees and base change |
| Actual representation equations | Sibling tangent/gauge classification; v0.25 associativity and square-zero correction criterion | Ordinary first-order representation algebra | Continuous locally constrained obstruction class and arithmetic vanishing/exactness |
| Moving-syzygy nonlinear lifting | Exact moving identities plus residual exactness lift the original polynomial system | Strongest newly reproduced generic nonlinear result | Prove those exact identities and exactness in the intended application |

Many of these ingredients have standard mathematical antecedents. The audit establishes scope and reproducibility, not priority or a theorem that the synthesis is historically new.

## 5. The strongest latest theorem, stated without arithmetic overreach

Let `q : R -> k` be surjective, with R commutative, k a field, kernel `(pi)`, and pi nilpotent. Let F be a finite coordinate polynomial system and B(x) a polynomial matrix of relation coefficients. Let x0 be a residual solution.

Assume:

\[
B(x)F(x)=0\quad\text{for every }x\equiv x_0\pmod\pi,
\]

and

\[
\operatorname{im}\bar J_{x_0}=\ker\bar B_{x_0}.
\]

Then there is x in the same residual fibre with F(x)=0.

This is theorem `PolynomialMovingSyzygyHensel.exists_exact_root_over_principal_nilpotent_residue`, lines 96–123 of the source snapshot. The fresh replay checks the theorem and its dependencies.

The mechanism is sound: write a nonterminal error as F(x)=pi^n e; exact moving relations force the leading residue of e into ker Bbar; residual exactness places it in the Jacobian image; polynomial Taylor gain improves the error order; nilpotence terminates the iteration. No integral retraction onto a compatible target is assumed.

The two difficult hypotheses are not replaced by names such as “syzygy” or “Selmer.” They are actual equality statements. The theorem is not about all local Artin rings, arbitrary nonprincipal maximal ideals, an inverse-limit solution, or an automorphic carrier.

## 6. Application audit findings

### A1. Solving auxiliary-augmented equations is not solving the original equations

Take R=Z/4 and F(x)=x²+1. Squares are 0 or 1, so F has no root. However

\[
F(1)+2=1+1+2=0\pmod4.
\]

Thus F(x)+y=0 has the exact solution (1,2), reducing to (1,0) modulo 2. Its residual Jacobian in (x,y) is [0,1], which is surjective. All of the auxiliary polynomial and Hensel conclusions can hold while the original system remains insoluble.

The quotient map A_aug -> A_original obtained by setting y=0 does not make an arbitrary point A_aug -> R factor through A_original: that requires the point to kill the auxiliary ideal.

**Verdict:** the generic augmentation theorems remain correct. Their interpretation as automatically producing the desired arithmetic point is false without a descent/specialization theorem. The latest v0.25 boundary explicitly records this correction.

### A2. Cotangent H1 is not automatically the deformation obstruction or dual Selmer space

The v0.22 exact sequence identifying presentation redundancy is useful. It does not, by itself, prove that `H1Cotangent` is the relevant arithmetic obstruction space.

The source `SelmerPresentationComparison.lean` explicitly defines:

```lean
structure Datum (P : Algebra.Presentation R S ι σ)
    (H : Type z) [AddCommGroup H] [Module S H] where
  intrinsicEquiv : P.toExtension.H1Cotangent ≃ₗ[S] H
```

Consequences of this datum do not construct its `intrinsicEquiv`. Moreover, the intrinsic finite-selection capstone assumes `[Field S]`, where S is itself the algebra presented by P. Reinterpreting S as a residue field changes the algebra whose cotangent complex is being computed; the necessary derived base-change comparison for a nontrivial deformation ring is an additional theorem.

Cotangent deformation theory involves derived Hom/Ext with the square-zero kernel as coefficients. The required degree depends on whether one is lifting a map, lifting an algebra, or solving a representation-deformation problem. Bare homology H1, its residue fibre, its dual, an Ext group and a dual Selmer space cannot be interchanged merely because they have related dimensions. Stacks Tags 08S3 and 00S0 make these distinctions explicit.

A concrete base-change warning: for S=F5[t]/t², the cotangent differential is multiplication by 2t. Its kernel is (t). The map from that kernel to S becomes zero after taking the residue, but the base-changed differential is zero and has a one-dimensional kernel. The natural comparison cannot be assumed to be an isomorphism.

**Verdict:** the presentation exact sequence survives. The earlier claim that `Selmer ≃ H1Cotangent` is the universally correct replacement was too strong. The v0.25 boundary has appropriately returned this to a degree-/coefficient-sensitive arithmetic comparison problem.

### A3. The clean irreducible prime-to-p image regime excludes p dividing rank

Let k be algebraically closed of characteristic p, Gamma finite of order invertible in k, and rho absolutely irreducible on a nonzero n-dimensional V. Define the Reynolds operator on matrices:

\[
E(X)=|\Gamma|^{-1}\sum_g\rho(g)X\rho(g)^{-1}.
\]

It centralizes rho, so Schur's lemma gives E(X)=a_X I. Trace is preserved, hence n a_X=tr(X). Taking X to be a rank-one matrix unit yields n a_X=1. Consequently n is nonzero in k, so p does not divide n.

This is an elementary mathematical deduction in the audit, not a newly Lean-checked declaration.

**Verdict:** the automatic irreducible prime-to-p specialization cannot itself resolve the p-dividing-rank sector that earlier messages emphasized as difficult. More general conditional detection theorems are not refuted, but applicability to that sector has not been demonstrated.

### A4. The local comparison is not merely an arbitrary normalization choice

In the current ancestor branch, `LocalTateNormalizationBoundary.lean` assumes both

```lean
e : L ≃ₗ[k] groupCohomology.H1 (Rep.of ρ)
hdim : Module.finrank k L = 1
```

where rho is the action on the full matrix coefficient module. The theorem does not itself construct a selected one-dimensional local quotient of a higher-dimensional H1.

For example, over F3 let C6 act on 2-by-2 matrices by conjugation with diag(1,-1). The cyclic norm is zero, but the Frobenius quotient has dimension two: the two diagonal directions survive. Thus the compared full H1 is not a line.

Two nonzero functionals on a two-dimensional space, such as the first and second coordinate maps, do not have identical kernels. Likewise two perfect pairings need not differ by a single scalar. A general arithmetic trace/Tate comparison requires identification of the relevant local subquotient and actual compatibility. The alternate v0.18 branch correctly assumes a unit-multiple comparison rather than inferring it from nondegeneracy alone.

**Verdict:** finite cyclic H1 and unit-scaling theorems survive under their hypotheses. The statement that only nondegeneracy of local Tate duality remains was too strong. Full local Galois H1, its unramified part, a tame quotient and a chosen local line must be kept distinct.

### A5. Residual collapse is a uniqueness theorem, not a carrier-existence theorem

If two semisimple residual representations with the required restriction data exist, the comparison theorem may identify them. This does not construct a residual Galois representation from an arbitrary Hecke eigensystem, and it does not place that eigensystem in determinant-bearing cohomology.

Earlier wording such as “the residual root is now occupied” moved an existence input into the completed column without proof. The latest boundary is more accurate: the nonzero patchable automorphic carrier remains missing.

### A6. Determinant selection is not automatic cyclic attachment

A determinant can select a member of a known scalar-twist torsor when p does not divide n. This does not prove that a candidate local automorphic parameter belongs to that torsor.

For p=3 and n=2, let zeta be a primitive cube root and take A=diag(zeta,zeta^-1), B=I. Then A³=B³ and det(A)=det(B)=1, yet A is not a scalar quotient twist of B. Their common lower local restriction is reducible. The same calculation is checked exactly over F7 in the audit examples.

**Verdict:** this does not contradict the correct irreducible-restriction torsor theorem. It does refute the stronger shortcut that determinant matching and base-change matching alone settle all p-not-dividing-rank local attachment problems.

### A7. Compatibility of defects is not correction exactness

For F(x)=(x,x²), the residual Jacobian at zero has horizontal image. Nevertheless F(2)=(2,4) modulo 8 is not horizontal. The exact moving relation is (-x,1)F(x)=0, not the frozen residual row (0,1).

Similarly, C=2R in R=Z/4 contains 2, which is divisible by 2 in R but not in C because 2C=0. These examples explain why an integral compatible target or graded-layer argument is needed.

v0.24 identified these failures, and v0.25 supplies the correct graded repair. But associativity only proves that a representation defect satisfies a relation; it does not prove that every such defect is in the image of the correction operator. The quotient between compatible defects and correctable defects is exactly where a genuine obstruction can remain.

**Verdict:** the current generic repair is substantive and survives. Arithmetic exactness, rather than compatibility alone, remains the indispensable input.

### A8. Branch counts are not one merged theorem library

The current ancestry has 741 declarations. The available union has 960. Neither number should be described as the number of new independent Strong Artin results, and the second is not a build result. Reused version numbers led prior summaries to combine siblings as if they were sequential additions.

### A9. Fresh compiler coverage is narrower than the source inventory

The v0.25 release was freshly reproduced, including all 55 new named-constant axiom reports. The expanded ancestry replay stopped after 30 additional modules. A passing latest checkpoint does not freshly reverify every historical declaration merely because old archives are embedded.

No actual Lean theorem failure was observed in the completed fresh builds. The failures found in this audit are chiefly application-level implications and scope inflation, not a demonstration that Lean accepted a false proposition.

### A10. Minimal scalar labels need not be minimal arithmetic prime sets

The finite-selection theorem counts independent scalar functionals. If an auxiliary label includes a prime together with an eigenspace choice, distinct labels may use the same prime. Conversely, simultaneous local deformation constraints may not be independently available merely because their scalar functionals exist. The arithmetic construction must show that the selected label family is realizable with the required local conditions and changing Selmer data.

### A11. Removing a scalar coefficient module is not automatically removing one global class

The quotient End(V)/kI is a coefficient-module quotient. Dividing a global H1 space by one cyclic character class is a different operation. The long exact cohomology sequence for 0 -> kI -> End(V) -> End(V)/kI -> 0 includes maps and a connecting term that must be analyzed. Fixed-restriction deformations and their allowed gauge group supply yet another precise relative condition.

**Verdict:** no general identification of these transverse models may be presumed. An actual relative Selmer complex is needed.

## 7. External theorem checks and novelty boundary

The audit checked primary-source statements in the following bounded scope:

- **Stacks Project, Tag 08S3, Lemma 91.2.1 and Remark 91.2.4:** square-zero map-lifting obstructions are expressed using an Ext group, with the kernel module as coefficients; changing lifts modifies the obstruction by the derivative correction map.
- **Stacks Project, Tag 00S0, Section 10.134:** the naive cotangent complex and the extra conditions needed for base change to commute with its homology.
- **Miagkov–Thorne, “Automorphy lifting with adequate image,” Forum of Mathematics, Sigma (2023), Definition 1.1 and Theorems 1.2–1.3:** generalized eigenspace projectors are part of existing adequacy theory; the published arithmetic results carry substantive residual automorphy, local, regularity and field hypotheses. Their adequacy definition includes p not dividing n.
- **Scholze, “On torsion in the cohomology of locally symmetric varieties,” Annals of Mathematics 182 (2015), 945–1066:** the published statement concerns Galois representations associated with eigensystems occurring in specified cohomology, not universal occurrence of the project's singular finite-Satake descents. Only the publisher's theorem-level abstract was inspected here, so it is not treated as a complete audit of every integral or nilpotent coefficient detail of the paper.

Source identifiers:

```text
https://stacks.math.columbia.edu/tag/08S3
https://stacks.math.columbia.edu/tag/00S0
https://doi.org/10.1017/fms.2023.3
https://annals.math.princeton.edu/2015/182-3/p03
```

This is not an exhaustive novelty review. It supports saying that the project organizes and formalizes recognizable existing mechanisms. It does not support calling the framework a foundation for all Langlands or asserting that its packaging has no precedent.

## 8. The corrected dependency graph

The current safe algebraic chain is:

```text
specified equations F and exact identities B(x)F(x)=0
  + actual residual image(J)=kernel(B)
  + principal nilpotent coefficient level
  -> leading-error compatibility
  -> corrections at successive powers
  -> exact root of F.
```

The safe representation chain is:

```text
chosen lift of a representation across a square-zero kernel
  -> multiplicativity defect
  -> associativity compatibility identity
  -> a correction exists iff the defect lies in the correction image
  -> genuine representation lift.
```

The missing arithmetic construction is not a single already-proved arrow:

```text
continuous locally constrained Galois deformation problem
  -> correct cochain/Selmer/cotangent comparison
  -> actual local detector and auxiliary-prime theorem
  -> genuine arithmetic exactness / obstruction removal
  -> nonzero determinant-bearing automorphic carrier
  -> level descent or supported specialization to the target point
  -> local-global compatibility and automorphic attachment.
```

The carrier and obstruction-removal arrows are separate substantive requirements. The exact dependency order will depend on the chosen patching or finite-precision route. In particular, a scalar-label selection theorem does not manufacture the Hecke module on which patching operates.

## 9. What is still needed, grouped by mathematical obligation

1. **A correctly typed arithmetic deformation problem.** Specify continuous Galois representations, coefficient rings, strict equivalence, fixed restriction, determinant/polarization data, allowed ramification and local lift conditions. Prove the first-order and obstruction identifications in that category, including base change and coefficient ideals.
2. **A genuine local-to-global auxiliary theorem.** Identify the local continuous cohomology and Tate pairing with the actual selected spectral condition, construct the finite Galois quotient, apply Chebotarev in its valid range, and show the resulting primes give the intended local deformation variables rather than arbitrary slack variables.
3. **Actual obstruction exactness.** Establish that compatible errors in the locally constrained arithmetic complex are correctable, or establish the weaker vanishing necessary for the target class. A relation identity alone does not establish exactness.
4. **Automorphic occurrence and support.** Produce a nonzero carrier with a Galois determinant/deformation action and sufficient level variation, flatness/depth, local-global compatibility and twist equivariance. The general algebra cannot supply this missing automorphic object.
5. **Descent back to the target.** Remove auxiliary ramification/coordinates or prove supported specialization at the required point. Then handle the ramified local parameters and, where relevant, classicality.
6. **Uniform scope.** Demonstrate these steps for every intended invariant cyclic stage, including cases not covered by clean prime-to-p hypotheses. The passage to nonabelian simple factors is a further research program, not a formal consequence of solvable induction.

These obligations should replace numerical progress percentages. Some are formalizations of known results in restricted ranges; others require a genuinely new arithmetic construction in the intended range.

## 10. Meaning for Komorebi Resolution Theory

The most defensible reusable contribution is an explicit separation of:

- presentation redundancy;
- compatible error directions;
- actual obstruction classes;
- allowable correction maps;
- nilpotent lifting depth;
- generic support and symmetry;
- existence of the arithmetic carrier itself.

The v0.24 and v0.25 negative controls are valuable: they prevent the resolution language from silently identifying objects that behave differently. The moving-syzygy theorem is a concrete successful lifting result, rather than an analogy.

The appropriate claim is a rigorous algebraic resolution toolkit with conditional interfaces to Langlands constructions. The audited material does not establish a new foundation of the Langlands program, universal obstruction removal, or an unconditional solution of Strong Artin. Whether any particular synthesis or proof method is new requires a focused literature review.

## 11. Recommended next checkpoint

Before generating another broad set of helper theorems, select a single explicit arithmetic test case and write an end-to-end theorem contract. Record the exact source of every external input and prove that its hypotheses are met. Separately, consolidate the branches under unique names and hashes and complete an integrated replay.

The most useful proof-development target is the actual representation obstruction class and its local conditions: normalize the multiplicativity defect, establish its cohomology class and independence of choices, identify the correctability criterion, and only then show what real auxiliary conditions accomplish. That is a sharper target than adding another abstract `Datum` equating the desired spaces.

## 12. Evidence package and limits

The evidence package contains the inventory and source hashes, exact source snapshots, reproducible finite-example code, fresh v0.25 replay result and logs, partial ancestry replay records, and the audit summary. It does not include the multi-gigabyte portable runtime or a new mathematical release.

Original release archives were left unchanged. Audit output and replay objects are separate. No full manuscript-by-manuscript or twelve-paper Komorebi audit, full Mathlib rebuild, independent proof-checker verification or exhaustive historical novelty analysis is claimed.
'''
(ROOT/'AUDIT_REPORT.md').write_text(report)

# Add concise index and clean replay evidence without generated Lean objects/runtime.
ev=ROOT/'replay_evidence';ev.mkdir(exist_ok=True)
shutil.copy2(release/'RESULT.json',ev/'v025_RESULT.json')
shutil.copy2(release/'verify.py',ev/'v025_verify.py')
shutil.copy2(ROOT/'lineage_replay_current/progress.json',ev/'partial_ancestry_progress.json')
for root,label in [(release/'verification/fresh','v025_fresh'),(ROOT/'lineage_replay_current/logs','partial_ancestry')]:
 if root.exists():
  for f in root.rglob('*'):
   if f.is_file() and f.suffix in {'.log','.json'}:
    target=ev/label/f.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
(ROOT/'README.md').write_text('''# Strong Artin audit evidence, 11 September 2026

Read `AUDIT_REPORT.md` first, then `AUDIT_SUMMARY.json` for machine-readable scope.

- Current v0.25 ancestry: 741 theorem/lemma declarations in 128 unique source files.
- Available all-branch union: 960 declarations in 178 unique source files. This is not one compiled release.
- Fresh v0.25 replay: 17 source modules plus all-new-constant axiom audit, PASS.
- Expanded ancestry attempt: 30 additional source modules passed, but the whole-ancestry run remained incomplete.
- Exact counterexamples test application shortcuts, not Strong Artin or the correctly stated conditional Lean theorems.

`source_blobs/` contains original active source snapshots deduplicated by exact SHA-256. `inventory.json` records branch provenance. No source theorem is modified here.

`tools/inventory.py` reads supplied `Strong_Artin_Lean_v*.zip` files under `/mnt/data`. Its root constants can be edited for local use. `tools/negative_checks.py` uses only the Python standard library. The v0.25 verifier requires the original release directory and exact portable Lean kit; the large kit is deliberately not bundled.

This is a self-audit, not an independent expert review. Do not interpret source counts or partial replay logs as a complete end-to-end automorphy proof.
''')

# Provenance hashes for selected audit outputs. Preserve report and raw manifests.
chosen=[ROOT/'README.md',ROOT/'AUDIT_REPORT.md',ROOT/'AUDIT_SUMMARY.json',ROOT/'inventory.json',ROOT/'sources.json',ROOT/'negative_checks.json',ROOT/'trust_scan.json']
chosen+=list((ROOT/'tools').glob('*.py'))
chosen+=list(ev.rglob('*'))
chosen+=list((ROOT/'source_blobs').rglob('*.lean'))
chosen=sorted({x for x in chosen if x.is_file()},key=lambda p:str(p))
(ROOT/'AUDIT_SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in chosen))
chosen.append(ROOT/'AUDIT_SHA256SUMS.txt')
out=Path('/mnt/data/Strong_Artin_Audit_2026-09-11_Evidence.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in chosen:z.write(p,'Strong_Artin_Audit_2026-09-11/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps({'report':str(ROOT/'AUDIT_REPORT.md'),'evidence_zip':str(out),'zip_bytes':out.stat().st_size,'zip_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'report_words':len(report.split()),'files':len(chosen),'trust_scan_hits':len(trust)},indent=2))
