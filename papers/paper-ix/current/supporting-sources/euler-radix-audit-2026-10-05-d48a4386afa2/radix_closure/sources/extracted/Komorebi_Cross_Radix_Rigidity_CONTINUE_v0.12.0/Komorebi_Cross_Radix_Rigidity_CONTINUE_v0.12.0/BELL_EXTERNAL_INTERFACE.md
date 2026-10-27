# Bell external interface record — v0.8.0

Checked 2026-09-10 against the primary paper:

Jason P. Bell, *A Generalization of Cobham's Theorem for Regular Sequences*, Séminaire Lotharingien de Combinatoire 54A, Article B54Ap (final version 11 January 2006).

## Exact external boundary

Bell Theorem 1.4: for a commutative ring `R`, if a sequence is `(R,k)`-regular and `(R,l)`-regular for multiplicatively independent positive integers `k,l`, then it satisfies a linear recurrence over `R`.

Bell Theorem 1.5 is stronger but **integer-valued**: an integer-valued sequence is both `k`- and `l`-regular for multiplicatively independent `k,l` iff its generating series is the expansion of a rational function whose poles are all roots of unity.

The v0.8 Lean package does **not** formalize either Bell theorem.  It introduces `BellDownstreamInterface a`, which stores the normalized downstream conclusion needed by Komorebi: after a finite threshold `N`, the complex-valued sequence agrees with a degree-`d`, period-`T` quasi-polynomial residue profile.

The external route from Bell Theorem 1.5 to that interface additionally uses the classical rational-generating-function/quasi-polynomial correspondence.  A checked reference is:

Matthias Beck, Steven V. Sam, Kevin M. Woods, *Maximal Periods of (Ehrhart) Quasi-Polynomials*, J. Combin. Theory Ser. A 115 (2008), 517–525, DOI 10.1016/j.jcta.2007.05.009. Lemma 9 records the pole/root-of-unity characterization for quasi-polynomials.

Because Bell's rational function need not be proper, its polynomial part affects only finitely many initial coefficients; that contribution is represented by the transient `N` coordinates in the Komorebi common hull.

## What is internal after the interface

Once `BellDownstreamInterface a` is supplied, v0.8 retains the v0.7 Lean theorem that every positive affine section `n ↦ m n + r`, hence every depth/address of every positive radix, belongs to one fixed linear submodule `CommonHull N T d`, with

`finrank CommonHull ≤ N + T*(d+1)`.

It also retains positive-affine invariance of `CommonHull` and adds the refined `OrbitCommonHull`, whose tail is the absolute minimal positive-affine profile orbit hull. Under full transient-prefix retention, the refined hull is minimal among positive-affine-invariant sequence subspaces containing the original interface sequence.

## Non-claims

- Bell is not formalized in Lean.
- v0.8 does not prove that an arbitrary complex-valued two-base regular sequence satisfies the interface.
- Bell Theorem 1.4 alone is not being silently strengthened to root-of-unity rationality.
- The normalized quasi-polynomial interface is a downstream contract, not a verbatim restatement of Bell's theorem.
