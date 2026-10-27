# Projector-Resolved Seed Calculus V
## First formalization block, v0.1.0

**Author: Komorebi P.**

**This is a source-candidate work package, not a completed or kernel-certified Paper V release.** The original 31-page adaptive-tree-resolved manuscript is included unchanged. Its SHA-256 matches the retrieved source checksum entry.

### Current status

| Item | Result |
|---|---|
| Manuscript inventory | 20 theorem-like results, 36 numbered records total |
| New Lean sources | Five proof modules, 29 theorem declarations |
| Lean compilation | Not run: `lake` and `lean` absent in the producing environment |
| New kernel-checked results | None reported |
| New exact finite tests | 12 passed; 25,825 counted assertions |
| Original 33-test companion suite | Not rerun; its source archive was not retrieved |
| Full verification command | Returned exit code 2, `BLOCKED_NO_LAKE` |
| Original manuscript edited | No; proposed repairs are in a separate supplement |

The candidates cover partition reconstruction, lifting, exact edge-error identities, finite objective selection, and recursively represented binary packet trees. See `THEOREM_LEDGER.md` for every remaining semantic and proof obligation. Candidate declarations are not the same unit as paper theorems, and neither number is a completion percentage.

### Start here

- `manuscript/Paper_V_Correction_Supplement.pdf`: four-page mathematical correction supplement, with editable LaTeX.
- `REVIEW.md`: detailed findings, scope limits, and the next proof sequence.
- `THEOREM_LEDGER.md`, `.json`, `.csv`: all 20 result records, mapped without claiming unverified coverage.
- `formalization/lean/`: candidate proof sources, a pinned toolchain and dependency lock, and a future theorem-kind/axiom audit.
- `tests/`: newly written standard-library rational reference models and tests. They are not translations executed by Lean.
- `verification/`: actual test logs, static checks, blocked formal-check status, and the future verifier.
- `provenance/`: baseline identity, source hash, extraction register, and package scope.

### Reproduce the checks

From this directory, run the independent finite tests and lexical/source-contract checks:

```powershell
python verification/verify.py --static-only
```

The static result is explicitly `STATIC_AND_EXACT_ONLY`, not a Lean pass. The full command is:

```powershell
python verification/verify.py
```

It stops with a nonzero status when Lean is absent or a gate fails. `VERIFY.ps1` and `VERIFY.sh` wrap these commands. A successful future run can verify the 29 candidate targets; it will still not certify full manuscript coverage or rewrite the ledger as complete.

The intended Lean version is `leanprover/lean4:v4.34.0-rc2`, with Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, matching the pins in the attached Paper IV release. The toolchain and dependency cache are **not bundled**. On a system where `lake` is already available and the dependencies can be fetched, cache setup is:

```powershell
Push-Location formalization/lean
lake exe cache get
Pop-Location
python verification/verify.py
```

These setup commands are supplied for reproduction. They were not run successfully in the producing environment. Candidate source and audit-harness elaboration errors may still require correction after a real Lean build.

### Corrections established in the supplement

The selector's empty competitor minimum needs a singleton case. Dynamic programming needs a tie rule. The channel-delay unit must be distinguished from original-sample delay. The Smith action must handle poles, including the zero-to-infinity half-turn. Probability bounds require a joint event, and the analytic and measure-theoretic theorem hypotheses need to be explicit. These repairs preserve the intended finite results without claiming universal edge discovery or infinite-tree statistical theory.

Paper IV is not changed by this package. Its earlier formal-build limitation is not removed by starting Paper V.
