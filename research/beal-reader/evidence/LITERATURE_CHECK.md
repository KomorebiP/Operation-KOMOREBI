# Beal Series 05 literature check

Checked 8 October 2026 in America/Chicago, with retrievals on 9 October UTC. This review authenticates external statements, versions, notation translations and their stated applications. It does not independently reprove the imported deep theorems. It does not certify that the actual Frey representation satisfies the project's inherited hypotheses.

The release records are `LITERATURE_SOURCE_MANIFEST.json`, `LITERATURE_LEAF_MANIFEST.json`, `LITERATURE_BIBLIOGRAPHY.tex`, `LITERATURE_ACQUISITION_RECORDS.json` and `LITERATURE_ACQUISITION_FAILURES.json`. Full external PDFs, extracted text, page images and the local source cache are private in `literature/` and must be excluded from the release. Historical source files were not edited.

## Outcome and trust boundary

The exact finite-S Poitou–Tate statement required by Block80 was located and read in Milne's second edition. The ordinary and cyclotomic coefficient modules were distinguished. Local Artin normalization, principal idele reciprocity, toric Kummer extension statements, universal period constant factors and the relevant lattice statements were checked at the leaves listed in the manifest.

The accepted implication is conditional: for continuous framed residual cocycles on the stipulated restricted group, if the specified local triviality and dual Sha vanishing hypotheses hold, the ordinary cup obstruction has a continuous primitive on that same group. The source theorem does not supply the actual residual cocycles, their framing, the geometric origin of the local affine sets, or a common family realization. First-stage affine membership, a compatible higher lift and the Diophantine contradiction remain separate obligations.

## Beal, Fermat and abc

Mauldin's 1997 AMS PDF returned 403. The published Czech translation of that article was acquired from DML and its statement read at printed page104. For positive integers A,B,C,x,y,z with x,y,z>2, Beal asserts that A^x+B^y=C^z entails a nontrivial common divisor. The AMS council record corroborates the common-prime wording through indexing, but its full PDF also returned403. The indexed council record is not presented as a fully inspected source.

For the unit-coefficient equation, a prime dividing two bases divides the third. Consequently gcd(A,B,C)=1 is equivalent to pairwise coprimality for a solution. If all three exponents have a common divisor n>2, replacing bases by the appropriate powers reduces to Fermat's Last Theorem. Official Annals records authenticate the Wiles and Taylor–Wiles bibliographic entries. The deep FLT proof is accepted as a classical input and was not replayed here.

Mihăilescu's full 2004 publisher PDF was not acquired. Both publisher URLs returned202 with empty responses. His own 2005 EMS publisher abstract states the unique consecutive-power solution. Full Bilu2005 was acquired and printed page69 states the odd-prime theorem and the complete positive formulation: x,y,u,v>1 admit only 3²−2³=1. This validates the base-one disposal for Beal exponents>2. It is a statement-level authentication with a published proof exposition, not a new audit of Mihăilescu's deep argument.

Darmon–Granville Theorem2, printed page515, fixes both the nonzero integer coefficients and the exponents. Its hyperbolic condition is 1/p+1/q+1/r<1. It proves finiteness of proper integer solutions, which here means gcd(x,y,z)=1. Positive pairwise-coprime Beal triples fit. Over number fields the source's properness and equivalence include ideal and unit data, so literal finite-coordinate language must not be transferred unchanged.

The assumed abc form is:

\[
\forall\varepsilon>0\ \exists K_\varepsilon>0\ \forall(a,b,c),\quad
 a+b=c,\ a,b,c>0,\ \gcd(a,b)=1
 \implies c\le K_\varepsilon\operatorname{rad}(abc)^{1+\varepsilon}.
\]

Darmon–Granville Section5.2, printed pages532–533, derives Fermat–Catalan finiteness for triples of powers from this conjectural estimate. The page533 formula was inspected as an image because the extracted exponent was corrupted. Its bound uses epsilon1/83 and the maximal hyperbolic reciprocal sum41/42, giving a largest powered term bounded by K_(1/83)^83. This is finiteness, not absence of exceptions.

For the Beal-only exponent region, excluding (3,3,3), order the exponents and obtain a uniform reciprocal sum at most11/12. Setting epsilon1/22 gives

\[
Z\le K_{1/22}Z^{(11/12)(23/22)}
 =K_{1/22}Z^{253/264},\qquad
Z^{1/24}\le K_{1/22},\qquad Z\le K_{1/22}^{24}.
\]

This inequality is a project derivation from the cited abc formulation. It is conditional on abc and counts powered triples. Unit bases may have infinitely many labelled exponent descriptions. None of these statements is a proof of full Beal.

## The actual signature branch and the modular input

Dahmen–Siksek's July2024 author working paper was acquired. Theorem1, printed page1, gives the exact branch dichotomy for nonzero primitive X⁵+Y³=Z⁷: either30 divides Z and7 does not divide XY, or Z is odd,3 does not divide XYZ,5 does not divide YZ and7 divides Y. Its long descent and enumeration are imported, not freshly replayed by this literature pass.

Pacetti–Villagra Torcomian arXiv:2512.17845v1 was acquired. Its equation(32), printed page28, realizes the plus family by y²=5x⁶−12x⁵+10tx³+t². This source supports the family construction it states. A transformation to the historical project model, its twist, stable model, residual lattice and framing require project proofs.

Corollary7.7, printed page31, assumes an auxiliary prime ell not dividing b and residual prime p>C(ell). In particular C(2)=13. The proof's resultant6084 and the observation7 does not divide6084 do not on their own verify every hypothesis of the small-prime argument. Theorem7.8, printed page32, starts with residual irreducibility before invoking the Hilbert modular newform and level conclusion. TheoremA excludes a prime set containing7. TheoremC additionally assumes a large-image conjecture. These leaves cannot be cited as an unconditional resolution of characteristic7.

The recovered files `pv_MagmaCode.m`, `pv_GPcode.gp` and `pv_Data.txt` are by Pacetti and Villagra Torcomian. The abbreviation is not Pohst–Vieta. Their headers and the authors' repository identify their role in this paper's computations. No explicit license was found in the recovered file headers or the repository listing. Their historical inclusion is provenance, not evidence that this release freshly reran their calculations. Parent release policy governs preservation of the original historical code/data. Full external articles remain excluded.

A search also found and acquired Peter Chocian's arXiv:2609.26996v1, submitted22September2026, which claims a computer-assisted proof for(3,5,7). The main claim and date were read. Its proof, dependencies and certificate archive were not audited, and it is not used as an accepted theorem. This finding prevents a literature-wide claim that no recent resolution has been proposed. The present project may accurately state its own remaining obligations.

## Finite-S duality and ordinary coefficients

Milne ADT I.4 uses a nonempty set S containing archimedean places. TheoremI.4.10 requires a finite G_S-module whose order is a unit in R_K,S. The project finite Sigma contains the primes over7 and therefore meets the invertibility condition for its7-primary modules. The theorem's Sha¹(M)–Sha²(M^D) pairing and degree1 exact image/annihilator assertion were read on printed pages56–57 and the diagram visually inspected. I.2 Corollary2.3 supplies local duality. I.5 supplies the finite-S Euler characteristic and H² sequence. At odd order, the modified real Tate terms vanish.

For trivial k=F49, the Cartier dual is k(chi), not trivial k. Choose a generator of μ7 and use the nondegenerate trace pairing Tr_(F49/F7)(xy) to identify Hom_(F7)(k,μ7) with k(chi). Exchanging dual modules in TheoremI.4.10 then pairs Sha²_S(k) with Sha¹_S(k(chi)). This translation is mathematical work in the project, not a license to forget twists elsewhere.

The project proposes an arithmetic proof of Sha¹_S(μ7)=0. Its needed ingredients are class number1 of K=Q(sqrt5), units±phi^Z, the full Sigma-unit basis, and the fact that phi is not a seventh power at the unramified quadratic7-adic place. Milne ANT Theorem4.3 gives the class-number conclusion from the Minkowski bound sqrt5/2<2. Unit and S-unit rank statements are authenticated, but identifying the generators and the local phi calculation requires direct project checks. The displayed normalized residue (phi^48−1)/7≡5sqrt5 mod7 is nonzero. The literature theorem alone does not establish this calculation.

With those arithmetic checks and the actual alpha,beta hypotheses accepted, alpha is pointwise zero at beta-support places. At fixed places either beta is a coboundary or the relevant ordinary H² vanishes. The cup class is locally zero, finite-S H² localization is injective, and the restricted primitive follows. An absolute Brauer localization theorem would give an absolute primitive but no control of ramification, so it cannot replace this argument.

## Reciprocity, conductor coordinates and twists

Milne CFT fixes arithmetic Frobenius. Its local Artin norm and transfer diagrams are stated in III.3.2, uniformizer normalization in I.1.1 and III.3.4, principal idele reciprocity in V.5.3(a), and the ray exact sequence in V.1.7. The local norm-diagram proof is marked to be added in the notes. This review authenticates the classical statement rather than pretending the missing exposition was read.

The ordinary difference z=p−p0 is classified through ordinary global H¹. The project has24 local ordinary coordinates and14 independent principal Sigma-unit relations, with completeness justified by finite-S duality and the class-group calculation. Necessity of principal relations by itself does not prove completeness of an arbitrary truncated matrix.

The inverse-cyclotomic beta descent is a distinct input. An ordinary conductor matrix cannot classify beta merely because both use Artin symbols. Over an unramified quadratic local extension, norm(q)=q² and arithmetic Frobenius transfers accordingly. At q≡−1 mod7 the inverse-cyclotomic factor1+chi^-1 makes the transferred unramified value zero. These are compatible normalizations, not proofs that the actual beta has the proposed global descent.

The self-conductor unit pi_q/q must be retained. A principal generator's norm identity supplies the self-unit relation in addition to off-place logarithms. Omitting it changes the diagonal conductor term. Source reciprocity supports the norm identity, while the project's embedding weights, residual values and sign conventions need their own exact checks.

Milne CFT III.4.4 and Remark4.5 require μ_n in the local field for the Hilbert/Kummer identification. K itself has no μ7. Over K(ζ7), the degree6 extension and restriction/corestriction can compare ordinary absolute H² with Brauer7. VIII.4.2 then gives global Brauer localization. None of this enlarges finite-S hypotheses for free.

Masley's1976 Main Theorem and table, printed page179, were read as an image. They give h(Q(ζ35))=1. For L=Q(sqrt5,ζ7), its index2 extension inside Q(ζ35) kills no nonzero7-primary ideal class, so Cl(L)[7]=0. This conclusion does not eliminate inverse-cyclotomic ramification or exhaust all conductors.

## Geometry and lattice statements

Mumford1972 Theorems3.3 and4.20 give the graph and Schottky statements under the source's split degenerate stable-fiber hypotheses. Ichikawa1993 is **The universal periods of curves and the Schottky problem**. Its Sections1.2 and2.6–2.7, Proposition2.4 and Corollary2.5 were inspected, with formula pages viewed as images. For a valid marked specialization, the off-diagonal actual period has the paired cross-ratio constant factor and corrections of positive order. The period divided by its constant factor instead has constant1.

The historical stable-fiber branch calculations and the value −phi^-4 can therefore feed this theorem only after their actual model and marking hypotheses are established. Node thickness controls valuation terms. It does not by itself identify all unit residues or certify the global Frey model.

Gregory–Liedtke Section4.4 equation(7) and Lemma4.9 identify toric Tate-module extensions with period Kummer images. The whole natural torsion module must be rational to force all period coordinates to be the relevant powers. Rational semisimplification is weaker. Prime-to-residue principal units are uniquely seventh-divisible, while7-adic principal units are not automatically so. Baker–Rabinoff Theorem2.9 and Remark6.7 identify monodromy valuation with the metric graph pairing, not all period residues.

Dolgachev–Lehavi Corollary2.2 was reused from the authorized historical source copy. It gives a geometric principal polarization after quotient by a maximal isotropic subgroup, with torsion order prime to characteristic. It does not assert that the quotient remains the same Diophantine family, and descent over K is a separate point. Ophir–Weiss Theorems1.2–1.3 and Lemma2.3 authenticate the stable-lattice geometry but warn against automatically realizing a prescribed character orientation at full depth when residual characters coincide.

Galbraith's extended version2.0 Chapter10 gives the exact Cantor composition, reduction and unique reduced representative statements used for finite divisor certificates. The source permits nonmonic F. This authenticates the algorithmic interpretation, not the origin of the tested global curve.

## Massey and deformation scope

Mináč–Tân2016 arXiv:1412.7611v3 Theorem1.2 (=4.15), printed page2, is the any-field, any-prime theorem with trivial F_p coefficients. The separate2017 JEMS Theorem1.2 is the mod2 result. Both are absolute-group vanishing assertions that choose some defining system.

Maire–Mináč–Ramakrishna–Tân2026 Theorem1.1 applies to number fields without ζ_p, odd p, and n≥3 for absolute and maximal tame groups. Its Remark1.1 explicitly permits newly ramified tame primes. Some prescribed defining systems can fail while another lifts. Theorem1.2 supplies the stated finite-depth lifts with additional choices. It does not furnish a fixed-Sigma, fixed-affine, compatibly framed tower or an integral Frey realization. The project therefore cannot close its secondary obstruction by citing these broad vanishing results.

Local maximal pro-p freeness without μ_p was located only as a recalled theorem in Chebolu–Mináč's2009 research survey. An original primary proof was not authenticated in this pass. It remains contextual and nonload-bearing.

## Unrestricted localization and its finite-set refinement

Neukirch's original1973 published paper was acquired through the GDZ digitized volume. Korollar6.4(c), printedpage90, was read directly as an image. For a finite absolute Galois module A over a number field, define its Cartier dual A′=Hom(A,μ) and the finite group G′ cut out by the dual action. The criterion H¹(G′,A′)=0 implies surjectivity of H¹(K,A) onto the product of H¹(K_v,A) over any finite set of places. The digitized source is scanned; only the required leaf has partial OCR, and the formulas were authenticated visually.

For the additive module k=F49 with trivial action, A′=k(χ), the dual field is K(ζ7), and G′=C6. Averaging gives vanishing since6 is invertible on7-primary coefficients. For A=k(χ), the dual action cancels and G′ is trivial. The unrestricted matching conclusions in the reader therefore follow. They neither prescribe a finite global ramification set nor construct an integral Frey representation.

Neftin's author manuscript reproduces the criterion in Theorem2.1(c), printedpage4. Corollary2.3, printedpage6, allows a further disjoint finite set T to be kept unchanged while local data at S are matched, assuming an initial global solution of the embedding problem. Under case(c), applying the surjectivity theorem to S∪T also proves the corresponding cohomological refinement directly. Controlling finite T does not control every prime outside S. The author manuscript and the original published source were both retained privately. The GDZ terms cover accompanies the private article extract; neither source is included in the release.

## Search bounds and acquisition record

The search prioritized the recovered source copy and primary author/publisher/journal repositories. Named-source searches covered Beal/Mauldin, fixed-signature and abc finiteness, Milne duality/class field theory, Mumford and universal periods, toric Kummer extensions, cyclotomic class numbers, lattice geometry and Massey statements. A second search engine verified the blocked Mauldin/Mihăilescu records and located the newer signature claim. The citation graph was followed only as needed for these leaves, including the Pacetti–Villagra electronic resource and the distinction between the two Mináč–Tân papers.

This is a bounded dependency review. It is not an exhaustive worldwide novelty search. Full FLT and Catalan proofs, the complete modular pipeline at7, Putz's Hunter enumeration, Chocian's recent proof and certificates, all geometric family identifications and arbitrary higher obstruction stages were not independently audited here.

The source cache contains24 verified PDF identities. The source manifest additionally records5 sources available only through metadata, publisher statements or accepted classical use. Failed AMS retrievals, both empty Mihăilescu publisher responses, the subscription-blocked EMS chapter, and one supplement acquisition-log indexing mistake are retained in the public acquisition failure metadata. The mistake lost three initial download bookkeeping records, not the acquired PDFs. Their local hashes and text extractions were recomputed, and the missing original HTTP record was not invented.
