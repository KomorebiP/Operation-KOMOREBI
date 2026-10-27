# Contributing

Contributions are useful when they improve mathematical correctness,
reproducibility, source clarity, or literature positioning.

## Before opening a pull request

1. Open an issue for a change that alters a theorem statement, hypothesis,
   proof, claim boundary, or interpretation.
2. Identify the exact theorem label or source line affected.
3. Run:

   ```bash
   python scripts/check_release.py
   cd manuscript
   python verify_block15_lane_transport.py
   python verify_block16_holonomy_lane_transport.py
   python verify_block16_publication_audit.py
   ```

4. Build the integrated manuscript and standalone note when the change touches
   LaTeX, generated tables, figures, references, or release PDFs.

## Mathematical review reports

A useful report contains the exact label, the hypothesis being used or omitted,
the smallest disputed statement, and a reproducible derivation,
counterexample, or correction. Classify the concern as a proof issue, typing
issue, descent/coherence issue, scope issue, prior-art issue, or expository
issue.

For Block 16, distinguish carefully among:

- a local lane label;
- an object-address monodromy orbit;
- a simultaneous source-target pair orbit;
- a compatible section of the matrix local system;
- a base-fiber matrix fixed by loop transport.

These objects are related but not interchangeable.

## Generated material

Do not hand-edit files under `manuscript/generated/` when a generator exists.
Run the responsible generator and commit both the generator change and the
recomputed output. Do not silently alter exact assertion totals, frozen test
schedules, release hashes, or validation records.

## Status discipline

Keep these statuses distinct:

- direct internal proof;
- conditional theorem;
- imported classical theorem;
- exact computational verification;
- framework or definition only;
- conjecture;
- external peer review or validation.

A pull request must not promote an internal proof or exact regression to
independent validation.
