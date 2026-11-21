## 6. Certificates and reproduction

### 6.1. How a finite certificate proves an all-index assertion

The written proofs supply the uniform annihilators and their start indices.
Finite determinant values alone would not supply those conclusions.
For clarity, the algebraic bridge used by the generating-function
certificates is recorded here.

**Certificate lemma.** Suppose a sequence satisfies a monic recurrence
\(A(S)W_N=0\) of order \(r\) for every \(N\ge1\). Set
\[
 \begin{aligned}
 G(z)&=\sum_{N\ge0}W_Nz^N,\\
 D(z)&=z^rA(z^{-1}),\\
 H(z)&=[D(z)G(z)]_{\le r}.
 \end{aligned}                                                    \tag{E2}
\]
Then \(D(0)=1\) and \(G=H/D\). The numerator \(H\) is determined by
\(W_0,\ldots,W_r\). If proposed polynomials \(U,V\), with \(V(0)=1\),
satisfy \(UD=HV\), then \(G=U/V\). If they are coprime, its reduced
denominator has degree \(\deg V\), which is exactly the minimal eventual
scalar constant-coefficient recurrence order.

**Proof.** The coefficient of \(z^{N+r}\) in \(DG\) is the stated
recurrence residual. Thus every coefficient above degree \(r\) vanishes,
which proves (E2) and the cross-multiplication assertion. If a monic
recurrence of order \(d\) holds eventually, multiplication of \(G\) by
its reversed polynomial yields a polynomial. Coprimality of \(U,V\) forces
\(V\) to divide that reversed polynomial, so \(d\ge\deg V\).
Conversely, multiplication by \(V\) gives an eventual recurrence of order
\(\deg V\). This proves equality, including order zero.

The modular witnesses in the source package establish coprimality after
clearing rational denominators. They retain both polynomial degrees and
verify a Bezout identity equal to one modulo the stated prime. A nonconstant
common factor over the rationals would retain a nonconstant common factor
under that degree-preserving reduction, contradicting the identity. This
supplies an exact lower bound, rather than an inference from a fitted list.

### 6.2. Portable replay

Extract the current sequence-formula source ZIP into a fresh directory.
Python 3.10+ and its standard library suffice for the mathematical replay:

```sh
python -B tools/verify_sequence_final_edition.py --output final-edition-checks
```

The command runs the six retained replayers supporting this edition: the
quadratic order-63 sample, the mixed order-112 sample, the sharp uniform
quadratic theorem, the uniform mixed theorem, the complete boundary table,
and the complete nonzero rule. It checks the component outputs and writes a
combined receipt. The original certificates are proposed coefficient lists;
the replayers reconstruct and verify their identities.

The N replay includes 45 degree-complete characteristic nodes, eight exact
Bezout leaves, ten reduced generating-function certificates, confluence
regressions, and 2,732 direct defining determinant comparisons. The written
collision and confluence arguments provide universal coverage. Some general
quartics in the confluence regressions lie outside the mixed family; those
checks do not assert that every regression order occurs in that family.

For an individual normalized parameter, use, for example:

```sh
python -B tools/sequence_hankel_orders.py --coefficients verification/sequence-library/hankel-compression/interior-coefficients.json --t 1 --q 1
```

This returns minimal eventual order 98. For a negative fractional argument,
use the equals form, for example `--q=-16/9`. The browser engine can be
compared with the Python engine using the optional Node.js 24 checks:

```sh
python -B -m unittest discover -s tools -p test_sequence_hankel_orders.py -v
node --test tools/test_sequence_hankel_orders.mjs
```

The versioned PDF and standalone HTML are produced from this same manuscript.
Their build receipt pins the manuscript, the four imported proof sources,
the renderer, and the output hashes. PDF rendering uses the retained MathJax
SVG runtime and a Chromium browser; it is separate from the standard-library
mathematical replay. Typography may vary with a different rendering engine.

### 6.3. Source lineage and review

This edition is based on source revision
`af2d91ead77d06f7903239f1da293e26bb00f240` and its 101-member source archive,
whose SHA-256 is
`e7a43e634553bf7d814518cd65a14769a2d2094afd8db85e5641675afca52ccd`.
That archive is retained unchanged as
`sequence-formula-source-af2d91ea.zip`.
The predecessor mathematical notes and their certificates remain unchanged.
The assembly report records the editorial joins, updated historical scope
sentences, and local cross-reference labels used in the consolidated paper.
Every imported TeX expression is checked against its source.

The source reviews are retained as `SHARP_QUADRATIC_REVIEW.md`,
`UNIFORM_MIXED_REVIEW.md`, `EXCEPTIONAL_ORDERS_REVIEW.md`, and
`INTERIOR_ORDERS_REVIEW.md`. The final-edition review checks their integration,
the boundary/nonzero partition, notation, certificate dependencies, and the
new certificate lemma. These are project self-reviews. Automated code tests,
browser checks, and source hashes serve their stated purposes; they do not
constitute independent mathematical review or Lean formalization.

## 7. Scope of the final edition

The mixed linear-weight, first-order-operator minimal-order classification
is complete as stated by Theorems M and N, with Theorem L giving the optimal
uniform bound. The quadratic identity-operator bound in Theorem K is also
sharp, but it does not classify the minimal order at every quadratic weight.
Pointwise quadratic-weight orders, higher-degree weights, and higher-order
mixed operators remain separate research targets.

This is a finalized edition of those stated results and their reproducible
evidence. It makes no historical novelty claim. Later corrections or
extensions should receive a new version while preserving this edition's
sources and hashes.
