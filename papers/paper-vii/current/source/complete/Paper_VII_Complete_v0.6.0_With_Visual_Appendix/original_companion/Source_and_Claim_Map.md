# Source and Claim Map

## Projector-Resolved Seed Calculus VII
### Quantum Seed Calculus: Symmetry Packets, Circuits, Effective Dynamics, and Quantum Spacetime

Author: Komorebi P.

This document separates the mathematical status of the statements in Paper VII. The paper contains no local bibliography or citation commands. Classical references are reserved for the consolidated end-of-series bibliography.

## Proved within the paper

The following results are proved directly in the finite-dimensional setting stated in the manuscript:

- the orbit-dimension formula for one seed under `M_d(C) \otimes I_m`;
- the finite observable-algebra seed-rank formula;
- the local-orbit/Schmidt-rank corollary;
- generation of the computational basis from `|0...0>` by Pauli-X address operators;
- cyclic character projectors and exact tensor/polyphase refinement;
- the exact circuit packet-path expansion;
- packetwise unitarity conservation;
- exact symmetry-sector invariance for commuting Hamiltonians;
- the commutator leakage bound;
- the moving-frame Hamiltonian with its connection term;
- the canonical connection of a complete differentiable projector family;
- block-diagonal measurement invariance under packet dephasing;
- the exact Schur-Feshbach projected-resolvent identity;
- positivity, self-adjointness, contraction, and composition of finite Euclidean transfer operators;
- the second-order low-mode dispersion bound on the periodic lattice.

## Classical input stated explicitly

The following results are identified as classical input and are not claimed as new theorems of the seed calculus:

- curvature of the projected connection, `F=P(dP \wedge dP)P`;
- the finite Kraus representation of completely positive trace-preserving maps;
- the finite Knill-Laflamme error-correction criterion.

The paper contributes a common packet interpretation and finite verification examples, not historical priority for these classical results.

## Numerical certificates

The implementation supplies deterministic finite certificates for:

- Bell-state preparation and quantum-seed reachability;
- cyclic packet completeness and tensor refinement;
- circuit packet-path reconstruction;
- exact and broken parity dynamics;
- the commutator leakage bound;
- moving-frame correction and the canonical packet connection;
- Bloch-sphere curvature;
- Kraus completeness, output trace preservation, and block-diagonal measurement invariance;
- Knill-Laflamme residual, syndrome completeness, and exact recovery for the three-qubit bit-flip code;
- Feshbach reduction versus bare truncation;
- packet Green blocks;
- lattice-circle dispersion convergence;
- one- and two-dimensional spectral-dimension diagnostics;
- positivity and semigroup composition of a finite Euclidean volume-transfer model.

Numerical certificates verify only the finite models and parameter ranges implemented. They do not prove the continuum conjectures.

## Conjectural statements

The following are presented as conjectures or programmatic targets:

- anomaly-free closure of refined gravitational and gauge constraints;
- cutoff- and volume-uniform Feshbach control;
- Lorentzian reconstruction from a reflection-positive Euclidean tower;
- convergence to the Einstein-Hilbert infrared action;
- emergence of a positive massless transverse-traceless spin-two sector.

No numerical result in the package is represented as a proof of any of these statements.

## Scope boundary

The paper does not claim:

- a solution of quantum gravity;
- an interacting continuum quantum field theory;
- a proof of anomaly freedom;
- a proof of Lorentzian causality or unitarity in a continuum limit;
- a derivation of general relativity from the finite toy models;
- experimental validation of a physical spacetime theory.

Its contribution is a finite projector-resolved quantum calculus, a collection of exact identities, and a sharply delimited continuum research program.
