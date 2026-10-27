# Strong Artin live research checklist after v0.14

Status meanings:

- `[x]` closed in the current formal/manuscript program at the stated boundary;
- `[~]` active next construction;
- `[ ]` open;
- `[E]` established external input used only in its declared range;
- `[X]` false shortcut or intentionally excluded route.

## I. Prime-cyclic finite algebra

- [x] quotient-character extension torsor;
- [x] cyclic spectrum, Fourier, and coefficient selectors;
- [x] quotient-prime characteristic-polynomial propagation;
- [x] semisimple residual collapse across a prime-cyclic quotient;
- [x] exact cyclic defect algebra and nilpotent special fiber;
- [x] transitive cyclic action on generic branches;
- [x] twist-stable support plus one generic branch implies all branches.

## II. First-order transverse obstruction

- [x] split cyclic and transverse Jacobian blocks;
- [x] transverse surjectivity reduces the full cokernel to the cyclic cokernel;
- [x] quotient-prime cyclic derivative is zero;
- [x] exactly one retained cyclic obstruction dimension;
- [x] full first-order obstruction vanishes iff the cyclic residual vanishes.

## III. Actual relative projectors

- [x] center actual trace-projector probes against the scalar line;
- [x] conjugation covariance of trace probes;
- [x] off-scalar simple-packet detection plus one nonzero-trace projector gives raw separation;
- [x] centered probes separate `End(W)/k·1`;
- [x] extract a finite basis of actual transverse projector probes.

## IV. Degree-one cohomology — v0.14

- [x] finite-group averaging makes every `1`-cocycle a coboundary when the group order is nonzero in the coefficient field;
- [x] restriction on `H¹` is injective across a finite quotient of order nonzero in the field;
- [x] a nonzero `H¹` class has a nonzero value on the normal subgroup;
- [x] formulate and compile the quotient coefficient representation `End(W)/k·1`;
- [x] remove the artificial “every nonzero value is nonscalar” hypothesis by working directly in the quotient;
- [x] nonzero transverse `H¹` class yields an actual centered-projector-detected, label-preserving group element.

## V. Cyclotomic-depth survival — v0.14

- [x] cocycle conjugation identity on a subgroup acting trivially;
- [x] centrality of `S/T` plus no fixed coefficient vectors forces nonvanishing to survive from `S` to `T`;
- [x] quotient fixed-vector vanishing by finite-group averaging;
- [x] Schur implies ambient adjoint fixed vectors are scalar;
- [x] transverse adjoint quotient has no fixed vectors for irreducible finite residual image with order nonzero in the field;
- [x] pullback through a surjective global-to-residual map preserves no-fixed-vector status;
- [x] relative cyclotomic-depth survival capstone under the explicit centrality hypothesis.

## VI. Pre-Chebotarev Taylor–Wiles selection — v0.14

- [x] two-candidate selector `g` versus `sigma*g`;
- [x] preserve the exact residual-image label;
- [x] preserve trivial cyclotomic label;
- [x] retain nonzero centered-projector cocycle evaluation;
- [x] combine deep survival and relative spectral detection into one pre-Chebotarev capstone;
- [~] **NEXT:** encode the finite quotient carrying residual, cyclotomic, cocycle-extension, and ramification labels, then apply/verify the exact Chebotarev interface;
- [ ] prove the selected prime is outside the excluded set and satisfies `q_v ≡ 1 mod p^N`;
- [ ] identify the centered trace evaluation with the nonzero local Tate-duality quotient used in the Taylor–Wiles condition;
- [ ] iterate one-prime selection to annihilate the complete transverse dual-Selmer space.

## VII. Relative patching / finite carrier

- [ ] construct the relative local deformation problem retaining the cyclic defect algebra;
- [ ] prove freeness/depth or maximal Cohen–Macaulay support over the cyclic factor;
- [ ] prove twist-equivariance of the patched/Hecke support;
- [ ] obtain one nonzero generic branch and invoke v0.11 to obtain all cyclic branches;
- [ ] alternatively lift through finite depths `1,...,m0` using Smith/resultant/Hensel corrections;
- [ ] construct one determinant-bearing Hecke packet at the explicit finite-precision threshold.

## VIII. Packet occurrence

- [E] torsion cohomology supplies determinants when the eigensystem occurs in its established range;
- [ ] prove universal occurrence of the weight-zero finite-Satake descent in a determinant-bearing carrier;
- [ ] pursue mod-`p` Smith/Tate occurrence followed by relative patching;
- [ ] pursue integral finite-depth Smith carrier descent as an alternative;
- [ ] pursue finite Hasse/derived weight change where available;
- [ ] pursue a large separating coefficient prime when it lowers carrier cost.

## IX. Complete one cyclic step and the solvable tower

- [x] finite-precision offset recovery once a determinant packet is supplied;
- [x] restriction of that determinant to the lower cyclic field follows from base change and Chebotarev at manuscript level;
- [ ] check ramified local parameters;
- [ ] close every invariant step;
- [ ] conclude finite solvable-image Strong Artin in the exact global range supported by the imported automorphic theorems.

## X. Unrestricted finite image

- [ ] build a separate mechanism for nonabelian simple composition factors;
- [ ] use `A5` as the first laboratory;
- [ ] test solvable-cover / compatible-restriction gluing;
- [ ] generalize only after the `A5` mechanism survives audit.

## Current narrow target

The next theorem is no longer an abstract projector or cohomology statement. It is the arithmetic realization step:

> Package the selected residual/cyclotomic/cocycle labels in one finite Galois quotient, apply Chebotarev to obtain an unramified prime with that Frobenius class, and prove that the resulting local restriction map is exactly the centered projector functional required by the Taylor–Wiles deformation condition.

The first half is a finite-extension/Chebotarev theorem. The second half is a local Tate-duality/deformation-ring theorem. They must remain separate until both are verified.
