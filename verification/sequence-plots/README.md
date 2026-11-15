# Plot customization: bounded software verification

Current model receipt: `run-003/manifest.json`, status `completed`. Its 16 Node
tests pass. Runs 001-002 are retained from before the final exported-title and
explicit signed-logarithm label adjustments.
The complete local regression run contains 42 Node tests, 10 atlas Python tests,
and the existing frozen-root-attributes guard. The separate source replay is
`../sequence-archive/run-006/manifest.json` and reports `passed`.

The model tests visit all 90 recovered records and their 5,487 terms. For each
record they test windows of size 1, 2, and min(32, stored length), at their first
and last valid starts, using previous/next/zoom-in/zoom-out/fit actions. They also
test every full stored window and the four display presets. Every selected raw
value must remain the corresponding exact integer string at its original index.
All 23 complete coefficient-row windows are checked against separately generated
ladder polynomial rows. Preference/link validation and sparse/coincident labels
use the explicit fixtures in `tools/test_sequence_plot_options.mjs`.

Browser checks cover 1440px, 390px and 320px layouts, shared appearance links,
recipient preference overrides, palette/color/size/line/grid/axis controls,
remember/reset, denied storage, window navigation, triangle rows, standalone SVG,
and 2x PNG dimensions. The existing atlas and archive browser suites retain
their exact-data, keyboard, clipboard, no-JavaScript and responsive checks.
Exported images and phone charts were visually reviewed. These are bounded
implementation checks and self-review, not accessibility certification or new
mathematical review. Floating chart coordinates remain approximate.

All 384 existing exact CSV, JSON and indexed-text exports are byte-identical to
the prior preview. The recovered source folder now disables text conversion for
all its files, preserving the original source bytes in future checkouts without
changing the frozen repository-root attributes. No original mathematical source
blob was modified.

Reports and screenshots are retained in the task workspace's
`sequence-plot-review/` folder. Publication, deployment and live verification
are recorded separately there.
