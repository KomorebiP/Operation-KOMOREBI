# Projector-Resolved Seed Calculus V, v0.3.0

Author: Komorebi P.

**All 133 included Lean theorem targets in 14 proof modules passed a fresh pinned build and the namespace-wide axiom audit. All 75 inherited candidates are included. Paper V as a whole is not yet fully formalized.**

The verifier completed with exit code 0 and `lean_kernel_checked: true`. Only `propext`, `Classical.choice`, and `Quot.sound` are permitted by the audit. No new axioms or proof placeholders are allowed. The manuscript still contains 20 theorem-like results; 133 supporting declarations is not a paper-completion percentage.

## What is now checked

- Signed integer polyphase coordinates, both reconstruction laws, literal FIR tap reindexing and time-domain transfer.
- Finite lifting, normalized finite real Haar, and normalized Haar reconstruction and energy on entire complex l2 channels.
- Bounded complex l2 packet operators, operator-level refinement, symmetry, orthogonality, norm-preserving polyphase coordinates, impulse expansions, dense shift-generated span, and integer shifts.
- Arbitrary positive finite branching, global cut optimization, exact perturbation envelopes, gap stability, singleton handling, and probability transfer from a joint event.
- A two-way equivalence between recursive cuts and set-valued complete prunings, and between the exactly-one-path-hit condition and covering antichains.
- CRT residue-mask factorization with dyadic-odd specialization.
- Homogeneous Smith action composition and scale compatibility, plus admissible finite-chart composition and zero/infinity half-turn identities.

## Verification

| Check | Result |
|---|---|
| Fresh build after deleting the project's compiled output | PASS |
| Pinned Lean 4.34.0-rc2 | PASS |
| Pinned revisions and clean tracked sources for all nine dependencies | PASS |
| Axiom audit of 133 explicit targets and all project-namespace declarations | PASS |
| Source hashes, inventory, imports, and audit coverage | PASS |
| Mathematical reference tests | 20 passed, 305,933 counted assertions |
| Static verifier controls | 14 passed |
| Real compiler controls | Valid theorem accepted; false theorem rejected |
| Complete manuscript coverage | **Not certified** |

`verification/verification_status.json` is the authoritative report for this run. The static verifier-control suite reports its own compiler flag as false because that suite does not simulate a successful compiler. The separately executed full verification report records the real compiler and audit pass.

## Reproduce

Install the pinned Lean toolchain with a normal Lean/Elan installation. From `formalization/lean`, run:

```text
lake exe cache get
```

Then, from the unpacked package root:

```powershell
python verification/verify.py
```

`VERIFY.ps1` and `bash VERIFY.sh` are wrappers. `python verification/verify.py --static-only` runs the exact reference tests and source checks without claiming Lean verification. Python 3.10 or newer is sufficient for those standard-library tests.

The mathlib pin is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Toolchain and dependency binaries are not included, so first setup requires downloading them. The environment-specific application-path adapter used for this run is documented, with its source and real compiler controls, in `verification/runtime/RUNTIME.md`; normal installations do not need it.

The source contract must be deliberately regenerated after reviewed source edits. The checksum files are unsigned integrity records and do not replace Lean verification.

## Remaining paper coverage

Read `THEOREM_LEDGER.md` for all 20 results. The principal remaining obligations are legitimate transform-domain/filter-bank representations, finite-depth packet operators and their full energy decomposition, measure-theoretic mask bounds, the formal-series cyclic product theorem, and explicit specialization of the antichain cost and Smith cyclic-action constructions. The Hilbert Haar theorem is on entire channels; its final energy connection to the original interleaved signal is listed separately.

The selector's comparison-count theorem proves a structural recurrence. It is not a bound on Lean execution time. The original manuscript's reported 33-test companion suite was not rerun and is distinct from the independent suites here.

The original manuscript and correction supplement are unchanged. Prior block reports are retained under `provenance/`; their former missing-toolchain status is historical. This release certifies the included Lean targets, not every statement in the PDF.
