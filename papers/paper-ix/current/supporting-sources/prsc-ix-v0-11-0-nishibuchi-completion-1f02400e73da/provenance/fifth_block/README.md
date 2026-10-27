# Paper IX v0.5.0: Checked Fifth Block

**Author: Komorebi P.**

This continues the status-corrected Paper IX manuscript and the checked fourth block.
It covers finite prime-power and dyadic unit decomposition, integral standard-window
residue independence, and Chinese-remainder packet factorization.

## Recorded scope

- 20 of 24 named manuscript-proved items checked; four pending.
- 333 explicit theorem declarations, 77 explicit definitions, 28 modules.
- New this block: three manuscript items (6.2, 8.3, 10.1), 61 supporting/main
  theorems and 17 definitions in seven modules.
- Three classical inputs and two conjectures remain separately tracked.

Read `docs/Paper_IX_Fifth_Lean_Block_Supplement.pdf`,
`docs/Paper_IX_Fifth_Block_Ledger.md` and `docs/Paper_IX_Fifth_Block_Amendments.md`.
The original manuscript and earlier supplements remain unchanged. Their amendments
are part of the current reading contract.

## Run

Requires the separately supplied Linux x86-64 portable Lean kit (Lean 4.34.0-rc2)
with the pinned Mathlib cache. This source archive does not include a runtime binary.

```bash
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Python 3.10+ is required. The launcher runs the unit suites and independent exact
mirrors, then starts a fresh output directory, compiles all 28 active modules with
warnings treated as errors, checks all nine dependency pins and all 410 explicit
declaration axiom reports, and requires 17 invalid-proof controls to be rejected.
To select a clean system interpreter, prefix the command with `PYTHON=/usr/bin/python3`.

For only Lean:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The recorded successful current run is in `verification/fifth_release/`.
Verification creates a new run rather than overwriting prior evidence.
`MANIFEST.json` covers the distributed files, not newly created run directories.
Check it with `python3 scripts/check_manifest.py`.

To regenerate this block's six-page PDF (requires the TeX packages listed in its source):

```bash
python3 scripts/build_fifth_supplement.py
```

## Mathematical boundary

The original rational packet coefficients are identified with integral p-adic lifts
before reduction to the residue field. The reduced sequence is independently
constructed and proved unique. Outside-window integrality is not assumed.

The finite root representative is explicitly a^(p^(ell-1)) for a unit modulo p^ell,
ell>=1. Its root equation, residue, uniqueness, multiplicativity and finite-precision
compatibility are derived. The mod-four dyadic sign splitting is proved separately
at ell>=2. No infinite p-adic group isomorphism or analytic logarithm is claimed.

CRT constructs the actual residue ring equivalence and proves the existing sequence
and formal-series projector identities, with canonical residue labels. It does not
identify arithmetic visibility weights.

The independent Python scripts are finite exact-arithmetic mirrors, not Lean code
extraction or universal proof substitutes. Pinned Mathlib supplies prior Lucas,
finite-field, unit-group, ideal-power, CRT and p-adic results. Its compiled cache
was reused, not independently rebuilt.

Pending manuscript items are 7.5, 8.5, 9.1 and 9.2. The global Euler difference
theorem and uniform period have not been promoted from the supplied manuscript
proof claims. Neither conjecture was resolved.

## Preservation and failures

All 21 upstream Lean proof files, the original manuscript and four earlier
mathematical supplements remain byte-identical. Original fourth-block metadata,
verifier and tests are archived in `provenance/fourth_block/`; current version
assertions were updated and 29 new release tests added. The active suite has 103 tests.

The 18 individual Lean development checks, including 11 unsuccessful drafts, remain
in `verification/fifth_development/`. They are inactive evidence, not proof inputs.
A separate clean cumulative run passed; the release audit records the second run
from freshly extracted distributed sources. Compiled project outputs are omitted
from the archive so verification must regenerate them.
