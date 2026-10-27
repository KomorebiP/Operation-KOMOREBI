# Independent actual-archive identity review

Scope: the actual `Komorebi_Space_Lean_Continuation_v1.12.0.zip` and its external
delivery/progress records, after packaging. Preparation does not accept a release.

The checker is maintained independently of the packaging and replay helpers. It
uses only the Python standard library and does not import, execute, or delegate a
decision to those helpers. It adapts the preceding release's independent archive
checker. The present checker author authored `CoordinateCovector.lean`; therefore
this review explicitly makes **no independent mathematical-review claim** about
that proof. The separately authored mathematical review is checked only for its
frozen identity and binding to the accepted source, full type export and run.

The checker must be frozen before packaging. Its archived and running hashes must
match `FROZEN_CHECKER.json`. Final verification must not run until the coordinator
announces that the actual ZIP and delivery records exist. The final JSON remains
outside both the frozen project and expanded release, at
`output/Komorebi_Space_Lean_Independent_Archive_Review_v1.12.0.json`. Existing
reports are never overwritten.

The final review independently checks:

1. Canonical, safe, unique ZIP paths, no file/directory collisions or symbolic
   links, ordinary members, no encrypted payloads, complete CRC reads, every
   payload SHA-256, and an exact non-self-referential manifest.
2. Actual ZIP equality with its expanded release; the pinned predecessor ZIP
   `40a5ddecb526dcb1f60c4475e3648f2b5aa906d2b4b5070f4a8b1c59db4d83d1` and expanded
   predecessor; all 5,863 predecessor files unchanged under `inherited_v1.11.0/`;
   the historical PDF unchanged; no new PDF, compiler objects or runtime payload.
3. The filtered current-project inventory, six root documents, current formal
   tree, accepted source snapshot, assembly, frozen overlay, and the two pinned
   new production-source hashes. Every inherited source/control byte outside the
   exact generated-file allowlist must be preserved; combined imports are only
   the two required additions.
4. Receipt/postflight/summary/ledger/coverage agreement, reviewed helper and
   validator identities, review-before-execution chronology, all acceptance
   evidence, final signoff, and the pinned root-reviewed packaging script.
5. An independently reconstructed complete command inventory: dependency pins,
   clean checks, every production compile, exporter, positive/negative/policy
   control, and terminal dependency checks. Arguments, order, working directory,
   strict Lean flags, logs, statuses, rejection markers and infrastructure-error
   exclusions must agree. Module, compilation, control and theorem counts are
   derived from archived source/receipt inputs rather than guessed.
6. Complete cumulative declaration and permitted-axiom inventories, all 4,982
   inherited declaration identities, every new full type, sorted/derived exports,
   and every public declaration detected from source. The source scanner includes
   `noncomputable def` and checks actual namespace separately from originating
   module. The expected sources currently contain 51 public declarations,
   including 43 explicit theorems; generated declarations are counted from export.
7. Exactly 13 complete written-result groups including WR15, no partial groups,
   and only WR10–WR12 remaining written-only; external delivery record and
   progress-file identity against this actual ZIP.

Limitations: this is not another Lean run or a rebuild/authentication of external
compiled caches. Bound runtime and compiled-object inventories are checked as
recorded evidence. Inherited declaration identity uses name, module, kind, unsafe
flag and axiom set, not proof-expression equality. Endpoint checks cannot detect
transient alterations restored before rechecking.

Preparation evidence: `preparation_001.json` and `preparation_002.json` retain
bounded synthetic checks; the latter tests the final checker revision. All 22
tests passed, including corrupt CRC, malicious paths, duplicate payloads or
manifest entries, symbolic links, file/directory collisions and omitted payloads.
These synthetic results do not constitute actual-archive acceptance.
