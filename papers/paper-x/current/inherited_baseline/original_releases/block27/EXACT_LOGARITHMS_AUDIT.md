# Block 20 exact computation audit

All implemented finite assertions passed. The computation uses only Python
integers and `fractions.Fraction`. It supplies bounded checks of the proposed
algebraic statements; the general statements require their separate Lean proofs.

## Contract and scope

The precise parameters and conventions are recorded in
`exact_logarithms_contract.json`. The sole program input is
`checks/exact_logarithms.py`, which has no project or third-party imports.
Column vectors are used. A Jordan block has ones on its superdiagonal, so
`N e_j = e_(j-1)` for positive `j`. The program evaluates

\[
\exp(N)=\sum_{j=0}^{d-1}\frac{N^j}{j!},\qquad
\log(I+X)=\sum_{j=1}^{d-1}\frac{(-1)^{j+1}X^j}{j}
\]

only after checking the relevant `d`th power is zero. There is no convergence
test or floating-point approximation.

| Finite test | Declared range | Passed cases |
|---|---|---:|
| Scalar truncated coefficient identities in both directions | Cutoffs 1 through 20 | 20 |
| `log(exp(tN)) = tN`, recovery, cutoff independence, and kernel equality | Chains of lengths 1 through 12; six mixed partitions; three bases; five nonzero rational values of `t` | 270 |
| `exp(log(I+N)) = I+N` | The same 18 partitions and three bases | 54 |
| Rectangular exponential/logarithm intertwiners | Source and target dimensions 1 through 6; all listed Jordan-module generators; two nonzero rational samples | 182 |
| Recovery of monodromy and the original group action | Source/target dimensions `(1,4)`, `(2,6)`, `(4,6)`, `(6,12)`; three affine group elements | 12 |
| Explicit affine representation law | Nine pairs of affine elements for each of four target representations | 36 |
| Failure of a logarithm stopped too early | Degrees 2 through 6 on chains of length degree plus 2 | 5 |

These rows count different finite checks, and should not be added as a count of
independent mathematical theorems. The matrix families are constructed examples,
not an exhaustive classification of rational nilpotent matrices. The rectangular
census is exhaustive over its explicitly listed generators, dimensions, and
samples, not over all rational intertwiners.

The mixed partitions are `(1,1,1)`, `(2,2)`, `(1,2,3)`, `(2,3,4)`, `(1,4,6)`,
and `(2,4,6)`. The five sample scalars are `1`, `-2`, `1/2`, `-2/3`, and `3/5`.
Two of the three bases are nontrivial rational frames built from upper and lower
shears and diagonal factors. Their inverses are checked on both sides. The
shears cross the boundaries between mixed blocks.

## Cross-checks

The matrix-power implementation of the exponential is checked against the closed
Jordan entry formula `t^(j-i)/(j-i)!`, conjugated by the explicit frame. The
logarithm of `I+N` is checked against its independent closed Jordan entry formula.
Truncated scalar series composition uses a separate coefficient-convolution
implementation. Exact row reduction checks equality of the row spaces of `N`
and `exp(tN)-I`, which implies equality of their kernels. Rank is additionally
checked against the Jordan formula: dimension minus the number of blocks.

For each rectangular generator, the program first verifies
`N_target H = H N_source`, then checks exponential and logarithm naturality.
The reconstruction cases use the explicit rational affine group law

\[
(t,z)(u,w)=(t+3^z u,z+w),\quad
r(t,z)=\operatorname{diag}(3^{-zi}),\quad
\rho(t,z)=\exp(tN)r(t,z).
\]

The common recovery sample is `(-2/3,0)`, so both supplied original actions are
the identity at that sample and the scalar is nonzero. The tests recover `N`
by the full finite logarithm and recover `r` by `exp(-tN)rho(t,z)`. Distinct source
and target bases are used, including the dimension-12 target. The representation
law itself is separately checked on the stated 36 pairs, so the factor order and
scaling convention are tested.

## Boundaries

For the degree-`m` truncated logarithm on a chain of length `m+2`, the entry
`(0,m+1)` of the recovery error equals `(-1)^(m+1)/(m+1)`. In particular, the
quadratic logarithm fails on a length-four chain with error `-1/3` in entry
`(0,3)`. These are actual computed nonzero errors, not expected exceptions that
skip a check.

A nonzero length-six nilpotent matrix and the zero matrix give the same
exponential at `t=0`. The kernel equality also fails at that sample. Finally,
`A=E_(0,1)` and `B=E_(1,2)` give an entry `(0,2)` difference of `1/2` between
`exp(A)exp(B)` and `exp(A+B)`. This checks that an exponential product statement
needs its commutativity condition even when `A`, `B`, and `A+B` are nilpotent.

## Recorded execution

The computation-audit version-2 runner recorded a completed execution on
CPython 3.12.13 in 10.848640 seconds, exit status zero. It enforced a 240-second
wall-clock cap, 220-second per-process CPU cap, 1 GiB address-space cap, one CPU
core, and a 1 MiB combined-log cap. The conventional thread cap was one; this
program does not spawn threads. There is no usable Git commit in this working
copy, so the manifest pins the actual source hash instead.

- Source SHA-256: `20dbbb7a5bca8559df52d06262f6723bdf3f7e2969e2d04449eb9e64ffc7a28d`
- Result SHA-256: `ebbeb29c3489b7fbe5a6471e894ee461431c69fe4ec3fb96da7815fae5eef7b2`
- Run manifest: `checks/logarithms_run/manifest.json`
- Original result: `checks/logarithms_run/results.json`
- Byte-identical convenient copy: `exact_logarithms.json`
- Standard output and standard error are retained in the run directory.

The manifest validator passed with `--root` and confirmed that the pinned input
and declared output hashes match. A reproducible scientific-result command is:

```sh
python3 checks/exact_logarithms.py --output /tmp/block20-logarithms-replay.json
cmp exact_logarithms.json /tmp/block20-logarithms-replay.json
```

For matching serialized environment metadata, use the recorded Python version.
The source hash embedded in the scientific result changes if the source changes.
The bounded-run command, effective limits, start time, source hashes before and
after execution, and result hashes are recorded in the manifest.

## Interpretation and limits

The implementation and its finite assertions passed the stated deterministic
checks. Closed Jordan formulas, independent coefficient convolution, and exact
rank computations provide separate checks of the main computations. A separate
reviewer should still assess the source and interpretation; the runner itself
only authenticates execution and pinned artifacts.

This audit does not establish a universal theorem, construct an arithmetic
Galois-to-Weil–Deligne attachment, compare coefficients or Hodge–Tate periods, or
claim novelty. It does not close any of the five full arithmetic claims. The
structural pattern it supports is that the logarithm cutoff follows the actual
nilpotency bound; a fixed quadratic cutoff cannot recover arbitrary nilpotent
monodromy, while any nonzero common unipotent sample permits the checked
recovery in this finite suite.
