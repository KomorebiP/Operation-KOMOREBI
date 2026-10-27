# Strong Artin live checklist after v0.16

Status meanings: `[x]` closed at the stated boundary; `[~]` active; `[ ]` open; `[E]` external/imported only in a declared range.

## Previous finite/cyclic and auxiliary-selection core

- [x] prime-cyclic extension torsor and residual collapse;
- [x] exact cyclic defect algebra and generic branch action;
- [x] twist-stable support propagation;
- [x] cyclic/transverse first-order obstruction splitting;
- [x] centered spectral-projector detection;
- [x] finite-group `H¹` averaging and cyclotomic-depth survival;
- [x] projector-detected pre-Chebotarev element;
- [x] adaptive exact finite auxiliary-set selection (v0.15).

## Jacobian bridge — v0.16

- [x] define the dual obstruction space as `ker J.dualMap`;
- [x] represent each auxiliary condition by a Jacobian column;
- [x] prove joint dual detection implies augmented-map surjectivity;
- [x] combine with v0.15 to select exactly the dual-obstruction dimension many admissible columns;
- [x] conclude the selected augmented Jacobian is surjective.

## Finite quotient and Chebotarev-class algebra — v0.16

- [x] prove a coprime auxiliary kernel still surjects onto the residual quotient;
- [x] specialize to finite `p`-group splitting/cyclotomic labels;
- [x] lift every residual class into the common splitting-label kernel;
- [x] construct the affine semidirect-product group of cocycle values and residual labels;
- [x] package a normalized cocycle as a group homomorphism;
- [x] combine cocycle and finite splitting labels in one finite quotient range;
- [x] prove the quotient map is surjective by construction;
- [x] prove the matrix cocycle conjugation formula;
- [x] prove commuting-projector detection is conjugacy-class invariant;
- [x] tie the selected projector to its actual residual Frobenius element;
- [x] construct an indexed Chebotarev-ready conjugacy class.

## Local linear Taylor--Wiles interface — v0.16

- [x] define the Frobenius coboundary map `1 - Ad(A)`;
- [x] prove a projector commuting with `A` kills its range;
- [x] descend the trace probe to the quotient by Frobenius coboundaries;
- [x] prove nonzero representative trace gives nonzero quotient detection;
- [x] identify the trace probe with the derivative/linear coefficient of a determinant coordinate;
- [ ] identify this quotient and functional with the exact arithmetic local deformation and Tate-duality quotient.

## Arithmetic instantiation

- [~] instantiate the abstract finite affine quotient with the actual continuous Galois cocycle and finite residue field;
- [E] apply Chebotarev to the selected finite conjugacy class outside the bad set;
- [ ] decode splitting in `E`, `q_v ≡ 1 mod p^N`, and the required residual spectral condition;
- [ ] prove the local spectral determinant coordinate is the actual Taylor--Wiles variable;
- [ ] prove the resulting functional detects every nonzero active dual-Selmer class;
- [ ] instantiate v0.15 to obtain the genuine finite set `Q_N`.

## Nonlinear deformation and carrier

- [ ] identify the arithmetic auxiliary variables with the columns of the global deformation/Hecke Jacobian;
- [ ] use v0.16 to eliminate every transverse first-order obstruction;
- [ ] prove finite-depth nonlinear lifting or relative formal smoothness over the cyclic defect algebra;
- [ ] establish residual occurrence of the finite-Satake descent in a determinant-bearing complex;
- [ ] construct a relative patched module with sufficient depth/MCM support, or reach the explicit finite threshold `m₀`;
- [ ] prove quotient-character twist-equivariance of support/kernel;
- [ ] obtain one generic branch and then all branches by v0.11;
- [ ] obtain the determinant-bearing Hecke carrier.

## Completion

- [ ] compare all ramified local parameters;
- [ ] close every invariant step in a solvable Clifford tower;
- [ ] conclude finite solvable-image Strong Artin in the imported global range;
- [ ] develop a nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] conclude unrestricted Strong Artin.

## Current first open theorem

The next exact arithmetic theorem is:

```text
v0.16 finite conjugacy class
  -> unramified prime v outside S
  -> split in E and q_v ≡ 1 mod p^N
  -> local block-determinant differential equals the Taylor--Wiles Tate functional.
```

The next exact global theorem remains residual packet occurrence in a determinant-bearing carrier.
