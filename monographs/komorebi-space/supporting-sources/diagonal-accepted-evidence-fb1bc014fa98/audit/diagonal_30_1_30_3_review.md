# Independent claim-match audit: Proposition 30.1 and Corollary 30.3

**Primary verdict: proved as written.** This verdict applies to the two printed target conclusions and their stated contract obligations for the exact source hashes below. Every in-scope obligation passed; no mathematical mismatch or unresolved gap was found. Theorem 30.2 is outside scope.

The assessment uses the raw definitions, theorem types, proof code, and relevant pinned-library definitions, plus independently derived critical implications. Author completion labels and review verdicts were not used as mathematical evidence. Compilation and axiom checks are reported separately from the mathematical reasoning.

## Exact claim and model

For all natural m>=1 on real l2(N), with positive printed coordinate n=j+1 and alpha=1/m^2, a_n=m^2/(m^2+n^2) is the unique global minimizer of ||Tx-w||^2+alpha||x||^2. Its residual is v_n=n/(m^2+n^2). A=||a||^2 and B=||v||^2 are the full infinite sums; m/4<=A<=4m/3 and 1/[4(m+1)]<=B<=2/m. For all natural K>=m, prefixes contain exactly n=1,...,K, and 0<=A-A_K<=m^4/(3K^3), 0<=B-B_K<=1/K.

For b_n=1/n^2 and its unique minimum-norm preimage w_n=1/n, c_n=m^2/[n(m^2+n^2)] is the regularized correction at alpha=1/m^2 and ||c-w||^2=B. For every s in the full l2 with ||s-b||<=delta, 0<delta<=1, and literal m=ceil(delta^(-2/3)), ||correction(T,alpha,s)-w||<=sqrt(2/m)+delta*m/2<=(sqrt(2)+1)delta^(1/3).

The `lp` type is mathlib's full square-summable function space on `Nat`, with real scalar Hilbert structure. `index j = (j:Real)+1` implements the printed positive index. `range K` contains `j=0,...,K-1`, hence exactly printed coordinates `1,...,K`; the remainder uses `j+K`, hence starts at printed `K+1`. All norms are the `lp` Hilbert norms, and `norm_sq_eq_tsum` identifies them with the infinite squared-coordinate sums.

The exported claim is represented by `proposition_30_1` together with `a_unique_minimizer` and the coordinate definitions/lemmas. The latter explicitly quantifies every competitor in the full Hilbert space. `corollary_30_3` itself states both noisy inequalities for an arbitrary element `s:H`, with the literal natural ceiling; it has no remaining exact-data-bias hypothesis.

## Obligation matrix

| ID | Obligation | Status | Raw evidence and finding |
|---|---|---|---|
| O01 | Frozen target and inherited dependency binding | passed | Printed chapter is byte-identical to parent 05i_diagonal_regularization.tex; inherited RegularizedHilbertRepair and BudgetProfile are byte-identical to the specified parent ZIP. Evidence: `Direct ZIP-byte comparison; BASELINE.json checked`. |
| O02 | Actual infinite real Hilbert space | passed | H is lp (fun _ : Nat => Real) 2. Membership requires the full squared-coordinate series to converge. There is no finite dimension or support bound. Evidence: `H; hilbert_mem_of_sq_summable; mathlib Memℓp/lp/inner_eq_tsum`. |
| O03 | Positive coordinate and finite-prefix convention | passed | index j = j+1; Finset.range K is exactly printed n=1,...,K. The shifted remaining series starts at n=K+1. Evidence: `index; partialA; partialB; A_sub_partial_eq_tsum; B_sub_partial_eq_tsum`. |
| O04 | Parameter, denominators, and domain | passed | m>=1 makes alpha=m^(-2)>0; j+1>0 gives all coordinate denominators positive. K>=m makes K>=1. Evidence: `index_pos; denominator_pos; alpha_pos; proposition_30_1_series`. |
| O05 | Bounded operator and adjoint | passed | T u has coordinate u_j/(j+1), acts on the full H, has operator norm <=1, and is self-adjoint by the infinite inner-product formula. Evidence: `Tlinear; T; T_apply; T_opNorm_le_one; T_adjoint`. |
| O06 | Square summability and vector construction | passed | w, a m, v m are genuine elements of H using p=2 and p=4 series comparisons; b and c are images under continuous T. Evidence: `summable_wCoord_sq; summable_aCoord_sq; summable_vCoord_sq; w; a; v; b; c`. |
| O07 | Displayed a is the universal regularized correction | passed | For every m>=1, its coordinate normal equation lifts by lp.ext to a Hilbert-vector equality, and normal_unique identifies a with correction T alpha w. Evidence: `a_apply; a_normal; a_eq_correction; RegularizedHilbertRepair.normal_unique`. |
| O08 | Unique global minimizer over all H | passed | The objective is ||T x-w||^2+alpha||x||^2. The wrapper quantifies every competitor x:H and every possible global minimizer; the energy identity yields uniqueness. Evidence: `a_unique_minimizer; RegularizedHilbertRepair.energy_identity/correction_best/correction_unique`. |
| O09 | Residual and actual infinite norm identities | passed | w-T(a m)=v m; ||a m||^2=A m and ||v m||^2=B m are the full infinite squared norms with the displayed rational summands. Evidence: `residual_eq_v; norm_sq_eq_tsum; norm_a_sq; norm_v_sq; A; B`. |
| O10 | A lower bound m/4 | passed | All m coordinates n<=m contribute at least 1/4; full series dominates the prefix. Evidence: `aCoord_sq_lower_prefix; A_lower`. |
| O11 | A upper bound 4m/3 | passed | The first m summands are <=1; the remaining sum is <=m^4/(3m^3)=m/3. Evidence: `partialA_upper; A_tail_upper; A_upper`. |
| O12 | B lower bound 1/(4(m+1)) | passed | For n>m the summand is >=1/(4n^2); exact lower telescoping comparison gives sum_{n>m} n^(-2)>=1/(m+1). Evidence: `vCoord_sq_lower_tail; series_tail_sq_lower; B_lower`. |
| O13 | B upper bound 2/m | passed | The first m summands are each <=1/m^2; the remaining sum is <=1/m. This valid proof differs from the printed sum-of-squares route. Evidence: `vCoord_sq_upper_parameter; partialB_parameter_upper; B_tail_upper; B_upper`. |
| O14 | Finite-cutoff A tail | passed | For every K>=m, 0<=A-partialA<=m^4/(3K^3), with exact full-minus-prefix equality before comparison. Evidence: `A_sub_partial_eq_tsum; A_tail_nonneg; A_tail_upper`. |
| O15 | Finite-cutoff B tail | passed | For every K>=m, 0<=B-partialB<=1/K, with exact full-minus-prefix equality before comparison. Evidence: `B_sub_partial_eq_tsum; B_tail_nonneg; B_tail_upper`. |
| O16 | Actual attainable b and minimum-norm preimage | passed | b_j=1/(j+1)^2, w_j=1/(j+1), T w=b. Since every multiplier is nonzero, T is injective, so w is the unique preimage and thus minimum norm. Evidence: `b_apply; w_apply; T_w_eq_b; T_injective; b_preimage_unique; w_minimum_norm_preimage`. |
| O17 | Actual c and its universal optimizer identity | passed | c=T(a m) has the displayed m^2/[n(m^2+n^2)] coordinates, and applying T to the a-normal equation proves the b-normal equation. Evidence: `c_apply; c_normal; c_eq_correction`. |
| O18 | Bias is the same infinite residual | passed | w-c=v and ||c-w||^2=B, with norm symmetry handling the sign. The bound sqrt(2/m) is discharged for actual b. Evidence: `w_sub_c_eq_v; norm_bias_sq; diagonal_bias_bound`. |
| O19 | Arbitrary full-Hilbert noisy datum | passed | s ranges over every H, constrained only by ||s-b||<=delta and the stated delta range. No coordinatewise, finite-support, probabilistic, or extra bias hypothesis remains. Evidence: `diagonal_noisy_error; corollary_30_3`. |
| O20 | Sharp propagated noise term | passed | The universal estimate is ||correction(s)-correction(b)||<=||s-b||/(2 sqrt(alpha)); alpha=m^(-2) and m>0 give delta*m/2. Evidence: `RegularizedHilbertRepair.correction_data_energy/data_noise_squared/data_noise_bound; noisy_error_of_bias_bound`. |
| O21 | Literal ceiling and real powers | passed | The final theorem literally sets m=Nat.ceil(delta^(-(2:Real)/3)); delta^(1/3) uses real exponentiation. Positive delta makes m>=1. Evidence: `noiseSchedule; one_le_noiseSchedule; corollary_30_3`. |
| O22 | Ceiling factors and final constant | passed | For 0<delta<=1, u=delta^(-2/3)>=1 and u<=m< u+1<=2u. Hence sqrt(2/m)<=sqrt(2)*delta^(1/3) and delta*m/2<=delta^(1/3). Evidence: `noiseSchedule_bounds; noiseSchedule_bias_bound; noiseSchedule_noise_bound; noiseSchedule_rate`. |
| O23 | Full target interface with no added mathematical hypotheses | passed | proposition_30_1 combines vector identities and all bounds/tails; a_unique_minimizer supplies explicit global uniqueness. corollary_30_3 carries both inequalities with the actual model. Evidence: `DiagonalTheorems.lean; actual elaborated types printed independently`. |
| O24 | Kernel axiom boundary for final declarations | passed | Fresh recursive #print axioms for proposition_30_1 and corollary_30_3, and six model/interface declarations, report only the three permitted standard axioms. Evidence: `Independent stdin elaboration, exit 0, warnings rejected`. |
| O25 | No admission or project-axiom substitution in reviewed new source | passed | Token scan of the five new reviewed modules found no sorry, admit, axiom, or unsafe occurrence; raw source and final recursive axiom output were also inspected. Evidence: `Five raw module sources and fresh recursive axiom output`. |
| S01 | Theorem 30.2 and live asymptotic modules | out of scope | No verdict on pi/4 series asymptotics, all-real-budget transfer, or hard-prefix limiting comparison. Evidence: `Explicit parent scope`. |
| S02 | Full clean dependency rebuild | out of scope | No full build was run. The fresh check elaborated the raw theorem interface against existing imported artifacts; final complete build provenance is the parent build task. Evidence: `Explicit parent scope`. |
| S03 | Every surrounding expository sentence as a separately named Lean theorem | out of scope | Ambient protected-coordinate prose and growth/asymptotic commentary are not added target obligations. The auxiliary printed ||T||=1 follows mathematically using the first unit vector, but only <=1 is a named declaration here. Evidence: `Target conclusions and contract delimit this audit`. |

Counts: 25 passed, 0 failed, 0 conditional, 0 not addressed, 3 out of scope.

## Critical implications derived independently

**C1 — Normal equation identifies a global, unique minimizer.** For n=j+1>0, (n^(-2)+m^(-2))*m^2/(m^2+n^2)=n^(-2). This is (T*T+alpha I)a=T*w in H, not merely coordinates outside H. For any competitor x, expansion gives J(x)-J(a)=||T(x-a)||^2+alpha||x-a||^2. Both terms are nonnegative, and alpha>0 forces x=a at equality.

**C2 — Infinite tails have the claimed orientation and constants.** For x>0, 1/x-1/(x+1)-1/(x+1)^2=1/[x(x+1)^2]>=0; 1/x^2-(1/x-1/(x+1))=1/[x^2(x+1)]>=0; and 1/(3x^3)-1/(3(x+1)^3)-1/(x+1)^4=(6x^2+4x+1)/[3x^3(x+1)^4]>=0. Finite telescoping at x=K+j gives the upper bounds 1/K and 1/(3K^3). The lower square comparison starts at x=K+1, giving 1/(K+1) after the reciprocal remainder tends to zero. Summability is established before identifying norms and tails.

**C3 — All four bounds follow without a truncation surrogate.** For n<=m, a_n>=1/2, yielding A>=m/4. With a_n^2<=1 on the prefix and <=m^4/n^4 outside it, A<=4m/3. The elementary inequality mn<=m^2+n^2 gives v_n^2<=1/m^2, so the prefix contributes <=1/m; the tail contributes <=1/m. For n>m, v_n>=1/(2n), and the lower reciprocal-square tail gives B>=1/[4(m+1)].

**C4 — Actual attainable datum and bias, not an assumed generic model.** T w=b coordinatewise. All weights 1/(j+1) are nonzero, so the preimage is unique. T commutes with its normal operator because T*=T and alpha is scalar; applying T to the a-normal equation gives the c-normal equation for c=T a and b=T w. Thus c is the universal correction for b. Algebra gives w-c=v, and the norm square is B.

**C5 — Sharp deterministic noise amplification and literal rounding.** For e=correction(s)-correction(b), the normal equation gives ||Te||^2+alpha||e||^2=<s-b,Te><=delta||Te||. Completing the square yields 4alpha||e||^2<=delta^2. With sqrt(alpha)=1/m this is ||e||<=delta*m/2. The triangle inequality adds bias <=sqrt(2/m). Put u=delta^(-2/3)>=1 and m=ceil(u), then u<=m<=2u. Because u*(delta^(1/3))^2=1 and delta*u=delta^(1/3), the two terms sum to at most (sqrt(2)+1)delta^(1/3).

The tail proofs use exact finite telescoping and convergence, rather than the manuscript's integral-comparison presentation. The upper bound for the first `m` residual summands uses the simpler global estimate `v_n^2 <= 1/m^2`, rather than the printed sum-of-squares calculation. Both routes establish the same constants under the same target hypotheses.

At `m=1`, `K=m`, and `delta=1`, the indexing, positivity, and ceiling estimates remain valid. The final theorem excludes `delta=0` exactly as the printed statement does. It does not assume finite-support noise, a stochastic noise model, or closed range of `T`. The minimum-norm assertion for the attainable datum is stronger here: every preimage equals `w`, by injectivity.

The relevant inherited objective is exactly `||T x-r||^2 + alpha*||x||^2`. Its coercivity assumption is `alpha>0` on complete real Hilbert spaces. The Lax–Milgram equivalence is used with those hypotheses discharged; the direct energy identity independently explains why the candidate is globally optimal and unique. `BudgetProfile.beta` was checked to be the distance to the image of the actual closed norm ball. No conclusion about its asymptotic limit is included.

## Type, axiom, and source binding

The printed target file is byte-identical to `source/chapters/05i_diagonal_regularization.tex` in the authoritative parent archive, SHA-256 `67e308826abe33873e1d99d6fcf70bb14df65d6b511597b295b0bf430520a990`. The inherited `RegularizedHilbertRepair.lean` and `BudgetProfile.lean` also match their parent bytes.

The existing raw Hilbert, series, and noise axiom/type outputs were inspected. The `SOURCE_SHA256` at the head of the existing noise log binds its probe file `records/noise_axioms.lean`, not the imported noisy-rate module; the module is hashed separately below. The empty theorem-interface compile log alone is not treated as proof of a successful build.

A fresh independent narrow check passed: the current raw `DiagonalTheorems.lean` was elaborated via stdin using `scripts/lean_env.sh lake env lean -DwarningAsError=true --stdin` in `lean/`, followed by `#print` and `#print axioms` for `H`, `T`, `a_unique_minimizer`, `proposition_30_1`, `corollary_30_3`, `c_eq_correction`, `norm_bias_sq`, and `w_minimum_norm_preimage`. Exit status was 0 and stderr was empty. Every recursive axiom list contained only `propext`, `Classical.choice`, and `Quot.sound`. The exact stdin SHA-256 is `3b308428ad1961f413bbeef412b1a877099fc6b812a9d4bbe2b80181ea816e31`; stdout SHA-256 is `e53e9ddaa36346a70165915770009a3099202a1f4c10fb971568bc5bb3ba437a`. The raw output is in the tool transcript and these digests make the deterministic probe reproducible. No `-o` or other artifact-output option was used.

Observed compiler: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release). Both the manifest pin and checked-out mathlib revision are `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. A source scan of all five reviewed new modules found no `sorry`, `admit`, `axiom`, or `unsafe` token. The final recursive axiom lists provide the stronger check against hidden project axioms for the audited declarations.

## Exact input hashes

| Role | Input | SHA-256 |
|---|---|---|
| primary | `records/TARGET_CONTRACT.md` | `55d1cae3ffa7d9b7a48678b08cd34312286736e81682b174ba4b3a573d5481f7` |
| primary | `proofs/PRINTED_DIAGONAL_THEOREMS.tex` | `f10d921f0272d27f0894547767736c32c5f094c7f77a4016b400527a73a229c2` |
| primary | `lean/KomorebiSpace/DiagonalDefinitions.lean` | `751bf02816f74e2fe8a8bc9f45c22f9538d087d1af536af3835e4906f4015f54` |
| primary | `lean/KomorebiSpace/DiagonalSeriesBounds.lean` | `fc606b9db34f39179ba3cedcc43504325bd14dfdba6de8c46ad7bd6a70a31cb2` |
| primary | `lean/KomorebiSpace/InfiniteDiagonalModel.lean` | `da72d7f6ccaa870581c23409837955e54db8be2a732354716e908fe9266501d2` |
| primary | `lean/KomorebiSpace/DiagonalNoisyRate.lean` | `55ad01c40e768c2ab7d70895ff5576c2576751137ebb7994198f1ebe27e2d21e` |
| primary | `lean/KomorebiSpace/DiagonalTheorems.lean` | `5b6200399270a02d87fc9e578137e5a8a496d404fa042a419f7a1ba138b207d7` |
| primary | `lean/KomorebiSpace/RegularizedHilbertRepair.lean` | `b57ee2a27d7c30e35c17a90655aad21a967ae73f830d84ee81a22a2c92276ae4` |
| primary | `lean/KomorebiSpace/BudgetProfile.lean` | `a11931c108e046080539e346bbf910a99395da0ee51dc8634f8101bb9c95170f` |
| binding_evidence | `records/BASELINE.json` | `4df78e95e2e288746c669b5ad79f9de6ff3aac2df98c5b6ce3b22e03eb91c0cb` |
| binding_evidence | `scripts/lean_env.sh` | `14c76783600717d3d74aa0cf7d38541ec6088cd1d1734ea69732f611dafffb34` |
| binding_evidence | `lean/lean-toolchain` | `8190e75a201741065fe508b28955dd64dd72d090babe5f70ce6848879d68ae88` |
| binding_evidence | `lean/lake-manifest.json` | `7e28e00cb45e028f411ea69972d18a9964f4c3affaf0212389afa9d1fe13df47` |
| binding_evidence | `logs/hilbert_axiom_audit.lean` | `bd017d67c30f9551aa950222df2e371e591a1069b49dfa6bbb233f19ef7bf1e1` |
| binding_evidence | `logs/hilbert_axiom_audit.log` | `6cf8060df7df9217fb8c95794a7a4294cc0a4b7ebc38ed63c5e6fb4e25c2d922` |
| binding_evidence | `records/series_axioms.lean` | `809bc7c656b6a1a4218789a4027ae95b2d7a019e38ef76ca8e0a86d793d21179` |
| binding_evidence | `logs/series_axioms.log` | `288699d5f04d8362863338b5dbe9ee403dab0fefa9047aaa1fa8067c4f9a1057` |
| binding_evidence | `records/noise_axioms.lean` | `7d9c1dc93a313e6611bd70ab66b79d5b506cb0f2d16da1b15bbaf464e00d486f` |
| binding_evidence | `logs/noise_axioms_001.log` | `a9d3bccba4ec395ea4bb623887b02b17b07b536419848934e46da79b93181789` |
| binding_evidence | `logs/theorem_interface_001.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| binding_evidence | `records/hilbert_inventory.json` | `cbe3ccfd5a2fdd6c27847f573066866fa6acd603898af6f0bb6d3d26624683c3` |
| pinned_library_leaf | `lean/.lake/packages/mathlib/Mathlib/Analysis/Normed/Lp/lpSpace.lean` | `20be210fd24a56462a072e57e9adfaa68020010a198ce016a30bd615c11813af` |
| pinned_library_leaf | `lean/.lake/packages/mathlib/Mathlib/Analysis/InnerProductSpace/l2Space.lean` | `b676e33fe380e3672f4472900aee9ae28516b127edd0174cab4c3d91b84a765c` |
| pinned_library_leaf | `lean/.lake/packages/mathlib/Mathlib/Analysis/PSeries.lean` | `d9d4d77f20ce7b777a713b21059694612f38b6498e9d5659f3e73bb921d1f595` |
| pinned_library_leaf | `lean/.lake/packages/mathlib/Mathlib/Analysis/InnerProductSpace/LaxMilgram.lean` | `eba401b4723e7107cb57769a28232f1f1d1eb670eaca647f7cdc66a9c67091cb` |

## Scope and limitations

- This is an independent claim-match and mathematical dependency review of Proposition 30.1/WR10 and Corollary 30.3/WR12, not a proof audit of the entire monograph or all pinned mathlib proofs.
- Theorem 30.2/WR11 and live asymptotic modules are outside scope. Reading the budget-profile definition and its direct bridge does not certify the asymptotic theorem.
- Fresh Lean validation was restricted to elaborating the raw DiagonalTheorems source via stdin and inspecting eight declarations and their recursive axioms. No full dependency rebuild, numerical experiment, or external literature search was performed.
- Imported .olean files were used for that narrow check. Raw current source was reviewed independently; a clean complete source-to-artifact build remains separate release evidence.
- The source hashes below, rather than author status reports, delimit this verdict. A later change to any relevant definition, proof, target, or dependency requires a corresponding review update.
- The full Proposition 30.1 claim is represented by proposition_30_1 together with a_unique_minimizer and coordinate definitions/lemmas. The single proposition_30_1 type does not restate global minimizer uniqueness textually.
- No source or proof was modified. Only this Markdown report and its JSON counterpart were written.

Unresolved in-scope mathematical issues: **none**. A later source change invalidates the corresponding hash-bound portion of this audit.
