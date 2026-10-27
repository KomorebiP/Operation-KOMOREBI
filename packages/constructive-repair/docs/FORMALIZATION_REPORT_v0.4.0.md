# Constructive Repair v0.4.0 — costed rational menus and rejection covers

Author: Komorebi P.  
Date: 19 October 2026

## Completed result

The costed rational-menu path is operational. A Python producer supplies exact coefficient matrices and separating blocks. Lean checks either an optimal admissible menu or rejection of the entire declared admissible family. No rational coefficient space is enumerated. Search currently enumerates candidate subsets, with a maximum of eight candidates.

The 23 prior source modules are byte-for-byte unchanged. The combined fresh run compiles and individually replays 37 modules and audits all 378 named theorem declarations. The 151 additional declarations comprise seven general cover/interface theorems and 144 concrete input, certificate, and rejection statements. These counts describe coverage, not novelty. The elementary linear-algebra and finite-optimization arguments are classical.

## Mathematical contract

Original input consists of D, E, R over Q, a finite admissibility table of subsets of the candidate columns, and nonnegative integer costs on those columns. For a selected set S, the actual equation is

    D U + masked(E,S) W = -R.

The mask retains the original q-column indexing. Unselected coefficient rows have no effect. Selected directions are charged regardless of whether a particular witness gives them zero coefficients.

A separating block (B,Y) satisfies

    Y D = 0,   Y masked(E,B) = 0,   Y R != 0.

The new `separates_subset` theorem proves that such a row excludes every subset of B. B itself need not be admissible. This is useful because a single checked block can reject many relevant alternatives without requiring a separate matrix witness for each one.

`checkCoveredOptimal_sound` proves admissibility, the original coefficient equations, and minimum cost among all admissible feasible selections. Its premises require that every strictly cheaper admissible selection be covered by a valid block. The finite coverage predicate is evaluated over the full candidate-subset universe, not an enumeration supplied by the producer as a completeness claim.

`checkCoveredNoRepair_sound` proves infeasibility of every admitted selection when all such selections are covered. An empty admissibility table yields an explicitly vacuous rejection. No result excludes new directions outside the declared menu.

## Executable producer and verifier

`python/rational_menu.py` uses exact Fraction row reduction, retaining the left transformation matrix. Inconsistent residual rows supply explicit separating functionals. Consistent pivot equations supply rational coefficients. Every proposed identity is rechecked independently of the elimination loop.

The producer evaluates all subsets, chooses an admitted feasible set of minimum cost, and uses maximal infeasible subsets as possible separation blocks. A deterministic greedy cover compresses the required rejection evidence. Minimum evidence size and polynomial-time search are not claimed.

The certified command is:

    python scripts/certify_menu.py INPUT.json --kit PINNED_KIT --output NEW_DIRECTORY

An externally produced certificate may be supplied with `--certificate CERTIFICATE.json`. The command creates only a local working directory and refuses to overwrite one. It emits the original problem separately from the witnesses, compiles their proofs, audits transitive axioms, replays the new modules through Lean's kernel, and compares a diagnostic Lean echo with the original numeric matrices and every derived subset's admissibility and cost.

Success outcomes are `KERNEL_CHECKED_OPTIMAL_MENU` and `KERNEL_CHECKED_NO_ADMISSIBLE_MENU`. Malformed evidence, timeouts, and budget exhaustion return `UNRESOLVED`. A Python-valid certificate is not called kernel-checked.

## Fresh evidence

- 37/37 combined modules compiled and replayed.
- 378/378 named theorem axiom lists audited.
- All 23 original v0.3.0 proof modules retained byte-for-byte.
- 24/24 additional menu cases exported, compiled, and input-echo checked: 20 optima and four no-admissible-menu results.
- 8/8 new paired corruption controls, plus all six previous controls.
- One separate custom-axiom policy control.
- 50/50 new Python unit tests.
- 120 deterministic menu problems and 709 individual subset feasibility comparisons against independent SymPy ranks.
- 34/34 preceding rational Python unit tests rerun.
- 20/20 original Python unit tests and the 3,307-record exact audit rerun.
- The fractional positive CLI returned an optimal menu of cost seven, with coefficient -5/4.
- The four-candidate infeasible CLI returned no admissible menu, using one separator to cover all sixteen subsets.
- A zero-trial-budget CLI control returned UNRESOLVED and exit code 2, without any mathematical rejection claim.

`evidence/verification/current/verification.json` is the authoritative combined fresh record. The previous release was also rebuilt and replayed separately in `evidence/verification/baseline_v0.3.0_fresh`. Inherited records are labeled separately.

## Failure controls

The new accepted source proves that each corrupted check returns false. Separate files then attempt to use those false equalities as true and are required to fail for the exact type mismatch. Controls cover missing cheaper alternatives, zero detectors, exaggerated block coverage, wrong coefficients, a suboptimal expensive singleton, a forbidden selection, a false complete rejection, and an attempt to use an unselected direction. Missing instances and parse errors do not count as successful mathematical rejection.

The first new module compilation failed on deprecated `if_true`/`if_false` names under warnings-as-errors. It was corrected to `ite_true`/`ite_false` and rerun. The failed source snapshot and log are preserved. The original free-repair CLI's theorem-audit filter was tightened to its actual imports so that adding a new general module does not break the old CLI. Its mathematical sources are unchanged.

## Trust boundary

All audited theorem dependencies are contained in {propext, Classical.choice, Quot.sound}. No sorryAx, new assumed theorem, or native-decision axiom is accepted. Concrete certificate reductions use `decide +kernel`.

Replay uses Lean's own kernel and the exact pinned imported environment. It is not a distinct proof-checker implementation and not a fresh proof of all Mathlib dependencies.

Typed rational cell decoding and mathematical checker soundness are formalized. The full external JSON grammar, Python parser, emitter, hashing, and file system are not. Correctness is certified for the literal typed input compiled by Lean. Independent input emission and a complete numeric/constraint echo test its binding to the original input.

The entire Python producer is not proved terminating or correct. Its submitted answers are checked. Zero-dimensional and empty-family cases are included in the samples. The implementation limits are resource guards, not a universal performance guarantee.

## Remaining work

The next mathematical/software step is to reduce the untrusted search work, for example with branch-and-bound while retaining the existing certificate checker as an independent endpoint. A direct adapter into the authoritative Komorebi Python matrix API and deduplication against Paper III are still outstanding. The current package is a standalone experimental extension, not an integration claim.

There is no new theorem about unrestricted nonlinear, integral, arithmetic, or categorical repair; no native Langlands host construction; and no change to Conjecture 66. The role of Komorebi Space remains the ambient realization and admissibility viewpoint, not a blanket assertion that every native problem supplies these finite matrices.
