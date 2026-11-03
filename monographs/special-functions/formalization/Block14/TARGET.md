# SF-LEAN-B14 target contract

Base: `297118ccc10550500619224d44f168f6491d02e5` (published Block13).
Authority: H.1 and S1-S3 in `monograph/sections_v11/coupled_structure_full.tex`,
lines 9-115. Scales are positive, without a contraction hypothesis; rows have
complex coefficients and are nonzero for the manuscript classification.

Prove that a constant row admits an arbitrary scalar functional of its
projection for every zero-constant analytic vector input iff the ordered
scale rows coincide and the row is gamma*(1,-1), gamma!=0. Prove the
projected field is then zero, and no invertible constant 2x2 change has two
autonomous rows. Treat arbitrary scalar functionals, not a quadratic ansatz,
and distinguish this operator statement from canonical-solution equality.

Register entire-function and local analytic-germ versions. Equate existence
of an arbitrary scalar functional with constancy on projection fibers;
germ equality is eventual equality near zero. Necessity uses entire polynomial
test inputs; sufficiency will hold for arbitrary functions. A theorem only
about the distinguished canonical pair would not meet this target.

Primary route: the explicit polynomial
f(z)=1-(1-z/q)(1-z/r)(1-z/a)(1-z/b) vanishes at zero and equals one at every
scale node, even when nodes repeat. Three elementary fiber comparisons force
c1+c2=0. Linear and quadratic inputs then recover qr=ab and q^2*r=a^2*b;
nonzero scales recover ordered row equality. Determinant algebra proves the
decoupling obstruction. For local germs, use entire test inputs and the
complex identity principle for necessity, and the pointwise zero identity
for sufficiency.

Alternative source route: polynomial interpolation and differentiation along
fibers. Resume if the explicit polynomial or algebraic comparison fails; its
first uncertainty is the interpolation API at repeated nodes. Alternative
tensor route: alternating bilinear coefficients at distinct nodes. This
requires separate collision handling and is deferred unless a tensor-level
certificate is needed. Discriminators: repeated scales and single-coordinate
rows, plus swapped rows where canonical components agree but operator
autonomy fails. These must not be silently excluded.

The odd-input-only remark and explanatory tensor/rank discussion are outside
this registered main H.1 contract. Preserve all earlier sources and evidence,
the G.2 guard, conditional type convergence and the open I-J/A-E backlog.
Review provenance is self-review; no delegation is authorized. Update actual
I/O, continuation/status records, GitHub and the live .io guide after replay.
