# Current status — v0.8.0

Base: supplied v0.7.0, whose exact hashes are in `audit/base_sha256.json`.
Current scope: written proofs and self-review. No Lean proof package and no
independent audit. All three finite check suites passed in this session.

## New results

| Ledger | Result | Restriction |
|---|---|---|
| K42 | Derived reduction along Z/D^n is exact, conservative, and not faithful | Perfect complexes, D squarefree positive with nonempty prime set |
| K43 | Weighted exchange cells and their residual transport | Scalar weights are explicit additional data; canonical tensor/base-change already commutes |
| K44 | Prime-power Koszul cohomology | Explicit valuation minimum, including unit and all-zero residue cases |
| K45 | Nilpotent-cone excision collapse | Killing a nonunit pair over Z/p^n annihilates the whole perfect category |
| K46 | Exact finite prime-component quotient, compatible with coarsening | Unit-seed pair tests included; removes entire selected factors |
| K47 | Uniform based-tower reconstruction | Fixed finite degree range, ranks, and strictly compatible matrices |
| K48 | Nonzero finite negative homology with pro-zero transition system | Actual transition maps retained |
| K49 | Generic-fiber formula for completion/repair comparison | Perfect completed input; fiber in the ambient derived category |
| K50 | Arithmetic fracture square for complexes and residuals | Perfect integral complexes; classical CRT mechanism |
| K51 | Effective arithmetic lattice gluing and equivalence of gluing categories | Localized finite free module, local lattices, specified generic identifications |
| K52 | Compatible integral operators descend | Exact intertwining and any inverse data supplied |

K15 now has a concrete positive lattice instantiation (K51). The intended
reciprocity application does not follow from that instance. K17, the
Langlands-facing global reciprocity obligation, remains open. K18, Lean
formalization, remains open. The previously refuted general ordered-filtration
independence claim is not reinstated.

## Three established distinctions

1. Canonical base-change compatibility versus deliberately weighted exchange.
2. Finite-level exact repair versus repair after completion. Coherent finite
   quotients can lose a nonzero generic fiber in the limit.
3. Reconstruction of a supplied complex versus construction from independent
   gluing data. K51 proves the latter only for the precisely specified lattices.

## Next executable mathematical target

Choose a natural, non-scalar arithmetic functor and its actual comparison with
derived coarsening. Compute that comparison's cone and its information-preserving
reconstruction data, without inserting a scalar defect by hand. A concrete first
candidate is a specified invariants/cohomology functor with an explicit group
and coefficient tower; exactness, boundedness, and comparison types must be
verified before fitting it into the present perfect-category model.

Further obligations remain: genuinely non-strict exchange coherence, general
tower effectivity, higher-dimensional coefficient rings, and construction of
the actual arithmetic/automorphic generic objects and identifications. None is
replaced by counting the number of proved ledger entries.
