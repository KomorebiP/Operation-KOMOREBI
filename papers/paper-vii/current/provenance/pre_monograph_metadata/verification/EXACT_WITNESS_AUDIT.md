# Exact rational finite witnesses

The independent script `scripts/exact_rational_witnesses.py` verifies 269 named
finite assertions using Python standard-library `fractions.Fraction`. The
run passed 269/269 assertions on CPython 3.12.14. The JSON output is
`exact_rational_witnesses.json`. A second invocation writing to a temporary
path produced byte-identical JSON under the same interpreter.

These are new, explicitly scoped finite examples. They are neither a rerun of
the recovered numerical verifier nor Lean proof checking. They do not upgrade
the status of a manuscript theorem or a formal-development block.

## Contract and reproduction

From the edition workspace root, run:

```sh
python3 verification/scripts/exact_rational_witnesses.py --out verification/exact_rational_witnesses.json
```

From the containing scratch workspace, the equivalent actual invocation was:

```sh
python3 paper_vii_work/verification/scripts/exact_rational_witnesses.py --out paper_vii_work/verification/exact_rational_witnesses.json
```

`--out` is required, and the script does not depend on its working directory,
the source manuscript, or an external package. Fractions are serialized as
exact rational strings, including integers. The JSON records every named
assertion, each input family and arithmetic convention, representative exact
matrices and certificates, explicit bounds, and nonclaims. JSON round-trip
equality is checked before writing. The parent computation manifest records
the command, execution provenance, and file hashes; this audit is not a
standalone manifest.

A successful exit means that every assertion in this fixed input family
passed. A failed assertion aborts the run before a new result is written. If a
prior JSON exists after a failed run, it must not be mistaken for current
evidence. The parent manifest's exit status and output hashes are the run
record. There is no sampling, seed, floating arithmetic, numerical tolerance,
search truncation, or indefinite loop. The largest rank array is 18 by 16;
the largest square operator matrix used in the channel/Schur calculations is
4 by 4. Seed Hilbert spaces have dimension at most 16.

## What is checked

| Family | Exact inputs | Finite assertion |
|---|---|---|
| Projector compression | `u=(3/5,4/5)`, `w=(-4/5,3/5)`, `P=uu^T`, `Q=ww^T`, `H=diag(1,-1)` | Complete orthogonal rank-one packets; `PHP=(-7/25)P`; `(PHP)^T(PHP)=(49/625)P`; `(QHP)^T(QHP)=(576/625)P`; `[H,P]^T[H,P]=(576/625)I`. |
| Involution propagation | The same `H`, with `(c,s)=(1,0),(0,1),(3/5,4/5),(5/13,12/13),(3/5,-4/5)` | `H^2=I`; the real and imaginary parts of `U=cI-isH` obey exact unitarity identities; the leakage norm squared is `s^2(576/625)`. |
| Single-summand seeds | All 16 pairs `1<=d,m<=4`; canonical grouped coordinate seeds for `M_d tensor I_m` | Explicit orbit rank is `dm`; each individual orbit rank is `d` times its coefficient rank; stacked row spaces have rank `m`; the numerical capacity inequality `(k-1)d<m<=kd` holds for `k=ceil(m/d)`. |
| Direct-sum seeds | `(M_2 tensor I_3) direct_sum (M_1 tensor I_2)` | Two explicit seeds generate a hull of dimension 8 under the declared direct-sum algebra. |
| Rational amplitude damping | `(a,b)=(1,0),(0,1),(4/5,3/5),(3/5,4/5),(5/13,12/13)`; `K_0=diag(1,a)`, `K_1=[[0,b],[0,0]]` | Kraus completeness; independently assembled Choi matrix equals the sum of rational Kraus-vector outer products; all 15 principal minors are nonnegative; output partial trace is identity; involution covariance; trace preservation on all four matrix units; a rational density example. |
| Schur/Feshbach, 2 by 2 | `H=[[1,2],[2,4]]`, retained dimension 1, hidden block `D=4`; `z=-1,0,1,2,3,5,6` | Exact block elimination and determinant factorization at all seven parameters; projected resolvent at five invertible parameters; kernel lifting at eigenvalues 0 and 5. |
| Schur/Feshbach, 3 by 3 | `H=vv^T`, `v=(1,2,3)`, retained dimension 2, hidden block `D=9`; `z=-1,0,1,2,5,10,14` | Exact block elimination and determinant factorization at all seven parameters; projected resolvent at five invertible parameters; kernel lifting at eigenvalues 0 (multiplicity 2) and 14 (multiplicity 1). |

The exact projector norm certificates give compression norm `7/25` and
off-block/commutator norm `24/25`. These values follow from the displayed
rank-one Gram identities and the exact identities for orthogonal projections;
no eigenvalue approximation is involved. The propagator checks correspond to
rational sine/cosine pairs. They do not select or approximate a real time,
evaluate a transcendental exponential, or check the inequality
`|sin(t)|<=|t|`.

For the channels, the Choi convention is output tensor input, as in the source
manuscript. The index is `output*2+input`; `vec(K)` is row-major. The Gram
factorization is therefore an exact positivity certificate over the complex
extension as well: `v* J v=sum_r |vec(K_r)*v|^2`. Checking all principal
minors supplies a second positivity characterization for these real symmetric
matrices. The rational damping probabilities are `0,1,9/25,16/25,144/169`.
These channels are unital exactly in the zero-damping case within this list.
The tested covariance operator is the rational involution `diag(1,-1)`.

For the Feshbach examples, `F(z)=z-A-B(z-D)^{-1}B^T`; no tested `z` lies in the
hidden spectrum. The lower component of a lifted vector is
`(z-D)^{-1}B^T x`, with the positive sign dictated by the lower block equation.
The exact lifts at `z=0` are `(1,-1/2)` for the 2 by 2 example and
`(1,0,-1/3),(0,1,-2/3)` for the 3 by 3 example. The latter tests a retained
kernel of dimension two. For invertible parameters, both products with the
computed full inverse are identity and its retained block equals `F(z)^{-1}`.
As hand algebra checks, the 2 by 2 family has
`F(z)=z(z-5)/(z-4)` and full determinant `z(z-5)`. In the 3 by 3 family,
`F(z)=zI-[z/(z-9)] [[1,2],[2,4]]` and the full determinant is
`z^2(z-14)`. The multiplicities in the recorded kernel checks agree with these
factorizations.

## Implementation audit

All matrices enter through `Fraction`; all matrix products, elimination,
inverses, determinants, and comparisons remain exact. Transposition implements
the adjoint because every input matrix is real. Complex propagation is handled
through two rational matrices for its real and imaginary parts, with both
unitarity conditions checked. No `float`, `complex`, NumPy, or symbolic-library
conversion is used.

Elimination computes ranks, inverses, and explicit nullspace bases. Cofactor
expansion computes determinants independently of elimination. Hand benchmarks
include the dependent rows `[[1,2],[2,4]]`, its nullspace `(-2,1)`, the inverse
of `[[2,1],[1,1]]`, and rejection of a singular inverse. Matrix dimensions and
basis ordering are fixed explicitly. The Choi construction applies the channel
to matrix units, whereas its independent Gram construction uses flattened
Kraus matrices; their equality tests the tensor indexing. The Feshbach block
elimination identity is checked separately from inversion and from kernel
lifting. Lifted vectors have full kernel rank and project back to the retained
kernel basis.

Three negative controls are counted as successful rejection checks: perturbing
the projector's `(0,0)` entry destroys idempotence; an over-normalized Kraus
pair fails completeness; and reversing the Feshbach lift sign fails the full
kernel equation. They detect those named failure modes, not arbitrary bugs.
The assertion count is the number of logical checks, not the number of matrix
entries, rational operations, cases, theorems, or proofs.

The source interpretation was checked against the local strengthened
manuscript: `thm:orbit_dimension`, `thm:quantum_seed_rank`,
`lem:off_diagonal_norm`, `thm:fixed_leakage`, `fact:kraus_choi`,
`thm:choi_covariance`, `thm:feshbach_resolvent`, and
`thm:feshbach_spectrum`. The script does not import or execute recovered
verification code and does not modify the raw source.

## Interpretation and limits

The implementation and its finite assertion are verified in the stated range.
The exact certificates expose structural mechanisms used in the written
proofs: row-space generation, Kraus Gram positivity, Schur elimination, and
kernel lifting. The selected examples do not prove these mechanisms uniformly.
In particular, testing the seed capacity inequality is not an independent
proof that arbitrary coefficient row spaces obey the required dimension bound.

No Lean source is compiled or checked. There is no exhaustion of rational
matrices, complex matrices, channel families, or Hamiltonians. No moving-packet
leakage, upper-half-plane self-energy, positive-definite memory kernel,
continuum limit, unbounded-operator claim, QEC theorem, or recovered numerical
residual is certified here. Formal checking, manuscript proof auditing, and
floating numerical reproduction remain separately scoped evidence streams.

Residual risks are ordinary finite-code risks: the same matrix primitives are
reused across cases, and neither successful examples nor negative controls
constitute a formal audit of every possible code path. The independent
determinant method, hand benchmarks, Gram construction, two-sided inverse
checks, and explicit lift residuals reduce the specific indexing and sign risks
that matter to these examples.
