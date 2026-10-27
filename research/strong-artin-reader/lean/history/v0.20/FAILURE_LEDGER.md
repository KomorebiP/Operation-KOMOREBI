# Failure ledger — Strong Artin Lean v0.20

No failed attempt below is counted as proof evidence.

## Portable runtime restoration

The first attempt to launch the large assembly as an interactive streaming process failed because streaming execution was not enabled.  The seven verified archive parts were then assembled synchronously.  The combined SHA-256 matched the supplied manifest, and the runtime extracted successfully.

A broad portable-kit self-verification later exceeded its wrapper after passing the initial runtime and dependency checks.  It was not used as release evidence.  The exact pinned runtime was instead used for fresh compilation of the relevant source closure.

## Scalar filtration API

Initial field-notation calls such as `h.mul_right` failed because `PowDivisible` unfolds to an existential proposition and Lean did not locate the extension theorem.  The API was renamed to explicit functions such as `powDivisible_mul_right` and recompiled.

Several first drafts also triggered warnings-as-errors for unnecessary tactic sequencing and unused simp arguments.  Those proofs were rewritten explicitly.

## Polynomial product remainder

The first product proof had an associativity mismatch between the target sum and the constructed divisibility proof.  The exact algebraic identity was isolated, the target rewritten by that identity, and the remaining association normalized explicitly.

## Matrix/linear-map bridge

An initial implementation used the inverse of `LinearMap.toMatrix` and caused typeclass inference failures in composition and identity lemmas.  It was replaced by Mathlib's explicit `Matrix.toLin`, using `Matrix.toLin_mul`, `Matrix.toLin_one`, and the `toMatrix`/`toLin` inverse theorems.

An initial matrix distributivity proof using `noncomm_ring` did not normalize the rectangular matrix expression.  It was replaced by an entrywise finite-sum proof.

## Quotient-type integrated theorem

A direct capstone specialized to the type `R ⧸ Ideal.span {pi}` with a `Field` instance repeatedly exceeded the bounded elaboration wrapper.  It was not claimed as checked.  The theorem was reformulated more generally with a residue-field homomorphism

```text
q : R →+* k,
Surjective q,
ker q = (pi),
```

which is mathematically cleaner, avoids quotient-type elaboration blowup, and compiled successfully.  A separate quotient-ring right-inverse lifting theorem remains checked without the overloaded integrated field instance.
