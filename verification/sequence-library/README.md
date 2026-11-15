# Finite sequence-library evidence

Current evidence: `run-005/manifest.json`, status `completed`, with
`run-005/checks.json`. The input contract is `contract.json`. Earlier runs are
retained development records; their source hashes precede packaging, notation,
attribution, and portable line-ending refinements.

The current exact checks cover 1,783 new parameter records and all 42,792 stored
terms / index maps. Independent comparisons include 2,880 reciprocal terms,
360 tangent coefficients, 3,240 hypergeometric seed coefficients, 6,336
congruential rational coefficients, 1,920 Appell rational coefficients, 16,032
reduced integer components, 24,024 classical-subsequence terms, and 3,696
subsequence hypergeometric coefficients. These overlapping check counts are not
counts of distinct mathematical results.

The complete OEIS replay scans 401,422 retained records against all 1,911 local
records. It reproduces 2,866 retained hits and 372,883 observed hit positions,
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
reference matching, export/sharing, no-JavaScript tables, and enlarged text /
forced colors. These checks are not accessibility certification. The
mathematical proofreading scope is recorded in `PROOFREAD_REVIEW.md`.
