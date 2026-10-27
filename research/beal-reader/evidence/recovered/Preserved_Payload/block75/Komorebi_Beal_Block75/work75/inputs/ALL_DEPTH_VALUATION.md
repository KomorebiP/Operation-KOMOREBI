# B74.3. An all-depth mixed-trace valuation

Let c=v7(C)>0, t=1+v7(c), c*=c/7^(t-1). Fix j>=n+t+1 and the probe tau_j from
B74.1. Let g in ker rhobar with beta(g)!=0. With T and D as in TRACE_EXTRACTION.md,

    BOX: v7(D(tau_j,g))=n+t=n+1+v7(v7(C)).               (7)

The leading coefficient is

    D(tau_j,g)/7^(n+t)
       = c* * v/(2epsilon) * beta(g) mod7.              (8)

This result does not bound n or c. It identifies an exact mixed trace valuation
that every actual representation with the stated geometry must have.

## Proof

From(4), D=7c*tr(J(rho(g)-I)) modulo7^j. Let V=rho(g). Since g is in the residual
kernel, all entries of V-I are divisible by7. The global natural depth further gives

    V21=7^n beta(g) mod7^(n+1).

The diagonal terms of J(V-I) have valuations at least n+1 except for the term
J12 V21. The J21 V12 term has valuation at least2n+1. Hence

    tr(J(V-I))=7^n kappa beta(g) mod7^(n+1).

Multiplying by7c=7^t c* proves(8). All factors on its right are nonzero, so the
valuation is exactly n+t, proving(7). The precision j ensures that the displayed
leading digit is not hidden by truncation. No unknown next digit can cancel it.

## Comparison with prior results

The general matrix expression for J keeps its nonzero diagonal and lower entries.
They are not literally deleted: their orders are high enough to drop from the
particular leading trace coefficient. All6480 finite family members test this
with nonrational coefficients and nontrivial toric diagonal terms.

The all-depth formula requires a higher probe precision as n+t increases.
At depth two with c prime to7 the signal first appears at7^3, and a modulus343
observation alone is zero. It must not be interpreted with the depth-one denominator49.
The construction needs the actual split toric valuation lattice and its alignment,
not an arbitrary representation having the same characteristic polynomials.
