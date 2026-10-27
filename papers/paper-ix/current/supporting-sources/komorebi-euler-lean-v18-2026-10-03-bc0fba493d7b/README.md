# Komorebi Euler Lean v18

The ordinary analytic derivative now commutes with the ACTUAL infinite Euler
packet sum at every order. Complete Hasse-jet and derivative packet-tail bounds,
explicit skeleton/source derivative channels, and the exact differentiated
residual recurrence and Wronskian critical-zero criterion are kernel checked.

**483 named theorem/lemma declarations in 49 modules; 66 new declarations.**
All 42 inherited mathematical modules remain byte-for-byte unchanged. Counts
include helper lemmas and are not claims of mathematical novelty.

An important distinction is also proved: packets beyond an integer row vanish
in value but have nonzero first derivatives. One cannot differentiate the finite
integer-row value formula by silently dropping that infinite slope tail.

Read PROOF_AND_STATUS.md for theorem statements and exact boundaries.
RELEASE_STATUS.json and evidence/v18_replay1/run.json and v18_replay2/run.json
record two completed clean replays. THEOREM_INDEX.json and Audit.lean cover every
indexed theorem. The input v17 archive is preserved under history/v17.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_packet_derivatives.py --output /path/to/NEW_packet_checks.json
```

Use fresh output paths; scientific outputs and replay directories refuse overwrite.
Pinned Lean 4.34.0-rc2; mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Compiled dependencies are reused, not rebuilt. Runtime binaries, cached dependencies,
compiled project artifacts and fonts are not included in this source package.

Only Classical.choice, Quot.sound and propext are accepted in the transitive
axiom audit. No custom mathematical axiom, unfinished proof or native-evaluation
proof axiom is accepted. The complete finite coefficient certificate is an
explicit hypothesis of the certificate-soundness theorem; unresolved Euler
families are not assumed to satisfy it.

No new irregular-family classification, enlarged coverage bound, or universal
Euler critical-value nonvanishing is claimed. Packet differentiation retains
ordinary derivatives in a structured decomposition; it is not a replacement
notion of differentiation.
