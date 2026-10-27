# Even-C torus and Frobenius at the prime above two

Status: proved local calculation, with the exact semistable Tate-module
filtration checked in the primary source. This note does not by itself
prove global irreducibility or nonexistence of a Diophantine solution.

Let \(A,B,C\) be positive pairwise-coprime integers satisfying
\(A^3+B^5=C^7\), with \(C\) even. Put \(K=\mathbf Q(\sqrt5)\), and
write \(K_2\) for its completion at the inert prime above two, whose
residue field is \(\mathbf F_4\). Let \(J\) be the Jacobian of

\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2.
\]

We use the stable model proved in `evenC_semistability_at2.md`, separately
audited in `cartier_independent_audit.md`.

## The two nodes are nonsplit over F4

The special fiber is geometrically irreducible, with rational
normalization and exactly two ordinary nodes \((r,r)\), indexed by the
two roots \(r,r^2\) of \(r^2+r+1=0\). Both nodes are
\(\mathbf F_4\)-rational. At a node the tangent cone is

\[
t^2+r^2st+r^2s^2.
\]

Its branches have slopes \(k\) satisfying
\(k^2+r^2k+r^2=0\). Set \(k=r^2z\). Since \(r^3=1\), division by
\(r\) gives

\[
z^2+z=r.
\]

The image of \(z\mapsto z^2+z\) on \(\mathbf F_4\) is \(\{0,1\}\).
Neither primitive cube root belongs to this image; equivalently
\(\operatorname{Tr}_{\mathbf F_4/\mathbf F_2}(r)=r+r^2=1\).
Thus the two branches at each node are defined over \(\mathbf F_{16}\)
and are exchanged by arithmetic Frobenius \(z\mapsto z^4\).

The dual graph \(\Gamma\) of the stable geometric special fiber has one
vertex and two loop edges. Frobenius fixes each loop as an unoriented
edge and exchanges its two branches, reversing its orientation. Hence

\[
\operatorname{Frob}_4=-I_2
\quad\text{on}\quad
H_1(\Gamma,\mathbf Z)\quad\text{and}\quad H^1(\Gamma,\mathbf Z).
\]

If one uses the minimal regular model instead, resolving a stable node
inserts a chain of rational curves and subdivides that loop. It does not
change graph homology or its Frobenius action. All normalization
components remain rational. This also follows from the stable-to-regular
model comparison in Deligne–Mumford, Proposition 2.3.

## Integral Tate-module filtration and its reduction

For a semistable Jacobian over a local field and a prime \(\ell\) different
from the residue characteristic, the canonical saturated Tate-module
filtration has Galois-equivariant graded pieces

\[
H^1(\Gamma,\mathbf Z)\otimes\mathbf Z_\ell(1),\qquad
T_\ell\operatorname{Pic}^0(\widetilde X_{\bar k}),\qquad
H_1(\Gamma,\mathbf Z)\otimes\mathbf Z_\ell.
\]

The middle piece is zero here because the normalization components are
rational. Taking \(\ell=7\) gives

\[
0\longrightarrow H^1(\Gamma,\mathbf Z)\otimes\mathbf Z_7(1)
\longrightarrow T_7(J)
\longrightarrow H_1(\Gamma,\mathbf Z)\otimes\mathbf Z_7
\longrightarrow0.
\]

The precise checked source is Tim Dokchitser, Vladimir Dokchitser and
Adam Morgan, *Tate module and bad reduction*, Proceedings of the AMS
**149** (2021), 1361–1372, DOI 10.1090/proc/15067. Theorem 1.5 and
equations (1.1)–(1.2) give the integral equivariant filtration;
Corollary 4.8, manuscript p.12, identifies its graded pieces using the
Jacobian's canonical principal polarization. The theorem permits residue
characteristic two. Remark 4.7 explicitly fixes Frobenius on
\(\mathbf Z_\ell(1)\) as multiplication by the residue cardinality.
The [final author manuscript, arXiv:1809.10208v2](https://arxiv.org/pdf/1809.10208)
was checked directly.

We use arithmetic Frobenius on the usual covariant Tate module, so its
action on \(\mathbf Z_7(1)\) is multiplication by 4. The left and right
graded pieces therefore have Frobenius eigenvalues \(-4,-4\) and
\(-1,-1\), respectively. Any Frobenius lift has characteristic polynomial

\[
\boxed{\det(T-\operatorname{Frob}_{(2)}\mid T_7(J))
       =(T+1)^2(T+4)^2.}
\]

All graded pieces are free \(\mathbf Z_7\)-modules, so reduction modulo
seven preserves the short exact sequence. Consequently the same formula
holds in \(\mathbf F_7[T]\) on \(J[7]\). It applies to eigenvalues of any
residual subquotient, and by lattice independence to constituents of the
rank-two RM factor. No assumption that the whole global semisimplification
is unramified is being used. A one-dimensional global constituent is
unramified at two because semistable inertia is unipotent.

For geometric Frobenius on this same Tate module, invert all eigenvalues:
they become \(-1,-1,-1/4,-1/4\). Mixing that convention with arithmetic
Frobenius at another place would invalidate a reciprocity comparison.

## Exact implication for the global character

Suppose a one-dimensional residual constituent \(\nu\), valued in an
algebraic closure of \(\mathbf F_7\), satisfies the separately established
global relation \(\nu^8=1\). Its arithmetic Frobenius value at the prime
of norm four belongs to \(\{-1,-4\}\). Since

\[
(-1)^8=1,\qquad(-4)^8=2\quad\text{in }\mathbf F_7,
\]

we obtain

\[
\boxed{\nu(\operatorname{Frob}_{(2)})=-1.}
\]

The same conclusion holds if both Frobenius and reciprocity conventions
are inverted consistently. This is the only global-character conclusion
provided by this note; existence, ramification, the order-eight relation,
and comparison with Frobenius at seven come from the separate global
argument.
