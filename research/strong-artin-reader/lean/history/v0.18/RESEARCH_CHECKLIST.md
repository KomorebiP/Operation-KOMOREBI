# Strong Artin live checklist after v0.18

Status meanings: `[x]` closed at the stated formal boundary; `[~]` active; `[ ]` open; `[E]` external theorem in a declared range.

## Finite cyclic local cohomology

- [x] finite cyclic `H¹` represented by the norm kernel modulo `ρ(g)-1`;
- [x] under zero norm, simplify to `A / range(ρ(g)-1)`;
- [x] prove the value-class map is surjective;
- [x] identify its kernel exactly;
- [x] identify `range(ρ(g)-1)` with Frobenius coboundaries for conjugation action;
- [x] obtain `Matrix / frobeniusCoboundaries ≃ H¹`;
- [x] pair the Frobenius centralizer perfectly with actual finite cyclic `H¹`;
- [x] prove the representative formula is `trace(PX)`;
- [x] identify the `q=1` tame relation space with the dual of finite cyclic `H¹`;
- [x] prove uniqueness of the tame-relation representative.

## Tate normalization

- [x] any two nonzero functionals on a one-dimensional line differ by a unique unit;
- [x] unit rescaling preserves exact nonvanishing;
- [x] transport the cyclic trace pairing across an arbitrary comparison equivalence;
- [x] reduce exact Tate normalization to one nonzero scalar;
- [x] prove arithmetic Tate nonvanishing is equivalent to `trace(PX) ≠ 0` under the comparison and nonzero-pairing hypotheses;
- [~] construct the comparison from continuous local Galois cohomology to the finite cyclic model;
- [ ] prove a suitable finite cyclic quotient has the required zero-norm action;
- [ ] prove the arithmetic local Tate pairing is nonzero on the selected line;
- [ ] determine the exact sign/unit under fixed Frobenius and Tate-twist conventions.

## Arithmetic Taylor--Wiles instantiation

- [ ] instantiate the continuous Galois cocycle in the finite affine quotient;
- [E] apply Chebotarev outside the bad set;
- [ ] decode splitting in `E` and `q_v ≡ 1 mod p^N`;
- [ ] use the v0.18 comparison to obtain the true local scalar functional;
- [ ] instantiate v0.15 and produce the arithmetic finite set `Q_N`;
- [ ] prove the global Selmer--Jacobian equivalence;
- [ ] identify local variables with the v0.17 Jacobian columns.

## Nonlinear lifting and support

- [ ] prove residual augmented-Jacobian surjectivity gives a lifted right inverse;
- [ ] prove the actual deformation equations satisfy a relative Hensel step;
- [ ] obtain the finite carrier through the explicit threshold `m₀`, or a flat/MCM relative patched module;
- [ ] identify generic coefficients with the split cyclic branches;
- [ ] prove quotient-character twist equivariance.

## Dominant global existence block

- [ ] construct a nonzero patchable residual finite-Satake packet in a determinant-bearing automorphic/cohomological complex;
- [ ] establish the required level variation and Galois determinant/deformation action;
- [ ] prove ramified local attachment;
- [ ] iterate every invariant step in the solvable Clifford tower;
- [ ] conclude finite solvable-image Strong Artin in the imported range;
- [ ] develop the nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] conclude unrestricted Strong Artin.

## First open theorem

Construct an arithmetic comparison diagram

```text
continuous local unramified H¹
  -> finite cyclic H¹
  ≃ Matrix / range(1 - Ad(F))
```

for the selected Taylor--Wiles line, and prove that arithmetic local Tate duality is nonzero there. Exact normalization may then be recovered up to a unique unit by v0.18.
