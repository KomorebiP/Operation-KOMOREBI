# Euler Lean XXII: actual nearest-neighbor cores and an analytic multiplicity ceiling

**Operation Komorebi — continuation v22 — 4 October 2026 (UTC)**

## Status and exact boundary

This release derives the nearest-neighbor factors from the ACTUAL separated
Euler skeleton and its constructed upper/lower analytic charts. The equal-slope
core is handled directly at the skeleton center, without dividing by a
hypothetical lower-root unit. One nearest neighbor forces last odd coefficient
index two. Two nearest neighbors give last odd index zero or one, or exactly one
further division by two exposes last odd index three. All higher coefficients
are controlled by exact formulas, not only by a finite computation.

The analytic capstone applies to every positive first omitted depth r whose
terminal index is at least four and whose carry-defined lower residue has only
simple roots in F_2. The actual normalized Euler function cannot have its
ordinary derivatives of orders 0,1,2,3 vanish simultaneously at any dyadic point.
This is a multiplicity ceiling, NOT a simplicity theorem. Possible double and
triple zeros are not excluded. No new arithmetic nonvanishing statement for the
remaining terminal-129 or terminal-161 progressions is claimed.

There are 67 new theorem/lemma declarations in eight mathematical modules. The
whole project has 794 such declarations in 87 modules; counts include helper
lemmas and negative controls, not independent novel results. All 79 incoming
mathematical modules are unchanged. The initial complete v21 replay passed.
Final clean replay details are recorded below and in RELEASE_STATUS.json.

No general closed-disc Weierstrass polynomial is constructed here. `LastOdd f d`
is the ACTUAL coefficient property: coefficient d is odd and every higher
coefficient is even. The analytic derivative conclusion is proved directly from
that property, so it does not depend on an unformalized preparation step.
No new manuscript terminal-degree or binary-complexity range is asserted.

## 1. Inherited actual objects

D is the genuine ring of dyadic integers (`ℤ_[2]`) and K its field (`ℚ_[2]`).
The independently defined signed Euler numbers, source, kernel, convergent
residuals and carry normalization are the unchanged v16–v21 objects.
For positive r, put j=j_r, mu=mu_r and delta=delta_r. The exact wall identity is

\[
G_r(x)=P_j(x)U_r(x-j)+2^\delta V_r(x),
\qquad
P_j(x)=\prod_{0\le l<j}(x-l)(2x-2l-1).
\]

The terminal index is the constructed LAST GLOBAL minimum of the actual packet
cost, not an arbitrary wall representation. U_r and V_r are the actual infinite
restricted series built from Bernoulli/source packets.

For i<j and j>=2, write

\[
k=k_i=\operatorname{bitlength}(\max(i,j-1-i)),\quad
 d=d_i=v_2(i!)+v_2((j-1-i)!),\quad t=t_i=k+d.
\]

The skeleton ball is i+2^k Z_2. The constructed local upper factor A_i satisfies

\[
P_j(i+2^kY)U_r(i+2^kY-j)=2^tY A_i(Y),\qquad \bar A_i=1.
\]

The v21 localization theorem says that, under `LowerResidueSimple j`, every
critical zero must be on one of at most two such balls with delta=d and
V_r(i) divisible by 2^(k+1). It is a theorem for each fixed actual residual;
no cross-parameter analytic interpolation is assumed.

## 2. A direct centered core avoids a quotient

Suppose delta=d, V_r(i)=2^k w, w is even, and the first evaluated lower Hasse jet
at i is odd. The inherited construction supplies the restricted lower tail

\[
T_i(Y)=\sum_{n\ge0}2^{kn}J_{n+1}(V_r,i)Y^n
\]

and the exact evaluation V_r(i+2^kY)=2^k(w+Y T_i(Y)). It constructs a restricted
integral F with

\[
\boxed{G_r(i+2^kY)=2^{t+1}F(Y).}
\]

At the level of ACTUAL constructed series, not just evaluations at integers,

\[
\boxed{2F(Y)=w+Y\bigl(A_i(Y)+T_i(Y)\bigr).}                 \tag{1}
\]

The new proof retains T_i directly. No lower-root factorization, inverse
lower-root unit, analytic square coordinate, or prepared polynomial is required.

## 3. The exact nearest-neighbor factors

Assume j>=4. Then k>=2. Among other skeleton integers l, the only possible
ones with v_2(i-l)=k-1 are i-2^(k-1) and i+2^(k-1), when they belong to [0,j).
At least one exists. Every other integer factor has valuation at most k-2.

In the normalized skeleton, the two nearest factors are exactly 1+2Y and 1-2Y
up to an odd constant absorbed below. All more distant factors have a slope
divisible by four. The odd companion factors and the actual upper affine
series have the same four-scaled property. Consequently Lean constructs integral
formal seeds E and T such that

\[
\boxed{A_i(Y)=N_i(Y)E(4Y),\qquad T_i(Y)=T(4Y),\qquad E_0\text{ odd},}       \tag{2}
\]

where

\[
N_i(Y)=
\begin{cases}
1+2Y,&\text{only the left nearest neighbor exists},\\
1-2Y,&\text{only the right nearest neighbor exists},\\
1-4Y^2,&\text{both nearest neighbors exist}.
\end{cases}
\]

The seed series themselves need not be restricted. Their rescaling by four is
restricted because every seed coefficient is integral. The coefficient identity
in (2) is what is used in the proof. The odd constant E_0 is not assumed to be
exactly one.

The skeleton construction proves (2) by extracting the one possible nearest
factor from each integer-product side and showing each remaining factor is in
the image of rescale(4). No new factorization hypothesis is added to the final
Euler theorem.

## 4. Complete coefficient identities for the formed half-core

Write E_n=[Y^n]E and T_n=[Y^n]T.

### One nearest neighbor

Let epsilon=1 or -1 denote its sign. Equation (1) gives, for EVERY n>=0,

\[
\boxed{[Y^{n+2}]F=4^n\{2(E_{n+1}+T_{n+1})+\varepsilon E_n\}.}          \tag{3}
\]

The coefficient at index two is odd; every coefficient above it is even.
Thus `LastOdd F 2`. The formula also proves geometric decay independently of
the inherited construction. In particular [Y^m]F is divisible by 4^(m-2) for
m>=2.

### Two nearest neighbors

The symmetric product gives

\[
[Y^2]F=2(E_1+T_1)
\]

and, for EVERY n>=0,

\[
\boxed{[Y^{n+3}]F=2\cdot4^n\{4(E_{n+2}+T_{n+2})-E_n\}.}              \tag{4}
\]

Every coefficient from index two onward is even. Its cubic coefficient has
exact dyadic order one, because E_0 is odd. Therefore precisely one of the
following occurs:

* `LastOdd F 0`;
* `LastOdd F 1`;
* F=2K for a CONSTRUCTED integral restricted K, with `LastOdd K 3`.

In the third case,

\[
\boxed{[Y^{n+3}]K=4^n\{4(E_{n+2}+T_{n+2})-E_n\}.}                    \tag{5}
\]

There is no possibility of another common factor after this division. This is
a theorem about the fully formed sum, not a bound inferred from separately
normalized summands.

The combined exact chart has a last odd index d_*<=3 and removed content either
t_i+1 or t_i+2. In the second case d_*=3. A 'cubic core' here can still have an
infinite analytic tail; the assertion is a complete residue/last-odd statement,
not that the function is literally a cubic polynomial.

## 5. A top-jet obstruction independent of Weierstrass preparation

For every integral restricted f and `LastOdd f d`, Lean proves

\[
\overline{\operatorname{HasseSeries}_d(f)}=1,
\qquad |J_d(f,x)|_2=1
\]

at every dyadic x. Using the previously established all-order analytic
identification,

\[
f^{(d)}(x)=d!J_d(f,x),
\]

it follows that

\[
\boxed{|f^{(d)}(x)|_2=|d!|_2,\qquad f^{(d)}(x)\ne0.}                  \tag{6}
\]

This also covers d=0, when the function is pointwise a unit.

A new all-order affine-chain theorem retains every scale: if

\[
g(a+sY)=c f(Y)
\]

on the dyadic disc, with g and f restricted and a,s,c integral, then

\[
\boxed{s^n g^{(n)}(a+sy)=c f^{(n)}(y).}                              \tag{7}
\]

The proof uses genuine `HasDerivAt` towers and eventual equality in a field
neighborhood, not differentiation of a discrete identity at integer rows.

For s=2^k and c=2^C, both scaling factors are nonzero. Thus the nonzero derivative
from (6) transports back to the ORIGINAL Euler row-offset coordinate. For
example, a one-neighbor half-core has a nonzero second derivative throughout
its candidate ball. The norm identities imply the original orders
v_2(G_r'')=d_i-k_i+2 in the quadratic case and
v_2(G_r''')=d_i-2k_i+3 in the divided-cubic case. These displayed orders are
algebraic consequences of (6)–(7); the Lean capstone is stated as nonvanishing.

## 6. Actual Euler analytic multiplicity ceiling

**Theorem (`eulerResidual_no_orderFour_zero`).** Let r>0, j_r>=4, and suppose
that every binary root of the actual carry-defined lower polynomial is simple.
Then for every x in Z_2,

\[
\boxed{\neg\bigl(G_r(x)=G_r'(x)=G_r''(x)=G_r'''(x)=0\bigr).}          \tag{8}
\]

More literally, the compiled statement negates simultaneous vanishing of
`iteratedDeriv d.val (qeval (eulerNormalizedResidual r hr)) x` for all d:Fin 4.

Proof: a putative four-jet zero is a critical zero, so v21 constructs its
slope-matching aligned skeleton ball. The exact local core from Sections 2–4
has a last odd index at most three. Equation (6) makes that derivative
nonzero, and (7) transports it back, contradicting the corresponding jet zero.

Thus a root under these hypotheses cannot vanish to order four or higher. This
is NOT a universal simple-root theorem. Exact double and triple roots remain
compatible with the generic nearest-neighbor hypotheses, and no general theorem
for multiple LOWER binary residue roots is asserted.

If every slope-equal candidate center in a family has only one nearest neighbor,
Lean similarly proves that derivatives of orders 0,1,2 cannot vanish together.
The formal proof uses the original Euler-defined functions throughout.

## 7. An actual resonant application and necessary negative controls

For actual terminal label 17, the inherited carry calculation gives the lower
polynomial X+1. A kernel-evaluated finite skeleton calculation shows that every
center with slope d_i=11 has only one nearest neighbor.

Therefore EVERY actual terminal-17 residual with wall distance 11 has no
simultaneous analytic zeros of derivative orders 0,1,2.

The explicit positive depth

\[
\boxed{r=2^{64}-17=18446744073709551599}
\]

has j_r=17 and delta_r=11, both verified by kernel-evaluated arithmetic through
the already-proved finite global-minimum bound. This is AT a permitted resonant
scale, unlike the preceding nonresonant example at 2^63-17.

The new end-to-end theorem excludes a triple zero for this actual infinite
Euler residual. It does not assert its root count or exclude double roots.

Two compiled generic identity controls prevent a stronger incorrect inference:

\[
A=1+2Y,\ T=-1,\ w=0\quad\Longrightarrow\quad F=Y^2,
\]

\[
A=1-4Y^2,\ T=-1,\ w=0\quad\Longrightarrow\quad F=-2Y^3.
\]

The first has an exact double zero. After the second's extra division by two,
the core -Y^3 has an exact triple zero. These are synthetic direct-core examples,
NOT Euler residual counterexamples.

## 8. Remaining obligations

The actual nearest-neighbor connection to a quadratic/cubic residue core is now
closed for the stated simple-lower-residue setting. What remains is distinct:

1. Derive and kernel-check the actual high-precision local arithmetic certificates,
   not merely their generic soundness implications.
2. Formalize the full multiplier/distance stability and routing theorem. The
   current global jet bound is for each actual r and does not require, or claim,
   an exact joint analytic interpolation of the undepleted multiplier family.
3. Formalize the carry-address/regular-complement results and additional
   preparation/square/critical-coordinate constructions at persistent residues.
4. Supply the missing Euler-specific critical-value nonvanishing argument, or
   classify an exact zero, in the remaining multiplier progressions.
5. Extend the resolution beyond the simple-lower-residue hypothesis when the
   lower residue itself has a repeated binary root.

The manuscript's all-parameter terminal-degree and binary-complexity bounds are
not increased or relabeled as fully formalized by this release.

## 9. Execution and reproducibility

The incoming v21 archive is preserved unchanged under history/v21. Its manifest
checks 360 entries. Its entire 727-declaration project passed a fresh baseline
compile and transitive-axiom audit before development. The restored compact
runtime archive matched its pinned hash; extraction completed successfully.

Eight new mathematical modules add 67 declarations. All 794 indexed declarations
must appear in each final compiled #print axioms audit. Only Classical.choice,
Quot.sound and propext are permitted. The source indexer is a project lexical
utility, not an independent Lean parser; its list is compared with the compiler's
actual audit output. Lean and the entirety of mathlib are NOT bootstrapped here:
the same pinned dependency cache is reused in both clean replays.

The supplementary standard-library audit passed 99,270 registered checks. It
checked all 18,522 skeleton balls for j=4..192 geometrically, then independently
expanded the original packet polynomial and translated its coefficients on 558
selected balls (full coefficients for j<=32, the first eleven normalized
coefficients for the selected larger examples through j=514). A separate finite
seed calculation checked 768 direct cores: 512 quadratic, 133 affine, 59 constant
and 64 divided-cubic outcomes. It checked 5,376 top-derivative valuations and the
actual terminal-17 integer witness. These finite checks corroborate the universal
Lean proofs; they do not certify a new Euler-family atlas.

### Development failures

Development compilation rejected API-name/rewrite errors, natural-power index
rewrites that changed both sides, insufficiently explicit polynomial-to-series
coercions, constant-coefficient normal forms, deprecated simplifier lemmas, and
an all-order chain-rule rewrite attempted in the wrong expression. All were
corrected before the clean replays. One preliminary inspection looked for a
nonexistent module basename; the actual source file was then inspected.

Failed development logs are retained separately. No failed or partial compile
is counted as an accepted theorem. The supplementary arithmetic audit had no
failed assertion. Final replay status and times are in RELEASE_STATUS.json and
the final record below.

## 10. Reproduction

Use the pinned Lean 4.34.0-rc2 runtime and mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Scientific Python scripts use only the
standard library and require Python 3.10+. Outputs must use fresh paths.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_nearest_cores.py --max-j 192 --trials 256 --output /path/to/NEW_nearest_audit.json
```

The source package omits runtime binaries, dependency caches, compiled project
objects, and fonts. The incoming archive retains its own history and evidence.

## Provenance

The actual source/packet/wall construction and the global slope localization
come from the unmodified v21 modules. The new proof uses the actual pinned
mathlib power-series rescaling, finite-product, dyadic residue, iterated-derivative,
and polynomial APIs. Exact source hashes are retained in PROVENANCE.json.

The nearest-neighbor mathematical mechanism was developed in the earlier research
record. This release kernel-checks its connection to the constructed Euler
functions, using the direct centered Hasse-tail identity. No historical-priority
claim is made for derivatives, Hasse coefficients, local lifting, or the Euler
formulas, and no external theorem is used as an unverified substitute for the
Euler factorization.

## Final clean verification record

All 360 incoming manifest entries matched, and all 79 inherited mathematical
modules are byte-for-byte unchanged. The fresh incoming 727-declaration replay
passed in 222.191646 seconds. The new eight modules contain 871 lines; the full 87
mathematical modules contain 9756 lines, including definitions and comments.

| Final replay | Audited declarations | Seconds |
|---|---:|---:|
| Fresh output directory | 794 | 224.124959 |
| Separate source-tree copy and fresh output | 794 | 221.295191 |

All 89 compiled .olean outputs have identical SHA-256 hashes between replays.
The transitive axiom union is exactly Classical.choice, Quot.sound, propext.
Times exclude runtime restoration and reuse pinned cached mathlib dependencies.
Every module was recompiled in each project replay; no prior project object
was used as the proof of a new module. The restored compiler and dependency
cache itself are not bootstrapped in this procedure.

| New module | Declarations |
|---|---:|
| `DirectCollisionCoefficients` | 12 |
| `EulerCollisionDegree` | 4 |
| `EulerCollisionExamples` | 9 |
| `EulerNearestCore` | 7 |
| `FourScaledSeries` | 12 |
| `LastOddDerivatives` | 6 |
| `NearestNeighborArithmetic` | 5 |
| `NearestNeighborSkeleton` | 12 |
