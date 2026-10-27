# Euler XXVI: a scale-sensitive cubic jet obstruction

Operation Komorebi — 4 October 2026

## Scope

The new Lean results concern the actual infinite analytic class

\[
 F(X)=a+bX+cX^2+uX^3+4\sigma X^4R(X),
 \quad a,b,c,\sigma\in\mathbf Z_2,\quad u\in\mathbf Z_2^\times,
 \quad R\in\mathbf Z_2\langle X\rangle.
\]

The multiplier of an Euler wall is denoted B below, not b. The tail-scale
parameter sigma is not the wall distance. It may be zero; the norm theorems
include that case without dividing by it.

The new invariant uses the exact inflection point already constructed in v25:

\[
 F''(\rho)=0,\qquad A=F'(\rho),\qquad C=F(\rho),
 \qquad v=J_3(F,\rho)=F'''(\rho)/6.
\]

Here v is a unit and is the cubic Hasse coefficient at the actual center rho.
It is not in general the original coefficient u at zero.

Define

\[
 \mathfrak D=4A^3+27vC^2.
\]

This is a **jet obstruction**, not the exact discriminant of a prepared
Weierstrass polynomial for the infinite function. Nonzero mathfrak D alone
does not exclude a repeated root. The proved bound below is indispensable.

The release adds 27 theorem/lemma declarations in six modules. All 104 inherited
mathematical modules are unchanged. The cumulative count is 950 declarations in
110 modules. Counts include helper lemmas and controls, not 950 independent
novel results. Verification receipts are in RELEASE_STATUS.json.

No new infinite multiplier family, terminal-degree bound, binary-complexity
bound, universal Euler simplicity, or historical-priority claim is made.

## 1. Integral third-order Taylor control

For any integral restricted series f and x,y in Z_2, the new proof gives

\[
 \left|f(y)-f(x)-(y-x)J_1(f,x)-(y-x)^2J_2(f,x)
 -(y-x)^3J_3(f,x)\right|_2\le |y-x|_2^4.
\]

The proof constructs fourth-order divisible remainders for each monomial,
then sums them using the inherited convergence theorems. It does not assume
an Archimedean Taylor remainder formula over Q_2.

A separate lemma constructs an integral quotient whenever |a|_2 <= |b|_2:
there exists q in Z_2 such that a=bq. The zero divisor case is handled
explicitly. This converts analytic error bounds into exact algebraic identities.

Lean: ThirdOrderRemainder.lean.

## 2. Exact critical data, with the tail scale retained

Let alpha be any actual critical point, h=alpha-rho. There exist integral e,f
such that

\[
 A=-3vh^2-4\sigma h^3e,
\]
\[
 C-F(\alpha)=2vh^3+4\sigma h^4(e-f).
\]

These are exact statements about convergent evaluations and genuine analytic
derivatives. They follow from the third-order Taylor remainder of X^4R and the
second-order remainder of its derivative, together with F''(rho)=0 and
F'(alpha)=0. The nonzero displacement assumption is NOT necessary.

The Hasse-composition identity J_2(f',x)=3J_3(f,x) is proved in the new module.
The complete coefficient computation also proves v=u+4sigma J_3(X^4R,rho),
hence |v|_2=1.

Lean: CubicUnitObstruction.lean; ScaledCubicUnitObstruction.lean.

## 3. The discriminant cancellation retains an extra ideal factor

If alpha is also a zero, then

\[
 \boxed{
 \mathfrak D=16\sigma h^7
 \left[-27v^2f+9v\sigma h\bigl(3(e-f)^2-4e^2\bigr)
 -16\sigma^2h^2e^3\right].
 }
\]

The bracket is integral. Therefore

\[
 \mathfrak D\in16\sigma h^7\mathbf Z_2.
\]

The inherited v25 identity |A|_2=|h|_2^2 at a critical point yields

\[
 \boxed{|\mathfrak D|_2^2\le
 \frac1{256}|\sigma|_2^2|A|_2^7.}
\]

Consequently

\[
 \boxed{|\mathfrak D|_2^2>
 \frac1{256}|\sigma|_2^2|A|_2^7
 \implies F\text{ has no critical zero in }\mathbf Z_2.}
\]

This is the formal capstone, including all infinite-tail effects.
For nonzero sigma,A,mathfrak D, the equivalent sufficient valuation inequality is

\[
 2v_2(\mathfrak D)<8+2v_2(\sigma)+7v_2(A).
\]

At a possible repeated root with d=v_2(h), one necessarily has

\[
 v_2(A)=2d,\qquad v_2(C)=1+3d,
 \qquad v_2(\mathfrak D)\ge4+v_2(\sigma)+7d.
\]

The formal norm statements avoid totalized-valuation conventions at zero.
The displayed valuation translations assume the mentioned quantities nonzero.
When sigma=0, the exact polynomial discriminant condition is recovered.

## 4. Odd-unit information on the former equality boundary

Suppose v_2(A)=2d and v_2(C)=1+3d, so the v25 norm test is inconclusive.
Write

\[
 A=2^{2d}A_0,\quad C=2^{1+3d}C_0,
 \quad \sigma=2^s\sigma_0
\]

with A_0,C_0,sigma_0 odd. A repeated root now requires

\[
 \boxed{A_0^3+27vC_0^2\equiv0\pmod{2^{2+s+d}}.}
\]

Thus matching the valuations is not enough. The normalized units must satisfy
an increasingly precise congruence.

For the tested Euler cores, sigma=2 and d=0. The necessary congruence is modulo 8.
Since an odd square is one modulo 8 and an odd cube equals its base modulo 8,
this becomes

\[
 \boxed{A\equiv5v\pmod8.}
\]

This translation is an elementary consequence of the formal divisibility
identity. No exact critical point is numerically presumed.

## 5. Finite certificate soundness

For the unscaled class (sigma=1), every critical zero forces mathfrak D=0
modulo 16. The new soundness theorem accepts a COMPLETE coefficient reduction
p in (Z/16Z)[X]. If every zero of its second Hasse derivative has nonzero

\[
 4(p^{[1]})^3+27p^{[3]}p^2
\]

modulo 16, the entire infinite core has no critical zero.

The concrete polynomial

\[
 p=12+5X+10X^2+11X^3+8X^4
\]

has that property. Its second Hasse derivative is 10+X modulo 16, so its only
inflection residue is 6. Its jet obstruction there is 8 modulo 16.
The finite check is performed by Lean kernel evaluation. The soundness theorem
applies to every infinite core satisfying the complete coefficient certificate.

The original Euler index-to-coefficient assertion for this particular polynomial
is still supplied by separately checked modular reconstruction, not a new
end-to-end Lean arithmetic computation.

Lean: CubicUnitCertificates.lean.

## 6. Euler chart connection

The inherited Euler construction produces two-neighbor cubic cores. Once a
specific tail scale and coefficient certificate are supplied, the new theorem
transports the scaled discriminant gap through the exact chart

\[
 G_r(i+2^{k_i}Y)=2^{t_i+2}F(Y)
\]

to absence of a critical zero of the original Euler residual on that ball.
Neither a favorable scale nor a favorable arithmetic gap is silently inferred.

The actual core coefficient theorem gives |a_n|_2 <= 2^{-(2n-6)} for n>=4.
In particular, all coefficients n>=5 are divisible by 16. Therefore a verified
modulo-8 statement for coefficient 4 suffices to establish the stronger exact
tail class 8X^4R for those Euler cores. It is not necessary to infer an infinite
tail statement from the length of a numerical coefficient vector.

Lean: EulerCubicUnitBridge.lean. The numerical coefficient lifting of the
specific extra factor is documented in the finite arithmetic records.

## 7. Sharpness and negative control

For any h, consider the synthetic polynomial

\[
 F_h(x)=2h^3+12h^4+(-3h^2-16h^3)x+x^3+4x^4.
\]

Exactly

\[
 F_h(x)=(x-h)^2\left(4x^2+(1+8h)x+2h+12h^2\right).
\]

The inflection center is zero, and the jet obstruction is

\[
 \mathfrak D_h=-16h^7(27+333h+1024h^2).
\]

For nonzero even h, the bracket is odd, so

\[
 v_2(\mathfrak D_h)=4+7v_2(h).
\]

This is EXACTLY the threshold that the strict inequality excludes.
In particular, at h=2,

\[
 F(x)=208-140x+x^3+4x^4
 =(x-2)^2(4x^2+17x+52),
\]

and

\[
 \mathfrak D=-9807872=-2^{11}\cdot4789\ne0.
\]

Lean proves the polynomial identities and the actual analytic critical zero
at x=2. The higher term permits a repeated root despite a NONZERO cubic jet
discriminant. This is not an Euler counterexample. It demonstrates why simply
checking mathfrak D != 0 would be unsound for infinite series.

Lean: CubicUnitSharpControls.lean.

## 8. Fresh fixed-index arithmetic results

The four tested actual Euler depths are

\[
 r=B2^{640}-161,\quad B\in\{3,7,11,15\},
 \quad j_r=161,\quad\mu_r=-154.
\]

The local coordinate is x=90+128Y and coefficient content is 162. Original
packet/source reconstruction is performed at 256 global bits, leaving 94 local
bits. An alternative reconstruction uses 288 global bits, leaving 126 local bits.
All four have exact higher-coefficient scale at least eight, with degree-four
coefficient of exact valuation three. Thus sigma=2 is justified for each.

| B | v2(A) | v2(C) | v2(mathfrak D) | v25 norm test | New scaled test |
|---:|---:|---:|---:|---|---|
| 3 | 0 | 1 | 3 | inconclusive | passes |
| 7 | 1 | 4 | 5 | passes | passes |
| 11 | 0 | 1 | 4 | inconclusive | passes |
| 15 | 2 | 2 | 4 | passes | passes |

For B=3 and B=11, the centered cubic jet is v=3 modulo 8. The slope A is,
respectively, 1 and 3 modulo 8. A repeated root would require A=7 modulo 8.
Both fail that necessary condition. This explains why the previous norm-only
balance missed the conclusion.

These are fixed-input applications. They do not classify an infinite multiplier
progression or enlarge a manuscript coverage bound. Those fixed inputs were
already studied in older atlases; the gain is a smaller discriminating invariant.
No claim that the large original-index coefficient calculations are Lean proofs
is made here.

The two reconstruction routes differ in their source expansions, scalar
factorial decompositions, and localization algorithms. Binary and Newton lifting
independently recover the same inflection residues. Shared components remain:
the modular Bernoulli evaluator and polynomial multiplication. Low-index
Bernoulli residues are independently compared with exact rational recurrence.

### Named frontier stress test

The additional fixed multiplier B=17659 was recomputed at 224 global bits on
the same full cubic ball. It has v2(A)=0, v2(C)=1 and v2(mathfrak D)=5, with
sigma=2. This is EXACTLY the new threshold: 2*5=8+2*1+7*0. The strict test is
inconclusive. No exact zero is inferred, and previous finer fixed-instance
classifications are not reversed. The test still leaves the corresponding
infinite arithmetic progression unresolved.

## 9. Execution and formal boundary

All 1097 incoming manifest entries matched, and the full 923-declaration baseline
was freshly compiled and axiom-audited. All 104 inherited mathematical modules
are unchanged. New replay commands, source hashes, axiom lists and timings are
recorded under evidence/v26_replay_A and evidence/v26_replay_B; see RELEASE_STATUS.json
for final verified totals.

The allowed transitive axiom union is Classical.choice, Quot.sound, propext.
No custom mathematical axiom, unfinished proof, native-evaluation proof axiom,
or unverified computational shortcut was introduced.

Development failures were an unsupported streaming launch, an early compile
before its imported baseline module was available, and ordinary rewrite,
coercion, and linter mismatches. They were corrected. Numbered development logs
are retained rather than overwritten. No incomplete run is counted as passed.

The final sources contain no proof of universal Euler simplicity. The critical
scalar questions in the remaining terminal-129 and terminal-161 progressions
remain open. Lower residue polynomials with multiple roots also retain their
previous boundary.

The new endpoint is a quantitative necessary ideal condition at every repeated
zero of the infinite cubic class. It preserves both odd-unit information and the
actual higher-coefficient scale. Failure of that condition is a finite,
checkable certificate of nondegeneracy.


### Final fresh receipts

- Incoming baseline: 275.624946 seconds, 923 audited declarations.
- Clean A: 327.392024 seconds, 950 audited declarations.
- Clean B: 326.057321 seconds, 950 audited declarations, separate source copy.
- All 112 compiled .olean files and all 950 transitive-axiom records agree.
- Generic exact checks: 2318.
- Four fresh original-index constructions at 256 bits: 228 registered checks.
- Four alternative constructions at 288 bits: 244 registered checks.
- Cross-reconstruction comparisons: 220.
- Additional B=17659 stress test: completed, criterion inconclusive.

The fixed-input computation counts are not combined with inherited v25 counts.
The two final replays ran concurrently with one worker per compiler process,
using the pinned cache. Runtime restoration and numerical tests are outside their
timings. Scientific arithmetic was exact rational/integer or modular arithmetic;
floating point was used only for elapsed-time metadata.
