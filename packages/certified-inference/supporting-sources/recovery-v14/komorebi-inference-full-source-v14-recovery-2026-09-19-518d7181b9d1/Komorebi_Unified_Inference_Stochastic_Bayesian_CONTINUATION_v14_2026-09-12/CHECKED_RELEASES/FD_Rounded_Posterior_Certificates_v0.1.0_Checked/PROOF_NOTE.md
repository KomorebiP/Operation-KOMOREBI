# Outward-rounded dyadic posterior certificates

## 1. Exact model and finite-precision arithmetic are distinct

The reference model is the retained exact factor-coded rational Gaussian model:

    P = L L^T, R = N N^T + sigma I, sigma > 0,
    S = H P H^T + R, F = P H^T - B S, v = y-Hm.

All rational input values denote exactly specified real numbers. The supplied
gain B can be arbitrary. It need not be the exact Kalman gain, and it need not
have been produced by the exact Richardson algorithm. The approximation is the
valid Joseph Gaussian of the represented B, while the reference is the already
proved explicit conditional posterior at y.

This release certifies a particular finite-fractional-precision enclosure
calculation, not IEEE-754 hardware. Center and radius values are rounded to a
2^(-p) grid, with unbounded signed integer parts. Overflow, NaNs, underflow,
processor rounding modes, BLAS, input parsing and export fidelity are not
included. The terminal sums of squared endpoints and tolerance comparison use
exact rational arithmetic. This mixed arithmetic contract is explicit.

The reference noise-floor proof still comes from the exact Gram-plus-floor
witness, rather than an approximate eigenvalue or a rounded covariance matrix.
Unknown physical model inputs and arbitrary covariance witness discovery remain
separate. Rounding the evaluation of a fixed model is not changing the model.

## 2. Scalar absolute error enclosures

A Ball contains rational center c and radius r. Encloses b x means |x-c|<=r.
An enclosing ball automatically has r>=0. Addition, negation, subtraction and
finite summation propagate the radii by the triangle inequality. Multiplication
uses

    center = c_a c_b,
    radius = |c_a| r_b + |c_b| r_a + r_a r_b.

The proof expands the product about its two centers and bounds all three error
terms, including the product of errors. Empty finite sums are covered.

For scale d=2^p define exact executable rational operations

    down_p(x)=floor(d*x)/d,
    up_p(x)=ceil(d*x)/d.

Lean proves down_p(x)<=x<=up_p(x), with no restriction on the sign of x. Recenter
and round a ball by

    c' = down_p(c),
    r' = up_p(r + |c-c'|).

The triangle inequality and upward rounding prove the new ball still encloses
x. Both c' and r' lie on the specified dyadic grid. Products are rounded before
summation. Sums are computed exactly and then rounded; sums of grid values have
no fractional-bit rounding loss before that final operation. No finite integer
word size is assumed.

If |x-c|<=r, then |x|<=|c|+r and

    x^2 <= (|c|+r)^2.

Rational-to-real transport of entrywise enclosure inequalities is proved.

## 3. Rectangular matrix and model evaluation

RoundedMatrix lifts the scalar rules entrywise to rectangular matrices, transpose,
addition, subtraction, multiplication, matrix-vector multiplication and vector
subtraction. Matrix products use finite sums of individually rounded interval
products. Their soundness is universal over finite index types, not a numerical
case assertion.

RoundedModel evaluates the full dependency graph from H,L,N,sigma,m,y,B:
prior covariance, observation-noise covariance, innovation covariance, gain
residual and innovation vector. It proves an entrywise absolute enclosure for
the corresponding EXACT rational expression at each node. These proofs do not
assume a correct residual interval from an external producer.

Exact packet projectors Q_a,D_b are themselves enclosed during their arithmetic
use. The rounded centers need not be idempotent or self-adjoint. The geometric
hypotheses are checked on the exact represented packets, and the enclosure
proof tracks errors from multiplying with their rounded representations.

For the rounded packet enclosure (c_abij,r_abij), define

    b_ab = sum_ij (|c_abij|+r_abij)^2.

Similarly use V=sum_j (|c_vj|+r_vj)^2 for the innovation enclosure. The new generic
roundedCandidate_valid theorem proves those bounds satisfy every finite exact
candidate obligation, assuming only a positive exact floor and valid complete
self-adjoint rational packet families.

## 4. Actual posterior guarantee

Let U=sum_ab b_ab and score=U*(sigma+V)/sigma^2. The retained semantic theorem
combined with the new enclosure proofs yields

    W2^2(actualPosterior, JosephApproximation(B)) <= ofReal(score).

For eps>=0 the exact rational scalar test

    U*(sigma+V) <= eps^2*sigma^2

implies W2<=eps. The all-coupling transport definition, possibly singular prior,
rectangular observation and explicit-versus-canonical posterior boundaries are
unchanged. This proof does not require computing the true gain or S inverse.

certifyRounded checks the positive floor and exact packet geometry, computes the
outward-rounded candidate, and checks its tolerance. Unlike invoking the older
exact checkCandidate computationally, its execution does not recompute the full
exact residual or its exact packet energies. The universal soundness proof
implies that the old exact checker would accept the returned candidate.

certifyPrecisions tries a finite list of precision values and returns the first
passing candidate. Every successful return has the actual-law guarantee without
pre-assumed input validity. None means not certified; it does not prove that the
true error exceeds the requested tolerance. No theorem of monotonicity of the
scores in precision, or eventual success of arbitrary precision schedules, is
claimed. Strict slack and a precision-completeness argument remain separate.

## 5. Kernel-checked concrete computations

The scalar input P=H=R=1, m=0,y=1,B=1025/2048 has exact residual -1/1024.
At p=4 the computed residual center is ZERO, with radius 1/8. Discarding that
radius is formally proved invalid. The p=4 score is 1/32 and rejects eps=1/500.
At p=12 the score is 1/524288 and certifies W2<=1/500. The actual precision-search
return for [4,12] is checked, as is rejection of a tighter coarse tolerance.

The two-state singular-prior example uses P=ones(2), H=R=I, m=0, y=(1,-1),
B=(39/125)ones(2), and rotated rational rank-one packets. Its p=4 score is 21/4;
p=12 yields 215859/4194304 and certifies W2<=1/4. The score computations, tolerance
results and successful return are Lean kernel reductions of the implemented
rounded evaluator, not statements accepted from Python output.

## 6. Evidence and limits

The exact Python producer simulates the same mathematical rounded operations
using Fraction. The exported Lean definitions contain the full exact model and
invoke the executable rounded evaluator. Kernel-reduced score/tolerance checks
and the generic theorem provide the formal instance evidence. Python output
alone is provisional. The parser, serializer and its faithful representation of
user intent remain a trust boundary to inspect, not a proved theorem.

Independent tests use Fraction scalar corner checks and SymPy exact matrix
expressions for nine rectangular dimension pairs at three precisions. They also
check negative values, grid membership, singular priors and invalid input types.
These are finite diagnostics, not a universal proof or performance benchmark.

All active modules have final-source receipts and complete declaration axiom
audits. The 42 inherited source modules in the active dependency slice were
freshly compiled, unchanged. The remainder of the v8 historical program is
preserved rather than fully rebuilt. See the verification receipt for actual
counts and failures. No literature-priority assertion is made.

## 7. Strongest next boundary

Prove quantitative precision sufficiency when the exact candidate has strict
slack below its posterior tolerance. Separately develop roundoff-aware gain
iteration: a rounded update has additive residual forcing and can exhibit a
roundoff floor, unlike the already checked ideal exact Richardson recurrence.
An adaptive-precision success theorem must control that forcing and the outward
certificate inflation. Neither follows merely from successful-return soundness.
