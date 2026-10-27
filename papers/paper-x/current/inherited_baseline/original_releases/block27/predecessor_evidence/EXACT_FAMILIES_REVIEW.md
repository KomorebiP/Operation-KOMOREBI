# Independent review of the Block 19 exact computation

Verdict: **PASS — implementation and finite assertion verified in the stated range.**

This review concerns `checks/exact_families.py`, its imported arithmetic in
`checks/exact_summands.py`, and `exact_families_contract.json`. It is separate
from the Lean proof audit. The experiment author did not perform this review.

## Contract and scope

The experiment starts from specified integral finite-group carriers and
complete labeled projector families modulo `p^(e+k)`, where
`e = v_p(|Gamma|)`. It averages each matrix once, corrects successively in the
remaining complement using `3X^2 - 2X^3`, and supplies the last projector by
subtraction from the identity. All output equations are checked modulo `p^9`
and all input labels must agree modulo `p^k`.

For each pair of independently perturbed inputs, the output families are
compared by `U = sum_i F_i E_i`. Gaussian elimination constructs a two-sided
inverse modulo `p^9`, then every labeled conjugacy equation, commutation with
the carrier, and congruence of `U` to the identity modulo `p^k` is checked.

The script uses exact integers, reduced rational fractions, and finite rings.
There is no floating point tolerance and no random sampling. Higher-rank
families are deterministically constructed examples, not an exhaustive
classification. Newton correction at finite precision does not establish
convergence or a universal theorem over complete DVRs. No arithmetic packet,
Weil–Deligne attachment, or Hodge–Tate assertion follows from these tests.

## Implementation review

- Row-major storage and column-vector actions agree throughout multiplication,
  conjugation, averaging and vector decomposition. The imported optimized
  rank-two multiplication agrees with its ordinary formula.
- The integral group matrices are checked for identity, distinctness, closure,
  and two-sided inverses. The S3 examples are noncommutative and the other
  selected carriers are commutative, as expected.
- Exact averaging uses the matching inverse matrix for each group element.
  Rational congruence requires a denominator prime to `p` and numerator
  divisibility by `p^k`. Conversion to a quotient uses the modular inverse of
  the denominator. Nonintegral averages are rejected.
- The corner algorithm checks the remaining complement is idempotent, verifies
  support on both sides, preserves retained precision, checks the exact defect
  factorization, and checks doubling at every iteration. Both orders of every
  pairwise projector product are tested. The last label is tested by the same
  complete-family assertions as all other labels.
- The canonical conjugator is tested directly, rather than accepted solely from
  the matrix formula. Gaussian inversion uses only unit pivots and verifies
  both products with its candidate inverse. Labeled intertwiners and conjugacies
  are separate checks.
- Modular traces are used only as benchmark invariants, not as proofs of rank.
  All constructed output projectors are explicitly nonzero modulo `p`.
- The exhaustive small-case loop checks all 16 matrices over F2 and accepts
  exactly eight idempotents. Every vector modulo 4 is reconstructed from its
  labeled pieces for each accepted pair.
- Adverse examples correctly distinguish idempotence, orthogonality, and
  completeness. The positive-depth failure gives a zero canonical conjugator
  after exchanging the labels. The precision-loss obstruction checks both
  possible lifts of the prescribed off-diagonal entry modulo 8.
- Case order is deterministic. There is no silent truncation, caching, early
  success, or inferred completion after timeout. JSON is round-trip checked.

## Reproduction and independent checks

The final source was replayed into a fresh directory through the computation
audit skill's bounded runner. The run used Python 3.12.13 on Linux x86_64,
completed with exit status 0 in 2.454701 seconds, and retained both source
hashes. Its manifest is `checks/families_independent_run/manifest.json`.
The complete scientific result is byte-for-byte identical to the author's
result. The original, independent replay, and supplemental reviewer manifests
all passed `validate_manifest.py --root`.

Reproduction command, from this project root:

```bash
python3 checks/exact_families.py --output NEW_DIRECTORY/exact_families.json
```

The complete bounded argv, input hashes before and after, output hashes,
environment and limits are recorded in the manifests. The independent replay
used a 240-second wall limit, 200-second CPU limit, 1 GiB address-space limit,
and one CPU. No limit was reached. Repository commit metadata is unavailable
for this copied project, so exact source hashes provide revision identity.

The reviewer also wrote `checks/review_families.py`, which uses a separate
list-of-rows matrix multiplication to check 30 deterministic rational matrix
products in dimensions 0, 1, 2, 3, 4 and 8. It independently enumerates the
16 matrices over F2, verifies the eight idempotents, verifies the polynomial
defect identity as exact coefficient lists, checks the one-digit obstruction,
and verifies the complete case list and counting formulas. Its run completed
with exit status 0 in 0.071179 seconds. Its manifest and result are
`checks/families_review_run/manifest.json` and
`checks/families_review_run/review.json`.

| Quantity | Verified result |
|---|---:|
| Constructed parameter cases | 49 |
| Constructed family lifts | 98 |
| Constructed labeled projectors | 370 |
| Exact averages, all non-idempotent before correction | 370 |
| Rigidity comparisons | 49 |
| Distinct output pairs and nonidentity canonical conjugators | 46 |
| Noncommutative family lifts | 36 |
| Constructed variants losing full input precision | 53 |
| Exhaustive rank-two pairs over F2 | 8 |
| Independently enumerated vector decompositions modulo 4 | 128 |
| Constructed Newton iterations | 826 |
| Total Newton iterations, including small and adverse cases | 866 |
| Empty and singleton edge cases | 2 |

The 49 parameter cases consist of 18 C2, 9 Klein-four, 18 S3, and 4 C4 cases,
with maximum ambient rank 8, at most 5 labels, primes 2, 3 and 5, retained
depths 1–3, and group-order valuations 0–2. The 53 precision losses are
observations about these corrections; necessity is established only for the
separate explicit adverse example.

## Pinned evidence

| Artifact | SHA-256 |
|---|---|
| `checks/exact_families.py` | `3068edcc87c674c1fb19f1289b0216a56f6098bd067c67202614ad035b545316` |
| `checks/exact_summands.py` | `71f1ebc2782ff9c7aef8114a2a07a835434a790ed6e4a76b6d10baf0baa31848` |
| Both full experiment results | `b912de56632cee168a0ac438b6a6b8afd2d04d7a31681631b05625f2587b836c` |
| Supplemental independent review result | `4cda80398a9649ade2117172fb6860cab41793f559199ad5b2a9f3214fe426a5` |

No implementation inconsistency or failed benchmark was found. Shared
arithmetic remains a limit of the production experiment; the supplementary
independent products, F2 enumeration and coefficient identity reduce that
specific risk. Universal results remain the responsibility of the separate
Lean proofs.
