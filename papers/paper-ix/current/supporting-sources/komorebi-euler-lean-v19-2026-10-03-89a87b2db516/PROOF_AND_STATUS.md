# Euler Lean XIX: canonical terminal walls and their actual analytic decomposition

**Operation Komorebi — 3 October 2026 — continuation v19**

## Status and proof boundary

This release derives the canonical terminal wall coordinates from the actual
finite global carry minimum and constructs both analytic factors in the wall
identity of the Euler-defined normalized residual. It proves the complete lower
residue polynomial, a pointwise-unit criterion, the corresponding equality-wall
Euler error theorem, and a genuine differentiated wall/Wronskian identity.

There are 83 new theorem/lemma declarations in nine modules. The complete project
contains 566 declarations in 58 mathematical modules. These counts include helper
lemmas and are not counts of novel mathematical results. All 49 inherited
mathematical modules are byte-for-byte unchanged.

The principal new identity, on EVERY dyadic argument, is

\[
G_r(x)=P_{j_r}(x)U_r(x-j_r)+2^{\delta_r}V_r(x).
\]

All objects are constructed from the actual Bernoulli/source packet functions.
Neither a favorable terminal index nor a normal-form hypothesis is supplied by a
caller. The upper and lower series are restricted and integral; the upper series
has complete coefficient reduction one and norm-one values everywhere.

This release does NOT yet formalize the full defect-address classification,
regular-complement theorem for the largest lower address, separating-ball atlas,
or the numerical higher-wall certificates from the research manuscripts. The
upper continuation here starts at the GLOBAL terminal index j_r; it must not be
confused with the smaller active lower address used by the regular-complement
theorem. No universal Euler simplicity, exact critical-scalar nonvanishing,
closed-disc Weierstrass preparation, or larger manuscript coverage range is claimed.

## 1. The inherited Euler-defined objects

D is the actual dyadic integer ring, Lean `ℤ_[2]`, and K is `ℚ_[2]`.
The signed Euler sequence is defined independently by reciprocal cosh and was
identified with its Bernoulli/source reconstruction in v16. The source, kernel,
restricted numerator J_r, field residual H_r, and integral normalized residual G_r
are the unchanged constructed objects from v17/v18.

For r>0,

\[
\alpha_{r,q}=8^q\frac{\beta_{r+q}}{\beta_r},\quad
\lambda_r(q)=v_2(\alpha_{r,q})=3q+s_2(r+q)-s_2(r).
\]

The actual binary digit sum is the sum of `Nat.digits 2 n`, not an axiomatized
complexity function. The inherited finite-minimum construction proves

\[
\mu_r=\min_{q\ge0}\lambda_r(q),\quad
j_r=\max\{q:\lambda_r(q)=\mu_r\},\quad
j_r\le\left\lfloor\frac{s_2(r)-1}{3}\right\rfloor.
\]

In particular EVERY q>j_r has strictly larger cost. The strict final-minimum
property is used, rather than an apparent local carry.

The actual normalized packet sum is

\[
G_r(x)=\sum_{q\ge0}\gamma_{r,q}P_q(x)\mathscr A(x-q),\quad
\gamma_{r,q}=2^{-\mu_r}\alpha_{r,q}.
\]

Each gamma is integral, and the prior construction justifies its evaluation and
all needed convergent rearrangements.

## 2. Binary arithmetic and canonical coordinates

The new binary module proves concatenation, multiplication by a power of two,
and the complement identity from actual base-two digits:

\[
s_2(b2^L+n)=s_2(b)+s_2(n)\quad(0\le n<2^L),
\]
\[
s_2(2^L-1-n)+s_2(n)=L\quad(n<2^L).
\]

For odd b>0 and 0<j<=2^L, it derives

\[
s_2(b2^L-j)+s_2(j-1)+1=s_2(b)+L.
\]

Define canonically, using the actual maximal power divisor,

\[
L=v_2(r+j_r),\quad b=(r+j_r)/2^L.
\]

Lean proves b is a positive odd integer, b2^L=r+j_r, and

\[
\boxed{j_r<2^L,\qquad r=b2^L-j_r.}
\]

Why is the inequality substantive? If j_r>=2^L, the earlier packet j_r-2^L
would have cost lower by 3*2^L+1, contradicting global minimality. The b=1 case
is excluded by r>0. The code implements this contradiction with the proved
binary identities, rather than assuming a small terminal label.

When j=j_r>0, define

\[
e_j(q)=3q+s_2(j-1)-s_2(j-q-1)\quad(0\le q<j),
\quad E_j=\min_{q<j}e_j(q).
\]

The finite lower minimum retains q=0. Lean proves E_j<=0, actual attainment,
and the identities

\[
\lambda_r(q)=e_j(q)\quad(q<j),\qquad
\mu_r=3j+1+s_2(j-1)-L.
\]

Define

\[
L_j=3j+1+s_2(j-1)-E_j.
\]

The Lean definition uses `Int.toNat`; a separate theorem proves the expression
nonnegative and its cast EXACT, so no negative value is silently clipped. Lean
then proves L_j<=L and defines the natural wall distance delta=L-L_j. Hence

\[
\boxed{L=L_j+\delta,\quad \mu_r=E_j-\delta,\quad
r=b2^{L_j+\delta}-j.}
\]

The binary-complexity identity follows exactly:

\[
\boxed{s_2(r)=s_2(b)+3j-E_j+\delta.}
\]

Finally the ENTIRE minimizing set is characterized:

\[
q\in\mathcal I_r\iff q=j\ \text{or}\
(q<j\text{ and }\delta=0\text{ and }e_j(q)=E_j).
\]

Thus positive wall distance leaves precisely the terminal minimizer. At equality,
all lower ties join it. Neither losing the constant tie nor replacing the last
minimum by the first is permitted.

## 3. Shifting past the terminal minimum makes the continuation a unit

For every a,q, the exact cost cocycle is

\[
\lambda_{r+a}(q)=\lambda_r(a+q)-\lambda_r(a).
\]

At a=j_r, the right side is strictly positive for every q>0. Therefore the
ACTUALLY constructed residual at r+j has

\[
\mu_{r+j}=0,\qquad j_{r+j}=0,\qquad \overline G_{r+j}=1.
\]

Set

\[
\varepsilon_r=\gamma_{r,j},\qquad U_r(Y)=\varepsilon_rG_{r+j}(Y).
\]

Lean proves epsilon is integral and odd, U_r is restricted, its ENTIRE series
reduces to one, and every evaluated value has dyadic norm one. In particular it
has no zero on Z_2. The release does not need a separate constructed restricted
inverse to obtain these unit-value and coefficient conclusions.

## 4. The lower prefix has its own arithmetic normalization

Define the lower scalar and lower series by

\[
\eta_{r,q}=2^{-E_j}\alpha_{r,q}\quad(q<j),
\qquad
V_r(X)=\sum_{q<j}\eta_{r,q}P_q(X)\mathscr A(X-q).
\]

The finite sum is over packets, not over Taylor coefficients of the translated
source. Each source remains the actual infinite restricted series.

Lean proves

\[
v_2(\eta_{r,q})=e_j(q)-E_j\ge0,
\]

so every lower scalar is legitimately embedded in Z_2. It constructs V_r as a
restricted integral series and proves its exact evaluated formula. The complete
coefficientwise reduction is

\[
\boxed{\overline V_r(X)=\sum_{q<j,\ e_j(q)=E_j}X^{\underline q}.}
\]

The lower normalizer is E_j, NOT mu_r. The distinction is what leaves the
explicit factor 2^delta in the wall identity.

## 5. Exact wall normal form for the actual Euler function

Apply the inherited convergent numerator block identity at the actual j_r.
Combining the upper and lower constructions with mu_r=E_j-delta gives

\[
\boxed{G_r(x)=P_j(x)U_r(x-j)+2^\delta V_r(x)}
\]

for every r>0 with j_r>0 and EVERY x in Z_2. The Lean theorem is
`eulerNormalizedResidual_terminal_form`.

The identity is stated through genuine analytic evaluation. It does not use an
invalid formal substitution at a nonzero constant in an arbitrary formal series.
All source translations are inherited convergent coefficient constructions.

At each original skeleton integer i<j,

\[
\boxed{G_r(i)=2^\delta V_r(i)}
\]

because P_j(i)=0 exactly. This is a value statement; it does not discard the
nonzero skeleton derivative at that point.

## 6. Pointwise lower units and a completed equality-wall consequence

For j>=2, every falling factorial of degree at least two vanishes at both binary
residue arguments. Consequently

\[
\overline V_r(x)=[E_j=0]+[e_j(1)=E_j]x\quad(x\in\mathbf F_2),
\]

where bracketed conditions are zero/one indicators. The resulting equivalence is

\[
\boxed{V_r\text{ has odd values everywhere}\iff
E_j=0\text{ and }e_j(1)\ne E_j.}
\]

This is pointwise unit behavior. It does NOT assert that the global residue
polynomial must be constant. Under the stronger regularity condition
`0<e_j(q)` for EVERY positive q<j, the code separately proves E_j=0 and the
full coefficient reduction Vbar=1.

At an ACTUAL equality wall delta=0 with j>=2 and the pointwise-unit condition,
P_j also vanishes at every binary argument, and therefore G_r has odd values
everywhere. The end-to-end Euler theorem is

\[
\boxed{
|E_{2N}-T_{r-1,N}|_2=2^{-(4r-1)}\left|\binom Nr\right|_2
\quad(N\ge r).
}
\]

The binomial is nonzero, so these errors are nonzero. In mathematical additive
valuation notation this is 4r-1+v_2(binomial(N,r)). The code's unconditional norm
form avoids confusing mathlib's integer-valued valuation of zero with infinity.

### Concrete all-row example: r=254

A kernel-evaluated finite cost witness proves

\[
(\lambda_{254}(0),\lambda_{254}(1),\lambda_{254}(2))=(0,4,0),
\quad\mathcal I_{254}=\{0,2\},\quad j_{254}=2.
\]

The inherited finite-global-minimum theorem excludes all later packets. Thus
r=254=2^8-2, L=8, E_2=0, delta=0, and the formal all-row conclusion is

\[
\boxed{
|E_{2N}-T_{253,N}|_2=2^{-1015}\left|\binom N{254}\right|_2
\quad(N\ge254).
}
\]

The binary G residue is 1+X(X-1), pointwise one but not a constant polynomial.
This is a genuine multi-packet equality-wall application. It is a new formal
connection, not an increase in the much broader previously proved manuscript
coverage range.

## 7. Genuine derivative and Wronskian transport on the actual wall

Define the exact field function

\[
S_r(x)=P_j(x)U_r(x-j).
\]

Lean proves its `HasDerivAt` statement with the product and chain rules. The wall
identity holds on an open field neighborhood of every dyadic point; differentiating
it is therefore justified, not an operation on a discrete set of integer rows.

\[
\boxed{G_r'(x)=S_r'(x)+2^\delta V_r'(x).}
\]

Define the denominator-free wall Wronskian

\[
\mathcal W_r(x)=V_r(x)S_r'(x)-V_r'(x)S_r(x).
\]

The exact identity is

\[
\boxed{\mathcal W_r(x)=V_r(x)G_r'(x)-V_r'(x)G_r(x).}
\]

Thus W!=0 excludes a critical zero with NO unit assumption on V. The stronger
biconditional requires V_r(x)!=0:

\[
G_r(x)=G_r'(x)=0\iff G_r(x)=\mathcal W_r(x)=0.
\]

The nonzero-lower-value hypothesis is explicit in `terminalWall_critical_iff`.
It cannot be dropped at a common zero of the skeleton and lower residual. No
nonvanishing of W for every Euler argument is claimed here.

## 8. New modules and verification

| Module | Declarations | Role |
|---|---:|---|
| BinaryWallArithmetic | 7 | Actual binary concatenation/complement and wall digits |
| TerminalCoordinates | 9 | Canonical odd multiplier, exponent and lower costs |
| TerminalWallMinimum | 13 | Actual lower minimum, wall origin/distance, complete ties |
| TerminalShift | 11 | Terminal shift is the actual index-zero residual and upper unit |
| TerminalLowerSeries | 12 | Actual normalized finite packet prefix and coefficient residue |
| TerminalNormalForm | 7 | Exact evaluated wall identity and skeleton-point values |
| TerminalResidues | 10 | Full residue, pointwise-unit equivalence, regular lower prefix |
| TerminalSlope | 6 | Actual analytic derivative and denominator-free Wronskian |
| TerminalConsequences | 8 | Sound finite carry witnesses, equality-wall Euler error and r=254 |

The nine modules contain 1,052 lines including definitions and comments. All 58
mathematical modules together contain 6,456 lines.

See `RELEASE_STATUS.json` for the final replay outcomes and measured times. Every
one of the 566 indexed declarations appears in the compiled `#print axioms` audit.
Only Classical.choice, Quot.sound and propext are permitted. The source checker
rejects unfinished proofs, custom axioms and native proof evaluation. The lexical
indexer is a project utility, not an independent Lean parser; its exact list is
compared with the compiler's audit output.

The input v18 archive's manifest verifies 838 entries. All 49 inherited Lean
modules are unchanged. The baseline project was freshly recompiled and audited.
Both final runs start with empty project compiled-output directories; the second
uses a separate source-tree copy. Pinned mathlib dependency caches are reused.
Lean and the whole of mathlib are not bootstrapped from source here.

The new independent standard-library audit passed 393,434 registered checks. These
include actual carry descriptors for every r=1..65536 plus 177 large/adversarial
cases. A successor-valuation recurrence checks the digit-sum cost calculation
independently on a wider finite window. Exact-rational tests include 47 wall
factorizations, upper-unit/lower-integrality checks, 47 error comparisons against
an independently generated cosh-reciprocal Euler recurrence, and seven equality-wall
row laws. Integer-row tests intentionally use nonnegative shifted arguments and
do not differentiate a terminating pointwise identity.

The final clean replays both passed, auditing all 566 declarations in 144.312318
and 128.348827 seconds respectively, excluding runtime restoration. All 60 compiled
`.olean` outputs have identical SHA-256 hashes across the two replays. The only
transitive axioms reported are Classical.choice, Quot.sound and propext. Exact
source and compiled-output hash comparisons are retained in evidence.

The finite tests corroborate the universal Lean proofs; they do not establish
any universal arithmetic scope by extrapolation.

## 9. Remaining formal and mathematical obligations

1. Formalize the defect-address criterion and the largest-active-address regular
   complement. The shifted index-zero continuation proved here is a different,
   simpler shift at the GLOBAL terminal index.
2. Construct the exact separated skeleton balls, their coefficient contents,
   nearest-neighbor factors and full local Euler coefficient certificates.
3. Connect these to the already formalized convergent Hensel and derivative
   modules to transport the larger mathematical atlases into Lean.
4. Formalize further unit-disc preparation and normal-form coordinates where a
   multiple residue survives. Do not substitute origin-adic formal preparation
   for the last-odd-coefficient restricted-series statement.
5. Prove the Euler-specific critical-scalar/Wronskian nonvanishing, or classify an
   exact zero, in the surviving arithmetic progressions. This remains mathematical
   research and is not supplied by compilation.

No all-parameter terminal-degree bound or manuscript binary-complexity bound is
increased by this formalization release.

## 10. Development failures and reproducibility

An early development compile used an incomplete project namespace output directory.
Lean did not search the fallback directory per individual module; copying the
fresh baseline dependencies into the development output corrected the search path.
A diagnostic probe without the required module header ran into the tool timeout;
its corrected module-form probe completed. The probe source is not in the release.
Further development failures concerned actual API names, coercion normalization,
field-valuation rewrites and warnings-as-errors. They were corrected before the
final clean replays. No failed development build is counted as a passed theorem.
The exact-arithmetic audit had no failed assertion.

All diagnostic logs are retained separately from final compilation reports.
The entire incoming v18 ZIP remains unchanged under history/v18.

Use Python 3.10+ and the pinned portable runtime; run with NEW output paths:

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_terminal_alignment.py --max-r 65536 --output /path/to/NEW_terminal_checks.json
```

The Lean pin remains 4.34.0-rc2, with mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Exact dependency and input hashes are in
PROVENANCE.json. Runtime binaries, dependency caches and fonts are not included.

The mathematical wall formulas were previously developed in the research record.
This release kernel-checks their construction from the actual Euler objects. It
makes no historical-priority claim for binary arithmetic, Hensel lifting,
Wronskians, or the specialized Euler formulas.
