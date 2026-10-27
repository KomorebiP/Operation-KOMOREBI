# Mathematical self-review

## Claim

A valid finite semiring matrix certificate for all source states determines a
finite original-observation test code whose equality is exactly the encoding
kernel. This gives an actual quantifier-free Mathlib definition, term-definable
code coordinates, and preservation of every translated observational query under
surjection to the actual encoded image.

## Verdict

The argument is proved as written at the exact Lean endpoints in the coverage
record, conditional only on the explicitly checked certificate equations and
standard language/library foundations. Completed execution is reported separately
in RESULTS.md. The review is a self-review, not independent refereeing.

## Dependencies and checks

1. Genuine word provenance is supplied by the inherited row trace and checked
   against actual matrix word actions, including empty words and left-to-right
   input order. It is not replaced by a test label.
2. P=WG proves the finite-code-to-encoding direction. Intertwining and output
   reconstruction prove the converse by the actual all-word theorem. There is no
   circular use of the logical certificate being constructed.
3. Local output and successor closure are derived for this code, satisfying the
   parent's concrete FiniteCodeCertificate fields.
4. The inherited standard compiler proves guarded satisfaction, including arbitrary
   binders. The new E formula is its concrete finite relation, not a renamed
   custom logic or a new predicate whose interpretation already is the answer.
5. Wrong-sort inputs are excluded by State. The Set.Definable theorem is global
   in the tagged universe; the term-code equality theorem is on state inputs.
6. Quantified reflection uses a constructed surjection to EncodedImage. The
   full target R^t can contain unreachable witnesses. A residue-four example
   proves this distinction in the actual standard logic.
7. A class formula for y assumes y belongs to EncodedImage. Its construction uses
   target tests only. Existence of a representative is used in the proof, not
   claimed as a verified computational inversion algorithm.
8. Zero observations/test lists are handled by the empty conjunction. An accepted
   zero-row certificate collapses all source states; state guards still exclude
   values. The finite suite includes zero-coordinate instances.
9. Growth witnesses prove a specific failure of an earlier test family, not
   global minimality of the final formula or optimality of the discovery order.
10. Matrix coordinate count t and observation test count l are distinct. No
    quantifier-rank or formula-length lower bound is inferred from arithmetic
    minimality. No standard first-order elementarity or QE is asserted.

## Finite experiments

The independent audit samples explicit kernel-related equal pairs as well as
random pairs, so equality checks do not mostly exercise the unequal branch.
It exhausts all state pairs in 44 small source systems, checks their value-tag
boundary, and compares quantified queries on actual image structures using a
separately implemented primitive target interpreter. The large case is checked
symbolically without enumeration. All 643 growth witnesses are tested.

These tests validate the executable path and conventions. Universal all-state,
all-word, and formula claims are proved by Lean, not by the tested ranges.

## Unchecked layers

The Python discoverer, chain-ring Smith implementation, parser, exporter and
independent checker are not verified programs. No new theorem establishes
termination of that particular discovery implementation. No new cross-domain
benchmark, training experiment, or historical priority assessment was performed.
