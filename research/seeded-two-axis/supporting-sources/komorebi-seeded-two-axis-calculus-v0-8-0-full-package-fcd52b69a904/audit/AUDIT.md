# v0.8.0 mathematical and artifact audit

## Normalized claim and verdict

The new block K42–K52 has written proofs for the specified perfect-complex,
finite coefficient, uniform based-tower, and finite-free-lattice contracts.
Primary verdict for that block: **proved as written, on authoring-session
self-review**. This is not independent proof review or a proof-assistant
certificate. No fresh complete audit of every retained earlier theorem is
claimed. The intended unrestricted reciprocity goal remains unproved.

## Dependency graph

Derived tensor / perfect base change -> K42 exact tower.
Minimal complexes over Z/p^m -> K42 conservativity and lost-morphism example.
Scalar weights + tensor associativity -> K43.
Koszul basis change + explicit kernels/cokernels -> K44.
Octahedral product cones + nilpotence -> K45.
CRT idempotents + K44/K45 -> K46 finite quotient equivalence.
Coefficient limits + ML product model -> K47 and K48 transition calculation.
CRT ring products + exact perfect functors -> K49 generic-fiber defect.
CRT principal parts -> exact arithmetic square -> derived tensor -> K50.
Bounded local lattices + finite CRT subgroup -> K51 existence and uniqueness.
Exact operator intertwining + restriction -> K52.

## Obligations reviewed

| Obligation | Status | Decisive check |
|---|---|---|
| Derived versus ordinary tensor | Passed | Infinite Tor over Z/p^2 rules out truncation surrogate |
| Perfect-domain membership | Passed | Bounded projective cones retained |
| Coarsening variance and composition | Passed | Derived reduction from m to n, m >= n |
| Conservativity versus faithfulness | Passed | Minimal-complex proof; D^n endomorphism counterexample |
| Actual origin of scalar residual | Passed | Weighted cell distinguished from canonical equivalence |
| Units, nilpotent, zero residues | Passed | h=0 and h=n treated in K44 |
| Quotient noncollapse | Passed with sharp boundary | Selected CRT factors erased; all selected implies zero |
| Finite vs infinite compatibility | Passed | Explicit Q_p fiber refutes unconditional interchange |
| Fiber/cofiber shift | Passed | Cofiber = fiber[1] in D(Bhat) |
| Completion perfectness assertion | Passed | Defect lives in ambient D(Bhat), not necessarily Perf(Bhat) |
| Tower effectivity scope | Passed after explicit contract | Uniform based matrices and compatible homotopies only |
| Lattice existence vs given-object reconstruction | Passed | K51 separately constructs independent gluing input |
| Generic identification hypothesis | Passed | Essential input, not deduced from invariants |
| Operator relations and inverses | Passed | Exact intertwining and inverse data required |
| Zero-rank and empty repair set | Passed | Zero module and identity repair conventions stated |
| Lean formalization | Not addressed | lean/lake not present on PATH |
| Independent mathematical referee audit | Not addressed | This was self-review |
| Arithmetic/automorphic existence | Out of current proved scope | Remains K17 |
| Historical novelty | Not assessed | Dependency lookup, not novelty survey |

## Computation evidence

All three scripts were executed successfully this turn. Results and bounds are
in the three JSON files in `checks/`. The new suite uses exact modular sets,
integer CRT, integer HNF, and Fraction arithmetic. The HNF output is checked
against finite residue groups and determinant/index. No random sample was
called exhaustive. Exhaustiveness is only for the finite families explicitly
listed in the script/report. No finite test is used to prove the limit or
universal categorical assertions.

## Failures and corrections

The first broad web query returned unrelated results. It supplied no evidence;
direct official Stacks pages were used instead. No checker failed in this new
block. No LaTeX compilation failure occurred in the final integrated source.
The launcher printed `TERM environment variable not set` after successful
latexmk completion; this was terminal environment output, not a TeX diagnostic.
There is no Lean executable in the runtime, so Lean certification was not run.

Mathematical negative results are preserved as results, not hidden failures:
ordinary tensor is not an exact substitute, finite prime-power excision can
collapse, and completion need not commute with repair. These refute the
unrestricted variants, not the restricted positive theorems.

## Source and layout

`audit/integrate_v080.py` was rerun with identical source hash. All base hashes
match the preserved supplied files. No duplicate labels or unresolved citations
or references were found. The final LaTeX log has no warnings, overfull boxes,
or underfull boxes. All 73 pages were rendered at 100 dpi using the PDF skill's
renderer. Five contact sheets were visually scanned; pages 39, 43, 45, 46, and
61 were additionally inspected at full page-image size. No clipping, black
squares, overlapping displays, or broken equations were seen. A text-coordinate
scan found no text spans outside page bounds and no replacement characters.
This visual check does not constitute a mathematical audit of all pages.

## Remaining target

Produce a natural, non-scalar arithmetic comparison whose cone survives derived
coarsening, then prove which local/generic information its repair must retain.
A chosen invariants/cohomology model must be checked for exactness and boundedness.
The generic objects and isomorphisms required for a Langlands-facing application
remain separate existence obligations.
