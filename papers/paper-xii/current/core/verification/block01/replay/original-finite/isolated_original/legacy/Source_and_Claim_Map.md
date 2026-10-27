# Source and Claim Map

## Paper identity

**Projector-Resolved Seed Calculus XII: Global Seed Completion — Adequate Projectors, Automorphy Lifting, and Final Occupancy**

**Author:** Komorebi P.

This map separates the results proved or exactly certified in the release from the classical theorems used as input and from the global statements that remain unproved.

## Common operator language inherited from Papers I-XI

The paper uses the same sequence throughout the series:

```text
residual seed
→ local deformation packet
→ generalized-eigenspace projector
→ auxiliary Taylor-Wiles refinement
→ patched module
→ R = T coordinate identification
→ finite Hecke occupancy
→ local-global realization
```

The common objects are:

- residual seed `rho_bar`;
- local and global deformation rings;
- exact idempotent projectors `e_alpha`;
- transfer blocks between packet components;
- finite group-algebra refinements `O[Delta_Q]`;
- augmentation or coarse-reconstruction maps;
- patched modules and support;
- commuting Hecke packet projectors;
- compatible-system Frobenius spines.

## Proved in the paper

### Exact algebraic theorems

1. **Bézout primary projector theorem.** Pairwise coprime primary factors produce exact generalized-eigenspace projectors. Their denominators are controlled by pairwise resultants.
2. **Local packet reconstruction.** A complete local projector family reconstructs the local deformation coordinate object and its global completed tensor product.
3. **Cyclic group-algebra quotient theorem.** Quotient maps between finite cyclic group algebras are exact algebra homomorphisms and commute through a refinement tower.
4. **Coinvariant recovery theorem.** Augmentation recovers the declared coarse module from the finite auxiliary level.
5. **Compatible free patching theorem.** A finite free compatible tower gives an inverse-limit module with exact coarse recovery under the stated finite hypotheses.
6. **Faithfulness and support theorem.** A faithful module over a finite product ring occupies every nonzero idempotent component.
7. **Ring-isomorphism packet transport.** An `R = T` isomorphism transports idempotents, orthogonality, reconstruction, support, and occupancy exactly.
8. **Finite-carrier occupancy theorem.** A nested finite family of commuting semisimple projectors has nonzero total intersection exactly when the final projector has positive trace.
9. **One-member propagation theorem.** Within a fixed semisimple compatible system, a common characteristic-zero Frobenius spine identifies the coefficient-prime members.
10. **Finite companion obstruction theorem.** One empty required finite companion level prevents completion of a compatible inverse-limit branch.
11. **Dyadic separation proposition.** Rational sign projectors may require denominator two and become integrally distinguishable only at a later `2`-adic depth.
12. **Dyadic augmentation theorem.** Finite group-algebra augmentation and coinvariant reconstruction remain exact at coefficient prime two without relying on semisimple character projectors.
13. **Conditional global seed completion theorem.** Eight explicitly stated hypotheses imply automorphic realization within the declared class.

### Exact finite certificates

1. A `5 × 5` matrix with three primary blocks has projector ranks `(2, 1, 2)` and denominators `(9, 144, 16)`.
2. The standard two-dimensional representation of `S3` over `F7` satisfies the four adequacy conditions in the complete finite calculation.
3. The trace-zero adjoint splits into sign and standard packets of dimensions `1` and `2`; both are detected by generalized-eigenspace projectors.
4. Odd and dyadic cyclic group-algebra towers satisfy multiplication, quotient-composition, augmentation, and coinvariant identities exactly.
5. The finite `R = T` support model preserves every occupied idempotent packet; quotient and nonfaithful-module controls lose declared packets exactly.
6. The consistent finite Hecke rank sequence is `(7, 4, 3, 2, 1, 1)`; one incompatible final condition gives rank zero.
7. The infinite tail-projection example has nonzero every finite stage but zero total intersection.
8. Four Frobenius traces recover the compatible-carrier multiplicities `(2, 0, 1)` exactly.
9. The dyadic sign packets merge modulo two and separate modulo four.

## Classical input used but not re-proved

The paper uses the following established theory as input:

- representability of framed lifting and deformation functors;
- tangent and obstruction descriptions through `H^1` and `H^2`;
- local deformation conditions and their representing quotients;
- adequacy-based automorphy-lifting theorems in their stated ranges;
- Taylor-Wiles auxiliary primes and Taylor-Wiles-Kisin patching;
- established `R = T` theorems;
- existence of Galois representations attached to suitable automorphic representations;
- Chebotarev density and Brauer-Nesbitt;
- local-global compatibility and classicality in the settings where they are known.

The supplied source basis is:

- Toby Gee, *Modularity lifting theorems*;
- Richard Taylor, lectures on automorphy lifting, notes by Dan Dore and Tony Feng;
- Konstantin Miagkov and Jack A. Thorne, *Automorphy lifting with adequate image*.

Bibliographic entries are intentionally excluded from this paper and retained in the consolidated series reference ledger.

## Conjectural or open in this paper

The paper does not prove:

1. universal existence of every required residual or coefficient-prime companion;
2. universal automorphic occupancy of every residual transport source component;
3. a uniform replacement at coefficient prime two for all odd-prime adequacy and patching hypotheses;
4. full support of a patched automorphic module on every admissible deformation component without the declared hypotheses;
5. positive trace for every finite global Hecke packet;
6. universal local-global compatibility and classicality;
7. unrestricted global Langlands reciprocity.

The exact remaining boundary is:

```text
completion:
    populate every required residual and coefficient-prime companion forest;

occupancy:
    prove positive finite Hecke-packet trace in the required global carrier;

realization:
    establish local-global compatibility and classicality uniformly.
```

## Numerical role

The finite calculations certify implemented formulas and expose negative controls. They do not substitute for the imported automorphy-lifting, patching, or global existence theorems.
