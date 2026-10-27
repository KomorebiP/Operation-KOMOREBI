# Realization Boundaries — Lean companion v0.2.0

**Komorebi P. · Realization Calculus**

The algebraic and topological foundation now includes the **actual canonical profinite completion theorem**. For every rational subspace W of the concrete quotient P/D, the group H_W has a continuous additive equivalence from its Mathlib profinite completion to the fixed prime product P. The equivalence respects the original inclusion, and the full profinite topology equals the induced product topology.

## Scope

The nine original modules are unchanged. Six new modules close the reverse pure-preimage correspondence, countability, product topology and density, finite-target extension and restriction equivalence, and the canonical profinite-completion comparison. The proper inclusion D → G_a is not surjective, but its extension to canonical completions is an isomorphism.

The accepted audit rebuilt 15 production modules and one entrypoint, checked 391 project declarations (including generated helpers), ran 36 positive contracts and 14 intended rejections, and replayed all fifteen production modules through Lean's kernel. There are 146 explicitly named source theorem/lemma declarations. See `LEAN_VERIFICATION_REPORT.md` for the exact gates and trust boundary.

**This is not full-book formalization.** Unmarked classification, the complete homomorphism/endomorphism theory, seed ranks, exact root counts and CRT, computability semantics and grammar diagonalization remain. The 45-result coverage ledger distinguishes finished statements from checked prerequisites.

## Reproduction

Use the existing Linux x86-64 portable kit `Komorebi_Portable_Lean_4.34.0-rc2`, including its pinned package cache. From this directory:

```bash
export KOMOREBI_LEAN_KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-new-audit
```

Choose a new output directory. The runner refuses to overwrite evidence, checks dependency revisions, clears project build output, compiles serially with automatic implicit parameters disabled and warnings as errors, audits exact declaration types and axiom dependencies, runs the controls, and performs project-module kernel replay. It compares source and imported-cache/compiler hashes at the recorded endpoints. The toolkit is usable in a compatible x86-64 Linux environment, including WSL2, not as a native Windows or ARM executable. Python 3.10+, Git and the portable kit's prerequisites are required. No network requests or dependency upgrades occur during verification.

The archive does not duplicate the multi-gigabyte runtime. Restore it from the existing five-part compact archive when needed. Runtime identity and restoration metadata are under `provenance`. A normal `lake build` is a separate compilation check, not a substitute for the full verifier.

## Source organization

| Module | Mathematical role |
|---|---|
| `Ambient` | Actual prime product, finite support, torsion and annihilators |
| `Quotient` | Actual quotient, unique integer division, derived rational module |
| `Preimages` | Rational preimages, exact root criterion, purity and separation |
| `FiniteQuotients` | Canonical quotient equivalences and finite-target kernels |
| `Extensions` | Rational quotient, reducedness and nonsplitting |
| `Sections` | Explicit rational lifts and unique normal forms |
| `Cocycle` | Finite-support bounds, cocycle laws and nonremovability |
| `PairedPrimes` | Every binary selector and its marked divisibility tests |
| `NormalForms` | A genuine twisted-addition group and its realization equivalence |
| `PureCorrespondence` | Reverse construction and order equivalence |
| `Countability` | D, normal forms, countably infinite paired groups and quotient criterion |
| `ProductTopology` | Product topology, density and open congruence kernels |
| `FiniteTargets` | Continuous extension, uniqueness and finite-target naturality |
| `ProfiniteCompletion` | Mathlib completion, comparison maps, inverse laws and topology equality |
| `CompletionConsequences` | D and paired specializations, residual finiteness and proper inclusion |

`docs/NEW_FORMAL_SCOPE.md` explains the proof route. `docs/EXACT_STATEMENT_REVIEW.md` quotes the exported endpoint types. `docs/NAMED_THEOREMS.json` maps named source results to exact types, line numbers and axioms. `docs/MONOGRAPH_COVERAGE.json` records every numbered book result. `PROGRESS_LEDGER_v0.2.0.md` gives the next restart point.

## Evidence and trust

The authoritative evidence is `verification/accepted_v0.2.0`. The v0.1.0 accepted run is retained under `verification/history/v0.1.0`, and historical documentation is retained under `docs/history/v0.1.0`. Failed development attempts are not relabeled as passes. Intentionally invalid files in `tests/negative` are excluded from production imports and include axiom, admitted-proof and unsafe-declaration tests.

Production permits only `propext`, `Classical.choice` and `Quot.sound`. The compiler, Lean's kernel, hardware and imported compiled dependencies are trusted. Kernel replay uses the same Lean kernel, not an independent implementation. Imported caches and the compiler were not rebuilt or independently authenticated upstream. These are mathematical Lean proofs, not conclusions inferred from finite Python tests. Noncomputable choices do not establish oracle-computability or extraction claims.

The publication PDF and final source ZIP remain unchanged. Their earlier verification statements are historical; this companion records the current formal scope without silently rewriting the book.

## License

The project Lean source and verification tooling remain MIT licensed under Komorebi P. Dependencies retain their upstream licenses and are not bundled here. No historical-priority or external-review claim is made.
