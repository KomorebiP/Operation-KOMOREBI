# Next research block after accepted WR03–WR05

This is a restart contract, not evidence that the next claims are formalized.

## Recommended next target: the full WR08 regularization alternative

Use the current monograph's `source/chapters/05h_regularized_repair.tex` as the raw target. Freeze its exact statement before editing or delegating. Work in the same real Hilbert spaces and with the same bounded linear map and actual correction norm as WR06–WR08.

As the positive real parameter tends to zero, prove all of:

1. Fitted images tend to the orthogonal projection of the datum onto the closure of the operator range.
2. Residual norms tend to the orthogonal residual floor.
3. The weighted penalty tends to zero.
4. When that projected datum lies in the actual range, corrections converge in norm to its unique minimum-norm preimage.
5. Otherwise correction norms tend to infinity, rather than merely being unbounded.

The first route should compare the regularized minimum with one fixed approximating correction, chosen before the parameter. For the attained branch, compare with the minimum-norm exact preimage to obtain a uniform norm bound; a vanishing weighted penalty is not such a bound. The escaped branch can reuse the accepted same-budget realization/escape theorem from WR01. Any sequential proof must explicitly close the implication to the full positive real-parameter limit.

The difficult implication is strong convergence in the attained branch. Preserve unsuccessful approaches and their precise blockers. Do not silently replace the full Hilbert theorem with a finite-dimensional, closed-range, separable, sequence-only, or rate theorem.

## Follow-on claims

| Claim | Remaining scope |
| --- | --- |
| WR09 | Complete the parameter-choice convergence consequence; re-audit every additional printed clause before promoting the group. Accepted pointwise sensitivity bounds remain useful dependencies. |
| WR16 | Combine the exact regularization limit with data and inexactness allowances to prove the full stopping-rule limit. The pointwise estimate alone is insufficient. |
| WR10 | Infinite diagonal model, membership/optimizer identity, energy and residual bounds, and certified tail estimates. |
| WR11 | Both sum asymptotics and the exact infinite-problem budget limit, including passage between sampled optimal budgets and all large real budgets. |
| WR12 | The explicit noisy attainable example, parameter rounding, and stated rate with constants. |
| WR15 | Coordinate-covector norm and its invariance under every invertible basis change in the stated finite-dimensional setting. |

## Separate gaps that this budget block does not close

- An independent referee audit of the entire monograph. The fresh audit here covers WR03–WR05 and their necessary printed background.
- A refinement proof connecting executable numerical certificate code to these mathematical declarations.
- Application-specific verification that a proposed model has the stated operator, norm, and protection kernel.
- New synchronized editions of the historical visual and Lean companion guides.

## Restart discipline

Start from the delivered `PROGRESS_LEDGER.json` and accepted run receipt. Check the four budget source hashes before reusing this block. Keep the original target and numbered attempts, assign disjoint file ownership, and require a fresh exact-type review plus integrated compiler/axiom/control evidence before changing coverage labels. Use only the theory and modest exact examples needed for those obligations; no large training experiment is part of this program.
