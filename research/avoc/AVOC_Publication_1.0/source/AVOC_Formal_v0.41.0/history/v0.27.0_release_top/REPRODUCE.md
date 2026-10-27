# Reproduce AVOC v0.27.0

## Frozen baseline and toolchain

This cumulative source tree extends the semantic-feedback AVOC v0.26 ZIP, not the parallel rewrite branch. The runtime and compiled caches are omitted. Use Linux x86-64 or WSL, Python 3.10+, Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine external revisions are pinned by lake-manifest.json.

    export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
    python tools/check_manifest.py
    python tools/inventory_v027.py
    python tools/verify_release.py --prepare
    python tools/build_parallel.py --seconds 20 --workers 3

Repeat only the bounded build command until it reports all 150 current targets. Do not prepare again between slices. After a host interruption check that its child is stopped, then rebuild unfinished targets and descendants. External cache revisions are verified and retained, not rebuilt.

    python tools/verify_release.py --audit
    python tools/verify_release.py --negative

There are 71 negative files; use --start/--count slices on execution-capped hosts. Setup/import failures and timeouts are not counted as mathematical rejection. The historical optional whole-table kernel reduction is not part of this build and was not successful.

## Check and publish the shipped certificate

    python tools/global_library.py validate examples/library/global.json --credit 300000
    python tools/global_library.py publish examples/library/global.json --store /tmp/avoc-global-new --credit 300000
    python tools/global_library.py query /tmp/avoc-global-new --queries examples/library/queries.json --credit 300000

The new store directory must not exist. `query` revalidates in a fresh Lean process and does not generate candidates. Existing research/upgrade stores are not migrated. Each call's credit is its own declared tariff limit; no shared wallet is debited.

For this bank validation costs 210245 tariff units. The three queries cost 115 in total, leaving 89640 from 300000. A funded invalid bank is charged even if it fails early. Runtime parsing/preflight/IO and timed-out computation are outside this abstract tariff.

`library_source_pins.json` binds reviewed source files. Do not refresh it to bless an arbitrary edit. The wrapper also checks current compilation records and direct-import output hashes. Rebuild and audit legitimate source changes before preparing a new release.

## Regenerate untrusted candidate data

    python tools/build_global_library.py /tmp/new-global-library.json
    python tools/global_library.py validate /tmp/new-global-library.json --credit 300000

The Python generator is not trusted for correctness. It refuses to overwrite its output. The Lean validation result is the authority for the declared certificate property.

The packaged `examples/library/lean_depth3.json` came from a fresh execution of the inherited Lean semantic producer; its witnesses exactly match the Python certificate. The recorded request/command/output is in results/v0.27.0/cold_lean_*. Historical output files are evidence from that run, not fresh execution on another host.

## Independent regressions

    python checks/test_global_library.py --part wire
    python checks/test_global_library.py --part store
    python tools/summarize_v027.py --baseline /path/to/semantic/AVOC_Formal_v0.26.0.zip

The wire test uses independent exact-node-size bitset enumeration, 25 accepted/rejected cases, 644 funded query comparisons, and 5152 individual truth checks. Its random program sample uses seed 20260913. The store test uses 13 cases in fresh temporary directories and actual Lean subprocesses; its interruption test raises a controlled Python exception, not SIGKILL or power loss. Existing paths are not overwritten.

The collector requires all 150 successful current sources/import outputs/logs, the exact 1447-name axiom audit, 71 substantive negative rejections, baseline byte identity, and current regression/source pins. Older filesystem/crash/retry suites are retained as historical records and not rerun here.

## Metadata and packaging

    python tools/record_v027_audit.py --baseline /path/to/semantic/AVOC_Formal_v0.26.0.zip
    python tools/audit/validate_computation_manifest.py results/v0.27.0/computation_manifest.json --root .
    python tools/package_v027.py --output /chosen/AVOC_Formal_v0.27.0.zip

The recorder times a fresh evidence collector, not all earlier builds/tests. The local validator is the inherited documented v1-only adaptation; metadata validation does not prove a theorem or authenticate the physical runtime. Per-file and per-test records supply the detailed hashes.

Check the ORIGINAL payload manifest before regeneration. Regeneration intentionally changes hashed evidence. Do not hash the manifest into itself or write its own check log over a hashed file. Packages omit .lake, .git, runtimes, bytecode, and compiled Lean outputs. Old wrappers are preserved with their versioned checking records; this release's new working interface is global_library.py.
