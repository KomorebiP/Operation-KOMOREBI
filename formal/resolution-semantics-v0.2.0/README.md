# Resolution Semantics: Lean companion 0.2.0

This separate companion compiles the 15 theorem statements from the original
two-valued scaffold and formalizes **Theorem 7.3, the two-world symmetry
obstruction**, including its stronger additive assertion. Lean 4.24.0 accepts
34 theorem declarations in total, including supporting lemmas and assumption
controls. This count is not 34 manuscript theorems.

The [original 0.1.0 edition](../../research/resolution-semantics/README.md)
and its dated evidence are preserved. The original scaffold fails before
compilation because its module documentation precedes `import Std`. Moving
the import exposes three additional rewrite failures. `KRSCore.lean` fixes
these by spelling out the pointwise goals; all 15 theorem statements remain
unchanged. [PROVENANCE.json](PROVENANCE.json) identifies the source bytes and
the manuscript statement.

## Reproduce

With Python 3.10 or later and the pinned Lean toolchain installed, run from
this directory:

```text
lake build
python replay.py --lean lean --output ../../verification/current/resolution-semantics-new-run
```

The output directory must not already exist. Use a fresh name for another run.
The package depends only on Lean's bundled `Std`; it has no mathlib dependency.
The replay builds fresh proof objects in an isolated directory, treats warnings
as errors, inspects every theorem's axiom inventory, and checks three expected
rejections. Compiler/import/setup failures do not satisfy those controls.

The [recorded Windows replay](../../verification/resolution-semantics/windows-2026-10-30-run5/receipt.json)
passed all 34 declarations and all three rejection controls. Both main
obstruction theorems have empty axiom inventories. One inherited helper,
`KRS.defect_eq_false_iff`, uses `propext`; the other 33 declarations have empty
inventories. No theorem depends on `sorryAx` or a custom axiom.

## Formal correspondence

| Manuscript scope | Formal declarations | Boundary |
|---|---|---|
| Section 4, defect identities in the two-valued case | `KRS.defect_*`, `KRS.triangle_telescope` | Boolean truth values only; no arbitrary Boolean algebras or categorical transport. |
| Section 5, invariants | `KRS.Invariant`, `KRS.invariant_*` | Constant, complement, xor and meet closure, and weakening the edge relation. No quotient or diagram-limit theorem. |
| Theorem 7.3, additive assertion | `KRS.TwoWorld.no_swap_equivariant_additive_retraction` | Arbitrary additive retractions from `Bool × Bool` onto the diagonal, with explicit swap equivariance. |
| Theorem 7.3, Boolean assertion | `KRS.TwoWorld.no_swap_equivariant_boolean_retraction` | Boolean-ring retractions preserve xor, meet and one; complement preservation is also proved. |
| Assumption controls | `leftProjection`, `rightProjection`, `lowerSummary`, identity and `zeroSummary` lemmas | Demonstrate what becomes possible when symmetry, additivity, diagonal image or retraction is omitted. |

`TruthPair` represents the Boolean ring over the two-element field.
`AdditiveRetraction` records a function into that ambient ring, requires its
image to be diagonal, requires preservation of xor, and requires every
diagonal value to be fixed. This is an explicit representation of a retraction
whose codomain is the diagonal subalgebra. Idempotence alone is insufficient.

## Proof and self-review

**Verdict: proved as written**, for Theorem 7.3 with the encoding above.
This is a self-review of the manuscript correspondence, together with Lean
kernel checking; it is not an independent scientific review.

For the two coordinate vectors `e1` and `e2`, equivariance and diagonal range
give `P(e1) = P(e2)`. Additivity and xor cancellation then give
`P(1,1) = (0,0)`, contradicting the retraction law `P(1,1) = (1,1)`.
The Boolean assertion follows because its retraction is additive.
The dependency chain uses only the definitions, pair equality, Bool case
analysis and equality substitution. No external mathematical theorem is used.

| Audit obligation | Result |
|---|---|
| Ambient ring, action and fixed subalgebra match Theorem 7.3 | Passed: coordinatewise xor/meet, coordinate swap, diagonal image. |
| Quantification covers arbitrary candidate retractions | Passed: the theorem accepts an arbitrary structure satisfying the laws. |
| The contradiction uses all needed hypotheses | Passed, with compiled counterexamples when each is dropped. |
| Boolean conclusion follows without an extra mathematical assumption | Passed: the Boolean-ring structure explicitly extends the additive retraction. |
| Axiom and placeholder audit | Passed for all 34 declarations; both main theorems are axiom-free. |
| Wider paper, forcing applications and arbitrary Boolean algebras | Out of scope. |

The first replay attempt failed while creating a Windows sandbox temporary
directory, before compiling the companion. Its
[failure receipt](../../verification/resolution-semantics/windows-2026-10-30-run1/receipt.json)
is retained separately. The successful runner now creates its temporary build
inside its requested output directory. Baseline source failures and setup
failures are not successful proof-rejection controls.

## Remaining work

The general Boolean-algebra-valued transport laws, product telescope, finite
graph integration, selector classification, envelopes, weighted projections,
stability and forcing applications remain outside this companion. The next
useful contract is a faithful formalization of the finite graph integration
theorem or the typed Boolean-algebra-valued transport differential.

[Reader guide](../../docs/components/RESOLUTION_SEMANTICS_LEAN.md) ·
[Original proof boundary](../../research/resolution-semantics/PROOF_BOUNDARY.md)
