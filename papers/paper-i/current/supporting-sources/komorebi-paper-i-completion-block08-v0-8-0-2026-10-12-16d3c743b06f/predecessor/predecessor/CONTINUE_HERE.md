# Continue here: Paper I after Block 06

Consult `VERIFICATION.json` and its accepted-run hash before relying on this checkpoint. Do not infer a completed audit from the existence of this restart guide alone.

## What is now supplied by the current source

`PaperICompletion6.ScalarExtension` proves the minimal-polynomial identity and cyclicity preservation/descent for the actual tensor extension. `PrimaryCyclicCriterion` proves the literal nonzero-primary cyclicity criterion. `OneInvariantFactor` constructs a genuine companion-matrix basis and identifies the monic factor with the minimal polynomial. `SixWayCyclicCriterion` assembles the exact six clauses, including a literal `AlgebraicClosure k` instance and the any-chain invariant-factor count-one consequence.

Do not reconstruct these as though they were still missing. Do not reinterpret the earlier native algebraically closed theorem as the extension theorem; the latter is now separately proved in its actual tensor-product form. The retained conditional predecessor wrappers remain valid compatibility APIs, not the strongest current statements.

## Next publication records

Stay on Paper I. Start with:

- `PSC-I-CI-NAKAYAMA`: the noncommutative radical lifting statement.
- `PSC-I-T-MODULE-TOP`: generator lifting and equality of canonical seed ranks modulo the Jacobson radical.
- `PSC-I-C-LOCAL-ALGEBRA-FORMULA`: the residue **division-ring** dimension formula, not only a commutative residue-field version.

The first is a classical-input record. The latter two are still `not_mapped` in this checkpoint. No next-block result is marked proved here.

The printed module-top theorem assumes only a unital ring A and a finitely generated left A-module M. It does not assume A/J semisimple. For J = Jac(A), it asserts that a family generates M iff its image generates M/JM over A/J, and then identifies the canonical cardinal-valued ranks. Preserve the absence of a semisimplicity assumption.

## A concrete pinned upstream starting point

The pinned Mathlib source `Mathlib/RingTheory/Jacobson/Radical.lean` already contains a **noncommutative** form:

    Submodule.FG.eq_bot_of_le_jacobson_smul

Its surrounding variables are `[Ring R]`, not `[CommRing R]`. The hypothesis is finite generation of an actual submodule N and N ≤ Jac(R)·N; the conclusion is N = ⊥. The same file defines `Ring.jacobson`, proves it two-sided, proves `Ring.jacobson_smul_top_le`, and provides the module-radical/coatomic machinery. `Module.Finite` supplies coatomicity through `RingTheory/Finiteness/Basic.lean`.

This avoids silently using the different commutative-only file `RingTheory/Nakayama.lean`. The pinned files and their hashes are recorded in `docs/NEXT_BLOCK_API_SOURCES.json`. They were inspected for planning, not freshly compiled as new project proofs in Block 06.

A prospective construction is:

1. Apply noncommutative Nakayama to the quotient M/N to derive M = N from M = N + JM, retaining the actual submodule-scalar-product maps.
2. Construct the canonical A/J action on M/JM using the proved two-sidedness of J. Prove the quotient representative and action laws explicitly.
3. Identify the image-span condition over A/J with the corresponding quotient condition over A, then lift generators by Step 1.
4. Derive both inequalities for the existing canonical `seedRank`, using images in one direction and lifted representatives in the other. Do not define the desired equality into a new certificate.
5. For the local corollary, construct the residue division-ring structure from local-ring hypotheses and prove that the quotient module's seed rank is its left division-ring dimension.

These are proof obligations, not accepted Lean theorems yet. In particular, the pinned `IsLocalRing.ResidueField` convenience API is commutative. Its direct use would not certify the printed arbitrary residue-division-ring scope. `IsLocalRing` itself is defined for semirings, so inspect the general local-ring and quotient APIs rather than silently narrowing the manuscript.

Useful boundaries to test include a genuinely noncommutative instance, a zero module, a radical quotient with nontrivial lifting, and a counterexample when the chosen ideal is not contained in the Jacobson radical. Finite generation must not disappear from the public theorem merely because a finite example passes.

## Source layout and reproduction

The current source is under `source/extension/PaperICompletion6`. All Block 05 files are preserved under `predecessor/`. Its source/object receipt is `predecessor/evidence/final_audit/verification.json`; older source roots remain in their original nested locations. The current accepted audit is `evidence/final_audit/verification.json`.

Use the external pinned `Komorebi_Portable_Lean_4.34.0-rc2` runtime. Do not run `lake update`. The reproducible launcher is:

    bash scripts/run_block06.sh /absolute/path/to/pinned-runtime /absolute/path/to/new-output

The output directory must not already exist. Development objects are under `evidence/dev_objects` and must not be substituted for final acceptance objects. The test fixtures intentionally contain invalid proofs and forbidden-axiom controls; they are not production mathematics.

Keep the 108 publication statements and stored source-proof records unchanged unless a documented publication correction is explicitly being made. Update coverage only for the clauses actually proved. Existing certificate-conditioned theorems remain useful compatibility APIs but are not a replacement for the intended general existence and construction statements.

Papers II–XII have not been rerun in this audit sweep. The nonsplit semisimple, expanded packet/functorial/topological, and executable-algorithm obligations remain separate.
