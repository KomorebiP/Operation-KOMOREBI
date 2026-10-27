# Build and verification — publication 1.7.0

## Verify before editing

Run `python3 checks/verify_payload.py` from the extracted root. It checks complete manifest coverage and hashes and scans nested archives for standalone font files. Embedded PDF fonts are expected. Disposable `.lake`, `.work`, Python and TeX outputs are excluded.

## Regenerate the reader set

Install `requirements-publication.txt` and TeX Live with the packages in `source/preamble.tex`, then run `bash build.sh`. The exact example programs use the Python standard library; some independent regression suites also use the declared SymPy dependency.

The build checks the proof-edit inventory, both unchanged formal source trees, frozen archives, canonical formal-file preservation, the retained KS concordance, the focused execution evidence, the separate WR coverage ledger, seven finite suites, rational examples, figure generation, three-pass typesetting of each PDF, and mechanical preflight. **It does not run Lean.** A successful source-bound audit check is not relabeled as new compiler execution. The accepted publication build and final review are identified in `audit/proof_detail/release.json`.

Preserve failed or interrupted build records. A partial PDF or a log ending before a terminal receipt is not successful build evidence. Use a supervised process for commands that exceed the outer tool window.

## Exact optimizer and proposal verifier

```sh
python3 examples/budgeted_repair.py
python3 examples/inexact_repair_certificate.py
python3 examples/inexact_repair_certificate.py --input problem.json
python3 examples/inexact_repair_certificate.py --verify certificate.json
```

Minimal proposed-correction input:

```json
{"d":[[1,0]],"p":[[1,-1]],"f":[1,0],"alpha":"1","correction":["1/4","1/4"]}
```

Use integers or rational strings, not floating-point entries. `measured_residual`, a full independent kernel `basis`, and `dual_witness` are optional. The verifier checks the actual preservation equation and Gram metric before issuing bounds. The measured fit and the actual model residual of the repaired candidate are returned separately. Error bounds are squared rational quantities. Arbitrary dual witnesses are valid but may be loose. The program certifies the declared regularized problem, not unknown physical truth or unregularized solvability.

The retained independently rerun suite is `checks/inexact_certificates_exact.py`. Its full ambient constrained-system oracle uses determinant formulas rather than the certificate program's kernel elimination route. This is finite implementation evidence, not universal refinement.

## Reproduce the focused formal extension

The portable runtime is not bundled. Supply the pinned Lean 4.34.0-rc2 Linux runtime and matching dependency cache:

```sh
python3 extension/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent-focused1
```

The verifier refuses to overwrite a label. It constructs the actual seven-target import closure in a fresh `extension/.work/<label>` directory, checks all nine dependency revisions, compiles every supplied module, audits all module-origin project declarations, and runs positive, false-claim, placeholder and custom-axiom-policy controls. The accepted source-bound record is identified by `audit/extension/release.json`. Every axiom is inspected even where a long declaration type is not included in the exported text.

The focused replay is **not** a cumulative replay of the canonical 138-module tree. The latter remains byte-identical to its accepted v1.2.0 baseline and can be independently replayed with:

```sh
python3 formal/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent-canonical1
```

The historical attempted cumulative label `baseline16` was explicitly interrupted before completion. It is not accepted. Never weaken the canonical preservation check to make a changed source tree appear unchanged.

## Render and renew integrity

```sh
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

Inspect contact sheets and enlarge new formulas, figures and tables. Rendering alone is not a review. Review records bind the final PDF hashes to the inspected pixels. After all intended payload edits, run:

```sh
python3 checks/hash_manifest.py
python3 checks/verify_payload.py
```

Do not append a log after the final manifest without renewing it. Runtime files, compiled caches, untracked temporary outputs and standalone fonts do not belong in the delivered ZIP.

## Remaining trust and coverage boundaries

The official kernel/compiler and pinned imported dependency caches remain trusted. Mathlib was not rebuilt from source and native Windows execution was not tested. Formal coverage is complete for focused WR06/07/13/14, partial for WR09/16, and written-only for the other ten WR groups. Source correspondence is editorial, and Python implementation tests are finite.

## Proof-exposition inventory

`checks/proof_detail_audit.py` compares recorded proof changes with the preserved v1.6.0 sources. It checks unchanged principal theorem statements, inherited labels, and both formal-tree file inventories. It binds the expanded proof texts to hashes and generates `PROOF_EXPANSION_MAP.md`. This is an editorial integrity check, not natural-language proof verification. The five analytic background lemmas are written support, not additional formally verified results.
