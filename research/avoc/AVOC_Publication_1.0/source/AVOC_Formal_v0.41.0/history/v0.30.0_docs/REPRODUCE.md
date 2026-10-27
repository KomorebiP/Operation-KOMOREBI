# Reproduce AVOC v0.30.0

Linux x86-64 or WSL, Python 3.10+, Lean 4.34.0-rc2 at 6a10ac8c22beadecabdbb0919c2b50214762f91d and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine exact dependency revisions are in lake-manifest.json. Runtime and cached/compiled binaries are NOT included.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v030.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 12 --workers 4
```

Repeat only the bounded build command until 166/166 final targets pass. Do not repeat --prepare between slices. The build begins with empty local outputs and retains exact pinned external dependencies.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative --start 0 --count 12
```

Continue negative groups at 12,24,36,48,60,72. There are 84 deliberate negative files. A timeout or import failure is not a successful rejection.

## Real stored-certificate use

```bash
python tools/affine_cache.py run examples/affine_cache/cold.json --store /tmp/avoc-affine-new
python tools/affine_cache.py run examples/affine_cache/shifted.json --store /tmp/avoc-affine-new
python tools/affine_cache.py run examples/affine_cache/ten_calls.json --store /tmp/avoc-affine-new
python tools/affine_cache.py run examples/affine_cache/short.json --store /tmp/avoc-affine-new
```

The first call generates, checks and publishes. Later matching linear maps reuse the saved certificate with a freshly computed offset and fresh validation. Calls can skip generation/revalidation when the opportunity test fails. Inspection/lookup/parsing are not free physical operations even when an arithmetic check is skipped.

`run` without `--store` is read-only cold exploration. `validate /path/to/certificate.json --credit 100000` rechecks a saved record directly. The store is a new certificate-only format, not an importer for older proof or upgrade stores.

No saved approval, caller-supplied rank or filesystem checksum is a substitute for the Lean checker. Runtime current-source/import/output hashes are checked before invoking the entrypoint. Generated source edits require rechecking/rebuilding, not silently repinning an existing protected store.

## Fresh tests

```bash
python checks/test_affine_cache.py differential
python checks/test_affine_cache.py live --group basic
python checks/test_affine_cache.py live --group economics
python checks/test_affine_cache.py live --group integrity
```

Each live group creates a new temporary store. The test's controlled exception is not a crash/power-loss test. An earlier unsplit live test exceeded its host timeout; that incomplete run is NOT final evidence. All groups were rerun against the final test source. The differential suite was also rerun after that test-source change.

## Collection and packaging

```bash
python tools/summarize_v030.py /path/to/AVOC_Formal_v0.29.0.zip
python tools/audit/validate_computation_manifest.py results/v0.30.0/computation_manifest.json --root .
python tools/package_v030.py
```

Metadata validation does not prove mathematics. The v1 audit schema records a collector run, not the timing of all earlier proof/test executions. Per-file compilation and per-test source/output hashes are the detailed evidence. Check the original delivered manifest BEFORE regenerating it. Package hashes exclude themselves, external packaging summaries, .lake, Python caches and runtime files.
