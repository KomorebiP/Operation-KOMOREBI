# Independent audit of arithmetic nonvanishing attempts

Normalized target: for every ordinary integer T>=0 whose index
r=(17659+2^18 T)2^640-161 has true terminal161, prove that its actual
critical value on x=10202+2^15 Z is nonzero. Equivalently, prove
Phi_r(2^(2r-25)) !=0 in the fixed-r depletion deformation.

Primary verdict: **incomplete, with the smallest missing implication**.
The identities and exclusions reviewed below do not imply this arithmetic
nonintersection. In particular, none proves that the actual depleted
critical value cannot have valuation exactly2r-25 with the required complete
unit expansion. No exact Euler double root has been found.

This is a separate-agent reconstruction from the raw new proofs, code and
outputs. It uses the immutable parent checkpoint for the packet definition,
finite template and fixed-r deformation theorem. The actual packet replay
uses the inherited engine and is not a new Bernoulli implementation.

## Dependency graph

* Signed Euler and rational Bernoulli definitions -> original generating
  functions, packet normalization and terminal valuation formula.
* Terminal valuation formula -> exact binary carry test -> hereditary
  admissibility -> explicit forbidden balls and their topology/measure.
* Midpoint Bernoulli identity -> analytic depleted Bernoulli unit -> exact
  factorial residues -> nonzero residue function -> full-family blow-up.
* Sparse admissible augmentations + finite termination at ordinary argument
  -> identity-theorem obstruction to an analytic full-family extension.
* Euler generating function + convergent Volkenborn expansion -> exact
  source-free interpolation -> arithmetic derivative units and finite
  residual resummation -> two-moment repeated-root criterion.
* Explicit orthogonal generating kernel -> Euler Hankel determinant product.
  There is no proved transfer from this determinant to the residual.
* Exact Bernoulli doubling identity -> weighted cutoff with finite defect ->
  half-shift operator and explicit noncommutative correction. The surviving
  shifted Bernoulli tail is not controlled by the finite g-tail transform.
* Ordinary rational residual values + exact tail EGF -> exclusion of every
  eventual finite polynomial-coefficient linear recurrence over Q or Q2.
* Immutable finite template -> selection of one ordinary T; independent
  actual packet evaluation -> valuation91/unit15mod32 discriminator.

The remaining arrow from any of these conclusions to actual arithmetic
nonvanishing is absent. No circular proof of that arrow was found.

## Audited obligations

| Obligation | Status | Decisive check |
|---|---|---|
| Binary carry criterion | passed | Minimize Md+s2(B+d)-s2(B) by the highest changed bit and set the lower new bits to zero. Integer strictness gives the displayed weak digit inequality. |
| Hereditary admissibility | passed | Internal failing bits persist; a failing top-prefix bit only gains an additional nonpositive carry contribution in an extension. |
| Excluded set and measure | passed | Every failing prefix determines odd d=2^t-b_t and t>=Md+s2(d-1)+1; converse uses the same carry formula. Conditional cylinder measure is2^(1-h). |
| Analytic depleted Bernoulli unit | passed | The 2n-th summand has Gauss valuation at least n+s2(n)-1. The first nonconstant term is -2z. |
| Residue valuations and factorization | passed | Removing the factor2(r+m) leaves denominator valuation q+v2((m-1)!)+v2((q-m)!). Residue ratios have valuation3h+s2(h), giving U_m=1mod2. |
| Whole-family blow-up | passed | Scaled packet valuations are uniformly at least3q+1+s2(m-1), so Gauss-norm dominated convergence is justified. |
| No local analytic extension of full depleted family from admissible integers | passed | Sparse high-bit augmentations remain admissible; evaluate at an ordinary argument in the chart, clear a common denominator with a simple zero, and use the analytic identity theorem. |
| Transfer of the preceding obstruction to scalar critical values | not addressed | Moving critical arguments do not give the finite meromorphic specialization used by that proof. The source explicitly records this distinction. |
| Source-free Euler interpolation and derivative units | passed | Direct binomial expansion of -I((1+4a)^(2s+1))/(2s+1) yields the stated series; omitted m>=2 terms vanish mod16. |
| Finite residual resummation | passed | P_m(s)A(s-m)=P_(m-1)(s)(9^(s-m+1)-1)/8 and P_(r+q)=P_r P_q(s-r) give the exact factors. |
| Two-moment double-root criterion | passed | Differentiation gives Ecal'=-2(Ecal+J1)/(2s+1); at forced skeleton zeros, the required conditions are instead the first and second derivatives of Ecal-S_r. |
| No bounded measure with Euler even moments | passed | Symmetrization gives all Euler moments; the resulting rational Amice transform has a pole at T=-1+i inside the unit disc, contradicting bounded coefficients. |
| Euler Hankel determinant | passed | The explicit two-variable orthogonal kernel is1/(1+zw), so the even-sector monic norms are((2j)!)^2. |
| Hankel nonvanishing implies residual nonvanishing | failed as a proposed direct dictionary | At r=1 the two ordinary evaluations give ratios -2/3 and2/105, so the proposed constant-multiple identification is false. |
| Weighted cutoff defect | passed | The endpoint terms are(1+4^r)a_r, so the first cross coefficient is((2r+4^r)/(2r-1))beta_r and has valuation s2(r)+v2(r). |
| Half-shift continuation and commutator | passed | The analytic square root of9 in1+4Z2 is-3. P_(n-1)(y/2) gives coefficient decay2n+s2(n), and [N,lambda]u=(4/3)s lambda u(s-1/2). |
| Independent nonzero forcing from the half-shift identity | not addressed | The surviving u_r(s-1/2) is not separately determined by the explicit transform lambda u_r-v_r. |
| Weighted nonunit forcing survives uncancelled | refuted | At the first packet,4^r a_r is cancelled exactly by the4^r beta_r/(2r-1) part of C_r(0). |
| Riccati shifted-tail identity | passed | Substitution g=p_r+t^r R_r gives2tR_r'=(1-2r-2p_r)R_r-t^rR_r^2+F_r; its constant forcing also cancels exactly. |
| Newton transfer composition | passed | P_i(x)P_j(x-i)=P_(i+j)(x), and8^(i+j) gives convergent rearrangement, so T_A T_B=T_(AB). |
| Kernel factorization preserves double zeros after transfer | refuted | h=(x-1)^2 has a double zero at1, while T_g h(1)=8/3. |
| Proposed r-dependent nonsquare witness | refuted as a useful test on deep critical cylinders | At x=r+10363, Z=B2^625 has distance valuation2 from c=20mod128, making K(Z) a nonzero square whenever v2(K(c))>=7. |
| No polynomial-coefficient recurrence for G_r(n) | passed | Q2 recurrence coefficients descend to Q by rational finite rank; a recurrence would make the factorially weighted EGF D-finite, contradicting its infinitely many genuine sech poles. |
| Odd valuation/leading-unit exclusion | refuted | The actual admissible index recorded in UNIT_FILTER_RESULT has critical value valuation91 and leading unit15mod32. |
| Index-dependent singularity exclusion | not addressed | The same example has91 vastly below2r-25 and therefore does not test the decisive equality. |

## Important scope details

The full-family extension obstruction uses a power-series analytic family
on a parameter ball, or a local analytic family after shrinking around the
admissible integer. The identity-theorem argument is not an argument about
arbitrary continuous functions on a totally disconnected set. It does not
rule out a separately proved scalar critical-value interpolation.

For clearing denominators at the selected ordinary argument x, a valid
choice is (2r-1)D(r) times the single product of (2r+h), h=1,...,2x.
Its zero at r=-m is simple, so the nonzero residue remains a nonzero value
after clearing. Multiplying all packet denominators together would obscure
this decisive simple-zero property.

The structural Volkenborn functional is bounded in the analytic coefficient
norm being used, not in the uniform norm on every continuous function.
The Amice obstruction concerns a bounded measure on all continuous
functions. These claims are compatible.

The no-recurrence theorem concerns the whole ordinary sequence G_r(n) for
each fixed r. It leaves nonlinear identities, rescaling equations, and
systems with additional transcendental functions untouched.

The half-shift operator is N b(s)=s(b(s)-b(s-1/2)), not ordinary
differentiation. Cancelling each source denominator before extending to the
half-integral coset is essential. It yields exactly
F_r=-(2N+1)M_r+(s9^(s+1)/3)u_r(s-1/2). Changing the analytic square-root
branch to+3 would change this identity and invalidate the computation.

The unit-kernel identities are translated through operator composition,
not pointwise multiplication. The exact8/3 example is an obstruction to
zero descent, not an Euler counterexample. The square-test argument uses
the actual critical value K(c), not an unlabelled substitution of the
depleted value. The unit/parity example happens to agree with the depleted
value far beyond the precision used.

## Finite evidence and reproducibility

The new unit discriminator was replayed and its JSON agrees exactly with
the recorded output. Separate code in `independent_checks.py` directly
minimized the terminal valuations through q=231, recovered mu=-154 and
j=161, lifted the stationary point by Newton iteration rather than the
author's joint bit search, and recovered the value15*2^91 modulo2^96.
The recorded actual reconstruction has142 normalized value bits,141
stationary bits, a scalar cutoff286 and83 nonzero localized packets.
Since178+2*141>320, stationary evaluation retains all320 raw value bits.

The carry controls replayed:5120 direct carry cases,41327 hereditary prefix
checks and160 forbidden-neighborhood checks, plus the stated pole controls
for m=1,...,4. The review independently rechecked5120 carry cases with a
different direct minimization formulation. These checks corroborate the
proof; they do not prove the unbounded statements by exhaustion.

The structural controls replayed:31 Volkenborn values,31 source-free values,
31 original reconstruction values,444 residual identities,169 orthogonality
pairs and7 Hankel determinants. All use exact integers and rational
fractions. Their full JSON agrees with the recorded run.

The weighted-tail replay passed33 coefficient checks,360 cutoff coefficient
checks and276 half-shift evaluations. The recorded branch is the negative
square root. Its complete JSON agrees with the original bounded run.

The unit-kernel checker independently constructs beta by reciprocal-series
inversion of(sinh(z)/z)^2. Its replay passed31 unweighted and31 weighted
coefficient identities,187 weighted tail identities,187 Riccati tail
identities and11 exact first-packet cancellations. The negative control
without C_r gives-17/45 at r=2 instead of the actual beta_2=1/15.
Scientific output agrees with the recorded run after removing elapsed time.

Current manifest roots:

* `root/unit_filter_run/manifest.json`: workspace root.
* `carry_nonintersection/certified_run/manifest.json`: workspace root.
* `structural/certified_run_final/manifest.json`: structural directory.
* `structural/weighted_run/manifest.json`: structural directory.
* `unit_identity/certified_run/manifest.json`: workspace root.
* `review/certified_run/manifest.json`: workspace root.

The earlier structural `certified_run` is historical because the author
added notation clarifications afterward. Its successor pins the final
proof. Do not classify the older proof hash as a current validation failure.

Development-only review failures: the first review-runner invocation omitted
required explicit input arguments and was rejected before execution; the
corrected run succeeded. Initial manifest validation used the wrong roots
for two independently packaged runs. Revalidation with the documented roots
succeeded. No failed mathematical check was converted into a passing result.

## Exact remaining gap

One must exclude simultaneous cancellation and stationarity for the actual
Bernoulli coefficients, with the ordinary index retained in the required
valuation equality and all higher unit digits. The full Euler derivative
units disappear after subtracting its prescribed prefix. The nonzero
Hankel determinant concerns a different remainder. Pole residues control
negative-parameter singular behavior but do not constrain the regular
part enough to exclude positive-parameter double roots.

The strongest safe conclusion is the collection of proved identities,
precise route obstructions and the finite counterexample to a proposed
unit/parity shortcut. The parent universal simplicity theorem and the
focused arithmetic nonvanishing target both remain open.

No Lean compilation was performed. `SOURCE_HASHES.json` pins the exact
proofs, code, outputs and inherited dependencies reviewed here. The cheapest
useful next check must test a proposed strict valuation separation for the
actual transformed remainder; adding parameter digits alone would not
resolve any of the missing implications identified in this audit.
