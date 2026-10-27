# Komorebi J-Space Causal Editor 1.2

Open `Komorebi_JSpace_Causal_Lab_v1_2.html` in a browser that permits local HTML scripts. The file is self-contained. It makes no external requests and requires no API key or installation for inference. The exact experience of opening an attachment depends on the client and device.

## Start

Select **Run the guided case**. This sets a fixed native episode, applies a bilateral J-candidate edit, audits facts, and commits original and edited branches. The two agents' original output is [0,1], and the edited output is [1,1]. Press **Swap** in the live panel: original becomes [1,0], while edited remains [1,1]. This is actual frozen-network inference, not text replacement.

The candidate editor and the committed trajectory are deliberately independent. Editing a preview control cannot silently restart or alter a committed experiment. Press **Commit current edit** to explicitly start a new one. Each working action includes two silent recurrent updates. Reading a new query does not advance state.

## New controls

- **Scan edit strengths** tests 21 values from 0 to 1 at increments of 0.05. Native whole-state mode tests only its two endpoints. Manual coordinate offsets are zero during diagnostics. Scores, predictions, facts, and private labels are measured, not interpolated. Selection of a favorable grid point is explicitly case-specific, not independent validation.
- **Run all controls** compares no edit, report-J, activation, PCA, random, complement and whole donor on identical initial states and suffixes. New memory errors are compared bit by bit, not only as net accuracy.
- **Commit current edit** starts persistent original/edited trajectories. Flip, swap, run a custom continuation, wait, reload facts, cut retrieval wires, inspect all consumers, undo, or audit memory.
- **Export / import session** records the actual activation origins, exact checkpoint/frame hashes, and action sequence. Import recomputes predictions. Saved answer fields cannot replace model output. An imported snapshot is not authenticated native provenance.
- Mobile trajectory rows become stacked cards. Controls retain labels, focus styles, error messages, and cancellation of outdated diagnostics.

## Scope

No neural training was done for editor 1.2. Model weights, inference engine, and candidate frames are unchanged from editor 1.1. The models are small saved GRU dyads, not this chat assistant's internals.

A report-J candidate is output-informed and three-dimensional because four centered report-class gradients have rank at most three. Other same-rank frames can also control output. Projected edits remain artificial, and the earlier natural-support failures are not repaired by these UI changes. Memory may fail during longer or repeated computation. No certified J-space or general preservation result is claimed.

The retained factual audit uses four independent branches. A sequence of live reloads, in contrast, carries state forward. Do not conflate those measurements.

## Rebuild and test

The HTML builder uses Python's standard library. Numerical checks need the already-declared NumPy/PyTorch runtime; browser tests need Playwright and a Chromium executable. Node runs the reference and engine-contract tests. Recorded versions are in `checks/REFINEMENT_EXECUTION.json`.

```text
python rebuild.py
node checks/test_port.js
node checks/test_causal_port.js
node checks/test_refine_engine.js
node checks/make_refine_numeric_fixtures.js
python checks/check_refine_pytorch.py
python checks/test_causal_browser.py
python checks/test_refine_browser.py
python verify_package.py
```

Tests write their result artifacts. Browser screenshots and exported-trial timestamps may differ on rerun, so verify the released file manifest before rerunning tests. A rerun is not expected to preserve the released screenshot hashes. Rebuilding the HTML without changing its inputs is deterministic.

`checks/check_file_open.py` is a separate local-file launch assay. The hosted test environment blocks file:// navigation by administrative policy. That attempt did not pass and is recorded separately; the browser tests use `set_content` on the exact built HTML instead.

## Files

`app/engine.js` and `app/causal_engine.js` are the inherited inference and intervention implementation. `app/refine_engine.js` adds diagnostic and trajectory primitives. `app/refine_ui.js` supplies their browser interface. The original PyTorch modules are in `runtime/`. `checks/` contains tested paths, raw outputs, and verification. Selected earlier code and reports are preserved under `provenance/`.

Raw logits, memories, and contexts remain in exported JSON. Correct answer references are used only for scoring and are not inputs to neural output heads.
