# Komorebi Sufficient Resolution — Lean v0.1.0

**Komorebi P. · 13 September 2026**

A first formal block for resolution, transport, composition defects, linear
globalization obstructions, and behaviorally sufficient quotients.

This release contains **68 explicit theorem declarations in six source modules**,
with **98 named declarations** (including definitions, structures, and abbreviations)
covered by the axiom audit. Counts include helper lemmas and concrete examples.
They are not a count of independent discoveries or a new census of earlier papers.

## What is proved

| Source module | Theorems | Formal scope |
|---|---:|---|
| `ExactResolution.lean` | 15 | Split analysis/synthesis, realizable coordinates, exact kernel representation with unique inverse, identity/addition/composition preservation. |
| `Compression.lean` | 19 | Retained/hidden idempotents, exact hidden-return factorization, defect coherence, defects of powers, sufficient invariant-lift closure, two-stage defect decomposition. |
| `Globalization.lean` | 7 | Actual quotient of compatible data by realizable data, zero class iff realizable, exactness iff all classes vanish, explicit uniqueness hypotheses. |
| `ObstructionTransport.lean` | 5 | Typed maps of presentation diagrams, induced obstruction maps, composition, preservation of zero, reflection only under injectivity. |
| `Behavioral.lean` | 14 | All-future invisible submodule, invariance, induced quotient dynamics/observations, full finite-word fidelity, kernel-minimality and a comparison map. |
| `Examples.lean` | 8 | Exact rational three-coordinate delayed return and inconsistent duplicate-coordinate examples. |

Every source is under `Komorebi/SufficientResolution/`; `Komorebi.lean` imports the whole block.
The detailed translation from formulas to Lean names is in `THEOREM_GUIDE.md`.

## Verification

Pinned environment:

- Lean and Lake: `leanprover/lean4:v4.34.0-rc2`.
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All nine dependency revisions are retained in `lake-manifest.json`.

The release verifier deletes and recompiles only this project's own compiled
modules, with warnings treated as errors. It audits every registered declaration
against the allowlist `propext`, `Classical.choice`, `Quot.sound` and replays each
of the six proof modules using `leanchecker`. This uses the same Lean kernel;
it is not independently implemented proof checking. The imported Lean/Mathlib
cache is reused, not rebuilt or replayed from scratch.

Production code contains no `sorry`, `admit`, custom `axiom`, `unsafe`, or
`native_decide`. Deliberately invalid control files are isolated under the
verification directories and are not imported by the library. The false theorem
and placeholder must be rejected. The custom-axiom control must compile and
then fail the axiom allowlist, demonstrating why compilation alone is insufficient.

`verification/release/report.json` is the machine-readable result.
`verification/release/axioms.json` and compiler/kernel logs preserve the evidence.
`verification/development/` retains diagnostics from unsuccessful drafts.
`DEVELOPMENT_NOTES.md` explains those failures and corrections.

## Replay using the preserved portable runtime

The multi-gigabyte Lean/Mathlib runtime is **not duplicated in this ZIP**.
Use the preserved `Komorebi_Portable_Lean_4.34.0-rc2` Linux x86_64 runtime:

```bash
cd /path/to/Komorebi_Sufficient_Resolution_Lean_v0.1.0
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This attaches the exact pinned cache, compiles serially, audits, runs negative
controls, replays project declarations, and executes five exact rational sanity
checks. No downloads are needed once that runtime is present. On Windows, this
is the Linux/WSL path; native Windows and WSL execution were not tested here.
All filesystem paths are supplied as arguments, including paths with spaces.

The default output is `verification/local-replay`, preserving the shipped
release evidence. `--timeout 180` is the per-command wall limit. Kernel replay
can be explicitly omitted with `--skip-kernel-replay`, but that produces a
weaker verification report and is not the release's verification standard.

Validate a report's manifest and pinned source hashes:

```bash
python3 scripts/validate_manifest.py verification/release/computation-manifest.json --root .
```

The validator is project-local, using the version-1 computation-manifest format.
The report additionally records before/after hashes of execution inputs.

## Boundaries

This is an algebraic formalization, not a claim that arbitrary compatible local
data globalize. The obstruction is constructed and characterized, not assumed
away. Positivity, probability normalization, integrality, causality, analytic
regularity, and arithmetic existence are not supplied by these generic theorems.

No Hodge/orthogonal reconstruction estimate, singular-value stability bound,
continuous-time memory integral, finite Cayley–Hamilton memory certificate,
finite-dimensional algorithmic stabilization bound, or Langlands correspondence
has been formalized in this release. The behavioral quotient is universal in
kernel-inclusion order; this release does not yet state a finrank inequality.

The earlier brainstorm remains a research plan. This ZIP certifies only the
formal statements enumerated here. No historical novelty or priority conclusion
is inferred from compiler acceptance.
