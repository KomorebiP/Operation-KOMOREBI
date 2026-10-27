# Progress record: visual atlas worked proofs v4

Date: 2026-10-20
Predecessor: Komorebi Space Visual Atlas v3.

## Completed

- Read the actual v3 renderer and recovered its precise rational Fourier model.
- Matched all plotted seed modes, details, cutoffs and the altered-view experiment.
- Wrote full mathematical proofs and explicit intermediate calculations in a
  12-page companion. Kept the original visual plates unchanged.
- Added explicit coherent/defect coordinates for the entire finite raw family.
- Derived the protected repair and the distinct nearest unprotected repair.
- Derived concrete coordinates for the protected obstruction quotient.
- Explained why internally coherent partial data always extend in this particular
  split finite chain, and supplied a separate branching model with an obstruction.
- Proved the bounded-energy criterion for the infinite Hilbert realization and
  supplied a counterexample to coherence without bounded energy.
- Replayed 8,969 original exact checks and passed 3,695 added exact checks.
- Compiled the proof PDF, removed a line overflow and sparse spill pages,
  rendered all 12 final pages, and visually reviewed the result.

## Execution issue and resolution

The first visible verification run reached report export but encountered a
PermissionError: the directory created by the container was not writable from
that Python session. Directory permissions were corrected. The complete verifier
was then rerun successfully and generated both JSON reports. The delivered PASS
record belongs to that successful rerun, not to the failed export attempt.

## Verification boundary

- Written proofs: complete for the explicitly stated finite and infinite results.
- Exact Python checks: passed for the finite identities and worked quantities.
- Original rendered graphics: retained from v3, not reinterpreted as entire spaces.
- Lean compilation: not performed for this companion.
- Historical novelty: not claimed for the Fourier construction or its standard
  Hilbert-space ingredients.
- Broader Komorebi monograph formalization: not audited by this task.

## Next restart point

The next optional formalization task is to encode the typed finite tower, the
right inverse S and the coherent projection C in Lean, then formalize the
protected quotient normal form. The infinite Hilbert theorem has a written proof
but no new Lean certificate in this package. There are no deferred proof steps
inside the manuscript's stated results.
