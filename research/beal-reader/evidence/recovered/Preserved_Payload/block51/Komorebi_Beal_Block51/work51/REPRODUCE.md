# Reproduce Block 51

## Standard run

Extract the archive and open a terminal in `Komorebi_Beal_Block51`.
Use Python 3.10 or later:

    python verify.py

The new check and byte-integrity audit use only the Python standard library.
The output report is written beside the extracted directory as
`Komorebi_Beal_Block51_replay.json`, not inside its frozen contents.

## Full selected replay

    python verify.py --replay-predecessors

This runs the new exact check plus the six selected documented predecessor
computations. Their cached inputs are present, so no network or external
Python package is required for this selected run. Other historical scripts
are not part of this command and retain their own dependencies/boundaries.

Set a distinct external report path to preserve several execution records:

    python verify.py --replay-predecessors --report ../beal51_replay_2.json

Every subprocess has a 120-second wall limit by default. Override with
`--timeout SECONDS` only as a declared execution choice. No OS memory or
CPU limit is imposed by this runner. A timeout is recorded as inconclusive
and returns a nonzero exit status; no stale result is accepted. Python's
hash seed is fixed to zero and bytecode writes are disabled in subprocesses.
There is no random mathematical sampling.

## Source and bounds

`work51/computations/depth_checks.py` is the new executable. Its bounds,
coefficient field, excluded cases and negative controls are stated in
`TARGET_CONTRACT.md`. It can be run directly with `--output PATH`, but
use an external output path to preserve package integrity:

    python work51/computations/depth_checks.py --output ../beal51_exact_result.json

The portable runner first validates `PACKAGE_SHA256SUMS.txt`, the two
recovered original ZIPs, and frozen predecessor hashes. It then copies
the working tree to an isolated temporary directory, removes the old
result for each job, and runs a fixed list of inspected source commands.
The resulting JSON must equal its pinned reference. It rehashes code,
cached HTML and new proof notes before/after, and rechecks the package.
It never obtains a command from a result manifest.

## Validation and what it means

A successful runner exit means the declared finite computations replayed
and byte integrity passed. The JSON schema is the project's own
`komorebi.beal.portable-verifier.v1`, not an externally certified schema
or a proof-assistant format. The runner implements the stated validation;
no unavailable skill-specific manifest validator is claimed to have run.

The initial six predecessor replays are preserved separately in
`verification/predecessor_replay/REPLAY.json`. The final development run
of the new source, including stdout/stderr and hashes, is in
`verification/development_final_run/`. The package's release replay is
in `verification/RELEASE_REPLAY.json` when present. The external final
archive audit additionally verifies ZIP CRC and payload checksums.

No step compiles Lean or proves the universal written arguments. The full
source-dependent arithmetic chain is not re-proved by the selected replay.
