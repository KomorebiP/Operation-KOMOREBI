# Komorebi source assessment for Paper X

Date: 2026-09-08. Baseline: Paper X Block 20.

**Verdict: incomplete, with the arithmetic interpretation of finite packets as the smallest missing implication.** The inspected Komorebi files contain useful constructions. None of the inspected sources supplies a completed Lean proof of the full arithmetic Claim 8.2. The ledger remains **15 checked / 5 partial**.

The most useful connection is between the earlier papers' local deformation quotients, the already checked ring-point reconstruction, and an explicit arithmetic finite quotient. This points to an arithmetic application whose objects and finite reductions can be defined completely.

## Findings that affect the next step

| Existing work | Actual content | Consequence |
|---|---|---|
| Strengthened Paper XII, section “Local conditions are quotient packets” | Completed tensor quotient law, simultaneous local quotient conditions, and global base change | Gives a precise model for finite admissibility when an actual arithmetic condition is represented by a specified quotient |
| Paper X `Reconstruction.lean` | `ringReconstructionEquiv`, `localReconstructionEquiv`, `represented_local_algebra_reconstruction` | The generic reconstruction algebra already exists. Apply it to the quotient ring instead of proving another generic completion theorem |
| Komorebi Resolution Completion `Gluing.lean` | `constraint_inter_iff_of_finite_stable` and `certified_joint_gluing` | A condition detected at fixed finite depth can be combined with another separately approximable condition on the same completed stream |
| Komorebi Math R3 `deformation/support.py` | Finite presentations, Fitting minors and fiber support calculations | Supplies concrete equation and minor-certificate models for local conditions, but does not identify arithmetic period invariants |
| R3 tame and finite-image modules | Explicit finite operators, induction, orbit/stabilizer packets and monodromy chains | Useful exact-formalization templates and finite arithmetic examples. Several operator checks use complex floating arithmetic |
| Hodge Calculus Dyadic Completion | Geometric conductor projectors and candidate CM carriers | Potential examples for coefficient-independent geometric summands, after cohomological realizations and comparison naturality are constructed |

## The quotient connection

Suppose a local deformation condition is represented by a specified quotient $R/J$. Let $\mathcal O$ be complete and separated for the $\pi$-adic topology. Compatible maps

\[
f_m:R\longrightarrow\mathcal O/\pi^m
\]

that kill $J$ reconstruct to a map $f:R\to\mathcal O$. For every $j\in J$,

\[
f(j)\in\bigcap_{m\geq1}\pi^m\mathcal O=0.
\]

Thus $f$ factors uniquely through $R/J$. Equivalently, use the existing reconstruction theorem with source $R/J$ from the beginning. Coefficient compatibility and adic continuity must be retained when passing from algebraic points to continuous local points.

Separatedness is sufficient for the algebraic ideal-killing argument. Closedness of $J$ matters when identifying the quotient as the intended complete Hausdorff topological ring. Nonempty sets at separate finite levels still require a compatible branch, supplied by the already checked finite-branch machinery under its hypotheses.

The indispensable arithmetic statement is the natural identification

\[
\{\text{chosen framed arithmetic objects over }B\}
\cong\operatorname{Hom}_{\mathcal O\text{-alg}}(R/J,B).
\]

It must hold for the actual finite coefficient rings and the complete target, with compatible reductions. Paper XII explicitly treats representability of general arithmetic deformation conditions as an external input. Neither its quotient theorem nor the Python support code proves this identification for arbitrary Hodge–Tate or Weil–Deligne conditions.

## Recommended concrete arithmetic packet

Use

\[
A=\mathbb Z_2[X]/(X^2-1),\qquad
q:G_{\mathbb Q}\longrightarrow C_2.
\]

Here $q$ is the actual character already defined in `ArithmeticCertificateExample.absoluteQuadraticCharacter`, through the action on a square root of $-1$. The existing source proves continuity and that its underlying character hits the nonidentity element.

For every commutative $\mathbb Z_2$-algebra $B$, the proposed interpretation theorem is

\[
\operatorname{Hom}_{\mathbb Z_2\text{-alg}}(A,B)
\cong\{x\in B:x^2=1\}
\cong\operatorname{Hom}(C_2,B^\times).
\]

An element satisfying $x^2=1$ is its own inverse. Pullback along the fixed, surjective $q$ identifies these with the characters of $G_{\mathbb Q}$ factoring through this quotient. At finite precision, use $B=\mathbb Z/2^m$; at the complete level, use $B=\mathbb Z_2$, with their appropriate topologies.

The quotient equations $X-1=0$ and $X+1=0$ identify precisely the trivial and quadratic characters. These conditions agree modulo $2$, while giving different integral characters. The finite scheme also has points that do not lift: $3^2\equiv1\pmod8$, but both possible lifts $3,11\pmod{16}$ square to $9\pmod{16}$.

This supplies a meaningful next block:

1. Prove the natural point/character equivalence and its reduction compatibility.
2. Connect it to the existing actual $G_{\mathbb Q}$ quotient and continuity proofs.
3. Apply the checked completion theorem to these explicitly interpreted finite packets.
4. Prove the residual collision and nonlifting examples in Lean.

These connections are **proposed, not newly Lean-checked in this assessment**. This would complete a restricted arithmetic instance. It would not by itself finish the full Hodge–Tate/Weil–Deligne clauses of Claim 8.2.

## A second useful connection: gluing detected conditions

The separate Resolution Completion package proves that, on one fixed completed observation stream, separate approximability of $P$ and $Q$ implies approximability of $P\land Q$ if $P$ is determined at one finite observation depth.

Paper X's finite-group type detector at depth $v_\pi(|\Gamma|)+1$ is a candidate for this finite-stability premise on a domain of actual integral representations of the fixed group. The domains, reduction observations and common completed stream still have to be identified. This does not combine arbitrary independent local branches or prove arithmetic local-to-global existence.

The same package defines a closure predicate by finite approximability. Proving that predicate closed does not prove that an independently defined Hodge–Tate or Weil–Deligne condition equals it. Its file `CompactDynamics.lean` concerns finite-state programs, not topological compactness.

## What the broader search did not supply

- R3 `FrobeniusSpine.local_labels` is `Mapping[Hashable, Any]`. `CompanionForest` wraps a supplied finite forest. These do not define arithmetic packet reduction.
- R3's finite Frobenius separator explicitly leaves Chebotarev coverage beyond the supplied trace table unchecked. Completion and patching reports combine supplied conditional gates.
- The later strengthened Paper X explicitly assumes an identification of inverse limits with complete local realizations, and later a bijection from realizations to the inverse limit. It clarifies the missing input rather than constructing it. Its realization definition also explicitly requires semisimplicity, which must be addressed if that later statement is adopted.
- The Completion Atlas's determinant route invokes a classical determinant-to-semisimple-representation theorem and coefficient descent assumptions. It supplies no checked arithmetic period comparison.
- Universal Seed Calculus and Universal Seed Lifting retain arithmetic realization, compatibility and representability assumptions. Their general completion language does not remove this distinction.
- The Hodge files concern rational/complex Hodge structures and Fermat motives. Their label `(HT)` means **half-twist correspondence**, not Hodge–Tate. The explicit CM packet correspondence is still stated as an open problem. Their geometric projectors are useful future examples, not existing p-adic comparison theorems.

The Hodge source's conductor projectors are rational combinations of graph correspondences. They could select the same geometric summand in multiple cohomological realizations once those realizations and comparison naturality exist. Those prerequisites were not supplied by the inspected files.

## Source locations and review scope

All source inspection was read-only. This pass did not edit production Lean files, run a Lean build, execute the Python test suites, or independently verify the external classical theorems cited by the papers. The small modular example above is direct arithmetic, not an exhaustive computation or a new compiler result.

Sources retrieved and inspected:

- `Komorebi_Math_1.0.0b4_Repair_R3.zip`: actual source and relevant tests in `langlands/local`, `langlands/finite_image`, `deformation/companions.py`, `deformation/support.py`, completion gates and patching reports.
- `Komorebi_Resolution_Completion_v0.12.0_LEAN_VERIFIED.zip`: actual `Core.lean`, `Constraints.lean`, `Gluing.lean`, `Transport.lean`, refinement and boundary sources.
- `PSC_Langlands_Maximal_Completion_Archive.zip`: relevant sections of the strengthened Papers X–XII, Completion Atlas, monomial and Clifford material. The strongest direct new source lead is Paper XII's `thm:tensor_quotient`, `cor:simultaneous_local`, and `prop:global_local_basechange`.
- `Projector_Resolved_Local_Langlands.tex`: located as an additional local-packet source; the detailed local-model conclusions above are grounded in the inspected R3 modules and Paper XI sections, not a claim to have audited this entire standalone paper.
- `Projector_Resolved_Hodge_Calculus_Dyadic_Completion.tex` and `Fermat_Hodge_Final_Gap_K23_Half_Twist.md`: conductor projectors, CM candidates and explicit correspondence boundary.
- `Universal_Seed_Calculus_Source(1).zip` and `Universal_Seed_Lifting_Release(1).zip`: relevant arithmetic, completion and remaining-assumption sections.
- Current Paper X Block 20: exact Claim 8.2 and `ClassCommonSpine.lean`, `CompletionAssembly.lean`, `Reconstruction.lean`, `RepresentationTopology.lean`, `PrecisionCompletion.lean`, and `ArithmeticCertificateExample.lean`.

Some discovery requests encountered a temporary capacity error. Retried searches and materialized source archives enabled the inspection above. Empty search results were not used as evidence that a theorem is absent. The conclusion is bounded to the inspected sources.

Conservative mathematical proofreading of this assessment checked notation, equation integration, stated hypotheses and the distinction between existing proofs and proposed applications. No manuscript was changed or typeset.

## Source snapshot hashes

| Source | SHA-256 |
|---|---|
| Komorebi_Math_1.0.0b4_Repair_R3.zip | 24cbd13e88dd5ab9aa4cf13e4530ece2a6643a09ce79c160b99b6f2d4562436a |
| Komorebi_Resolution_Completion_v0.12.0_LEAN_VERIFIED.zip | fb9e7f4d370a639e2f0ac65e1cfebd55b040de86ae55f7b0e247dd1c05b2dfdc |
| PSC_Langlands_Maximal_Completion_Archive.zip | 158c4e8e7af0ef3a5c20ad827bdfdc09753ff4272092114c7d3bc376df8bfa00 |
| Projector_Resolved_Hodge_Calculus_Dyadic_Completion.tex | f2869d8c9e12fd261b005e6562376b3668bf32f9376a0046f919ea9f01f26302 |
| Fermat_Hodge_Final_Gap_K23_Half_Twist.md | 294057cb29bb0a4fe70589bd13f003015fe6d9a14a7758912c733480ae0609e4 |
| Universal_Seed_Calculus_Source(1).zip | 9163c303052e2f763b2020d8041931f94efd6b8ba78ac3cac40fe1ba0ed06e45 |
| Universal_Seed_Lifting_Release(1).zip | 4de124c85d8befcbd6c15cae15dc2e31d23fa594b829a3e3671a113b6a89347d |
