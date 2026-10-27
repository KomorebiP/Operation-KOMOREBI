# Paper I completion: Block 08

**Result: PASS for the nonsplit semisimple seed formulas, compatible abstract decomposition construction, authenticated predecessor and upstream-only whole-project logical kernel replay.**

**Date:** 12 October 2026. **Version:** 0.8.0.

Five further proof-level publication records are covered and the Wedderburn-Artin classical input is integrated. This does not claim complete formalization of the expanded monograph. All predecessor mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For an arbitrary semisimple Artinian ring A and finitely generated left module M, the new development constructs actual compatible presentations

    A ≃ product_i M_(d_i)(D_i),
    M ≃ direct_sum_i (D_i^(d_i))^(m_i),

and proves

    seedRank_A(M) = max_i ceil(m_i / d_i).

The D_i are arbitrary division rings, not assumed commutative. Positive matrix sizes, absent factors and zero/empty cases are handled explicitly. The upper and lower generator bounds use the literal left span of seed-matrix rows. The constructed regular-module equivalence takes actual natural columns and is proved A-linear.

The abstract existence theorem does not take a decomposition, spectral/multiplicity certificate or seed-rank equality as an input. The proved ring decomposition is integrated from the pinned Mathlib. The compatible module decomposition is constructed by decomposing into finite simple summands, projecting nontrivially into regular-module columns, using simplicity to obtain isomorphisms and regrouping the actual factor fibres.

For any Artinian ring, the formula on the literal radical quotient and module top computes the original module's seed rank. The finite-dimensional-algebra clause derives Artinianity internally. The printed split corollary has an exact original-ring/top wrapper in addition to the quotient-ring variant. Once a split presentation is supplied, algebraic closure is unnecessary.

The natural-module rank-one result and the multiplicity obstruction are now proved over arbitrary division rings, with actual finite-direct-sum and column-model equivalences. These are classical mathematical completions, not claims of new classical discoveries or an executable decomposition algorithm.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | 2041 / 2041 |
| Complete predecessor compared with original ZIP | 2042 / 2042 files |
| Authenticated predecessor source/object pairs | 46 / 46 |
| New production modules freshly compiled | 8 / 8 |
| Original normative contract retained | 35 rows, 84 mapped declarations |
| Public-or-coverage names resolved with types and axioms | 378 / 378 |
| Source-owned entries inventoried and axiom-audited | 1634 / 1634 |
| Logical production declarations rechecked | 1627 / 1627 |
| Inherited generated partial runtime helpers separately inventoried | 7 |
| Complete production-module closure replayed | 54 modules |
| New boundary module freshly compiled and replayed | 1 / 1 |
| New public mathematical boundary assertions | 25 / 25 |
| Logical replay entries including boundary helpers | 1672 |
| Deliberately invalid controls rejected | 11 / 11 |
| Clean foreign-namespace control | Passed |
| Accepted expected-outcome commands | 39 / 39 |
| Final production source/object identities | 54 / 54 |
| Exact dependency Git revisions checked | 9 / 9 |
| Flat current source copies checked | 54 / 54 |

The seven mathematical modules and import-only root contain 44 public theorem declarations, nine definitions, six abbreviations and one scoped instance. The larger owned inventory includes private/generated supporting declarations. These are not counts of independent discoveries.

Only `propext`, `Classical.choice` and `Quot.sound` appear as transitive axioms. No production placeholder or custom axiom passed the audit. Invalid fixtures, audit I/O instrumentation and archived failed drafts are not production proofs.

**The 46 predecessor sources were not freshly recompiled in this run.** Their source/object bytes were authenticated and copied into isolated imports. The eight additions and new boundary module were freshly compiled in initially empty output directories. No development object substituted for an accepted new compilation. Every logical production declaration and boundary declaration was then replayed from an upstream-only starting kernel environment. Exact replay/ownership name sets match; the seven runtime helper names match separately. The corrupt-proof control was rejected by the actual kernel. Duplicate generated theorem data are accepted only when their type, universe parameters, theorem group and proof expression are identical.

## Boundary checks

The rational quaternion tests exercise genuinely noncommutative scalars. Three natural copies for M_2(H) have rank two, five have rank three, and one generator cannot produce three copies. Right-division coefficient order is verified and a reversed quaternion order is proved to fail.

A heterogeneous product has one quaternion factor and one rational factor. Its seed bound is a maximum, not a sum. The tests check literal regular columns, A-linearity, inverse identities, natural-factor simplicity and zero action from another factor. Absent multiplicities, empty products and zero modules are covered.

The zero-size counterexample shows that d>0 is essential to the row criterion and natural rank-one statement. The finite-algebra theorem is also instantiated on a noncommutative square-zero quaternion extension, with rational finite-dimensionality proved via its actual equivalence to H × H.

All these are exact Lean assertions. Missing finite-generation and semisimplicity assumptions, the false positive-size application, wrong ceiling/product counts and reversed coefficient use are deliberately rejected. Foreign-namespace custom axioms and a placeholder compiled with warnings disabled are rejected by the ownership guard. A clean foreign-namespace theorem is accepted.

## Publication coverage

All 108 stored statements, prose proofs and source-location/hash records are unchanged. Among the 69 proof-level records: **26 covered, 25 partial and 18 not mapped**. These are reviewed correspondence categories, not a blanket completion percentage.

The regular-module multiplicities lemma, full nonsplit semisimple theorem, algebraically closed split formula, full-matrix corollary and multiplicity-obstruction corollary move from partial to covered. The Wedderburn-Artin classical input becomes integrated. The original 35-row contract is not rewritten. The coverage generator is gated on final acceptance and was rerun byte-identically.

The positive-size natural-module convention remains explicit in the coverage notes. The split corollary's original-ring wording is handled by its own theorem rather than silently replaced by a quotient-ring statement.

## Failures and recoveries

The development index records 30 compiler receipts: 18 zero-exit exploratory runs and 12 rejected drafts/API probes. Two additional foreground interruptions have preserved snapshots/logs but no accepted exit receipt. No exit code is invented for them.

Rejected drafts involved API names, warning-fatal unused assumptions and instance syntax, noncommutative scalar-action rewriting, quotient ring-hom inverse inference, cardinal ceiling casts, universe elaboration, and test scalar/finiteness instances. Corrections preserved the intended mathematical hypotheses rather than weakening the audit. A streaming execution mode failed before execution; ordinary execution recovered the offline runtime. Two source inspections used the wrong directory and were corrected.

None of these exploratory or interrupted attempts contributes to PASS. The accepted launcher completed every required check. Its recorded elapsed time is 743.737 seconds, excluding development, runtime recovery and final packaging.

## Trust and reproduction

The combined `run_block08.sh` launcher was actually executed. Every command has an observed outcome and preserved log/hash. The runtime and all nine dependency revisions are authenticated. Mathlib's pinned cache is reused, not rebuilt or fully replayed. Replay uses Lean's own kernel, not an independent verifier. The TeX-to-Lean map is reviewed semantic correspondence, not kernel parsing of prose.

The source/evidence package includes the complete unchanged predecessor and a byte-identical flat 54-module source tree. The large portable runtime remains external. Publication PDFs and prior license-status records are unchanged. The constructions remain noncomputable; no executable Wedderburn, canonical-form or numerical eigensolver is claimed.

## Next restart

Stay on Paper I. Proceed to algebraic exact-sequence generator bounds, actual invariant-submodule packet restriction and quotient descent, then packetwise exactness and induced transfer blocks. Construct the quotient projector family from invariance, rather than assuming an unrelated quotient family. The semisimple, radical-top, primary, geometric and cyclic-classification blocks are now established and must not be reconstructed as missing work.

Other packet/functorial/topological and executable obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep. `evidence/HANDOFF_POSTFLIGHT.json` records final process and file checks.
