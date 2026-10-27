# Block 19 exact finite computation audit

Outcome: **the implementation and finite assertions pass in the stated range**. The general theorem and convergence over a complete DVR require the separate Lean proofs. This report describes the finite computation only.

## Contract

For an actual integral representation of a finite group, write `e = v_p(|G|)`. The inputs are complete labeled orthogonal equivariant projector families modulo `p^(e+k)`, where `k > 0`. The script averages each matrix once over the rational numbers, checks that the result is p-integral and preserves the input modulo `p^k`, and then performs corner-supported Newton correction in `Z/(p^9)`.

At each step, `C = I - sum(previous output projectors)` is the remaining complement. The next average is compressed to `C A C`, and the cubic `f(A) = 3A^2 - 2A^3` is iterated. The final output label is the complement. Every endpoint is checked for all ordered orthogonality equations, idempotence, exact equivariance in the target finite ring, completeness, and the prescribed reduction modulo `p^k`. The number of labels does not enter the retained-depth parameter used by the algorithm.

For two output families with the same reductions, the script forms `U = sum_i F_i E_i`. It checks `U = I mod p^k`, both inverse equations, exact equivariance modulo the target modulus, `U E_i = F_i U`, and `U E_i U^(-1) = F_i` for every label.

All arithmetic uses Python integers and `fractions.Fraction`. Unit denominators are inverted exactly when reducing p-integral rational numbers. No floating point arithmetic, numerical tolerances, external algebra packages, or random sampling are used. Matrices act on column vectors.

## Range and counts

| Carrier | Nonzero labels | Prime | Retained depths k | Ambient ranks |
| --- | --- | --- | --- | --- |
| C2, diagonal sign characters in mixed integral bases | 3, 4, 5 | 2, 3 | 1, 2, 3 | 3, 4, 5 |
| Klein four, integral characters in mixed bases | 3, 4, 5 | 2 | 1, 2, 3 | 3, 4, 5 |
| S3, repeated sum-zero permutation lattice in mixed bases | 3, 4 | 2, 3, 5 | 1, 2, 3 | 6, 8 |
| C4, repeated rotation lattice in mixed bases | 3, 4 | 2 | 1, 2 | 6, 8 |

The full Cartesian products shown in the table give **49 parameter cases**. Each case uses two deterministic integral perturbations of the same quotient family, giving **98 constructed family lifts** and **370 nonzero labeled output projectors**. The input group-order valuations are **0, 1, and 2**. Every target quotient has depth **9**. Every exact average in these constructed cases is non-idempotent, so all **370 averages** genuinely require the idempotent-correction machinery or final-complement construction.

The S3 action is verified over the integers to be noncommutative. Its **36 constructed family lifts** have three or four nonzero labels, avoiding tests restricted to scalar projectors on an irreducible carrier. Mixed integral bases prevent the tests from assuming that the supplied action is already displayed in the output decomposition.

There are **49 explicit rigidity comparisons**. In **46**, the two output families are different and the canonical conjugator is not the identity in the target ring. The other three comparisons check the identity case. All canonical conjugators are invertible and give the prescribed labeled conjugacy.

The smaller exhaustive test examines **all sixteen 2 by 2 matrices over F2** for the trivial group. Exactly **eight** are idempotents, each defining a complete ordered pair `(E,I-E)`. All eight pairs lift successfully. An independent vector-level check enumerates all sixteen vectors modulo 4 for each output pair, for **128 vector checks** in total. It checks reconstruction and the action of each label on each projected component.

The empty family on the zero module and the singleton identity family also pass. There are **866 cubic Newton iterations** in total: **826** for the constructed families, **32** for the eight exhaustive pairs, and **8** for the precision-loss example. The empty and singleton cases require no cubic iteration.

These high-rank families are deterministic constructed inputs, not an exhaustive classification or uniformly distributed random sample. The seed families are exact orthogonal integral projectors, and every perturbed input is independently checked to satisfy the required equations at the input precision before correction. For the diagonal 2-adic cases, the seed shear is only equivariant at the stipulated quotient precision, which exercises actual loss of digits in averaging.

## Boundary results

1. **Independent idempotent lifts need not be orthogonal.** Start with the three coordinate projectors in rank three. Replace the first by `E_11 + 2 E_12`, leaving the other two unchanged. Every output is an exact integer idempotent with the correct reduction modulo 2, but the ordered product of the first and second is `2 E_12`, which is nonzero. Thus separately applying a single-projector theorem does not establish the family theorem.

2. **Completeness alone is insufficient.** The matrices `2I`, `-2I`, and `I` sum to `I`, but they do not form an idempotent family. The algorithm must preserve the projector and orthogonality conditions in addition to the sum.

3. **Positive retained depth matters for rigidity.** Swapping the two rank-one coordinate labels in rank two gives two complete orthogonal families for which `sum_i F_i E_i = 0`. Congruence modulo `p^0 = 1` is vacuous and does not imply that this canonical matrix is invertible.

4. **The original precision can be impossible to retain.** For the C2 carrier `diag(1,-1,1)`, the complete family

   `E_11 + 2E_12`, `E_22 - 2E_12`, `E_33`

   is equivariant modulo 4. Any equivariant matrix over the 2-adic integers must have zero `(1,2)` entry between these two distinct sign characters. More concretely, all possible lifts of its prescribed upper entry from modulo 4 to modulo 8 are **2 and 6**, and both fail the necessary relation `2a = 0 mod 8`. Hence there is no integral equivariant lift preserving this family modulo 4. The algorithm succeeds modulo 2 and produces the three coordinate projectors modulo 512. This is an obstruction to any lift retaining the stronger prescribed precision, rather than just a failure of the implemented algorithm.

Among the constructed tests, **53 of 98** output families do not retain the entire input depth `e+k`, while all retain the required depth `k`. That statistic describes the implemented outputs only. The preceding explicit C2 obstruction is the separate justification that such loss can be unavoidable.

## Implementation and provenance

Authoritative code: `checks/exact_families.py`. Its only project-local import is `checks/exact_summands.py`, whose elementary exact matrix helpers are pinned in the manifest. The new script does not call the predecessor's correction routines or sample generators.

The script checks each supplied carrier's group closure, identity, and inverse laws exactly over the integers. It checks both equations for every change of basis. At every cubic step it independently evaluates the factorization

`f(A)^2 - f(A) = (A^2-A)^2 (4(A^2-A)-3I)`.

It separately verifies defect precision doubling, retention of previous digits, corner support on both sides, and final family equations. The explicit inverse is obtained by unit-pivot modular Gaussian elimination and then checked by multiplication on both sides. Trace values are included as benchmarks, while no conclusion about module rank is drawn from trace alone. JSON output is checked for a serialization round trip.

These alternate checks share the same elementary matrix arithmetic routines. They are orthogonal invariant checks, not a wholly independent mathematical software implementation. Independent code review and any replay are recorded separately.

The main version-2 provenance record is `checks/families_run/manifest.json`. Its input and result hashes passed the computation-audit manifest validator. The deterministic result `exact_families.json` is byte-identical to `checks/families_run/exact_families.json`. The run contract is `exact_families_contract.json`.

The recorded run completed in **2.52833 seconds** with Python **3.12.13** on Linux x86-64. Enforced limits were 60 seconds wall time, 50 seconds CPU time, 512 MiB address space, one CPU core, and 1 MiB captured output. The one-thread environment setting is cooperative. No Git revision was available for this extracted project, so the source and result SHA-256 hashes identify the checked files.

- New script SHA-256: `3068edcc87c674c1fb19f1289b0216a56f6098bd067c67202614ad035b545316`.
- Imported helper SHA-256: `71f1ebc2782ff9c7aef8114a2a07a835434a790ed6e4a76b6d10baf0baa31848`.
- Deterministic result SHA-256: `b912de56632cee168a0ac438b6a6b8afd2d04d7a31681631b05625f2587b836c`.

Regenerate the deterministic result from the release root:

```text
python3 checks/exact_families.py
```

The complete command, bounds, pinned inputs, output identity, and execution status are in the version-2 manifest. The bounded runner requires a fresh directory for an additional provenance record.

## Interpretation

The tested mechanism is a single averaging loss bounded by `e`, followed by orthogonal correction in complementary corners retaining `k` digits, and a near-identity matrix giving labeled rigidity. The observed equations are structural identities that the separate Lean proofs must establish uniformly. These computations establish only the finite instances described here. They do not prove a complete-DVR limit, universal existence of arithmetic packets, a Weil–Deligne attachment, or a Hodge–Tate comparison. No full arithmetic claim is upgraded on the strength of this finite audit.
