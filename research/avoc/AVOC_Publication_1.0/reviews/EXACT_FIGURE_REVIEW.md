# Exact examples and figures

The 18 publication figures were produced by `scripts/avoc_figures.py` using
Python and matplotlib. Numeric inputs use exact integers and rational
`fractions.Fraction` values. Conversion to decimal occurs at the rendering
boundary. The schematics were drawn directly in matplotlib and were visually
reviewed for readable labels, clipping and overlap. Captions and output hashes
are recorded in `figure_catalogue.json`.

## Fresh checks

- The inherited recorder test ran against its independent dictionary automaton
  on all 69,905 command words of lengths zero through four over 16 commands,
  with two IDs and two keys, plus 12 longer focused scenarios.
- Calibration regression checked 11,193 count-mass cases for n = 0 through 12,
  three fixed alpha values, 10 grid cells and the 41-point rational parameter
  grid i/40. Independent binary sequence enumeration checked 45 distributions
  for n = 0 through 8 and five fixed rational probabilities. Eighteen interface
  checks passed.
- An independent integer cross-multiplication implementation reproduced the
  exact grid-cell evaluator on the declared four cases, including n = 500,
  k = 400, m = 1000, alpha = 1/100. The archived actual fixture returned the
  same interval [361/500, 433/500].
- The two-attempt completion-order experiment enumerated all four Boolean
  vectors and reproduced first-report success probability 3/4.
- The twenty-attempt experiment evaluated 21 exact binomial count classes,
  representing all 2^20 equally likely initiation vectors for the specified
  success-first completion rule. The displayed event has mass 308333/524288.
  The full interval-miss mass is 616667/1048576.
- The deadline example reproduced completion probability 1/2 and conditional
  first-bit success probability 1.
- The actual rank-one F5 source in `examples/staged_affine/certain.json` was
  read and its dense versus width-one affine evaluation compared on all 625
  vectors in F5^4.

Figures 6 and 7 use the source's abstract uncertainModel quote-planning fixture.
They are explicitly labelled as abstract quote fixtures, in the initial untried
state, with setup costs 0 and continuation horizon h = 1. This means two total
actions: the selected stage and then deployment. The broad robust Q enclosure
has warm nominal 120 and radius 208, giving [-88, 328]. The exact warm
stage-then-deploy expected Q range is [120, 200], while cold Q is 60. The warm
range is not a primitive one-step reward. Figure 6 separates the broad enclosure
from that sharper Q range, so the conservative cold choice is not presented as
the true optimal action.

The fine-grid calibrated fixture has warm nominal 722/5, radius 1872/25 and
Q interval [1738/25, 5482/25]. Its lower endpoint exceeds distinct competitor
upper endpoints 60 and 0. These are valid abstract quote-planning values, not
artifact-backed saving examples. The fixture has calls = 1 and original
rankOneProgram execution cost 36. Its quoted gross amounts 200 and 60 therefore
cannot be supplied by an actual BoundedArtifact saving, which is at most 36.
The numerical values remain fresh exact-arithmetic reproductions, not fresh
calls to the Lean planner. This scope correction changed labels and captions,
not the previously recorded computations or their numerical results.

## Provenance and limits

`exact_run/manifest.json` and `recorder_run/manifest.json` are complete version 2
bounded-run provenance records. Both passed the computation-audit manifest
validator with project-root hash checks. Declared inputs were unchanged. The
exact run additionally checked all 16,913 inherited release files before and
after execution and found no byte changes.

The retained source release was not edited, and historical verification outputs
were not overwritten. Fresh results are in `exact_example_results.json`,
`fresh_python_checks.json` and `figure_render_checks.json`.

No new Lean compilation was run. These bounded Python checks do not imply
universal Python/Lean refinement. They do not establish authenticity, physical
source laws, durable storage or measured hardware cost. The completion-order
counterexample refutes an external applicability shortcut, not the formal
source-generative theorem.
