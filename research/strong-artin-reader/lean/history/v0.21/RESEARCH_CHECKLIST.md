# Strong Artin live checklist after v0.21

Status meanings: `[x]` closed at the stated formal boundary; `[~]` active; `[ ]` open; `[E]` external theorem in a declared range.

## Completed formal-presentation bridge

- [x] compile finite multivariate polynomials into the v0.20 expression language;
- [x] preserve polynomial evaluation under compilation;
- [x] prove principal-adic depth equals at least monomial total degree at nilpotent points;
- [x] prove all terms above the nilpotence cutoff vanish;
- [x] define finite Artin evaluation by total-degree truncation;
- [x] prove truncation evaluation stabilizes beyond the cutoff;
- [x] define canonical evaluation using Mathlib `MvPowerSeries.subst`;
- [x] prove canonical substitution equals finite truncation exactly;
- [x] prove later truncations give the same value;
- [x] prove the polynomial compiler preserves formal partial derivatives;
- [x] compile finite formal-power-series systems to v0.20 polynomial systems;
- [x] prove compiled evaluation equals the original untruncated formal evaluation;
- [x] define the matrix of original formal linear coefficients;
- [x] prove every truncation level `N ≥ 2` has that same Jacobian at the origin;
- [x] prove a surjective reduced linear coefficient matrix gives an exact formal zero;
- [x] form the relation ideal of the completed presentation;
- [x] factor canonical evaluation through the quotient;
- [x] produce an actual algebra point of the completed presentation quotient.

## Arithmetic presentation and Jacobian identification

- [~] choose the actual finite-level relative deformation/Hecke algebra relevant to the cyclic Strong Artin step;
- [ ] prove it admits a finite completed presentation by formal coordinates and relations;
- [ ] identify the formal coordinates with global deformation and Taylor--Wiles variables;
- [ ] identify the original linear coefficient matrix with the arithmetic augmented Jacobian;
- [ ] prove the global Selmer--Jacobian comparison;
- [ ] derive residual surjectivity from the selected arithmetic auxiliary set;
- [ ] apply the v0.21 point theorem at the explicit attachment precision `m₀`.

## Local arithmetic comparison

- [~] compare continuous local Galois `H¹` with the finite cyclic/Frobenius model;
- [ ] prove normalized local Tate duality equals a nonzero unit times `trace(PX)`;
- [E] realize the Chebotarev-ready finite conjugacy class outside the bad set;
- [ ] derive splitting in `E` and `q_v ≡ 1 mod p^N`;
- [ ] instantiate the arithmetic one-prime interface and the genuine set `Q_N`.

## Dominant automorphic carrier block

- [ ] construct a nonzero patchable determinant-bearing residual finite-Satake packet;
- [ ] establish Hecke/deformation action and Taylor--Wiles level variation;
- [ ] connect its finite-level Hecke character to the formal presentation above;
- [ ] construct a flat/MCM relative patched module or use the v0.21 finite-depth point;
- [ ] identify generic coefficients with the split cyclic branches;
- [ ] prove quotient-character twist equivariance;
- [ ] prove ramified local attachment;
- [ ] iterate every invariant solvable Clifford step;
- [ ] conclude finite solvable-image Strong Artin;
- [ ] develop a nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] conclude unrestricted Strong Artin.

## First open theorem

The nonlinear/presentation lane is now reduced to the arithmetic comparison:

```text
actual relative deformation/Hecke algebra
  -> finite completed formal presentation
  -> linear coefficient matrix = Taylor--Wiles-completed arithmetic Jacobian.
```

Once residual surjectivity is supplied, v0.21 constructs an exact finite-level point of the untruncated completed quotient automatically.
