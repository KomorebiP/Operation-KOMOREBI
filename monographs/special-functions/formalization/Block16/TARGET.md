# SF-LEAN-B16 target contract

Mathematical base checkpoint: SF-LEAN-B15, Git
`b5faff8889c48150e1fa41be11b6a3d2c47f493b`.
The unrelated reading-table fix `6c05060c` is preserved before publication.
Authority: Appendix J, `monograph/sections_v11/coupled_lab_full.tex`,
normalization and recurrence at lines 15-32; source models
`research/coupled_lab.py:coupled_odd_derivatives` and
`research/family_lab.py:ordinary_taylor_coefficients`.

For every rational scale tuple, every natural index n and either component,
prove the binomial derivative recurrence has the unique solution
A_n=(2n+1)! u_n, B_n=(2n+1)! v_n, where (u_n,v_n) is the existing ordinary
rational recurrence. No positivity or contraction hypothesis belongs to this
algebraic statement. Include zero, signed and noncontracting scale data.

Define a finite paired append-array model initialized at [(1,1)]. At step
n+1, read only stored indices 0 through n and append the next derivative
pair. Prove its entries and length equal the infinite recurrence through
the inclusive last index. Prove enumerate/divide-by-(2n+1)! conversion and
the subsequent enumerate/multiply/sum polynomial equal the certified
ordinary polynomial. Transfer the existing real enclosure to these finite
array polynomials under its original strict contraction and adequate-fuel
hypotheses. Last N retains N+1 coefficients; first omitted degree is 2N+3.

Primary route: the integer choose-factorial product identity cancels the
two input factorials; scaling the ordinary recurrence gives the binomial
recurrence, whose strong-induction uniqueness identifies all indices.
Then use a finite append invariant and list-index identities. Cheapest
discriminator: A_1=2qr, while u_1=qr/3, hence division by 3! is essential.
Attempt to falsify missing-factorial, wrong-parity and exclusive-length
variants with rejection controls; do not weaken their false conclusions.

Alternative direct route: divide the derivative recurrence before induction
and prove ordinary recurrence uniqueness over rationals. Deferred if the
factorial-scaled route closes this contract; resume for a reverse interface
that needs normalization independent of the existing ordinary sequence.
Alternative bounded-output testing cannot establish the all-index claim;
it is not accepted as its proof.

This block specifies mathematical recurrences and finite arrays. It does
not prove execution semantics for Python, Fraction, math.comb/factorial,
mutation or runtime validation. Paired storage models the two rows because
both new entries depend only on the prior prefix, but full source-program
refinement remains open. Guarded disk-majorant loops, resource failures and
returned-dictionary semantics are the next obligations. Additional J
degree/denominator/symmetry, ancillary F/H, I and A-E coverage remain.

Preserve earlier blocks, manuscripts, Python sources, PDFs and receipts.
Review provenance is self-review. Update exact I/O, GitHub and .io after
the accepted pinned replay and catalogue qualification.
