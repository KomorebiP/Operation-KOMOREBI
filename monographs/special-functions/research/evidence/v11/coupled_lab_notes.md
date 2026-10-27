# Coupled laboratory integration note

Checkpoint: SF-DISCOVERY-110. Public attribution: Komorebi P.

The reusable module `coupled_lab.py` uses Python's standard library and imports
the existing exact coefficient, phase and tap operations from `family_lab.py`.
The figure builder additionally uses NumPy and Matplotlib. Neither script
contacts an external service. The generic integer and signed catalog rows are
formal power series, with no claim of analytic convergence.

## Normalization and recurrence

Write

\[
U(z)=\sum_{n\ge0}A_n\frac{z^{2n+1}}{(2n+1)!},\qquad
V(z)=\sum_{n\ge0}B_n\frac{z^{2n+1}}{(2n+1)!}.
\]

The exact recurrence is

\[
A_n=\sum_{i+j=n-1}\binom{2n}{2i+1}q^{2i+1}r^{2j+1}A_iB_j,
\qquad
B_n=\sum_{i+j=n-1}\binom{2n}{2i+1}a^{2i+1}b^{2j+1}A_iB_j,
\]

with \(A_0=B_0=1\). Coefficients with even derivative index vanish. Swapping
the components sends the parameter tuple \((q,r,a,b)\) to \((b,a,r,q)\).
Identical rows \((a,b)=(q,r)\), or exchanged rows \((a,b)=(r,q)\), yield the
scalar reduction \(U=V=T_{q,r}\).

Both derivative arrays are polynomials in four scale variables with
nonnegative integer coefficients. Their total degree is at most \(n(n+1)\).
Indeed, a recurrence term with \(i+j=n-1\) has degree at most
\(2n+i(i+1)+j(j+1)\le n(n+1)\). If all four denominators divide \(D\),
then \(D^{n(n+1)}A_n\) and \(D^{n(n+1)}B_n\) are integers. The clearing
factor is a convenient uniform choice and need not be minimal.

## An elementary exact evaluation certificate

This argument uses \(0<q,r,a,b<1\) and does not require the order theorem.
Let \(Q=\max(q,r,a,b)\). All ordinary odd Taylor coefficients are positive
and at most one: induction in the ordinary recurrence bounds the coefficient
of \(z^{2n+1}\) by \(n/(2n+1)\) for \(n\ge1\). Thus both series converge
on the unit disk and, for \(0\le x<1\),

\[
\max(U(x),V(x))\le \frac{x}{1-x^2}.
\]

Analytic continuation by the integral equations expands each known disk by
the factor \(1/Q\), so both solutions are entire. Positive coefficients
give \(\max_{|z|\le x}|F(z)|=F(x)\) for either component. The integral
equations therefore imply

\[
M(x):=\max(U(x),V(x))\le x\bigl(1+M(Qx)^2\bigr).
\]

Start at the first member \(Q^kx<1\) of this finite contraction ladder,
use \(x/(1-x^2)\) there, and repeatedly apply \(B(x)=x(1+B(Qx)^2)\)
backward. This defines the rational `disk_majorant` bound for rational
parameters and radius. The implementation has explicit recursion and integer
size guards, which raise errors rather than returning a weakened result.

If \(F_N\) retains odd indices \(0,\ldots,N\), then for \(S>R\ge0\),

\[
\max_{|z|\le R}|F(z)-F_N(z)|
\le B(S)\left(\frac RS\right)^{2N+3}.
\]

For every omitted exponent \(m\ge2N+3\), use
\(R^m\le (R/S)^{2N+3}S^m\), sum positive terms, and bound their sum by
\(F(S)\le B(S)\). No extra geometric denominator is needed. For rational
\(x\ge0\), `certified_evaluation` returns the exact interval
\([F_N(x),F_N(x)+B(S)(x/S)^{2N+3}]\) for each component.

## Worked calls

```python
from fractions import Fraction as Q
import coupled_lab as lab

p = (Q(1,5), Q(2,5), Q(3,5), Q(7,10))
A, B = lab.coupled_odd_derivatives(*p, last=12)
certificate = lab.certified_evaluation(*p, Q(1), last=30, outer_radius=2)
root = lab.pf_order(*p)  # floating approximation, not interval arithmetic

derivatives = lab.full_egf_coefficients(B)
phases = lab.phase_lanes(derivatives, 3)
matrix = lab.polyphase_tap_matrix([1, -2, 1], 3)
length = len(derivatives) + 2
output_phases = lab.apply_polyphase_matrix(phases, matrix, length)
output = lab.merge_lanes(output_phases, length)
```

At \(x=1\), with \(N=30\) and \(S=2\), the common tail bound is below
\(1.600\times10^{-13}\). The partial values are approximately
\(U(1)=1.027044341827337\) and \(V(1)=1.1467074957737624\).
These displayed decimals are rounded illustrations. The returned fractions
are the actual certificate.

Run the independent checks and regenerate figures from the project root:

```text
python3 checks/coupled_v11.py
python3 build_coupled_figures.py
```

The first command passes 1,559 exact assertions, 10 numerical comparisons,
and 13 separate input/resource guards. Independent constructions include dense
ordinary Taylor Picard iteration, sine/cosine division for tangent, the exact
sinh formula, component symmetry, and direct convolution versus phase carry.
The test counts describe bounded implementation checks, not universal proofs.

## Six visual plates

1. `coupled_01_matrix`: the exact order-one PF anchor
   \((1/5,2/5,3/5,7/10)\), with positive right eigenvector \((1/2,1)\).
   The matrix entries and both eigenvector equations are exact.
2. `coupled_02_functions`: generic contractions
   \((1/3,2/3,1/2,3/4)\), showing the component values and amplification
   above the shared initial slope. Floating log coefficients through index
   240 agree with index 120 at the largest plotted argument \(x=8\) to
   displayed double precision. This is a diagnostic, not a tail proof.
3. `coupled_03_growth`: the order-one anchor through \(R=160\), with
   separate amplitudes and finite-radius local slopes. Index 800 agrees
   with index 400 at the largest plotted radius to displayed double precision.
   The slope picture does not assert existence of a limiting type constant.
4. `coupled_04_landscape`: numerical PF roots on a \(65\times65\) grid
   in \((q,b)\), fixing \(r=2/5,a=3/5\). The highlighted anchor is exact.
5. `coupled_05_certification`: rigorous rational disk tail bounds for four
   radii, displayed as logarithmic curves. This figure certifies both components.
6. `coupled_06_polyphase`: exact base-three phase reconstruction of the
   second component's derivative array under taps \((1,-2,1)\).
   Ordinary FIR on EGF derivative arrays represents integral shifts, not
   multiplication of exponential generating functions.

## Recovered build failure

The first figure build failed before completing because Matplotlib's mathtext
parser requires explicit braces in fraction labels. Replacing abbreviated
fractions with braced numerator and denominator arguments fixed the build.
The complete set was then regenerated and each image inspected. No data or
mathematical formula changed in that repair.
