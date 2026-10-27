# Editorial development and failure record

This record concerns the new visual appendix and package, not a new Lean release.

1. The first graphics generation exposed two Python invalid-escape warnings (`\Delta` and `\mathrm`). Those strings were changed to raw strings and generation was rerun with warnings treated as errors.
2. The first two LaTeX attempts stopped on U+0008 characters introduced by ordinary Python `\bmod` strings in two plate headers. Those strings were made raw. The failed compiler outputs remain under `editorial_evidence/development/`; neither failed attempt was counted as a build pass.
3. The first complete 30-page draft had an overfull paragraph because a `tabularx` environment immediately followed prose without a paragraph break. Explicit paragraph separation fixed it. The final appendix has no box warnings.
4. Review of the opening plate found a misleading juxtaposition of a generic residue address and the Euler family's different denominator address. The generic selector address is now `k=Nq+r`, with `r=k mod N`. The Euler normalization/address convention is explained separately on V-2 and V-6.
5. A redundant set of column labels on the row-weight plate was removed, and “depth-one truncation” replaced the less explicit “one-edge truncation.” No mathematical source was changed.
6. The preserved evidence-index replay reports two already-documented stale summary counters in a historical strengthening inventory (theorem and definition counts). The authoritative reconciliation uses the actual declaration entries, source hashes, and recorded axiom sets; it does not revise historical files or promote those counters to a fresh theorem total.
7. The original manuscript rebuilt successfully with its existing one underfull-box warning. All 48 pages match the preserved PDF in extracted text and rendered appearance. That warning was retained rather than hidden by editing the manuscript.

All final positive assertions and deliberate false controls passed in the intended senses. The final PDF and package replays are separate evidence from these corrected drafts. No Lean process, original missing numerical package, or external-paper reauthentication is claimed.
