# Euler nonintersection: a uniform finite-parameter certificate

## Status

This continuation proves a computer-assisted family exclusion using the inherited
Euler wall identities and a new finite coefficient certificate. It is not a new
Lean release: no Lean compiler was run. It does not prove universal Euler
simplicity, and it does not construct an all-precision analytic interpolation of
the actual undepleted integer-index family.

The certificate is universal in its stated parameter range, rather than a list
of sampled multiplier checks. The finite lifting proof explaining the universal
quantifier is given below. Exact integer/modular calculations supply the finite
coefficient inputs to that proof.

## Main conclusion

For an ordinary integer T define

    B = 17659 + 2^18 T,
    r = B*2^640 - 161.

For every integer 0 <= T < 2^449 and every x in Z_2,

    NOT (G_r(x)=0 AND G_r'(x)=0).

Thus every dyadic root of each of these actual Euler residuals is simple.
This is a statement about one structured family of depths, not about every
r < 2^1107, all terminal-161 walls, or all terminal labels.

More generally, for any T>=0 for which the true terminal label remains 161,
a critical zero is possible only if

    T = tau_450 mod 2^450,

where the canonical residue tau_450 is stored in fast_certificate_629.json.
Its hexadecimal value is

    0x3fc88555e10fac0e48a7941d28a76c4dc218d7b7138e11d8d2e2765e15d63f9d88865d583659a844f7b68907781c55c9f4b60a21aead7d3cd

It satisfies

    2^449 <= tau_450 < 2^450.

A zero of a finite congruence system is NOT declared an exact singular Euler
parameter. The one retained residue class remains unresolved.

## 1. Inherited objects and the precision contract

We use the signed Euler residual of the preceding releases:

    G_r(x) = sum_(q>=0) gamma_(r,q) P_q(x) A(x-q),
    gamma_(r,q) = 2^(-mu_r) 8^q beta_(r+q)/beta_r,
    P_q(x) = product_(i=0,...,q-1) (x-i)(2x-2i-1).

The actual carry cost is

    lambda_r(q) = 3q+s2(r+q)-s2(r),
    mu_r = min lambda_r(q),
    j_r = max {q : lambda_r(q)=mu_r}.

The carried-forward results used here are:

* Exact packet construction, integral normalization and restrictedness.
* The finite cutoff q <= floor((s2(r)-1)/3) for a possible carry minimum.
* The terminal identity G_r=P_j U_r+2^delta V_r, with U_r reducing to 1.
* Exact isolated-skeleton normalizations on the canonical dyadic balls.
* The uniform finite-precision multiplier template in Continuation VI,
  Theorem VI.7 of Dyadic_Euler_Tails_Running_v6.md.

The last theorem is mathematical input from that manuscript, not newly compiled
Lean arithmetic in this continuation. Its hypotheses and why it applies are
spelled out rather than omitted.

Fix j=161, L=640, P=629, r_base=2^640-161 and Q=2P=1258. At the base index split

the finite packet approximation into low and upper parts L_0 and U_0:

    L_0 = sum_(q<161) gamma_(r_base,q) P_q A(.-q),
    U_0 = sum_(161<=q<1258) gamma_(r_base,q) P_q A(.-q),

with complete coefficient precision 2^629. On either parity ball, for every
positive odd B whose true terminal label is 161,

    B G_(B*2^640-161) = B L_0 + U_0 mod 2^629

COEFFICIENTWISE. The supplied precision hypotheses hold because

    2^640 > 2(161+1258),
    2(2^640-161)-1 > 629,
    641-ceil(log2(2(161+1258)+1)) = 641-12 = 629.

No all-precision interpolation in B follows or is needed.

For clarity, the arithmetic reason for the template is that every nonzero
factorial offset 2^641 B+(t-322), with q<1258, has the same stripped odd unit
modulo 2^629 as at B=1. The sole zero offset for q>=161 contributes the explicit
odd factor B in the denominator. The Bernoulli units agree at this precision.
The inherited parity cutoff controls every omitted q>=1258 independently of
remote carry events.

The Bernoulli congruence is itself based on the exact midpoint/duplication
identity and the 2-adic Bernoulli denominator theorem. For even n sufficiently
large compared with P,

    2 B_n = sum_(k=0,...,P) binom(n,k) 2^k B_k mod 2^P.

All divisions in the modular code are by odd units after valuations are removed.
References for these classical identities: DLMF 24.4 and 24.10.

The baseline gamma bound already makes q>=371 zero coefficientwise at this
precision. Therefore computing q<=370 produces the same finite template as
q<1258. This is a proved cutoff, not an empirical truncation.

## 2. True terminal label throughout the displayed finite-height range

For positive odd B,

    s2(B*2^640-161) = s2(B)+637.

If 0<=T<2^449, then B<2^467, so s2(B)<=467 and s2(r)<=1104.
The inherited carry-minimizer cutoff is therefore at most 367.

For q<161,

    lambda_r(q) = 3q+2-s2(160-q).

The exact 161-entry finite table has minimum -1, attained only at q=1.
At q=161,

    lambda_r(161) = -154.

For 161<q<=367,

    lambda_r(q) = -154+3(q-161)+s2(q-161) > -154.

Every later q is outside the global minimizer cutoff. Thus the true terminal
label and normalization are

    j_r=161, mu_r=-154,

for EVERY parameter in the asserted range. The lower minimum is -1 and the wall
distance is delta=153. This proves the terminal hypothesis; it is not assumed
from the visual form of the index.

## 3. All possible critical zeros are on one skeleton ball

The lower residue is coefficientwise X modulo two. Hence V_r=X+2R_r and V_r
is a global dyadic isometry with unit derivative and one root beta_r.

Its complete reduction modulo 128, uniformly in B, gives

    beta_r=90 mod 128.

This is computed from the low prefix divided by 2^153. The scalar congruence in
Section 1 retains far more than the 160 global bits needed for this conclusion.

For j=161 the canonical skeleton partition is explicit:

* i=0,...,32 and i=128,...,160: i+256 Z_2;
* i=33,...,127: i+128 Z_2.

These balls partition all 256 residues modulo 256, each exactly once.

Write k_i for the radius exponent and

    d_i = v2(i!)+v2((160-i)!).

On its skeleton ball the upper skeleton S_r=P_161 U_r satisfies

    v2(S_r(x)) >= k_i+d_i,
    v2(S_r'(x)) = d_i.

Since V_r' is a unit, if delta!=d_i the two derivative summands in

    G_r'=S_r'+2^delta V_r'

have different valuations and cannot cancel. If delta=d_i but beta_r is outside
the ball, then v2(V_r(x))<k_i, so the lower VALUE summand strictly dominates
S_r(x); G_r(x) cannot vanish.

Consequently a critical zero can only occur on the ball containing beta_r:

    x=90+128Y.

Here d_90=(90-s2(90))+(70-s2(70))=86+67=153=delta.
This proves that the subsequent local certificate controls the whole domain,
not merely one arbitrarily selected disc.

## 4. The cubic chart has only two possible derivative addresses

After removing content 162, the uniform template on x=90+128Y is

    B*2^-162 G_r(90+128Y) = A_0(Y)+T A_1(Y) mod 2^467.

The complete coefficient certificate shows A_1'=0 modulo 512. Exact residue
evaluation of A_0' modulo 512 leaves, after reduction modulo 256, only

    Y=79 or 221 mod 256.

On 221+256Z_2 the value has exact valuation two for all T: A_0(221) has valuation
two, A_1 is divisible by eight, and integral restricted-series Lipschitz control
makes the shift by 256 invisible modulo eight. Thus that entire ball is root-free.

The remaining address is

    Y=79+256Z,
    x=10202+2^15 Z.

This conversion is exact: 90+128*79=10202 and 128*256=2^15.

## 5. Deep affine parameter certificate

On the remaining ball the entire template is divisible by 2^178. Define

    H_0(Z) = 2^-178(17659 L_0+U_0)(10202+2^15 Z),
    H_1(Z) = 2^-178(2^18 L_0)(10202+2^15 Z).

Both are integral coefficient records modulo 2^451, and

    B K_T(Z) = H_0(Z)+T H_1(Z) mod 2^451,
    K_T(Z)=2^-178 G_r(10202+2^15 Z).

This is a uniform statement for actual integer Euler inputs. Multiplication by
B is a nonzero constant in Z, so it preserves roots and critical zeros.

Each H_i' has even coefficients. Set

    Q_i=H_i'/2 mod 2^450.

The one-bit loss is explicit. The complete coefficient reductions satisfy

    H_0 = 1+Z^2 mod 2,
    H_1 = 1 mod 2,
    Q_0 = Z mod 2,
    Q_1 = 0 mod 2.

More informative low coefficients are

    H_0 = 7+8Z+11Z^2 mod 16,
    H_1 = 13 mod 16,
    Q_0 = 4+11Z mod 16,
    Q_1 = 0 mod 16.

An actual critical zero therefore forces the finite simultaneous system

    H_0(Z)+T H_1(Z)=0 mod 2^450,
    Q_0(Z)+T Q_1(Z)=0 mod 2^450.

## 6. Eliminate the parameter before solving the critical equation

Because H_1 is a unit, eliminate T:

    W(Z) = H_1(Z) Q_0(Z)-H_0(Z) Q_1(Z).

The complete reduction is W=Z mod 2 (in fact W=4+15Z mod 16).
Its derivative is a unit modulo two everywhere. Each simple zero modulo 2^k
has exactly one lift modulo 2^(k+1), by the polynomial Taylor expansion.
Consequently W has exactly one zero zeta_N modulo 2^N for every N<=450.
Then the unique parameter residue is

    tau_N = -H_0(zeta_N)/H_1(zeta_N) mod 2^N.

Equivalently the Jacobian of the pair (H_0+TH_1,Q_0+TQ_1) is the identity
modulo two. Starting from the single solution (T,Z)=(1,0) modulo two, each of
its four possible next-bit pairs contains exactly one solution. This proves
uniqueness over ALL residue pairs, not just along a selected numerical path.

Both methods were implemented independently at the finite system level:

1. enumerate the four possible lifts of the existing pair at every bit;
2. eliminate T, lift W/H_1 as a one-variable rational unit equation, then recover T.

They agree through all 450 bits.

The terminal residue has bitlength 450 and is >=2^449. Thus it cannot equal the
residue of any ordinary T in [0,2^449). A hypothetical exact critical zero would
force precisely that impossible equality. This completes the stated family
nonintersection argument.

## 7. What remains and why this is not universal closure

For arbitrary admissible T in the original progression the proof leaves ONE
residue class modulo 2^450. It does not leave one known exact p-adic parameter,
and it does not identify any actual singular Euler input.

The 629-bit certificate uses a specific finite-template precision ceiling. It
must not be promoted to an exact affine parameter identity. Increasing the
precision beyond that ceiling requires including the changing factorial and
Bernoulli unit corrections, with a fresh proof of the resulting parameter model.

The epsilon-lift distinguishes arithmetic and depleted realizations, but its
vertical transversality alone does not prove their arithmetic nonintersection.
For the fixed chart where it is justified, the dangerous equality remains

    v2(depleted critical value)=2r-25

with exact cancellation of units. The current finite certificate excludes that
possibility for the displayed range WITHOUT asserting a global depleted
parameter function or an arithmetic approximation bound for its root.

Unresolved:

* The retained unbounded terminal-161 parameter class and other unmatched phases.
* The remaining terminal-129 progressions.
* General lower residue polynomials with multiple binary roots.
* Universal simplicity across all positive depths.

## 8. Arithmetic verification and reproducibility

The supplied verifier records 3979 registered exact/modular checks. These are
code-level comparisons, not 3979 independent mathematical theorems.

The checks include:

* Global-first versus local-first coefficient assembly at 272 global bits.
* Cross-precision agreement at 272, 512 and 629 bits.
* Newton versus logarithmic source coefficients, including every coefficient
  at precision 629.
* Exact rational Bernoulli recurrence versus modular unit-binomial evaluation.
* High-index giant-binomial versus unit-binomial routes at smaller check precisions.
* Every binary lifting stage and the independent parameter-elimination method.
* Complete finite carry and skeleton partition interfaces.
* Fresh actual index reconstructions at T=0,1,718787533 and 2^449-1.
* Positive planted singular parameter controls, which remain correctly retained.

The high-index Bernoulli and gamma definitions remain inherited, not wholly
independent mathematical implementations. No Lean compiler, olean build, or
axiom audit was run for these new results.

Execution failures retained:

* Streaming execution was unavailable; the attempted launch started no process.
* A slow global-first 512-bit calculation hit its 60-second time limit.
* An initial local-first 512-bit calculation still constructed huge binomial
  integers and hit 45 seconds.

The completed code separates binomial valuations from odd units and avoids giant
exact binomial numerators. The completed 629-bit construction took approximately
four seconds in this environment. The failed launches are not counted as passes.

All ordinary integer intervals in the theorem are genuine mathematical bounds.
The program did NOT enumerate 2^449 multipliers. The uniform coefficient theorem
and unique residue-lift argument are what supply that quantifier.
