# Lean guide: bounded read-only conservative proofreading

Review date: 2026-10-07. Mode: review-only, followed by checking the root
author's narrowly forced corrections. No guide, source-proof, or generator
edits were made by this reviewer. No Lean compilation or scientific replay
was performed in this pass.

## Disposition

**PASS for the hash-bound source reviewed below.** The explanatory body
accurately describes the model, certificate predicates, semantic least
bounds, sharing invariant, balanced cut, affine-output existence proof,
formal scope, and current versus archived evidence. All 115 appendix theorem
types are exact transcriptions of the archived catalog. All catalog names,
source hashes and declaration-line locators bind to the actual supplied
formal files and inventory.

The review does not turn archived elaborated types into fresh elaboration,
and does not audit all 115 proof terms adversarially. It is a conservative
source/notation/evidence check against the actual formal modules, catalog,
verifier and supplied logs. The separate core audit reconstructs the critical
cut/degree/cover arguments.

## Exact reviewed artifacts

| Artifact | SHA-256 |
|---|---|
| `manuscripts/lean.tex` | `f19fd8e595fe6de9eb9858ce317fbb1dc64d943bf48e38c9847ca9ca9d118cbe` |
| `manuscripts/lean_register.tex` | `65d2757b1cca6ceea5711e96ec5dd6345325a86c3e1b37061ca08f9374183396` |
| `manuscripts/lean_statements_utf8.txt` | `2cba1b0b09597299dc76a88513612bf8bdc5c7c2f138e1094d8af26ced3455ed` |
| `scripts/build_lean_guide.py` | `fc2fdb5fd62e5f32fb217be91af4293a5ac700b0103bda00e33ba680c05c02b8` |
| `scripts/build_lean_register.py` | `bd1d1c973db0c6b16debb519ecd241dfad918df731353e28495c4ea3826ff224` |
| Source `reference/lean-block02/declaration_catalog.json` | `f6166bd86c3e7ca1ed9fe55cc32293e3fadf56324c4e1b5e0190699b8cc90dce` |

Body and appendix have separate hash bindings. Subsequent source changes
require identifying the changed scope; this report is not an approval of
an unspecified later revision.

## Required correction and author response

One exact-name typo was found in the chapter “Certificates, semantic minima
and natural arithmetic”: `SafeDegreeLE f d` is not a source predicate. The
intended predicate is uniquely forced by its description and actual definition:
`CompleteSafeDegreeLE f d`.

The root author changed both the generator and generated body. The final
source contains the actual predicate name. This is the only mathematical-token
correction requested by this reviewer; it does not alter any theorem or proof.

The initial appendix displayed an empty field for the 25 axiom-free entries.
The root changed those labels to “none” and improved the standalone title and
metadata lines. The 115 statement strings stayed unchanged.

The final layout follow-up places each declaration in a complete unbreakable
minipage and lets module groups flow without forced page breaks. A new exact
extraction confirms that all 115 type strings and the complete UTF-8 sidecar
remain unchanged, with 115 matching minipage pairs. Body and guide-generator
hashes are also unchanged. Only appendix layout and its generator binding
were updated; no substantive re-audit was needed.

The final body also incorporates precise three-/four-wire finite ranges and
the companion reviewer's negative-test mechanism clarification. In particular,
the monomial-length test supplies a false length witness, and the affine-AND
test supplies a degree-two proof to a degree-one goal. Four-corner parity is
the separate positive semantic exclusion theorem. That distinction is correct.

## Meaning and model checks

| Check | Result |
|---|---|
| Generic C01 wire type | Correct: arbitrary `W : Type` with `DecidableEq W`, not an unstated finite-wire premise |
| Generic boundary | Correct: target equation separates both branches for each x; no extra injectivity of all logical-input encodings is assumed |
| Canonical model | Correct: `Sum (Fin n) (Sum (Fin a) Unit)` has n+a+1 wires, n varying inputs, a zero ancillas and a target |
| Restoration | Correct: all x and both initial target values; dirty internal wires and target feedback are allowed |
| Primitive legality | Correct: CNOT control differs from target; Toffoli controls and target pairwise distinct |
| C01 completeness | Correct existential coordinate detection, not XOR of all packets and not target-only detection |
| Degree representation | Correct concrete finite XOR-monomial certificate, allowing repeated variable indices; Boolean reduction cannot increase degree |
| Degree versus ANF | Correct distinction: a polynomial representation bound, no separate executable canonical normalization or free homogeneous extraction |
| Zero degree | Correct: formal degree-zero certificate; Python mathematical degree helper uses -1 for zero |
| Shared invariant | Correct: arbitrary finite lists including duplicates; products have budget t+length(L), hence coordinates t+1 |
| Initial affine premise | Correct: the general run theorem needs degree-one certificates for initial coordinates; the canonical boundary supplies them |
| Restoration versus growth | Correct: restoration is used later to identify the final target with f, rather than being needed for the degree-growth induction |
| `CompleteSafeDegreeLE` | Correct: every positive has a possibly different detecting safe function of bounded degree |
| `beta` | Correct chosen least admissible natural cover bound; existence from point indicators; no efficient detector-finding algorithm asserted |
| `AffineSafeDegreeLE` / `betaStar` | Correct universal quantification over `DegreeLE 1` functions and least common upper bound, equal to the finite maximum over affine masks |
| Noncomputability | Correct: standard classical-choice definitions are noncomputable declarations, not a claim that the finite mathematical parameters are uncomputable |
| Affine output | Correct legal NOT/CNOT gate-list existence construction, not a separately exposed executable compiler or total-gate optimum |
| Balanced cut | Correct attainable prefix count; ceiling based on Toffolis, not half the total gate-list length |
| Natural subtraction | Correct: `2 * betaStar f - 3` saturates at zero; integer reading is max(0,2 betaStar−3) |
| Formal scope | Correct: C01, maintained NCT specialization of F3, numerical C02; dual, affine input invariance, general monotone ideal and C03–C08 stay outside |
| AND fixture | Correct: inherited scratch example costs two Toffolis but direct AND2 optimum is one; generic monomial optimum is not newly formalized |

The prose phrase “degree-one function” is used in the certificate sense,
including constants: the body explicitly defines the `DegreeLE 1` predicate
and includes the constant and empty-circuit affine cases. No mask class is
silently reduced to exact algebraic degree one.

## Complete register and finite-scope checks

The reviewer independently extracted all 115 `lstlisting` blocks from the
generated appendix and compared every block directly with its corresponding
catalog `statement_utf8`. There are no missing, duplicate or altered types.
The complete UTF-8 sidecar equals the independently constructed concatenation
of the 115 IDs and original type strings. All names equal the committed
theorem inventory's name set.

For every catalog entry, the actual formal source-file SHA-256 matches its
catalog hash, and the stated declaration line contains the correct theorem
name. The catalog statement starts with the exact fully qualified name.
The final endpoint is correctly identified as L107.

| Module | Declarations |
|---|---:|
| Gates | 16 |
| CutComparison | 13 |
| Examples | 11 |
| Degree | 19 |
| MultiplicativeDegree | 12 |
| SafeDegree | 22 |
| AffineOutput | 14 |
| DegreeChecks | 8 |
| Total | 115 |

There are 40 inherited and 75 new declarations. The catalog axiom partition
matches the body's exact counts: 25 empty sets, 17 only `propext`, 3 only
`Quot.sound`, 40 both, and 30 all three including `Classical.choice`.
The ten non-ASCII characters in the types are exactly the ten glyphs covered
by the listing's literate mappings. Their renderability is a PDF check, not
a new elaboration.

The finite checker range now matches its actual enumerator: every word over
the documented 12-gate three-wire alphabet of length0..3 (1,885 words), and
every word over the documented 28-gate four-wire alphabet of length0..2
(813 words), totaling2,698. The alphabet uses one order for each symmetric
Toffoli control pair; the scope does not claim enumeration of both ordered
control-constructor spellings as distinct syntax.
All subset products of final registers yield 28,088 checks. Restored words
are 173+78=251. The 278 truth-table functions include n=0, whereas the
276 original oracle constructions start at n=1. No exhaustive circuit
optimality or universal theorem is inferred from those tests.

## Evidence and failure distinctions

The September 21 archived verification record is the source of the
115 theorem, eight module-replay and eight expected-rejection numbers.
The reviewed October 7 verification record has status FAIL, error
`[Errno 2] No such file or directory: 'lean'`, and `commands=[]`.
The body's statement that no fresh elaboration, axiom audit, kernel replay
or negative-control rejection completed is accurate.

The source verifier, pinned toolchain, allowed axiom sets and retained
development/toolchain-match reports were read directly. A text scan finds
no `sorry`, `admit` or `axiom` declarations in the maintained modules; the
only “axiom” occurrence is prose stating that restoration is not an axiom.
That scan is not promoted to an axiom dependency audit.

The historical executable-hash match does not authenticate an entire
upstream multipart toolchain distribution. The guide explicitly preserves
that limitation. It also correctly treats the bundled checker as sharing
the toolchain trust boundary, rather than an independent implementation.

## Validation and coverage limits

Validation performed: exact text/type/name/locator/hash comparisons,
module and axiom tallies, source-level predicate and proof-structure reads,
finite enumerator range inspection, and comparison with supplied archived
and failed fresh records. All passed after the forced predicate correction.

No edits were made by this reviewer. No fresh kernel check, all-science
replay, exhaustive proof audit of all 115 terms, or independent human
review is claimed. PDF compilation and final layout are the root agent's
separate validation. No unresolved mathematical, notation, or evidence
correction remains in the hash-bound body and appendix reviewed here.
