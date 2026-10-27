# Proof Path Theory v1.2.0 — verification summary

**Outcome: PASS.** Recorded run: 2026-10-19T05:17:49.269102+00:00.

| Check | Result |
| --- | --- |
| Python tests | 96 passed, zero failed or skipped |
| Fresh Lean module builds | 8 passed |
| Lean own-kernel module replays | 8 passed |
| Named theorem declarations | 42 checked, including 10 concrete binary example theorems |
| Selected named declaration axiom audits | 78 passed |
| Deliberate invalid controls | 4 rejected by Lean; 1 explicit false axiom rejected by policy |
| Exhaustive binary realization systems | 5,039 checked: 4,359 feasible and 680 infeasible |
| Inherited exact checks | 18 certificate comparisons; 100 greedy cases; 1,024 retention identities; 114 covariance cases |
| Native Lean export | 5 compiled roots, 195 nodes, checked declared closure |
| Manuscript | 46 pages, 14 vector figures, zero LaTeX/preflight warnings |
| Distribution | Wheel and source archive built; isolated wheel installation/import passed |

## Completed mathematics

The proof-field local-model diagram has actual contravariant restriction maps and
an explicit equivalence with its coherent realization space. Whole-support gluing
has a Lean proof and a checked counterexample to pairwise-only AND-rule coverage.
General functional and matrix obstruction alternatives, affine-fiber
classification, exact observation counts and all-predicate compression sufficiency
are included in the checked interfaces.

The paper and code also correct two mathematical distinctions: lossless recoding
need not be the original archive, and audit/discovery equivalence need not be
ordered. Certification strings cannot silently become true booleans.

## Verification boundaries

The entire 33-result-group manuscript is not Lean-formalized. Exact counts are
checked; the uniform-entropy interpretation is a written corollary. The native
exporter was executed on real compiled declarations, not universally verified as
a parser. The Python solver is tested and its generated examples are independently
checked as Lean propositions, not proved correct for every input. Kernel replay
uses Lean itself, not an independent verifier or a fresh replay of all Mathlib.
No empirical social claim, historical-priority claim or external peer review is
implied. The author's redistribution license remains unselected.

## Reproduce

```bash
python scripts/check_manifest.py
python scripts/verify_release.py --runtime /path/to/portable-kit
```

The complete ZIP contains source, manuscript, tests, schema, wheel, sdist, native
export, ledgers, runtime pins and the actual logs. The multi-gigabyte runtime is
supplied separately. Development failures, fixes and interrupted invocations are
retained and not relabeled as successful runs.
