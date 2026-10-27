# Build and verification instructions — 1.2.0

## Integrity before mutation

Run `python3 checks/verify_payload.py` from the extracted root. It checks every manifested payload and recursively rejects standalone font files in nested archives. Embedded PDF fonts are expected. Disposable Python, TeX, and local Lean caches are excluded consistently.

## Formal replay

Supply the pinned Linux x86-64 portable runtime. From the root:

```bash
python3 formal/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent1
```

Use a new label for every attempt. The script verifies the compiler version, nine dependency pins, complete import closure, source scan, 139 clean compilation targets, project axiom dependencies, positive regressions, and seven rejection/policy controls. It terminates timed-out process groups and never treats timeout as success. Default timeout is 300 seconds per command, adjustable with `--timeout` for a slower machine. The delivered successful run used the timeout recorded in its command invocation/receipt; time limits are not performance guarantees.

A new accepted source version can be bound with:

```bash
python3 checks/finalize_formal.py --labels independent1
```

This overwrites the **current** release summary after verifying the named replay is PASS and still matches the source, tests, pins, and audit program. Preserve the delivered summary or work in a copy before rebinding. It never rewrites the individual replay records or original historical archives.

## Publication build

Install the packages in `requirements-publication.txt` and a TeX Live installation providing the imports in `source/preamble.tex`. Then run `bash build.sh`. It reruns archive/source comparison, current formal correspondence, the historical-union static inventory, three exact finite suites, figure generation, evidence counts, three-pass PDF compilation, and mechanical preflight. It consumes current accepted formal evidence but does not execute Lean itself.

The static inventory intentionally describes the original 133-module union. The current 138-module production graph and root are recorded by the formal replay. These are different scopes, not conflicting counts.

## Rendered review

```bash
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

Inspect all contact sheets and enlarged pages carrying changed formulas, diagrams, or tables. Rendering alone is not a review pass. Only after inspecting the final PDFs should `audit/visual_review.json` be renewed against their hashes. Run `python3 checks/hash_manifest.py` after every intended payload edit and `python3 checks/verify_payload.py` before distribution.

## Not bundled or not claimed

The external runtime, external mathlib caches, disposable local `.lake` objects, and standalone font files are not included. Native Windows, a full source rebuild of mathlib, an independent kernel, and a universal Lean refinement of the Python program were not tested or established by this release. Conventional Lake metadata is supplied, but the recorded replay route is the offline verifier above.
