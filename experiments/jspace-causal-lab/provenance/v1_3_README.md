# Komorebi J-Space Causal Lab 1.3

Open `Komorebi_JSpace_Causal_Lab_v1_3.html` in a browser. It is a self-contained offline HTML app with bundled model weights. Some messaging-app attachment previews do not execute JavaScript.

## Start

Open the **Does it last?** tab. Select **Load the guided case**, then **Run three-way comparison**. The app compares original, edited and donor-reference states through a real native swap, followed by factual reloads. The direct editor and persistent session remain under **J → output**.

To challenge a favorable example, use **Run fixed-setting challenge**. The same intervention settings are applied to every generated case. The exact evaluator cannot replace model outputs. Inspect failed cases as well as successful cases.

## Contents

`app/` holds standalone JavaScript inference, interface sources, immutable model weights and locked candidate frames. `runtime/` contains the original Python model definitions. `checks/robustness/` contains the new contract, all 384 assay traces, verification outputs and screenshots. Older evidence is retained separately by its original filenames and provenance directory. `REPORT.md` states exactly what ran and what did not.

## Rebuild and checks

The app itself needs no Python or Node installation. Source rebuilding and validation do:

```text
python rebuild.py
python verify_package.py
node checks/test_challenge_engine.js
python checks/check_challenge_pytorch.py
python checks/audit_challenge_results.py
python checks/test_challenge_browser.py
python checks/test_challenge_browser_numeric.py
python checks/validate_challenge_manifest.py
```

Python numerical tests require NumPy and PyTorch. Browser tests additionally require Playwright and a Chromium executable. The environment used here had Python 3.13.5, NumPy 2.3.5, PyTorch 2.10.0+cpu and Node 22.16.0. No exact dependency resolution or installation on another machine is claimed.

`checks/run_challenge_assay.js` refuses to overwrite its existing assay contract and evidence. Run it only in a separate copy after intentionally moving that copy's old assay output files aside. Its settings are recorded before outcomes; it does not train the models or tune the edit to each case.

## Interpretation

This is an instrument for actual upstream edits affecting frozen neural computation, not proof of naturally localized J-space. Factual recall and private-state preservation can fail. Whole donor references can also fail later computation. No connection to this chat model's internal activations exists.
