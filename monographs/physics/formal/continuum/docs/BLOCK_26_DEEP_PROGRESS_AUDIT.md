# Komorebi Physics v0.26.0 — deep progress audit

## Executive assessment

Block 26 is the first checked layer in the project where the refinement coordinate is not merely a spectator.  The new fine site lies on the coarse edge, a coarse translation takes two fine translations, and the midpoint field is fixed by gauge parallel transport.  This converts the prior exact refinement architecture into an actual local geometric statement in one direction.

The key advance is not simply the identity `halfShift² = coarseShift`.  The exact theorem combines four structures at once:

1. geometric edge subdivision;
2. ordered `U(1)` sublink composition;
3. nontrivial Clifford-projector transport;
4. measure-correct Hilbert interpolation.

The block also identifies a precise limit on exactness.  Independent directional interpolations cannot be combined globally without accounting for loop holonomy.  Flat plaquettes permit path-independent corner values.  Nontrivial plaquettes force different transported states, and the release contains a checked witness with holonomy `-1`.

## From Block 25 to Block 26

Block 25 proved an exact tower on `Site × Fin 2`, with the child coordinate ignored by lifted translations.  Its value was architectural: exact evolution/refinement commutation and exact Hilbert normalization.  Its limitation was geometric: the physical step size did not change.

Block 26 replaces one coarse edge by two sequential subedges.  The fine midpoint is physically distinguished by the first half-link.  The coarse link is not copied; it is reconstructed as the ordered product of fine links.  The fine shift therefore executes the same transport in two local operations.

## Exact directional theorem

Let `u` be a coarse link and let `S.first`, `S.second` satisfy

`S.second x * S.first x = u x`.

Let `I_S` place `ψ x` at the endpoint and `S.first x • ψ x` at the midpoint.  Then for every Clifford involution `A`,

`S_fine(A)² I_S = I_S S_coarse(A)`.

The source defines the difference as an `intertwiningDefect` and proves it identically zero.

## Hilbert theorem

Interpolation creates two representatives of every coarse cell, so raw counting measure produces a factor of two.  The release proves that factor rather than suppressing it.  Multiplying the fine sum by one half gives an exact isometry.  The averaging restriction combines the endpoint and back-transported midpoint, and the adjoint identity is checked directly.

This supplies a well-defined covariant projection onto the coarse-interpolated subspace.

## Local dynamics

The one-axis symmetric walk `M-S-M` is refined factorwise.  The local operator `M` is supplied with an exact half-step square root and the directional shift is split into two geometric substeps.  The entire refined walk exactly intertwines with the coarse walk and preserves the half-cell Hilbert product when the local steps carry their Hilbert certificates.

Concrete spectral phases of the Hermitian beta involution provide an explicit massive instance.

## Curvature as obstruction

For two directions, the two paths to a corner differ by the plaquette ratio

`Ω = P_xy / P_yx`.

The release proves:

- `Ω = 1` iff path phases agree;
- `Ω` is gauge invariant when the translations commute;
- the two transported nonzero spinors agree iff `Ω = 1`;
- an explicit finite configuration has `Ω = -1`.

This changes the next research problem.  The goal is no longer to force exact simultaneous interpolation unconditionally.  The correct next theorem must separate:

- a flat sector with exact three-axis compatibility;
- a curved sector with a defect determined by holonomy.

## Formal verification

The release has 125 active mathematical modules, 2,209 theorem declarations, and 2,718 audited declarations.  Block 26 adds 45 theorems among 76 declarations.  All 124 v0.25 mathematical modules are byte-identical to the checked parent.  The new module and cumulative import compile with warnings treated as errors.  All new declarations were subjected to `#print axioms`; only standard imported dependencies were observed.  Three deliberately false statements were rejected for their intended mathematical reasons.

## Remaining gap to the physical thesis

The project now has a checked local geometric refinement mechanism, but not yet a completed local-discrete/global-continuous physical theory.  The next decisive steps are:

1. construct a three-dimensional refined cell;
2. derive a flat exact theorem and a curved holonomy-dependent defect theorem for the full spatial sequence;
3. prove scale decay or summability of that defect;
4. reconstruct into a continuum Hilbert space;
5. prove convergence to the continuum Dirac evolution;
6. make the gauge links dynamical rather than fixed background data.

Block 26 therefore closes the first geometric edge problem and isolates curvature as the next load-bearing obstruction.
