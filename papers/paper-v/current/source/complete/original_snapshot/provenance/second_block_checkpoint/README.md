# Projector-Resolved Seed Calculus V
## Second proof-development block, v0.2.0

**Author: Komorebi P.**

**Classification: UNCOMPILED LEAN SOURCE CANDIDATE.** None of the 75 theorem declarations in this bundle has been accepted by a Lean process in the producing environment. The mathematical reference tests and source-contract checks pass. The full verification command exits **2, BLOCKED_NO_LAKE**.

This is a continuation of `PRSC_V_v0.1.0_First_Block.zip`, using the same 31-page adaptive-tree-resolved manuscript. It is not a certified replacement for the paper and does not assert complete formalization.

## What changed

The first block contained 29 candidate theorem declarations in five proof modules. This block adds 46 declarations in four new modules, bringing the inventory to **75 declarations in nine proof modules**. The root import and kernel-audit candidate cover all 75 targets. Eleven `.lean` files are present when the root import and audit are included.

| New module | Declarations | Scope |
|---|---:|---|
| `IntegerPolyphase.lean` | 11 | Concrete signed quotient/remainder coordinates, two inverse laws, divisible-modulus refinement, channel and original-sample delay conventions |
| `FIRTransfer.lean` | 6 | A bijective FIR tap reindexing and finite-support time-domain polyphase transfer with literal kernels |
| `FiniteAdaptive.lean` | 17 | Arbitrary positive finite branching, recursive cuts, exact synthesis, finite minimization, best-basis optimality, exact envelopes, and strict-gap stability |
| `FiniteTransforms.lean` | 12 | Flat even-length indexing, lifting inverses, exactly normalized real Haar identities, and an abstract matrix criterion |

Declarations are not manuscript results. The paper's ledger still has **20 theorem-like statements**. Do not divide the two counts to estimate completion.

## Actual checks

| Check | Outcome |
|---|---|
| Inherited exact reference suite | 12 tests passed, 25,825 counted mathematical assertions |
| New second-block exact suite | 8 tests passed, 280,108 counted mathematical assertions |
| Verifier controls | 14 tests passed, including mutation rejection, missing targets, pins, timeout logs, and Python `-O` |
| Total mathematical assertions | 305,933, excluding uncounted unittest checks and verifier assertions |
| Frozen source hashes, target inventory, import and audit coverage | Passed |
| Ordinary and optimized-Python static verification | Passed; no Lean check was requested by that mode |
| Full verification | Blocked because `lake` is absent, exit code 2 |
| Fresh Lean elaboration, compilation, and axiom audit | **Not run** |
| Original manuscript's reported 33-test companion suite | Not rerun; it is not the independent suite in this bundle |

The new tree tests cover all 626 ordered rooted tree topologies with one through eight nodes, including unary branches and arity seven. They compare 129,958 node subsets with an independent root-to-terminal path predicate. They check 3,130 rational cost assignments against exhaustive pruning minimization and 471 exhaustive small integer objectives. These are finite regression checks, not a universal proof or Lean execution.

Normalized Haar is tested in the exact field Q(sqrt(2)), not with floating-point tolerances. Integer and FIR checks include negative indices, signed delays, and very large addresses.

## Run the checks

Python 3.10 or newer is sufficient for the exact tests. They use the standard library only.

From the unpacked root in PowerShell:

```powershell
python verification/verify.py --static-only
python verification/verify.py
```

Equivalent wrappers are `VERIFY.ps1 -StaticOnly`, `VERIFY.ps1`, and `bash VERIFY.sh`. The shell wrapper forwards arguments, including `--static-only`.

`--static-only` includes all three Python suites and source checks. It deliberately makes no Lean claim. Without that flag, a missing `lake` produces exit 2, not success. Other failed gates produce exit 1. An actual pinned build and audit must succeed before the verifier can report candidate-target kernel checking.

The compiler pin is `leanprover/lean4:v4.34.0-rc2`. The mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. These were inherited from the first block and Paper IV's configuration, not its verification status. Dependencies and toolchain binaries are not bundled. A machine without those dependencies cannot perform an offline Lean build from this archive alone.

Source hashes are intentionally strict. After editing a proof, the recorded hashes, theorem source locations, and audit targets will need a deliberate reviewed update. The manifest is an unsigned integrity check, not proof authenticity or a compiler substitute.

## Reading order

`REVIEW.md` gives the new results and limitations. `MATHEMATICAL_NOTES.md` gives ordinary mathematical derivations behind the main additions. `THEOREM_LEDGER.md`, `.csv`, and `.json` map each paper result to candidate source and the remaining scope. `verification/` contains actual logs and machine-readable reports. `provenance/first_block_verification/` and `provenance/first_block_documents/` contain historical evidence, not current verification.

The original manuscript and the first block's four-page correction supplement are retained unchanged. No new PDF certification label has been added.

## Remaining boundaries

The important remaining bridges are the infinite-dimensional Hilbert-space statements, the complete reverse equivalence between recursive cuts and the paper's set-valued antichains, the filter-bank/matrix representation, and the measure-theoretic packet perturbation theorem. The formal-series cyclic product, projective Smith action, and CRT specialization remain untouched by the new source modules.

The Lean selector is a mathematical specification, not a verified efficient runtime implementation. Its comparison-count recurrence is separate from the actual two-traversal Python implementation. No Lean runtime complexity or constant-cost rational arithmetic claim is made.
