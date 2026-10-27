# Strong Artin live checklist after v0.15

Status meanings: `[x]` closed at the stated boundary; `[~]` active; `[ ]` open; `[E]` external in a declared range.

## Finite/cyclic and pre-Chebotarev core

- [x] prime-cyclic extension torsor and residual collapse;
- [x] cyclic defect algebra and generic branch action;
- [x] twist-stable support propagation;
- [x] cyclic/transverse first-order obstruction splitting;
- [x] actual centered-projector detection on the transverse quotient;
- [x] finite-group `H¹` averaging and restriction injectivity;
- [x] survival to the common residual/cyclotomic kernel;
- [x] label-preserving, projector-detected pre-Chebotarev element.

## Adaptive finite auxiliary selection — v0.15

- [x] define the active selected kernel as the intersection of selected scalar local-functional kernels;
- [x] one detecting auxiliary label is automatically fresh;
- [x] each fresh selection strictly lowers the active subspace and its finrank;
- [x] starting from `Q₀`, at most the current active dimension many new labels kill the kernel;
- [x] preserve an arbitrary fixed arithmetic admissibility predicate;
- [x] select exactly `dim H` scalar local conditions from the empty set;
- [x] simultaneous local evaluation is injective;
- [x] package the result as `OnePrimeSelectionInterface`;
- [x] abstract one-prime detection implies an exact finite relative Taylor--Wiles set.

## Arithmetic instantiation of the interface

- [~] package residual, cyclotomic, cocycle-extension, and ramification labels in one finite Galois quotient;
- [ ] realize the selected conjugacy datum by Chebotarev outside the prescribed bad set;
- [ ] derive `q_v ≡ 1 mod p^N` and the required residual spectral condition;
- [ ] identify centered projector evaluation with the actual local Tate-duality quotient;
- [ ] prove that this gives the scalar linear functional required by `OnePrimeSelectionInterface`;
- [ ] instantiate v0.15 and obtain the genuine finite set `Q_N`.

## Carrier and patching

- [ ] residual occurrence of the finite-Satake descent in a determinant-bearing complex;
- [ ] relative local deformation problem retaining the cyclic defect algebra;
- [ ] relative patched module with sufficient depth/MCM support;
- [ ] twist-equivariance of patched support/kernel;
- [ ] one nonzero generic branch, then all branches by v0.11;
- [ ] alternative finite-depth lift through the explicit threshold `m₀`;
- [ ] determinant-bearing Hecke carrier at that threshold.

## Completion

- [ ] ramified local parameter comparison;
- [ ] every invariant step in a solvable Clifford tower;
- [ ] finite solvable-image Strong Artin in the imported global range;
- [ ] nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] unrestricted Strong Artin.

## Current first open theorem

Construct the arithmetic/local-pairing instance of `OnePrimeSelectionInterface`:

```text
nonzero transverse dual-Selmer class
  -> admissible unramified prime v
  -> scalar local Taylor--Wiles functional nonzero on that class.
```

Once this one-prime theorem is established, v0.15 completes the finite iteration automatically.
