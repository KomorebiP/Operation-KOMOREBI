# Build and verification instructions — publication 1.3.0

## Verify before changing the package

Run `python3 checks/verify_payload.py` in the extracted root. It verifies the manifested bytes and rejects standalone font files, including in nested archives. Embedded PDF fonts are expected. Disposable Python, TeX, and local Lean caches are excluded consistently.

## Rebuild the publication

Install the packages in `requirements-publication.txt` and TeX Live providing the imports in `source/preamble.tex`, then run:

```bash
bash build.sh
```

The command checks archive/source integrity, the source concordance against the accepted **1.2.0** declaration inventory, the historical import-union inventory, four exact finite suites, figure generation, evidence counts, three-pass PDF builds, and mechanical preflight. The new commands are `checks/expansion_exact.py` and `checks/build_expansion_figures.py`. The first checks every formal file against the frozen 1.2.0 baseline. **This command does not execute a new Lean replay.**

Do not use a short wrapper timeout for the whole publication build. The accepted build has an explicit zero exit code and elapsed time in `audit/expansion/build_final_receipt.json`. That timing is a record for one run, not a performance guarantee. Regeneration changes timestamps and hashes, so finish intentional edits before renewing the manifest.

The static historical import inventory describes the original 133-module union. The accepted formal record describes 138 production modules and a root after the five 1.2.0 additions. These are different scopes, not contradictory inventories.

## A separate new formal replay

The runtime is not bundled. Supply the pinned Linux portable Lean 4.34.0-rc2 runtime and its matching dependency cache, then use a fresh label:

```bash
python3 formal/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent1
```

The unchanged verifier checks the toolchain and nine dependency pins, the full import closure, positive-source policy, 139 compilation targets, declaration axiom dependencies, and the positive and seven rejection/policy controls. It refuses to overwrite an old replay directory. The accepted supplied formal record is `audit/formal/replay2/receipt.json`, generated for version 1.2.0, not for this expansion.

A different formal source tree requires a new versioned formal release and an explicitly updated baseline. Do not replace `audit/expansion/baseline.json` merely to bypass its unchanged-source check. The inherited `checks/finalize_formal.py` is a version-1.2 binding script, not an automatic publisher of a new formal version; preserve old records and review its version assumptions before intentional rebinding.

## Render and inspect

```bash
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

Inspect every contact sheet and enlarge changed formulas, diagrams, and tables. Rendering is not itself a visual-review pass. Renew `audit/visual_review.json` only after reviewing the final PDF bytes. The delivered record includes a pixel comparison to reviewed draft renders and individual inspection of the changed final pages.

After final intended payload edits:

```bash
python3 checks/hash_manifest.py
python3 checks/verify_payload.py
```

Avoid writing a build log inside the package after generating its final manifest. Such a log is itself a changed payload and needs a new hash.

## Trust and portability boundaries

No new compiler run, independent kernel, full-source mathlib rebuild, native Windows test, or universal verification of the Python implementation was performed in this publication expansion. Formal dependencies remain those recorded in the 1.2.0 baseline. Mathematical images are generated from explicit formulas; no standalone font files are included.
