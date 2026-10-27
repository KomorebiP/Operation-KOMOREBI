# Collatz author notes

Author and release pseudonym: Komorebi P.
Edition prepared 8 October 2026.

Expanded reader edition: v1.1. The main body contains approximately 9,000 whitespace words. The separate visual guide is part of the release, rather than being replaced by the four figures embedded in the monograph.

## Substantive reader expansion

The expanded edition preserves every theorem statement from v1.0. It adds a reader route, a derivation of the transported offset, exact ordered-word progressions for (1,3) and (3,1), the missing endpoint-bit example at n=3, and both arithmetic density normalizations. It explains affine fixed points and checks the (2,2) equality case at source 1.

A new finite prefix from n=165 ends at167 after17 steps despite a contracting homogeneous coefficient. Its exact word, cumulative depth, offset, and gap are displayed. The text explicitly states that165 already descends to31 at its first step. It is a warning against a coefficient-only endpoint test, not a failure orbit or a least-source counterexample.

The progression151+8192s is worked through all three exact odd steps, ending at1+54s, with valuations1,1,10. The source and exit slope differences prove exact first descent for every integer s>=0. A short separate certificate55→83→125→47 connects the exit at s=1 to the verified27 orbit.

The bounded-deficit proof now has a slower explanation of each gate. It derives the local-word bound from the ratio of cumulative coefficients, counts positive words by separators, records W_ell as an exact binomial coefficient, and writes the final contradiction as a finite inequality. Its D=3 example chooses ell=9 and yields a bound below0.868 for the relevant density-height coefficient.

The appendix retains all42 odd states from27 to1, with exact valuations, offsets, shortcut depth, and classical clock. Its first descent clocks are37,59,96. Its first arrival at1 clocks are41,70,111. A reader glossary and dependency account identify which results use the global noncrossing hypothesis and which require eventual bounded deficit.

## Mathematical scope

The monograph does not prove Collatz. It gives complete written proofs of the finite affine law, exact valuation cylinders, composition, descent criterion, strong induction bridge, fixed horizon obstruction, compressed run exits, unbounded delayed terminating seeds, arithmetic progression lifts, and exclusion of eventually bounded deficit under permanent coefficient noncrossing.

The proof of the saved bounded deficit conclusion is reconstructed directly with valuation cylinders. Its exact generating weight gives the decay factor 65536/84375. This is a written monograph proof. It is not a fresh Lean formalization or replay of the historical shortcut-weight proof.

Permanent coefficient noncrossing means 2^S_r <= 3^r at every accelerated time. It must never be replaced by absence of actual descent. Actual descent requires (2^S_r - 3^r)n > C_r.

## Formal provenance

Historical compilation and axiom audit assertions are attributed to the specific saved v0.19 audit and Proof Atlas v0.17 boundary. No fresh Lean compilation was performed while preparing this monograph.

Selected readable files are retained under evidence with returned metadata. CollatzDeepResidueCertificate.lean was returned through line 1000 of 1867. The displayed 1087 modulo 4096 proof is complete within that excerpt. The unread tail is not represented as newly inspected.

No archive materialization was attempted for this Collatz writing task. There is no Collatz archive access failure to report.

## Finite computations

The orbit of 27, exact first accelerated descent at time 37, cumulative shortcut depth 59, and figure data belong to the exact finite computation layer for this edition. Historical T^59(27)=23 is separately attributed to the saved formal audit.

The partial residue count 1804/2048 and the 244 residual classes are saved finite computation evidence. The supplied rules have uniform descent proofs, while the enumeration is not presented as a Lean enumeration theorem. No progress percentage for Collatz is inferred.

## Remaining obligations

1. Force actual descent below the original source after some coefficient crossing, or supply a different universal descent theorem.
2. Exclude permanent coefficient noncrossing with unbounded deficit. The bounded strip height argument does not automatically extend to that branch.
3. Prove successful certificate production for every source if pursuing an adaptive certificate system.

The global conjecture, half contraction classification, arbitrary exit termination, and complete residue cover remain open in the presented project sources.

## Review and editorial record

An independent review confirmed the elementary cylinder and no-cross packing proof chain before the final manuscript audit. The initial fixed point sentence was corrected because the real fixed point and its integer floor can coincide. No theorem or proof was changed by that prose correction.

The tree caption maps diagram labels r1 and r2 to a0 and a1. The manuscript uses A for odd acceleration and T for the shortcut map.

Root owns final PDF compilation and visual page inspection. Its audit/layout results supersede the preliminary source-only proofreading record when the full release is assembled.

## Expansion review and execution limits

The independent v1.1 reviewer checked the ordered-word and admissibility examples, the165 prefix, the151 progression, all42 rows of the27 appendix, the finite word count, the finite packing inequality, and the D=3 coefficient. No defect was found in that mathematical pass. The final source hash is recorded in PROOFREADING_VALIDATION.json and in the assembled review report.

One temporary ad hoc exact-integer check initially failed with a Python IndentationError. The extra indentation was removed and the check reran successfully. That failure produced no artifact or mathematical result and did not affect the published source. No unresolved computation failure remains in this expansion task.
