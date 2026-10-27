# Fresh Paper X production replay

This directory supplies the 122 unique Lean modules selected from the recovered
10 October 2026 checked baseline: the union of the twenty publication source
routes and their imports, including the conditional terminal theorem. The exact
terminal import subset contains 97 modules. `PUBLICATION_SOURCE_MANIFEST.json`
records each delivered source hash, import list and preserved source origin;
`TERMINAL_SUBSET.json` identifies that smaller subset.

These sources retain the amended conditional scope. Compilation does not prove
universal companion existence, carrier existence or nonzero occupancy. The
later residual-system attempt and missing 16–17 October continuation are outside
this selection. No production source was altered for this replay.

Both fresh runs passed all 122 modules: A1 in 143.247 seconds and B in 227.622
seconds. Run B used this copied delivery tree to test relative source-path
resolution. All 392 generated artifact pairs matched byte for byte, including
private/server payloads and IR files. `REPLAY_SUMMARY.json`, `BUILD_COMPARISON.json`
and the complete raw records in `build_A1/` and `build_B/` retain those results.
They do not claim equality with historical inherited proof-object bytes.

## Rebuild

Extract the separately supplied Linux x86_64 Komorebi offline kit. Its exact
archive SHA-256 is
`66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.
The kit supplies Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` and eight additional pinned
dependencies. The runtime and Mathlib caches are external to this paper release.

```bash
python3 rebuild_production.py \
  --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /absolute/path/new-empty-paper-x-build \
  --workers 2
```

Use Python 3 and Git in a compatible Linux x86_64 environment. The output
directory must be new or empty, so failed attempts remain available. The driver
derives delivered source paths from its own directory, verifies all 122 hashes
and all nine dependency HEADs, then compiles the explicit dependency closure
with `-j1 -DwarningAsError=true`. It seeds no Paper X proof objects. It uses the
kit's existing compiled Mathlib/dependency caches; it does not perform a cold
Mathlib build or fetch dependencies. Eight package cache directories are
present in this kit; its declared `Cli` Lake dependency has no compiled cache
directory and is not a production import.

On this hosted environment unmodified Lean reports `failed to locate
application`. Only for that startup failure, the driver uses the kit's included
`compat/app_path.so` through `LD_PRELOAD`. The retained C source and hashes in
`runtime_evidence/` show that this helper redirects the current process's
numeric `/proc/PID/exe` readlink to `/proc/self/exe`. It addresses executable
self-location and leaves Lean's kernel and proof rules unchanged. No global
Lean installation or permanent environment change is made.

The driver writes complete per-module stdout/stderr, commands, return codes,
timings and source/object hashes in `BUILD_REPORT.json` and `logs/`. The
recovered source contains third-party support modules; original notices and
the preserved Apache 2.0 license/attribution records are in `third_party/`.

For two completed runs, compare every generated artifact with:

```bash
python3 compare_builds.py /path/to/build-A /path/to/build-B \
  --output /path/to/comparison.json
```

`selection_script_as_executed.py` is retained selection provenance, with its
original baseline/restoration paths. Reproduction uses the delivered manifest
and sources through `rebuild_production.py`; it does not require rerunning the
historical selection step.
