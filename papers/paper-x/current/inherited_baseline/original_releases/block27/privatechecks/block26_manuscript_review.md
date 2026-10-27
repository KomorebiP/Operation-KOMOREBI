# Block 26 manuscript comparison and proofreading

Status: passed, review-only. No manuscript or Lean source was edited in this
assignment. No objective mathematical-scope, LaTeX, or language defect was
found in the changed passage and surrounding definitions reviewed below.

## Exact reviewed revision

- Manuscript: `source/Projector_Resolved_Seed_Calculus_X_Block26_Amended.tex`
- Manuscript SHA256:
  `ff7337e3b9acb01cb3677e49a7d995135c9bc9a5985ef701539a5e5c90648ab2`
- Patch: `source/Block26_Amendments.patch`
- Patch SHA256:
  `b628c336025b1763a96aba777538d1590d1b92d39d34927d196edb24bcfbd164`

The reviewer did not author the manuscript, the absolute-integral Frobenius
construction, the integral Frobenius recognition module, or the final
arithmetic separator. This reviewer authored `CyclotomicInertiaBridge.lean`;
that component is therefore a self-review, not an independent proof audit.
The present assignment compares the manuscript's scope with the nine final
module statements and relevant proof bodies. It does not substitute for the
separately recorded independent proof audit or cumulative compiler run.

## Coverage

The review covers all changed hunks of `Block26_Amendments.patch`, the
preamble/macros, the neighboring original Finite Frobenius separation theorem
and proof, the Block 25 system-equivalence and good-place conventions, and the
surrounding arithmetic coverage and formalization-boundary paragraphs.

| Manuscript assertion | Final Lean evidence and scope checked |
|---|---|
| Actual continuous, surjective restriction with open kernel | `AbsoluteGaloisRestriction.restriction_commutes`, `restriction_surjective`, `restriction_continuous`, and `restriction_kernel_isOpen`; `CyclotomicAbsoluteSamples.restrictionMap` derives normality from the cyclotomic hypothesis. |
| Preservation and reflection of equivariant isomorphisms, invariant subspaces and irreducibility | `SurjectiveRepresentationPullback.nonempty_equiv_iff`, `subrepresentationOrderIso`, `isIrreducible_iff`, and `memberwiseEquiv_iff`. Surjectivity is retained; no finite acting group is required. |
| Every rational prime has an actual integral-closure prime and absolute Frobenius witness | `AbsoluteIntegralFrobenius.exists_frobenius`, assembled from `exists_frobenius_at`, the actual invariant-ring action, proved discrete-action continuity, residue characteristic, and `residue_perfect`. The element stabilizes the actual prime ideal and has the stated p-power residue action. |
| Root reduction and cyclotomic Frobenius recognition | `CyclotomicIntegralFrobenius.map_injective_on_roots`, `order_nonzero_in_quotient`, and `restriction_eq_primePower_of_residue`. The geometric-sum factor reduces to a nonzero element. Coprimality supplies the required nonvanishing. |
| Unramified pulled-back representations | `CyclotomicIntegralFrobenius.restriction_eq_one_of_inertia` and `pullback_trivial_on_inertia` concern the actual ideal inertia subgroup. The manuscript says that the representations are unramified; it does not say that Qbar/Q is unramified. |
| Separate valuation formulation | `CyclotomicInertiaBridge` uses the valuation-subring stabilizer and its residue-action kernel. The valuation and its residue characteristic, and any valuation-decomposition Frobenius element used for recognition, remain supplied. |
| Common trace separator at genuine arithmetic witnesses | `CyclotomicAbsoluteArithmeticSeparation.finite_arithmetic_system_separator` supplies the primes, integral-closure prime ideals, and stabilizing p-power Frobenius elements. It retains the common finite cyclotomic factorization, cofinite good-place conditions, compatibility, finite-dimensional characteristic-zero members, and componentwise system nonisomorphism. |
| Trace identities at any global lift | `CyclotomicAbsoluteSamples.pullback_on_lift` and `pullback_character_on_lift`; `CyclotomicAbsoluteSeparation.finite_absolute_system_separator` retains each coefficient member's good-prime premise. |
| Necessary boundaries | `SurjectivePullbackBoundary` proves failure without surjectivity and failure of full-group coverage despite projected quotient coverage. `CyclotomicInertiaBridge` proves the actual Z2 root-reduction counterexample and nonunit root order. |

The exact hashes of all nine reviewed Lean modules are recorded in
`privatechecks/block26_manuscript_review_checks.json`.

## Meaning and notation checks

- Arithmetic Frobenius consistently means the p-power residue action. No
  inverse Frobenius convention is silently substituted.
- The ideal-stabilizer construction and valuation-stabilizer formulation are
  explicitly separate. Their identification is neither assumed nor asserted.
- Arbitrary selected global lifts are not described as decomposition-group
  elements. The actual arithmetic witnesses are obtained by a distinct proved
  existence theorem, then identified after restriction.
- The final separator has one fixed cyclotomic quotient. The manuscript does
  not promote this to coverage in every finite quotient of the absolute
  Galois group or to general Chebotarev coverage.
- The system equivalence is the componentwise representation-isomorphism
  relation defined in the adjacent Block 25 paragraph. Optional arithmetic
  labels are not used in place of that equivalence.
- The row index j and constituent index i agree with `sampleMatrix t v`.
  The algebraic trace matrix has a nonzero determinant; ordinary member-trace
  equalities retain the individual member's good-place condition.
- Prime existence is existential. No algorithm to compute the selected prime,
  or effective upper bound on it, is claimed.
- The manuscript's 17 checked / 3 partial status is retained. Claims 9.1, 9.2,
  and 11.1 remain partial; no new Hodge--Tate, Weil--Deligne attachment, or
  universal occupancy result is asserted.

## Validation actually performed

1. `git apply --check` passed in a fresh temporary directory containing the
   exact Block 25 predecessor manuscript.
2. Applying the patch there reproduced the delivered Block 26 manuscript
   byte for byte.
3. The original Finite Frobenius separation theorem and its proof are byte
   identical to Block 25. Their unchanged segment SHA256 is
   `6db3e6ea5ba2c0096666260e69eb8bad982b49cd83918f6c314212e3a8c0dc33`.
4. The new Block 26 passage has five balanced display pairs, 72 dollar math
   delimiters, and balanced unescaped braces. Its control-sequence names were
   checked against standard LaTeX/math commands and the supplied preamble.
   No new label, citation key, or reference target is introduced by that
   passage.
5. Every changed sentence and display was read in its neighboring context.

Routine edits: none. Mathematical-token changes: none. Unresolved objective
issues in the reviewed scope: none.

No TeX/PDF typesetting or visual certification was performed. No Lean module
was recompiled as part of this editorial assignment; module compilation and
axiom evidence belong to the production and independent proof-audit records.
