# Reproduce AVOC v0.36.0

## Environment

Linux x86-64/WSL; Python 3.10+; Lean 4.34.0-rc2 commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.  Nine exact dependency revisions are
recorded in `lake-manifest.json`.  Runtime binaries and compiled dependency caches are not
included in the source ZIP.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v035.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 20 --workers 3
```

Repeat the bounded build until all current targets pass; do not repeat `--prepare`.  Then:

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative
python checks/test_staged_affine.py
python tools/summarize_v035.py /path/to/AVOC_Formal_v0.34.0.zip
```

There are 193 local targets and 100 deliberately invalid Lean files after indexing.  Import
failures and timeouts are not substantive negative-test evidence.

## Executable examples

```bash
python tools/run_staged_affine.py examples/staged_affine/certain.json
python tools/run_staged_affine.py examples/staged_affine/risky_warm.json
python tools/run_staged_affine.py examples/staged_affine/one_step.json
python tools/run_staged_affine.py examples/staged_affine/after_warm_success.json
```

The request wire is:

```text
["staged-affine-f5-v1", sourceProgram, warmCacheRecord, coldCandidate,
 calls, coldGenerationCharge, warmSuccessProbability, coldSuccessProbability,
 operationalBudget, horizon, reportHistory]
```

Rational probabilities are `[integer,naturalDenominator]`.  History entries are
`[actionName,reportBool]`; zero-probability or unavailable histories are rejected.

The entrypoint validates both certificates before constructing its typed in-memory model.
Do not interpret its Bellman accounting as a measurement of that eager physical validation.

## Packaging

```bash
python tools/package_v035.py --output /chosen/AVOC_Formal_v0.36.0.zip
python tools/check_manifest.py
```

Check the original payload manifest before regenerating evidence.  Regenerated logs change
manifest-covered files.  Pinned dependency caches are retained and are not rebuilt from
source by these commands.
