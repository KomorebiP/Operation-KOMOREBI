# Independent arithmetic and normalization audit113

Date: 2026-10-01 UTC.

**Primary verdict: incomplete, with the smallest remaining implication identified.** The corrected character theta'_F is an actual simple character, preserves the required central-character compatibility, and its complete cubic self-twist scalar obstruction vanishes. Its occurrence in the particular candidate AI_(L/F)(chi) remains unproved. The original, uncorrected theta_F fails that occurrence test: its nontrivial uniformizer scalar excludes the necessary cubic self-twist for every central-type extension. This is a rejection of this specific new test instance, not a counterexample to original Claim16.2 or a promotion from 65/66.

The arithmetic construction, literal lattice quotient, and actual canonical quadratic-extension trace pass this audit after one recorded normalization repair. The audit inspected raw formulas and scripts, re-executed the finite computations, and independently reconstructed the critical central scalar without the author's averaged intertwining operator.

## 1. Authoritative revisions and scope

The following exact revisions were reviewed:

| Artifact | SHA256 |
|---|---|
| `reports/ARITHMETIC113.md` | `4774c6e680aac343f8cf75e726cc8ea1c92387955f586abdc154d89aa55afd09` |
| `reports/LATTICE113.md` | `e4eb2e0432f609fbdd884e7c7b51852442d5cd55917c302b4a0dae4e0c3a4552` |
| `evidence/arithmetic/cyclotomic_check113.py` | `9e3e0f95f36fa47a21bf820c4b7433ecd9703839d53710abf0cb62855eb8986d` |
| `evidence/arithmetic/self_twist113.py` | `e888439f2584f158c14c55951aad1cd4a0185f28d6ccbf92468c4efdcbf528dc` |
| `evidence/arithmetic/central_twist113.py` | `fbc325d0ab54c303dc8fa4d799fc02a861a69bd379e935b5ab0336a8919c7f78` |
| `evidence/lattice/check_lattice113.py` | `fc18403539307af67c0839c5a6b91b1f97cc3bb9706021ead8aa613435347cd4` |

The coefficients are exact rational numbers in the two Eisenstein field presentations, and exact F3/F9 arithmetic. The p-adic logarithms used for individual character values are reduced to finite rational sums with a proved tail bound. No floating-point approximation is used. This audit does not claim a Lean formalization of local fields or automorphic induction.

The primary source checks used the unchanged local BK book text and supplied BH1996/BH1999 PDFs/extractions. Relevant exact leaves were BK1.4.14–15,3.1.7–8,3.2.1,3.3.2 and5.1.1; BH1996(14.9),14.21 and the proof of14.3; BH1999§1.8,§3.1 Lemmas3–5 and A2.2–A2.4. The all-central-type exclusion also has a separate independent source audit in `reports/SELF_TWIST_AUDIT113.md`. No global novelty claim is made.

## 2. Dependency graph and obligation matrix

The verified path is:

1. Actual cyclotomic fields and additive-character convention determine chi and the minimal parameter beta.
2. Literal hereditary-order ideals determine H1,J1 and the actual simple character theta_F.
3. The actual matrix commutator gives the finite symplectic quotient and eta degree.
4. The norm/trace construction gives the actual quadratic tame lift and its fixed-character power.
5. The actual finite quotient, Glauberman correspondence and determinant normalization give the trace−3.
6. Direct conjugation identities on the actual H1 and J1 yield a model-independent full central-type scalar.
7. BK intertwining and compact induction transport a nontrivial scalar into an exclusion of the original candidate; the explicit correction removes that scalar but does not identify the prescribed inducing character.

| Obligation | Result |
|---|---|
| F=Q3(zeta3), L=Q3(zeta9), relative degree3 and different exponent6 | Passed |
| Additive conductors p_F and p_L^(-3) | Passed |
| chi conductor7 and conjugate quotient conductor5 | Passed |
| beta=pi^(-10) minimal, full field degree3 | Passed |
| Actual theta on U_L^1 U_A^6, J1=U_L^1 U_A^5 | Passed |
| Quotient order9, eta_F degree3 | Passed |
| Quadratic quotient order81, eta_K degree9, fixed-character theta_F² | Passed |
| Canonical C2 extension trace−3 | Passed |
| Central-character-aware tame occurrence equivalence | Passed as a corollary of the checked source theorem |
| Original theta's cubic simple-character intertwiner | Passed |
| Original theta's full central-type scalar | Nontrivial, equal to zeta3, independently verified |
| Original theta occurrence in AI(chi) | Refuted by the full-type self-twist obstruction |
| Corrected theta' simple-character and central compatibility | Passed |
| Corrected theta' full cubic self-twist | Passed |
| Corrected theta' occurrence in the particular AI(chi) | Not proved |
| Original Paper XI packet, kappa and unchanged H5 attachment | Not supplied by this instance |

## 3. The normalization error found and repaired

The first lattice report used psi_F(x)=psi_Q3(-Tr(x)/3), while the arithmetic report and exact witness script used the plus sign. Those choices give inverse literal chi and theta, so the initial claim that the two routes shared the same character was false. This was an integration error, even though the conductor and dimension calculations were unaffected.

The repaired common convention is

\[
\psi_F(x)=\psi_{\mathbf Q_3}(\operatorname{Tr}_{F/\mathbf Q_3}(x)/3).
\]

Since Tr(1)=2, the residue character is a↦zeta3^(2a). The raw companion-matrix computation returns the alternating matrix-trace form B. The actual group-commutator exponent is therefore 2B. Upstairs it is Tr_(F9/F3)(2B), and on the embedded F3 quotient it is4B=B, twice the original exponent2B. This agrees with theta_K restricted to H_F^1 being theta_F².

The old report was preserved at `evidence/lattice/LATTICE113_SIGN_REVIEWED_SNAPSHOT.md`, SHA256 `37776798a1b79ea9c56cad066cb3d49095468a09f441e8c9abc3a4d6696728fc`. The unchanged raw matrix computation remains valid because it computes B, independently of the final additive-character embedding.

## 4. Local arithmetic and actual groups

The relative Eisenstein polynomial is X³+3X²+3X−pi_F. Its derivative at pi is3(1+pi)², so the different exponent is6. With v_L(3)=6 and the specified trace divided by3, the induced character psi_L is trivial on p_L^(-3) and nontrivial on p_L^(-4). Thus beta=pi^(-10) produces chi conductor7. Logarithm and exponential are inverse on p_L^4 and U_L^4, so this is an ideal-level conductor calculation, not an inference from one vanishing sample.

The automorphism sigma(zeta9)=zeta9^4 satisfies v_L(sigma(pi)/pi−1)=2. Since10 is a3-adic unit, v_L(sigma(beta)−beta)=−8; the conjugate character quotient consequently has conductor5. The script's rational trace witnesses support these reductions. The Eisenstein basis valuation formula is valid because its six basis terms have distinct valuations modulo6.

The explicit principal order and its radical satisfy

\[
(\mathfrak P^r)_{ij}=\pi_F^{\lceil(r+j-i)/3\rceil}\mathcal O_F,
\qquad \mathfrak P^r\cap L=\pi^r\mathcal O_L.
\]

The minimal-stratum formulas give H1=U_L^1 U_A^6 and J1=U_L^1 U_A^5. The character formula agrees on their defining intersection U_L^6: the logarithm error there has valuation at least12, including all denominator effects. Multiplicativity of the deep character follows from beta P^12=P² and tr(P²)⊂p_F. Conjugation by U_L^1 preserves it because it commutes with beta. These checks establish an actual simple character, rather than only a finite model with matching dimensions.

The literal quotient is F3³/diag(F3), with nondegenerate alternating form induced by2B. It has order9, hence eta_F has degree3 by BK5.1.1. Over the unramified quadratic field the same construction gives F9³/diag(F9), order81 and eta_K degree9. These dimensions are different from the dimension3 of the Weil representation after restriction; no whole-carrier identification is permissible.

## 5. The actual quadratic trace is−3

The norm/trace definition makes theta_K invariant under the actual order-two field automorphism tau. Uniqueness of eta_K therefore makes eta_K stable. Its action factors through the finite3-group J_K^1/U_(A_K)^11. Fixed cosets lift: in the additive lattice j_K=pi O_M+P_K^5, average x with tau(x), dividing by2. This stays in the integral lattice and preserves the coset modulo P_K^11. Thus the fixed finite group is the image of the actual J_F^1.

The restriction of eta_K to J_F^1 is three copies of the unique degree3 representation containing theta_F². For precise source typing, theta_F² is itself a minimal simple character for parameter2beta, with the same groups. BK5.1.1 applies directly. Its multiplicity3 is odd, so A2.2 identifies it as the Glauberman correspondent.

A2.3 supplies the determinant-one extension, and A2.4 gives trace±3 at tau. An involution in dimension9 with trace+3 has three negative eigenvalues, so its determinant is−1. Determinant one forces trace−3, with positive/negative eigenspace dimensions3/6. This argument concerns the actual arithmetic representation. Applied to the explicitly constructed norm lift of the corrected theta', the same proof uses (theta')² as its fixed character and gives the same trace. It does not assume a comparison with a Schrödinger model or identify the original Paper XI kappa.

## 6. Independent reconstruction of the central scalar

The self-twist computation uses

\[
g=1+\operatorname{diag}(0,1,2)\Pi^4,
\quad h=g^{-1}\Pi g\Pi^{-1},
\quad u_i=1+D_i\Pi^5\ (i=0,1).
\]

I independently computed h using the exact matrix algebra, then used its **first column**, rather than the author's greedy digit procedure, to define the field element ell=h(1). In the rational basis1,pi,...,pi^5 this is

\[
\ell=1+\frac{-84474\pi-186945\pi^2-189810\pi^3
                    -91756\pi^4-16836\pi^5}{2593}.
\]

The exact results are v_L(ell−1)=4 and mult(ell)^(-1)h∈U_A^8. This provides an independent actual H1 decomposition. Evaluating the character with this decomposition, using 36 logarithm terms instead of26, gives:

| Unit-character coefficient | theta_a(h), as an exponent modulo1 |
|---|---|
| beta | 1/3 |
| beta+pi^(-8) | 0 |
| beta+2pi^(-8) | 2/3 |

The deep matrix character remains psi_beta in all three rows. Thus these are different unit-character extensions of the same deep character, not silently changed strata. The common tail bound makes both finite logarithm truncations exact for the displayed phases.

A second direct calculation gives g^(-1)u_i g u_i^(-1)∈U_A^9 with theta_a-value1 for both i and all three corrections. The cubic norm character has value1 on det(u_i). Therefore the eta-level intertwiner may be the identity. Every other such intertwiner is scalar by irreducibility; equivalently, a matrix commuting with both the actual shift and clock generators is scalar.

This avoids the possible error of inferring uniqueness from a search through only nine Weyl matrices. The scalar at the uniformizer does not depend on the chosen Pi-operator S: eta_a(h) is already scalar, and every eta-level intertwiner is scalar. In the report's convention theta^g(x)=theta(g^(-1)xg),

\[
\Lambda^g(\Pi)=\eta_a(h)\Lambda(\Pi),
\qquad \omega_{\rm cub}(\det\Pi)=\omega_{\rm cub}(\pi_F)=1.
\]

Hence the remaining scalar is exactly theta_a(h), for **every** central-type extension Lambda. Rescaling Lambda(Pi) cannot change it.

## 7. Source-qualified exclusion and its limit

BK3.3.2 gives I_G(theta)=L×J1 for this full-degree minimal stratum. The group N=L×J1 is normalized by g: g normalizes J1, it fixes the central−1, and g^(-1)Pi g=h Pi with h∈H1. BH1999§3.1 Lemmas3–5 and the compact-induction classification, also displayed explicitly in BH1996's proof of14.3, account for the actual central-type extensions and their induced supercuspidals.

For the original theta, Lambda^g and Lambda⊗omega_cub agree on J1 but differ at Pi by zeta3. They are therefore inequivalent on N. They share the same H1-character theta^g, so any possible global intertwiner lies in I_G(theta^g)=N. This rules out all additional intertwining cosets; an inner conjugation from N cannot repair the failed equivalence. The compact-induction criterion then excludes the cubic self-twist for every theta-containing supercuspidal. AI_(L/F)(chi) has that self-twist because omega_cub is trivial on L/F norms. The original theta occurrence is consequently zero.

BK's displayed conjugation convention is opposite to the report's. The preceding argument compares the two representations with the **same** H1-character and uses the inversion-stable self-intertwining subgroup N, so it does not depend on calling the cross-intertwining coset gN or g^(-1)N. This orientation check is material.

The corrected theta' has scalar1. The identities on J1,Pi and central−1 now give the full central-type self-twist. This is a real correction through the actual type. It remains insufficient to identify which inducing character under cyclic automorphic induction corresponds to that type, or which of the three central-type extensions with fixed central character is AI(chi).

## 8. Central compatibility of the correction

Let nu(u)=psi_L(pi^(-8)log u) on U_L^1. It has conductor5, hence is trivial on the deep intersection U_L^6. Thus replacing chi by chi nu on U_L^1 yields another actual simple character in C(A,0,beta).

The corrected character retains compatibility with the original central character. Since U_F^1=mu3 U_F^2, logarithm kills mu3 and log(U_F^2)⊂p_L^6. Multiplication by pi^(-8) leaves p_L^(-2), inside p_L^(-3), an ideal on which psi_L is trivial. Hence nu is trivial on U_F^1.

The independent first-column calculation also checked the separate uniformizer normalization. The ratio pi_F/pi³ belongs to U_L^4 and has nu-value zeta3². Taking nu(pi)=1 would therefore give the wrong value on pi_F. Taking instead nu(pi)=zeta9 and nu(−1)=1 gives nu(pi_F)=zeta9³ zeta3²=1 and hence nu restricted to F× is trivial. This changes no unit-character value in theta'.

Only the three displayed powers of this particular conductor-five correction were tested. Neither the computation nor this audit establishes a unique or canonical correction among all admissible unit characters.

## 9. Execution evidence and remaining task

The cyclotomic script was replayed with Python 3.12.14 and all 16 checks passed. Its stdout SHA256 was `88a5a7d72aa2189f09a330fee3f01dc48767687c1e37f2f301a81557635fece9`.

The final self-twist script replay passed its three norm-kernel generators and six unit-generator checks, in about 2.21 seconds. Its stdout SHA256 was `be9bdf653164a04caca99748285ef97eea9a5ddeac527820d0881e74b8514405`. The final central script at coefficient 0 passed in about 5.71 seconds, stdout SHA256 `69ebea13fbed209cc1b10b2982b7e6f051295acffecbe94f52175567a6ab6bfb`. The independent decomposition above checked all three scalar values separately, without calling the central script's eta or S constructors.

The lattice script was replayed into a temporary directory to preserve the authoritative result. Its result was byte-identical to the stored JSON, SHA256 `ca452086c979ee07afac04ed7c2db382dd1800a59473426f78e5ad01fcc16c91`. It checked all 531441 ordered F9³ pairs, the radicals, quotient orders and fixed quotient. Runtime was about 5.38 seconds. These are finite checks for one specified arithmetic instance; the reductions in the reports supply their mathematical interpretation.

The narrow next task is to identify the inducing L-character and central-type extension for the corrected theta', or directly evaluate the theta' occurrence in the **same** AI_(L/F)(chi). The necessary cubic self-twist now passes, but it does not prove that identification. Original Claim16.2, its original packet/kappa and its unchanged H5 are not resolved by substituting the corrected theta'.
