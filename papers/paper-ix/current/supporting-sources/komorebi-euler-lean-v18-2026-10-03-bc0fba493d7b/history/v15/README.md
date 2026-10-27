# Komorebi Euler Lean v15

The actual restricted dyadic Euler source, Bernoulli kernel valuation, packet
identities, and sharp finite reconstruction-tail theorem.

**224 named theorem/lemma declarations, 22 modules; two clean Lean replays and
complete transitive axiom audits.** See `PROOF_AND_STATUS.md` for exact theorem
scope and remaining mathematical/formal gaps.

The source is constructed, not postulated. Its integer values are proved equal
to `(3^(2n+2)-1)/(4(2n+1)(2n+2))`. The Bernoulli kernel has proved exact valuation
`4m-1`. The finite reconstruction error has optimal modulus `2^(4M+3)`.

The universal identity of that reconstruction with independently specified signed
Euler numbers remains a formal obligation. No Euler critical scalar is proved
universally nonzero here. Prior numerical family coverage is not relabeled Lean
coverage.

## Read or reproduce

- `PROOF_AND_STATUS.md`: mathematical details, trust boundary, failures.
- `Euler/`: 22 mathematical Lean modules, including the 14 unmodified v14 modules.
- `THEOREM_INDEX.json`: all 224 audited names and source locations.
- `evidence/clean_replay_1` and `clean_replay_2`: actual compile logs and axiom lists.
- `evidence/rational_alignment.json`: optional finite Python corroboration only.
- `history/v14`: preserved incoming source/proof/evidence snapshot.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_rational_alignment.py --output /path/to/NEW_check.json
```

Use Lean 4.34.0-rc2 and mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. With a normal configured installation,
`lake update` and `lake exe cache get` obtain the pinned dependencies, then the
replay script can be used without `--runtime`. These network setup commands were
not needed or executed for the recorded portable-runtime replays.

No runtime binaries, cached project outputs, or font files are distributed.
