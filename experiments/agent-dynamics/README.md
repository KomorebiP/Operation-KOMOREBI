# Agent Dynamics — Python Visual Atlas
## Internal state, external feedback, and interaction between agents

**Operation Komorebi · Python visual companion v1.0 · 9 October 2026**

This companion replaces generated infographic artwork with reproducible Python diagrams and numerical displays. It is a new illustrative model, not a revision of the theoretical manuscript.

## Start here

- `Agent_Dynamics_Python_Visual_Atlas.pdf`: fourteen landscape pages, with one main figure per page.
- `Agent_Dynamics_Animated.gif`: eighteen synchronized agent/environment frames.
- `Agent_Dynamics_Interactive.html`: self-contained offline player. Open it in a browser to play, pause, step, or drag through the events. It contains all its own images and makes no network requests.
- `plates/`: all fourteen figures in editable SVG and high-resolution PNG.
- `frames/`: every animation frame as a PNG.

## What is being visualized

Two explicit finite-state reasoners receive different bit observations of one source location. They retain separate probability distributions and evidence histories, and share receipts through a reliable message channel.

A sensor convention changes between investigations. An impossible report triggers a supplied reset rule: the observing agent archives stale evidence and expands its model to include both possible sensor conventions and all source locations. A message carries that change to the other agent. Ordinary readings eventually leave two compatible explanations. Repeating those readings does not resolve the ambiguity. A separate calibration does, and a checked action is then issued.

The source location displayed in the environment is **viewer-only truth**. Neither agent receives that value directly. Belief probabilities are exact uniform weights on the compatible finite cases. The entropy and plotting coordinates are numerical summaries of those probabilities.

The schedule, sensor semantics, reset policy, communication protocol, and action gate are supplied. This illustrates inference, memory, model revision, and interaction. It does not demonstrate a learned query policy, neural activation dynamics, consciousness, or recursive improvement of the update algorithm.

## Regenerate with Python

Python 3.10 or newer is required. From this folder:

```bash
python -m pip install -r requirements.txt
python build.py
```

On Windows, `py` may be used instead of `python`:

```powershell
py -m pip install -r requirements.txt
py build.py
```

The diagrams and charts use Matplotlib. Pillow writes the GIF. No standalone font files or generated image assets are required. The source uses the default Matplotlib colors and colormap, with line styles and hatching as supplementary distinctions.

To run only the finite checks:

```bash
python code/model.py
```

`code/model.py` contains the state-update rules. `code/visuals.py` contains the drawings, charts, animation, and HTML packaging. Each chart uses one axes in its own figure. The 3D plot is a projection of explicit belief distributions onto expected binary coordinates, not a simulated neural embedding.

## Data and checks

`data/agent_trace.json` records all private states, exact rational probabilities, receipts, model epochs, predictions, and event counts. `data/agent_trace.csv` is a compact tabular export. The reference checks cover all eight source locations under the specified schedule, receipt deduplication, model contradiction, calibration, and three matched evidence-access conditions.

The main example uses seven ordinary observations, one calibration, seven message bundles, and one external action. Under the declared prices of one per ordinary observation, two per calibration, and one per external action, sensing plus action costs ten units. Messages, computation, and storage are separate resources and are not claimed to be free.

The no-message and no-calibration comparisons are exact comparisons of available post-change evidence. They are not retrained-agent ablations or empirical performance estimates.

## Source relationship

The conceptual foundation is *Self-Improving Intelligence: Representation, Discovery, and Recursive Revision*, first edition v1.0.0, especially Sections 7, 9, 24, and 31. `SOURCE_MAP.md` specifies the relationship. No original manuscript or earlier guide was overwritten.

Read `REVIEW_NOTES.md` for the actual execution and visual-review scope, including resolved export and layout failures. Verify the frozen files before rebuilding with:

```bash
python code/verify_package.py
```

Rebuilding changes generated timestamps and may change PDF/SVG bytes across installations. The exact finite model and its data, rather than binary cross-platform identity, are the reproducibility target.
