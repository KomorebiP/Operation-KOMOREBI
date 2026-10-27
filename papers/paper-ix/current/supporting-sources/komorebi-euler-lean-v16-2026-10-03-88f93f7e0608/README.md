# Komorebi Euler Lean v16

The independently defined signed Euler sequence is now proved equal to the
constructed Bernoulli/source reconstruction for every row. The sharp
`2^(4M+3)` error modulus and its optimality witness are therefore actual
Euler-number theorems, not merely reconstruction-sum theorems.

**279 named theorem/lemma declarations in 28 modules; 55 new declarations.**
The exact recurrence, parity, ordinary integrality and uniqueness of the signed
Euler sequence are included. The input v15 snapshot is preserved in `history/v15`.

Read `PROOF_AND_STATUS.md` for the proof chain and the precise remaining gaps.
`RELEASE_STATUS.json` and the clean replay logs report executed verification.
`THEOREM_INDEX.json` lists every audited declaration.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_rational_alignment.py --limit 128 --output /path/to/NEW_check.json
```

Lean 4.34.0-rc2; mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The portable runner uses cached pinned
dependencies; full Lean/mathlib bootstrapping is not claimed.

No universal critical-scalar nonvanishing, rowwise collision classification, or
new terminal-degree/digit-sum bound is claimed. The next formal block is the
infinite H_r/G_r construction and its carry normalization. All earlier source
and kernel obligations preserved in history retain their original version scope;
the identification obligation from v15 is closed by the new v16 modules.

No runtime binaries, cached project objects, or font files are distributed.
