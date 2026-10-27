# Komorebi J-Space Causal Lab 1.4

Open `Komorebi_JSpace_Causal_Lab_v1_4.html` in a browser supporting JavaScript.
It is self-contained, uses fixed embedded weights, and makes no network requests.
No Python or Node is needed to use the app. Attachment previews may not execute it.

**New:** Across agents → Load guided case → Trace the connection.
Edit one agent. Compare direct effect, first-packet restoration, packet-only
replay and a whole donor reference. Inspect earlier/later checkpoints and reverse
the direction. The original direct editor and all earlier tabs remain.

This is a research instrument for candidate causal states, not a J-space
certificate. Start with `REPORT.md` and `checks/relay/FAILURES.md`.

## Source layout

`app/`: unchanged neural inference/weights/frames plus current and earlier UIs.
`runtime/`: original Python/PyTorch model definitions.
`checks/relay/`: current contract, raw compressed assay, numerical fixtures,
results, browser screenshots, actual command records and explicit failures.
`provenance/`: historical reports/scripts/manifests. Earlier versioned result
records describe their original execution, not automatic verification of all
current files. Use the current manifest and commands below.

## Rebuild and verify

```sh
python verify_package.py
python rebuild.py
node checks/test_relay_engine.js
python checks/check_relay_pytorch.py
python checks/audit_relay_results.py
python checks/test_relay_browser.py
python checks/test_previous_ui_on_1_4.py
```

The tested environment used Python 3.13, PyTorch 2.10.0+cpu, NumPy, Node 22.16.0,
and Playwright with system Chromium. The browser app has no external dependencies.
Individual checks are short. `checks/run_1_4_checks.py` is a foreground supervisor
for the full assay replay plus checks, with bounded child execution and exit
recording. It overwrites diagnostic output files; rerunning research scripts can
change timestamp-bearing records, so use an extracted copy for reruns.

The source manifest verifies file integrity, not scientific correctness. The
local computation-manifest check is not the canonical Mathbox executable.
