# Strong Artin live research checklist after v0.13

Status meanings:

- `[x]` closed in the current formal/manuscript program at the stated boundary;
- `[~]` active next construction;
- `[ ]` open;
- `[E]` established external input used only in its declared range;
- `[X]` known false shortcut / intentionally excluded route.

## I. Prime-cyclic finite algebra and residual structure

- [x] quotient-character extension torsor on isomorphism classes;
- [x] cyclic spectrum / Fourier / coefficient selectors;
- [x] determinant selector when applicable;
- [x] quotient-prime characteristic-polynomial propagation;
- [x] semisimple prime-cyclic residual collapse (v0.10);
- [x] exact cyclic defect algebra and nilpotent special fiber (v0.11);
- [x] exact cyclic twist action on generic branches;
- [x] one twist-stable supported branch implies all generic cyclic branches.

## II. First-order quotient-prime obstruction

- [x] cyclic/transverse Jacobian splitting (v0.12);
- [x] transverse surjectivity makes full cokernel equal cyclic cokernel;
- [x] quotient-prime scalar cyclic derivative is zero;
- [x] exactly one scalar obstruction dimension remains under transverse surjectivity;
- [x] full obstruction vanishes iff cyclic residual vanishes.

## III. Actual spectral-projector probe bridge — v0.13

- [x] center arbitrary raw probes against one defect-detecting reference probe;
- [x] centered joint kernel is exactly the defect line when raw probes separate;
- [x] realize centered functionals by centered trace-projector combinations;
- [x] construct the conjugation representation on `End(W)`;
- [x] prove conjugation-covariant projectors give covariant trace probes;
- [x] prove every nonzero invariant kernel contains a simple packet without assuming modular semisimplicity;
- [x] simple-packet detection implies joint separation;
- [x] replace full simple-packet detection by **off-scalar detection + one nonzero-trace reference projector**;
- [x] relative/off-scalar detection implies the full obstruction is exactly cyclic;
- [x] extract a finite linearly independent basis of actual centered quotient-projector probes;
- [x] selected basis size equals the transverse deformation dimension.

## IV. Representation-theoretic arithmetic condition

- [~] **NEXT TARGET:** prove or classify when the actual quotient-prime residual image with its generalized-eigenspace projectors satisfies `DetectsEverySimplePacketOffScalar`;
- [ ] identify exceptional finite-image configurations where relative detection fails;
- [ ] determine whether Komorebi seed/duality/finite-precision mechanisms close those exceptional configurations separately;
- [ ] produce a finite certificate/checking procedure for relative spectral detection for a given finite residual image.

## V. Global auxiliary-prime realization

- [E] classical adequate-image Taylor--Wiles theory constructs finite auxiliary sets under its published regular/adequate hypotheses;
- [ ] prove the required **relative** Taylor--Wiles/Chebotarev selection theorem in the quotient-prime singular setting;
- [ ] realize the finite v0.13 transverse probe basis by auxiliary Frobenius classes;
- [ ] preserve required congruence conditions `q_v ≡ 1 mod p^N` and local deformation packets;
- [ ] prove the resulting transverse correction data survives at every finite depth needed below.

## VI. Finite-depth lifting to the attachment threshold

- [x] manuscript one-step Hecke obstruction is identified by a residual Jacobian cokernel;
- [x] v0.12/v0.13 reduce the first-order linear obstruction to the cyclic coordinate under relative detection;
- [ ] extend transverse control to nonlinear corrections through depths `1,...,m0`;
- [ ] use Smith/resultant/Hensel weights at singular coefficient primes;
- [ ] produce one Hecke homomorphism `T -> O/varpi^m0` at the explicit finite-precision threshold;
- [ ] specialize a determinant/Galois carrier at that packet;
- [ ] verify restriction to the already attached representation over the cyclic extension.

## VII. Finish one invariant cyclic step

- [x] high-precision cyclic offset recovery exists at manuscript level once the finite determinant packet is supplied;
- [x] finite Satake separation upgrades sufficient finite congruence to exact characteristic-zero attachment;
- [ ] apply the carrier at every required invariant step;
- [ ] check finitely many ramified local extension spectra.

## VIII. Solvable Strong Artin

- [E] cyclic/subnormal automorphic induction and solvable base change in their established ranges;
- [x] finite Clifford recursion is reduced to orbit steps plus invariant steps;
- [ ] close every invariant step by the finite carrier construction;
- [ ] conclude Strong Artin for all finite solvable-image representations in the precise declared global range.

## IX. Unrestricted finite image

- [ ] develop a mechanism for nonabelian simple composition factors;
- [ ] use `A5` as the first adversarial/simple-factor laboratory;
- [ ] formulate and test solvable-cover / compatible restriction descent;
- [ ] extend beyond `A5` if a structural mechanism survives;
- [ ] conclude unrestricted Strong Artin only after these non-solvable factors are handled.

## Current narrow target

The next proof problem is no longer "show projector probes span the transverse dual." v0.13 proves that from the exact relative spectral condition.

The next target is:

> For the actual finite quotient-prime residual image arising at an invariant Strong Artin Clifford step, prove that generalized-eigenspace projector trace functionals detect every simple conjugation packet outside the scalar cyclic line, or classify and separately close the exceptions.

Only after this representation-theoretic condition is secured should the program promote the next box to the global relative Taylor--Wiles selection theorem.
