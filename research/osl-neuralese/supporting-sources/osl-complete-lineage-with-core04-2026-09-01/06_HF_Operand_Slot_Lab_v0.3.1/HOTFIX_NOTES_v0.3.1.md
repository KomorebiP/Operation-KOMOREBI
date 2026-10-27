# v0.3.1 packaging hotfix

## Failure repaired

The v0.3.0 PowerShell launcher started a transcript inside the extracted source
directory before calling `verify_package.py`. Exact manifest verification then
correctly rejected that newly created, unmanifested transcript. This prevented
the smoke profile from reaching dependency checks or model execution.

## Changes

- The live PowerShell transcript is now written to the operating-system temp
  directory. On failure it is still included in `FAILED_OSL_HF_V03_*.zip`.
- Exact source verification now excludes only narrowly recognized generated
  artifacts: Python bytecode, top-level `results`/`results_*` trees, launcher
  transcripts, and launcher failure ZIPs.
- Unexpected source files and all source checksum mutations remain fatal.
- Release assembly has a strict clean mode that also rejects recognized runtime
  artifacts before the outer ZIP is built.
- The documented extraction command uses a new timestamped destination, which
  prevents files from an older extraction from contaminating a fresh test.

## Scientific status

There are no model, data-generation, loss, metric, threshold, seed, profile, or
experimental-protocol changes from v0.3.0. Results from v0.3.0 and v0.3.1 are
scientifically comparable; v0.3.1 only makes the packaged runner executable.
