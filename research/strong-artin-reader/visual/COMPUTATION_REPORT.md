# Strong Artin visual computation report

Edition 1.0, 8 October 2026. Scope: 24 native vector figures, 24 PNG previews, and the exact data used by the visual guide. The finite examples illustrate the stated algebraic assertions. They do not prove Strong Artin or construct an automorphic carrier.

The final bounded run completed successfully. Its version 2 evidence manifest is `computations/atlas-final-v1.0/manifest.json`. The Mathbox validator accepted it with project root `strong_artin_set`. It records the actual argv, software versions, input hashes before and after execution, runtime, CPU affinity and cooperative thread limits, and all 52 scientific result hashes. Copies of all 48 figure assets, the data, layout checks, and reports are included with the run. The current source pins are in `SOURCE_PINS.json`.

## Computation contract

All mathematical decisions use exact integers, `Fraction` rationals, explicit finite fields, or the cyclotomic pair algebra `Q[zeta]/(zeta^2+zeta+1)`. Matplotlib uses floating coordinates only to draw the certified objects. No random sampling is used. Matrix vectorization is row major, ordered as `(11,12,21,22)`. Polynomial coefficients follow `det(TI-A) = sum (-1)^k e_k(A) T^(n-k)`.

The mathematical domains and saved values are attached individually to each figure in `data.json`. Schematic torsor alignment and research gates have no invented probabilities or quantitative success rates. The conditional theorem diagrams identify the required realization, semisimplicity, characteristic, and arithmetic application inputs in the adjacent guide text.

## Exact controls

- The three rank 3 scalar twists of `diag(1,1,zeta)` have elementary coefficient rows `(2+zeta,1+2zeta,zeta)`, `(−1+zeta,1−zeta,zeta)`, and `(−1−2zeta,−2−zeta,zeta)`. Their determinants agree and their traces separate.
- The exact local alignment sets shown above the coarse filter control share label 1. The three coarse filters have pairwise intersections and empty total intersection. They are explicitly not exact prime cyclic alignment sets.
- The order 3 group `diag(2^j,4^j)` over `F7` has trace alphabet `{2,6}` and injective trace words `(2,6)`, `(6,6)`, `(6,2)`. It satisfies the basis bound 4 and rank bound 16.
- Cyclotomic reduction at a place above 3 collapses all three twist rows to `(0,0,1)`. Reduction with `zeta -> 2` above 7 gives three distinct rows.
- The complete 78 multisets of two roots chosen from 12 are enumerated. The finite alphabet polynomial reductions at 2, 3, 5, and 7 are exact.
- The `C2` pointwise matrix assignment over `F7` fails the multiplication relation although its roots belong to a finite cyclotomic set. It is labeled an algebraic model, not automorphic data.
- Full matrix cyclic cohomology over `F3` gives dimension 0 for `C2` and dimension 2 for `C6` in the stated conjugation action.
- The square zero correction over `Z/4`, the moving relation modulo 8, and the augmented equation control modulo 4 are checked directly. The original scalar equation in the augmented control has no root.
- Four exact rational Newton corrections for `x^2=6` give 5 adic error valuations `1,2,4,8,16`. The exact residual identity is asserted at every step.
- For the unipotent square map, the full derivative matrices satisfy `BD=DB=4I`. The passing target has `B delta=(0,0,32,0)`. The failing target has `(0,16,0,0)`. The certificate exponent is 2, greater than the scalar degree valuation 1.
- Every odd root of `x^2=1` modulo 2, 4, 8, and 16, together with every reduction edge, is enumerated. The node 3 modulo 8 has no successor modulo 16.

The independent reviewer reconstructed all 20 numeric models and the complete 24 figure inventory without importing this generator. The parent review includes that separate evidence.

## Layout verification and resolved failures

Every figure uses a 7.5 by 5 inch canvas and text at least 14 points. The generator checks actual renderer text bounds against both the canvas and every containing card. The complete final run passes both checks. A separate native visual reviewer inspected all 24 PNGs individually. The parent checks the assembled PDFs.

Earlier native visual inspection found crowded headers, card overflow, footer clearance, literal exponent carets, and short arrow gaps. They were corrected through explicit line breaks, centered headers, card height changes, superscripts, and wider arrow gaps. The first strict card containment run stopped at a crowded introductory card. The next diagnostic run identified 14 additional card containment failures. Those were fixed, and the final run passed every card. No mathematical assertion or Matplotlib API execution failed.

The initial draft incorrectly described the trivial degree one character as a cuspidality exception. Review corrected it to the familiar pole of its L function. The root alphabet comparison scope now excludes one fixed exceptional set. The l adic rigidity spread states the finite coefficient extension and finite ramification hypotheses. The final route diagram says weak attachment and explicitly retains the remaining local checks. Final report self review also caught a transposition of the two rotated second coefficients in this prose report and corrected it. Generated data and figures already had their correct order.

## Limits

The computations are finite examples and implementation checks. The diagrams do not identify the intended arithmetic deformation functor, prove a Selmer or cochain comparison, establish correction image exactness in that arithmetic problem, construct a residual or l adic realization, or replay a Lean release. None of their counts certify a universal theorem.
