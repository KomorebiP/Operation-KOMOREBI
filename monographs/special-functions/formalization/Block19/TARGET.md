# SF-LEAN-B19 target

Base checkpoint: SF-LEAN-B18, source SHA-256
f959bb0778ee1e2ed25577e1099775a5f9c03f1c6def7e55b1c95e430bed18ab,
on repository base f49e00d6088bbc8dca4f8a3a70b232db1eea085b.

Target: bind the actual pinned evaluator and its callees to an imperative
translation, then prove that every terminating translated execution refines
certifiedEvaluationSpec, including derivative mutation, reverse fold, exact
dictionary contents and modeled error propagation. Compose normal-return
refinement with both actual-function enclosures and the complex disk error.

The trust boundary must name Python parsing/translation and exact primitives.
This does not aim to verify CPython, Fraction or the host hardware. It must
not assume the desired loop invariants or the final dictionary correspondence.
Input conversion and arbitrary custom object behavior must be explicit in the
contract, not silently modeled by an invalid-input tag.

Routes considered:

1. A general Python interpreter in Lean. The source grammar probe exposes
   comprehensions, mutation, calls, exceptions and dictionary literals; a
   whole-language implementation adds much more than this target needs.
   Deferred in favor of a closed, source-checked supported fragment.
2. Checked source translation plus imperative refinement. Main discriminators:
   shared old-array products, actual list order and resource-guard placement.
   This is the active route. Source mutations must break the binding check.
3. Per-return certificate validation. This could certify individual results
   with a fail-closed wrapper, but would not prove the original evaluator's
   source relation. Retained as a fallback, not counted as this target's proof.

A proof of only the typed result, matching formulas or more finite samples
would be partial progress. A source-bound imperative refinement theorem with
an explicit primitive/parser trust boundary completes the stated target.
Full unconditional verification of all Python runtimes is outside this target.
