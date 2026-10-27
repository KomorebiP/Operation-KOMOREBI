# Beal research, Block 72
## Higher-precision natural periods and the required valuation coordinate

Release7.2.0,21 September2026. The higher-precision fixed-seven local comparison
is complete through its stated window. It supplies a forced valuation coordinate
for the ACTUAL global upper extension at precisions where that extension exists.

**None of the eight bounded depth-one patterns is eliminated.** Their local lift
spaces are nonempty at the next precision and throughout the guaranteed period
window. The complete reducible branch, full signature, and Beal remain unresolved.
All arithmetic conclusions retain TARGET_CONTRACT.md's actual geometric and
representation hypotheses. No new Lean or independent mathematical reviewer.

## 1. The actual comparison is known beyond the residual level

Put c=v7(C)>=1 and C=7^c C0. The inherited period errors are in1+7^(7c)O_F.
Seventh powering takes1+7^s O_F bijectively onto1+7^(s+1)O_F, so those errors
vanish in F*/F*^(7^j) whenever

    1<=j<=7c-1.

For c=1, this gives the actual period classes modulo7,49,343,2401,16807,117649.
This is the guaranteed precision window, not a claim that the actual errors
become nontrivial immediately afterward.

Let X_j=[phi], H_j=[3], T_j=[7]. These form a THREE-coordinate free Kummer basis:
two unit coordinates and one valuation coordinate. The marked period matrix is

    P_j=Z_j I+2X_j R,
    Z_j=7c T_j+Lambda_j H_j,
    R=[[1,-2],[-2,-1]],
    Lambda_j=7ell_j(C0)-3ell_j(A)-3-5d_j,
    ell_j(a)=log(a^6)/log(3^6) mod7^j,
    d_j=ell_j(5)/2.

Applying the actual Tate-period intertwiner before reduction again identifies the
toric and quotient coefficient actions. Since X_j is primitive, the common
matrix commutes with R modulo7^j. Its trace-zero square-root condition forces
one coherent sign

    S=epsilon R mod7^j.

Thus the actual local scalar extension is

    kappa_j=2epsilon*w X_j+Lambda_j H_j+7c T_j.

This lifts B71's local comparison, not the entire global Tate representation.
Base-field sqrt5 and coefficient-field w remain distinct. See PRECISION_WINDOW.md
and HIGHER_RM_COMPARISON.md.

## 2. At level49, C0 and the valuation term return

Define two different-precision Fermat quotients:

    Q_A=(A^6-1)/7 mod49,   q0=(C0^6-1)/7 mod7.

Exact arithmetic gives

    ell_2(A)=20Q_A+28Q_A^2 mod49,
    [sqrt5]=39[3] in F*/F*49,
    Lambda_2=47+38Q_A+14Q_A^2-7q0 mod49.

Consequently

    kappa_2 = 2epsilon*w[phi]
              +(47+38Q_A+14Q_A^2-7q0)[3]
              +7c[7].

Both the C0-dependent term and7c[7] disappeared at level7; neither may be omitted
at level49. The table covers every294 rational unit A mod343 and42 rational unit
C0 mod49, hence12348 pairs. See LEVEL49_FORMULA.md.

## 3. The ACTUAL global higher extension has a forced valuation coordinate

Let n be the actual depth and m=floor(n/2)+1. The pinned diagonal theorem makes
the SAME global natural representation upper triangular with characters chi and1
modulo7^j for j<=m. Its actual upper entry defines alpha_j. At7, the global
chi-line equals the toric line because the residual cyclotomic character has a
separating inertia element. This equality uses the same primitive natural lattice.

If

    alpha_j|F=U_j X_j+V_j H_j+W_j T_j,

then, in the explicit period window, one unit g_j gives

    U_j=2epsilon*w*g_j, V_j=Lambda_j*g_j, W_j=7c*g_j.

The valuation identity persists even beyond the known UNIT window: the actual
valuation matrix is exactly7cI. Therefore, at every legitimate global triangular
precision j<=m,

    v7_truncated(W_j)=min(j,1+v7(c)).

In particular, when n>=2 the actual alpha_2 exists and

    W_2=7c*v/(2epsilon) mod49.

If7 does not divide v7(C), that coordinate is nonzero. A supposed actual higher
lift that keeps only[phi],[3],[sqrt5] and has no[7] valuation component is impossible
in that case. The actual lift is allowed to contain, and is required to contain,
the coordinate. This is a necessary condition, not an arithmetic contradiction.

Equivalently, a proved zero valuation coordinate would force7^(j-1)|v7(C). No
universal zero-valuation claim or finite-flat hypothesis is inserted. See
ACTUAL_GLOBAL_LIFT.md.

## 4. Why the eight depth-one patterns survive

At n=1, the inherited global triangular precision is ONLY j=1. There is no
supplied global triangular mod49 representation. The local geometric extension
at49 exists, but replacing it with an arbitrary global Kummer lift would erase
the actual lower-left7*beta terms.

For every residual-compatible A and C0, a unit lift of the residual graded gauge
produces a local higher extension matching the residual class. Hence every allowed
A mod49 class admits all seven lifts to A mod343. The complete second-level counts
are

    36*294*42=444528 coefficient/A/C0 inputs,
    116424 compatible local lifts,
    8*12*7*42=28224 augmented bounded pattern/A/C0 choices.

No one of the eight patterns is removed. The larger augmented count is the
addition of new coordinate choices, not an increase in representations or a new
conductor classification. The set of allowed A mod49 is unchanged.

There are7056 distinct(A,C0) pairs underlying the bounded choices. For each, set
C=7C0 and take the unique7-adic fifth root B of C^7-A^3. Hensel gives an exact
primitive local equation. Both algorithms reproduce every B modulo7^18 and agree
on the ordered root-list hash. B is a7-adic root, NOT asserted an ordinary integer.
No common global beta, integer triple, or integral endpoint is constructed.

These positive families show why the attempted elimination by higher LOCAL
liftability alone fails. See LOCAL_LIFT_SURVIVORS.md.

## 5. Negative controls and review

- At c=1, the generic period error1+7^7 is killed through j=6 but not at j=7.
  It does not assert that the actual Jacobian's error has that value.
- An integral square-root matrix congruent to R modulo7 can fail the required
  commutation modulo49. The actual period relation is essential.
- The matrices [[1,1],[0,1]] and [[1,0],[7,1]] preserve the residual natural line,
  but no primitive lift(1,7t) is common invariant modulo49. They are not Frey
  representations; they refute an automatic global-lift shortcut.
- Dropping7c[7] for c prime to7 loses a genuine local obstruction. A positive
  example with A=C0=c=1 has coordinates(3w,3,14), not(3w,3,0), modulo49.
- No full J[7] rationality over F is claimed; F does not contain mu7.

Gregory-Liedtke's printed1906–1908 and Ichikawa's printed4–5 were opened and
visually checked at their primary sources. The general period/Tate functoriality
was authenticated. Its application to the actual marked family remains the stated
inherited conditional geometry. This is not external independent proof review.

## 6. Observed checks and reproduction

The clean default Block71 replay passed before development in24.075 seconds.
It was not a new full historical-chain replay. The observed new primary and
separate scientific runs both passed; the timed development rebuild took9.228
seconds. The immutable archive's fresh replay and audit are recorded externally.
A provisional aggregate tool call timed out without a report and is retained as
incomplete execution, not a pass. The final fresh-extraction run is separately
launched and monitored.

|Finite check|Coverage|
|---|---:|
|Higher unit-coordinate sample cases|1152 at j1–6 in both methods|
|Period/valuation sample cases|1728 in both methods|
|Complete rational(A mod343,C0 mod49) table|12348 in both methods|
|Independent full trace-zero matrix scan mod49|117649|
|Centralizer candidates mod7,49,343|49,2401,117649|
|Complete coefficient/A/C0 inputs|444528|
|Accepted local lifts|116424 in both methods|
|Bounded pattern/A/C0 choices|28224 in both methods|
|Exact valuation/gauge checks|12348 in both methods|
|Separate local Hensel-root certificates mod7^18|7056|

The primary program uses an omega basis, rigorously truncated logarithms and
Newton lifting. The separate program uses a phi basis, multiplicative digit
coordinates, a p-power limit instead of the log series, entrywise centralizers,
and single-digit Hensel roots. Neither imports the other's arithmetic.

The release verifier deletes and regenerates BOTH expected scientific JSONs,
compares their complete contents, checks frozen sources, and requires intended
rejection of altered coordinates, roots, valuations, support counts and payload.
The retained schema-v1 record has explicit input before/after hashes. Its unchanged
project-local v1 validator is identified as such, not as the full plugin validator.
No new Frobenius point counts, Lean compilation, or mathematical reviewer.

## Remaining task

The local fixed-seven calculation is now explicit at higher precision, including
its missing valuation coordinate. At depth one, the next actual comparison must
retain the global nontriangular mod49 deformation and beta. At higher depth,
compare the forced W_j with genuine global/fixed-prime data. Neither task is solved
by freely choosing a lift of the residual three-generator class.

The eight bounded patterns, unrestricted conductor/depth, minus component,
integral global realization, independent upstream acceptance, CM/higher Hilbert
branches, full signature and full Beal remain open.
