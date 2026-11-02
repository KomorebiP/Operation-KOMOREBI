# Routes and implementation notes: SF-LEAN-B07

The explicit balance route succeeded: continuity, H(0)=-1, H(infinity)=1 and
strict monotonicity on the nonnegative half-line supply the unique positive
root. Explicit 2x2 determinant algebra then proves the spectrum at a root.
The converse uses reality of eigenvalues and an attained finite norm maximum.
It does not require a general positive-matrix spectral comparison theorem.

Scratch compiler corrections concerned API and typing: the decreasing-power
limit theorem is in the root namespace; product comparison needs the old
second factor and new first factor nonnegative; the function equality in the
limit is proved pointwise; matrix notation needs its scope; real powers are
formed before complex scalar extension; the determinant factorization uses
the correctly signed balance identity; complex algebraic closure needs its
explicit import; and nonnegative norms are converted to real norms through
the library's coercion lemma. No mathematical premise or conclusion was
weakened, and no production placeholder was used.

Missing pinned cache entries were fetched for matrix/characteristic-polynomial
and spectral APIs, followed by complex-polynomial algebraic closure. This is
environment preparation; the public verifier does not fetch dependencies.

General Perron-Frobenius matrix comparison remains deferred, with comparison
and continuity API obligations unresolved. Revisit it for larger matrices.
Logarithmic scalar reparametrization remains deferred, with its variable-change
monotonicity contract untested. Revisit it for explicit exponent enclosures.
Neither alternative is classified as failed or exhausted.

Boundary falsification distinguishes t=0, strict contraction, eigenvector
orientation, and max versus sum normalization. The rational tuple tests a
negative second eigenvalue. Exact fixtures are controls, not substitutes for
the universal proofs. Scratch preflight files stay outside the repository's
production and evidence areas. Every fresh replay uses a new directory;
earlier failed fresh runs, if any, are preserved separately.
