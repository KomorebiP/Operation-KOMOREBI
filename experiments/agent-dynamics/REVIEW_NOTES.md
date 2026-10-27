# Review and validation notes

**Agent Dynamics — Python Visual Atlas, v1.0**

## Delivered scope

Fourteen landscape visual plates, eighteen synchronized animation frames, an animated GIF, a self-contained step-through HTML player, exact finite-state model code, and exported numerical traces. Every diagram and chart is generated in Python with Matplotlib. Pillow packages the animation. No generated infographic image is used.

This is a new illustrative companion. It does not alter the canonical Self-Improving Intelligence manuscript or rerun that manuscript's full research suite.

## Numerical source

The state updates are explicitly implemented in `code/model.py`. A reasoner receives reports and messages but not the hidden source location. The renderer's view of world truth is separate from each agent's observation interface.

The two agents initially retain a uniform distribution over eight locations under one known sensor convention. After a supplied, unannounced change between investigations, an impossible report invokes a supplied reset rule. Old evidence is archived, not silently reused with changed semantics. An explicit message communicates that reset to the other agent.

Uniform post-reset beliefs and the selected query schedule are modeling assumptions, not learned behavior. This is not a noisy Bayesian change-point learner. The active finite model remains fixed between resets. The source is constant in each illustrated investigation. The reset mechanism does not guarantee safety or correct detection under arbitrary drift.

The plots show location probabilities, location entropy, joint source/convention ambiguity, predictions made before receiving each report, and the actual event sequence. The 3D coordinates are expected high/middle/low bits computed from the complete probability vector. That projection is explicitly identified as lossy.

## Executed checks

- 684 assertions passed, covering all eight possible source locations under the declared eighteen-event schedule, exact probability normalization, initial and calibrated identification, contradiction handling, repeated observations, message deduplication, and matched evidence-access comparisons.
- The saved final JSON trace matches a fresh execution of the model.
- The final PDF contains fourteen pages. All were rendered through PyMuPDF and inspected in a contact sheet. Selected full-page diagrams, the 3D plot, and full-size animation frames were also inspected.
- The final PDF has no detected out-of-page words or Unicode replacement characters.
- The GIF contains eighteen frames; all eighteen underlying PNG frames were inspected in a contact sheet.
- Fourteen SVG plates and fourteen PNG plates were exported.
- The standalone HTML embeds all eighteen Python-rendered frames and has no external assets or network calls. The play/step/slider code was inspected. Browser automation and cross-browser execution were not performed.

The tests are project-authored finite implementation checks, not independent proofs, empirical AI measurements, or independent external replication. A mathematical model can be internally consistent without describing a particular deployed agent.

## Corrections actually encountered

1. The first Python-visible export failed with a `PermissionError` when writing `data/agent_trace.json`. The runtime executing the plotting code did not have write permission on the container-created output directories. Permissions were corrected within this new project folder, and export was rerun successfully.
2. Visual inspection found that a generic empty-body box helper centered certain container headings over their contents. A dedicated top-header option moved the environment, agent, and action-check headings above the numerical displays. All affected figures and animation frames were regenerated.
3. A prediction-to-revision arrow crossed its label. It was rerouted, and the message-channel annotation was moved away from the agent boundary. The action-gate arrow was moved to avoid an unintended crossing of the message route.
4. Zero entropy was initially displayed as negative zero from floating-point formatting. It is now normalized to nonnegative zero. Singular location and receipt labels were corrected. The exact probabilities were unaffected.

No model assertion failed in the completed runs. The export failure and visual corrections are not erased by the subsequent successful exports.

## Reproduction boundary

The delivered `build.py` regenerated the model data, atlas, and animation through its component functions in this interaction. The recorded package versions are in `validation/execution_environment.json`. The model was then rerun in a fresh interpreter and its complete trace compared with the stored JSON.

A clean-environment installation, Windows execution, external peer review, PDF/A, and accessibility tagging were not certified. The SVG/PDF contain ordinary vector drawing data; no standalone font file is included. Snapshot hashes check file integrity, not source authenticity or mathematical truth.
