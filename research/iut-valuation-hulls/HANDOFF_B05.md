# B05 continuation handoff

**Accepted checkpoint:** B05; 28 Lean modules + one entry point, 5 new modules,
3 negative controls rejected. `verification/b05/verification.json` is the
current verification record. The user has expressed an interest in actually
bridging Komorebi to Mochizuki's Hodge theaters, not merely analogy.

## Confirmed results

* Local unit saturation iff identical valuation level.
* Local nonzero O-multiplier saturation iff reachable at equal/deeper valuation.
* Strictly shallower pilot excluded from both closures.
* Minimal exponent cost to adjoin a pilot = `a-min(a,b)`; sharp.
* For weights s>=1 and depth m, exact total cost `m Σ(s-1)`.
* F17 marked reduct plus 1+1 anchor does not determine 1+2; verified field laws.
* A discrete approximate witness transfers the scalar upper bound with exact
  additive loss; witnesses must match the same branch and normalization.

## Source-required obligations, unchanged

Neither the original theta prime-strips and Kummer maps, nor the actual
holomorphic hull/determinant/procession normalization, have been instantiated.
`IUT312.SourceWitnessTheorem` has no genuine IUT proof term. The existing
finite countermodel is not a counterexample to IUT. No abc proof or refutation.

## Decisive next mathematical task

Use the original IUT III Remark 3.9.5(vii) (Ob1–Ob9), Theorem 3.11,
Remark 3.11.1, and Corollary 3.12 Step (xi-c)–(xi-f). Build a theorem about the
*actual* source-defined possible regions `Pβ` and the construction `φ(P_B)`.
Show precisely how the local unit or log-link indeterminacy acts on that hull,
and compute the output normalized log-volume before invoking the fixed q-pilot.
Then prove the q-pilot scalar is attained, approximated cofinally, or reached
with a controlled loss **in the same branch**. A source-backed IPL/SHE/APT
certificate must not be treated as a scalar witness by itself.

This source-instantiation task is the actual research frontier. If it cannot be
closed, record the exact missed compatibility and never claim that the small
algebraic models settle the original IUT proof.

## Verification caveat

The legacy sequential B03 verification attempt timed out while individually
checking files after successfully completing its clean Lake build. A complete
B05 parallel per-file audit then ran to completion with all source, compiler,
contract, and negative-control checks passing. See logs. The first aborted
F17 brute-force draft was replaced by generic algebraic transport lemmas.
