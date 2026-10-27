# Build and verification — publication 1.5.0

## Verify the delivered bytes before editing

From the extracted root run `python3 checks/verify_payload.py`. It checks the manifest, rejects extra substantive payloads, and scans for standalone font files, including nested archives. Embedded PDF fonts are expected. Disposable Python, TeX, and Lean caches are excluded.

## Rebuild the publication

Install `requirements-publication.txt` and TeX Live with the packages in `source/preamble.tex`, then run `bash build.sh`. The exact example program itself uses only the Python standard library. The independent ambient KKT test additionally uses SymPy; the pinned publication requirement is included.

The build checks frozen archives, source correspondence, formal-file preservation, six finite suites, the separate WR scope ledger, rational examples, figures, three-pass PDF typesetting, and mechanical preflight. **It does not run Lean.** The accepted execution for this edition is `audit/regularization/build06.json`, with its portable log copy in the same directory. Its recorded elapsed time is an execution fact, not a runtime guarantee. A short outer tool timeout can interrupt the entire pipeline; preserve terminal receipts rather than treating a partly written PDF as success.

## Exact protected repair example

```bash
python3 examples/budgeted_repair.py
python3 examples/budgeted_repair.py --input problem.json
```

A minimal `problem.json` is:

```json
{"d":[[1,0]],"p":[[1,-1]],"f":[1,0],"alpha":"1"}
```

Use integers or rational strings such as `"1/3"`, not JSON floating-point numbers. `measured_residual` is optional. When provided, the fitted residual uses those data while the true candidate residual is still computed from the supplied D and repaired candidate. The actual preservation equation is enforced, not merely penalized. The returned `budget_certificate` gives a rational numerator and squared norm for the unit dual witness, avoiding rounded square roots. It certifies the fixed model and target data, not unknown physical truth. The kernel Gram matrix is essential unless the chosen basis is orthonormal.

The command `python3 checks/regularization_exact.py` separately runs the written-extension finite audit. It includes adjugate and ambient KKT oracles and retains the normal-equation, budget, affine-energy, noise, and tail distinctions.

## A separate fresh formal replay

The pinned runtime is not bundled. Supply the Lean 4.34.0-rc2 portable Linux runtime and its matching cache, then run:

```bash
python3 formal/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent1
```

The verifier refuses to overwrite a prior replay. The retained accepted record is `audit/formal/replay2/receipt.json`, produced for v1.2.0. Its scope is 138 production modules and the root, not the new written WR statements. The earlier static 133-module import-union inventory has a different historical scope. Adding WR formalizations requires a new versioned formal baseline. Do not weaken or overwrite the inherited unchanged-source check to make edited sources pass.

## Render, inspect, and renew integrity

```bash
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

Inspect every contact sheet and enlarge new formulas, diagrams, and tables. Rendering alone is not a review. The current review record binds the final PDF hashes to the inspected draft and final pixels.

After every intended payload edit, run:

```bash
python3 checks/hash_manifest.py
python3 checks/verify_payload.py
```

Do not append logs inside the package after the final manifest without renewing it. New timestamps are genuine new bytes. Neither manifest validation nor the WR metadata validator certifies a mathematical proof.

## Trust boundary

No new compiler run, independent kernel, full-source mathlib rebuild, native Windows test, or universal Python-to-Lean refinement was performed. The exact finite audit verifies stated cases, not unbounded quantifiers. The twelve new theorem groups have complete printed proofs and explicitly separate formalization obligations.
