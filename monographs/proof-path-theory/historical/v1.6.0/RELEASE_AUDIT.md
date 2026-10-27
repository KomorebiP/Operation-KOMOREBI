# Proof Path Theory — final proofreading and verification, edition 1.6.0

**Author:** Komorebi P.  
**Date:** 19 October 2026  
**Publication:** 1.6.0, 62 pages and 22 numbered vector figures  
**Python distribution:** 1.4.0  
**Formal evidence:** inherited technical release 1.2.0; no new Lean run

## Applied mathematical corrections

**Refinement and task preservation.** Section 23 no longer infers a recoverability
chain merely from reconstruction of the certified target. It supplies an explicit
recovery map between representation schemes and proves decoder transport by
composition. It also explains why target preservation alone need not preserve
provenance, examples, or side-record queries. This is a written argument, not a
new Lean theorem.

**Endpoint equivalence.** Definition 11.1 now fixes the background theory,
interpretation, inference policy, and complete assumption context. The relation
is not inferred from identical target and premise labels while ignoring admitted
axioms or external assumptions.

**Positive-rule models and protected fibers.** The unrestricted positive-rule
system always admits the full node set as a model. A prescribed extension fiber
can still be empty. The text now states this directly and keeps some-model
membership distinct from derivability in the least model. The seven-model visual
study and the pairwise-gluing counterexample explicitly take the admissible-leaf
set to be empty, not merely the required-premise set.

**Provenance.** Proposition 19.3 and its proof distinguish serialization from
hashing. Determinism supplies equal digests for equal serialized bytes. Detecting
a record difference additionally requires that its encoding retain that
distinction. No universal collision-freedom claim is made about SHA-256.

**Conclusion and reference material.** The conclusion distinguishes declared
certified closure from semantic validity, which still needs sound leaves and
rules. The reference appendix carries the corrected assumptions and scopes.

All 33 result groups remain. Of the 131 pre-existing mathematical environments,
127 are byte-identical to edition 1.5.0. Four changed: the gluing example's leaf
hypothesis, the endpoint definition, and the digest proposition and proof.
The unnumbered refinement argument and explanatory paragraphs are tracked
separately. The approved environment hashes and complete source diff are included.

## Actual software defect repaired

The old `provenance_digest` joined string parts with a separator. Two distinct
input tuples containing that separator could produce exactly the same bytes,
and zero parts collided with one empty part. The failure occurred before
hashing. Both regressions fail against the untouched Python 1.3.0 baseline.

Python 1.4.0 uses a versioned prefix and a JSON array of strings. It rejects
non-string parts and surrogate code points, while preserving empty parts,
ordering, tuple boundaries, and accepted Unicode scalar values. The surrogate
restriction prevents JSON's escaped-pair representation from identifying an
ill-formed Python surrogate pair with an actual supplementary Unicode scalar.
Historical version-1 digests must retain their format markers. The snapshot
serializer and all certificate, realization, and review algorithms are unchanged.
See `docs/PROVENANCE_FORMAT.md` for the exact byte contract and migration rules.

## Publication corrections

The version 1.5.0 design is retained: five illustrated part openers, four worked
visual studies, genuine 3D binary geometry, and 22 vector figures. The underlying
example data are unchanged. The retention diamond now uses readable
incomparability text, and the cube heading separates its ambient vector space
from its scalar equations. The restriction diagram states its empty admitted
leaf set. The retention plot has a dedicated float page so its qualification
is not stranded on a nearly empty page.

Literal code glyphs replace typographic quotes in executable listings. The
figure-generation command is a standalone code block with its required space.
The PowerShell extraction commands avoid the continuation character. All five
ledger questions now stay on one page. Appendix C explains that manifest
verification precedes any command that rewrites reports or rebuilds artifacts.

All final pages were rendered with a PDF renderer. Contact sheets and enlarged
changed pages were inspected. This is a visual and structural review, not a
PDF/UA certification, independent peer review, or printer color-profile audit.

## Fresh verification

| Check | Result |
|---|---:|
| Python regression tests | 128 passed; no failures, errors or skips |
| New tests relative to 1.5.0 | 17 |
| Exhaustive binary realization systems | 5,039 passed |
| Feasible binary systems | 4,359 |
| Infeasible binary systems | 680 |
| Exact certificate cross-checks | 18 passed |
| Greedy coverage instances | 100 passed |
| Retention algebra identities | 1,024 passed |
| Covariance checks | 114 passed |
| Ordered tuple encoding cases | 2,801 |
| Unchanged original mathematical environments | 127 of 131 |
| Preserved stable result groups | 33 |
| Preserved original test files | 11 |
| Unchanged formal source/configuration files | 17 |
| Unchanged inherited formal evidence files | 35 |
| Numbered vector figures | 22 |
| Final manuscript pages | 62 |
| Final LaTeX reference/layout warnings | 0 |
| PDF preflight warnings | 0 |
| PDF text outside page bounds | 0 |
| Embedded raster images in monograph | 0 |

The publication verifier checks approved source changes, the retained logical
records, diagram data, PDF captions, copied commands, and ledger pagination.
Python package installation and final manifest/ZIP checks are recorded separately
in `evidence/finalization_1.6.0/` and the delivery verification record. Historical
reports retain their original dates and are not fresh evidence for this edition.

## Failure and correction record

The preceding turn's execution service failed before edits could run. In this
turn execution recovered. The first edit script stopped at an exact-match guard
because Python interpreted a LaTeX escape in a non-raw string. It had not written
the source. Raw strings corrected that preparation error.

Two expected baseline tests reproduced the old digest ambiguity. Three additional
development tests exposed the need to reject surrogate code points in the new
JSON encoding domain. The final implementation passes all five targeted cases
and the full suite. The failure logs are preserved rather than deleted.

Initial PDF drafts revealed a stranded retention qualification and a one-line
appendix continuation. The retention example was placed on a dedicated float
page and the repeated appendix instructions were shortened. The final page check
rejects near-empty text pages and verifies the ledger list is not split.

## Remaining boundaries

No Lean compilation or kernel replay ran in this edition; the required pinned
runtime is not installed in this execution environment. The existing 17 formal
source/configuration files and 35 inherited evidence files match their baseline
hashes. That is an identity check, not a new formal verification.

This release completes the requested editorial and software correction pass.
It does not independently referee the entire monograph, prove every Python
routine for arbitrary inputs, or validate the social models empirically. The
redistribution license remains the author's decision, unchanged by this pass.
