# Failure ledger — Strong Artin Lean v0.17

No failed draft or timed-out wrapper is counted as proof evidence.

## Generic-fibre development

The first `GenericFiberSurvival` draft failed for proof-engineering reasons:

- reversed arguments to `mem_powers_iff`;
- a missing localized-module instance;
- a definition requiring `noncomputable`;
- a recursive simplifier invocation;
- an injectivity equality presented in the wrong orientation.

The statements were not promoted until the corrected module compiled with warnings as errors.

## Tame pairing development

Early local-pairing drafts failed because of:

- a deprecated `push_neg` use;
- an invalid quotient extensionality invocation;
- a missing dual-basis import and incorrect theorem name.

The final modules use an explicit perfect trace-pairing equivalence and compile cleanly.

## Product-ring support development

One broad `import Mathlib` attempt exceeded the bounded compile window. A nonexistent narrow import was also tried. The final module uses only the required narrow imports. Additional failures involving `FaithfulSMul.eq_of_smul_eq_smul`, coordinate evaluation, and iterate orientation were corrected before verification.

## Split-prime quotient development

The first draft had:

- a missing dual-definition import;
- an implicit scalar-field ambiguity in the cyclic-line definition;
- an unused simplifier argument treated as an error.

All were corrected; the final module compiled.

## Functional-to-column development

The first double-dual proof route used `dualMap_surjective_of_injective` and left typeclass/inference goals unresolved. The final proof uses surjectivity of `Subspace.dualRestrict` and the finite-dimensional evaluation equivalence.

## Column quotient development

The first `ObstructionColumnQuotient` draft failed because:

- a range-membership witness was applied as if it were an argument;
- `LinearMap.sub_mem_ker_iff` was used in the wrong logical orientation;
- `Submodule.quotEquivOfEq` was under-applied;
- the quotient equivalence simplifier lacked `Submodule.quotEquivOfEq_mk`.

The corrected module proves the kernel/range identity, uniqueness modulo range, and quotient equivalence with no proof escape.

## Exact dimension development

The first `MinimalAuxiliaryColumnCount` compile hit the default heartbeat limit while elaborating an implicit `Subspace.dual_finrank_eq`. Supplying its universe/type arguments explicitly removed the elaboration blowup. The theorem then compiled without increasing the heartbeat limit.

## Automatic pipeline development

The first draft used invalid field-notation layout across a line break. The syntax was corrected; no theorem statement changed.

## Replay infrastructure

An attempted interactive streaming replay failed because the container did not support streaming execution. A first background invocation then failed because the replay script had not been created by the rejected streaming command. The script was recreated explicitly and the authoritative replay was launched from a clean output directory.

These were execution-wrapper failures, not Lean theorem failures.

## Auxiliary-column minimality development

The first draft left scalar/module parameters underdetermined in `evaluationMap`, then exposed the zero-subtype coercion instead of the intended scalar-zero goal. The final proof supplies the transverse obstruction type explicitly and rewrites the goal before expanding the augmented map. No statement was weakened.
