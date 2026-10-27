# Paper I completion: Block 07

**Result: PASS for the noncommutative Nakayama/module-top/local-residue development, the authenticated predecessor, and upstream-only whole-project logical kernel replay.**

**Date:** 11 October 2026. **Version:** 0.7.0.

This closes two proof-level publication records and integrates the noncommutative Nakayama classical input. It does not claim that the entire expanded monograph is formalized. All predecessor mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For an arbitrary unital ring R and a finitely generated left module M, with J = Jac(R), the source proves the exact set/family equivalence and canonical equality

    S generates M iff its image generates M/JM over R/J,
    seedRank_R(M) = seedRank_{R/J}(M/JM).

Any chosen lifts of a generating quotient family generate upstairs. The actual quotient scalar action, surjectivity and exact kernel are proved separately. The rank equality uses the existing canonical minimum, with both cardinal inequalities derived from genuine generating sets. A natural seedFinrank equality is also proved. No commutativity, Noetherian, finite length or semisimplicity assumption is imposed.

The Nakayama theorem itself accepts ANY left ideal I contained in the Jacobson radical and proves N + IM = M implies N = M. Only the later ring-quotient statements need I to be two-sided.

For a genuinely noncommutative local ring, the source establishes uniqueness of the maximal left ideal and maximality of the actual Jacobson radical. It constructs the division-ring structure on R/J internally, then proves

    seedRank_R(M) = dim_{R/J}(M/JM),

where dimension is LEFT vector-space dimension. A commutative residue field is not substituted, and no division-ring or rank certificate is supplied by the caller. These are classical mathematical results integrated into Paper I, not claims of new classical discoveries.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | 1697 / 1697 |
| Entire predecessor compared with original ZIP | 1698 / 1698 files |
| Unchanged predecessor source/object pairs authenticated | 42 / 42 |
| New production modules freshly compiled | 4 / 4 |
| Original normative contract preserved | 35 rows, 84 mapped declarations |
| Public-or-coverage names resolved with types and axioms | 316 / 316 |
| Source-owned entries inventoried and axiom-audited | 1544 / 1544 |
| Logical production declarations rechecked | 1537 / 1537 |
| Generated partial runtime helpers separately inventoried | 7 |
| Production module closure replayed | 46 modules |
| Additional boundary module freshly compiled and replayed | 1 / 1 |
| New public mathematical boundary assertions | 19 / 19 |
| Total logical replay entries including boundary helpers | 1582 |
| Deliberately invalid controls rejected correctly | 10 / 10 |
| Clean foreign-namespace control accepted | 1 / 1 |
| Accepted expected-outcome commands | 34 / 34 |
| Final production source/object identity checks | 46 / 46 |
| Exact dependency revisions checked | 9 / 9 |

The new source has 23 public theorem declarations, one definition and three abbreviations in three mathematical modules and one import-only root. Its 31 compiler-owned entries include generated supporting declarations. None of these counts measures independent mathematical discoveries.

**The 42 predecessor sources were not freshly recompiled in this block.** Their source/object bytes were authenticated. The four additions and the new boundary module were freshly compiled into isolated initially empty output directories. Development objects were not substituted for accepted new compilations. Earlier boundary suites remain historical evidence, not newly rerun test suites here.

Only `propext`, `Classical.choice` and `Quot.sound` appeared as transitive axioms. No authored production placeholder, custom axiom or prohibited unsafe/partial declaration passed the source and ownership gates. Intentionally invalid fixtures and audit I/O instrumentation are outside that production-source claim.

## A substantive audit classification correction

The broader object audit identified seven inherited compiler-generated partial runtime helpers ending in `_unsafe_rec`. Previous inventories included them without distinguishing them from logical declarations. Lean's official replay excludes such runtime implementations, so it would be inaccurate to call every one of the 1544 inventory entries a separately kernel-replayed logical declaration.

This block explicitly separates **1537 logical production entries** from **seven generated runtime helpers**, while retaining the source ownership and axiom inventory for all of them. An unexpected partial declaration is rejected. The names and classification are preserved in the accepted receipt and raw object inventory. No predecessor mathematical source needed repair.

The new replay starts from authenticated UPSTREAM imports only. It verifies that none of the 46 production modules, the new boundary module, or any selected project constant is already trusted in that starting environment. It then replays the entire logical dependency closure. The exact set of 1582 rechecked names matches the ownership audit's logical production-plus-boundary set. The seven runtime names also match separately. This is a name-set check, not merely matching totals.

One duplicate generated theorem is merged only after its type, universe parameters, theorem group and proof expression are all shown identical. Incompatible duplicates are rejected. A separate corrupted-proof control presents the well-typed false claim 0 = 1 with the proof `Eq.refl 0`; the kernel rejects it. The accepted logs preserve the injection and rejection.

This strengthens project-dependency replay but remains Lean's SAME kernel, not an independently implemented verifier. No executable runtime-correctness claim is made for the generated helpers.

## Boundary tests

The noncommutative example is the trivial square-zero extension of the rational quaternion division ring. Its actual Jacobson radical is identified with the kernel of first-coordinate projection. The tests prove that epsilon is nonzero, epsilon squared is zero, the ring is noncommutative, its regular module has seed rank one, and its actual module top has residue-division-ring dimension one. The set {1 + epsilon} generates via the new lifting theorem.

The integer example has N = 3Z and I = 2Z: N is proper but N + I Z = Z. It demonstrates why the radical-containment hypothesis cannot be discarded.

The fraction field of Q[[t]], regarded as a Q[[t]]-module, has radical times module equal to the whole nonzero module. Its radical quotient has seed rank zero while the original module has nonzero seed rank. The test proves that the original module is not finitely generated. Thus finite generation is tested against a real mathematical counterexample, not only a missing typeclass instance.

Other assertions check actual quotient kernels/actions and zero-module behavior. All are exact Lean assertions, not numerical experiments.

## Publication coverage

All 108 stored statements, source proofs and source-location/hash records are unchanged. Among the 69 proof-level records there are now **21 covered, 30 partial and 18 not mapped**. These are correspondence categories, not an overall completion percentage.

`PSC-I-T-MODULE-TOP` and `PSC-I-C-LOCAL-ALGEBRA-FORMULA` move from not mapped to covered. `PSC-I-CI-NAKAYAMA` becomes classical_input_integrated. The semisimple formula remains partial, with its radical/top reduction now explicitly discharged. The separate original 35-row contract is preserved unchanged.

The deterministic coverage generator was actually rerun and produced byte-identical JSON and Markdown.

## Failures and recoveries

The development index records 19 compiler runs: 7 zero-exit exploratory runs, 10 rejected drafts/instrumentation runs, and 2 explicit 180-second driver timeouts. Failed source snapshots and logs are retained.

Failures included a looping rewrite, a missing prerequisite object, warning-fatal local-instance/unused-variable issues, test API/type corrections, and replay-wrapper syntax/indexing. The stricter object checks exposed generated partial helpers and an identical generated theorem duplication; the final audit classifies and checks those cases rather than pretending they were mathematical source repairs. Longer explicit execution limits replaced the interrupted development runs. A streaming execution mode was unavailable before command execution; ordinary execution was used. Minor source/coverage inspection errors are recorded separately.

None of those development or operational attempts contributes to final acceptance. The composed launcher was actually executed and all accepted checks completed. The accepted run recorded 975.159 seconds, excluding runtime recovery, development, coverage review and packaging.

## Trust, reproduction and next restart

The exact compiler and nine dependency revisions were authenticated. Mathlib's cached objects were reused, not rebuilt or fully replayed. Publication correspondence is reviewed semantic matching, not kernel interpretation of TeX prose. Mathematical constructions remain noncomputable. Publication PDFs were not rebuilt, and the existing license-status records were not changed. The large portable runtime remains an external prerequisite.

Run `bash scripts/run_block07.sh /absolute/path/to/pinned-runtime /absolute/path/to/new-output` from Linux or WSL. The output must not already exist. Do not update the dependency pins.

The next target is the nonsplit semisimple matrix/product seed-rank formula and regular-module multiplicities over arbitrary division rings, followed by abstract decomposition integration. The general radical/top reduction is now proved and must not be redone as though still missing. Packet/functorial/topological and executable-algorithm obligations remain in the map. Papers II–XII have not been rerun in this sweep.

Final process, source/object and artifact checks are recorded in `evidence/HANDOFF_POSTFLIGHT.json`. The full restart instructions are in `CONTINUE_HERE.md`.
