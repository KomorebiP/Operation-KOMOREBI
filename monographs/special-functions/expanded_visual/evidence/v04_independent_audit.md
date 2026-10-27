# Independent mathematical review of the thirteen v0.4 additions

This is a definition-first audit. The independent exact implementation was
written and run before reading the three new author generators. It imports no
author implementation. A second reviewer independently reconstructed the
normalization, translation, boundary, seed-repair, and discarded-channel
reductions. Agreement between reviewers is supporting review, not a proof.

The finite experiment checks the implementation in its declared range. The
elementary reductions below separately establish the displayed general
identities under their stated conventions. Final source pins and the review
verdict are recorded in the companion JSON after the full reproduction run.

## Mathematical conventions and dependency graph

Coefficients are in Q, R, or C, and factorial-normalized statements use a
characteristic-zero field or a Q-algebra. Ordinary z denotes a causal unit
delay. Coarse u denotes a complete phase block. A unilateral sequence is zero
at negative indices. Finite input records are zero beyond their final stored
sample, and convolution retains every terminal output. An explicitly observed
infinite prefix is not a finite input record.

Definitions -> coefficient comparison, polynomial multiplication, telescoping,
or finite linear algebra -> displayed elementary claim -> independent bounded
check and author figure. OEIS records identify three familiar sequences in the
bridges; their identities here have direct coefficient reductions. No external
theorem is needed to close any new general implication. The historical project
sources supply conventions, not an unstated proof assumption. There is no
dependence on a new Lean certificate or a novelty claim.

## Direct reductions

**B01, surviving modes.** With seeds a0=a, a1=b, multiplying the generating
series by D=1-3z+2z² gives a+(b-3a)z. Partial fractions give
A=(2a-b)/(1-z)+(b-a)/(1-2z), so a_n=(2a-b)+(b-a)2^n. The constant mode cancels
iff b=2a; the dyadic mode cancels iff b=a. Both vanish for a=b=0. Thus poles in
the reduced rational function depend on the numerator, while the recurrence
still has the same two candidate factors.

**B02, recurrence-aware tap reduction.** In the polynomial ring,
h=1+2z+z²=(2+z)-(1-z-z²). The causal Fibonacci series has DF=z, hence
hF=(2+z)F-z. The correction at index one is necessary. More generally polynomial
division h=qD+r and the actual input residual DF=N give hF=rF+qN. For finite
input records N includes the terminal residuals; it must not be replaced by the
infinite-series numerator z. This is an input-equation reduction, not equality
of the two filters on arbitrary signals.

**B03, reciprocal contracts.** D_r=1-rz has a formal inverse for every r because
its constant term is one. Its coefficients are r^n by multiplication. For
r≠0 the geometric series converges when |z|<1/|r|. At r=1/2, its absolutely
summable impulse response has sum two, so triangle inequality bounds every
bounded-input causal output by twice the input sup norm. At r=2, the bounded
constant input one produces 2^(n+1)-1, proving failure of bounded-input
stability. Evaluating the rational continuation on the unit circle does not
make the divergent causal series converge there.

**B04, coefficient integration.** The central-binomial coefficients obey
(n+1)b_{n+1}=2(2n+1)b_n and b0=1; these determine the formal solution to
(1-4z)B'=2B, namely the branch (1-4z)^(-1/2) with value one at zero. Formal
termwise integration followed by division by z sends b_n to b_n/(n+1), the
Catalan coefficients. The quotient is well-defined because the integral has
zero constant term. The analytic formula holds on |z|<1/4 with the specified
branch, and C(0)=1 is removable. At z=1/8 the exact area is (2-sqrt(2))/4 and
the average is 4-2sqrt(2). The displayed curve is sampled; these labels come
from the closed form, not quadrature as a proof.

**O01, factorial conjugation directions.** Define (Na)_n=a_n/n! and stationary
causal H by (Hv)_n=sum_{k=0}^{min(K,n)}h_k v_{n-k}. Direct substitution gives
(N^-1 HN a)_n=sum h_k(n)_k a_{n-k}. This pulls stationary Taylor-coordinate taps
back to counts. In the opposite direction, (NHN^-1 c)_n=sum h_k c_{n-k}/(n)_k.
Only k≤n occurs, so no zero falling factorial is inverted. For counts a_n=1,
stationary raw difference has counts (1,0,0,...), while stationary Taylor
difference of 1/n! has returned counts 1-n. These are distinct operations.

**O02, argument translation.** Expansion gives
B4(x+1)=x^4+2x^3+x²-1/30, whereas B4(x)=x^4-2x^3+x²-1/30. Their difference is
4x³ for every real or complex x. For integer N≥0, telescoping yields
sum_{k=0}^{N-1}k³=[B4(N)-B4(0)]/4=[N(N-1)/2]², including the N=0 empty sum.
The variable being shifted is the polynomial argument, not its order or its
Taylor coefficient index. At N=5, B4(5)=11999/30 and B4(0)=-1/30, giving 100.

**O03, boundary contracts.** On four-periodic vectors the operator
D_per x[n]=x[n]-x[(n-1) mod4] has constants as its kernel. Telescoping forces
the output sum to zero. Conversely any zero-sum output admits cumulative-sum
reconstruction with one arbitrary additive constant. A fixed x[0] removes that
freedom. For a causal finite zero-extended vector, its full difference includes
the terminal negative last sample and prefix summation recovers the input.
The guide does not claim surjectivity of difference on finite support or on
bounded infinite sequences. In fact finite-support outputs must have total
sum zero, while the bounded output y_n=1 has unbounded inverse x_n=n+1.

**C01, finite Fibonacci residual.** P8=(0,1,1,2,3,5,8,13) has zero-extended
polynomial degree seven. Multiplication by A=1-z-z² cancels the internal
recurrence coefficients. The seed gives z, and the two last terms give
-21z^8-13z^9. Thus the complete residual is z-21z^8-13z^9. The terminal terms
express the cutoff, not a failure of the stored recurrence.

**C02, three-phase operation.** In residue order 0,1,2, fine delay has matrix
C3=[[0,0,u],[1,0,0],[0,1,0]]. Therefore C3²=[[0,u,0],[0,0,u],[1,0,0]] and
A(C3)=[[1,-u,-u],[-1,1,-u],[-1,-1,1]]. Splitting the full residual gives
R0=-13u³, R1=1, R2=-21u². Each wrap uses the coarse delay u. These equations
are just regrouping of exact polynomial coefficients, so interleaving the
complete three streams recovers the full residual.

**C03, perturbation localization.** Adding one to x5 adds the impulse z^5 to
the input polynomial. Linearity changes the residual by
A z^5=z^5-z^6-z^7. All three resulting nonzero coefficients must remain; a
single changed input sample does not imply a single changed residual sample.

**C04, discarded-channel obstruction.** For even selection E, the generic
operator EA does not factor through E. The witness delta1 has E delta1=0, but
EA delta1=-delta1 in coarse indexing. Equivalently the even output of the
two-phase matrix [[1-u,-u],[-1,1-u]] depends on the discarded odd channel.
This proves nonclosure on arbitrary causal records. Even samples satisfying a
Fibonacci model have a distinct coarse recurrence 1-3u+u²; that restricted
model does not supply generic closure for the original fine operation.

**C05, model-constrained repair.** In the finite length-eight Fibonacci family
x0=a, x1=b, the even observations are a,a+b,2a+3b,5a+8b. Consequently a=x0,
b=x2-x0. All four even observations can be preserved iff
x4=3x2-x0 and x6=3x4-x2. When these hold, the model fixes the four missing odd
samples uniquely. The even data alone cannot establish that the original
discarded samples obeyed this model. Inconsistent observations have no exact
repair preserving all four; no noisy recovery claim is made.

**C06, streaming state and flush.** The local formula
y_n=x_n-x_{n-1}-x_{n-2} depends only on the last two input samples. A three-phase
emitter also needs n mod3; the value is the address of the next output. For
chunks(2,3,3), states after consumed counts 2,5,8 have histories (0,1),(2,3),
(8,13), and phase clocks all equal two. Two zero flush samples produce y8=-21
in phase2 and y9=-13 in phase0. Resetting history or phase at a chunk boundary
changes the operation. Local-state induction proves equality with the complete
convolution for every partition of a finite record; the bounded experiment
separately checks its implementation.

## Obligation matrix

| Scope | Load-bearing obligation | Direct evidence | Bounded independent check |
|---|---|---|---|
| B01 | Numerator controls exact factor cancellation | Partial fractions | 81 seeds, 32 coefficients |
| B02 | Reduced taps retain seed and terminal residual | Polynomial division identity | 49 additional seed pairs |
| B03 | Formal inverse differs from stable causal response | Geometric sum, triangle bound, unstable witness | 7 rational rates, 24 coefficients |
| B04 | Coefficient division equals normalized integration | Termwise formal integral and closed form | Degrees 0–24 |
| O01 | Both operator directions use the correct weights | Explicit factorial ratios | 13 vectors × 4 kernels, 16 coefficients |
| O02 | Argument shift is a discrete primitive | Polynomial expansion and telescoping | 31 rational arguments, N 0–24 |
| O03 | Boundary controls kernel, image, and recoverability | Kernel calculation and telescoping | 125 zero-sum targets, explicit full tail |
| C01 | Full finite residual contains both tail terms | Coefficient cancellation | Prefix lengths 2–24 |
| C02 | Delay wraps create correct channel bank | Matrix multiplication | Lengths 1–32, full tails |
| C03 | Perturbation creates a three-term stencil | Linearity | Impulse positions 0–15 |
| C04 | Generic even-only operation is impossible | Explicit kernel witness | Delta1 and P8 companion |
| C05 | Repair is unique only inside the stated model | Seed reconstruction and consistency | 81 seeds and 324 rejected inconsistencies |
| C06 | Two-sample history and phase clock survive chunking | Local-state induction | Lengths 1–32, chunks 1–7, all 128 P8 partitions, full flush |

## Reproducibility and limits

The computation contract is `v04_independent_contract.json`. The current
bounded version2 run and final source pins are named in
`v04_independent_audit.json`. The runner records actual command, software,
input hashes before and after, declared result hash, exit status, resource
caps, and execution time. Prior runs are superseded when source or accounting
metadata changes. The author generators use independent implementations and
their own evidence records.

No new Lean proof, historical novelty result, noisy inverse theorem, or
continuous reconstruction accuracy is established. Sampled curve geometry is
visual support. The elementary universal conclusions above have exact
reductions; the finite test bounds are implementation evidence only.
