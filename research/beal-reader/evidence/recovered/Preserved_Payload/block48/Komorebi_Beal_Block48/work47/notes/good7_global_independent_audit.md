# Independent audit of the two-to-seven Frobenius argument

Audit date: 2026-09-19. Reviewer: the separate modular-correlations agent.

## Verdict and scope

No gap was found in the combined written argument proving absolute irreducibility of the residual rank-two RM representation when C is even and seven does not divide C. Together with the retained odd-C result, this gives irreducibility whenever 14 does not divide C.

This verdict uses the previously audited Block46 realization, conductor bounds, local associated-character weights, lattice-independence, and class-field inputs. The new finite-flat Frobenius transport, the exact torus signs, their compatibility with reciprocity, and the final contradiction were independently checked below. The result is a written proof with named external arithmetic theorems, not a Lean formalization and not the nonexistence of a primitive solution.

Reviewed working files:

- `notes/mod7_good_reduction_irreducibility.md` (the canonical final theorem, read after the component audit and confirmed to compose the checked statements correctly);
- `notes/mod7_irreducibility_extension.md` (the earlier seven-divides-AB version, for the shared global character argument);
- `notes/reciprocity_two_seven.md`;
- `notes/ordinary7_candidate.md`;
- `notes/evenC_semistability_at2.md`;
- `notes/evenC_torus_frobenius.md`;
- `notes/cartier_independent_audit.md`.

The proposed good-seven proof and the local notes were read before this reviewer supplied comments on them. The reviewer did not author those proofs. This audit independently reconstructs the combined deduction. After the canonical final theorem was available it was separately read in full and found to state and compose the same checked result correctly. The earlier seven-divides-AB main note remains a narrower historical claim.

## 1. The global character produced by reducibility

Suppose the rank-two representation is absolutely reducible and its characters are lambda and mu. The retained determinant statement is (lambda mu)^8=chi^2. It does not need the stronger equality lambda mu=chi.

Semistability at all finite primes outside three and five, now including two for even C, makes the degree-one characters unramified away from three, five and seven. At three and five, the determinant is trivial on wild inertia because its eighth power is trivial and a 3-group or 5-group has no nontrivial element of order dividing eight. If either character were wild, the other would be wild; the sum of their conductor exponents would be at least four, contradicting the retained bound three. Their tame inertia orders consequently divide eight and four respectively.

At seven the local weight input gives exponents e,f in {0,1,7,8}. Applying reciprocity to the global unit phi=(1+sqrt(5))/2 and each eighth power eliminates e=1,7 because phi has order sixteen in the residue field F49. Thus e,f lie in {0,8}. The determinant identity imposes

    8(e+f)=16 mod 48,

so precisely one character is unramified at seven. Denote it by nu. Then nu^8 is unramified at every finite prime and trivial at the real places. The field K has class number one: rounding the coefficients of a+b phi gives a norm error bounded by 3/4, so its integer ring is norm-Euclidean. Global class field theory therefore gives nu^8=1.

This step produces one fixed global character. Later local matches are required of that same nu. It is not a separate choice of a local constituent at two and at seven.

## 2. Reciprocity retains the two Frobenius labels

The identity phi^4=3phi+2 is correct. This unit is totally positive, has residue -1 at (3), and residue 1 at (sqrt(5)). Since nu is tame at these places and unramified elsewhere, global reciprocity gives nu_(3)(-1)=1.

The positive number 2/7 has residues -1 and 1 at those same places. Its only nonzero valuations are +1 at the inert prime (2) and -1 at the inert prime (7). Applying reciprocity with one consistent convention gives

    nu(Frob_(2)) = nu(Frob_(7)).

No real sign remains. The norm of the first prime is four and the norm of the second is forty-nine. Those norms must not be replaced by two and seven.

## 3. Independent derivation of the torus signs

For even C, both A and B are odd. The stable special fiber at two is irreducible, has rational normalization, and has nodes (r,r) with r^2+r+1=0. At either node the tangent equation is

    t^2+r^2 st+r^2 s^2=0.

Writing the slope as k=r^2 z reduces the branch equation to z^2+z=r. Its right-hand side has trace one from F4 to F2, so the branches are not defined over F4. They are defined over F16 and exchanged by Frob_4. Both nodes themselves are F4-rational.

It follows that Frob_4 acts by -I on the rank-two graph homology: each of the two loops is fixed with its orientation reversed. The source's integral Tate-module filtration supplies toric and graph graded pieces; the normalization contributes no abelian part. Their eigenvalues on the covariant seven-adic Tate module are -4,-4 and -1,-1. The filtration is saturated, so reduction modulo seven preserves these eigenvalues. Since (-4)^8=2 modulo seven whereas (-1)^8=1, the fixed character nu must satisfy

    nu(Frob_(2))=-1.

I independently checked the primary source [Dokchitser–Dokchitser–Morgan, *Tate module and bad reduction*, arXiv:1809.10208v2](https://arxiv.org/pdf/1809.10208), Remark 4.7 and Corollary 4.8, manuscript pp.11–12. They give the integral equivariant pieces and the cyclotomic Frobenius convention used here. The lattice reduction and the characteristic-two application are valid. Inverting all Frobenius conventions consistently leaves the forced value -1 unchanged.

## 4. Finite-flat transport at the residual prime is justified

The delicate step is transporting an unramified constituent of generic seven-torsion to the special fiber without losing its Frobenius value. The argument in `ordinary7_candidate.md` handles this correctly.

An arbitrary finite coefficient extension is handled by a power of J and an underlying F7-subquotient W/U. Schematic closures in the good-reduction abelian scheme give a finite-flat quotient Q with this generic representation. The same unramified representation has a finite-étale model over the unramified local ring. Since e=1<6, Raynaud's uniqueness identifies the two models, preserving the generic and special Frobenius action. The special geometric points of Q are a subquotient of the special seven-torsion of that power of J. Surjectivity on geometric points follows from the finite faithfully flat quotient over an algebraically closed residue field.

I checked [Raynaud, *Schémas en groupes de type (p,...,p)*, original paper](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf), Theorem 3.3.3 and Corollary 3.3.6, printed p.268. The uniqueness statement applies to arbitrary finite commutative p-power groups under e<p-1. Its morphism statement gives unique extension, with flat kernels and cokernels. It does not require first trivializing nu or discarding the Frobenius label.

## 5. The Cartier scalar is the correct eigenvalue

The directly verified Cartier–Manin matrix is

    M = [[0,A^2 B],[A,0]] mod 7.

Its entries belong to F7, so its second semilinear iterate over F49 is the scalar matrix A^3 B I. The transpose convention for Hasse–Witt does not change this scalar square.

I independently checked the corrected version of [Achter–Howe, *Hasse–Witt and Cartier–Manin matrices: A warning and a request*, arXiv:1710.10726v5](https://arxiv.org/pdf/1710.10726), §2.5, printed p.6. It gives, for the forty-nine-power Frobenius endomorphism, the full characteristic-polynomial congruence

    P49(T) = T^2(T-A^3 B)^2 mod 7.

This polynomial annihilates the Frobenius endomorphism of the special Jacobian. One can prove this from Cayley–Hamilton on an auxiliary Tate module and faithfulness of the endomorphism action. Consequently it annihilates every subquotient of the special seven-torsion geometric points. Since the transported unramified character has a nonzero eigenvalue, that eigenvalue must be A^3 B. Thus

    nu(Frob_(7))=A^3 B mod 7.

This avoids an unjustified use of a good-reduction trace on the full ramified seven-adic representation. It also avoids selecting an arbitrary quadratic factor of a degree-four polynomial or assuming that the integral RM order is maximal. The full annihilating polynomial and a finite-étale subquotient suffice.

## 6. Contradiction and exact boundary

Combining the previous steps gives A^3 B=-1 modulo seven. In particular A and B are units. Since B^6=1,

    A^3+B^5 = A^3+B^{-1} = 0 mod 7.

This contradicts C^7 nonzero modulo seven. The good-seven even-C branch is therefore absolutely irreducible.

When C is divisible by seven the good-reduction finite-flat comparison used in §4 is unavailable. This audit makes no claim to exclude that branch. Together with the retained odd-C theorem, the only uncovered branch of this irreducibility argument is 14|C. Even full irreducibility would still require modular attachment at seven and elimination of all candidate forms before proving signature (3,5,7).

## Audit limitations and provenance

No new computation or formal theorem was claimed by this audit. The existing symbolic Cartier calculation, point-count checks, and prior Block46 source hypotheses were retained, while the new local-to-global composition and the three primary theorems above were checked independently. The initial version-specific arXiv request for 1710.10726v5 failed; the current PDF fetched successfully and explicitly identified itself as v5 with the corrected §2.5 formula. The source-note authors received the audit conclusions during this review, but no mathematical repair was required for the checked combined chain.
