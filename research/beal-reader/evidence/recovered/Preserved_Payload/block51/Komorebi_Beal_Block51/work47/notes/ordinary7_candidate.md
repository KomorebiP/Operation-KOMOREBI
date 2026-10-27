# Block47: Frobenius transport for an unramified constituent at seven

Status: complete written derivation of the local Frobenius transport lemma. The final global extension is conditional here on the independently audited torus-at-two calculation and the combined global character argument. This file does not change the status of previously frozen claims.

## Local statement

Let K_7 be the unramified quadratic extension of Q_7, with residue field k=F_49. Let A,B be integers for which A^3+B^5 is nonzero modulo seven. Let J be the good-reduction Jacobian of

\[
 Y^2=X^6+10BX^3+12AX+5B^2.
\]

Let nu be a one-dimensional unramified constituent over Fbar_7 of J[7] restricted to G_{K_7}. Write Fr_7 for arithmetic Frobenius, whose action on the residue algebraic closure is x -> x^49. Then

\[
 \boxed{\nu(\mathrm{Fr}_7)=\overline A^{\,3}\overline B\ne0.} \tag{1}
\]

The same conclusion applies to any associated RM constituent whose underlying residual semisimplification occurs in J[7]. No integral maximality of the specialized RM order is required.

## Finite-flat transport preserves the Frobenius label

Choose a finite coefficient field E/F_7 over which the constituent and its submodule/quotient presentation are defined. Regarding J[7] tensor E as an F_7-representation realizes it as the seven-torsion representation of a power J^m, where m=[E:F_7]. Thus the E-line carrying nu is the generic representation of a nonzero F_7-subquotient

\[
 U\subset W\subset J^m[7](\overline K_7),\qquad V=W/U.
\]

Let R=O_{K_7} and let Jcal/R be the abelian scheme. Take schematic closures Ucal subset Wcal inside Jcal^m[7]. These are finite flat group schemes, and Qcal=Wcal/Ucal is finite flat and killed by seven. Its generic fiber is the unramified representation V.

The unramified representation V also has a finite étale R-model Ecal, using the equivalence between finite étale schemes over a henselian local ring and over its residue field. Raynaud's theorem applies at absolute ramification index e=1<6: the identification of generic fibers extends uniquely to an isomorphism

\[
 \mathcal Q\simeq\mathcal E. \tag{2}
\]

This is stronger than killing nu after an unramified extension. It retains its precise Frobenius eigenvalue. The generic and special geometric points of a finite étale R-model carry the same unramified Galois representation, with arithmetic Frobenius acting by x -> x^49 on the special geometric points.

The required uniqueness and morphism statements are Raynaud, *Schémas en groupes de type (p,...,p)*, Theorem 3.3.3 and Corollary 3.3.6(1), printed p.268. The schematic closure and quotient facts are in §2.1. The theorem is stated over a mixed-characteristic DVR with e<p-1; its statement does not require an algebraically closed residue field. [Primary source](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).

The special fiber Qcal_k is a subquotient of Jcal_k^m[7]. On geometric points, Wcal_k -> Qcal_k is surjective: a finite faithfully flat quotient has nonempty fibers, and every nonempty finite scheme over an algebraically closed field has a geometric point. Thus Qcal_k(kbar), with its Frobenius action, is an actual subquotient of Jcal_k^m[7](kbar).

## Cartier determines the only possible nonzero Frobenius eigenvalue

Put a=bar(A)^3 bar(B) in F_7. The exact coefficient computation gives Cartier–Manin matrix

\[
 M=\begin{pmatrix}0&\overline A^{\,2}\overline B\\ \overline A&0\end{pmatrix}.
\]

All entries lie in F_7. Over F_49, the square of the semilinear Cartier operator has matrix

\[
 M M^{(1/7)}=M^2=aI_2.
\]

The Hasse–Witt transpose gives the same scalar square. The zeta congruence in Achter–Howe §2.5 therefore yields

\[
 L_{49}(T)\equiv(1-aT)^2\pmod7,
\qquad
 P_{49}(T):=\det(T-\pi_{49}\mid V_\ell J_k)
 \equiv T^2(T-a)^2\pmod7, \tag{3}
\]

where ell is any auxiliary prime different from seven and pi_49 is the 49-power Frobenius endomorphism. Their paper explicitly formulates the second congruence for the relative Frobenius endomorphism of the Jacobian. [Primary source, §2.5](https://www.math.colostate.edu/~achter/math/hwcm0618.pdf).

For completeness, the same polynomial P_49 annihilates pi_49 as an endomorphism of J_k: Cayley–Hamilton proves this on V_ell J_k, and the Tate-module action is faithful. Faithfulness follows because an endomorphism killing all ell-power torsion must be zero; equivalently the union of prime-to-characteristic division points is Zariski dense. Hence the reduction of P_49 annihilates pi_49 on J_k[7](kbar), and on every subquotient and every power of this module.

By (2), nu(Fr_7) is a nonzero eigenvalue of pi_49 on such a special-fiber subquotient. Equation (3) forces it to equal a. This proves (1), including the conclusion that a is nonzero.

No assertion that the rank-two Frobenius polynomial equals an arbitrarily selected quadratic factor was used. The full degree-four annihilating polynomial suffices. No good-reduction trace at the residual characteristic was naively substituted into a ramified seven-adic representation; the finite étale subquotient provides the legal comparison.

Under the opposite global Frobenius convention, both generic and special eigenvalues are inverted and the formula becomes nu(Fr_7)=a^{-1}. The later contradiction uses the value -1 and is unchanged. Throughout this note the arithmetic convention above is fixed.

## Proposed global application, with explicit dependencies

Suppose A^3+B^5=C^7 is primitive, C is even, and 7 does not divide C. Assume hypothetical absolute reducibility of the RM representation. The Block46 conductor, unit and determinant argument, now using `evenC_semistability_at2.md`, gives a constituent nu with these properties:

1. nu is unramified outside the primes above 3 and 5.
2. It is tame at these two primes and nu^8=1.
3. It is an associated constituent of J[7] and is unramified at seven.

The prime two is inert in K=Q(sqrt5). The independent torus calculation is intended to show that the full residual Frobenius eigenvalues at its norm-four prime belong to {-1,-4}. Since (-4)^8=2 modulo seven while (-1)^8=1, property 2 forces

\[
 \nu(\mathrm{Fr}_2)=-1. \tag{4}
\]

Here Fr_2 denotes Frobenius of K at its prime of norm four. Equation (4) remains a dependency on the torus calculation, not an inference from the singular curve's ordinary point count.

Let phi=(1+sqrt5)/2. The unit phi^4=3phi+2 is totally positive. Its residue modulo (3) is -1 and modulo (sqrt5) is 1. Global reciprocity on phi^4, together with tameness and the unramified conditions, forces the local unit character at (3) to take -1 to 1.

Now use the positive rational number 2/7. Its residues at (3) and (sqrt5) are respectively -1 and 1. Its valuations at the K-primes above two and seven are +1 and -1, with all other finite valuations zero. Every real local factor is trivial because 2/7 is positive. Reciprocity therefore gives

\[
 \nu(\mathrm{Fr}_2)=\nu(\mathrm{Fr}_7). \tag{5}
\]

Using (1), (4) and (5), obtain

\[
 \overline A^3\overline B=-1.
\]

In particular A and B are nonzero modulo seven. Fermat's finite-field identity gives A^6=1 and hence A^{-3}=A^3. Thus B=-A^3 and

\[
 A^3+B^5=A^3-A^{15}=A^3-A^3=0\pmod7.
\]

This contradicts C^7 nonzero modulo seven. Consequently, once the three global character properties and the torus calculation are verified together, the even-C, 7-not-dividing-C branch is absolutely irreducible. Combined with Block46, only the even-C, 7-dividing-C branch would remain in this particular irreducibility argument.

The proof's target is absolute irreducibility of an attached representation. It is not nonexistence of the original primitive solution and does not eliminate modular forms.
