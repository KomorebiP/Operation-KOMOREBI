# Komorebi J-Space Causal Editor 1.1

An offline interactive activation editor for the actual saved Workspace Incubator models. This is an inference-tool release, not a training release or certified J-space result.

## Open

Open `Komorebi_JSpace_Causal_Lab.html` in a JavaScript-enabled browser. Weights, fixed candidate frames, scripts and saved benchmark data are embedded. No account, network, Python or installation is needed for use. Some attachment viewers do not run HTML; a browser is required. No in-chat renderer or access to ChatGPT's hidden state is claimed.

The default tab is **J → output**. Click **Apply candidate edit**. In the checked default case, each agent's answer changes from [0,1] to [1,1]. Select other donor values or use the strength slider to recompute the actual frozen network's probabilities. **Reset edit** returns to the exact captured baseline, without a new episode.

The three advanced coordinate sliders add offsets within the fixed local J frame. They are measured in calibration standard deviations. The two agents have different bases; matching slider indices is not a proof of a common semantic coordinate system.

Change the late consumer or add a common continuation after the edit. Query changes do not mutate the recurrent state. The factual-memory audit reads independent copies of the before/after states and does not overwrite the active experiment. The source world is used for event initialization and evaluator scoring, never as a replacement for the answer head.

Controls include same-rank random directions, PCA, an activation-interaction basis, the J complement, whole native donor states and no edit. One-agent writes are separate from bilateral edits. Whole-state replacement is marked native only when both agents receive the same matched donor execution; fractional whole-state interpolation is disallowed in that mode.

The original **Memory & work**, **Recorded evidence**, and **Model & limits** tabs remain available. **Capture the memory/workbench state** copies the actual live repaired-model activations into the causal experiment. Those arbitrary captured phases are explicitly outside the fixed calibration family. Neither tab silently overwrites the other's session.

## What J means here

For each agent, we average gradients of four exact-report logits with respect to the pre-delay hidden state, propagating through two frozen silent updates. Centering the four rows bounds rank by three. Their top right singular vectors form a fixed three-row orthonormal matrix U.

The projected edit is

    h' = h + alpha * U.T @ U @ (h_donor - h)

followed by any common continuation, the silent delay and the unchanged answer head. At alpha zero, no edit is applied. At alpha one, only the candidate component is replaced. Optional manual offsets are also confined to this component.

The candidate is output-informed. Rank three is not an emergence discovery. The task has four pair values, not a language-model vocabulary. This app changes the small saved GRU models, not the assistant producing the chat.

## Native matched donors

The same factual source is advanced by two identity tokens to make the recipient. An equal-duration working program supplies a donor with the requested pair. The source world, private labels, observation history and cue remain fixed. A same-value target uses two left flips instead of the recipient's two identity tokens, providing a nontrivial program sham.

Selecting a requested donor value influences the native working program used to make the donor. It never writes a desired answer into the output field or logits. The model can fail. Its output and the exact evaluator are always displayed separately.

## Measured checks

The fixed calibration used 768 contexts per lineage, four native program alternatives, and seed 927710. A separate sampled bank used 256 histories per lineage and seed 927711. The frame was saved and hashed before that bank was evaluated.

Immediate bilateral J edits and J edits followed by a common swap both gave 100% exact donor-pair answers in the tested bank. The same-rank random and complementary replacements gave 0% donor-pair answers, retaining the factual result. PCA and the activation-interaction candidate also worked. No unique Jacobian superiority follows.

After immediate J edits, all eight facts were correctly recalled in 97.27% and 97.46% of agent-cases in the two lineages. Both intact baselines scored 99.41%. Current private-label recall was preserved in these banks. Perfect output control did not imply perfect later factual recall.

These 512 lineage-history evaluations use 256 unique procedural histories and reuse selected trained lineages and are not fresh training replications or an untouched primary study. There was no new natural-support audit. Projected hybrids remain artificial, with earlier stronger support failures unresolved. Native whole-state witnesses are a different, nonlocalized control.

## Validation and reproduction

The original engine passed its saved 4,608-decision PyTorch reference comparison. The new editor matched a further 1,344 tested decisions across 168 intervention paths in both Node and Chromium, including fractional edits, arbitrary coordinate offsets, complements, unilateral edits, native controls and later operations. Sampled agreement is not universal or bit-exact browser equivalence.

From this directory:

    node checks/test_port.js
    node checks/test_causal_port.js
    python checks/audit_causal_results.py
    python rebuild.py
    python checks/test_causal_browser.py

Node tests need no npm packages. The independent scorer needs NumPy. Browser tests use Python Playwright and Chromium; `CHROMIUM_PATH` can select the executable. Numeric reference regeneration uses the retained original architecture definitions in `runtime/` and the immutable exported weights, so a full historical training archive is not required:

    python checks/fit_causal_frames.py
    python checks/evaluate_causal_frames.py
    node checks/test_causal_port.js
    python rebuild.py

Those regeneration commands replace analysis files and their hashes; they are a new computation, not a verification of the original sealed file set. Timing and floating-point library differences may change files. Use `python verify_package.py` for integrity-only checking.

The browser tests load the exact HTML with Playwright `set_content`. They exercise desktop and 390-pixel phone views, causal controls, state nonmutation, native continuations, memory audits, exports, lineage changes, the old workbench and zero external requests. Attachment-client behavior is outside their scope.

See `REPORT.md`, `checks/causal_assay.json`, `checks/causal_independent_audit.json`, `checks/causal_port_validation.json`, and `checks/causal_browser_validation.json` for the exact evidence. `provenance/` preserves unchanged prior source and inherited test scripts as historical records.
