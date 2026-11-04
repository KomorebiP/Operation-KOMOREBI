# SF-LEAN-B16: factorial normalization and finite arrays

The registered normalization contract is proved for **every rational scale
tuple and every natural index**, without positivity or contraction:

\[
A_n=(2n+1)!u_n,\qquad B_n=(2n+1)!v_n.
\]

The derivative arrays satisfy the Appendix J binomial recurrence; u_n,v_n
are the ordinary rational coefficients already identified with the canonical
real coefficients. The finite paired append-array model has length N+1 and
contains precisely indices 0 through N. Enumerating these entries and dividing
entry n by (2n+1)! gives the ordinary coefficient prefix. Enumerating that
prefix, multiplying by x^(2n+1), and summing gives the existing certified
polynomial, for every rational x and last index N. Under the original strict
contraction and adequate-fuel hypotheses, its exact rational endpoints enclose
the actual real canonical component. This completes a mathematical dependency
of Python refinement, not full source-program refinement.

Source authority is Appendix J, monograph/sections_v11/coupled_lab_full.tex
lines 15-32, coupled_lab.py:coupled_odd_derivatives and certified_evaluation,
and family_lab.py:ordinary_taylor_coefficients. The mathematical base is
`b5faff8889c48150e1fa41be11b6a3d2c47f493b`; publication also preserves unrelated reading-table commit
`6c05060c54d96aabf73fb7ab937d150cb6ff80ae`. Source and assessment hashes are in IO_MANIFEST.json.
Manuscripts, Python code, PDFs, earlier blocks and guides retain their bytes.

The key integer identity is choose(2n+2,2i+1)*(2i+1)!*(2(n-i)+1)!=(2n+2)!
for 0<=i<=n. It follows from the pinned Mathlib choose/factorial theorem,
with its subtraction index proved explicitly. Multiplying the ordinary
recurrence by (2n+3)! then gives the binomial recurrence: its divisor
2n+3 cancels, leaving precisely the even factorial above. Strong-induction
uniqueness identifies the sequences at all indices. The input indices i and
n-i are at most n, so the finite append step reads only existing entries;
its default out-of-range value is never used. Indexed list identities prove
the conversion and polynomial sums, and Block15 supplies the analytic bound.

The first discriminator is A_1=2qr versus u_1=qr/3; division by 3! gives the
required equality. The n=0 factorial is 1 and both rows start at 1. Signed,
zero and noncontracting rational tuples are included algebraically; no entire
convergence is inferred for these tuples. Last N includes N+1 entries and
the inherited first omitted exponent is 2N+3.

`lean/CoupledNormalization.lean` adds **30 theorem declarations**, bringing
the registered count to **435**. All **63 fresh replay steps** pass across
sixteen coupled modules: 396 theorem axiom audits, sixteen same-kernel
replays, four expected rejections and one positive fixture. The finite core's
39 names retain inherited evidence. Mathlib imports are cached, not freshly
rebuilt or replayed. Only propext, Classical.choice and Quot.sound are allowed.
Review provenance is **self-review**. The claim map covers all new names once.

The verifier installs nothing, makes no network requests, stages exact inputs
in a new external directory and checks input stability at the end. Formal I/O
contains 56 inputs, 64 packaged outputs, sixteen generated objects and 37 staging
copies. Source assessment and development diagnostics are separately inventoried.

The paired list, exact rational arithmetic and binomial/factorial operations
are Lean mathematical specifications. No Python interpreter, Fraction or
standard-library implementation is certified. Runtime validation, list mutation,
the guarded majorant while-loop/reverse fold, bit limits and returned dictionary
remain explicit obligations. Next: a successful bounded ladder trace must
produce the proved fuel majorant, while step/bit errors remain failures.
Other J degree/denominator/symmetry correspondence, ancillary F/H, I and broad
A-E development remain. No whole-book formalization percentage is established.
