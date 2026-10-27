# Fourier-orbit obstructions and a conjugation-only route to the cubic comparison

**Komorebi H12 v0.11.0. Base: Based Holonomy v0.10.0.**

## Status

The original equality U_Gamma=U_alg and Im(C_pol U_Gamma^3)=0 remain unproved.
No actual relative gamma/model multiplier or its Fourier coefficients have been
constructed in this release. The goal is not replaced by the auxiliary results.

This block proves a constructive alternative to compact descent. For the actual
hyperbolic integer unit matrix, a nowhere-zero holomorphic multiplier on the
intermediate cover is reducible to a monomial if and only if all its nonconstant
dual-orbit coefficient sums vanish. A convergent formula constructs the gauge.
A strictly weaker conjugation condition suffices for the desired cubic bound,
provided the multiplier represents the actual discrepancy and the inherited
modulus comparison is available. The construction also works smoothly on the
real torus and need not begin with a compact holomorphic comparison line.

The smooth Fourier cohomological mechanism is classical [1]. We give the
specialized proof, signs, exponential-decay version, explicit flat extension,
and conductor-three consequence. No literature-novelty claim is made.
Twenty-eight Std-only coefficient theorems are freshly compiled and audited.
The infinite-series, topology, exponential, and analytic comparisons are
ordinary proofs, not hidden Lean axioms.

## 1. Actual matrix and three distinct variables

Let

    M = [0,1,0; -4,2,15; -1,0,4],
    A = transpose(M) = [0,-4,-1; 1,2,0; 0,15,4],
    A^(-1) = [8,1,2; -4,0,-1; 15,0,4].

The intermediate cover is X=C^3/Z^3=(C^*)^3; its real torus is T^3=R^3/Z^3.
Use column base coordinates v and frequencies k in Z^3, and

    e_k(v)=exp(2*pi*i*k^T v).

Then e_k(Mv)=e_(Ak)(v). This is frequency transport, NOT shifting the scalar
return index in F(rho^m/3), nor changing the argument multiplier in F(kz).

The actual characteristic polynomial is

    h(x)=x^3-6x^2+12x-1=(x-2)^3+7.

Its real root is a=2-cuberoot(7), with 0<a<1. Its two complex roots have common
absolute value b=a^(-1/2)>1 because det M=1. Thus M and A are hyperbolic.
They are diagonalizable over C. A real adapted norm can be chosen so

    ||k||_* = max(|k_s|, |k_u|),
    ||A^j k||_* = max(a^j |k_s|, b^j |k_u|),

where k_s is a real stable coordinate and k_u a complex unstable coordinate.
Every nonzero integer k has both coordinates nonzero: otherwise positive or
negative iterates would tend to zero while remaining nonzero integer vectors.
In particular every nonzero A-orbit is infinite and escapes in both directions.
No orbit contains both k and -k: that would produce a nonzero periodic vector.

The conductor point is p=e2/3=(0,0,1/3). Its carry is

    Mp-p=(0,5,1),
    (Ak)_2=15k_1+4k_2 = k_2 modulo 3.

Thus each dual orbit has a well-defined conductor residue k_2 modulo 3.

## 2. Scalar holomorphic multipliers and their genuine ambiguity

For a nowhere-zero holomorphic function a_X on X, the map

    (v,t) -> (Mv,a_X(v)t)

is a linearization of the trivial line for the infinite cyclic unit group.
Changing frame by a nowhere-zero holomorphic b_X changes the multiplier to

    a_X'(v)=a_X(v)b_X(v)/b_X(Mv).                         (1)

Every such a_X has a unique decomposition

    a_X(v)=alpha * e_m(v) * exp(h(v)),
    alpha != 0, m in Z^3, h holomorphic and Z^3-periodic,
    Fourier coefficient h_hat(0)=0.                     (2)

To prove existence, lift a_X to the simply connected space C^3 and take a
holomorphic logarithm. Its increments along n in Z^3 are 2*pi*i*m^T n with
m integral. Remove that linear term, then remove the zero Fourier coefficient
into alpha. Uniqueness follows from the constant integer ambiguity of a log.
The smooth version on T^3 follows from removing the winding class in
H^1(T^3,Z), then lifting the remaining null-homotopic map to C.

A frame b_X=c*e_n*exp(g) changes m by (I-A)n and h by g-g composed with M
(after discarding the harmless constant coefficient of g). Alpha is unchanged.
The base value of a_X is not necessarily alpha until the nonconstant part has
been removed; do not identify those two values prematurely.

The original gamma function F(pi(v)) is NOT automatically a function on X:
its shifts in the tau and s directions have theta multipliers. The theorem
below concerns a relative scalar multiplier AFTER genuine comparison data
have produced one, with its regularity and nonvanishing checked. It cannot be
applied simply by inserting the known one-variable logarithm of F.

## 3. The complete Fourier obstruction and its explicit right inverse

Write

    h(v)=sum_(k in Z^3) c_k e_k(v), c_0=0.

For each nonzero frequency orbit O=A^Z k define

    Q_O(h)=sum_(j in Z) c_(A^j k).                        (3)

The sum is independent of the chosen orbit representative. For smooth h it is
absolutely convergent by rapid coefficient decay; for holomorphic h on all X,
the Laurent coefficients decay faster than every fixed exponential. In either
case the full coefficient sequence is absolutely summable on the real torus.

### Theorem 3.1

For smooth h on T^3 with mean zero, the following are equivalent:

1. Q_O(h)=0 for every nonzero A-orbit O;
2. h=g-g composed with M for a smooth mean-zero g.

If h extends holomorphically to ALL X, the constructed g also extends
holomorphically to ALL X. In both cases g is unique after fixing its mean zero.

An explicit coefficient formula is

    b_k = sum_(j>=0) c_(A^(-j) k)
        = -sum_(j>=1) c_(A^j k),  k != 0,
    b_0=0,
    g(v)=sum b_k e_k(v).                                  (4)

The two tails in (4) are equal precisely because the orbit sum vanishes.

**Necessity.** Coefficient comparison in h=g-g(Mv) gives

    c_k=b_k-b_(A^(-1)k).

Summing on an orbit telescopes. Both endpoints vanish by coefficient decay and
escape of the orbit, proving Q_O=0. Notice the TWO endpoints; a one-sided
cumulative sum without the second condition is insufficient.

**Recurrence.** The first formula in (4) gives
b_k-b_(A^(-1)k)=c_k. It remains to prove regularity of g, not just formal equality.

**Convergence.** Put mu=min(a^(-1),b)>1 and
kappa=inf_(k in Z^3, k!=0)||k||_*>0. If the unstable component of k dominates,
use the forward tail in (4); along it the norm grows at least mu^j||k||_*.
If the stable component dominates, use the backward tail. Thus the coefficients
are summed only in an expanding direction.

In the holomorphic case, for every R>0 Laurent Cauchy estimates give a constant
C_R with |c_k|<=C_R exp(-R||k||_*). Since mu^j>=1+j(mu-1),

    |b_k| <= C_R exp(-R||k||_*) /
             (1-exp(-R(mu-1)kappa)).                       (5)

The possible forward tail starts at j=1, so the displayed j=0 bound is still
valid. Estimate (5), for arbitrary R, proves absolute normal convergence on
every compact product annulus in X. Hence g is holomorphic globally.

For the smooth version, use for any N>0 the bound
|c_k|<=C_N||k||_*^(-N); summing the geometric growth gives

    |b_k|<=C_N||k||_*^(-N)/(1-mu^(-N)).                    (6)

Since N is arbitrary, g is smooth. Uniqueness follows because invariant
coefficients would be constant on infinite escaping orbits and also decay.
QED.

The smooth statement is the zero-translation specialization of the Fourier
cohomological argument in Zeggar [1], Sections 3-5. His coefficient transport
uses M^(-T); our indexing uses its inverse A=M^T, so the orbit sets coincide.
Signs and tail endpoints in (4) are derived here directly, not copied from a
possibly differently signed cochain convention. The exponential estimate (5)
supplies the stated global holomorphic version.

## 4. This is a constructive compactification criterion

For the scalar multiplier (2), all Q_O(h) are invariant under holomorphic frame
changes (1). If they vanish, use b_X=exp(-g). The new multiplier is exactly

    a_X'(v)=alpha e_m(v).                                  (7)

Conversely a gauge equivalence to (7) forces those orbit sums to vanish.
Thus the criterion is necessary AND sufficient within the explicitly specified
space of nowhere-zero holomorphic scalar multipliers. It is not a criterion
for arbitrary unspecified gamma gerbes or meromorphic sections with poles.

There is then an explicit compact extension. Put D=M-I and take the real row

    u=-m^T D^(-1),
    6u=(3m0-3m1+m2, -3m0-3m1-m2, 15m0+15m1+3m2).          (8)

For lambda=n+omega*l, n,l in Z^3, define the unitary character

    chi(lambda)=exp(2*pi*i*u*n).

Because uD=-m^T is integral, chi(Mlambda)=chi(lambda). The flat line on
C^3/Z[omega]^3 with this character admits the constant lift alpha. Restrict to
X and trivialize the real periods by T=exp(-2*pi*i*u*v)t. Its lifted multiplier
is exactly alpha e_m(v), since -uD=m^T. This constructs the compact extension,
not merely its class.

The converse that a restriction of a compact holomorphic M-equivariant line
is holomorphically gauge-equivalent to a monomial uses v0.10's compact-line
lemma. Hence Theorem 3.1 gives a direct cover-level test for such scalarizations.

At p=e2/3 every periodic gauge has b_X(Mp)=b_X(p), so based fiber multipliers are
unchanged. In the monomial gauge,

    a_X(p)/a_X(0)=exp(2*pi*i*m2/3),
    [a_X(p)/a_X(0)]^3=1.                                  (9)

The free scalar alpha is retained until the ratio cancels it. Winding-frame
changes preserve m2 modulo 3, since ((I-A)n)_2 is divisible by 3.

## 5. The phase problem needs LESS than full flattening

Define conjugate reflection on periodic holomorphic functions by

    h#(v)=overline(h(overline(v))).

On the real torus this is ordinary conjugation. Its coefficient at k is
conjugate(c_(-k)), and it commutes with composition by the real matrix M.

### Theorem 5.1: conjugation-only criterion

Suppose the multiplier (2) is nowhere zero and smooth on T^3 (or holomorphic on
X), and for every nonzero frequency orbit O,

    Q_O(h) = conjugate(Q_(-O)(h)).                         (10)

Then there is a smooth (respectively holomorphic) frame in which

    a_X'(v)=alpha e_m(v) exp(r(v)),

where r is real-valued on the real torus. In particular if

    |a_X(p)/a_X(0)|=1,

then

    [a_X(p)/a_X(0)]^3=1.                                  (11)

**Proof.** The mean-zero function k=h-h# has zero orbit sums by (10). By
Theorem 3.1, k=g-g(Mv) with mean-zero g. Its uniqueness gives g#=-g, although
this extra property is not needed just to compute the new multiplier. Take
b_X=exp(-g/2). Equation (1) then replaces h by

    h-(g-g(Mv))/2=(h+h#)/2=:r.

For real v, r(v) is real. At the fixed conductor point, the based ratio is

    exp(2*pi*i*m2/3) * exp(r(p)-r(0)).

Its modulus is exp(r(p)-r(0)). The stated unit-modulus condition therefore
forces r(p)-r(0)=0 and proves (11). QED.

The full orbit sums need NOT vanish. For example h=e_(3e2)+e_(-3e2) has nonzero
symmetric residues, is real on the real torus, and already gives h(p)=h(0).
Thus this phase criterion is genuinely weaker than compactifiability.

The inherited modulus equality for U_Gamma/U_alg supplies the modulus premise
ONLY after that ratio has been identified with this based multiplier. Neither
that scalar identification nor (10) is established for the gamma data here.

## 6. Only two conductor residue sectors can contribute

For any mean-zero h in the stated regularity class, absolute convergence gives

    h(p)-h(0) = sum_O (omega^(k2)-1) Q_O(h),                (12)

where k is any representative of O. It is well-defined since (Ak)_2=k2 mod3.
Orbits in residue zero contribute nothing. Opposite orbits are paired by
complex conjugation under (10); their contribution in (12) is real.

This gives a still weaker sufficient target: only the weighted sum of the
antisymmetric orbit residues in the two nonzero conductor sectors must vanish.
It may cancel between different orbits. Proving (10) orbitwise is a transparent
sufficient method, not a necessary condition for one special-point equality.
No finite set of sampled small residuals proves this infinite identity.

## 7. Finite-support cancellation has an exact certificate

On a finite stretch k_j=A^j k, write h=sum_(j=l)^r c_j e_(k_j). Let

    charge=sum c_j.

Subtract charge*e_(k_l) from h and cumulatively sum its coefficients. The
resulting finitely supported g satisfies exactly

    h=g-g(Mv)+charge*e_(k_l).                              (13)

In particular a finite orbit block is a finite Laurent coboundary iff its total
charge is zero. This is an algebraic proof, not a floating-point test. A producer
accepts a specified seed and integer-indexed block, constructs g, and checks
the full Laurent identity. It does not use a bounded search to claim two
arbitrary seeds are in distinct orbits.

For k=e2 the actual orbit begins

    (0,0,1), (-1,0,4), (-4,-1,16), (-12,-6,49).

The old stencil (1,-6,12,-1), if applied along THIS Fourier orbit, has charge 6.
It does not define a removable logarithmic gauge. Its exact decomposition is

    h = [g-g(Mv)] + 6 e_k,
    g = -5e_k-11e_(Ak)+e_(A^2k).                           (14)

Subtracting 6e_k gives a genuine closed stencil. The equality H(rho)=0 in the
scalar return axis does not imply zero Fourier-orbit charge: these are different
actions. This is a checked negative control against conflating the axes.

The Lean module H12OrbitAntidifference proves the universal finite prefix-sum,
endpoint, gauge-conservation, exact reconstruction, and zero-tail statements.

## 8. No finite periodic-point test certifies flattening

For any prescribed N>=1, put

    Q_N=lcm_(1<=j<=N) |det(M^j-I)|.

Every point of period at most N on T^3 has Q_N*v integral: use the adjugate of
M^j-I. Define for any real nonzero theta

    h_N(v)=theta [e_(Q_N e2)(v)-e_(-Q_N e2)(v)],
    a_N(v)=exp(h_N(v)).                                    (15)

Then a_N is entire and nowhere zero on X, equals one at zero and at EVERY
periodic point of period at most N, has modulus one on T^3, and obeys

    a_N(-v)=a_N(v)^(-1).

Nevertheless its two nonzero frequency-orbit charges are theta and -theta;
the two orbits are distinct by hyperbolicity. Thus a_N is not removable by a
holomorphic scalar gauge and fails the orbitwise conjugation criterion.

The point is not to refute the gamma equality. This is a universal obstruction
to treating finitely many successful unit-return tests as a proof of global
flattening. The exact checker verifies the denominator certificates for N<=6;
the argument above proves the assertion for every N.

## 9. Where the actual gamma comparison still enters

No compact comparison line has been constructed here. No relative gamma/model
scalar a_Delta has been derived from the actual cochains. Therefore neither
Q_O(h_Delta)=0 nor its conjugation-only version (10) has been proved.

The concrete next work is:

1. From the actual gamma and independently normalized arithmetic-model cochains,
   produce a relative multiplier a_Delta at least smooth and nowhere zero on
   the real torus. If a meromorphic expression is used, prove that the relevant
   zeros and poles cancel. A formula involving F(pi(v)) alone is not enough.
2. Identify its based multiplier a_Delta(p)/a_Delta(0) with U_Gamma/U_alg. Do not
   prescribe a_Delta at p to force that identity.
3. Prove the antisymmetric logarithm h_Delta-h_Delta# is a unit coboundary, e.g.
   by exact Fourier-orbit reindexing using (4). A finite tail certificate or an
   identity of generating functions can prove infinite cancellations; numerical
   smallness cannot.

If these steps hold, Theorem 5.1, the inherited modulus theorem, and the existing
branch enclosure complete the cubic and original comparisons. This is a valid
alternative to requiring full compact gerbe descent. It is not an assertion
that the new hypotheses already hold for gamma.

## 10. Computation and formal scope

Fresh Lean modules: H12OrbitAntidifference (14 theorem constants),
H12DualFourier (9), H12FourierExtension (5): 28 in total. They use the pinned
Lean 4.34.0-rc2 compiler and bundled Std. They prove finite integer coefficient
statements and exact matrix/winding identities. The global analytic theorem,
the smooth/holomorphic logarithm construction, its convergence estimates, and
the phase criterion are ordinary proofs, NOT claimed as Lean analysis.

The checker audits every exported theorem's transitive axioms and requires a
false integer statement to fail. Only propext, Classical.choice and Quot.sound
are permitted. No project axioms, admitted proofs or native_decide are allowed.

The exact Python checker proves its finite Laurent certificates by dictionary
arithmetic over Fraction and uses independent symbolic matrix computations.
It tests all 3905 coefficient strings of length 1..5 in {-2,-1,0,1,2}; this is
implementation evidence, not the proof of the universal theorem. It also tests
signed orbit indices -15..15, denominator certificates for periods up to six,
and conjugation/boundary identities. Exact counts are in evidence/exact_results.json.
No gamma numerical comparison, new interval certificate, or novel algebraicity
claim is made. The 360 inherited source declarations and historical evidence
are preserved inside the predecessor ZIP, not freshly replayed in this block.

## References

[1] Abdellatif Zeggar, Equation cohomologique d'un automorphisme affine hyperbolique
du tore, arXiv:1902.04849v1, 13 February 2019. Sections 3.3, 4.3-4.6 and 5.
https://arxiv.org/html/1902.04849 . Primary source checked for smooth Fourier
orbit obstructions and adapted-norm convergence. The full holomorphic estimate
used above is proved explicitly here, not attributed to an unverified theorem.

[2] Felder, Henriques, Rossi, Zhu, A gerbe for the elliptic gamma function,
arXiv:math/0601337v1, Sections 3.1 and 4. The actual lattice is Z^3; no automatic
extra-Eisenstein compactification follows from these definitions.
https://arxiv.org/html/math/0601337v1

[3] Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields,
arXiv:2311.04110v2. Gamma conventions and the distinction between a proved
modulus formula and the conjectural complex-value identification.
https://arxiv.org/html/2311.04110v2

[4] Retained Based Holonomy v0.10.0, PROOF.md Sections 5-9. Supplies the
compact-line endpoint, counterexample on the cover, and the still-missing
scalar identification. Its source/evidence ZIP is retained byte-for-byte.
