# Komorebi Stratified Universality - Block 04 Progress Note

**Version:** 1.4.0 Block 04  
**Date:** 29 August 2026  
**Manuscript:** *Stratified Universality for Resolved Representations: Finite Profiled Atlases, Effective Descent, and Rational-Mask Digital Realization*

## Block objective

Block 03 established effective descent on a unit purely periodic overlap. Block 04 performs the next bounded step: remove periodicity from the digital and functional-Mahler overlap while retaining explicit normalization, bridge passports, information-loss accounting, higher coherence, object and morphism effectivity, and a named classification target.

## Selected semantic domain

Fix a prime `p`. The semantic category is discrete with objects

\[
F(z)\in 1+z\mathbb F_p[[z]]
\]

whose canonical mask

\[
R_F(z)=\frac{F(z)}{F(z^p)}
\]

is rational. This domain strictly contains the unit-periodic objects of Block 03. For odd `p`, it contains automatic sequences that are not C-finite or eventually periodic.

## Frobenius-radical characterization

In characteristic `p`,

\[
F(z^p)=F(z)^p,
\qquad
R_F(z)=F(z)^{1-p}.
\]

Therefore a unit series has rational canonical mask exactly when `F^(p-1)` is rational. For a reduced mask `R=A/B`,

\[
F^{p-1}=B/A.
\]

Every selected series is algebraic over `F_p(z)` of degree at most `p-1`.

## Rational-collapse obstruction

For every irreducible divisor and the place at infinity, record the valuation of `B/A` modulo `p-1`. The resulting finite-support class vanishes exactly when `B/A` is a `(p-1)`-st power in `F_p(z)`. Hence it vanishes exactly when `F` itself is rational.

Consequences:

- for `p=2`, every rational mask collapses to a rational series
- for odd `p`, nonzero obstruction produces automatic, nonrational, non-C-finite, non-eventually-periodic series
- the unit-periodic atlas is the zero-transient part of the collapse locus

## Canonical Cartier module

For a reduced mask `A/B`, define

\[
D=\max\left\{\deg B,
\left\lceil\frac{\deg A+(p-2)\deg B}{p-1}\right\rceil
\right\}.
\]

The numerator transitions

\[
T_d(P)=\Lambda_d(PAB^{p-2})
\]

preserve the polynomial space of degree at most `D`. The map

\[
\Theta(P)=\frac{P}{B}F
\]

is injective and intertwines `T_d` with Cartier sections.

The canonical Cartier module is the span of the complete `p`-kernel:

\[
\mathcal V_p(F)=\operatorname{span}_{\mathbb F_p}
\{\Lambda_wF\}.
\]

It is finite dimensional, reachable, and observable. It is therefore the unique minimal digit-linear realization up to similarity. Its dimension is the Cartier rank `r_p(F)`.

## Exact reachable compiler core

The fixed-denominator compiler has a sharper structure than the generic finite-automaton reduction:

\[
\mathcal R(A,B)\cong\mathcal K_p(F),
\qquad
W(A,B)\cong\mathcal V_p(F).
\]

Thus:

- reachable numerator states are exactly the canonical `p`-kernel states
- their span is exactly the canonical Cartier module
- reachable numerator states are already behaviorally distinct
- the only deterministic-state loss is removal of ambient states outside the orbit of `B`

The exact hierarchy is

\[
r_p(F)
\leq
\kappa_p(F)
\leq
p^{r_p(F)}
\leq
p^{D+1}.
\]

## Three normalized charts

The verified atlas contains:

1. the reduced rational-mask chart
2. the minimal reachable-observable Cartier-module chart
3. the minimal LSD-first `p`-DFAO chart

All three are equivalent to the semantic category of unit rational-mask series. The ambient polynomial compiler remains a larger directional constructor.

## Coherence and effectivity

Each normalized fiber over a fixed series is contractible:

- the reduced mask is unique
- a Cartier-module automorphism fixing the initial vector and digit operators fixes a spanning set
- a minimal deterministic automaton automorphism fixing the start state and transitions fixes every reachable state

The unique comparison isomorphisms therefore satisfy the triple-overlap coherence law. Compatible local objects and morphisms glue uniquely, giving effective descent.

## Complete descended invariant

The descended package records

\[
\mathcal J_p^{\mathrm{rm}}(F)=
(R_F,\omega_{p-1}(R_F),D(R_F),
\mathcal V_p(F),r_p(F),
\mathcal K_p(F),\kappa_p(F),\mathcal A_p(F)).
\]

The reduced mask reconstructs the formal series through the coefficientwise infinite product. The package is therefore complete on the declared semantic category.

## Exact examples

- `p=3`, `R=1+z`: Cantor-digit indicator, rank 1, two states, noncollapse
- `p=3`, `R=1/(1+z)`: rank 2, four states, noncollapse
- `p=3`, `R=(1+z)^2`: rational alternating collapse
- `p=2`, `R=1/(1+z+z^2)`: finite transient, showing strict extension beyond pure periodicity
- complement Thue-Morse as a unit automatic negative control with nonrational canonical mask

## Exact validation

- 125 reduced normalized masks
- 11,391 exact checks
- 51 collapse masks
- 74 noncollapse masks
- zero failures
- exact finite-field, polynomial, Cartier-transition, and formal-series arithmetic

## Exact boundary after Block 04

Block 04 proves a second heterogeneous effective-descent theorem and includes nonperiodic automatic objects. It does not prove that every automatic sequence has a rational mask, classify all `p`-regular sequences, merge functional and Newton-Mahler theories, or establish a native all-moduli digital invariant.

The next bounded block should address one of two closely related targets: a broader automatic or regular normalization theorem, or a prime-power/local refinement of the rational-mask atlas. The first route attacks the remaining digital boundary directly. The second route adds arithmetic depth while preserving the exact Cartier and polyphase interfaces.
