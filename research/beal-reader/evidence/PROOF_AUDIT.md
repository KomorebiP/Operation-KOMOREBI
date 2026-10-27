# Independent mathematical audit of the Beal reader edition

Audit date: 9 October 2026 (UTC). Publication attribution requested by the project: Komorebi P., 8 October 2026. Review kind: **internal independent agent**, not an external referee. This audit reconstructed the arguments independently of the reader-edition author's conclusions. Historical sources were read without editing them. Separate agents remain capable of sharing model errors; agreement alone is not mathematical evidence.

## Normalized target and primary verdict

The audited target is a restricted, first-stage deformation problem, not Beal's conjecture. Fix the field, coefficient modules, residual cocycles, common frame, triangular reference, complete beta support, and inherited local geometric conditions below. The restricted cup equation has a continuous global primitive. The first-stage fixed-local and toric conditions on that primitive are solvable exactly when a particular class in the cokernel of the computed localization operator vanishes. That arithmetic class is not evaluated in the supplied work.

**Primary verdict: conditional on the named inherited arithmetic inputs H1–H6 of the Block79 target contract, together with the stipulated complete-support and rational-descent data.** The conditional cohomological implication, local cochain identities, ordinary localization presentation, and affine criterion check correctly. The finite rank data apply to the four frozen supports. No proof establishes that a residual candidate is realized by a global Frey object, that its affine obstruction vanishes or is nonzero, that its upper-stage lift exists, or that all primitive Beal signatures reduce to this regime.

Final mathematical review status: **math_passed_for_stated_scope**. All 25 new reader chapters, the paper and guide entry sources, both shared preambles, all 24 guide diagrams' labels and exact data, and the specifically named companion evidence reports were reviewed at the frozen revision recorded in `evidence/REVIEW_PINS.json`. No critical correctness defect remains in the statements at that scope. This verdict does not convert the explicitly unproved research obligations into conclusions. Full-page layout is a separate parent-agent review.

The missing implication required for a pattern exclusion is an authenticated computation or proof of nonvanishing of the **actual** arithmetic target class. A homogeneous kernel dimension, synthetic evaluator target, pointwise finite-field identity, or local matrix packet cannot supply that implication.

## Exact object and convention card

* Base field: `K = Q(sqrt(5))`, `phi = (1+sqrt(5))/2` in K.
* Coefficient ring: `O = Z_7[w]/(w^2-5)`; residue field `k=F_49`; depth-one ring `R=O/49`. The coefficient symbol w is not the base-field element sqrt(5).
* Chi denotes the cyclotomic character, with its R-valued or k-valued reduction specified by the equation in use. The action on k(chi) is multiplication by chi; on k(chi^-1) it is multiplication by chi^-1; on k it is trivial.
* Fix normalized, continuous **cocycle representatives**, not only their cohomology classes: `alpha in Z^1(G_Sigma,k(chi))`, `beta in Z^1(G_Sigma,k(chi^-1))`. Their laws are `alpha(gh)=alpha(g)+chi(g)alpha(h)` and `beta(gh)=beta(g)+chi(g)^-1 beta(h)`.
* The natural Kummer class is inherited as `alpha = v w [phi] + r [3] + [sqrt(5)]`, with the normalized coefficient data and one common frame. The frozen eight tuples are necessary-system candidates, not known global representations.
* S is the **complete** ramification support of beta, one of the four frozen nine-prime sets. The historical bound is primewise: **every rational prime ramifying in beta is at most 2000**. It is not a bound of 2000 on a conductor product. Sigma adds the places over 2,3,5,7 and the two real places. These rational fixed primes give four finite K-places; all support primes are inert in K. General statements about arbitrary finite Sigma containing 7 and infinity are distinguished from dimension statements for these specific Sigma.
* For a continuous k-valued 1-cochain p, `dp(g,h)=p(g)+p(h)-p(gh)`. The cup cochain is `omega(g,h)=alpha(g)chi(g)^-1 beta(h)`, with trivial target action. The required equation is `dp=-omega`. A primitive is a global cochain, not a freely assigned list of local values.
* The local Artin map sends the chosen uniformizer to **arithmetic Frobenius**. At support q the uniformizer is the rational prime q; at 5 it is sqrt(5). The ordinary inertia coordinate is evaluation on the Artin image of the explicitly pinned residue generator. The toric constant is `h_q=(Nq-1)/7 mod 7`.
* Choose one continuous triangular reference `rho0=[[chi,b0],[0,1]]` over R lifting the pinned residual representation. It is auxiliary. For an actual representation with that residual matrix and determinant chi, `rho=(I+7X)rho0`, `X=[[p,q],[beta,-p]] in sl_2(k)`. No assertion identifies rho0 with an actual Frey representation.

## Claim cards and dispositions

|Card|Exact claim|Hypotheses and evidence|Audit disposition|
|---|---|---|---|
|C0|Actual Frey objects give the stipulated natural lattice, residual class, depth-one expression, local toric packets, fixed traces, and bounded residual candidates.|Block79 H1–H6, Block73 contract and inherited leaves.|Conditional. Their bytes and finite controls do not authenticate all geometric hypotheses.|
|C1|For every finite Sigma containing 7 and the real places, `Sha^1_Sigma(K,mu_7)=0`.|Class number one; units `+/-phi^Z`; Kummer theory; explicit local obstruction at 7.|Passed by reconstructed arithmetic proof.|
|C2|`H^2(G_Sigma,k) -> sum_(v in Sigma) H^2(K_v,k)` is injective.|C1, finite-S Poitou–Tate, nondegenerate F7 trace pairing. For frozen Sigma the map is an isomorphism to k^9.|Passed. Finite-S duality, rather than unrestricted absolute-group localization, is essential.|
|C3|Every stipulated residual pair admits normalized continuous `p0` on G_Sigma satisfying `dp0=-alpha cup beta`.|Alpha is identically zero at support; beta locally a coboundary at fixed places, or fixed H2 terms vanish; C2.|Passed conditional on the stated residual hypotheses. No higher representation is needed for this implication.|
|C4|At a fixed place, the unique primitive meeting the trace equation is `pfix(g)=lambda chi(g)^-1 alpha(g)`.|`beta(g)=(chi(g)^-1-1)lambda`; some local element has chi != 1; same frame.|Passed by direct calculation and character argument.|
|C5|Ordinary localization is injective with exact image `ker L=im J`, local dimension 24, global dimension 10.|Frozen supports; class number one; complete Sigma-unit basis of size 14; finite-S H1 exactness; pinned Artin coordinates.|Passed mathematically. Numerical L/J coefficients and ranks checked by the separate computation audit.|
|C6|The ramified beta Frobenius rows include the self-conductor unit, with degree-two orbit weights and quadratic transfer as written.|Stipulated rational inverse-cyclotomic descent; complete conductor; pinned residues; principal reciprocity and norm compatibility.|Passed conditional on descent and complete conductor. This is not an ordinary-character formula for beta on G_K.|
|C7|For A=EJ, ranks are 7,7,8,7 and homogeneous k-kernel dimensions are 3,3,2,3.|Four frozen exact input sets; all 15 rows; correctly normalized b and c.|Computational finite assertion; separate engines reproduce it. It does not decide affine nonemptiness.|
|C8|A global primitive meeting all first-stage conditions exists iff `A z=t(p0)`, equivalently `N t(p0)=0` for a full left-null basis N.|C3–C7, same global p0 in every local target, complete left-null basis.|Passed exact linear-algebraic criterion. Actual t and Nt remain unevaluated.|
|C9|Smaller same-frame cardinalities are 343,343,49,343 whenever the constrained affine set is nonempty.|Additional common pointwise semilinear j/frame/reference; minus-support coefficients in wF7.|Passed only with the extra hypothesis. Without it use 49^3,49^3,49^2,49^3.|

## Dependency graph

1. Minkowski bound plus the elementary fundamental-unit proof imply `Cl(K)=1` and `O_K^*=+/-phi^Z`.
2. These facts and Kummer theory reduce a globally and locally trivial Sigma-restricted mu7 class to phi^e. The explicit 7-adic calculation forces e=0 mod7; hence C1.
3. C1, the trace-pairing dual identification, and finite-S Poitou–Tate imply C2.
4. Local residual hypotheses make the cup class vanish at every Sigma-place. C2 then gives C3.
5. The fixed local beta coboundary plus cocycle expansion gives C4.
6. The Sigma-unit basis, local class field theory, and H1 Poitou–Tate exactness give the exact ordinary localization image C5. Separate arithmetic checks certify the displayed matrices.
7. Rational inverse-cyclotomic descent, principal-idele reciprocity, the self-unit norm identity, and Artin norm compatibility give C6. Separate arithmetic checks certify all residue and Hensel evaluations.
8. C5 and C6 supply A=EJ. Exact finite rank/nullspace verification gives C7.
9. C3 supplies an existing global affine origin; C4 and the toric equations define its target; C5 gives all global character corrections. This proves C8. The extra semilinear constraint then gives C9.

The upper q-equation and integral/geometric lift do not follow from this graph. The actual affine target enters at step 9 and has no supplied arithmetic evaluation. There is no circular use of an actual higher representation in C1–C3. There would be a circular argument if a desired actual representation were assumed merely to obtain a preferred p0 satisfying its own trace and toric conditions.

## Decisive reconstructed calculations

### The global dual kernel

The real-quadratic Minkowski ideal bound is `sqrt(5)/2<2`; thus each ideal class contains an ideal of norm 1. A unit may be scaled by a power of phi and by -1 so that its first real embedding lies in `[1,phi)`. If it lies strictly between the endpoints, a norm -1 unit has integral trace `a-a^-1` strictly between 0 and 1, and a norm +1 unit has integral trace `a+a^-1` strictly between 2 and sqrt(5)<3. Neither is possible. This proves the stated fundamental unit.

A Sigma-unramified Kummer class has valuations divisible by 7 outside Sigma. Principality removes those valuations by a seventh power. Local triviality at all Sigma-places makes the remaining valuations divisible by 7; another seventh power leaves phi^e, with the sign already a seventh power. At the unique place over 7, `F=Q_7(sqrt(5))` is unramified quadratic, and the verified identity is

`(phi^48-1)/7 = 5 sqrt(5) mod7 !=0`.

A seventh-power unit has 48th power congruent to 1 mod49: its torsion factor has order dividing 48 and its principal-unit factor is a seventh power in `1+7O_F`. Hence phi is not a seventh power. If phi^e were one with 7 not dividing e, Bezout would force phi itself to be one. This proves C1 without sampling possible global classes.

The F7-Cartier dual of trivial k is k(chi), using `(x,y) -> Tr_(k/F7)(xy)` and mu7 as the target. Finite-S Poitou–Tate pairs `Sha^2(k)` with `Sha^1(k(chi))`; two F7 coordinates reduce the latter to C1. Every module-order prime belongs to Sigma; real modified terms vanish at odd order. For frozen supports, only the nine support places contain mu7, each gives a one-dimensional k-valued H2 term, and global dual invariants vanish. Thus the claimed H2 isomorphism has the stated domain.

### Signs, cochain degrees, and the fixed local formula

The cup has degree 2 with trivial coefficients. Expanding the two cocycle laws in `d omega(g,h,t)` cancels all four resulting terms, so it is a genuine continuous 2-cocycle. Vanishing of its cohomology class means that an admissible continuous 1-cochain exists; the negative sign is handled by negating a primitive of omega. Substitution of the identity element gives p0(1)=0.

For `pfix=lambda chi^-1 alpha`, expansion gives

`dpfix(g,h)=lambda alpha(g)chi(g)^-1(1-chi(h)^-1)=-alpha(g)chi(g)^-1 beta(h)`.

It also gives `(chi(g)-1)pfix(g)+alpha(g)beta(g)=0`. If another primitive meets the trace equation, its difference z is an ordinary character and `(chi(g)-1)z(g)=0`. Choose h with chi(h)!=1. For any g with chi(g)=1, both h and hg have nontrivial chi, whence z(h)=z(hg)=0 and z(g)=0. All other g are already forced to zero. This is uniqueness of the local **cochain in the fixed frame**, not uniqueness under arbitrary reframing.

At support places chi is locally trivial. Consequently the inherited local class-zero alpha is identically zero as a cocycle there. Thus a restricted primitive p is locally an ordinary character at support. At fixed places pfix and p0 are generally inhomogeneous cochains, but their difference is an ordinary character; only that difference is placed into Artin coordinates.

### Ordinary localization versus twisted beta

The local ordinary spaces have dimensions `1+1+1+3+18=24`: one unramified coordinate each at 2,3,5; a two-dimensional principal-unit quotient and one uniformizer coordinate at 7; inertia plus uniformizer at each support. Phi and 3 form the 7-adic unit basis, with normalized 48th-power logarithms `5 sqrt(5)` and `6`.

The Sigma-unit basis modulo seventh powers is `phi,2,3,sqrt(5),7,q1,...,q9`, of size 14. Valuations prove independence of the 13 nonunit generators; phi is not globally a seventh power. The class number eliminates ideal-class generators. H1 duality identifies the localization image with the annihilator of these principal relations. Thus L is a complete presentation, not only a necessary matrix constraint. Localization injectivity follows because a character trivial at all Sigma-places is everywhere unramified; an odd-order character has no real-place ramification; the class number is one.

The rational-uniformizer self-coordinate for an **ordinary** character is zero in its own residue-unit relation because its own local unit component is 1. In contrast, the **twisted beta** row at its conductor involves a cyclotomic prime generator pi_q, and its local unit is generally nontrivial. Confusing these two situations drops an essential contribution.

At q=1 mod7, in the selected cyclotomic completion write `pi_q=q u_q`. Since `Norm(pi_q)=q`, the product of u_q and the five other conjugate local unit values is 1. Taking the selected residue log gives `ell_q(u_q)=-sum_(b=2)^6 ell_q(pi_q(z_q^b))`. Combining this with the weighted principal-idele relation gives the self term

`D_(q,q)=sum_(b=2)^6 (1-b)ell_q(pi_q(z_q^b))`.

For q=-1 mod7, the six embeddings describe only three residue primes. Weights b and -b give the same functional after residue Frobenius, because the residue log changes by -1. Three orbit representatives or half of the six-embedding sum are required. Unramified quadratic restriction at a q=1 support gives the factor 2 via `Norm(q)=q^2`; at q=-1 a compatible rational Frobenius square gives beta value zero by `1+chi(q)^-1=0`. The c-coordinates use the pinned inertia conversion, not automatic equality with the frozen s-coordinates.

### The affine criterion and exact scope

Let z_char be a global ordinary character with parameter vector z, so its localization is Jz. The fixed-local target consists of the coordinates of `pfix-p0`; a support target is `-h_q c_q-(c_q p0(F_q)-b_q p0(T_q))`. The first-stage conditions for `p0+z_char` are exactly `EJz=t(p0)`.

If p0 is replaced by `p0+z0_char`, with localization Jz0, then each fixed coordinate and support toric coordinate changes by the corresponding negative row of Az0. Thus `t(p0+z0_char)=t(p0)-Az0`. The class in coker A is independent of the chosen **global** bare primitive. This argument does not permit substituting unrelated local primitives.

For a **full** left-null basis N, rank N equals `15-rank A`, so `ker N=im A`; hence Nt=0 is sufficient as well as necessary. An arbitrary matrix satisfying NA=0 would yield only a necessary test. If the affine set is nonempty, it is a torsor under ker A, which gives exactly the first-stage cardinalities over k. All these statements concern cochains under the specified finite conditions. A q matching the prescribed global and local upper data, higher integral lifts, complete actual local conditions, and Frey realization still require additional arguments.

### What the upper-stage boundary actually means

The upper right cochain has coefficients k(chi), with differential `d_chi q(g,h)=q(g)+chi(g)q(h)-q(gh)` and prescribed right side

`Omega_p(g,h)=2 alpha(g)p(h)+alpha(g)^2 chi(g)^-1 beta(h)`.

The cocycle laws for alpha,beta together with `dp=-alpha cup beta` make Omega_p a continuous 2-cocycle with these coefficients. At a fixed local place, if `beta(g)=(chi(g)^-1-1)lambda` and the Stage-P trace condition forces `p=pfix=lambda chi^-1 alpha`, define the normalized continuous cochain

`qfix(g)=-lambda chi(g)^-1 alpha(g)^2`.

Expanding `alpha(gh)^2` gives

`d_chi qfix(g,h)=lambda chi(g)^-1 alpha(g)^2(chi(h)^-1-1)+2lambda chi(h)^-1 alpha(g)alpha(h)=Omega_p(g,h)`.

At support places alpha is identically zero, so Omega_p is identically zero and q=0 is a local primitive. These elementary local facts prevent interpreting the unfinished upper stage as an established nonzero bare H2 obstruction. The report makes no such nonvanishing claim. The actual remaining task includes matching the prescribed global/local upper data (in particular the marked fixed-seven valuation), satisfying higher integral constraints, and authenticating an actual geometric realization. An arbitrary choice of a local upper primitive does not accomplish those tasks.

## Obligation matrix

|Obligation|Status|Evidence and limitation|
|---|---|---|
|Coefficient domains, actions, degrees, and continuity|Passed|Reconstructed cocycle and cochain laws over k; rho0 over R prevents mixed-characteristic carry errors.|
|Quantifiers and complete support|Conditional|Frozen S is stipulated complete beta support; bounded regime is not an unrestricted conductor theorem.|
|Bare primitive remains in restricted domain|Passed|Finite-S H2 argument directly produces p0 on G_Sigma.|
|Actual p descends to restricted quotient|Passed conditionally|B79 inertia proof plus cocycle law gives constancy on omitted inertia cosets and their closed normal closure. Extra upper q-ramification is allowed.|
|Finite surrogate compared with actual object|Not addressed for realization|The matrices genuinely represent ordinary character differences. They do not authenticate p0, t, an actual representation, or a Frey object.|
|Cocycle and local trace signs|Passed|Direct expansion above; arithmetic Frobenius convention fixed.|
|Local Artin variance, norm transfer, and conductor self-unit|Passed conditionally|Primary CFT norm diagrams and principal-idele theorem checked by literature audit; descent remains inherited.|
|Finite-S duality and dual module|Passed|Milne ADT I.2.3 and I.4.10 exact versions authenticated; order invertible in Sigma-integer ring.|
|Ordinary localization completeness|Passed|Sigma-unit/Kummer basis and PT image exactness; dimensions independently certified.|
|Frame and reference independence|Passed at stated level|Affine origin shifts checked; optional semilinear counts require common j/frame/reference. Arbitrary reframing is outside the claim.|
|Matrix ranks and tested range|Passed as finite evidence|Separate unchanged arithmetic engines reproduce all four matrices/ranks and self-unit Hensel checks. The finite support range is explicit.|
|Actual arithmetic affine target|Not addressed|No authenticated 15-coordinate t(p0) or seven/eight-coordinate Nt(p0) supplied.|
|Upper-stage q and integral lift|Out of scope|No inference from Stage-P criterion to their existence.|
|Unrestricted signatures or Beal proof|Out of scope|No residual exclusion and no universal signature/conductor reduction supplied.|

## Source and computation checks

The literature audit authenticated the 2006 second edition of Milne's *Arithmetic Duality Theorems*: I.2.3 (local duality), I.4.10 (finite-S duality and exact localization diagram, printed 56–57), and the required dual-module dictionary. It authenticated Milne's *Class Field Theory*, v4.03: arithmetic Frobenius in local Artin reciprocity, norm/inclusion compatibility, and annihilation of principal ideles by global Artin reciprocity. The local norm/transfer statement is present in those notes with its proof marked to be added, so the audit accepts the classical theorem rather than claiming to have replayed a proof absent from that source. The separate literature report records exact source pins. These classical leaves establish the cohomological and reciprocity implications, not the project's inherited geometric hypotheses.

The computation auditor reports a fresh unchanged Block80 plus immediate Block79 replay, passing in 15.15 seconds, with v2 manifest validated and input archive unchanged. Both complete Block80 JSONs were rebuilt identically. Independent checks cover phi's `[0,5]` logarithm, 3's `[6,0]` logarithm, support phi rows zero, L rank14/J rank10, A ranks7/7/8/7, complete null bases, nonzero minors, and all seven self-conductor Hensel units. Its report records commands and input/output pins. This audit does not label the two code engines as independent proofs of the inherited geometry.

One historical metadata claim failed: Block71's primary output labels its unit domain as 2304, whereas the enumerated ring has `49^2-7^2=2352` units. The separate original engine reports 2352, consistent with 48 nonzero residue classes, each with 49 lifts. The archived bytes remain unchanged and a separately pinned correction is supplied by the computation auditor. The reader must use 2352 if quoting this domain. This does not change the Block80 operator or its ranks.

The final evidence chapter correctly separates the unchanged Block67 verifier's scientific `PASS`, zero exit, eight compared outputs and nine rejected corruptions from the new generic wrapper's failed attempt to require a different status label. Its interpretation correction is a separate pinned record. It likewise preserves the archival Block69 wrapper's aggregate 840-second timeout as resource-inconclusive, while naming the later portable scientific replay and its seventeen matched JSONs separately. Portable scientific success for Blocks67–80 is not represented as completion of every historical packaging wrapper. This review checked these status distinctions against the computation audit; it did not rerun those code suites itself.

The final computation evidence is frozen. Its `RUN_SUMMARY.json` reconciles 32 executed records, preserves failed statuses, names every portable block67–80 as completed, and records zero authenticated arithmetic targets and zero eliminated patterns. The portable69 report contains seventeen complete-JSON comparisons at unchanged bounds. Manifest schema validation expressly distinguishes archived-input observations requiring the original archive from distributed portable input validation; neither kind of validation is mathematical verification by itself.

The separate final reader-data QA supplies 194 exact assertions and identifies both frozen publication PDFs. This review read its report and reusable accepted script. The script compares the complete matrices and support/inertia data with freshly reproduced source records, reconstructs the q11 roots rather than claiming new curve counts, and distinguishes the synthetic target from actual arithmetic. Its first QA run failed because its own h test confused cyclotomic residue degree with the residue degree of a place in K. The corrected version uses `Q=q²` for every all-inert support place; the failed script, traceback and manifest remain separate and no guide datum was changed. This is the correct field for `h=(Q-1)/7`; cyclotomic degrees continue to serve a different role in beta's residue-symbol normalization.

## Required reader corrections and remaining check

The frozen standalone reader states the arithmetic Artin/Frobenius convention, distinguishes chi reductions, writes primitive shifts as addition of a global character rather than a local vector Jz, states the primewise 2000 ramification bound explicitly, preserves H1–H6 as conditional inputs, and calls the eight tuples residual candidates. The numerical dimensions describe the operator; the actual affine class remains explicitly unevaluated. The final guide likewise retains the same complete-support, frame, semilinear, and realization boundaries.

The cheapest mathematically useful next check is an authenticated construction of one global restricted p0 for a stipulated residual pair together with its compatible 15 local target coordinates, or a structural argument computing its cokernel class without selecting numerical p0 values. Passing Nt=0 would establish only the listed Stage-P conditions; a nonzero authenticated Nt would exclude that stipulated Stage-P candidate. Neither outcome alone proves the unrestricted conjecture.

## New reader arguments checked independently

The new elementary arguments were reconstructed before consulting their historical analogue. The following checks passed at the displayed scope.

* **Prime/four exponent reduction:** every exponent >2 has an odd prime divisor or is divisible by 4; exponent absorption preserves each base's prime support. The remaining signature set is infinite and does not reduce to (3,5,7).
* **Conditional abc bound and unit bases:** positivity and primitivity give `rad(ABC)<=ABC<H^(1/x+1/y+1/z)`. The assumed abc estimate yields the written height bound only when `(1+epsilon)s<1`. For (3,5,7), `s=71/105`, the C-bound exponent is `15/(34-71 epsilon)`, hence `150/269` at epsilon=1/10. Apart from the Fermat-excluded signature (3,3,3), all Beal signatures have `s<=11/12`. The final chapter takes epsilon=1/22 and explicitly enlarges `K_(1/22)>=1`, giving `(1+epsilon)s<=23/24` and the uniform conditional powered-height bound `H<K_(1/22)^24`. This bounds a finite set of powered triples, not its emptiness. The accepted Catalan theorem separately excludes A=1 or B=1: the only consecutive powers are 3²−2³=1, whose upper exponent 2 is forbidden here. With all bases greater than one, a uniform powered-height bound also bounds every exponent label. Neither deep input is re-proved in the reader.
* **Radical-ceiling negative control:** independent exact-integer arithmetic confirms `2+109*3^10=23^5=6436343`, radical 15042, and `6436343^71>15042^105`. Its logarithmic quality is approximately 1.629911684127. This is a primitive sum, not a (3,5,7) solution.
* **Universal identity and inverse parametrization:** direct multiplication gives the common factor `t^35(1-t)^84`. Substituting `t=A^3/C^7` and `lambda=C^8/(A B^4)` recovers each nonzero rational base exactly. The four valuation sectors force the displayed unique lambda valuations; their divisibility conditions are necessary and sufficient for primitive integrality. The denominator failure at t=1/2 and nonprimitive lambda=4 example check.
* **Complete local coefficient criterion:** at odd primes, two unit bases guarantee a unit partial derivative even at 3,5,7. The cyclic-group gcds are exactly 2. At noncoefficient primes, the exceptional sign pattern is handled by the universal identity and the exact nonsquare-pair count `(p+1)/4`. The dyadic criterion follows from the unique even base and squares modulo 8; square-root digit lifting starts at n>=3, and odd power maps lift bijectively. The argument covers Z_p-solutions with nonzero roots and at most one p-divisible base, not one common global root triple.
* **Everywhere-local examples and finite CRT witnesses:** both squarefree triples (3,5,2) and (2,3,11) pass every coefficient-prime and dyadic condition. The prime-avoidance CRT construction gives pairwise-coprime positive bases satisfying each finite congruence system, without exact equality. The all-odd mod8 relation has 36 of 64 triples; inclusion-exclusion gives `3*16-3*4=36`, and all three marginals are full.
* **Frey algebra:** independent SymPy exact Sylvester calculations give discriminants K,K,4K at the three interpolating pairs, K=9331200000. Weighted homogeneity proves the complete three-monomial interpolation space. The nodal substitution, resultant 45, and four characteristic-seven coefficients check exactly. The associated geometric, finite-flat, conductor, and irreducibility applications retain their named inputs.
* **Stable lattices and local depth:** for O-lattices, the integral complementary projectors split a stable lattice into two rank-one fractional ideals, giving the segment 0<=j<=n. The local depth argument checks for integral N,F, primitive (x,y), and t>=0; the natural local cup application additionally uses t>=1 and h>=1. Explicit integral hypotheses were requested in the standalone theorem. This local matrix argument does not prove a geometric realization.
* **Conditional eligible-prime necessity:** the stipulated characteristic-zero toric chi-line intersects each stable lattice in a saturated line. Where chi is nontrivial, its reduction splits the opposite local extension; this uses an actual line and survives stable-lattice changes. At the fixed places over 2,3,5, the norms are 4,9,5, each outside ±1 modulo7; the tame Frobenius relation and unramified quotient therefore give `H1(K_v,k(chi^-1))=0`. The specified seven-adic toric line also splits locally. If no variable C-prime had norm 1 modulo7, beta over `L=K(zeta7)` would thus be everywhere unramified. Restriction is injective because `[L:K]=6`; class field theory and `Cl(L)[7]=0` contradict its nonzero class. The latter follows from the authenticated `h(Q(zeta35))=1`: L is the index-two subfield, and norm after ideal extension is multiplication by two. CRT with the split/inert residue degrees gives exactly q modulo35 in `{1,8,13,22,27,29}`. The necessity is conditional on the local toric and global-unramified inputs and imposes no particular additional fixed prime.
* **Discriminant collapse:** the two quadratic trace roots are algebraic integers and are real in `[-2 sqrt(Q),2 sqrt(Q)]` because each corresponding pair of complex roots has product Q and equal absolute value sqrt(Q). Their squared difference D is an integer, divisible by `7^(2r)` and bounded by 16Q. The collapse follows at the stated strict bound. The 2549 quartic negative control has D=12005=`5*49^2`, agrees with the relaxed quartic congruence modulo343, and fails the stronger rank-two precision.
* **Marked periods and torsion:** the split rational uniformization proof uses `mu_M^2 intersect Lambda=1`, since the lattice is torsion-free. Both directions of the full torsion criterion check. The level-seven unit reduction is multiplication of its additive class by 2; the level49 reduction is multiplication by 16. They give exactly 75A and `3*5^9 A/C0^35`. The four-prime common-coefficient contradiction has determinant6 mod7. The marked period comparison itself remains an inherited geometric input.
* **Trace product and twisted orbit normalization:** expanding the determinant gives `bc=T+(Q-1)D+7TD-7D^2`; the Q=1 mod7 specialization and trace/norm correction formulas check. The zero product condition is preserved without replacing it by beta(F)=0. Degree-two conductor prime weights correctly use three orbits or half of the six-embedding sum.
* **Legitimate higher global precision:** the historical actual diagonal theorem gives a triangular global alpha_j only for `1<=j<=m=floor(n/2)+1`. The explicit unit-period formula applies in the common range `j<=min(m,7c-1)`. The exact period valuation matrix still gives the valuation coordinate at all legitimate `j<=m`. For n=1, m=1, so no actual global triangular mod49 extension has been obtained by this route.
* **The defined valuation functional and mixed trace:** strict local alignment at K7 makes the local adjoint representative p=beta=0; its upper k(chi)-cocycle has the well-defined [7] coordinate nu7. Residual alpha and coboundaries have valuation zero, so the remaining aligned strict gauges preserve it. The numerical target follows from the actual period class and the reference's zero valuation. The trace identity is exact; its depth-one signal is modulo343, while the all-depth signal requires `j>=n+t+1`. A labelled probe and detecting element from one representation are required. The example products 51 and 100, and prescribed target98, are correct.
* **Secondary cochain algebra and coefficient domains:** direct expansion gives `ds=-(alpha cup beta+beta cup alpha)` and `R_p+d_chi(alpha p)=mu_p`, with indeterminacy `2[alpha] cup H1(K,k)` for unconstrained absolute primitives. For constrained Stage-P solutions, variation is restricted to the permitted character space, eventually kerA. The U3(F7) commuting-pair control refutes only a formal implication for arbitrary groups; it is not an absolute Galois or Frey counterexample. The absolute H2(kchi) localization proof via a degree-six extension, restriction/corestriction, and Brauer localization checks; it does not establish a finite-S result by itself.
* **Unrestricted interpolation:** original Neukirch Korollar6.4(c) and the Neftin reformulation were authenticated by the literature audit. The dual module translations give group C6 for ordinary k and the trivial group for k(chi); their positive H1 vanish. The resulting finite-local interpolation permits new ramification and cannot replace the restricted image theorem.

The reader's status statements must describe the incomplete Operation Komorebi route. A recent external preprint reports a claim for signature (3,5,7); this edition does not audit that full external proof and should not infer a global literature-status verdict from its own unfinished route.

The guide's mathematical labels, domains, counts, and target distinctions were checked against the same claims. The final revision implements the requested corrections: the self-conductor subtitle says norm q, global character shifts are distinguished from their parameter vectors, exponent reduction preserves prime support, and the natural alpha residual entry is distinguished from the opposite-endpoint beta class. The complete beta support and primewise bound are explicit on physical guide page12. Figure generators use finite-field coordinates as labels, not as real magnitudes or actual arithmetic realizations. The guide's exact native data run records 142 bounded checks, and its author's `PROOFREADING.md` and `VISUAL_SELF_REVIEW.json` identify their separate self-review scope. Final reader and guide revisions are pinned in REVIEW_PINS.json.

The eleven declarations in `evidence/formal/BealAffineReader.lean` were also reviewed against their stated prose roles. Their domains are generic monoid cochains, a field-unit character and supplied twisted cocycle, and linear maps over a commutative ring. The negative cup sign, toric trace identity, affine translation, quotient-class identity, and kernel-translate statements match the reader. The complete-null equivalence explicitly assumes `ker N=range A`; its necessary-only counterpart is separate. The formal report correctly excludes continuity, actual Galois groups, restricted primitive existence, local uniqueness, actual matrix completeness, target authentication, and finite cardinalities from this module. The forty public statements are 21 historical Block47, 8 historical Block48, and 11 new generic statements, with distinct verified scopes. They are not a formal Beal proof.

## Exact source pins

Paths are relative to `/workspace/scratch/fd5253a691e7`. SHA256 values refer to the exact bytes read in this audit.

|SHA256|Source|
|---|---|
|84b67a8b0fefeea3633cacb9eb29b948468cdac82d20dd6df4ea39f2689ee3ac|beal_sources/block80/work80/TARGET_CONTRACT.md|
|ea3c97b7b710150befd901b270c560bbfd0c3f3e955b1b0aa9178920dd6941cf|beal_sources/block80/work80/THEOREM_INDEX.md|
|dc9b884207ef1f9c760de993bf0b0c67994c64b7d92b9c1ef8992f3907172dae|beal_sources/block80/work80/notes/RESTRICTED_CUP_PRIMITIVE.md|
|aac794a0f52c6e4e09c06c779ec31fa019330e9486fbdec501b0255bb9b21456|beal_sources/block80/work80/notes/FIXED_LOCAL_PRIMITIVE.md|
|cc74eed974514d6fe4a5a52f48f2fb0f129d5e33d5df985c0620346784640e06|beal_sources/block80/work80/notes/ORDINARY_LOCALIZATION.md|
|53a3830053be14781ba1bc52d0d9c7f2f0f4e81b5354f8a524b3371db662271a|beal_sources/block80/work80/notes/RAMIFIED_FROBENIUS.md|
|09f4d7e20662568a5674f8b99fab492992e1bf568cbcfcd8d525d3cf057c12b5|beal_sources/block80/work80/notes/AFFINE_OBSTRUCTION.md|
|54cbb8ea950df0f3a6d795ab7cf384ec4b1ada4ce033cd499e4eb3ac3fe397f0|beal_sources/block80/work80/inputs/pinned_0_TARGET_CONTRACT.md|
|47b9fc31fe1f1cc6459ec13fcd5df49dd55d12db837f36932649598017b93aa1|beal_sources/block80/work80/inputs/pinned_0_INERTIA_RESTRICTION.md|
|d765d392efad422a1936eebbb84d5f1b74d87749bd304abd16c9d1dbefc9d2b5|beal_sources/block80/work80/inputs/pinned_0_SUPPORT_Q_VALUES.md|
|5a2864719e3d982cd85353a57a8f6d3f34591bdb2ee4d48c555cf4976a715589|beal_sources/block80/work80/inputs/pinned_9_SURVIVORS.md|
|a909d24c9247c56e7e9af43509501f1dd3cd7c27d0414d1c14efc8ae8c771280|beal_sources/block80/work80/inputs/pinned_11_DEGREE_TWO_RECIPROCITY.md|
|cfe4b08cbacee54be2329a03e25fe537ad3670b66793e9d191c268be2f60c7b1|beal_sources/history/block73/Komorebi_Beal_Block73/work73/notes/ADJOINT_DEFORMATION.md|
|890da5f1ce878c8da6fd2ddb3dc45d250ba2fce292563611422be15311f842cd|beal_sources/history/block73/Komorebi_Beal_Block73/work73/TARGET_CONTRACT.md|
|29441c5862630d23293d64f09f0c56d9367e2bb08bfed65a78e74694f76f7fbe|beal_sources/history/block73/Komorebi_Beal_Block73/work73/inputs/B54_FROBENIUS_MONODROMY.md|
|0bd011dfc61f8269bd29bb3dbe4b48ef5f4c5bb0bd01a69f56ad3e7034753e3b|beal_sources/history/block73/Komorebi_Beal_Block73/work73/inputs/B72_ACTUAL_GLOBAL_LIFT.md|
|cb0e09e98b6eaf9efcc00ea8f1ac5acc7336411d23b0e58eb53edabe64f28092|beal_sources/history/block73/Komorebi_Beal_Block73/work73/notes/FIXED_SEVEN_DEFECT.md|
|d0b7ef4fb1f0e6dcaf5b01246d9371b55dc51243ca7329eefe2c7dd0b0478db2|beal_sources/history/block74/Komorebi_Beal_Block74/work74/notes/TRACE_EXTRACTION.md|
|ddf72d9d8ebd5e1208537e0b88e7e8e4ee81d04f0b811f1b6b870934461ee7c0|beal_sources/history/block74/Komorebi_Beal_Block74/work74/notes/ALL_DEPTH_VALUATION.md|
|302ab57142f3487b7f64449eb59fad982ed198c9297eea18e67b4fced475aad8|beal_sources/history/block75/Komorebi_Beal_Block75/work75/notes/NORMAL_FORM.md|
|145f963b0d79a2b9ec966e45df77f263516ee84315c480adb82fc437fd2efb28|beal_set/evidence/formal/BealAffineReader.lean|
|7658c70bd96fb52e2946f1a00896683eeac189275dae150b587da96c4146c261|beal_set/evidence/FORMAL_STATUS.md|

### Frozen publication and companion-review revisions

These paths are relative to `beal_set`. The complete reviewed-input map, including portable copies of the historical leaves above, is in `evidence/REVIEW_PINS.json`. Pinning a companion report authenticates the evidence revision used; it does not mean this reviewer independently executed its checks.

|SHA256|Source|
|---|---|
|f1c73dfc12b53be2c7abc1d4eb07389d7c11389014547b91b1cf8691d9683f7f|evidence/COMPUTATION_AUDIT.md|
|1bb18d4d56453e2cd2210a71b355ddcc6fddfa50a91215269c5264fbef09bd89|evidence/LITERATURE_CHECK.md|
|5140e12025fb16f95691838f5eb3632e376888e61289f15527aab5d12ca60229|evidence/READER_COMPUTATION_QA.md|
|1bf3c651415dc9cd0a1fd9dbbe1679ad7a2a22f95ddea81ff061174c7f4a71d2|evidence/computation/FINAL_COMPUTATION_PINS.json|
|f0c8dfc2f7f53544ff22b3a8146fd5f4865ef186e4267a71479bc2a93886b535|evidence/computation/MANIFEST_VALIDATION.json|
|5126bd3b013e9c1879779cad7cc5f010ab62a5739145afe36a8b6f2a9aafbee8|evidence/computation/RUN_SUMMARY.json|
|429d970e98ab5e3e42d8dc9407a133f2f3478772b69e4e9931c78ddc58edc6a9|paper/AUTHORING_NOTES.md|
|b23eaee9fb9691ea976a03e01d16656a9126c3f22a1946ca5fb7677bc8a53939|paper/PROOFREADING.md|
|9e6149aa9ee2ba8eca6ca6bebe2c8f34663640c9fd576cb3d22d64f61969dd30|paper/chapters/00_reading.tex|
|7efe67684beefc53a27f59e447790f926ceaace86b047af0f55590dbe3f129ac|paper/chapters/01_statement.tex|
|e0f89c0641e44ab347846cade44d6322bd1b1baa1e50890ea16ba5da0f9d405f|paper/chapters/02_signatures.tex|
|73990797e3ac0cb51ead0c20c67ea4436ef3e5db623bd1f75a045d10c592ac49|paper/chapters/03_scaling.tex|
|20299ffd7cd44da2686b4033f660325f974c32f197d721c67a4fbbea9c543bd6|paper/chapters/04_local_strata.tex|
|81d33daa2f9e3e66ce7385f47c0aeff4036d4093128c0333c5e3aa8167d87f54|paper/chapters/05_frey.tex|
|04d738046e0bbb79160ae0411111bcf921f397f8f98d7b477af1c99d097c51e2|paper/chapters/06_modular_labels.tex|
|83bf51b0a1de9b6c996cffcd8615fc35a3d515af20d12a127540d6d7393dd3c9|paper/chapters/07_natural_depth.tex|
|11fbc18a6f3554171c2e98c930654f000ea8d5259fb41ffc9f9676c2361575ad|paper/chapters/08_global_coefficients.tex|
|8a2e28407f8d8971d3b6bd97b562fa4140886a0fcd12f2fbc224597dd53ad157|paper/chapters/09_periods.tex|
|55cf48575f14fdbee4eae47e1caf576a273c0e5686ef204977cb5b8bb76da826|paper/chapters/10_reciprocity.tex|
|b6d4893144668d524aac796dabfa21510822828aea070b774aad78a4c634c5d6|paper/chapters/11_bounded_patterns.tex|
|3dc6166a25a33ee09f4a9c63c6e6f14c742555d9968e1737de7c3e2ef2e842a8|paper/chapters/12_fixed_seven.tex|
|76ebfdd43e97fcc9dee00f6d1032dcb99a609d31d8b2e24ae028c28b4513b89a|paper/chapters/13_deformation.tex|
|5da7b4d8d171c8807c6075b5dcd63611910d118f6168d456f52655a4ad657cc5|paper/chapters/14_integral_trace.tex|
|d4dfa71a0d7da079476ac3e376ef002df74345c97d0b8dd411ddac7392c66947|paper/chapters/15_semilinear_image.tex|
|6251d93fd1b5b326d1c06186845ee0ac38b4fffafffd9dc5a0aaab077f9a0717|paper/chapters/16_secondary.tex|
|c928c09085127f838c24b2cd94c65a996e9147d75e9010a154cdf0b8cf5cc99d|paper/chapters/17_local_flexibility.tex|
|f61424879ae3b9c883f10312bc5336df4f709027b5b6dba3f135e45eefb5ba49|paper/chapters/18_ramification.tex|
|e532226ab7468d4ad89617b7dd0502a9ca497f789f55edf6942ff163621a3e06|paper/chapters/19_bare_primitive.tex|
|d2f2eb60aa5b55dd79e798eb31417e8cc79da405d5c6cfe7f86bfbe439c65349|paper/chapters/20_localization.tex|
|553d10ef28e7eb6bec6acf17615a8ff9d58f3092ab526505182d9fbb492f7a38|paper/chapters/21_ramified_frobenius.tex|
|1ed9288af43f8203f7d67d1f8f16d4c3eb682a9248a6680745d900a8fa55f37f|paper/chapters/22_affine.tex|
|eb8c1ccec9fab9eb1f77d60b0fdfa147ce5783e18243e71e1e00b0c9c762bf92|paper/chapters/23_evidence.tex|
|43b6ff0bddf3b896dbdab0f6c7b1d89b7b19c789ced590735b2ddca1e48771da|paper/chapters/24_sources.tex|
|c64bc2c468e48e23c9b058cbbaac8c2371874fcb10872143fe3abed27a4251e3|paper/main.tex|
|43a94b3303652dd72fbc3463d00e5e16b0bdddce27a1c4e0e4d6c143e22e97b8|shared/figures/01_beal_terms.pdf|
|505028810a8d29bc83851d8ba28276eab27809b69506099d6a17338335153d9f|shared/figures/03_valuation_packets.pdf|
|b5355a09ecc5cb2401f81ff9e05378bf935b3655400cd3631d02cf076c0c6a5b|shared/figures/11_support_sets.pdf|
|20272db28da3129ff50f1d573b1eb2130061cfa0040b181f6a4077cbc89cd619|shared/figures/19_affine_dimensions.pdf|
|1ca5821b56f99456228ae370962a35f4013dd977b909e0a1ba98461e4fd32059|shared/figures/24_research_boundary.pdf|
|b8cdfe3743d4784c5ad7e1095b5b36c34e902543b7a23d90b49c65a8e42afc46|shared/guide_preamble.tex|
|d0ab3fef0bd027e7588479abcc72ccdd745cd7f38e333441919f04c6492cdf2f|shared/preamble.tex|
|faf70393646a988587dd07d7a270e0ac1d91f3b5071e3bfaa424b587730a8d20|visual/PROOFREADING.md|
|8f747712db48526aa4cdf4727f95b8e82e8dcecd396ad51d14e72b2acb6d6403|visual/VISUAL_SELF_REVIEW.json|
|dd85ee109fb3ad11e47113440feaa2fd8e21480ab9554ab12bf4d2d53af1adaf|visual/body.tex|
|426ac2252352b8b98ae7b63b8efcf7cd2201295466046523e6ea7ab1874302de|visual/data.json|
|3452c8bb3e02ea5f690566d1d53c1145372b5bd18d443aa8cf5363101816b494|visual/figures.py|
|f93b3ba6cf3d8b37cd6b4bafccd8ba41c4053f8ff5b24a0327ad4925eda75a43|visual/main.tex|
