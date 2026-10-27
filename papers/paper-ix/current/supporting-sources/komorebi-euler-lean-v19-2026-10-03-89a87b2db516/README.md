# Komorebi Euler Lean v19

**Canonical terminal coordinates and the actual Euler wall decomposition.**

This source release contains 566 theorem/lemma declarations in 58 mathematical
Lean modules. Nine new modules derive the canonical odd multiplier, terminal
exponent, nonnegative wall distance and complete minimizing set from the actual
Euler carry costs. They construct the upper and lower analytic factors, prove
`G_r(x) = P_j(x) U_r(x-j) + 2^delta V_r(x)` on the entire dyadic disc, and give full
coefficient residues and an actual derivative/Wronskian identity.

See [PROOF_AND_STATUS.md](PROOF_AND_STATUS.md) for exact hypotheses, consequences
and remaining work. `RELEASE_STATUS.json` is the machine-readable verification
record. All 49 inherited mathematical modules are unchanged. The complete v18
archive is preserved in `history/v18/`.

## Run

Requires Python 3.10+ and the recovered portable runtime, Lean 4.34.0-rc2 with
mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```bash
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_terminal_alignment.py --max-r 65536 --output /path/to/NEW_terminal_checks.json
```

The replay builds each module from source into an empty project-output directory,
uses one worker and warnings-as-errors, then audits every declaration's transitive
axioms. Only `Classical.choice`, `Quot.sound` and `propext` are permitted. The pinned
compiled mathlib caches are reused. A new directory or output filename is required
for every replay/audit; existing evidence is not overwritten.

No runtime binaries, dependency caches or font files are included. The historical
replay records contain paths to the original working directories; reproduce using
your own runtime and evidence paths.

## Proof boundary

The actual terminal wall identity is now proved. The full local skeleton atlas,
largest lower-address regular-complement theorem and numerical higher-family
certificates are not yet transferred into Lean. Exact critical-scalar nonvanishing
in the remaining arithmetic progressions is still a mathematical question.
No universal Euler simplicity or increased manuscript coverage bound is claimed.
The theorem count includes auxiliary results and is not a novelty count.
