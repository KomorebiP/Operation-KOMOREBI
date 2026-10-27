# Strong Artin live checklist after v0.23

Status meanings: `[x]` closed at the stated formal boundary; `[~]` active;
`[ ]` open; `[E]` external theorem in a declared range.

## Presentation and intrinsic obstruction

- [x] identify the raw transpose-Jacobian kernel;
- [x] construct its canonical surjection to intrinsic cotangent `H1`;
- [x] identify the kernel as relation syzygies;
- [x] prove the syzygy/raw/intrinsic sequence is exact;
- [x] show genuine arithmetic functionals vanish on presentation syzygies;
- [x] show redundant relations cannot be killed by arithmetic auxiliary probes.

## Syzygy-corrected auxiliary selection — v0.23

- [x] pull intrinsic Selmer local functionals back to a raw presentation;
- [x] prove injective intrinsic evaluation leaves exactly relation syzygies;
- [x] prove the selected raw evaluation is surjective;
- [x] obtain the exact sequence
  ```text
  0 → relation syzygies → raw obstruction → selected coordinates → 0;
  ```
- [x] prove the selected cardinality is intrinsic cotangent-`H1` rank;
- [x] prove
  ```text
  intrinsic rank + syzygy rank = raw obstruction rank;
  ```
- [x] prove cardinality minimality among scalar families with syzygy kernel;
- [x] prove one intrinsic set works for two different presentations;
- [x] under conormal independence, compare raw obstruction spaces through the
  common coordinate space;
- [x] prove that comparison preserves every selected coordinate.

## First technical continuation

- [~] define the compatible equation subspace annihilated by relation syzygies;
- [ ] prove the augmented Jacobian has image exactly that compatible subspace;
- [ ] formulate a syzygy-compatible nonlinear Hensel theorem whose defects and
  Taylor remainders remain in the compatible subspace;
- [ ] alternatively construct a conormally independent first-jet presentation;
- [ ] connect the quotient-corrected intrinsic obstruction to the v0.20/v0.21
  nonlinear finite-level lifting pipeline.

## Arithmetic instantiation

- [ ] construct the actual Strong Artin comparison
  ```text
  intrinsic cotangent H1 ≃ transverse dual Selmer;
  ```
- [ ] construct the arithmetic one-prime Taylor--Wiles interface on that
  intrinsic space;
- [E] realize the prepared conjugacy classes by Chebotarev;
- [ ] identify continuous local Galois `H1` and local Tate pairing with the
  checked finite cyclic/projector model;
- [ ] identify the true local auxiliary variables with intrinsic selected
  coordinates.

## Global carrier and completion

- [ ] construct a nonzero patchable determinant-bearing residual finite-Satake
  automorphic packet;
- [ ] construct a flat/MCM relative patched module or a finite-depth carrier;
- [ ] prove quotient-character twist equivariance;
- [ ] complete ramified local attachment;
- [ ] iterate every invariant step of a solvable Clifford tower;
- [ ] conclude finite solvable-image Strong Artin;
- [ ] develop a nonabelian-simple-factor mechanism;
- [ ] conclude unrestricted Strong Artin.
