# Failure and verification boundaries

No failed or interrupted invocation is counted as a successful compilation.
Exact attempted sources and compiler output remain in the audit directories.

1. A streaming container execution request was unavailable. Runtime assembly and
   extraction completed through a recorded bounded ordinary process instead.
2. Initial scalar drafts had absolute-value token spacing, an overbroad simplifier
   rewrite, and argument-side/type elaboration issues. Explicit inequalities and
   small normalizations fixed them. One draft reached Lean's deterministic
   heartbeat limit; this is not a mathematical counterexample.
3. Several automatically inherited section typeclass assumptions were unused.
   They were removed with precise omission declarations. Warnings stayed errors.
4. The candidate-return proof needed explicit reduction of its local let binding.
   This was fixed without assuming candidate validity.
5. One posterior-wrapper invocation was interrupted by the outer execution limit.
   Its draft log includes deterministic elaboration limits and has no completion
   receipt. Explicit candidate arguments and a proved gain-projection identity
   avoided expensive definitional unfolding; the final module passed alone.
6. Generated examples initially required explicit rational-to-real normalization
   and a clearer Boolean branch proof. A legacy conditional lemma name was also
   deprecated in the pinned runtime; the final exporter uses its supported name.
7. A boundary test needed its enclosure predicate unfolded before kernel decision.
8. The inventory generator initially counted a word in a documentation comment as
   a theorem name. Anchoring declarations to Lean declaration lines fixed this;
   an attempted audit before that fix had no generated source and did not run Lean.
9. The first combined axiom-audit invocation was interrupted before its receipt.
   Its source also used an unsupported pretty-print option. A separately recorded
   run exposed that option error, it was removed, and the final full audit passed.
10. The predecessor's inherited prefix in MODULE_ORDER.json was not a usable
    topological build order. This release computes and validates its order from
    actual imports, without changing any retained theorem source.

Completed failed compiler checks, incomplete snapshots, final receipts, and
negative-control rejections are distinguished in FINAL_VERIFICATION_RECEIPT.json.
The latest full audit covers every active declaration and checks current source,
compiled-output and dependency hashes. The 42 active inherited sources were all
freshly rebuilt; unrelated historical proof chains were not.

The external Mathbox manifest validator executable was not found in the accessible
skill filesystem and was not run. The retrieved manifest schema was used, and the
packaged source/receipt/hash/axiom checker was run successfully. No external-validator
success is claimed.

This release does not model IEEE-754 hardware, bounded integer range, uncertain
physical inputs, arbitrary machine rounding routines, or convergence of a rounded
Richardson solver. A finite precision schedule can return NOT_CERTIFIED honestly.

The first packaging helper replaced a dotted directory suffix rather than appending
.zip, shortening the focused archive filename. The helper was corrected and both
archives and all internal manifests were regenerated and checked. No proof source
changed in that packaging correction.
