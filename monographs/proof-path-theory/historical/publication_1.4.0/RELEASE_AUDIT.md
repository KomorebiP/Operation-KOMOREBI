# Proof Path Theory 1.3.0 — publication and software audit

This is the monograph editorial release, not a new cumulative Lean release.
`PROOFREADING_REPORT.md` records the substantive changes. The current dated
aggregate is `data/editorial_verification.json`. `data/release_verification.json`
identifies that same scoped result and separately points to the earlier full
technical run under `historical/v1.2.0/`.

The current audit checks Python syntax and tests, finite comparisons, binary
realization certificates, the previously generated native export, manuscript
cross-references, the complete appendix JSON, package installation, and the PDF.
The inherited formal sources and 35 evidence files are compared byte-for-byte
against recorded v1.2.0 hashes. No compiler invocation is inferred from that
comparison.

Five diagnostic regression cases intentionally fail against the old source:
one admitted-leaf case and four exact-cost-selection cases. Their separate logs
are retained in `editorial/logs/`. The final suite passes all 111 cases. Source
changes are recorded in `editorial/certificate_patch.diff`.

Existing standard-axiom and negative-control records retain their original scope
and timestamps. The complete manuscript is not formally certified as a whole,
and this review does not count source labels or prose corrections as newly
verified theorems.
