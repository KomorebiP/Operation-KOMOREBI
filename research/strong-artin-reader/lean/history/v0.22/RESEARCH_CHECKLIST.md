# Strong Artin live checklist after v0.22

Status meanings: `[x]` closed at the stated formal boundary; `[~]` active; `[ ]` open; `[E]` external theorem in a declared range.

## Presentation and cotangent obstruction

- [x] identify the relation differential map with the finite-support transpose-Jacobian action;
- [x] identify the raw presentation obstruction with the transpose-Jacobian kernel;
- [x] construct the canonical map from the raw kernel to intrinsic cotangent H1;
- [x] prove that map is surjective;
- [x] identify its kernel with relation syzygies;
- [x] prove the syzygy–presentation–H1 sequence is exact;
- [x] prove canonical injectivity iff the selected relations are independent in the conormal module;
- [x] obtain a linear equivalence under conormal independence;
- [x] prove the rank correction by syzygy rank;
- [x] prove duplicate conormal relations create a nonzero spurious obstruction;
- [x] define the intrinsic Selmer comparison datum;
- [x] transport exactness to the Selmer obstruction space;
- [x] prove genuine arithmetic functionals vanish on relation syzygies;
- [x] prove nonzero syzygies prevent complete arithmetic detection on the raw kernel.

## Corrected arithmetic presentation target

- [~] construct the actual Strong Artin comparison
  ```text
  cotangent H1 ≃ transverse dual-Selmer obstruction;
  ```
- [ ] prove the selected deformation/Hecke relations are independent in the conormal module; or
- [ ] define the Taylor–Wiles one-prime interface on the quotient by relation syzygies;
- [ ] prove the intrinsic obstruction has the finite dimension predicted by the global Euler characteristic;
- [ ] compare the intrinsic obstruction map with the v0.21 polynomial/formal-presentation Jacobian.

## Local and auxiliary arithmetic

- [ ] construct the continuous local Galois-H1 comparison;
- [ ] prove local Tate duality is a nonzero-unit multiple of the projector trace;
- [E] realize the prepared finite conjugacy class by Chebotarev outside the bad set;
- [ ] derive the required splitting and Taylor–Wiles congruence conditions;
- [ ] instantiate the arithmetic one-prime interface on the intrinsic obstruction space;
- [ ] obtain the genuine finite auxiliary set.

## Carrier and completion

- [ ] construct a nonzero patchable determinant-bearing residual finite-Satake packet;
- [ ] construct the relative deformation/Hecke presentation;
- [ ] prove relative flat/MCM patching or finite-depth carrier existence;
- [ ] prove quotient-character twist equivariance;
- [ ] complete ramified local attachment;
- [ ] iterate every invariant step in a solvable Clifford tower;
- [ ] conclude finite solvable-image Strong Artin;
- [ ] develop a nonabelian-simple-factor mechanism;
- [ ] conclude unrestricted Strong Artin.

## Current first open theorem

Construct the arithmetic comparison with the **intrinsic** obstruction:

```text
transverse dual Selmer
  ≃ cotangent H1 of the relative deformation/Hecke presentation.
```

Then either prove conormal independence or explicitly pass from the raw transpose-Jacobian kernel to its quotient by relation syzygies before invoking v0.15–v0.21.
