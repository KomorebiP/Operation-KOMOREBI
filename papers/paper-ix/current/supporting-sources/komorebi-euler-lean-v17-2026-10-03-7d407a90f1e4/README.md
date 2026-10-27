# Komorebi Euler Lean v17

The actual infinite Euler residual H_r and its carry-normalized integral series
G_r are now constructed from the Bernoulli/source packets in Lean. Convergence,
exact all-row factorization, the global carry minimum, the complete binary
residue, and the last odd coefficient are proved from those definitions.

**417 named theorem/lemma declarations in 42 modules; 138 new declarations.**
All 28 incoming mathematical modules remain unchanged. Source line counts and
helper-declaration counts are not claims of mathematical novelty.

The exact normalized Euler row law is now end-to-end. Terminal index zero is
root-free, terminal index one has one actual simple dyadic root, and depths with
at most three binary one-bits have a fully explicit exact row error law.
The larger mathematical research atlases have not all been ported into Lean.

Read PROOF_AND_STATUS.md for the construction and remaining obligations.
RELEASE_STATUS.json and evidence/v17_replay1/run.json and v17_replay2/run.json
record actual clean replay status. THEOREM_INDEX.json lists every audited lemma.
The incoming v16 archive is preserved in history/v16.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_residual_alignment.py --max-r 32 --max-offset 24 --output /path/to/NEW_check.json
```

Lean 4.34.0-rc2; mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The portable runner uses pinned cached dependencies; no whole-library bootstrap
is claimed. Runtime binaries, dependency caches and font files are not included.

The only allowed transitive axioms are Classical.choice, Quot.sound and propext.
No unfinished proof, custom mathematical axiom or native-evaluation proof axiom
is accepted. The terminal arithmetic and local Euler certificates still need
further formal bridges. The surviving critical-scalar questions remain research
obligations; no universal nondegeneracy or new coverage bound is asserted.
