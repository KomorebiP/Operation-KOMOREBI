# Independent scope review: Claims 9.1, 9.2, 11.1, and 11.2

Review date: 2026-09-08. Read-only review of the frozen Block 22 manuscript and production Lean. No new Lean theorem was compiled during this review, and no production source was edited.

Base archive: `PRSC_X_v0.22.0_Checked_TwentySecond_Block.zip`, SHA256 `36073e737aac860ef1db06f9cc8e7b9ec915534387f200a1f48f9c4249666c75`.

## Finding

None of these four claims can be promoted to the ledger's **full arithmetic** checked status solely by assembling the existing interfaces. Claim 11.2 has the shortest logical proof and its quantified abstract equivalence is already proved. It is not an independent way around the arithmetic interpretation needed for Claim 8.2. Claim 9.1 has one substantial arithmetic input, Frobenius coverage, in addition to a system/member identification bridge; Claim 9.2 inherits that input and requires actual local-invariant additivity; Claim 11.1 imports both completion and carrier recovery.

There is an important distinction between this assessment and an assertion that more arithmetic existence theorems must be added as hypotheses. The source already supplies the relevant forests, local closure, compatible carrier, and constituent systems where specified. Unconditional occupancy, universal local closure, and construction of an unknown carrier are **not** obligations of these conditional claims.

## Claim 9.1: finite Frobenius separation

Exact source statement: finitely many pairwise nonisomorphic strictly compatible systems, all members absolutely irreducible, with common algebraic unramified traces admit a square invertible trace matrix at distinct permitted unramified places. The same algebraic determinant stays nonzero under every coefficient embedding. Ordinary Frobenius trace comparison excludes places above the coefficient residue characteristic.

The source proof fixes a coefficient prime and uses character independence and density of the union of Frobenius conjugacy classes. It then selects independent evaluations and descends the matrix to the common number field.

Available exact interfaces:

* `GeneralCharacters.independent_irreducible_characters` handles arbitrary monoids in characteristic zero, assuming pairwise nonisomorphism of the actual representations at the field in question.
* `GeneralCharacters.irreducible_dense_separator` assumes density of the conjugacy-saturated supplied samples and continuous characters.
* `ProfiniteSeparation.irreducible_separator_of_quotient_coverage` replaces density by `QuotientCoverage`, meaning that every coset of every open normal subgroup contains a conjugate of a supplied sample.
* `TraceRecovery.common_trace_separator` and determinant/recovery transport handle the common algebraic matrix.

These are enough once the **actual arithmetic sample map**, its permitted-place domain, and its quotient coverage are supplied and proved. Neither the project nor the pinned Mathlib contains an identified Chebotarev theorem under a search for `Chebotarev`, `Čebotarev`, or relevant attached compatibility type names. This is a bounded source search, not a claim about all formal libraries.

A concrete additional general lemma could close the system/member bridge: equality of one member's characters forces equality of the common algebraic traces by injectivity of the coefficient embedding; density and irreducible character separation then force equivalence at every other coefficient prime. This requires specifying system isomorphism as the intended family of member equivalences, and it still needs arithmetic coverage. Therefore this useful lemma alone would not finish 9.1.

## Claim 9.2: compatible-carrier summand completion

Exact source hypotheses supply a semisimple strictly compatible carrier decomposed into compatible absolutely irreducible systems, together with bounded natural multiplicities at one coefficient prime. The conclusion has two parts: the same multiplicities define a strictly compatible summand at every coefficient prime, and finitely many Frobenius traces uniquely recover them.

`CarrierSummands` constructs the actual sum representation and equivariant split inclusion/retraction. `CarrierPolynomials` proves its characteristic-polynomial and trace formulas. `CarrierCompatibility` proves common polynomials, continuity, triviality on supplied sets, and recovery from an actually nonsingular sampled trace matrix. Later local/monodromy modules construct and compare supplied operator data. These are substantive parts of the conclusion.

Two exact missing implications prevent full completion:

1. The intended arithmetic Galois-to-local-data attachment must commute with these sums, including the requisite coefficient comparisons and Hodge–Tate/period conditions. Supplied local operator data are not already the attached arithmetic data merely by renaming a structure.
2. The trace matrix must come from the actual arithmetic separator in 9.1, not an additional nonsingularity assumption absent from the stated theorem.

Finite-group integral projector lifting is already useful and checked, but further finite-group lifting does not discharge either implication for all supplied strictly compatible carriers in 9.2.

## Claim 11.1: residual-system completion criterion

The exact source conclusion is existence of a strictly compatible arithmetic system under exhaustive residual roots, a common spine, residual companion existence, finite-depth nonemptiness/branching/closure, and compatible horizontal transports. Its additional carrier clause promises finite-Frobenius recovery at every coefficient prime.

The proof explicitly cites 8.2 for existence and 9.2 for recovery. `CompletionAssembly.conditional_common_spine_completion` supplies continuous coefficient-field representations, common polynomials at supplied samples, and a supplied `Local` predicate from its supplied stability implication. Thus finishing the exact arithmetic interpretation of 8.2 would immediately settle the main existence part, without an unconditional closure theorem. It would not by itself settle the whole 11.1 claim, because the recovery clause still imports 9.1 and 9.2.

The source also does not restate all the constituent/decomposition hypotheses of 9.2 in the final phrase “known compatible carrier.” A faithful final formal statement should explicitly refer to the previously defined compatible-carrier hypotheses, rather than silently dropping them or inventing a stronger theorem. This is a dependency-explication issue, not evidence of a counterexample.

## Claim 11.2: exact location of the remaining existence problem

This source item is a **corollary describing the boundary**, not a new theorem constructing arbitrary global arithmetic packets. It lists residual nonemptiness for every coefficient prime, nonemptiness at every higher precision, and positive trace for every required global packet. It says reconstruction cannot create a missing root, repair an empty level, or force occupancy; finite branching and nonempty levels give a branch, and assumed closure reconstructs the admissible object.

The exact existing theorem `IndexedExistenceBoundary.all_required_packets_iff` is:

`(exists rho, SystemRealizes rho and continuous/local rho and every supplied packet Occupied)`

if and only if

`(every residual level nonempty) and (every level of depth >= 2 nonempty) and (every supplied packet's actual joint-projector trace nonzero)`.

The index of packets is arbitrary and may be infinite; each packet has a finite list of split commuting operators on a finite-dimensional characteristic-zero carrier. `JointOccupancy` already converts trace nonzero into the unique positive natural dimension, so no ordering on an arbitrary coefficient field is assumed. The proof neither chooses a carrier nor proves universal positive occupancy.

Two scope facts matter:

* Section 10 already specifies a finite packet as actual commuting split operators with targets. At that **finite linear-algebra level**, no further mysterious packet theorem is required; the quantified boundary is fully checked.
* The formal left side of `all_required_packets_iff` is `SystemRealizes` (every chosen finite condition) plus a generic `Local` predicate and independent occupancy assertions. It contains no common algebraic Frobenius equation and no type or theorem identifying the manuscript's intended arithmetic systems and required arithmetic packets with those supplied data.

Consequently, a thin new wrapper around this theorem would not produce a new full arithmetic result. If 8.2's arithmetic interpretation is completed, the exact remaining 11.2 route is short: instantiate these finite conditions with that interpretation, instantiate each required packet with its actual Section 10 carrier and operators, and prove that the chosen packet index ranges over exactly all the required packets. The existing theorem then closes the corollary. No new Chebotarev or Hodge–Tate theorem is independently needed by its logical proof, but the meaning of the arithmetic completion side is inherited from 8.2.

Changing the status description to “checked abstract boundary corollary” would accurately describe the theorem already present. Counting that as a newly completed **full arithmetic** claim would change the current ledger target and should not be presented as a proof advance.

## Recommended executable decision

Keep the root effort on 8.2. First specify its actual arithmetic source and target types, and determine whether the source's existing inverse-limit closure assumption has exactly the type needed to transfer from all finite conditions to those target properties. If that transfer is source-faithful, use `ClassCommonSpine.unframed_common_spine_completion` or `CompletionAssembly.conditional_common_spine_completion` and discharge their concrete arithmetic input fields. Do not add existence of a realization bijection or a stronger comparison certificate under the name of mere closure.

If that succeeds, assess 11.2 immediately: it should be the shortest follow-on complete claim. If it cannot be done because the manuscript does not define the intended packet reduction/attachment sufficiently, record that exact definition gap rather than substituting another fixed quadratic special case for the universal theorem.

## Evidence hashes

All paths below are relative to `/root/.codex/tmp/paperx_block22`.

| Source | SHA256 |
|---|---|
| `source/Projector_Resolved_Seed_Calculus_X_Block22_Amended.tex` | `c963d3926a10af5f574097084e760595d7c25f21767ed814970d614b8485181c` |
| `lean/PaperX/IndexedExistenceBoundary.lean` | `3fd7a505893def0c1086da57ec2354b6dd007b7a614a16a282b96600eda8da1d` |
| `lean/PaperX/CompletionAssembly.lean` | `1900d2142d60552da6d0e8816a83eac1b4240133ea2e311ffcfa6f0e650b293c` |
| `lean/PaperX/SystemCompletion.lean` | `adcf49fb8257342b8f4064e2fc1e17681d51bf551f43d6643bf94d7c1d782406` |
| `lean/PaperX/ProfiniteSeparation.lean` | `c23660150cd7a55a7da46770967d33dd9e3c068ced194f78e928be0f00b7ee1b` |
| `lean/PaperX/GeneralCharacters.lean` | `ed31851177b1a85ea5d836ccf9b2a06a8968cb7c31d77dbea897fb39a28fd7ea` |
| `lean/PaperX/CarrierCompatibility.lean` | `5686a56df2526bb551b863f4585cbe03b60f3d4c851d5c5ce65fbd67bdccaac1` |
| `lean/PaperX/CarrierSummands.lean` | `33a3afc42de1a2c03016cb347c2cf3fd159babdf3983b7c56ed89a95595cc338` |
| `lean/PaperX/JointOccupancy.lean` | `c088ab5e1eedd2b3395d5592f831ab82d8ec8d0521dbd38210e771ee80cf57d4` |
| `lean/PaperX/TraceRecovery.lean` | `d62a7b0966d53bb7331ead3ca41e8b6ba74d5882cc39997a85ebd6ef2e7f73ff` |
