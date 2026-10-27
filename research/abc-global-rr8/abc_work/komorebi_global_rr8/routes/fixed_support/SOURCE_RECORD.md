# Source check for the fixed-support route

Checked on 2026-10-25. This is a theorem-extraction and application check,
not a novelty search and not a rereading of the entire proof of the source.

**Source.** J.-H. Evertse, H. P. Schlickewei and W. M. Schmidt,
*Linear equations in variables which lie in a multiplicative group*,
Annals of Mathematics 155 (2002), 807–836,
DOI https://doi.org/10.2307/3062133.

The publisher's article page confirms authors, title and publication:
https://annals.math.princeton.edu/2002/155-3/p04 .

The exact theorem text read was the 33-page primary author-hosted preprint:
https://pub.math.leidenuniv.nl/~evertsejh/00-equation.pdf .
It is linked as item [55] from the author's institutional publications page:
https://pub.math.leidenuniv.nl/~evertsejh/publications.shtml .
The retrieved PDF has no explicit version date on its opening page. It is
therefore pinned here by this exact primary URL and retrieval date, not
identified with an unverified final published PDF or a guessed byte hash.
No full source text or PDF was copied into the checkpoint. The versioned
arXiv PDF math/0409604v1 was attempted but could not be fetched by the web
tool; it is not the theorem-text version on which this route relies.

**Extraction.** Theorem 1.1, beginning at the end of PDF page 1 and
continuing on page 2, assumes a characteristic-zero algebraically closed
field and a subgroup of the n-fold multiplicative group of finite rank r.
It gives at most exp((6n)^(3n)(r+1)) nondegenerate solutions to the stated
linear equation with fixed nonzero coefficients. The definition of
nondegeneracy and rank was read immediately before that theorem.

**Translation.** Embed positive rational S-units into the algebraic closure
of Q. Set n=2, both coefficients to 1 and Gamma=U_S squared. Unique prime
factorization gives rank r=2|S|. Positivity implies nonzero coordinates,
and for two variables these are the only proper nonempty subsums.
The primitive rational-normalization bijection is proved in PROOF_NOTE.md.
The application therefore verifies the stated count and fixed-S finiteness.

**Boundary.** The extracted theorem does not supply a maximum-height
estimate to this route. No theorem about a sharp radical-height bound,
formal Lean source, actual IUT instantiation or novelty is inferred.

Web retrieval references for the coordinator: primary theorem text
`turn105view0`, publisher metadata `turn103view1`, author link provenance
`turn104view0`. The coordinator must open the primary URL before using an
inline source citation from its own answer.
