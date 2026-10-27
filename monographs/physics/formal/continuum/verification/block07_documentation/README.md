# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–07 · v0.7.0

**PASS: 572 theorem declarations, 688 inventoried named declarations, 34 mathematical modules, and 50 negative controls.** The completed result is `verification/final/report.json`. Block 07 adds **89 theorem declarations, 19 definitions and one structure**, preserving all 29 previous mathematical source modules byte-for-byte. The cumulative total contains 533 full-edition declarations and 39 recovered Paper VII theorems. These are declaration counts, not independently discovered physical laws or a completion percentage.

The included reference is the **550-page Projector-Refinement Physics: Complete Unified Theory**. Its identity and target pages are recorded in `verification/block07_source_identity.json`. Read `docs/BLOCK_07_PROOF_GUIDE.md`, `STATUS.md`, `docs/SOURCE_MAP.md` and `docs/CLAIM_LEDGER.json` for exact scope. The next task is in `CONTINUE_HERE.md`.

## Block 07

| Module | New theorems | Main result |
|---|---:|---|
| PositiveEffects | 25 | Actual Born probabilities and continuity for positive overlapping resolutions |
| MovingEffects | 14 | Actual moving-source derivative, differentiated partition and unitary transport |
| EffectRefinement | 14 | Constructed address coarsening, exact current aggregation and composition |
| WeightedEffects | 9 | Nonnegative column-normalized postprocessing and its actual derivative |
| EffectExamples | 27 | Exact nonprojector and moving-source witnesses, invalid-alternative tests |

The effects are bounded Hermitian positive operators summing to the identity. No idempotence, orthogonality, pairwise commutation, or finite-dimensional state space is assumed. The probability is the actual Born expectation `Re <psi,F_i psi>`, separately proved real and nonnegative; it is not silently replaced by `||F_i psi||^2`.

Starting from the actual original state derivative and effect derivatives, the proofs derive `p_i' = s_i + sum_j J_ij`, with `s_i = <psi,F_i' psi>`. Both Hermiticity of the velocity and zero total source follow by differentiating the actual Hermitian partition identities. The scalar probability law and source cancellation are not assumed as atlas fields.

Address coarsening proves actual probability, source and current laws `p^c=Rp`, `s^c=Rs`, `J^c=RJR^T`. A separate added result permits fixed nonnegative real weights whose columns sum to one. Unnormalized, signed, or time-dependent weights are not promoted to valid instances of that result.

## Run the cumulative verifier

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck
```

The verifier checks the exact runtime/dependency pins, all inherited mathematical source-preservation hashes, removes local compiled outputs, recompiles all local mathematical modules and the aggregate with one worker and warnings as errors, audits all inventoried declarations, and checks every negative control against its own designated proof diagnostic and mapped source range. Import errors, timeouts, or a nonzero batch exit alone do not count as successful rejection tests.

Lean is **4.34.0-rc2**, Mathlib **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. Nine exact dependency revisions and clean tracked trees are checked. Permitted axiom dependencies are only `propext`, `Classical.choice` and `Quot.sound`. The imported dependency cache is reused, not independently rebuilt wholesale. No admitted active proofs, custom axioms, unsafe/native evaluation, or kernel-bypass options are used.

Runtime assembler and checksums are included in `runtime_restore_support/`; the multi-gigabyte runtime and seven archive parts are not duplicated. `verification/block06_baseline/` records the successful fresh audit of the 483-theorem starting point. All earlier evidence and the successful/failed Block 07 development snapshots are retained. See `docs/BLOCK_07_FAILURES.md`.

## Recheck the packaged ZIP

```bash
python3 scripts/recheck_archive.py --archive /path/to/Komorebi_Physics_Lean_v0.7.0_Checked_Block_07.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /path/to/new-empty-parent --out /path/to/recheck-evidence
```

The destination must not exist. This safely extracts, checks all payload hashes, invokes the extracted complete verifier, compares proof inputs, counts, dependency pins and axiom inventories, then checks hashes again. The external archive-check report records the actual result of a specific run; the presence of the script alone is not a recheck certificate.

## Boundaries and next target

The new results concern a finite resolution of bounded operators. The unitary-adjoint section additionally assumes a complete complex Hilbert space. The state flow and operator-norm derivatives are explicit inputs, not constructed solutions. The two-dimensional effects in the exact witness commute; the general results do not require commutation. The affine state witness is only a local derivative witness; the sine-weighted effect family is globally positive but is not asserted to arise by unitary conjugation.

Earlier limits on ODE existence, positivity-preserving semigroups, entropy boundary points, general-graph convergence, coarse Markov closure, infinite refinement, unbounded/countable/trace-class extensions, gravity, cosmology, and empirical adequacy remain. Chapter 3 still needs complete inventory.

**Next: Chapter 5.4, equations (5.22)–(5.31), Parseval-channel realization and dilation.** Construct analysis/synthesis operators, prove the actual channel norm and operator reconstruction identities, and build the direct-sum dilation. Equation (5.32), recovery of the sharp current, is already checked here. Do not claim an arbitrary-effect factorization or universal dilation before constructing it.
