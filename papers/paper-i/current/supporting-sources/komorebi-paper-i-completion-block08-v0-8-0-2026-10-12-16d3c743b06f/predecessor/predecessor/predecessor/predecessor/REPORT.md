# Paper I completion: Block 04

**Result: PASS for the complete current 33-module closure and the intrinsic-primary extension.**

The missing intrinsic primary quotient has been constructed and its exact kernel proved. The full printed single-operator theorem, PSC-I-T-SINGLE-OPERATOR, is now mapped at its stated arbitrary-field, finite-dimensional scope. This is not full formalization of the expanded monograph. The original formal component and all Block 02–03 sources remain unchanged.

## Mathematical completion

For every finite-dimensional endomorphism T over any field k, let X_p be the actual subspace killed by some power of p(T). The new development proves

    mu_p(T) = dim_{k[t]/(p)} X_p / p(T)X_p
            = number of elementary-divisor summands with primary label (p),

and

    seedRank_{k[T]}(V) = max_{p monic irreducible} mu_p(T).

The maximum is proved bounded and attained, including on the zero space. Neither the dimension equality nor a primary decomposition is supplied as an input to the public operator maximum theorem. The actual decomposition existence result from Block 03 is reused.

The inclusion X_p -> V/pV has exact kernel pX_p. Its surjectivity follows from stabilization of the descending images of multiplication by p. The resulting quotient equivalence is linear over the residue ring itself and maps a class to its included class. Finite-dimensionality internally supplies the needed Artinian hypothesis.

The grouped factors are proved equivalent to the literal X_p. A separate theorem counts any supplied positive primary decomposition of X_p, not only one obtained by grouping a chosen decomposition of V. Every individual primary multiplicity is now proved presentation independent. Associated irreducibles are counted together, and absent labels contribute zero.

These are classical mathematical results integrated into Paper I's actual definitions. They are not claims of independent classical novelty. See docs/PROOF_GUIDE.md and docs/SEMANTIC_REVIEW.md for the constructions and semantic correspondence.

## Actually executed verification

| Check | Result |
|---|---:|
| Preserved predecessor manifested payloads | 678 / 678 |
| Freshly compiled production modules | 33 / 33 |
| Original + Block 02 + Block 03 + Block 04 | 20 + 4 + 4 + 5 |
| New mathematical modules / import-only root | 4 / 1 |
| Original formal-contract rows | 35 / 35 |
| Original mapped declarations resolved | 84 / 84 |
| Complete source-owned declaration audit | 1414 / 1414 |
| Compiler-owned entries in new modules | 113 |
| New public declarations | 47 |
| Production modules replayed through Lean's kernel | 33 / 33 |
| Additional boundary-test module replays | 2 / 2 |
| Mathematical boundary assertions | 51, including 17 new |
| Invalid controls rejected as intended | 15 / 15 |
| Positive foreign-namespace guard control | 1 / 1 |
| Accepted expected-outcome command checks | 110 / 110 |
| Postflight production source/object pairs | 33 / 33 |
| Exact dependency revisions checked | 9 / 9 |

New public declaration kinds are {"abbrev": 2, "def": 14, "theorem": 31}. The owned inventory includes generated helpers, private declarations, definitions and structure machinery. It is not a count of independent or novel theorems.

The only reported transitive axioms were `Classical.choice`, `Quot.sound`, `propext`. No production placeholder, custom axiom, unsafe declaration or forbidden native-decision proof shortcut passed the gate.

The verification is a fresh two-stage project build. First, the unchanged Block 03 launcher rebuilt all 28 prior modules into a new object directory and ran its complete audit. Second, the new verifier compiled all five extension modules into another initially empty directory, importing those freshly built baseline objects. Saved predecessor project objects were used for development only, not for final acceptance.

Both constituent stages were actually executed. The new combined convenience launcher was syntax-checked but was not separately used to duplicate them. Recorded accepted stage times were 2476.268 and 1016.234 seconds. These do not include recovery, development or packaging.

## Exact regressions and hypothesis checks

The new Lean suite tests p = t^2+1 over Q. Two nonlinear primary chains have intrinsic residue-field dimension two. A single squared nonlinear primary block has dimension one. It checks absent labels, associated irreducibles, explicit versus chosen presentations, zero spaces, the exact intrinsic kernel and natural behavior on quotient representatives.

A genuine counterexample establishes that the primary-to-global quotient map need not be onto without the finiteness hypothesis: for the free module Q[t] and p=t, the primary component is zero but the quotient by t is nonzero. This is a proved negative mathematical result, distinct from the deliberately ill-typed fixture files.

Four additional invalid applications are rejected: omitting the Artinian hypothesis, changing the repeated-primary intrinsic dimension from two to one, replacing the scalar-image kernel by the zero kernel, and substituting irreducibility of t for irreducibility of the zero polynomial. These do not change production theorems.

## Publication correspondence

All 108 publication records and their statement/proof source fields are unchanged. Exactly one proof-level record changes status: PSC-I-T-SINGLE-OPERATOR moves from partial to covered. The cyclic-matrix criterion receives more precise progress notes but remains partial.

The 69 proof-level records now have **17 covered, 32 partial and 20 not mapped**. This is not a completion percentage, and these records are not the same units as the original 35-row contract. All 125 distinct mapped declaration names appear in the final compiler-owned inventory. The deterministic JSON and Markdown map generator is rerun byte-identically as a packaging check.

## Failures and boundaries

The development index records 8 rejected compiler runs, 0 compiler timeouts and 2 interrupted foreground invocations without completed receipts. Rejected drafts included unused-simplification warnings, section-variable/syntax issues, a scalar-power rewrite, API names, dependent-subtype rewrites and finite subtype counts. Those drafts are retained separately from the accepted fresh run. An interactive execution attempt was also unsupported by the container. A report-writer generator initially failed Python parsing because of nested quotation delimiters; the corrected standalone assembler was syntax-checked and executed only after the accepted receipts existed. The tooling incident record retains those details. None of these unsuccessful attempts counts toward PASS.

Mathlib's authenticated pinned cache was reused, not freshly rebuilt or completely replayed. Replay used Lean's own kernel, not an independent implementation. The coverage map is a reviewed semantic correspondence, not a kernel interpretation of TeX. All new constructions are noncomputable. There is no new verified executable factorizer, normal-form algorithm or eigensolver.

The arbitrary non-diagonalizable eigenspace formula over an algebraically closed field and the scalar-extension/rational-canonical clauses of the six-way cyclic criterion remain. Nonsplit semisimple, local-module/Nakayama, expanded packet/topological and executable-algorithm obligations are still separate. Papers II–XII have not been rerun in this sweep. Publication PDFs and license-status records are unchanged.

## Handoff

The package includes the complete unchanged predecessor, new sources, tests, both fresh-stage logs and objects, source/type/axiom inventories, failed-development snapshots, the complete updated coverage map and a versioned ledger. The large portable runtime remains an external prerequisite.

No audit or compiler process remains active. Start next with the arbitrary-operator geometric-multiplicity formula, using the exact paths and proof plan in CONTINUE_HERE.md.
