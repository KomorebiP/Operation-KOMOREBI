# Projector Resolved Seed Calculus — Paper VII
## Checked second block · v0.2.0

**Author: Komorebi P.**

This is a cumulative formalization release. Five additional named finite results are now checked in Lean. It is not a claim that the entire original manuscript or its continuum conjectures has been verified.

| Measure | First block | Second block, cumulative |
|---|---:|---:|
| Named finite manuscript items checked | 6 of 19 | 11 of 19 |
| Named finite items remaining | 13 | 8 |
| Lean theorem declarations | 32 | 82 |
| Active Lean modules | 4 | 9 |
| Continuum conjectures proved | 0 of 5 | 0 of 5 |

The new block adds **50 declarations** across **five modules**. Supporting lemmas, concrete specializations and audits are included in declaration counts. These are not counts of separate manuscript theorems or difficulty-weighted completion percentages.

## New checked results

| Item | Module | Declarations | Exact scope |
|---|---|---:|---|
| 2.4 Computational seed | `ComputationalSeed.lean` | 14 | Actual products of locally addressed Pauli X gates generate the full standard complex basis for every number of qubits. |
| 3.2 Tensor/polyphase refinement | `TensorRefinement.lean` | 11 | Arbitrary finite tensor factors and dimensions, then residue grouping preserving orthogonality, completeness and adjoints. |
| 6.1 Moving-frame Hamiltonian | `MovingFrames.lean` | 9 | Constructs the differentiated coordinates, proves the transformed equation and Hermiticity of the connection. |
| 6.3 Canonical packet connection | `CanonicalConnection.lean` | 9 | Derives projector identities from real derivatives and proves both formulas for C, skew-adjointness and its commutator identity. |
| 7.2 Finite Kraus channel | `KrausChannels.lean` | 7 | Complete positivity at every finite auxiliary dimension, linearity, trace preservation and density-matrix preservation. |

## Verification result

The recovered final run successfully recompiled all nine active modules. Every compiler exit code was 0. All 82 theorem declarations have matching `#print axioms` output. No theorem used an axiom outside `propext`, `Classical.choice`, and `Quot.sound`. The active modules contain no `sorry`, `admit`, new `axiom`, `unsafe`, or `native_decide` token after comments and strings are removed. All final module checks were warning-free under `-DwarningAsError=true`.

Both negative controls passed by being rejected: a deliberately false natural-number equality and a deliberate `sorry` placeholder. The negative-control sources are intentionally invalid and are not active proof modules.

Runtime: **Lean 4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.

Pinned Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

See `verification/second_block_release_run/SUMMARY.json` for commands, source hashes, exit codes, log hashes, theorem-by-theorem axioms and timings. The portable runtime's archive SHA-256 checks are recorded separately. Imported dependencies were reused, not independently rebuilt or rechecked.

## Reproduce

Use the previously delivered portable Linux kit. From this release folder:

```bash
python scripts/verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_rerun
```

On a host with a short command time limit, run the following command repeatedly until `COMPLETE PASS`:

```bash
python scripts/verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_rerun --max-checks 3 --resume
```

Exit code 2 means a deliberate checkpoint pause, not PASS. Exit code 1 means failure. Exit code 0 means the complete run passed. Resume accepts previously successful entries only after checking source, log, runner, runtime and theorem-inventory consistency. Use a new output directory and omit `--resume` for a wholly fresh rerun. Module mode, one Lean thread and the existing low-memory launcher are retained.

## Manuscript and provenance

The original Paper VII TeX and PDF are preserved unchanged. The first-block mathematical supplement remains included. The second-block supplement gives statements, proof explanations, exact formalization boundaries and reproduction instructions. `THEOREM_LEDGER.json` and `.md` are the current cumulative ledger. Historical first-block reports and metadata are explicitly separated.

The four original Lean modules are unchanged byte-for-byte and were recompiled. Their preservation hashes are in `verification/UPSTREAM_PRESERVATION.json`. The first-block Feshbach invertibility correction and the distinction between physical compression and full constraint closure remain valid and documented in the earlier supplement.

The execution session restarted during development, losing the working tree and raw second-block failure logs. The sources were reconstructed and all final checks rerun. `verification/DEVELOPMENT_HISTORY.md` distinguishes those lost development logs from the surviving final verification evidence. The verifier now writes resumable checkpoints.

## Still unchecked

Eight finite named results remain: 2.1 orbit dimension, 2.2 minimum quantum seed rank, 2.3 local orbit and Schmidt rank, 3.1 cyclic character projectors, 5.2 quantitative leakage, 6.4 manifold projected connection and curvature, 8.1 Knill–Laflamme, and 10.1 finite Euclidean transfer. Conjectures 12.1–12.5 remain unproved.

The original numerical suite was not rerun, and Papers I–VI were not rebuilt. Kernel checking of the stated Lean propositions is not by itself a guarantee that every sentence, figure or physical interpretation in the unchanged original manuscript has been validated.
