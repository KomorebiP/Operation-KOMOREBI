# Reproducing Paper II release 1.1.1

Run the commands below from the extracted release root. The current reading
edition is dated 19 October 2026. Release 1.1.1 adds the open license and release
documentation on 20 October 2026. The accepted scientific sources and reading
PDFs retain their exact reviewed bytes.

## Check the complete package

This check uses only Python's standard library:

```sh
python3 scripts/verify_package_integrity.py
```

It checks the complete inventory, file sizes, and SHA-256 hashes against
`MANIFEST_SHA256.json`. Run it before building or creating files inside the
release tree. The manifest excludes itself and Python bytecode caches.

## Check the source and publication evidence

On Linux or WSL, with Python and PyMuPDF installed:

```sh
python3 verification/open_release_2026-10-20/verify_release_bindings.py \
  --root . \
  --output ../Paper_II_binding_check
```

This checks all 75 current Lean module hashes and their order, the three Lean
configuration files, the 57 strict-audit inputs, the frozen module manifest,
the seven manuscript chapter hashes, and the reviewed PDF hashes, page counts,
text, and internal page destinations. It reads the successful replay receipt.
It does not run Lean or constitute a new mathematical acceptance decision.

## Replay the current formalization

The runtime is distributed separately. Use the pinned x86-64 Linux kit
`Komorebi_Portable_Lean_4.34.0-rc2`, on Linux or WSL. It must contain the Lean
toolchain, `compat/app_path.so`, and the pinned dependency repositories and
caches under `workspace/.lake/packages/`.

The driver authenticates the toolchain, dependencies, adapter, and relevant
cache bytes against `verification/closeout_2026-10-19/audit_driver/runtime_bindings.json`.
The runtime identity and archive hashes are retained under
`verification/closeout_2026-10-19/runtime_identity/`.

Set the kit path in this command to its location on your machine:

```sh
paper2_release_root="$(pwd)"

python3 verification/closeout_2026-10-19/audit_driver/verify_release.py \
  --root "$paper2_release_root/formal/current" \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --out "$paper2_release_root/../Paper_II_fresh_replay" \
  --manifest "$paper2_release_root/verification/closeout_2026-10-19/attempt02_m4096/execution_inputs/release_modules.json" \
  --lock-file "$paper2_release_root/../Paper_II_lean_replay.lock" \
  --timeout 600
```

The output directory must not already exist. The successful recorded run used
an 8 GiB container and a 4096 MiB Lean allocation limit. Its result is at
`verification/closeout_2026-10-19/attempt02_m4096/verification.json`:
75 production modules, 2,112 logical declarations replayed, and nine negative
controls passed. Lean's own kernel and the authenticated upstream cache are
the stated trust boundary. The upstream cache was not independently rebuilt.

The current manuscript correspondence accepts 53 of 53 enumerated proof-level
records under their stated hypotheses. This separate semantic record is at
`formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json`.

An ordinary pinned `lake build` compiles the source. It does not perform the
additional ownership audit, negative controls, or strict kernel replay above.

## Run the existing Python tests

Install the dependencies declared by
`source/canonical_v1.2.1/code/python/pyproject.toml` in your chosen environment,
including pytest. Then run:

```sh
PYTHONPATH="$PWD/source/canonical_v1.2.1/code/python" \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q -W error -p no:cacheprovider \
  source/canonical_v1.2.1/code/python/tests
```

The fresh 20 October run passed all 48 tests, including comparison of a fresh
finite experiment run against the stored results. The actual Python and
package versions, commands, source hashes, log, and JUnit report are retained
in `verification/open_release_2026-10-20/`. These are bounded numerical and
symbolic checks. They are not universal mathematical proofs.

## Rebuild the reading PDFs

Work in a copy of the release tree. Install XeLaTeX, BibTeX, Python, and
PyMuPDF. The required font files and their notices are bundled.

```sh
python3 publication/build_current.py \
  --map formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json \
  --edition-date 2026-10-19
```

This regenerates the traditional, visual, and Lean editions and their
navigation records. Rebuilding creates a review build and changes the file
inventory. A changed build needs its own page review and integrity manifest
before it is treated as a new release. The existing PDFs in this archive are
the exact previously reviewed 80-, 26-, and 51-page editions.

## License and historical evidence

`LICENSE.md` is the current project grant. Original software and
machine-readable material use MIT. Original prose and figures use CC BY 4.0.
Third-party sources and fonts retain their own terms and notices.

Older dated readmes, source snapshots, failed checks, and verification
receipts describe their original stages. Their absolute working paths are
provenance. The current commands above use the extracted release root and
explicit local runtime/output paths.
