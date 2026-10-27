# Independent Hodge publication proof audit

Audit date: 9 October 2026. The raw recovered originals were read without editing them. This report owns only its audit files. It reconstructs the three September proof notes and selected August infrastructure, dyadic and completion claims. It is a manuscript proof review, not a peer review or a formal verification.

## Normalized claim and primary verdict

The strongest overall target would be an explicit cycle constructor for every rational Hodge packet on every Fermat fourfold, and ultimately for arbitrary smooth projective complex varieties. **Primary verdict: incomplete, with the smallest missing implication.** Universal packet coverage has not been proved, and the characteristic-zero K23 Chow realization has not been constructed or fully typed. The general rational Hodge conjecture is not established by the recovered program.

This verdict does not invalidate the positive special cases. The degree 70 carrier, degree 210 transfer, global invariant-column capacity certificates, direct-quotient obstructions and explicit standard-family cycle arguments reconstruct coherently under their actual hypotheses. Their named classical dependencies have now been checked in primary texts by the companion literature audit. They may be presented as manuscript-level special-case proofs. They do not establish novelty, universal coverage, or a complete list of representing surfaces.

The raw August frame theorem is false as written. The raw universal constructive theorem omits a coverage hypothesis. The unguarded K23 construction can produce a zero character entry and also leaves its rational CM target ambiguous. These failures should be corrected in the new reader and retained explicitly in the audit history.

## Exact sources and evidence revisions

`proof_claim_cards.json` pins each authoritative source path and SHA256, as well as exact section locators. The inputs are the unmodified `PROOF.md` files in Carrier 70 v0.1.0, Carrier Transfer v0.2.0 and Dual and Cycles v0.2.0, and the August `Projector_Resolved_Hodge_Calculus_Complete.tex`. These originals are not silently upgraded to the new publication's statement.

The independent finite arithmetic checks are in `proof_audit_checks.json`. They freshly check all seven capacity primal/dual certificates, the degree 210 multiset identity and stabilization counts, the degree 70 projective-torus character identity, the minimum q=2 differential factor, and the two decisive counterexamples. `proof_obligation_matrix.json` records passed, failed, conditional, not addressed and out-of-scope obligations. Companion exact experiment replays and compiler limitations have their own reports and are not inferred from a PASS label in an old archive.

## Dependency graph

The degree 70 path is:

`full-support rational balanced orbit -> normal weighted carrier with K_Y=-3H -> uniruled resolution -> algebraic rational(2,2) lifts -> finite torus pullback -> rational orbit projection -> boundary injectivity -> finite cube-map push-pull`.

Its geometric leaves are the Fermat character decomposition, normal hypersurface adjunction with the verified ambient-codimension condition, BDPP, the uniruled-fourfold Hodge theorem, lowest-weight image, pure-Hodge semisimplicity and functorial algebraic correspondences. Exact exponent arithmetic authenticates the particular carrier and its character, not those external theorems.

The degree 210 path is:

`degree 70 packet -> degree 210 inflation -> exact 30-entry identity -> append 24 negatives -> algebraic 54-entry joined character -> remove 24 complementary pairs -> rational 48-dimensional target packet`.

Every auxiliary block is already algebraic. Four-entry blocks use the surface theorem. The two longer blocks deflate to Aoki standard cycles at degree 35. The negative terms are converted into complementary pairs, so the proof uses the precise classical removal theorem rather than cancellation of arbitrary unknown motives.

The explicit standard-cycle path is:

`Newton identity -> actual integral complete-intersection surface -> uniform Jacobian wedge determinant -> unique socle complement -> authenticated nonzero period -> rational group-module generation of all supported lines`.

The negative constructor path is independent:

`positive integer dual costs + finite residue potential -> all invariant-column inequalities -> global relaxedcapacity upper bound -> matching primal witness or matrix obstruction`.

It excludes one matrix method, not algebraicity. In fact some excluded packets have explicit cycles or the degree 210 transfer.

The incomplete universal path would require both `universal packet grammar coverage` and `every admitted branch has a nonzero algebraic projected correspondence`. Neither a finite census nor a CM sign calculation supplies these missing arrows.

## Reconstructed degree 70 argument

The carrier polynomial has weighted degree 30 for W=(10,6,3,3,3,8). Its cone gradient is exhausted by three coordinate planes, so the hypersurface is normal by the codimension of its singular locus and Serre's criterion. The ambient weighted strata meet the fourfold in codimension at least two. This justifies the canonical Weil divisor equality K_Y=-3H without asserting quasismoothness, log terminal singularities, or Fano positivity on a resolution.

A general moving complete-intersection curve in the fourfold avoids its singular locus. Its strict transform avoids the exceptional divisors and has negative canonical intersection. A pseudoeffective divisor cannot have that intersection on this moving covering curve class. BDPP supplies uniruledness of the smooth projective resolution. The known rational Hodge theorem for uniruled fourfolds can therefore be applied.

The matrix calculation gives B=210A^-1, B1=7W and AB=210I. On projective tori this is an isogeny, whose Fermat restriction is a finite etale cover. The character is genuinely a torus character, not an unhomogeneous polynomial surrogate: beta=A^T a/70=(3,3,1,3,2,3), u=beta-3r0=(3,3,-5,3,2,-6), W.u=0 and B^T u=3a-630e0. The deck subgroup therefore fixes the whole rational orbit.

Full support kills every coordinate-boundary Gysin term. The relevant coordinate scaling fixes a stratum pointwise while acting nontrivially on the packet, and its normal-orientation/Tate contribution is trivial. Thus restriction is injective and surjective on this packet. Finite descent preserves rationality and the mixed Hodge structure. The descended pure weight four packet lies in the lowest-weight image of compact cohomology. Semisimplicity gives rational(2,2) lifts. These steps justify use of actual algebraic surface classes on the compact carrier.

The resolved graph and rational orbit projector preserve algebraic cycle spans. Their pullback agrees on the open torus with the prescribed packet class. Boundary injectivity makes that agreement global. The finite coordinate-cube map then pushes cycles down to degree 70. Positive coordinate-power maps give the stated infinite packet tower. No basis of24 explicit surface equations or general Hodge theorem follows.

## Reconstructed degree 210 transfer and capacity bounds

The thirty-entry identity was independently rechecked from its stored fourteen generators. Each side has 24 auxiliary entries. Appending the negatives of the left auxiliary multiset creates a54-entry character, on a Fermat 52-fold, and precisely 24 removable complementary pairs. This is the degree and multiplicity bookkeeping needed by the actual geometric cancellation theorem.

The degree 210 dual vector has positive coordinates summing to1. Its invariant-column inequality is universal. The source provides both a finite low-degree premise plus a large-degree cutoff and a residue shortest-cycle certificate. The newer potential formulation is especially transparent: Bellman inequalities bound any word prefix below by its potential, and a last-edge lower bound supplies the full return cost. This argument applies to a nonempty word of any length. It is not an extrapolation from a degree 18 scan.

All seven stored primal witnesses and every finite potential inequality were independently recomputed. The exact values are 6/5,2,1,2,1,1,11/10 for the seven named inputs, respectively. Rectangular feasible witnesses are allowed by the relaxed capacity definition. A capacity of2 can be attained by only two columns. This does not itself produce an invertible six-column matrix or a normal hypersurface. The value 11/10 for the old degree 70 carrier is a global optimum in this invariant-column model, not a bound on every geometric construction or on a scale-dependent Fano index.

The uniform family with q>5 and gcd(b,q)=1 has positive integral dual numerator divisible by q. Its capacity is exactly 1 because the all-ones column is a matching primal witness. This excludes universal applicability of the positive-anticanonical matrix constructor. It is fully compatible with the explicit surface below.

## Reconstructed five-phase cycle and periods

For every q>=2, the surface Z_kappa is the actual ambient complete intersection e1=e2=P-kappa*z^5=0. Newton's identity proves containment in the smooth Fermat X_(5q). The base S_q in P4 is a smooth connected complete intersection: failure of Jacobian rank would force all nonzero qth powers to equal one nonzero constant, contradicting their sum being zero in characteristic zero.

The coordinate curves are smooth and reduced, with no common irreducible component. P consequently has valuation 1 at a generic coordinate curve. The monic fifth-root equation is Eisenstein at that valuation and defines an integral finite flat cover of S_q. The surface is an integral complete intersection of degree 10q^2. It may be singular, which is admissible in the authenticated complete-intersection period theorem.

The determinant identity comes from three polynomial wedge identities. The first four rows contribute 25 de1 wedge de2 wedge de3 wedge de4. The last pair contributes 25q times the geometric-series sum in dP wedge dz. The elementary-symmetric Jacobian and e5=P^q contribute q^4 times the Vandermonde in the first five variables. The signs match the fixed row and coordinate order. Cancellation is in the polynomial ring, so the result extends across P=0. Every determinant monomial has the required degree 3m-6.

For each b, the dual residue numerator has exactly one socle-complement term in the determinant. Its coefficient 625q^5*kappa^(q-b) is nonzero. With the Villaflor v5 normalization, the period is (2pi i)^2*kappa^(q-b)/(50q). This is a genuinely nonzero cycle period, not merely a matching character label.

Although kappa need not be rational, the integral Betti cycle class is rational. Diagonal automorphisms act rationally on Betti cohomology. The primitive class has nonzero components on all 120(q-1) unit-stable support lines, and its rational group module spans exactly those lines. Thus whole rational packets in this family are algebraic. The family and its defining Aoki construction are already known. This audit makes no novelty or priority claim.

## Decisive raw-source failures and restrictions

**Ambient frame positivity.** Let V=span(e1) in R2 and use the single algebraic-model cycle c=e1+e2. Then C C* has positive compressed Gram value 1 on V. Yet e1 is not in span(c). The smallest missing implication is containment or invariance. Positivity proves V intersect span(c)^perp=0, not V subset span(c). A safe new statement requires c_j in V, for example after an algebraic packet projector, or an invariant frame. Without that condition, rational rank[C H]=rank C is the direct exact containment test.

**K23 zero-entry boundary.** At m=15 take A=(1,14,2,9,14,5), P=(1,14), T=(2,9,14), e=1. This is full support and every unit conjugate sums 45. The phase-pair and phase-triple sums are both zero modulo 5. But c=sum(P)/5 is zero modulo q=3. The formal C_P therefore contains a zero entry and is not the claimed full-support Fermat curve character. This decomposable packet should exit through the earlier pair branch. The nondegenerate K23 branch must require c,d,e to be nonzero or handle degenerations separately.

**K23 rational realization.** Ordinary tensors of rational Galois packets are not automatically rank-one. Rank-one applies to chosen lines after cyclotomic splitting, or to an explicitly specified diagonal tensor component. A projector onto only the upper CM half-plane is not a rational full-orbit idempotent. A lower-conductor curve factor and an original-level packet can also have different rational dimensions. The desired correspondence must specify coefficient field, rational orbit, scalar extension or multiplicity, character projection and nonzero matrix coefficient. Matching CM signs alone supplies none of these algebraic maps.

**Universal grammar coverage.** The August conditional theorem lists correspondence assumptions and then classifies every seed by the grammar. Universal mixed-prime coverage has not been supplied. The documented finite coverage through 100 is not an all-degree theorem. The new theorem must be restricted to admitted packets or carry universal coverage as a separate assumption. Completing the K23 map would still leave this distinct coverage obligation.

**Prime-power minimum domains.** The displayed five-primary seed has zero last entry at r=1. Its formula requires r>=2. The p-element lifting-kernel mass argument applies at filtration s>=2. At base prime s=1, every odd character is primitive, and the nonzero odd Fourier coefficients give complement pairing directly. The three-primary seed also needs explicit representative and nonzero-entry bounds. These are domain corrections, not Hodge counterexamples.

**Degree 33 rational bridge.** The old text has a valid exact exponent identity but skips the compact rational Hodge lift. The target character freshly gives A^T a/33=(1,2,2,1,1,2), so the same full-support torus-carrier argument used at degree 70 supplies the missing bridge to the smooth cubic. A complex residue monomial is not itself a rational class. This addition belongs in the new reader, while the original short proof remains archived with its omission visible.

## Dyadic audit and historical coverage

The selected all-degree dyadic proof reconstructs coherently. The later August 15 status note lists uniform uniqueness as requiring a complete uniform write-up. That note does not identify a counterexample or a failed tree step. This audit records a selected manuscript reconstruction of the older argument, not a silent reversal of the later publication downgrade. The final reader may retain the uniform result at manuscript-review status. The later note is pinned separately in the claim cards. The even-coordinate triangle matrix is unimodular. Subtracting its integral reconstruction leaves an odd-support vector killed by the sawtooth matrix. Primitive odd Dirichlet Fourier values are nonzero, including their dyadic conductor lifts. The authenticated Sharifi source supplies the needed nonvanishing leaf in place of an unchecked book attribution.

The sign gauge turns defect mass into exact total variation on the augmented trivalent tree. Integer coarea and the forest boundary formula bound every defect of mass at most 6. The allowable shapes split into two surface atoms except a four-star. Two edge atoms cannot cover a star because K_(1,3) has no perfect matching. The star conductor determines full-conductor centers, which normalize to a single unit orbit. The displayed SAT3 multiset identity closes that orbit. These deductions are symbolic and independent of finite packet counts.

This audit did not independently re-enumerate the archived 89,478,480 weighted coefficient checks, all degree 100 mixed-prime packet counts, or all 364 K23 certificates. Those statements must retain their exact historical or fresh-replay labels from the computation report. This selected proof audit also does not cover every analytic Dolbeault, K-theory, family-propagation, support, ghost-algebra or Weil assertion in the wider historical corpus.

## External sources, formal scope and strongest safe publication

The exact external contracts are in `literature/CHECKED_SOURCES.md` and `literature/source_contracts.json`. In particular, the semisimplicity citation is Deligne Hodge II Lemma 4.2.3, not an unchecked Hodge III attribution. Aoki's original 1987 text was now obtained, including concatenation, complementary-pair removal, standard-cycle hypotheses and the historical equations. The first-order Weil deformation checks and a faulty secant-source eigenspace identification retain their separate narrow evidence boundary. No failed external source is promoted to a theorem.

The recovered Lean script assumes an arbitrary AlgPacket predicate, a seed and two closure inputs. It formalizes no schemes, Chow groups, mixed Hodge structures or correspondences. The current compiler probe failed before elaboration and there is no current Lean pass. See `formal/FORMAL_STATUS.md` for exact source pin and commands.

The strongest safe publication is a substantial conjecture exposition and constructive research record containing sound linear-algebra reductions under their corrected hypotheses, the dyadic combinatorial grammar, explicit special-case carrier and cycle constructions, exact global constructor obstructions, and clearly separated construction and coverage gaps. It is not a solution of the general Hodge conjecture. The cheapest next research check is to type one nondegenerate K23 target completely and certify one actual nonzero algebraic correspondence. Universal grammar coverage remains a separate theorem to prove even if that local map succeeds.

Proofreading self-review: routine prose spacing and typography were corrected in this report only. Mathematical assertions and original source files were not changed. JSON files parse successfully. Coverage is this report and its thirteen claim cards.
