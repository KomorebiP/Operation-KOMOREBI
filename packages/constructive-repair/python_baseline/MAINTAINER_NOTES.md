# Reviewer instructions and audit taxonomy

This package intentionally separates *claims*, *sources*, *proofs*, *algorithms*, and *test evidence*.

## Evidence classes

- **Ordinary proof:** elementary linear/categorical identities with written proofs in `TECHNICAL_AUDIT.md`; independently assessable without running Python.
- **Exact computation:** finite checks in `audit_trace.txt` and 3,307 records in `case_records.jsonl`. These do not prove universal theorems by themselves.
- **Independent computation:** brute-force coefficient enumeration instead of Gaussian elimination, and optional third-party SymPy calculations of rank, Stirling sums, and Euler values.
- **Counterexample:** a strict mathematical failure of a stronger claim (e.g., first-order linear obstruction does not decide nonlinear solvability).
- **Inherited source:** existing Paper III, IX, and XI constructions that this audit **tests** rather than re-proves from scratch.
- **Unresolved:** claims for unrestricted nonlinear, arithmetic, or automorphic realizations, and any universal automated discovery ability.

## What reviewers should try to break

1. Replace a prime field with a composite modulus; the code should reject its treatment as a field.
2. Insert a rational coefficient with nonunit denominator mod `p`; the code should reject conversion.
3. Insert a float; no exact-arithmetic certificate should accept it.
4. Construct a small finite menu where target lies in the span of two candidates but neither individually spans it.
5. Force the missing direction to violate a conserved linear functional and ensure it is rejected.
6. Coarsen a nonzero obstruction to zero and verify the target's zero result is not promoted to a source repair.
7. Change one edge transport in a graph while keeping it invertible; the fundamental cycle must detect mismatch.
8. Use a nonlinear residual whose derivative vanishes but which has an exact nearby root; ensure linear no-go is scoped correctly.
9. Claim one extra power of `p` after truncation and check `E_2 - S_2(7) = -98` defeats the claim.
10. Remove the root-filter condition `p ∤ m` and see that the normalized projector need not be defined.

## Audit independence limits

The deterministic random checks are not independent of the solver's mathematical representation: both were devised in this evaluation. The finite-field coefficient enumerator is algorithmically independent of Gaussian elimination, and optional SymPy cross-checks use separate implementations. There is no outside human referee, and none is claimed.

## Integrating with Operation Komorebi

Do not merge this into the stable Komorebi Python library without a separate API compatibility and provenance audit. Avoid naming this experimental module as a canonical pre-existing theorem of Realization Calculus. It is a specific *certificate-producing arrangement* of largely existing algebraic facts. Reuse source theorems where appropriate and preserve the distinction between a finite typed certificate and an actual arithmetic realization witness.
