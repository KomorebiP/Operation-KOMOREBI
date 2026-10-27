# Independent mathematical change audit

**Normalized claim.** The mathematical assertions introduced or clarified by the frozen 29-hunk proofreading diff are well-typed and follow under the stated local hypotheses and conventions; no changed hunk creates a new unsupported numerical or comparison conclusion.

**Primary verdict: proved as written.** This verdict is restricted to the frozen proofreading diff, not the full monograph.

**Scope.** Nineteen changed chapter files; 29 unified-diff hunks (31 localized editorial edits were reported by the editing team). Every changed hunk was reviewed against raw parent/revised passages and sufficient neighboring definitions/proofs. Relevant raw Lean declarations and proof bodies were inspected; all Lean files remain byte-identical to the parent. No source edits or Lean build were performed by this reviewer. No author review verdict was used as evidence.

## Dependency graph

- Declared real Hilbert/normed types + continuous linear operators -> operator-norm pointwise estimates -> triangle inequality -> KS69 reference-space certificate.
- Reference certificate + preserved old kernel + strict C*epsilon<1 -> absorbable error estimate -> equality of kernels and degraded gain in KS70.
- Same Hilbert correction ball + operator/data norm bounds -> two pointwise residual comparisons -> two infimum comparisons -> WR05; nominal WR04 dual lower bound -> robust lower certificate.
- Actual tower restrictions + monotone schedule -> typed block sums -> finite telescope -> schedule residual definition; dyadic odd lift -> divisibility support -> sharp first excluded coordinate.
- Cocycle and gauge definitions -> square-one relation/conjugacy; marked-arrow equations -> unique ordered solution. Functor hom maps -> categorical comparison definitions.
- Euclidean correction norm/Gram matrix -> workshop objective and optimizer; inverse edge isometry -> equal paired norms -> sqrt(2) residual scaling.
- Finite fibers + sequential restriction laws -> decreasing-image stabilization -> surjective persistent-image bonds -> coherent tower point and exact evaluation image.

## Critical independent derivations

**KS69/KS70.** Write u=x-qx. For KS69, Dx=(D-Dtilde)x+(Dtilde*x-y)+y gives ||Dx||<=epsilon||x||+eta+||y||; multiply by the nonnegative reference gain C. Kernel preservation makes Dtilde*q=0, so the same argument on u gives ||u||<=C||Dtilde*x||+C*epsilon||u||. Division uses only 1-C*epsilon>0 and also covers C=0. If Dtilde*x=0 this forces x=qx, proving the previously unassumed kernel inclusion. The projection remains that of the reference kernel until equality has been proved.

**WR05.** Both maps act on the same Hilbert correction space, with the same norm ball ||a||<=M. The residual difference is (r-rtilde)-(T-Ttilde)a, bounded by delta+eta*M. The reverse triangle inequality gives both pointwise comparisons. Taking infima over the identical nonempty ball gives the absolute profile bound. A nominal unit-ball dual witness lower-bounds the nominal profile, so subtracting delta+eta*M gives the claimed true-profile lower certificate. No relation between optimizers and no moving-kernel conclusion is needed.

**Dyadic endpoint and scheduled residuals.** The scheduled block sum has source X_phi(n+1) and target Y_phi(n), and is zero when the levels coincide. Fine differentials telescope without commuting operators. The dyadic lift inserts zeros at even indices; repeated odd lifts allow positions k+1 divisible by 2^N. In the identity scalar model, constant residual one leaves remainder 2^N at k=2^N-1, proving the revised first-excluded-coordinate wording.

**Metrics and examples.** Reverse-edge isometry preserves residual norm, so orientation duplication doubles the sum of squared norms and multiplies its square root by sqrt(2). For the workshop kernel basis (2,1), J(c)=(1-2c)^2+5c^2=9(c-2/9)^2+5/9; the correct output is (4/9,2/9), whereas c=2/5 has actual objective 21/25. The harmonic definition gives H_(n+1)-H_n=1/(n+1), matching the maximum-norm movement calculation.

**Finite towers and categorical definitions.** Decreasing nonempty images inside each finite X_n stabilize. Their stable sets have surjective adjacent restrictions, so recursive choice constructs a coherent point and lifts every persistent value. This uses the sequential tower hypothesis now explicit in the atlas. For a functor, faithfulness/fullness are respectively injectivity/surjectivity on each fixed source-target hom-set; essential surjectivity is up to isomorphism. The revised definitions give exactly these quantifiers.

## Obligation matrix

| Obligation | Status | Scope |
|---|---|---|
| General logic and typing | passed | All 29 changed hunks, including explicit bounded-linearity and same-source/same-target assumptions. |
| Quantifiers and admissible objects | passed | Sequential finite towers, arbitrary-cardinality finite-level views, category hom-sets, common correction balls, and real Hilbert vectors. |
| Boundary cases | passed | C=0, M=0, zero support vector, alpha>0, repeated schedule levels, N=0 dyadic depth, identity square-one group element, and H_0=0. |
| Metrics and normalizations | passed | Euclidean versus maximum norms, actual kernel Gram factor, and doubling of squared oriented residual norms. |
| Variance, actions, and composition order | passed | Contravariant restrictions in block residuals and multiplicative gauge/marked-arrow order. |
| Raw source correspondence | passed | Relevant declarations and proof bodies read directly; all Lean source files are byte-identical to parent. This is not a new Lean compilation claim. |
| Exact snapshot identity | passed | Independently compared archive bytes, changed-file manifest hashes, actual source difference set, and every TeX label list. |
| External theorem/literature re-verification | out of scope | No changed hunk introduces a new external source dependency. The finite-tower assertion is independently supported by the printed stabilization argument; unchanged citations and pinned library imports were not freshly fetched or compiled. |
| Fresh universal audit of unchanged theorems | out of scope | Only neighboring definitions/proofs necessary to validate changed semantic assertions were examined. |
| Full Lean build, PDF layout, figures, and final archive integrity | not addressed | Separate verification work; this report certifies the source snapshot specified below. |

## Complete changed-hunk review

### H01: source/chapters/01_views.tex:83 — Coherent-family implementation

**passed.** The unchanged definition is a dependent family satisfying every pullback equation. ViewSections.lean defines Ambient by exactly that subtype; the revised explanatory statement does not identify the category of elements with the set of coherent sections.

### H02: source/chapters/02_obstructions.tex:110 — Parity reference

**passed.** The printed KS09 criterion applies to the two-view equation 2m=k. There is one integer preimage exactly for even k. A disconnected unprescribed integer coordinate contributes an independent Z ambiguity, as KS10 states. Removing the historical source qualifier does not change this claim.

### H03: source/chapters/02a_prescription.tex:88 — Finite-tower criterion

**passed.** The new explicit reference is to KS58, whose hypotheses are a sequential system of nonempty finite sets. Its persistent-image proof in 06_boundaries.tex establishes existence and the exact prescribed-value criterion. No general infinite compatible-choice claim is introduced.

### H04: source/chapters/03_towers.tex:320 — Normed split coarsener

**passed.** The actual formula inserts zero in even positions and a target section in odd positions; the identity rho*s=I gives CJ=I. Uniform section and bonding bounds are retained by the surrounding normed construction. Removing original does not remove a hypothesis.

### H05: source/chapters/03_towers.tex:414 — Actual dyadic hierarchy

**passed.** The preceding displayed coarsener/lift are the varying-fiber hierarchy referred to. If all details vanish, an even coordinate is zero and an odd coordinate is a section applied to the next-level coordinate with smaller index. Strong induction at all starting scales gives zero; no scalar substitute or norm-convergence claim is used.

### H06: source/chapters/03_towers.tex:445 — Strict dyadic cutoff

**passed.** The guaranteed prefix is k+1<2^N, so its first excluded coordinate is k=2^N-1. In the identity-bonding scalar hierarchy, the constant residual one has restored remainder 2^N at that coordinate. The corrected next-coordinate wording is sharp, including N=0.

### H07: source/chapters/03a_observation.tex:2 — Finite level versus finite cardinality

**passed.** Resolution.Obj is an arbitrary natural-number-indexed type family; FinitelyObserved factors each output coordinate through some input level and has no Finite instance. The added explanation matches these definitions and keeps the later finite-fiber existence hypothesis separate.

### H08: source/chapters/03b_repair_transport.tex:147 — Schedule residual definition

**passed.** Monotonicity gives a=phi(n)<=b=phi(n+1). Each term rhoY[a,k] r_k rhoX[k+1,b] maps X_b to Y_a, exactly the sampled residual fiber. At repeated levels the sum is empty and equals zero. Substitution of the fine differential telescopes to the sampled differential. Boundedness still requires the later uniform gap bound.

### H09: source/chapters/04_symmetry.tex:4 — Nonabelian coefficient terminology

**passed.** The cocycle/gauge formulas use group multiplication in fixed order and only assume groups and restriction homomorphisms. Need not be abelian states the intended lack of commutativity without treating separate groups as elements that commute.

### H10: source/chapters/04_symmetry.tex:166 — Square-one cocycles

**passed.** The unique nonidentity C2 arrow requires p*p=1, which includes p=1. CocycleExamples.loopCocycleEquiv has precisely the subtype {p // p*p=1}. In S3 these are identity plus three transpositions, with two conjugacy classes. The remaining phrase nonidentity involution has the conventional order-two meaning.

### H11: source/chapters/04a_boundary_lab.tex:48 — Two-view versus finite model

**passed.** The view category has two objects but the coefficient group H is arbitrary. The marked-arrow equations solve uniquely as a0=psi^-1 phi and a1=(rprime)^-1 a0 r in that order; no finiteness of H is needed. Two-view is the accurate scope.

### H12: source/chapters/05_geometry.tex:342 — Joint orthogonal projection

**passed.** Px lies in M and x-Px=(x-P_Lx)+(P_Lx-Px) is perpendicular to M. Therefore Px is the orthogonal projection of the input x, rather than a projection of the error. The restricted second-stage construction and its norm identity agree with QuantitativeDescent.repair_eq_projection.

### H13: source/chapters/05_geometry.tex:617 — Original exact vector

**passed.** Original exact means Dx=0. For a unit x perpendicular to ker Dprime, qprime*x=0 and Dprime*x=(Dprime-D)x, hence 1<=Cprime*||Dprime*x||<=Cprime*epsilon. The revision changes terminology only.

### H14: source/chapters/05a_certificates.tex:20 — Bounded linear measured operator

**passed.** The added bounded-linearity assumption types the operator difference norm and matches e:E ->L[real] R in ResidualPerturbation.lean. The norm triangle and the given reference certificate prove KS69. KS70 still requires preservation of the old kernel plus C*epsilon<1 and concludes equality rather than assuming it.

### H15: source/chapters/05a_certificates.tex:42 — Euclidean measurement example

**passed.** For D(a,b)=a and Dtilde(a,b)=a+t*b on Euclidean R2, the orthogonal projection is (0,b), the least gain is 1, and ||D-Dtilde||=|t|. At x=(-tB,B), Dtilde*x=0, the reference distance is |tB|, and |t|*||x||=|t|*sqrt(1+t^2)*|B|. The explicit norm declaration makes these numerical statements unambiguous.

### H16: source/chapters/05e_escape.tex:34 — Constant square-summable sequence

**passed.** If u_n=-t for every positive integer n, the first N squared entries sum to N*t^2. Finite total square sum forces t=0 and u=0. The new wording preserves the exact kernel/nonfeasibility conclusion.

### H17: source/chapters/05g_budget_certificates.tex:60 — Full range as union of budget images

**passed.** Every a has finite norm, so ran(T) is the increasing union over M>=0 of T(closedBall(0,M)), whether or not the full range is closed. In the Hilbert setting each budget image is closed by a weak subsequence of bounded lifts and convex by linearity. The revision removes the accidental suggestion that nonclosedness was assumed.

### H18: source/chapters/05g_budget_certificates.tex:101 — Zero support-vector/radius cases

**passed.** The support pairing is <a,T*z>. If T*z=0 it vanishes for every feasible a; if M=0 the only feasible a is zero. Hence every feasible pairing, not merely its maximum, is zero in either exceptional case. For M>0 and T*z nonzero, a=M*T*z/||T*z|| attains M*||T*z||.

### H19: source/chapters/05g_budget_certificates.tex:133 — Bounded linear nominal budget map

**passed.** The new assumption matches S:H ->L[real] Y in BudgetRobustness.lean. Both profiles use the same H norm and same ball. For each feasible a, residual-norm difference is at most delta+eta*M; taking infima in both directions proves WR05. The nominal dual lower bound follows by subtracting this allowance from WR04. No changing-kernel comparison is claimed.

### H20: source/chapters/05h_regularized_repair.tex:199 — Minimum-norm least-squares description

**passed.** When b=P_closure(ranT)r is attained, the preimages of b are exactly the least-squares corrections by orthogonal decomposition. The minimum-norm preimage a-dagger is the same selected limit as in WR08. Reordering the phrase does not change the selected object.

### H21: source/chapters/05h_regularized_repair.tex:210 — Data vectors

**passed.** r and rtilde are vectors in the same real Hilbert target, with the same T and positive alpha. Adding vectors merely makes their type explicit; the data-sensitivity quantifiers and constants remain unchanged.

### H22: source/chapters/05j_inexact_certificates.tex:68 — Identification of sharp bounds

**passed.** For alpha>0, T=0 gives g=alpha*e and equality in ||e||<=||g||/alpha. T=sqrt(alpha)I gives g=2alpha*e and equality in ||Te||<=||g||/(2sqrt(alpha)). The names now identify the correct first two estimates without claiming simultaneous sharpness for all operators.

### H23: source/chapters/06_boundaries.tex:16 — Categorical comparison definitions

**passed.** For R:S->K, faithfulness is injectivity of each map Hom_S(A,B)->Hom_K(RA,RB); fullness is its surjectivity for every A,B; essential surjectivity is that every K-object is isomorphic to some RA. The revised paragraph gives these exact quantifiers and distinguishes equality from isomorphism.

### H24: source/chapters/06_cases.tex:171 — Reverse-edge residual geometry

**passed.** For inverse isometric transports, the reversed residual equals minus the inverse transport applied to the forward residual, so their norms agree. Duplication doubles the sum of squared residual norms and multiplies its square root by sqrt(2), leaving the exact kernel and source distance unchanged. The least gain 1 becomes 1/sqrt(2); the maximum residual norm is unchanged.

### H25: source/chapters/09_workshop.tex:44 — Harmonic path definition

**passed.** With H_n=sum_{j=1}^n 1/j (H_0=0), the harmonic increment is 1/(n+1). The other residual-coordinate increment is 1/((n+1)(n+2)); the maximum norm therefore gives the claimed steps. Dividing by residual 1/(n+1) yields C_n=1 for drift and C_n=1/(n+2) for the convergent path.

### H26: source/chapters/09_workshop.tex:69 — Euclidean basis metric

**passed.** On ker p=span(2,1), a=(2c,c) has squared norm 5c^2. Thus J(c)=(1-2c)^2+5c^2=9(c-2/9)^2+5/9. The stated optimizer and objective follow. Omitting the Gram factor gives c=2/5, whose actual objective is 1/25+20/25=21/25. The Euclidean declaration is necessary and correct.

### H27: source/chapters/10_hypothesis_atlas.tex:11 — Sequential finite-fiber scope

**passed.** The atlas now includes the sequential inverse-system condition of KS58. Nonemptiness of all finite fibers alone for an arbitrary diagram is not substituted for the stated tower hypothesis. The persistent-image condition on a prescribed value is retained.

### H28: source/chapters/10_hypothesis_atlas.tex:52 — Companion guide name

**passed.** The named source Komorebi_Space_Lean_Guide.tex and corresponding PDF exist. Renaming the guide reference makes no mathematical/formal-coverage assertion beyond the unchanged paragraph; its general verification claims were not re-certified by this semantic diff audit.

### H29: source/chapters/12_proof_tools.tex:99 — Explicit analytic step

**passed.** The sentence now describes the derivation as explicit rather than missing. Its subject remains the continuous inverse for complete source/target spaces after bijectivity is established. No hypothesis, proof step, or theorem conclusion is changed.

## Snapshot and provenance

Parent archive SHA-256: `1eec4e02d890a07d80df30220aa05fd3c5fd8be0a9476abbab404591ee0fa8e8`.
Diff SHA-256: `aee84f484b1e3e6a1f4769a378d03578c5c082fe38860ccafd83e1d4e4fac542`.

The following before/after hashes were independently recomputed from the archive and revised source, rather than accepted from the supplied manifest. The manifest matched every value and the exact changed-file set. All existing TeX label lists matched the parent.

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| source/chapters/01_views.tex | `5fc06575fd78316dbf0865f5895582c0fc8b8894f378881dd413b3e885d74a8c` | `58ce7c22e9b8a5ad25d510e6b8d2a24a138677450bc21d833385ac39f0614b77` |
| source/chapters/02_obstructions.tex | `6b837a0a7c03a2f3bc6d1c82ca3e7c63ef25a0f9d7bb81e7482b07a791abaa88` | `106ebdbd8fd7271cf5bec2d52369d20c37c6b2d7358ae9dbdddd00149976d0d0` |
| source/chapters/02a_prescription.tex | `f4dbb208cb264a6aa0806e1841f2f95aff34484940b57e82fac9c86d1a42c7cd` | `5551541408db826a79e22fab5cba64bd3f42282e498d45ec4ddf0ac59120ea0f` |
| source/chapters/03_towers.tex | `95c398067329f39ebba6b3b2388c51a1012f1aa3da0b302f02633401cd0cb6c7` | `577f76958dcc8b7b5d9c7be6a15ea42014b97146a94993466780dd1f38a42cfd` |
| source/chapters/03a_observation.tex | `9a644067876415d1456fa36d804b3106e556b5f3ad4f15176e58936751a102cb` | `a67f0aa6167d1697e14a7527e0ff9310a7f1b91e45d8bef1eed52e876e7f6024` |
| source/chapters/03b_repair_transport.tex | `5b90a3abbedd9271b79507b12295a229f1084bf7f23e8dd1d8216bfaa4a5d44a` | `208348b8d211f731643971bb9409c8f4e1abbfc3b5a4b3a8e596e59053833a3e` |
| source/chapters/04_symmetry.tex | `f1f4aee9ff003b42a5667729af12b6a800e955f310c9d4ed87b41d0b4ba27f35` | `e2d936f0df8ad271ae2be279a8538c9085a9caaa91a1bf14c147b003667f437c` |
| source/chapters/04a_boundary_lab.tex | `ddb9f1c14c7137303221a28d682c958efc8fef367122fcb0ec5569f47ec157f1` | `0015cd8ae217c2a9e89e0185f2ba3cc6bbe8dbcbb05a562380a413b7fc174e31` |
| source/chapters/05_geometry.tex | `b673686a8ef6d6018f30d6d79191d2cdc7dcecc24ba7bcda6e173f923a1157f9` | `b2939693dc59a726eef302c8163535ed79b747f2881d1290cfc73d84dd78e913` |
| source/chapters/05a_certificates.tex | `8185e8313d45ccd1150f83f599a5edd862f67dc2b0af96d4086a53e0bb851b26` | `94510b1a8bfc2eec7e5c6cb8baa73ac412d766c8296d38ba3b476e3e909766f0` |
| source/chapters/05e_escape.tex | `72f3b19c0460f27d088b51403e40fe2bf4e36a682f51737e3d32263723ee7960` | `2c71d289c6b88061387f62f91f11bd9e15a2f2deb2104d593d1a7987208cfc50` |
| source/chapters/05g_budget_certificates.tex | `e17eaf134e1dae15bdbd471c573a8345037c8eb590b6e77f5246ae93c7f43c01` | `6f653ebd221d1a49547887a1e0ec737ddee7171961a1dc1d3c4a1afcc6e24cd9` |
| source/chapters/05h_regularized_repair.tex | `02de2bb0b44310e2b910f3228b08be1bcd536d97f7adddd6377a7805acbbe443` | `09afab8232c724334ab5dad33bdd09a4bacc59f315e2633a1349d08eac7446c5` |
| source/chapters/05j_inexact_certificates.tex | `9c8a5a5eeee79363a6d4cd565df7358a3674448ceafdfe8c2ef90734dae0e093` | `a79c3f0213a593129aa1c17cf80804e738d8f62984b1812cbb642731479135f5` |
| source/chapters/06_boundaries.tex | `87e259da118b70bba1fdad69feaa01e107410c66a7fd7ba9e00952809ccbafdf` | `409bb7e54ad80b5b8f7759d2656d465cd891e69855f818fb8688b5754047ba61` |
| source/chapters/06_cases.tex | `924b41f8df0db1d747f1baf39d2a22e0f1f9e53b21c19e3a61cc287478c59e79` | `881b88e51dcd2b1c4a2739b24a504c46d207becf8f79cab65c653a2b01d1f91a` |
| source/chapters/09_workshop.tex | `c26e8bdfc989742f42dfea8dcce57827d87dd22bd8efe6a006fa2d782db64a7a` | `a5ea04dba30d0c1afcabe1dd7570fe002d54597d7a1acc6c2337137a766b6257` |
| source/chapters/10_hypothesis_atlas.tex | `fe2d56989d03d99122cfda9ea291e78c19648dca01d073dfe333aec6554dbb44` | `5312cfc7c03d818ee314ee0d24034619461c8a8839ccd44483060bc725c4cdeb` |
| source/chapters/12_proof_tools.tex | `27d16a96d6574ba66bd698cf8d7326f56f6d93fa4ed4144c449e32db8eb42165` | `7431e594c67364e7547924ad1af0e70ed80f4f214d6828b1563ce144499d0fbe` |

The accompanying JSON records the hashes of the 21 raw Lean files inspected and the machine-readable hunk matrix.

## Remaining gap and next check

None for the frozen changed-hunk mathematical claim. Unchanged theorem validity, fresh kernel checking, layout and package delivery are outside this verdict.

All mathematical meaning introduced or clarified by these 29 frozen diff hunks is supported by the reviewed raw context and independent derivations, with the stated hypotheses and metrics. This does not certify the entire monograph anew.

Use a byte/hash comparison to ensure packaging retains this exact reviewed source snapshot; rerun this diff audit only if a mathematical hunk changes.
