# Primary-source contracts for Series 09

Checked 9 October 2026. These are exact external-input contracts, not a global novelty claim or a complete independent reproof of the sources. Full third-party PDFs and extracted text remain outside the distribution.

## Sources

### Milne2022: Fields and Galois Theory

- Author: J. S. Milne
- Version: Kea Books, 2022
- Stable locator: https://www.jmilne.org/math/Books/FT0.pdf
- Private snapshot SHA-256: `ccf970256a2d0468b302b02e150a594c34eb538691fa80360404a330d0b3e779`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `c5000fc0dcdef2d1ba3274d9c9e922ebcfbfee386c4d54d56b8bfa1ba8ca054f`

### SchmidtWingberg1998: Safarevic's theorem on solvable groups as Galois groups

- Author: Alexander Schmidt and Kay Wingberg
- Version: arXiv:math/9809211v1, submitted 17 September 1998
- Stable locator: https://arxiv.org/pdf/math/9809211v1
- Private snapshot SHA-256: `87e03e784815eec69e3d7e973244cd76bac111abd0f46ebbacdc1d4518827029`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `b7a851bd0d327ac24dd7196fb81fed1965c70b133a6268f8e1171c2aaddb78be`

### DebesHarbater2021: Pre-Galois theory

- Author: Pierre Dèbes and David Harbater
- Version: Osaka Journal of Mathematics 58 (2021), 71–101; published author-hosted copy, revised 11 September 2019
- Stable locator: https://pro.univ-lille.fr/fileadmin/user_upload/pages_pros/pierre_debes/A59-DebesHarbater2.pdf
- Private snapshot SHA-256: `2000db902b9a10aa3ed6151e398da808034107a5e8095fbc54f62259386ae7aa`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `c9a3102e2ba505e6a37c88d0a926931edba1c516273f6dc79cdb4b6f75257477`

### Debes2026: Hurwitz spaces and inverse Galois theory

- Author: Pierre Dèbes
- Version: Author manuscript dated 9 April 2026, 27 pages
- Stable locator: https://pro.univ-lille.fr/fileadmin/user_upload/pages_pros/pierre_debes/A67-Nakamura60.pdf
- Private snapshot SHA-256: `fbd50569675a5ff90e4bbf120abccbcdb73330f5458fd8f8a67a8a564095a4d7`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `03402537cddfb46944cef6a323ccd3124b306c18844a949d1f631b961a67a3b2`

### DebesLectureNotes: Arithmétique des revêtements de la droite

- Author: Pierre Dèbes
- Version: Undated 385-page author-hosted snapshot, checked 9 October 2026. Author publications page describes a 2024 work in progress; that is not asserted as this PDF revision date.
- Stable locator: https://pro.univ-lille.fr/fileadmin/user_upload/pages_pros/pierre_debes/V2-ArithRevDte-v3.pdf.pdf
- Private snapshot SHA-256: `fc7aea4a6517256b2ac6cfa19bcddfb3ec490931c6d05b74f1f9486d7fe85a1b`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `99cbed342a46becfc8bbb127dfce67f93b26b761fc4a7971c9979981ff23f8a4`

### HuangEtAl2026: The Mathieu group M23 is a Galois group over Q

- Author: Xiaoyu Huang, Blake Jackson, Kyu-Hwan Lee, Bjorn Poonen, Rachel Pries and Shaowu Zhang
- Version: arXiv:2608.08538v2, submitted 7 October 2026; manuscript date 4 October 2026
- Stable locator: https://arxiv.org/pdf/2608.08538v2
- Private snapshot SHA-256: `7e4da0cffcba34c2ee5d22255daeff62cca8f099e695cac53ef9d85f86be4b0f`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `fb71f700551f74388a66adc61bb2826687d1b11ac695834c7fc276f8dd6ac109`

### ConradCyclotomic: Cyclotomic Extensions

- Author: Keith Conrad
- Version: Undated author-hosted snapshot, checked 9 October 2026
- Stable locator: https://kconrad.math.uconn.edu/blurbs/galoistheory/cyclotomic.pdf
- Private snapshot SHA-256: `2962191954ae1903a827393dd9aeba758e18af65671ee021992bb80fa164ad7a`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `dce09d5e1b681d2e723336476fe155373c502fa944f17b437c41bcfdda2d9dd8`

### ConradPatternsPrimes: Patterns in Primes

- Author: Keith Conrad
- Version: Undated author-hosted snapshot, checked 9 October 2026
- Stable locator: https://kconrad.math.uconn.edu/blurbs/ugradnumthy/prime-patterns-1.pdf
- Private snapshot SHA-256: `15b45606ff0d00eeda437399671eec33a0f32060e02afdaed6bb3f1b22e0a595`
- Extraction: available with pdftotext pdftotext version 24.02.0
- Extracted-text SHA-256: `75ad2e984e02cd9853099180fbb713fd47ab800175a12af16d63015ec725fea3`

## Dependency contracts

### LC01: Rational inverse Galois problem and dated status

- Sources: Debes2026, HuangEtAl2026
- Exact locators: Dèbes2026, Galois preamble, printed p.2; Huang et al. v2, §1.1, printed pp.1–2
- Source status: states open problem
- Result used: For each finite group G, seek a finite Galois field extension L/Q with Gal(L/Q) isomorphic to G. The general assertion remains open in the checked 2026 sources.
- Hypotheses: G is any finite abstract group; base is Q.
- Notation: G = prescribed finite group; L = an actual field, finite over Q
- Project implication: A representation on a vector space, a G-action on a disconnected algebra, or a realization over a larger base is not by itself the requested field extension.
- Classification: Conjectural or explicitly open in a checked source
- Caveat: This is a dated source check, not an exhaustive certification that no subsequent paper exists. The newer v2 status context was inspected on 9 October 2026.

### LC02: Regular realization is a stronger input

- Sources: DebesHarbater2021
- Exact locators: Introduction, printed p.71, zero-based PDF p.0
- Source status: defines and states implication
- Result used: A regular realization over k is a Galois field extension of k(t) in which k is algebraically closed. Over a Hilbertian base it implies an ordinary realization.
- Hypotheses: Finite Galois extension; characteristic zero is the project scope.
- Notation: k = Q in this piece; F = project L/Q(t); regular = L ∩ Qbar = Q
- Project implication: Regularity excludes new algebraic constants; the symbol t is transcendental.
- Classification: Known after translation of notation
- Caveat: An ordinary realization does not furnish a regular one by adjoining a dummy variable. For nontrivial L/Q, L(t)/Q(t) contains L as new constants.
- Caveat: No converse from ordinary to regular realization is asserted.

### LC03: Hilbert specialization with a controlled exceptional locus

- Sources: DebesLectureNotes, HuangEtAl2026
- Exact locators: Dèbes notes, Theorem 2.6.3(a),(d), printed p.85; Remark 2.6.5, p.87; Dèbes notes, Definition 5.2.2 and Theorem 5.2.4, p.206; Proposition 5.2.14, pp.213–214; Huang et al. v2, §1.2, p.2
- Source status: proves theorem and corollary; modern paper states the regular consequence
- Result used: Over Q, a finite Galois extension of Q(t_1,...,t_r) admits specializations retaining G on a Hilbert subset outside a proper Zariski closed exceptional locus. A fixed nonzero constraint polynomial may also be kept nonzero.
- Hypotheses: r ≥ 1; finite Galois field extension; a primitive polynomial for the full extension, not merely for an arbitrary smaller root field; localization avoids coefficients, denominators and discriminant zeros.
- Notation: T = tuple (t_1,...,t_r); P = minimal polynomial of a primitive element of the entire Galois extension; N_t0 = specialized splitting field; Hilbert subset = specializations preserving the declared irreducibilities
- Project implication: The specialized primitive polynomial stays irreducible of degree |G|. Away from the model exceptional locus its splitting-field group embeds into G. Equality of degrees forces the full group. Zariski density permits replacing finitely many nonzero restrictions by their product.
- Classification: Known after translation of notation
- Caveat: Characteristic zero alone is insufficient: Q is Hilbertian by the cited theorem; C is not.
- Caveat: For one parameter the excluded polynomial zero set is finite. In several parameters it is generally an infinite proper hypersurface.
- Caveat: Not every unbranched value retains the full group. Infinitely many suitable values need not, without a separate argument, describe distinct isomorphism classes for a nonregular constant extension.
- Caveat: For a nontrivial regular one-parameter extension, Huang et al. state infinitely many G-extensions over Q. The trivial group is handled separately.
- Caveat: The author lecture notes are a work in progress and have unfinished cross references. The locally pinned numbered statements, rather than dangling references, were used.

### LC04: Shafarevich solvable-group realization

- Sources: SchmidtWingberg1998
- Exact locators: Theorem 1, printed p.1; introduction, pp.1–2
- Source status: proves
- Result used: For a global field k and a finite solvable group G, some finite Galois K/k has Gal(K/k) isomorphic to G.
- Hypotheses: Take k=Q; G finite and solvable.
- Notation: K/k = project L/Q; G(K/k) = Gal(L/Q)
- Project implication: This supplies an external existence theorem for the solvable sector.
- Classification: Known after translation of notation
- Caveat: This theorem does not by itself prescribe arbitrary completions, bound discriminants, give a polynomial algorithm, or prove regular realization over Q(t).
- Caveat: The authors explicitly correct a prime 2 issue in the original Shafarevich argument. The corrected proof source is used rather than treating the 1954 article alone as the extracted complete proof.

### LC05: Every symmetric group is realizable over Q

- Sources: Milne2022
- Exact locators: Theorem 4.28, p.69; Lemma 4.31 and Example 4.32, pp.70–71
- Source status: proves construction
- Result used: Every S_n occurs over Q. Squarefree modular patterns, irreducibility, and an elementary permutation criterion provide a construction.
- Hypotheses: n ≥ 1; n=1 and n=2 are handled separately; for n≥3 use a monic integral polynomial with the required squarefree reductions.
- Notation: G_f = group of the splitting field, not of a single root field; n = number of polynomial roots
- Project implication: The authors may prove their own subgroup criterion. The external arithmetic step is LC08. A full S_n splitting field has degree n!, not n.
- Classification: Known after translation of notation
- Caveat: The source prints 15f_1+10f_2+6f_3 for monic degree-n polynomials. Its leading coefficient is 31. To retain the monic input of Theorem 4.28, use coefficientwise monic CRT or subtract 30X^n. All reductions mod2, mod3, mod5 are unchanged by that subtraction.
- Caveat: Repeated low-degree factors must be excluded when making modular patterns.

### LC06: Cyclotomic Galois group

- Sources: ConradCyclotomic
- Exact locators: Theorems 1.1, 2.3, 2.5, printed pp.1–4
- Source status: proves
- Result used: Gal(Q(ζ_N)/Q) is (Z/NZ)^× through σ(ζ_N)=ζ_N^a. Finite multiplicative subgroups of a field are cyclic.
- Hypotheses: N ≥ 1; ζ_N primitive. For the arbitrary-base injection, the characteristic must not divide N.
- Notation: μ_N = all Nth roots of unity; ζ_N = a chosen primitive root; a = a unit residue class modN
- Project implication: For prime p the cyclotomic group is cyclic of order p−1.
- Classification: Known after translation of notation
- Caveat: For arbitrary K the exponent map may be a proper subgroup of the unit group. The isomorphism here is specifically over Q.
- Caveat: Exponentiation describes the automorphism on roots of unity, not on every field element.

### LC07: Cyclic fixed-field construction

- Sources: ConradCyclotomic, ConradPatternsPrimes, Milne2022
- Exact locators: Conrad Patterns in Primes, Theorem 2.4, printed p.2; Conrad Cyclotomic Extensions, Theorem 2.5, p.4; Milne, Theorem 3.17(d), pp.47–48
- Source status: states Dirichlet; proves algebraic inputs
- Result used: For m>1, choose a prime p≡1 modm and let H be the subgroup of order (p−1)/m in Gal(Q(ζ_p)/Q). Its fixed field has group C_m.
- Hypotheses: m is a positive integer; take Q for m=1.
- Notation: m = target group order; p = cyclotomic conductor, which need not equal m; H = kernel of the cyclic quotient of order m
- Project implication: The quotient computation and normality of H are elementary project deductions.
- Classification: Formal corollary not stated
- Caveat: Dirichlet is stated, not proved, in the author notes. No effective search bound follows. The piece can use only C2/C3 examples without importing this general prime existence step.
- Caveat: An optional elementary Φ_m(m) construction and a Gaussian period generator are recorded in classical_constructions_check.json. They are optional and not dependencies of the manuscript unless written out and audited.

### LC08: Good-prime factor degrees give a cycle

- Sources: Milne2022
- Exact locators: Theorem 4.28, printed p.69, zero-based PDF p.78
- Source status: proves
- Result used: For monic f∈Z[X] and prime p with squarefree reduction, its distinct irreducible factor degrees modulo p are the cycle lengths of some element of Gal(f/Q).
- Hypotheses: Monic integral polynomial; p does not divide disc(f), equivalently the reduction has simple roots.
- Notation: f_bar = reduction modulo p; m_i = degrees of distinct irreducible factors; G_f = permutations of roots in the characteristic-zero splitting field
- Project implication: For x^4−x−1, the independent exact computation must verify the mod2 and mod7 factorizations and squarefreeness before supplying 4-cycle and 3+1-cycle witnesses. The theorem is the bridge from those finite factorizations to the characteristic-zero group.
- Classification: Known after translation of notation
- Caveat: Finite modular data alone does not prove the bridge.
- Caveat: A cycle witness gives an element in the actual Galois group, not every permutation having the same cycle shape.

### LC09: Irreducible cubic discriminant classification over Q

- Sources: Milne2022
- Exact locators: Corollary 4.2, p.58; Proposition 4.5, p.59; Example 4.7, p.60
- Source status: proves criteria and example
- Result used: An irreducible cubic over Q has group A_3≅C_3 if its discriminant is a square, and S_3 otherwise.
- Hypotheses: Cubic irreducible over Q, hence separable; discriminant is nonzero.
- Notation: D(f) = disc(f); G_f = splitting-field group acting transitively on three roots
- Project implication: Irreducibility and the exact discriminant must be separately established for each worked cubic.
- Classification: Known after translation of notation
- Caveat: Corollary 4.2 requires characteristic ≠2. Example 4.7 prints characteristic ≠3, which is insufficient for its square criterion in characteristic2. The project uses Q only, so both exclusions hold.

### LC10: Artin finite automorphism fixed-field theorem

- Sources: Milne2022
- Exact locators: Corollary 3.11, printed pp.45–46; underlying Theorem 3.4 and Corollary 3.5, pp.42–43
- Source status: proves
- Result used: For a finite subgroup G⊂Aut(E) of a field, E/E^G is finite Galois with group G and degree |G|.
- Hypotheses: E is a field; the given action is faithful, so G is actually embedded in Aut(E).
- Notation: E = Q(x_g : g∈G); g(x_h) = x_(gh); E^G = invariant field
- Project implication: Permutation of algebraically independent variables induces distinct Q-automorphisms. This proves realization over the invariant field.
- Classification: Known after translation of notation
- Caveat: It does not prove E^G=Q or E^G purely transcendental. A unitary representation alone supplies no field multiplication.

### LC11: Ordinary Galois correspondence

- Sources: Milne2022
- Exact locators: Theorem 3.17, printed pp.47–48; Remark 3.18, p.48
- Source status: proves
- Result used: For finite Galois E/F, H↦E^H reverses subgroup inclusion. Normal H gives Gal(E^H/F)≅G/H.
- Hypotheses: The ambient field extension is already finite Galois.
- Notation: H = subgroup of G=Gal(E/F); E^H = fixed intermediate field
- Project implication: Intersection and compositum translations used in the packet lattice are deductions from this correspondence.
- Classification: Known after translation of notation
- Caveat: The finite-dimensional projector range can represent the fixed vector space. Multiplication and the ambient Galois field still need to be supplied to identify it with a fixed field.

### LC12: Finite normal basis theorem

- Sources: Milne2022
- Exact locators: Definition 5.17 and Theorem 5.18, printed pp.86–90
- Source status: proves
- Result used: A finite Galois E/F has a basis consisting of the G-conjugates of one element.
- Hypotheses: Finite Galois extension; the source uses finite in Definition 3.9.
- Notation: α = normal-basis generator; F[G]→E = Σ a_g g ↦ Σ a_g g(α)
- Project implication: This gives an equivariant F-vector-space isomorphism with the regular module.
- Classification: Known after translation of notation
- Caveat: The isomorphism is not an algebra isomorphism with the group algebra. Transported field multiplication depends on the chosen field and normal basis. No field is created from a regular module by this theorem.

### LC13: Field trace, norm and towers

- Sources: Milne2022
- Exact locators: Remark 5.47, printed pp.107–108; Proposition 5.48, p.108
- Source status: proves for separable extensions; leaves inseparable tower case as exercise
- Result used: In a finite Galois extension, trace is Σ_g g(x), norm is ∏_g g(x). Both compose through intermediate field towers.
- Hypotheses: Finite separable extension for the project; finite Galois where the sum/product is over the full group.
- Notation: L/E/K = project field tower; P_H = normalized subgroup averaging
- Project implication: In characteristic zero, P_H(x)=Tr_(L/L^H)(x)/|H|. The norm is multiplicative and nonlinear as a map of vector spaces.
- Classification: Known after translation of notation
- Caveat: A normalized projector is the trace divided by group order, not the unnormalized trace. Do not assert norm is a linear transfer.
- Caveat: In positive characteristic dividing |H| the normalized formula is not available.

### LC14: Fresh M23 context

- Sources: HuangEtAl2026
- Exact locators: Theorems 1.1 and 1.3, printed pp.1–2, v2
- Source status: proves in author preprint
- Result used: The v2 preprint gives M23 over Q and a regular M23 realization over Q(t). It still describes the unrestricted problem as unresolved.
- Hypotheses: One specified finite group. Version v2, not the older v1, is the inspected copy.
- Notation: M23 = Mathieu sporadic simple group
- Project implication: Use only as dated literature context. It is not a dependency of the project’s elementary constructions.
- Classification: Known after translation of notation
- Caveat: The project has not rerun the preprint’s Magma certification or independently audited its Belyi-map computations. The preprint status is explicit.
- Caveat: Do not repeat older claims that M23 is still the outstanding sporadic case.

### LC15: Noether rationality is sufficient, not automatic

- Sources: DebesLectureNotes, Milne2022
- Exact locators: Dèbes notes, §5.5.1.2, printed pp.221–222; Milne, Aside 5.41, printed p.104
- Source status: states strategy and reports negative background
- Result used: If Q(x_g)^G is purely transcendental over Q, the finite Galois invariant-field extension can be Hilbert-specialized to realize G over Q.
- Hypotheses: Faithful field action as in LC10; an actual Q-field rational parametrization of the invariant field; finite number of parameters.
- Notation: F^G≅Q(t_1,...,t_r) = the missing rationality input; Noether route = LC10 followed by LC03
- Project implication: Transport the finite Galois extension across the rational field isomorphism and apply LC03.
- Classification: Formal corollary not stated
- Caveat: Milne’s Aside 5.41 reports Swan’s 1969 negative example for the cyclic group of order 47. That report is background only: the project has not independently audited Swan’s paper or proof, and the negative example is not a proof dependency.
- Caveat: Failure of that sufficient rationality route does not refute inverse Galois realizability of the group.
- Caveat: The manuscript does not use this source to claim every invariant field is rational or that a representation repair proves the missing rationality hypothesis.

### LC16: Continuous finite quotients of the absolute Galois group

- Sources: Milne2022
- Exact locators: Proposition 7.7, printed p.123; Theorem 7.13, statement on printed pp.125–126, especially (b) and (d)
- Source status: proves
- Result used: Restriction Gal(Ω/F)→Gal(L/F) is a continuous surjection when L/F is a finite Galois intermediate extension. A continuous homomorphism q:Gal(Ω/F)→E to a finite discrete group has an open normal kernel H; M=Ω^H is finite Galois over F and Gal(M/F)≅Gal(Ω/F)/H≅im(q).
- Hypotheses: Ω/F is Galois and carries the Krull topology; E is finite with the discrete topology; q is a continuous group homomorphism. For the project take F=Q and Ω=Qbar.
- Notation: Ω/F = Qbar/Q; q = the proposed lift to the finite group E; H=ker(q) = open normal subgroup; M=Ω^H = finite Galois field supplied by the correspondence
- Project implication: Chapter 6 has a continuous lift q with π∘q=ρ, where ρ is restriction to L. Then ker(q)⊆ker(ρ), so the order-reversing correspondence gives L⊆M. For a surjective lift, the identified group is E, and restriction to L becomes π; its kernel gives Gal(M/L)≅ker(π). The weak case supplies im(q), not necessarily E.
- Classification: Formal corollary not stated
- Caveat: An abstract homomorphism is insufficient without continuity. Openness follows from the finite discrete target and continuity, while normality follows from being a kernel.
- Caveat: This correspondence turns an already constructed continuous quotient into a finite field. It does not prove a proper lift exists for every embedding problem.
- Caveat: The first isomorphism theorem and the kernel inclusion are elementary project deductions, rather than extra existence theorems.

### LC17: Primitive elements for finite characteristic-zero realizations

- Sources: Milne2022
- Exact locators: Theorem 5.1, printed p.78; Remark 5.2, pp.78–79
- Source status: proves
- Result used: If E=F[α_1,...,α_r] is finite over F and α_2,...,α_r are separable over F, then E=F[γ] for some γ. In particular every finite separable field extension has a primitive element.
- Hypotheses: Finite field extension, with a finite generating list satisfying the separability condition; all algebraic generators are separable in characteristic zero. The project uses a finite Galois extension of Q.
- Notation: E/F = the existing realization L/Q; γ = the primitive element used in the polynomial certificate; Q[γ] = the whole extension, not merely a subfield
- Project implication: The degree of the minimal polynomial of γ is [L:Q]=|G| for an existing G-realization. The power basis 1,γ,...,γ^(|G|−1) gives a unique rational expression for each automorphism image of γ, so the certificate format in Chapter 7 can encode any existing realization. These degree and basis assertions are the project’s elementary consequences of the source theorem.
- Classification: Formal corollary not stated
- Caveat: Existence of a primitive element for an already given finite separable extension is not a procedure to construct a realization of an arbitrary group.
- Caveat: No claim is made that a generator of an arbitrary smaller root field generates the full splitting field.
- Caveat: The source theorem is slightly stronger than the separable special case: its first generator need not be separable. Only the characteristic-zero special case is used.

## Search boundary and failures

This check used two search engines, official author publication pages, original versioned preprints and author books. A second agent independently checked the classical symmetric and cyclotomic constructions. It did not search or certify every possible group realization or the novelty of project results.

The exact queries, citation graph and acquisition diagnostics are in `search_diagnostics.json`. All substantive theorem dependencies above have an authenticated readable source. The unavailable Harbater copy was replaced by the published author-hosted Dèbes copy. The source-cache ingestion problem was resolved in a private cache root. No failed fetch is treated as evidence of theorem absence.

The local source hash pins an inspected snapshot. It does not turn an external theorem into a theorem proved by this project.
