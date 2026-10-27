# Admissibility dictionary and a discriminating check

This is a focused reconstruction boundary. It supplies two elementary
derivations and identifies the unverified typed arrows. It does not prove or
refute the full IUT comparison.

## Staged dictionary

The following arrows are **tasks to verify**, except for the explicitly
elementary consequences below. They must not be silently treated as equalities
of definitions.

| Reconstruction interface | Original-side input to match | Current status |
| --- | --- | --- |
| LANA weakened BPS | Actual prime-strip, Galois/unit data, compact structures and value-group rigidification | Source-level correspondence; full equivalence not reconstructed |
| LANA \(VC(I)\) | Family of packets indexed by stage \(j\) and place, each with prescribed tensor factors, component weights and integral structures | Compressed container notation; no license to replace it by an arbitrary direct sum |
| An admissible choice \(S\) | A complete tuple of allowable realizations, comparisons and region choices yielding the prescribed output | No complete independent predicate translated in this pass |
| Output family \(\{P_\beta\}\) | The actual output after those choices | Not interchangeable with the family of hull approximants of one already fixed \(P\) |
| \(S\mapsto M\mapsto[M]\) | Output region, hull, corrected weighted determinant and log-Kummer adjustment, then numerical quotient | Each comparison and its normalization must be retained |
| \(\eta_S^{anab}=\eta^q\) | Native marked pilot represented by this admissible construction with useful quantitative bound | **Unverified compatibility** |

Thus the original fixed-region approximant family \(\Phi(P)\) and LANA's
integral-structure choice \(S\) have different logical positions. The former
starts after a region is available. Choosing an element of it does not by
itself manufacture a new admissible input tuple or comparison map.

## Elementary consequence of a bounded hull

Let \(\mathcal P\) be a partially ordered family of regions, with an
inclusion-preserving real functional \(\mu\), and let \(\phi\) be a closure
operator: it is monotone, extensive and the identity on its closed objects.
Fix \(P\) and define

\[
\mathcal A(P)=\{H:H\text{ closed},\ H\subseteq\phi(P),\
                  \mu(P)\le\mu(H)\}.
\]

Then

\[
\phi(P)\in\mathcal A(P),\qquad
\bigcup_{H\in\mathcal A(P)}H=\phi(P),\qquad
\sup_{H\in\mathcal A(P)}\mu(H)=\mu(\phi(P)).
\]

Proof: \(P\subseteq\phi(P)\) and monotonicity give the first assertion.
Every member lies in \(\phi(P)\), while this closed region itself is a member,
giving the union identity. The same argument applied to \(\mu\) gives the
supremum formula, with the supremum attained.

Consequently, a prescribed number \(q_0>\mu(\phi(P))\) cannot be realized
or upper-dominated by varying only \(H\in\mathcal A(P)\). If
\(q_0\le\mu(\phi(P))\), numerical domination follows by choosing the largest
member, but this implication begins with the desired upper bound and supplies
no independent proof of it. A geometric inclusion of the native pilot region
into the same hull would be sufficient by monotonicity; its existence is a
separate compatibility claim. Exact equality of numbers may be stronger than
needed, but an uncontrolled scalar change is not a proof of the weaker bound.

This checks a definite proposed repair: **hull-approximant freedom alone
cannot force a native number beyond the existing hull's bound**. The argument
does not apply to a change of the underlying admissible family unless the
new family and its hull estimate are first constructed.

## Why a cyclic permutation of the \(j^2\) coordinates needs a new map

Consider the proposed model

\[
L_\theta=\bigoplus_{j=1}^k\pi^{j^2m}\mathcal O,
\]

and its hull after cyclic permutations of these \(k\) summands. This is a
well-defined operation in that model. Its coordinates are the \(k\) separate
exponents \(j^2\), and its ambient object is their direct sum.

The source-map table instead specifies a tensor packet at each stage, with
\(j+1\) factors at stage \(j\). Permuting tensor factors in that stage has a
different domain and codomain from moving one stage to another. A source-to-model
map would therefore have to prove both that the displayed direct-sum summands
represent those original objects and that the cyclic permutation is induced by
an allowed comparison, with the component weights and markings preserved.
Neither statement follows from naming both operations permutations.

As a simple algebraic type check, for any field \(K\), the multiplication map

\[
K\otimes_K\cdots\otimes_K K\simeq K
\]

identifies every permutation of the factors with the identity. Multiplication
by a central scalar \(a\) in one factor induces multiplication by the same
\(a\) on the tensor product, regardless of that factor's position. Thus
factor-permutation symmetry does not, as a formal principle, turn
\(a=q^{j^2}\) into \(q^{r^2}\) for another stage \(r\). This is a type
diagnostic only: these tensor products over \(K\) are not substituted for the
original packets, and no claim is made that the specialization satisfies
initial Theta-data.

The cyclic construction is therefore **unverified as an admitted original-IUT
variation**. This verdict does not declare that no more elaborate global
construction can induce an effective mixing. It identifies the explicit map
and normalization proof needed before the model can bear that interpretation.

## Next mathematical step

Construct a tuple parameter space \(\mathscr A\) from the complete original
definitions and a map \(a\mapsto S_a\), then form the actual marked comparison
\(\eta_a\). Prove compatibility with changing the admissible tuple and retain
one quantitative hull bound across the choices used. Test whether the native
marked map occurs among these \(\eta_a\), or at least whether a witnessed
numerical upper-cofinality condition holds. A free choice of real scalar,
arbitrary container, or direct-sum permutation does not resolve this task.

Only the bounded-closure and tensor-factor statements above are independently
proved here. Theorem 3.11's anabelian leaves and the full determinant/log-Kummer
pipeline remain source assertions requiring further reconstruction. No new
ABC inequality or formal proof-assistant verification is claimed.
