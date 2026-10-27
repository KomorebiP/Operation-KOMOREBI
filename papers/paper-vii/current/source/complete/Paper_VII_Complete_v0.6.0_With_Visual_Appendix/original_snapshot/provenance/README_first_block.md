# Projector-Resolved Seed Calculus VII
## v0.1.0 — Checked First Block

**Author: Komorebi P.**  
**Date: 2026-09-06**

This release begins the Lean verification pass for Paper VII, *Quantum Seed Calculus: Symmetry Packets, Circuits, Effective Dynamics, and Quantum Spacetime*. It is not a claim that the entire paper is Lean verified.

## Results actually obtained

| Active source | Theorem declarations | Lean exit code | Recorded seconds |
|---|---:|---:|---:|
| `QuantumPacketCore.lean` | 19 | 0 | 4.081 |
| `SchurFeshbach.lean` | 4 | 0 | 3.689 |
| `LowModeConvergence.lean` | 2 | 0 | 3.452 |
| `ConstraintAudit.lean` | 7 | 0 | 4.432 |

**32 theorem declarations passed across four source files.** All 32 `#print axioms` reports contain only `propext`, `Classical.choice` and `Quot.sound`. The four active sources contain no `sorry`, `admit`, new `axiom` declaration, `unsafe` declaration or `native_decide`. Two intentionally invalid files under `verification/negative_controls/` were rejected with exit code 1. They are controls, not library theorems.

The six covered source items are 4.1, 4.2, 5.1, 7.1, corrected 9.1 and 11.1. There are **13 other named finite theorem-like items not checked in this release**, and five separate continuum conjectures remain unproved. The inventory is not a difficulty-weighted completion percentage. See `THEOREM_LEDGER.md`.

## Two substantive audit findings

**Feshbach hypothesis.** The original Theorem 9.1 assumes only invertibility of the eliminated block. The active proof requires invertibility of both that block and the full resolvent matrix, and also proves the equivalent Schur-complement invertibility criterion. The case z = 0, H = diag(0, -1) shows that the extra condition cannot simply be omitted.

**Constraint compression.** For an exact common-kernel physical projector P, all constraints satisfy C_a P = 0. Then the proposed anomaly already satisfies A_ab P = 0, and therefore P A_ab P = 0. This cannot by itself certify full operator closure. The added Lean module supplies the generic proof and a nonzero physical projector with noncommuting 3 by 3 constraints. It does not resolve the continuum conjectures.

The low-mode result also makes h != 0 explicit. Its checked bound holds for every real frequency and nonzero real spacing, which is stronger than the manuscript's low-mode interval restriction.

## Reproduce using the portable kit

Run from the extracted release directory in Linux or WSL:

```bash
python3 scripts/verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For a single module:

```bash
python3 scripts/check_low_memory.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 formalization/QuantumPacketCore.lean
```

The kit must include its workspace, pinned dependency sources and compiled cache. The large portable runtime is not duplicated in this release. The commands use the kit already retrieved in this conversation. Native Windows execution was not retested in this block.

`verify.py` checks version and mathlib Git revision, compiles all four standalone modules, checks every exported theorem's axiom list, runs both expected-failure controls, writes logs and returns a nonzero status on any failed gate. New evidence goes to a timestamped directory, leaving `verification/release_run/` unchanged. No inherited environment variables are written to disk.

The low-memory runner captures Lake's environment and lets Lake exit before starting Lean. Lean runs with one worker and `-DwarningAsError=true`. The sources use targeted public module imports. There is no RAM limiter in the script. The session's cgroup limit was 4 GiB, but no controlled peak-memory benchmark was conducted. The final four module checks took 15.654 seconds combined in this warmed environment, including per-file launcher setup. This is not a cold-start performance claim.

## Verification boundaries

Lean accepted these statements under their explicit hypotheses. They are general symbolic proofs, not a replacement by floating-point examples. The exp result uses the actual operator exponential; circuit depth is arbitrary and finite; measurements are finite complex matrices; the Feshbach proof is a literal retained submatrix of the full inverse.

The new constraint diagnostic includes exact rational-matrix certificates. It does not establish gravitational constraint closure, a physical continuum limit, Lorentzian reconstruction, an Einstein limit or a spin-two sector. The original 22-test numerical suite was not rerun. Papers I-VI were not rebuilt in full, and the imported mathlib library was not independently rechecked.

## Manuscript deliverables

`manuscript/Paper_VII_First_Lean_Block_Supplement.pdf` is the newly compiled and reviewed mathematical supplement. Its self-contained LaTeX source is alongside it. `Paper_VII_Original_Unchanged.pdf` preserves the retrieved 25-page manuscript. The three targeted source amendments are in `Paper_VII_First_Block_Amendments.patch`. The original PDF is intentionally not presented as though those changes were applied. Original figure assets were not retrieved, so the original figure-dependent TeX was not rebuilt.

## Failures and repairs retained

Initial proof attempts failed on recursive field notation, section-variable inclusion, explicit complex-number imports and finite-index simplification. A deprecated import also produced a warning and was replaced. The retained development logs document those failures; the final release run is warning-free. No mathematical result was admitted to bypass a failed proof.

`provenance/` distinguishes the two reused Paper VI proof sources from newly written Paper VII code. `verification/release_run/SUMMARY.json` is the machine-readable release result. `SHA256SUMS.txt` covers the final release contents except itself.
