# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–04 · v0.4.0

**PASS: 304 theorem declarations, 372 audited named declarations, 20 mathematical modules, 23 negative controls.** The authoritative completed audit is `verification/final/report.json`. Block 04 adds **94 theorems** and **15 definitions**. All 15 Block 03 mathematical source files remain byte-identical and are freshly recompiled. The cumulative theorem count is 265 authored in this full-edition program plus 39 recovered Paper VII declarations.

The source is the included **550-page Projector-Refinement Physics: Complete Unified Theory**, not the shorter Physics Guide. This release formalizes Chapter 2's selected foundations and Chapter 4's selected transfer extensions under explicit finite-atlas, bounded-operator and finite-matrix assumptions. It does not formalize all 550 pages.

## Block 04 additions

| Module | New theorem declarations | Content |
|---|---:|---|
| `TensorAtlas` | 17 | Constructed Kronecker atlas, arbitrary joint-state marginals and joint probability derivatives |
| `PartialTrace` | 32 | Explicit reduced matrices, positivity, trace preservation, local algebra and actual derivatives |
| `InformationTransport` | 12 | Actual Shannon, real-power moment and Rényi derivatives, including direct matrix-flow interfaces |
| `EntanglementWitness` | 5 | Proved positive-partial-transpose condition for finite nonnegative product mixtures |
| `QuantumInformationExamples` | 28 | Exact Bell density, finite-mixture exclusion, marginal counterexamples and information-rate tests |

Read `docs/BLOCK_04_PROOF_GUIDE.md` for the mathematics, `docs/SOURCE_MAP.md` for the equation map, `STATUS.md` for scope, and `CONTINUE_HERE.md` before extending the library. Previous proof guides and evidence are retained.

The tensor-marginal theorems apply to arbitrary joint states, not only product states. Reduced-state positivity follows from an already PSD input. The entropy laws are actual derivatives; matrix interfaces derive component balance from the original von Neumann equation. Strict positivity, nonempty support where needed, and q≠1 are explicit. Packet entropy is not claimed to be von Neumann entropy or monotone in time.

## Verify locally

Use Linux x86-64 or WSL with the restored exact-pin kit:

```bash
bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Equivalent command with an explicit evidence location:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

Lean is **4.34.0-rc2** and Mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier checks all nine dependency revisions and clean tracked trees, removes local compiled outputs, rebuilds all 20 mathematical modules plus the aggregate with one worker and warnings as errors, audits every inventoried name in bounded module batches, and requires each invalid control to fail with its intended proof diagnostic. Timeouts and import failures do not count as proofs or successful controls.

Only `propext`, `Classical.choice` and `Quot.sound` are permitted axiom dependencies. All definitions and structures in the inventory, including the proof-bearing tensor construction, are audited. No active admissions, custom axioms or native-evaluation proof escapes are allowed. The imported Lean/Mathlib cache is used, not rebuilt wholesale.

`verification/final/report.json` records the completed cumulative audit. `verification/block03_baseline/` records the independently rerun 210-theorem starting point. Earlier successful reports and both failed and successful development attempts are retained. `docs/BLOCK_04_FAILURES.md` separates mathematical, proof-script, and environment issues.

The multi-gigabyte compiler/dependency runtime is **not** duplicated in the source ZIP. Its seven-part assembler and exact checksums are under `runtime_restore_support/`. All seven runtime parts were restored and verified in the production session; their availability is not implied by the source ZIP itself.

## Recheck a packaged release

```bash
python3 scripts/recheck_archive.py --archive /path/to/Komorebi_Physics_Lean_v0.4.0_Checked_Block_04.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /path/to/new-empty-parent --out /path/to/recheck-evidence
```

The destination must not exist. The script checks ZIP integrity, extracts safely, verifies manifest hashes, invokes the extracted cumulative verifier, then checks hashes again and compares proof-input hashes, counts, dependencies and axiom inventories against the packaged report. Local proof outputs are rebuilt; imported pinned dependency caches are reused.

## Limits and next target

No ODE existence/uniqueness, positivity preservation from initial data, infinite-dimensional trace-class extension, countable/unbounded limit, q=1 entropy limit, automatic entropy monotonicity, gravity/cosmology proof or observational confirmation is claimed. The information-rate affine trajectories are local positive witnesses, not globally positive solutions.

Next: **Chapter 4.7, Lindblad packet jumps (4.45)–(4.52)**. Derive the diagonal population equation from the actual matrix generator, including square-root rates, anticommutator factors and index orientation. Chapter 3's unit/variational/asymptotic claims remain separately uninventoried. There is no justified full-edition completion percentage.
