# Euler Lean XIV: convergent-series evaluation, analytic Hensel lifting, and collision certificates

**Operation Komorebi — 3 October 2026 — continuation v14**

## Status

This continuation closes the generic restricted-series evaluation and simple-root
lifting bridge left open in v13. The new functions are actual convergent sums in
mathlib's dyadic integers. Their first and second derivatives are proved to agree
with the corresponding evaluated Hasse coefficient series, using genuine analytic
derivatives over the dyadic field. Finite coefficient certificates now control
infinite evaluations and all evaluated Hasse jets.

A direct contraction proof lifts every simple binary residue root of an arbitrary
restricted series, with uniqueness on its parity class and a nonzero analytic
derivative. It does not pass through an assumed polynomial approximation or an
unproved Weierstrass preparation. The exact root-distance norm law is also proved.

The v13 nearest-neighbor coefficient identities now imply convergence of their
full formal cores automatically. The terminal-514-shaped root-free/split
certificates and terminal-161-shaped mod-8 no-triple-jet certificate have corresponding
infinite-series consequences, with their coefficient hypotheses explicit.

There are **143 named theorem/lemma declarations in 14 mathematical modules**:
77 inherited and 66 new. The mathematical source contains 1,705 lines including
comments and definitions. Declaration counts include helper lemmas and synthetic
controls; they are not counts of independently novel mathematical results.

This is NOT an end-to-end formal proof of the original Euler source, of a complete
Euler terminal family, or of universal Euler nondegeneracy. No critical scalar is
proved universally nonzero. The remaining bridges are stated in Section 8.

## 1. Objects and convergence

Let D be the actual ring `ℤ_[2]` and Q its fraction field `ℚ_[2]`.
For f in `PowerSeries D`, use mathlib's existing predicate

    Restricted f := PowerSeries.IsRestricted 1 f.

The compiled equivalence `restricted_iff` identifies this condition with

    ||coeff n f|| -> 0.

No evaluation is assumed in that definition. Define

    reval f x = sum' n, coeff n f * x^n       (x in D),
    qeval f x = sum' n, (coeff n f : Q) * x^n (x in Q).

For restricted f, `summable_weighted` proves convergence after ANY integral
coefficient weighting, and `hasSum_reval` gives the actual evaluated sum.
`coe_reval` proves that the D-valued sum agrees with qeval at every integral
argument. No convergence or analyticity of qeval outside D is claimed.

D is open as a subset of Q. This allows genuine Q-derivative statements at every
point of the closed dyadic unit disc, including points of norm one.

## 2. Finite certificates control infinite evaluations

For k>=0 let redPow k be mathlib's genuine ring map D -> ZMod(2^k).
The residue map is proved locally constant and continuous. If p is a polynomial
over ZMod(2^k) and

    redPow k (coeff n f) = p.coeff n  for every n,

then `reval_residue_polynomial` proves

    redPow k (reval f x) = p.eval (redPow k x)

for every x in D.

The proof maps a HasSum through the continuous ring homomorphism and compares it
with the FINITE polynomial sum. No values are sampled. The quantified coefficient
hypothesis includes the complete omitted tail; an unchecked finite vector alone
is not such a certificate.

Define the Hasse coefficient series by

    coeff n (hasseSeries d f) = choose(n+d,d) * coeff(n+d) f,
    rjet d f x = reval (hasseSeries d f) x.

`restricted_hasseSeries` proves convergence for every d. The theorem
`rjet_residue_polynomial` proves the corresponding equality with `hasseDeriv d p`
for every d. In particular finite root-free or simultaneous-jet certificates
transfer to the entire restricted series.

The two congruence theorems in CollisionAnalytic also compare arbitrary restricted
series with each other: coefficient congruence modulo 2^k implies congruence of
evaluations and every evaluated Hasse jet at the same modulus.

## 3. Actual analytic derivatives, not finite differences

The central estimate, proved by an integral monomial remainder and convergent
summation, is

    ||reval f y - reval f x - (y-x)*rjet 1 f x|| <= ||y-x||^2.

There is also the global Lipschitz estimate

    ||reval f x - reval f y|| <= ||x-y||.

The first estimate gives the genuine analytic derivative in Q:

    HasDerivAt (qeval f) (rjet 1 f x : Q) (x : Q).

The HasDerivAt proof works on an actual neighborhood of x in Q, using openness of
the integral disc and the quadratic error estimate after division by ||y-x||.

The Hasse composition identity is proved coefficientwise:

    rjet 1 (hasseSeries k f) x = (k+1)*rjet (k+1) f x.

An eventual equality on an open Q-neighborhood then yields

    deriv (qeval f) x = (rjet 1 f x : Q),
    deriv (deriv (qeval f)) x = 2*(rjet 2 f x : Q).

The second formula is proved with HasDerivAt first, not merely assigned as a
definition. Since Q has characteristic zero, analytic vanishing of value, first
derivative and second derivative forces rjet 0,1,2 to vanish.

All-order evaluated Hasse-certificate soundness is proved. The genuine analytic
derivative identification is supplied through order two in this release; no
all-order iterated-derivative or full analytic translation theorem is silently
claimed from it.

## 4. Direct analytic Hensel theorem

Suppose f is restricted and its full coefficient reduction modulo two is p.
Let a in D satisfy

    p(res a)=0,   p'(res a) != 0.

The compiled theorem `restricted_hensel_simple_residue` proves there is z in D
such that

    reval f z=0,
    res z=res a,
    deriv (qeval f) z != 0,

and z is the unique zero in that parity class.

The proof does NOT apply the polynomial Hensel theorem to a truncation. Let
u=rjet 1 f a, an actual dyadic unit, and contract

    T(x)=x-u^(-1)*reval f x

on the closed complete residue class of a. The derivative residues are constant
there. The quadratic Taylor bound gives contraction constant 1/2, and mathlib's
complete-metric fixed-point theorem constructs the root. Uniqueness is fixed-point
uniqueness. The previously proved analytic derivative formula gives simplicity.

Moreover `restricted_isometry_on_simple_residue` proves

    ||reval f x - reval f y|| = ||x-y||

whenever x,y lie in a parity class on which the reduced derivative is nonzero.
Consequently `restricted_root_distance` gives

    ||reval f x|| = ||x-z||

on the root's parity class. In valuation notation this is the normalized law
v_2(f(x))=v_2(x-z). The actual Lean theorem uses norms, including at x=z.

As an exact corollary, every restricted series whose reduction is X^2+X has
EXACTLY two dyadic zeros, one in each parity class, and both have nonzero genuine
analytic derivative. This permits infinitely many nonzero higher coefficients.

## 5. The nearest-neighbor formal cores now converge automatically

The v13 one-neighbor formula is

    coeff(n+2) H = 4^n*r*(2 e_(n+1) + epsilon e_n).

The v13 two-neighbor formula is

    coeff(n+3) H = 2*4^n*r*(4 e_(n+2)-e_n).

Here e can be ANY formal series over D; it need not be restricted. Integral
coefficients have norm at most one, and ||4||=1/4. These identities therefore
force geometrically decaying tails. `oneNeighbor_restricted` and
`twoNeighbor_restricted` derive Restricted H from the exact half-core identity.
When 2F=H, the corresponding cubic-tail identity proves Restricted F as well.

The upgraded dichotomy includes both restrictedness and the inherited LastOdd
conclusions. LastOdd remains a coefficient predicate; its name is not used to
assume full-disc preparation or multiplicity.

`oneNeighbor_split_of_first_coeffs` is particularly economical. Given the exact
one-neighbor identity, odd r and epsilon, and e_0=1, it needs only

    red(coeff 0 H)=0,  red(coeff 1 H)=1.

The quadratic coefficient and all higher residue coefficients are derived from
the exact formula. Lean then proves the entire infinite core has exactly two
simple dyadic roots. This is a finite input test with a proved infinite tail.

## 6. Infinite-series terminal-shaped certificate applications

`restricted_terminal514_rootfree` takes the complete mod-4 coefficient identity
with

    u X^2 + 3(1+t)X + 2,

where u is odd and t is odd modulo four, and proves no dyadic root exists for
an arbitrary restricted series. The finite no-root calculation is inherited
from the kernel-checked v13 residue proof; the infinite evaluation soundness is
new. A companion theorem discharges restrictedness automatically for a one-neighbor
core satisfying the exact formal identity.

`restricted_terminal161_no_analytic_triple` takes the complete mod-8 coefficient
identity with

    4+(2+6t)X+6X^2+X^3

and proves that the ACTUAL analytic function, first derivative, and second
derivative cannot simultaneously vanish anywhere in D. This is stronger than
v13's polynomial-only soundness statement. No unproved equivalence to an analytic
Weierstrass polynomial is used.

These remain CONDITIONAL ON THE STATED EXACT COEFFICIENT IDENTITIES. We have not
computed/formally derived those identities from the original Euler indices in
this Lean tranche. Therefore their names identify the shape of the certificate,
not a newly established end-to-end terminal-514 or terminal-161 theorem.

## 7. A genuinely infinite synthetic test

RestrictedExamples defines

    f(X)=X+X^2+sum_(n>=3) 4^(n-2)X^n.

Lean proves every coefficient from degree three onward is nonzero, proves
restrictedness, proves its coefficient reduction is X^2+X, and applies the
infinite-series lifting theorem to obtain exactly two simple dyadic roots.

This is a synthetic consistency check, NOT an Euler residual. It demonstrates
that the new theorem is not restricted to polynomials in disguise. The inherited
exact double/triple-root controls remain in NegativeControls and the v13 snapshot.

## 8. What is closed and what remains

Closed in this release:

- Actual restricted-series convergence and evaluation on the dyadic unit disc.
- Coefficient-certificate soundness for evaluations and every evaluated Hasse jet.
- Genuine analytic first and second derivative identities.
- Direct infinite-series simple-root Hensel existence, uniqueness, and root-distance law.
- Automatic convergence of the one/two-neighbor formal cores and their permitted halves.
- Infinite-series soundness for the displayed root-free, split, and no-triple-jet shapes.

Still open as formal construction tasks:

1. Construct the Euler source, beta kernel, H_r and G_r in these types and prove
   their convergence, normalization, source bounds, and actual nearest-neighbor
   identities from the arithmetic definitions.
2. Derive the saved Euler coefficient/parameter certificates formally from exact
   arithmetic data and tail bounds. The generic soundness bridge is now ready;
   the original data-to-coefficients bridge is not silently assumed completed.
3. Prove full analytic affine translation/scaling/Hasse bookkeeping and connect
   all-order multiplicity and LastOdd to the correct restricted closed-disc
   Weierstrass preparation where general root counting still needs it. The local
   ring FORMAL first-coefficient preparation theorem remains a different statement.
4. Construct the exact analytic square or derivative-square charts rather than
   only use the v13 chart implications with supplied hypotheses.

Still open as mathematics:

5. Resolve exact critical-scalar nonvanishing or classify a genuine zero in the
   surviving terminal-129 and terminal-161 integer multiplier progressions.
   The generic analytic lifting theorem only resolves simple residue roots; it
   does not turn an unresolved repeated residue root into a simple one.

No consecutive-degree or binary-digit-sum coverage bound is increased here. Those
prior bounds remain manuscript/computer-assisted results, not end-to-end Lean
corollaries supplied by this package. No universal Euler simplicity, algebraic
squarefreeness, or historical-priority claim is made.

## 9. Execution record

The 59 entries of the incoming v13 manifest matched. The complete inherited 77-
declaration project was compiled and axiom-audited freshly before development.
The runtime was restored from the five visible Compact archives and its combined
archive SHA-256 matched the recorded pin. Runtime binaries are not distributed.

The final project is checked by two clean compilations from distinct fresh output
directories, one of them from a separate copy of the complete source tree. Each
compiles all 14 mathematical modules, the umbrella import, and every indexed
#print axioms command, with one worker and warnings treated as errors. The
machine-readable reports are in evidence/clean_replay_1 and clean_replay_2.

The transitive axiom allowlist is propext, Classical.choice, Quot.sound. A clean
axiom audit does not discharge a theorem's explicitly stated hypotheses.
Pinned mathlib binary dependencies are used; neither all of mathlib nor the Lean
compiler is rebuilt from source in these replays.

Development builds caught ordinary API, notation, coercion, typeclass-instance,
and linter mismatches. For example, tsum_mul_left over the integer ring requires
an explicit summability proof, unlike the division-ring version. Those errors
were corrected; retained development diagnostics are separated from clean replay
logs. No unfinished proof was accepted as a passing declaration. The failed
searches for the runtime were resolved by metadata listing and materialization.
No new Euler-family numerical atlas or arithmetic critical-scalar computation is
claimed in this turn.

## 10. Reproduction and provenance

    python3 scripts/verify_manifest.py
    python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
        --evidence /path/to/NEW_replay_directory

The replay refuses existing evidence/build directories, uses the pinned Lean
4.34.0-rc2 and mathlib revision, and audits all named theorem/lemma declarations.
It does not write the complete process environment into evidence.

The complete unmodified v13 snapshot is in history/v13. The six new modules are
RestrictedEvaluation, RestrictedCalculus, RestrictedHensel, RestrictedJets,
CollisionAnalytic, and RestrictedExamples. The original v12 research note is
retained as reference only; its presence does not mark every claim as formalized.

Mathlib supplies actual p-adic rings and fields, convergence/ultrametric tools,
HasDerivAt/deriv, continuous residue homomorphisms, and the complete-metric
fixed-point theorem used in the direct analytic lifting proof. The mathematical
claims here are evidenced by the Lean source and transitive axiom logs, not by
execution counts alone. No historical-priority review was performed.
