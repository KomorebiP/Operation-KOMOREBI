# Current and historical verification

The current release is the **18 October 2026 proofreading**. Begin with
`proofread_2026-10-18/RELEASE_VALIDATION.json` and the root `PROOFREAD_REPORT.md`.
Only reports explicitly included there are current acceptance evidence.

The October 9 `MONOGRAPH_*`, `monograph_*`, and `monograph_checks/` records
remain dated historical evidence. Their original source and PDF pins are
preserved; they have not been silently rebound to revised sources. The
September 6 Lean compiler and axiom transcripts remain inherited evidence.

Current preservation means nine complete mathematical parts, exact preservation
of all 107 complete proof bodies and extracted mathematical spans, and the same
147 statement-kind records. It deliberately permits the six reviewed prose
clarifications and two figure-layout changes in two parts. It does not assert that all
nine complete files are byte-identical. The new comparator is read-only unless
`--report` is supplied; its original exact-file comparator is in provenance.

Failed intermediate font/PDF candidates are retained as diagnostic history in
the current review records. They are not accepted PDFs. The final visual report
pins each accepted PDF by SHA-256 and supersedes those failed candidates for
this release. Source proofreading and PDF rendering do not constitute Lean
kernel execution or universal mathematical certification.
