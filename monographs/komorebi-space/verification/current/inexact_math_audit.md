# Independent mathematical audit: diagonal inexact rate

**Normalized claim.** For all measured data `s` and proposals `a` in the actual real Hilbert space `H = lp (fun _ : ℕ => ℝ) 2`, and real `δ, κ, ε`, assume `0 < δ ≤ 1`, `0 ≤ κ`, `‖s-b‖ ≤ δ`, and

\[
\|T^*(Ta-s)+\alpha a\|\le\varepsilon\le\kappa\alpha\delta^{1/3},\qquad
m=\lceil\delta^{-2/3}\rceil,\quad\alpha=m^{-2}.
\]

Here `(Tu)_j=u_j/(j+1)`, `w_j=1/(j+1)`, and `b=T w`, so `b_j=1/(j+1)^2`. Then

\[
\|a-w\|\le(\sqrt2+1+\kappa)\delta^{1/3}.
\]

**Primary verdict: proved as written.** No mathematical repair, additional bias assumption, finite-dimensional restriction, or extra condition on the noise is needed.

This is an independent subagent audit from raw definitions and proofs. Author attempt logs and author verdict reports were not used. No production source was edited. No `.mathbox` ledger was present in the review workspace or publication root. The applicable proof-audit checklist sections were general logic/typing, computation-dependent claims, and source/dependency checks.

## Exact target and source correspondence

The reviewed theorem is `KomorebiSpace.DiagonalRegularization.diagonal_inexact_rounded_rate` in `publication/lean/KomorebiSpace/DiagonalInexactRate.lean`, lines 12–51. Its source SHA-256 is `9afe32989eb89da7781aee5b73008ee86f9ce418d24c72af9c6a74bad6f976a7`.

The printed target is `publication/source/chapters/05k_stopping_rules.tex`, subsection “Retaining the explicit diagonal rate with an inexact solver,” lines 126–140, together with its inherited measured-data and normal-residual hypotheses in the preceding subsection. Its reference to WR12 identifies the attainable data in `05i_diagonal_regularization.tex`, lines 145–184. The formal `w` is precisely the printed minimum-norm preimage `a^dagger`, since `T w=b` and `T` is injective. The local proposal binder `a` shadows the unrelated model family name `a m`; the theorem does not restrict its proposal to that family.

## Dependency graph

1. `DiagonalDefinitions` defines positive coordinate index `j+1`, `wCoord`, `bCoord`, and the infinite sum `B m`.
2. `DiagonalSeriesBounds` proves square summability and `B_upper : B m ≤ 2/m` for `m≥1`. The proof splits the genuine sum into a prefix bounded by `1/m` and a summable reciprocal-square tail bounded by `1/m`.
3. `InfiniteDiagonalModel` constructs the real infinite `lp` model, its bounded diagonal operator and adjoint, `w`, `b`, and `alpha`. It proves `c m` is the exact regularized correction for `b`, and `‖c m-w‖²=B m`.
4. `RegularizedHilbertRepair` constructs the unique correction via the coercive normal operator. Its certificate gives `‖a-correction(s)‖≤‖gradient(s,a)‖/alpha`; its data estimate gives noise gain `1/(2√alpha)`.
5. `DiagonalNoisyRate.diagonal_bias_bound` combines steps 2 and 3. Its `corollary_30_3` combines this proved concrete bias with step 4 and the literal ceiling bounds, without retaining the generic helper's `hbias` premise.
6. The new theorem rewrites the measured normal residual as `gradient T alpha s a`, cancels the proved positive `alpha`, and applies the triangle inequality through the same measured-data correction used by `corollary_30_3`.

All mathematical leaves used here are internal Lean proofs or standard formal-library definitions/theorems. There is no external paper, numerical experiment, randomized sample, truncation-based assertion, or circular dependency in this route.

## Independent derivation of the critical implication

Set `q=δ^(1/3)>0` and `u=δ^(-2/3)`. Because `δ≤1`, `u≥1`; the ceiling obeys `u≤m<u+1≤2u`, so `m≥1` and `α=m^-2>0`.

Let `x_s=correction T α s`. The exact identity `gradient T α s a=T*(Ta-s)+αa` and the certificate imply

\[
\|a-x_s\|\le\frac{\|T^*(Ta-s)+\alpha a\|}{\alpha}
\le\frac{\varepsilon}{\alpha}
\le\kappa q.
\]

Every cancellation uses `α>0`. Separately, the actual infinite bias identity and the data gain give

\[
\|x_s-w\|\le\sqrt{2/m}+\delta m/2
\le(\sqrt2+1)q.
\]

Indeed `u q²=1` and `δu=q`, so the lower ceiling bound controls the bias and the upper ceiling bound controls the propagated noise. Adding the two inequalities through `x_s` yields precisely the target constant. At no point is the residual against the measured datum `s` replaced by a residual against the intended datum `b`.

## Obligation matrix

| ID | Status | Obligation | Finding and evidence |
|---|---|---|---|
| O01 | passed | Infinite domain and coordinate indexing | H = lp (fun _ : ℕ => ℝ) 2; index j = j+1; all quantified proposals and measured data are elements of H. `InfiniteDiagonalModel.lean:20,46-72; DiagonalDefinitions.lean:9` |
| O02 | passed | Concrete operator and target | (Tu)_j=u_j/(j+1), w_j=1/(j+1), b=T w with b_j=1/(j+1)^2; injectivity proves w is the unique and minimum-norm preimage of b. `InfiniteDiagonalModel.lean:87-109,111-134,200-208` |
| O03 | passed | Literal schedule and parameter | m=Nat.ceil(delta^(-(2:ℝ)/3)); noiseSchedule is definitionally this schedule; alpha m=((m:ℝ)^2)^(-1). `DiagonalInexactRate.lean:15-22; DiagonalNoisyRate.lean:14; InfiniteDiagonalModel.lean:140` |
| O04 | passed | Positivity and cancellation | delta>0 gives delta^(-2/3)>0, m>=1, alpha m>0. Division by alpha is justified by div_le_iff₀ hα. `DiagonalInexactRate.lean:21-22,37` |
| O05 | passed | Measured residual identity | gradient T alpha s a = T.adjoint (T a-s)+alpha•a, so the solver certificate uses s, not b. `DiagonalInexactRate.lean:23-30; RegularizedHilbertRepair.lean:18-20,60` |
| O06 | passed | Certificate implication | For the same alpha and measured datum s, norm(a-correction(s))<=norm(gradient(s,a))/alpha; combining hsolve and hε cancels positive alpha to obtain kappa*delta^(1/3). `DiagonalInexactRate.lean:33-40; RegularizedHilbertRepair.lean:129-148` |
| O07 | passed | No hidden exact-data bias hypothesis | corollary_30_3 obtains diagonal_bias_bound internally; c_eq_correction, norm_bias_sq and B_upper establish the concrete infinite bias bound sqrt(2/m). `DiagonalNoisyRate.lean:136-165; InfiniteDiagonalModel.lean:210-227; DiagonalSeriesBounds.lean:349-353` |
| O08 | passed | No finite surrogate | norm_sq_eq_tsum identifies genuine lp norm squares; B is an infinite tsum. Prefix and tail bounds prove B_upper by summable decomposition; no truncation error is dropped. `InfiniteDiagonalModel.lean:180-196,225-227; DiagonalDefinitions.lean:18; DiagonalSeriesBounds.lean:157-174,325-353` |
| O09 | passed | Data noise constant | data_noise_bound gives norm(correction(s)-correction(b))<=norm(s-b)/(2*sqrt(alpha)); at alpha=m^-2 and m>0 this is delta*m/2. `RegularizedHilbertRepair.lean:190-215; DiagonalNoisyRate.lean:91-119` |
| O10 | passed | Rounding constants | For u=delta^-2/3>=1, u<=m<=2u. Hence sqrt(2/m)<=sqrt(2)*delta^(1/3) and delta*m/2<=delta^(1/3). `DiagonalNoisyRate.lean:40-88` |
| O11 | passed | Final triangle inequality | The intermediate correction is the measured-data minimizer; summing its error to w and solver error gives exactly (sqrt(2)+1+kappa)*delta^(1/3). `DiagonalInexactRate.lean:41-51` |
| O12 | passed | Quantifiers and boundaries | All s,a:H and real epsilon are covered under the stated inequalities; epsilon>=0 follows from hsolve. delta=1 gives m=1 and alpha=1; kappa=0 forces zero measured normal residual. delta=0 is intentionally excluded. `DiagonalInexactRate.lean:12-19` |
| O13 | passed | Printed target correspondence | The target subsection uses the attainable WR12 datum and inherited measured-data and normal-residual hypotheses. Lean identifies its a-dagger with w and retains every printed constant and ceiling. `05k_stopping_rules.tex:126-140; 05i_diagonal_regularization.tex:145-184` |
| O14 | passed | Exact-source elaboration and axioms | The frozen source copied verbatim into InexactAuditProbe.lean compiles with -j1, warningAsError=true and autoImplicit=false. Printed type contains no extra premises. Reported axioms are propext, Classical.choice, Quot.sound, with no sorryAx. `reviews/InexactAuditProbe.lean; reviews/inexact_math_audit_probe.log` |
| O15 | out of scope | Broader stopping law and escaping conclusion | The audited declaration proves the concrete finite-delta attainable rate only; it does not claim universal optimality or convergence for the escaping datum. `DiagonalInexactRate.lean:12-19` |

## Boundary and scope checks

At `δ=1`, `m=1` and `α=1`; no endpoint is lost. At `κ=0`, the hypotheses force `ε=0` and zero measured normal residual, recovering the exact-solve rate. A separate `ε≥0` hypothesis is unnecessary because a norm is nonnegative and `hsolve` implies it. `δ=0` is deliberately outside this finite-integer schedule. The statement covers arbitrary Hilbert-space perturbations and arbitrary Hilbert-space proposals; no finite-support, coordinatewise noise, or probabilistic hypothesis is present.

## Formal check and its scope

An isolated probe copied the exact theorem source verbatim, then printed its elaborated declaration and axioms. It ran from the new publication Lean directory with:

```sh
/workspace/scratch/5d9f7f8127b0/komorebi_diagonal_formalization/scripts/lean_env.sh lake env lean -j1 -DwarningAsError=true -DautoImplicit=false /workspace/scratch/5d9f7f8127b0/publication_v115/reviews/InexactAuditProbe.lean
```

Exit code: **0**. Warnings were treated as errors; automatic implicit parameters were disabled. The printed type has precisely the stated `s,a,δ,κ,ε` quantifiers and hypotheses. The target and the key imported results `corollary_30_3`, `diagonal_bias_bound`, `correction_error_bound`, and `data_noise_bound` report only `[propext, Classical.choice, Quot.sound]`, with no `sorryAx` or custom axiom. The probe elaborates the fresh target source against the available dependency oleans; this report does not claim a fresh whole-project build. The relevant raw dependency proofs were separately read as described above.

The evidence is in `reviews/InexactAuditProbe.lean` and `reviews/inexact_math_audit_probe.log`. Full source hashes and evidence-file hashes are in `reviews/inexact_math_audit.json`.

## Remaining gap and safe conclusion

**Exact remaining gap: none for the frozen declaration.** The strongest safe statement is the normalized universally quantified concrete inexact attainable rate above. This audit does not assert universal optimality of the tolerance, nor a limiting realization for the escaping datum. No further mathematical check is required before integration if the recorded target source hash remains unchanged.

## Input hashes

| Input | SHA-256 |
|---|---|
| `publication/lean/KomorebiSpace/DiagonalInexactRate.lean` | `9afe32989eb89da7781aee5b73008ee86f9ce418d24c72af9c6a74bad6f976a7` |
| `publication/lean/KomorebiSpace/DiagonalNoisyRate.lean` | `55ad01c40e768c2ab7d70895ff5576c2576751137ebb7994198f1ebe27e2d21e` |
| `publication/lean/KomorebiSpace/InfiniteDiagonalModel.lean` | `da72d7f6ccaa870581c23409837955e54db8be2a732354716e908fe9266501d2` |
| `publication/lean/KomorebiSpace/DiagonalDefinitions.lean` | `751bf02816f74e2fe8a8bc9f45c22f9538d087d1af536af3835e4906f4015f54` |
| `publication/lean/KomorebiSpace/DiagonalSeriesBounds.lean` | `fc606b9db34f39179ba3cedcc43504325bd14dfdba6de8c46ad7bd6a70a31cb2` |
| `publication/lean/KomorebiSpace/RegularizedHilbertRepair.lean` | `b57ee2a27d7c30e35c17a90655aad21a967ae73f830d84ee81a22a2c92276ae4` |
| `publication/source/chapters/05k_stopping_rules.tex` | `506439d12645a2957ac545075702d323c589fe333e96d15174d4ddd8b4541603` |
| `publication/source/chapters/05i_diagonal_regularization.tex` | `f10d921f0272d27f0894547767736c32c5f094c7f77a4016b400527a73a229c2` |
| `publication/lean/lean-toolchain` | `8190e75a201741065fe508b28955dd64dd72d090babe5f70ce6848879d68ae88` |
| `publication/lean/lake-manifest.json` | `7e28e00cb45e028f411ea69972d18a9964f4c3affaf0212389afa9d1fe13df47` |

Parent immutable publication SHA-256: `73e9c5caa36f4ba05029c01481b345ce24cf9b1905dfb012ed21dd4bcfe86dc0`.

## Publication status text rereview

The final added status paragraph in `publication/source/chapters/05k_stopping_rules.tex` was independently reread after this audit. It accurately identifies the concrete declaration, actual infinite operator, measured-data residual, literal ceiling, and derived bias. The mathematical target is unchanged. Reviewed updated file SHA-256: `c24603387f4ec8fb297cd294bd9a919af2ce8bf920719ba3189b5a47c7640009`. The original source hash above remains preserved as the initial audit input.
