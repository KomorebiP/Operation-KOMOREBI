# SF-LEAN-B18: typed certified-evaluation results

The typed evaluation-result specification now connects the proved finite
arrays and guarded majorant to the complete seven-field result. Every
successful specification return preserves `x`, `last_index`, `outer_radius`,
`majorant`, `tail_bound`, `U` and `V`, encloses the actual canonical real
components, and bounds the Taylor error throughout the complex disk `|z| <= x`.

The new source is [CoupledEvaluationResult.lean](../../lean/CoupledEvaluationResult.lean).
Its 17 theorem declarations bring the recorded scope to 482 names, including
39 inherited finite-core names. This is not a count of independent discoveries
or a percentage of the monograph.

The result retains `N+1` ordinary odd coefficients for `last_index=N` and
uses first omitted degree `2*N+3`. The specification uses the actual source
defaults, 20 majorant steps and 2,000,000 bits. It keeps errors separate from
successful results and proves that the default outer radius `max(1,2*x)`
exceeds `x`. Both endpoints share the same tail but use their own component
polynomials. The success premise is essential: the unchecked result
constructor is not itself a certificate.

## Verification and provenance

* Fresh compilation, all 17 theorem axiom audits and same-kernel replay pass.
  Only `propext`, `Classical.choice` and `Quot.sound` occur in the axiom audit.
* All 19 focused formal replay steps pass, including five expected
  rejection controls and one positive fixture. The controls reject removal of
  the success premise, exponent 5 at `N=0`, zero retained coefficients at
  `N=0`, a false origin-radius bypass, and a placeholder proof.
* Seventeen unchanged coupled dependency modules are reused from the successful
  Block17 receipt after checking source, compiler/checker and compiled-object
  hashes. Their 426 theorem names and the 39-name finite core are inherited
  evidence. Mathlib is cached, not freshly rebuilt. This is not a fresh replay
  of the entire dependency stack or an independent kernel check.
* Actual Python checks pass on 240 explicitly enumerated rational grid cases,
  plus the default `N=24`, manuscript `N=30` and named boundary/error cases:
  507 checks in total. The separate oracle uses ordinary Taylor recurrence
  and a recursive majorant, avoiding derivative binomials/factorials and the
  source's mutable ladder. It is not extracted Lean code.
* Python 3.12.14 and Lean 4.34.0-rc2 are recorded, with Mathlib revision
  `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Exact source and output hashes,
  commands, platform and timings are retained in the linked receipts.

The final formal evidence is [evidence/receipt.json](evidence/receipt.json).
The bounded runtime evidence is
[python-check-003/manifest.json](python-check-003/manifest.json), with
`run.status=completed`; its manifest was validated against current input hashes.
The exact finite population and non-claims are in
[computation-contract.json](computation-contract.json).

The first full-stack attempt stopped at an unchanged module with a cached
Mathlib file-read error; its failed receipt and log are preserved under
`diagnostics/` and are not acceptance evidence. The first Python audit had an
incorrect test expectation about step exhaustion at outer radius 1; its failed
record is retained. `python-check-002` passed an earlier checker revision;
`python-check-003` is the evidence for the final checker, adding default and
manuscript examples. Development compiles remain outside the release.

## Exact boundary

The Lean theorem concerns `certifiedEvaluationSpec`. A conditional manual
source correspondence argument is recorded in
[SOURCE_CORRESPONDENCE.md](SOURCE_CORRESPONDENCE.md), with explicit assumptions
about Python execution, Fraction, integers, stdlib operations, containers,
dictionary construction and exceptions. The finite checks do not close that
universal runtime refinement gap.

One useful distinction is now explicit: `x=0` defaults to outer radius 1 and
still calls the majorant. Strict contractions reach the small seed in one
ladder step from 1. At `x=1`, default outer radius 2 and scales `999/1000`,
the fixed 20-step budget is exhausted. No error becomes a weaker certificate.

The work is local and unpublished, based on repository commit
`f49e00d6088bbc8dca4f8a3a70b232db1eea085b`. The existing calculator,
manuscript, prior blocks and historical parent guidance are unchanged.
Review is author self-review; see [SELF_REVIEW.md](SELF_REVIEW.md).

## Reproduce

From `monographs/special-functions/`, use a fresh output path:

```text
python tools/check_evaluation_result.py --output NEW_RESULT.json
python tools/verify_coupled_evaluation_result.py --toolchain KIT --mathlib MATHLIB --work NEW_EXTERNAL_DIRECTORY --git GIT --dependency-build BLOCK17_BUILD --dependency-receipt formalization/Block18/evidence/inherited-block17-receipt.json
```

The inherited build must contain the exact objects bound by that receipt.
Omit the two dependency options for a full fresh coupled-module replay.
No dependency download is performed by either checker. The exact bounded-run
argv is also recorded in the runtime manifest.

Next: mechanize the pinned Python source-to-model relation, starting with the
array-loop invariant and checked ladder state, then dictionary and exception
semantics. Other J degree/denominator/symmetry claims, ancillary F/H, Appendix I
and broader A-E remain as recorded in Block17. Ordinary type convergence stays
conditional and G.2 retains its nonzero-defect guard.
