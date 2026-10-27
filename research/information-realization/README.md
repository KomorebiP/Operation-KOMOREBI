# Komorebi Information Realization
## v0.4.0 — Lean block 1

**Date:** 15 October 2026  
**Status:** 58 named theorem declarations compiled in Lean, with warnings treated as errors, an axiom audit for every theorem, and five negative-control checks. The declarations include supporting lemmas, not 58 independent research results. This is the first formal block, not a claim that the entire information program is formalized.

This release preserves the unchanged v0.3 package under `prior/` and adds a genuine Lean project. It does not replace paper proofs or Python evidence with unchecked Lean syntax.

## Main checked result

Let R be the decoder's linear observation, F the linear task, and U the helper's accessible linear observation. The underlying domain is a vector space over a division ring. On finite-field finite-dimensional spaces this specializes to the setting of the v0.3 paper.

* Exact recovery from all accessible information is possible exactly when `ker R ∩ ker U ⊆ ker F`.
* Under this condition, a **linear** helper code exists into the obstruction subspace `D = F(ker R)`. A linear decoder recovers F from R and that message.
* Every correct helper code, even nonlinear, has at least `|D|` messages.
* For finite fields, `|D| = q^d`, where `d = dim D`.
* The dimension is exactly `rank [R;F] - rank R`, represented in Lean by ranks of linear-map ranges.

The proof constructs the helper map by extension from its accessible image. It does not assume the desired optimal encoder as a hypothesis. The separate certificate-soundness theorem deliberately takes a certificate equality as an input.

## Other checked results

The foundational module proves recovery/factorization, explicit obstruction impossibility, access constraints, and an arbitrary-code alphabet lower bound. The predictive module constructs the operational quotient itself, its induced actions, and its universal factorization property. It proves simulation under every finite action word.

The Haar module proves the repair and closed dynamics symbolically over every field in which `2 ≠ 0`. The all-time result quantifies over every natural time index. It is not limited to a finite trajectory test. It also proves the invisible source direction, first-detail access impossibility, the single-field-symbol lower bound, a concrete GF(5) result, and the characteristic-two collision.

| Module | Named theorem declarations |
|---|---:|
| Foundations | 13 |
| LinearAccess | 9 |
| OptimalRepair | 4 |
| Dimension | 2 |
| Predictive | 13 |
| Haar | 17 |
| **Total** | **58** |

## Reproduce offline

The existing portable runtime is required but is **not duplicated in this small archive**. It is Lean **4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

From an extracted copy of this package, run:

```bash
python3 tools/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --label local_replay
```

This builds serially with `-j1 -DwarningAsError=true`. It deletes only this project's own `.lake/build/lib/lean` directory before compiling, does not download anything, checks compiler and Mathlib pins, audits all 58 theorem dependencies, and executes the expected-rejection controls. A nonzero exit indicates an unsuccessful verification. Logs and a JSON report are placed under `reports/local_replay/`.

The portable kit requires Linux x86-64. The current execution was Linux x86-64, not native Windows. The command can be used inside a matching WSL environment, but no new Windows/WSL execution is claimed here.

For a normal Lean installation, `lean/lakefile.toml`, `lean/lean-toolchain`, and the pinned dependency manifest are included. The completed runs used the offline driver above, not a newly fetched Lake dependency tree.

## Trust and status

All theorem dependencies are within Lean's standard `propext`, `Classical.choice`, and `Quot.sound`; 16 theorem declarations have no axiom dependencies. No production theorem uses `sorryAx`, added axioms, `native_decide`, or a compiler-trust shortcut. Definitions used across the new module boundary are explicitly exposed.

The `NegativeControls` directory intentionally contains a rejected placeholder and an injected axiom. These are adversarial test fixtures, excluded from the production library, **not premises of any of the 58 theorems**. The custom-axiom test is accepted by Lean as an explicitly axiomatized statement and then rejected by the independent dependency allowlist. Compiler exit status alone is not considered sufficient.

The earlier Python construction algorithms, the native floating-point Haar implementation, entropy/risk theorems, and the finite-step linear closure algorithm have not all been proved in Lean. See `FORMALIZATION_LEDGER.md` for exact boundaries.

## Navigation

`LEAN_GUIDE.md` maps notation to declarations. `AUDIT_REPORT.md` records failed development attempts and successful replays. `DECLARATIONS.json` gives every theorem name and source location. `PROGRESS_LEDGER.md` states the restart point. `reports/clean_run_02/SUMMARY.json` is the strengthened clean run. `reports/archive_replay/SUMMARY.json` records verification from a separate extracted source archive. `MANIFEST_SHA256.json` covers delivered files.
