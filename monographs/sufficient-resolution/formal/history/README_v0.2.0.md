# Komorebi Sufficient Resolution — Lean v0.2.0

**Komorebi P. | 13 September 2026**

A cumulative checked release for exact resolution, compression defects, linear
globalization obstructions, behavioral quotients, and the discrete-memory bridge.

**125 explicit theorem declarations in 11 proof modules; 169 explicitly named
declarations audited.** This block adds 57 theorems in five modules. Counts include
helper lemmas and exact examples. All six original production source files are
unchanged. This does not update the theorem census of Papers I–XII.

## Main new result

For a visible/hidden linear system

    T = [[A,B],[G,D]],  E_n = C T^n R,  M_k = B D^k G,

where C selects the visible coordinate and R initializes hidden state to zero,
the release proves:

    E_n = A^n for every n
      iff M_k = 0 for every k
      iff E_(m+n) = E_m E_n for every m,n.

The exact discrete memory equation is derived from actual powers of T:

    y_(n+1) = A y_n + B D^n z_0
              + sum_{j=0}^{n-1} B D^(n-1-j) G y_j.

If the hidden space has dimension d over a field, the all-depth criterion reduces
to M_0,...,M_(d-1), or equivalently equality E_n=A^n through depth d+1. This includes
d=0. The visible space need not be finite-dimensional. An arbitrary supplied monic
annihilating polynomial gives a degree-controlled version even without a hidden
dimension assumption.

For ANY split compression C R=I, the release constructs the canonical hidden space
ker(C), proves both analysis/synthesis inverse laws, and transfers the same memory
and finite-horizon criteria to the original compressed powers C T^n R. No
orthogonality is required.

The finite tests are exact equalities of entire linear maps, not sampled states
or floating-point approximations. All-state closure, including arbitrary hidden
initial states, has the stronger criterion B=0.

## Contents

| Module | Theorems | Status |
|---|---:|---|
| ExactResolution | 15 | Unchanged |
| Compression | 19 | Unchanged |
| Globalization | 7 | Unchanged |
| ObstructionTransport | 5 | Unchanged |
| Behavioral | 14 | Unchanged |
| Examples | 8 | Unchanged |
| DiscreteMemory | 15 | New |
| MemoryClosure | 14 | New |
| FiniteMemory | 6 | New |
| SplitMemory | 10 | New |
| MemoryExamples | 12 | New |

- `BLOCK_02_THEOREMS.md`: formulas, scope, and exact Lean declaration names.
- `THEOREM_GUIDE.md`: original block guide plus the updated continuation link.
- `PROGRESS.md`: completed layers and remaining obligations.
- `CONTINUE_HERE.md`: restore procedure and the next recommended proof block.
- `AUDIT.json`: machine-readable claim boundaries.
- `verification/release/`: current source build, axiom lists, kernel replay and controls.
- `verification/roundtrip/`: extracted-archive clean rebuild and replay evidence.
- `verification/development_v0.2.0/`: unsuccessful draft diagnostics and subsequent passes.
- `verification/predecessor_replay/`: fresh v0.1.0 replay performed before extension.
- `verification/predecessor_sources.json`: byte-preservation audit of the original six sources.
- `history/Komorebi_Sufficient_Resolution_Lean_v0.1.0.zip`: original archive, unchanged.

## Verification and trust boundary

Pinned Lean/Lake: `leanprover/lean4:v4.34.0-rc2`.
Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
All nine dependency revisions are checked against the retained manifest.

The verifier deletes this project's compiled outputs, compiles serially with
warnings as errors, audits every explicitly registered declaration, and runs
`leanchecker` on every production module. It permits only `propext`,
`Classical.choice`, and `Quot.sound`. Production sources contain no `sorry`,
`admit`, custom axioms, `unsafe`, or `native_decide`. Deliberately invalid controls
are isolated in verification directories, never imported by the production root.

The kernel replay uses Lean's own kernel, not an independently implemented proof
checker. Imported Lean/Mathlib objects are reused. In particular, Cayley-Hamilton
is an imported proved Mathlib theorem, not a new discovery claimed by this release.
No historical novelty or priority claim follows from verification.

The Python controls include the five original rational checks and 1,307 exact
assertions across 20 block systems, hidden dimensions 0–3, visible dimensions 1–2,
and evolution depth at most 9. They test implementation and indexing only. The
universal mathematical conclusions are established by the Lean proofs, not by
those finite controls.

## Reproduce

The multi-gigabyte portable runtime is not duplicated in this source/evidence ZIP.
Use the preserved Linux x86_64 runtime, which also runs under x86_64 WSL:

```bash
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/validate_manifest.py verification/local-replay/computation-manifest.json --root .
```

No downloads are required once that pinned runtime is restored. The Python checks
use only the standard library. The verifier's default output preserves the shipped
release evidence. Its default per-command limit is 180 seconds, with Lean restricted
to one thread. Native Windows and WSL execution were not tested in this run.

## Remaining boundaries

The selected discrete-memory/finite-certificate block is complete under its stated
algebraic hypotheses. Continuous-time Volterra/semigroup analysis, norm stability,
Hilbert-space obstruction decomposition, positivity-constrained realization,
constructive finite behavioral minimization, nonlinear descent, and arithmetic
existence remain separate obligations. A conditional generic algebraic criterion
does not establish a domain-specific realization or a Langlands correspondence.
