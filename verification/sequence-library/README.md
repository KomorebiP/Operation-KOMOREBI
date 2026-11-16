# Finite sequence-library evidence

Current evidence: `run-008/manifest.json`, status `completed`, with
`run-008/checks.json`. The input contract is `contract.json`. This run replays
the same finite assertion after interface copyediting. Earlier runs preserve
the evidence for their recorded source inputs.

The current exact checks cover 1,895 parameter records and all 45,480 stored
terms / index maps. Independent comparisons include 2,880 reciprocal terms,
360 tangent coefficients, 3,328 hypergeometric seed coefficients, 6,336
congruential rational coefficients, 1,920 Appell rational coefficients, 16,032
reduced integer components, 24,024 classical-subsequence terms, and 3,696
subsequence hypergeometric coefficients. These overlapping check counts are not
counts of distinct mathematical results.

The 112 research additions contribute 2,112 ordinary secancy-polynomial
coefficients, 288 theta specializations and 288 theta-polynomial coefficients.
The independent oracle uses powers of 1-D_N and unsigned first-kind Stirling
coefficients for the secancy columns. Theta coefficients use a separate formal
polynomial recurrence for cosh(z)^(-x), followed by signed Euler convolution.
The stored windows retain their original n offsets. The seed hypergeometric
checks extend through n=31 for the new j=0, N=2..12 formulas.

The complete OEIS replay scans 401,422 retained records against all 2,023 local
records. It reproduces 2,869 retained hits and 372,886 observed hit positions,
including repetitive / low-information prefixes. It does not establish
infinite identities, novelty, or pairwise distinctness.

Run `python tools/audit_sequence_library.py --oeis --output RESULT_JSON` to
repeat the checks. The manifest records the bounded-run command, actual input
and result hashes, Python version, dirty source state, resource observations,
and timing. Validate it with the computation-audit skill's
`scripts/validate_manifest.py MANIFEST --root .`.

Frontend evidence is separate: the Node suites test exact query semantics,
palette/state validation and legacy behavior; browser suites exercise the
library and original plotting interfaces at 1440/390/320px, full-snapshot
reference matching and shared-excerpt restoration, scoped saved entries across
collections, four-source exact comparisons, arrow-key navigation, SVG/PNG/CSV
export and sharing, no-JavaScript tables, and enlarged text /
forced colors. These checks are not accessibility certification. The
mathematical proofreading scope is recorded in `PROOFREAD_REVIEW.md`.

The readability browser suite checks green and monochrome schemes, page display
modes, visible text contrast, saved preferences, and record offsets in HTML and
CSV. It also covers printing, no-JavaScript reading, enlarged text, forced colors,
and shared plot colors. All 6,069 existing exact data exports remain unchanged
after the editorial pass. These are local implementation/self-review results;
production delivery checks are separate.
