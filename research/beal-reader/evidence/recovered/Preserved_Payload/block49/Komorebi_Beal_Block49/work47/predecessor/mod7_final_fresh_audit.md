# Fresh audit of odd-C mod-seven irreducibility

**Normalized claim.** For positive pairwise-coprime integers A,B,C satisfying A^3+B^5=C^7 with C odd, let J be the Jacobian of y^2+y(X^3+B)=2BX^3+3AX+B^2. Over K=Q(sqrt(5)), the two-dimensional representation obtained from its K-defined real multiplication has absolutely irreducible reduction at the inert coefficient prime (7).

**Primary verdict: proved as written.** This is a written arithmetic proof using the declared standard and primary-source inputs. It is not a formalization, an elimination of the remaining modular forms, or a proof that the initial Diophantine solution cannot exist.

Reviewed on 2026-09-19. Exact reviewed artifact: `mod7_oddC_written_proof.md`, SHA-256 `faa4c7962eab007dd200b8af05f2905c8329125b22aed0e6471b6fffe3f1d0ce`. Base archive SHA-256 supplied with the task: `eb8f9537a827c7487875f51f77eb202e3b2008e677f4993f724cc4fc0321349f`. No proof file was modified.

## Independence and scope

I read the raw proof and independently reconstructed the determinant, local-character, unit, class-field, and Frobenius argument before reading `source_refinement_review.md`. That later file supplied source context, not my verdict. I then directly checked the relevant primary sources. I did not reuse the project's finite-field implementation for the independent point-count and character computations below. This is a fresh subagent audit; it does not claim independence from all possible shared model errors.

## Dependency graph

1. The explicit source-family substitution identifies J without a quadratic twist and supplies K-defined real multiplication and rank-two conductor bounds at 3 and 5.
2. The displayed curve gives good reduction at 2 and semistability at every prime at least 7.
3. The full Tate-module determinant gives the norm of the rank-two determinant, independently of a rank-two polarization convention.
4. Hypothetical absolute reducibility gives two associated characters over the algebraic closure of F7. The conductor bounds force their eighth powers to be unramified away from 7.
5. Semistability at 7 gives four possible local weights. Reciprocity for the fundamental unit removes the two mixed weights; the determinant forces one character to be unramified at 7.
6. The class number calculation makes that character's eighth power trivial globally.
7. Good-reduction Frobenius at the norm-four prime forces its value to have eighth power four in F7, a contradiction.

The proof does not use residual irreducibility to establish any of steps 1–6. In particular, it does not use the source's residual-unramified conclusion or its large-prime irreducibility theorem.

## Crucial reconstruction

### Coefficients, lattices, and determinant

Write E=K_(7), with residue field k=F49. The rank-two E-space is the full four-dimensional Q7 Tate space with its real-multiplication action. A Galois-stable O_E lattice exists: taking O_E times any stable Z7 lattice still gives a finite stable lattice in that space. Its underlying Z7 lattice and T7(J) are commensurable. Their reductions have the same semisimplification over F7; extending scalars preserves their composition factors.

If W is its rank-two k-reduction and delta=det_k(W), restriction of scalars gives

    det_F7(W)=Norm_F49/F7(delta)=delta^(1+7)=delta^8.

The Weil pairing on the four-dimensional Tate space gives det_F7(J[7])=chi^2, hence delta^8=chi^2. This argument never asserts delta=chi.

If W is reducible over Fbar7, its constituents lambda and mu need only be Fbar7-valued. Indeed, after extending the underlying F7 representation to Fbar7 one obtains the two coefficient embeddings of W. Consequently lambda and mu occur as degree-one composition factors of J[7] tensor Fbar7 and satisfy the associated-character hypothesis. Their product is the chosen embedding of delta, so (lambda mu)^8=chi^2 remains valid. No maximal specialized endomorphism order or self-adjointness of real multiplication is needed.

### Conductor and local weights

For residual characteristic seven and residue characteristic q=3 or 5, the finite wild inertia image has q-power order. Averaging preserves its invariant dimensions on reduction and on semisimplification. Tame invariant codimension cannot increase on these operations. Thus the residual semisimple conductor is bounded by the characteristic-zero rank-two conductor.

The identity delta^8=chi^2 kills delta on wild inertia at 3 and 5, because eighth powering is injective on a finite abelian 3-group or 5-group. If one constituent is wild, so is the other. Each then has conductor exponent at least two, contradicting the sum bound three. They are therefore tame. A character of the entire local Galois group kills the Frobenius conjugation commutator, so its tame inertia image has order dividing N(v)-1: eight at (3), four at (sqrt(5)). This holds equally for Fbar7-valued characters. Their eighth powers are unramified there. At every other prime away from 7, good or semistable reduction supplies the same conclusion, and eighth powering kills real-place signs.

At the unique prime over 7, K is unramified quadratic. A degree-one associated character of a semistable abelian variety has weights zero or one at the two embeddings, giving exponents e in {0,1,7,8} of a level-two fundamental character. Wild inertia at 7 cannot act on a finite Fbar7 multiplicative character. A common reversal of reciprocity changes all signs together and has no effect on the argument.

### Unit reciprocity and Frobenius contradiction

With phi=(1+sqrt(5))/2, reduction gives phi^2=phi+1 and phi^8=-1 in F49. Thus phi has order sixteen. Since lambda^8 is unramified away from 7 and trivial at infinity, evaluating it on the principal idele phi gives phi^(8e)=1. Hence e is even and e is either zero or eight. The same holds for mu.

Cyclotomic inertia has exponent eight, so delta^8=chi^2 requires

    8(e+f)=16 modulo 48.

For e,f in {0,8}, exactly (0,8) and (8,0) satisfy this. One constituent nu is therefore unramified at 7. Its eighth power is everywhere unramified, including infinity. Rounding in the integral basis 1,phi gives |Norm(u+v phi)|=|u^2+uv-v^2|<=3/4<1; this proves norm-Euclideanity and ordinary class number one. Because infinity is already killed, there is no narrow-class-group omission. Global class field theory now gives nu^8=1.

The independently enumerated point counts are (3,7) over F2,F4 for (A,B)=(0,1) modulo 2 and (3,5) for (1,0). Newton identities give T^4+T^2+4 and T^4+4 at 2. Since 2 is inert in K, Frobenius at its K-prime squares these eigenvalues, giving (T^2+T+4)^2 or (T^2+4)^2. Every constituent eigenvalue satisfies the corresponding quadratic, without needing to select a rank-two factor.

For Q0=T^2+4, alpha^2=3 implies alpha^8=4 modulo 7. For Q1=T^2+T+4, successive reduction gives alpha^4=5 and again alpha^8=4. These calculations hold in the quotient algebras and hence for every root over Fbar7. They contradict nu(Frob)^8=1 directly; the displayed resultants are not essential to the conclusion.

## Model checks

The rational coordinate changes from the source sextic are invertible because AB is nonzero; direct substitution yields exactly the displayed integral curve. The discriminant argument in `signature_route.md` uses weighted homogeneity to reduce the universal identity to three exact Sylvester determinants; its monomial space and interpolation inference are valid. It is a polynomial discriminant, which is all the semistability argument needs.

If a prime ell>=7 divides C, A and B are units and u=A^2/B^3 satisfies u^3=B and u^5=-A. The special-fiber factorization is therefore valid. The first quadratic has two distinct roots, the second has two distinct roots, and their resultant 45 is a unit. Each double root has two distinct tangent directions, giving an ordinary node. The second quadratic is not a square over the algebraic closure's rational function field, so the special fiber is irreducible. Its genus-zero normalization has four distinct points over the two nodes and the fiber is stable.

The proper model is obtained by the ordinary two-chart double cover of P1. It is flat because its equations are monic in the double-cover variable. At infinity the second chart has leading equation v^2=1 and is smooth for odd ell. A possible singularity of the total surface at a node does not obstruct a stable nodal family or semistable reduction; regularity of that total surface was not assumed. Thus the asserted semistability follows. If ell does not divide C, the unit discriminant gives good reduction.

At 2, the stated affine derivative checks pass. The infinity chart is v^2+(1+B t^3)v=2B t^3+3A t^5+B^2 t^6, whose v-derivative at t=0 is one. This completes the good-reduction check rather than relying on affine smoothness alone.

## Primary-source verification

All source checks were performed on 2026-09-19. The following paragraphs record the external content used; the argument above supplies the application.

* Pacetti–Villagra Torcomian, *On the generalized Fermat equation of signature (5,p,3)*, [arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1), dated 2025-12-19: Section 2.2 identifies the real-multiplication realization up to Tate twist; Section 7.1 gives the genus-two sextic. Corollary 3.6 and its conductor table give upper bound three at 3; Proposition 3.14 and Table 3.5 give upper bound three at 5. Their hypotheses apply with (a,b,c,p,q,r)=(B,-C,A,7,5,3), independently of residual irreducibility. Tate twisting is unramified at these two primes. Retrieved HTML SHA-256: `0a229582422938740aa8d3c541691c011e4200f49a7adcc78fe6c7e3c1d145aa`.
* Larson–Vaintrob, *Determinants of Subquotients of Galois Representations Associated to Abelian Varieties*, [arXiv:1110.0255v4](https://arxiv.org/pdf/1110.0255v4), dated 2012-03-30: the introductory definition allows scalar extension to the algebraic closure. Lemma 4.10 and Definitions 2.7–2.8 give the local embedding weights with bound d times the ramification index. The lemma has no large-prime assumption. The unipotence and principal-idele facts used here also occur in the proofs of Lemmas 4.6 and 5.4. The successfully fetched unversioned PDF authenticates itself on its first page as v4. SHA-256: `a94392c302cab29c44d88f6b67ca5bf58716913e9f97a12a5cbbec4b964325a2`.
* Dokchitser–Dokchitser–Maistret–Morgan, *Arithmetic of hyperelliptic curves over local fields*, [arXiv:1808.02936v2](https://arxiv.org/pdf/1808.02936v2), dated 2018-10-15: Theorem 10.3(1) gives the semistability equivalence for the curve and its Jacobian. The odd-residue-characteristic and genus hypotheses hold at every use here. The exact v2 PDF was fetched and its first-page version checked. SHA-256: `f46f20a4adf8215c566252779a3b4b9028890df36013c7b747fcec2c0313f3a5`.

The primary PDFs were extracted with `pdftotext -layout`; the theorem statements, surrounding definitions, and relevant proofs were read. General Weil-pairing, residual lattice-independence, and class-field-theoretic facts are used in their usual exact forms. I did not reprove the external theorems or audit every result cited inside these primary papers.

## Obligation matrix

| Obligation | Status | Decisive reason |
|---|---|---|
| Source-family and Tate-twist translation | passed | Explicit rational substitution; twist does not affect 3/5 conductors |
| RM lattice and F49/Fbar7 distinction | passed | Restriction of scalars and common composition factors |
| Norm determinant | passed | delta^8=chi^2 on the full four-dimensional module |
| Residual conductor upper bounds | passed | Tame codimension inequality and wild averaging |
| Tameness at 3 and 5 | passed | Two wild characters would force conductor at least four |
| Semistability at 7 | passed | Proper flat stable nodal model |
| Allowed weights at seven | passed | Exact LV lemma, d=1 and ramification index one |
| Global unit restriction | passed | phi has order sixteen; eighth powers kill every other local factor |
| Existence of unramified constituent | passed | Two and only two determinant-compatible weight pairs |
| Class-field conclusion | passed | Infinity killed and ordinary class number one |
| Frobenius contradiction over Fbar7 | passed | Both quadratics force eighth power four |
| Nonexistence of primitive solutions | out of scope | Requires additional modular elimination and the C-even branch |

## Computation boundary and remaining gap

An independent standard-library Python enumeration returned point counts `(3,7)` and `(3,5)`. Pair arithmetic in F7[T]/(T^2-T-1) returned phi^8=6 and phi^16=1; pair arithmetic modulo each Frobenius quadratic returned T^8=4. Exhaustive enumeration of the four remaining exponent pairs returned `(0,8)` and `(8,0)`. These are exact finite algebra checks, not evidence of a universal Diophantine nonexistence claim. SymPy was unavailable; no conclusion depends on it.

There is no remaining implication missing from this irreducibility argument at the stated written-proof level. The strongest safe statement is precisely absolute irreducibility for the C-odd branch. The next research obligation is the separate level-lowering and surviving-form elimination problem, not another local irreducibility test.
