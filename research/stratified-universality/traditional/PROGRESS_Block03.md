# Komorebi Stratified Universality - Block 03 Progress Note

**Version:** 1.3.0 Block 03  
**Date:** 29 August 2026  
**Manuscript:** *Stratified Universality for Resolved Representations: Finite Profiled Atlases, Effective Descent, and the First Heterogeneous Model*

## Block objective

Blocks 01 and 02 supplied the common resolved envelope, the stratum and bridge interface, higher-coherence bookkeeping, and four obstruction theories. Block 03 carries out the next prescribed step: choose a restricted finite heterogeneous atlas, type every bridge, prove every nonempty multiple-overlap law, and establish effective descent for both objects and morphisms.

## Selected semantic domain

Fix a prime `p`. The common semantic category is the discrete category of sequences

\[
a=(a_n)_{n\ge 0}\in\mathbb F_p^{\mathbb N},
\qquad a_0=1,
\qquad a_{n+T}=a_n
\]

for some positive period `T`. The least period and primitive word are retained as part of the normalized invariant data. The condition `a_0=1` is not cosmetic: it makes the functional-Mahler quotient regular and normalized at the origin.

## Four normalized charts

### 1. Minimal recurrence chart

The linear chart stores the monic minimal recurrence with nonzero constant term and the required initial values. Over a finite field, an invertible recurrence state has a finite cyclic orbit. Conversely, pure periodicity gives the annihilator `E^T-I`. Therefore persistent C-finite sequences and purely periodic sequences coincide on this domain.

### 2. Reduced rational OGF chart

The rational chart stores the unique reduced fraction

\[
F_a(z)=P_a(z)/Q_a(z),
\qquad P_a(0)=Q_a(0)=1.
\]

Pure periodicity is detected by

\[
Q_a(z)\mid 1-z^T,
\]

and the least admissible `T` is the minimal period.

### 3. Canonical digital chart

The digital chart is the canonical least-significant-digit-first `p`-kernel automaton. For a period-`T` word `w`, every kernel state is

\[
b_{u,r}(n)=w_{un+r\bmod T},
\]

with transition

\[
(u,r)\xrightarrow{d}(pu,r+ud)\pmod T.
\]

The pair presentation is finite, and quotienting by equality of subsequence behavior gives the unique reachable minimal automaton.

Writing `T=p^nu M` with `(M,p)=1`, the multiplier orbit has exact size

\[
|U_p(T)|=\nu+\operatorname{ord}_M(p),
\]

using `ord_1(p)=1`. Hence the pair model gives an explicit finite state bound.

### 4. Rational functional-Mahler mask chart

For `F(0)=1`, the unique mask is

\[
R(z)=F(z)/F(z^p),
\]

and

\[
F(z)=\prod_{j\ge0}R(z^{p^j})
\]

coefficientwise. On the selected essential image this is an equivalence with the normalized periodic semantic category.

## Directional compiler lane

A reduced rational mask `A/B` produces a finite Cartier numerator representation. With

\[
D=\max\left\{\deg B,
\left\lceil\frac{\deg A+(p-2)\deg B}{p-1}\right\rceil\right\},
\]

there are at most `p^(D+1)` raw numerator states. This representation is not generally minimal. Reachability and output-equivalence minimization preserve every coefficient and recover the canonical `p`-kernel automaton. The constructor and quotient therefore remain directional with an explicit information-loss statement.

## Coherence and effectivity

Every normalized presentation over a fixed sequence has only the identity automorphism. Each normalized semantic fiber is therefore contractible. This rigidity proves:

- all four triple-overlap comparison diagrams commute
- the two quadruple composites agree
- the higher-coherence defect is the identity

The resulting four-chart pseudofunctor has descent category equivalent to the unit purely periodic semantic category. Local objects glue because their semantic sequences agree. Compatible local morphisms glue uniquely because every normalized fiber is rigid.

## Complete descended invariant

The descended package records

\[
\mathcal J_p(a)=
(T(a),w(a),m_a,P_a/Q_a,\mathcal K_p(a),\mathcal A_p(a),R_a).
\]

The components are connected by exact comparison identities. The primitive period word makes the package complete on the declared semantic category. This is not claimed as a complete invariant for all C-finite, automatic, or Mahler systems.

## Worked models

- the even-indicator word `10` over `F_2`
- the alternating unit word `12` over `F_3`
- the period-three word `110` over `F_2`
- the nonunit word `01` over `F_2` as a negative control outside the regular mask chart

## Exact validation

- 583 primitive unit-periodic semantic objects
- 39,805 exact checks
- zero failures
- all arithmetic performed over prime fields and exact polynomial rings
- theorem proofs remain symbolic and do not depend on the enumeration

## Exact boundary after Block 03

Block 03 establishes a real, but restricted, heterogeneous effective-descent theorem. It closes the existence question for one four-chart atlas spanning finite-linear, digital, and functional-Mahler strata. It does not establish effective descent for the full eight-stratum registry or for nonperiodic automatic and regular sequences.

The next progressive block should widen the digital side beyond pure periodicity while preserving the bridge passport standard. The cleanest target is a finite automatic/rational-mask overlap in which the rational-mask compiler, the canonical `p`-kernel, and a finite linear Cartier representation are compared without assuming periodicity.
