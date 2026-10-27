The N=4 dyadic difference bound now holds at every row. For each address
`j < 4` and all natural numbers `u`, `k`, and `n`, the checked theorem proves

\[
2^k\mid\Delta_u^k C_{4,j}(n)
\]

inside the actual integral lift in \(\mathbb Z_2\). It also proves the corresponding
zero-safe rational valuation statement and the same divisibility for the original
unnormalized coefficients \(E_{4n}^{(4,j)}=j!C_{4,j}(n)\). In particular, `n = 0`
and difference orders larger than the row are included. The earlier interface
exposed only the exponent \(\min(k,n)\).

The proof uses the charged differential operator
\[
A_c=\frac{D^4-c}{2}.
\]
The fourth-order Leibniz formula gives
\[
A_{c+d}(fg)=A_c(f)g+fA_d(g)
+2D(f)D^3(g)+3D^2(f)D^2(g)+2D^3(f)D(g).
\]
The correction coefficients are integers. Induction on the number of operator
iterations proves integral closure under products with additive charges and
under actual reciprocals with negated charges. A second induction shows that
shifting a charge by 2 preserves this property, using
\(A_{c+2}=A_c-1\).

The previously checked `source_kummer` theorem supplies flatness with charge 1 for
each explicit dyadic source at every row. Actual reciprocal integrality follows
from its constant coefficient 1. Inversion gives charge -1, and shifting by 2
returns charge 1. The power-series identification with the original normalized
Euler packet then extracts the unshifted difference at degree \(4n\). This
extraction contains no subtraction of degrees and needs no lower bound on `n`.

`ChargedDworkClosure.lean` contains the general algebraic proof, and
`DyadicFourAllRows.lean` supplies the actual source, reciprocal, coefficient, and
rational bridges. Its public conclusions are `base_step_bound`,
`normalized_bound`, `normalized_precision`, `unnormalized_bound`, and
`unnormalized_precision`, in namespace `KomorebiPaperIX.DyadicFourAllRows`.

The frozen production sources contain 36 theorems, 5 definitions, and 1
abbreviation. Fresh replay passed with Lean 4.34.0-rc2 and warnings treated as
errors. All 42 declarations were individually audited; their only axioms are
`propext`, `Classical.choice`, and `Quot.sound`. Three positive statement controls
passed. Two negative controls failed as intended: the old row-capped theorem
cannot establish the new all-row statement, and the result does not permit
address `j = 4`. These controls verify the interface boundary; they are not
mathematical counterexamples to every possible statement beyond that boundary.

`replay_01/all_rows_audit.json` records the source hashes and checks. Reproduce
with the included script, supplying the matching baseline project and its
compiled imports:

```sh
python3 verify_all_rows.py \
  --kit /absolute/path/to/portable-runtime \
  --baseline /absolute/path/to/Nishibuchi-completion \
  --baseline-build /absolute/path/to/checked-baseline-build \
  --output /absolute/path/to/new-audit-directory
```

This is a proved strengthening for the generalized N=4 packets. It is distinct
from the classical N=2 sharp dyadic reconstruction tail and requires no transfer
of that tail's coefficient formulas.
