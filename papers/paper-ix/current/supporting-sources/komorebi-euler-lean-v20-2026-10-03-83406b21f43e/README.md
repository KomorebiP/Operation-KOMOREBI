# Komorebi Euler Lean v20

**Exact skeleton localization and an end-to-end pointwise-unit Euler atlas.**

This release contains 653 theorem/lemma declarations in 70 Lean mathematical
modules. Twelve new modules add convergent affine charts, exact skeleton
factorizations and a disjoint cover of the dyadic unit disc. These derive an
all-distance root-count, derivative and root-distance atlas for actual Euler
walls whose lower residual is pointwise odd. The arithmetic lower-cost criterion
is retained explicitly. In particular actual regular terminal walls of degree
at least two are covered without a degree bound.

The finite active-skeleton type is proved equivalent to the complete type of
actual dyadic residual roots. The new r=510 example has exactly two simple roots,
one in each parity class, and an exact Euler-error formula at every original row
in each ball. Counts include helper lemmas and are not novelty counts.

See [PROOF_AND_STATUS.md](PROOF_AND_STATUS.md) for the precise scope and remaining
work. `RELEASE_STATUS.json` records actual compilation and independent-check
outcomes. All 58 inherited mathematical modules remain unchanged; the complete
incoming v19 ZIP is retained under `history/v19`.

## Reproduce

Python 3.10+ and the pinned portable runtime are required:

- Lean 4.34.0-rc2
- mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_skeleton_localization.py --precision 32 --output /path/to/NEW_check.json
```

Use new output paths. The replay recompiles every project module, then audits
all declarations' transitive axioms. It reuses pinned mathlib dependency caches;
it does not bootstrap Lean or mathlib. Only Classical.choice, Quot.sound and
propext are allowed. No runtime, dependency cache, compiled project objects or
font files are shipped.

## Remaining boundary

This does not resolve lower-root-containing slope collisions or exact critical
scalar vanishing. The nearest-neighbor quadratic/cubic bridge on those balls,
address/complement formalization, and further preparation remain explicit work.
No universal Euler simplicity, algebraic squarefreeness, increased manuscript
coverage number, or historical-priority claim is made.
