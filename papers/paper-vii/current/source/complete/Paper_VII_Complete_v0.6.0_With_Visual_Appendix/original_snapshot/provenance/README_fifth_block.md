# Projector-Resolved Seed Calculus VII
## Checked fifth block · v0.5.0

**Author: Komorebi P.**  
**Date: September 6, 2026**

This cumulative release completes the finite Knill–Laflamme criterion (item 8.1). It contains **256 Lean-checked theorem declarations across 20 modules**, including **55 new declarations in five modules**. The declarations include supporting lemmas, specializations and exact regression examples. They are not 256 independent manuscript theorems.

**18 of 19 named finite-sector manuscript items are fully checked.** Item 6.4 remains partial: its normed-parameter-space connection and curvature results are checked, but the global smooth range bundle and atlas gluing are not formalized. All five continuum conjectures remain unproved.

## Newly checked mathematics

| Module | Declarations | Role |
|---|---:|---|
| `KnillLaflammeSufficiency` | 22 | Actual unitary Gram diagonalization, null-error removal, positive-eigenvalue syndrome normalization and a total CPTP recovery |
| `KnillLaflammeNecessity` | 7 | Rank-one Gram and Kraus rigidity, Gram necessity derived from recovery, and the finite channel equivalence |
| `QuantumStateBridge` | 9 | Normalized density matrices versus code operators, complex polarization and arbitrary finite reference systems |
| `ErrorSpanRecovery` | 9 | The same decoder on all coherent error combinations, all normalized channels in the error span, and the general unnormalized error-family equivalence |
| `KnillLaflammeExamples` | 8 | Singular nonorthogonal errors accepted, full-space qubit dephasing rejected, and the zero-code case |
| **Total added** | **55** | **One additional complete named manuscript item** |

The channel theorem assumes actual Kraus normalization, `sum E_a† E_a = I`. It proves that a finite trace-preserving Kraus recovery exists on all code density matrices if and only if there is a positive semidefinite matrix C with `P E_a† E_b P = C_ab P`.

For an error family that is not normalized, `error_family_correctable_iff_gram` instead uses exact recovery with a single nonnegative, code-independent scale. Sufficiency gives scale `trace C`. It does not assert that a trace-increasing map is a channel, or that a zero error is inverted to a normalized state. `Data.recovery_span_channel` proves that the constructed decoder corrects every normalized channel assembled from the original error span.

The construction is explicit as mathematics but uses noncomputable spectral choices in Mathlib. This release is a formal proof development, **not a numerical decoder implementation or performance benchmark**. The Knill–Laflamme criterion is classical; the new contribution here is its completion and integration in this project's checked sources.

## Verification record

The current evidence is `verification/fifth_block_release_run/SUMMARY.json`. All 20 active sources were freshly compiled during this block, including the 15 byte-for-byte unchanged upstream modules. The final run was checkpointed in batches; cached messages refer only to verified checkpoints from this same new run, not to unrerun fourth-block claims.

Runtime: **Lean 4.34.0-rc2**. Mathlib revision: **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**.

Every final module returned exit code 0, with warnings treated as errors. All 256 theorem-level axiom reports passed the inventory check. Axiom dependencies are confined to `propext`, `Classical.choice` and `Quot.sound`; one upstream theorem is axiom-free. The active sources contain no admitted proofs, new axiom declarations, `unsafe`, or `native_decide`. Both deliberate invalid controls returned the expected rejection. Sixteen Python verifier regression tests passed.

There were **25 failed checks among 37 captured development checks**. Their logs and exact source snapshots are kept under `verification/fifth_block_development/`, separate from the successful final evidence. Deliberate verifier pauses return code 2 and are not proof failures. Development snapshots may contain invalid drafts and should not be imported as active modules.

This run did **not** rebuild Papers I–VI, rerun the original numerical suite, independently recheck all imported Mathlib proofs, or verify any continuum conjecture. Normal Lean compilation and axiom auditing do not by themselves certify that every informal sentence in the unchanged manuscript matches the formal statements.

## Reproduce with the portable kit

The multi-gigabyte portable runtime is not duplicated inside this release. Use the already assembled compatible Linux kit, including through a suitable Linux/WSL environment. No external download or package installation is part of the verification script.

From the extracted release directory:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_check
```

For a host with a short command limit, repeat this **same** command until the report is complete:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_check --max-checks 3 --resume
```

Exit codes are 0 for complete pass, 1 for failure and 2 for a saved incomplete checkpoint. Do not treat an incomplete checkpoint as a complete release verification.

The verifier now compiles local dependencies in order. It records hashes of transitive source dependencies, public/private Lean interfaces and IR outputs, the runner, the verifier, the inventory and logs. A missing or modified dependency invalidates reuse. Generated compiler caches are deliberately omitted from the distributed ZIP and recreated on verification. This also means that resuming the packaged historical report requires fresh compilation rather than trusting missing cache artifacts.

`check_low_memory.py` still lets Lake exit before launching Lean, limits Lean to one worker and treats warnings as errors. The added `--import-dir` and `--output` options let it build local module dependencies. It does not impose a RAM cap or reduce proof obligations. New modules use `import all` only for selected small local modules whose definitions must be unfolded.

## Package contents and preservation

- `formalization/`: the 20 active Lean modules.
- `manuscript/Paper_VII_Fifth_Lean_Block_Supplement.pdf` and `.tex`: statements, proofs, assumptions and remaining scope.
- `THEOREM_LEDGER.json` and `.md`: current manuscript-to-source coverage.
- `verification/`: final compiler output, declaration audits, controls, development failures, preservation comparisons and artifact checks.
- `provenance/`: upstream records and source versions, including the previous runner and verifier.

The 15 upstream proof modules, the original manuscript PDF/TeX and all four earlier supplements are unchanged. The preservation audit covers **26 retained files** from the exact fourth-block ZIP. The original manuscript is preserved, not silently rewritten to suggest that every result is now formalized.

`SHA256SUMS.txt` covers the distributed payload except itself. Its presence is an integrity record, not an independent mathematical proof.
