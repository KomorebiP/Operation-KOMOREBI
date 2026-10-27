# Runtime recovery failures

The first extraction commands were `tar --zstd -xf lean-4.34.0-rc2-linux.tar.zst`
and `tar --zstd -xf lean-4.19.0-linux.tar.zst`, each in `abc_private_runtime`.
They attempted to preserve archive ownership. This host rejected the packaged
UID and GID, with errors such as `Cannot change ownership to uid 1001, gid 1001:
Invalid argument` for the 4.34 release and GID 1002 for the 4.19 release.
The terminal tool truncated the large output, so a complete raw log of those
first commands is unavailable. Their command, error mechanism and completion
status are retained in this record. This was an environment extraction error,
not a Lean source failure or a mathematical counterexample.

Both first extraction processes completed with exit code 2. Tool session IDs
were 91269 for 4.34.0-rc2 and 97530 for 4.19.0. The error stream ended with
`tar: Exiting with failure status due to previous errors`.

The correction is to extract the unchanged authenticated archives with
`tar --no-same-owner --zstd -xf ...`. This changes host ownership handling only.
It does not change compiler or source bytes. Corrected command logs and status
are recorded by `extract_runtimes.py`.

After the corrected extraction, both Lean executables returned exit code 1
with `error: failed to locate application`. Both Lake version commands worked.
Absolute executable paths and `LEAN_SYSROOT` did not fix the Lean startup
failure. The retained `RUNTIME_VERSIONS.json` records the initial version
failure. `PROC_EXE_DIAGNOSTIC.json` records that `/proc/self/exe` is readable
while the Python process's own numeric `/proc/<PID>/exe` returns errno 13.
The official runtime source lookup is pinned in `RUNTIME_SOURCE_DIAGNOSTIC.json`.

A `strace` diagnostic was denied: `PTRACE_TRACEME: Operation not permitted`.
The denial is retained in `runtime_launch_attempt01.strace.log`. No tracing
result is claimed. The narrowly scoped compatibility shim then allowed both
unchanged official Lean binaries to report their exact versions and compile.

The initial ABCJet `lake update` recovered the exact pinned dependency sources
but exited 1 because its cache post-update hook tried to extract leantar with
packaged numeric ownership. The error was the same host ownership mechanism,
with UID 1001 and GID 118. The complete command log is `jet_lake_update.log`.
The unchanged leantar release archive was extracted into a task-specific cache
with `--no-same-owner`, and its executable/archive hashes and version are in
`LEANTAR_RECOVERY.json`.

The first subsequent `lake exe cache get` exited 1 because the ProofWidgets
release fetch failed. That output does not supply an HTTP status, so no HTTP
cause is inferred. The explicit verbose `proofwidgets:release` retry passed
and showed the exact pinned release URL. Both command logs are retained.

## Source style check and correction

The original ABCJet source then built successfully. It emitted two
`linter.unnecessarySeqFocus` warnings, at lines 19 and 53. Direct elaboration
with warnings treated as errors failed on those warnings. This is retained
under `jet_provenance_run`, whose provenance manifest records a failed run.
It is a style-check failure after successful proof compilation, rather than
a mathematical error. A separate copy makes the two sequencing changes
suggested by the compiler. Its build, strict direct elaboration and seven
axiom checks passed, with the original source unchanged. The exact diff and
both source hashes are retained.

## Report authoring

One final-report patch failed because its requested context line did not
match the actual wrapped paragraph. The patch was atomic and the report was
unchanged. Applying the patch with the exact context succeeded. This did not
affect a Lean source, theorem statement, compiler run or provenance manifest.
