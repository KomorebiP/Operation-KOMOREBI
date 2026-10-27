# Corrected edition finite representative bookkeeping

The corrected edition changes exactly two lower endpoints in the strengthened
verifier from `-N//2` to `-(N//2)`. The preserved raw verifier and every raw
source file remain unchanged. `ODD_N_REPRESENTATIVE_FIX.diff` is the complete
source diff, and `CORRECTION_PROVENANCE.json` records both SHA-256 hashes. Byte
comparison confirms that the entire corrected script is the original byte
string with just those two replacements, adding four bytes.

The distinction matters for odd sizes because Python evaluates `-N//2` as
`(-N)//2`. For odd `N`, the old list has `N+1` integers and repeats a residue
class. The corrected list `arange(-(N//2), N-N//2)` has exactly `N` integers,
each residue class once, with `|k| <= N/2`. The two variants agree for even `N`.

Fresh separate evidence is in `../corrected_fresh_20261006_r2/manifest.json` and
`results.json`. The schema version 2 manifest validates against the project
root. The corrected script was copied into an isolated copy of the preserved
strengthened package; its TeX, Bib, PDF, legacy values and figure checks used
preserved assets. No other verifier code changed.

| Evidence | Result |
|---|---|
| Counts, residue uniqueness and bounds for all integer `N = 4..32` | 87 assertions pass, 29 explicit representative lists |
| Corrected strengthened suite | 17,699 checks pass in 15 groups |
| Corrected spectral geometry group | 13,856 checks pass |
| Unchanged original strengthened replay | Separately retained: 18,049 checks, spectral group 14,206 |
| Check-count change | Minus 350 duplicate-mode inequality checks |
| Other group records | Exactly equal to the preserved report |
| Raw source preservation | All 784 files unchanged before/after corrected replay |

The 350 removed checks comprise 28 inequalities for the 14 redundant 1D modes
and 322 inequalities for redundant 2D mode pairs at odd sizes 5,7,9,11,13,15,17.
The later 2D and 3D loops still sample 100 modes where the source specifies
sampling. Correcting the input list can change those sampled values under the
same RNG seed; their fixed check counts remain the same. The heat-trace sizes
16,32,64,128 are even and their representatives are unchanged.

This is a finite bookkeeping correction. It supplies no universal theorem,
continuum limit, exhaustive sample of arbitrary matrices, or new Lean check.
The original source gate and the corrected edition gate are separate evidence.

Portable replay from the evidence project root, using a new output directory:

```bash
python verification/scripts/reproduce_corrected.py --source source --downloads downloads --out verification/my_corrected_run
python verification/tools/validate_manifest.py verification/my_corrected_run/manifest.json --root .
```

The original raw-run manifest remains valid and was revalidated after this
correction. The initial correction-generation guard mistakenly counted the
substring in both lower and upper endpoints and stopped before producing a
corrected file. The initial bounded driver therefore failed at setup. That
attempt is retained in `../corrected_fresh_20261006/` with its driver snapshot
and `SETUP_FAILURE.md`. Its input driver was subsequently revised, so its
project-root freshness check is explicitly stale; it is not successful
evidence. No mathematical assertion failed during that attempt.
