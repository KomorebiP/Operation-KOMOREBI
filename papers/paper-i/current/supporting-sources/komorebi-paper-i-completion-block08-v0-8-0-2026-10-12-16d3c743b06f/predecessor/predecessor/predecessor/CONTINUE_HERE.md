# Continue Paper I after Block 05

## Authoritative predecessor and restart

Use this Block 05 package only after its top-level `VERIFICATION.json` reports PASS and its manifest matches. It contains the full unchanged Block 04 predecessor. Preserve the prior mathematical sources and dependency pins.

The new production source is under `source/extension/`. `PaperICompletion5.lean` imports three mathematical modules:

1. `PaperICompletion5/LinearPrimaryEigenspace.lean`
2. `PaperICompletion5/GeometricSeedFormula.lean`
3. `PaperICompletion5/CyclicGeometricCriterion.lean`

Do not repeat the intrinsic quotient, residue kernel, primary presentation, or geometric multiplicity proofs as though they were still missing. Those results have their current source and evidence here.

## Next mathematical target: actual scalar extension

The printed six-way cyclic-matrix criterion includes a statement AFTER extending an arbitrary base field k to an algebraic closure K. Block 05 proves the geometric criterion when the original field is already algebraically closed. These are different Lean statements.

The next bridge should use an actual tensor-product extension `K ⊗[k] V` and actual extended endomorphism, for example the pinned Mathlib `T.baseChange K` API. Prove a sufficient preservation/reflection statement, rather than introducing an unrelated operator S over K:

    HasCyclicVector T iff HasCyclicVector (T.baseChange K),

or, equivalently for finite-dimensional operators, the relevant equality of minimal and characteristic polynomials under extension together with reflection of polynomial equality through the injective coefficient map.

`LinearMap.charpoly_baseChange` is present in the pinned source at `Mathlib/LinearAlgebra/Charpoly/BaseChange.lean`. A matching operator minpoly-base-change theorem has not been established in this package. Do not silently assume it or confuse a general algebra-element minpoly theorem with the special endomorphism-extension statement.

Additional pinned source interfaces located during handoff review are `Module.End.baseChangeHom` in `Mathlib/LinearAlgebra/TensorProduct/Tower.lean`, `Module.Flat.linearIndependent_one_tmul` and `LinearMap.baseChangeHom_injective` in `Mathlib/RingTheory/Flat/Basic.lean`, and the natural endomorphism tensor map `LinearMap.tensorProductEnd` in `Mathlib/RingTheory/TensorProduct/Maps.lean`. These names were inspected in the pinned source, not compiled into an additional Block 05 scalar-extension proof. Injectivity over k alone must not be confused with preservation of linear independence over K.

One possible proof route is to show linear independence of the powers I,T,...,T^(d-1) survives a field extension and use the annihilating polynomial obtained by mapping coefficients. Another is to derive an exact annihilator base-change statement for the polynomial module. These are proof plans, not verified new results.

After the extension bridge, combine it with

    CyclicGeometricCriterion.hasCyclicVector_iff_all_spectral_multiplicities_one

at K to obtain the actual clause (vi). Retain the nonzero finite-dimensional hypotheses where the statement uses seed rank one.

## Finish the exact six-way assembly

The actual one-factor quotient equivalence is now available:

    HasCyclicVector T iff Nonempty (Module.AEval' T ≃_{k[t]} k[t]/(minpoly_k(T))).

The original cyclic/minpoly bridge, primary-label injectivity, intrinsic multiplicities, grouped primary equivalences, and conditional invariant-factor count are preserved. Finish the exact links to every nonzero intrinsic primary component being cyclic and to the manuscript's rational-canonical wording. A mathematical one-factor module equivalence is not automatically an implemented companion-matrix or invariant-factor algorithm.

## Further work remains

The full 108-record map remains authoritative for nonsplit semisimple, module-top/Nakayama, expanded packet/functorial/topological, and executable algorithm obligations. Papers II–XII have not been rerun in this final sweep.

## Reproduction and scope

Run `bash scripts/run_block05.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output` in Linux or WSL with Python 3. The output path must not exist. The runtime is an external prerequisite. Do not run `lake update`.

This block's accepted strategy freshly compiles four new production modules, authenticates 33 unchanged predecessor source/object pairs, and replays all 37 through the same official Lean kernel. It is not a fresh rebuild of all 37 sources, a full Mathlib rebuild, or an independent verifier. `evidence/PREDECESSOR_ATTEMPT_NOT_ACCEPTED.json` records a separate cancelled optional rebuild that must not be mistaken for an accepted complete run.
