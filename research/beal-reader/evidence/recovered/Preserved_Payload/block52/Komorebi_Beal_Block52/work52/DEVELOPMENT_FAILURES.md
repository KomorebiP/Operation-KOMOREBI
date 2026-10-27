# Development failures and rejected implications

## 1. Incorrect representative-level equation filter: IMPLEMENTATION BUG

The first exploratory program computed a Frobenius polynomial once per
weighted isomorphism orbit, and incorrectly retained the whole orbit based
on whether its representative satisfied the seventh-power residue condition.
Although curves are isomorphic under (A,B)->(u^5A,u^3B), their equation
right-hand sides scale by u^15. That multiplier need not be a seventh power.

At29, (A,B)=(0,1), u=2 gives right-hand sides1 and27 respectively: the first
is a seventh power and the second is not. The faulty whole-orbit filter
returned140 pairs rather than116, with120 false positives and96 omissions.
At43 its280 returned pairs included240 false positives and missed218 of the
258 admissible pairs. At71 it returned518, with444 false positives and636
omissions. These are invalid search results, not mathematical counterexamples.

The failed exploratory source is retained as
`verification/exploration_v1_incorrect_orbit_filter.py.txt`. Its old outputs
were superseded, not relabelled as valid evidence. The corrected program
filters each member, checks set equality against direct enumeration, and
uses the mistake as an executable negative control. A separate implementation
then counts every one of the1240 admissible pairs without using orbits.

No arithmetic conclusion in this release uses the faulty outputs. The
prime29 depth theorem also has a separate search-free Weil-bound proof.

## 2. Repeated roots alone do not prove scalar Frobenius: REJECTED SHORTCUT

The characteristic polynomial (T+13)^2 does not force an arbitrary matrix
to equal-13I: a nonzero upper Jordan entry survives. We explicitly use the
classical reducedness/semisimplicity of finite-field abelian Frobenius to
pass from (T^2-13)^2 to pi^2=13. A Jordan negative control is retained.

## 3. Determinant divisibility at depth one: FALSE EXTENSION

The norm-divisibility lemma requires n>=2. At n1, [[1,1],[7,1]] gives norm49
rather than a multiple of2401. The ordinary n1 branch is not eliminated.

## 4. Arithmetic restrictions are not global solutions or contradictions

Good-reduction sieves do not cover q|C. Primitive bad residues(-1,1,0)
remain at each tested q. Nonempty coefficient directions are not geometric
realizations. Nonzero alpha at a bad place does not force beta ramification.
The old ray family is excluded only when13 is good;13|C remains open.

## 5. Minor execution/retrieval errors, recovered

One ad-hoc symbol probe failed before execution because `else2` was typed
without a separating space. It was corrected and rerun successfully before
its arithmetic was used. This was a syntax error, not a mathematical failure.
One lookup for a historical GPcode file used a nonexistent path. It supplied
no input to the new proof or computation; the documented predecessor scripts
and source records were used instead.
A web PDF screenshot request using a raw URL failed content-type resolution;
it succeeded when retried with the opened PDF reference. The relevant Milne
pages were then visually checked. Neither error affected the final data.

## 6. Review and inherited limitations

The independent point-count code is an independent algorithm written in this
same session. There was no fresh human or second-agent proof review.
Block50's recorded extension-geometry review ended with an availability/
usage-limit failure. Block51's later self-review is preserved as self-review.
This block does not reclassify either historical event.

No new Lean compilation was attempted and no certificate is claimed. No new
run timed out. Any future timeout must be reported as inconclusive, not pass,
UNSAT, or an empty arithmetic possibility set.
