# Continue from Paper I Block 07

## Accepted-source layout

- `source/extension/PaperICompletion7/Nakayama.lean`: general noncommutative radical lifting and literal quotient-map construction.
- `source/extension/PaperICompletion7/ModuleTop.lean`: generating sets/families, lift theorems, canonical cardinal/natural seed-rank equalities.
- `source/extension/PaperICompletion7/LocalResidue.lean`: unique maximal left ideal, internally constructed residue division ring and local dimension formula.
- `source/extension/PaperICompletion7.lean`: current import root, retaining `PaperICompletion6`.
- `predecessor/`: unchanged complete Block 06 source and evidence tree.

Use `VERIFICATION.json` and its hashed `accepted_run` receipt to determine actual acceptance. Never infer PASS from this restart guide alone.

## Next mathematical target

Continue with the NONSPLIT semisimple seed-rank theorem, not another proof of module-top reduction. The relevant publication records are `PSC-I-CI-WEDDERBURN-ARTIN`, `PSC-I-L-REGULAR-MODULE-MULTIPLICITIES` and `PSC-I-T-SEMISIMPLE-SEED-RANK`.

First construct the actual left-module equivalence for products of matrix rings over arbitrary division rings:

    A = product_i M_(d_i)(D_i)  as a left A-module
      is isomorphic to direct_sum_i S_i^(d_i).

For one matrix factor, the columns of the regular matrix module give the natural-module copies. Retain the LEFT action and noncommutative multiplication order. This is a proof plan, not an already verified new declaration.

Then prove the minimum-generator formula for actual multiplicity modules:

    seedRank_A(M) = max_i ceil(m_i / d_i).

Handle division rings without using commuting scalar identities that hold only over fields. A regular-module/free-module quotient or a row/column construction can supply the upper and lower bounds. Treat zero modules and absent factors explicitly. Integrate the proved abstract decomposition existence and module decomposition APIs, rather than taking a rank formula as a certificate.

Finally apply the new `seedRank_eq_radicalTop` to the actual module top for the finite-dimensional-algebra clause. That reduction is now proved over arbitrary unital rings; it is no longer a missing hypothesis.

The current local-ring residue formula alone does NOT prove the matrix-product formula. Matrix rings of size greater than one are not local, and different product factors are independent simple components.

## Existing API to reuse

Namespaces:

- `Komorebi.PaperICompletion7.Nakayama`
- `Komorebi.PaperICompletion7.ModuleTop`
- `Komorebi.PaperICompletion7.LocalResidue`

Important declarations are `idealTopMap`, `idealTopMap_ker`, `lifts_generate`, `seedRank_eq_radicalTop`, `seedFinrank_eq_radicalTop`, `quotient_basis_lifts_generate`, `residueDivisionRing`, and `seedRank_eq_residue_dimension`.

The predecessor split-field implementations are `Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv` and `semisimple_seedRank_eq_maxCeilDiv_of_equivalences`. Their existing hypotheses and object definitions must be inspected before generalizing. Do not silently rename a field proof as a division-ring proof.

## Reproduction and audit

From Linux or WSL, with Python 3 and the exact portable runtime available:

    bash scripts/run_block07.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-audit

The output directory must not already exist. Do not run `lake update` or substitute a newer compiler. The toolchain and dependency cache are external prerequisites, not included in this compact evidence ZIP.

The accepted strategy authenticates 42 predecessor source/object pairs, freshly compiles the four additions and new boundary suite, audits source-owned declarations, and replays the complete logical closure from an upstream-only starting environment. The seven inherited generated partial runtime helpers are separately inventoried and excluded from proof replay. Continue using exact name-set matching and the malformed-proof rejection control.

The remaining packet/functorial/topological and executable algorithm obligations are in `coverage/COVERAGE_108.json`. Papers II–XII remain outside this final sweep so far. Do not count their historical evidence as a new run here.

## Noncommutative matrix implementation warning

For A = M_n(D) and m copies of its natural left module, represent M as n-by-m matrices with A acting by LEFT multiplication. A family of r seed matrices generates exactly when the rows of those matrices, viewed as vectors in D^m, have sufficient left-D span. This suggests the lower bound m ≤ nr and coordinate-row seeds for the matching upper bound. This paragraph is an unverified construction plan.

Do not request an `Algebra D A` instance when D is a genuinely noncommutative division ring: the usual algebra typeclass has commutative scalar assumptions. Restrict scalars through the diagonal ring homomorphism D → M_n(D) when a left-D dimension argument is needed, or work directly with explicit matrix multiplication. The diagonal image need not be central. Preserve multiplication order in every row/column identity.
