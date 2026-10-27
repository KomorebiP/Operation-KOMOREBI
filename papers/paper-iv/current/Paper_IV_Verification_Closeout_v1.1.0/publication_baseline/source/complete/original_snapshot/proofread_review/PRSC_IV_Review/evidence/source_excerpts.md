# Original source excerpts

All line numbers are from files inside the uploaded original archive. These are evidence excerpts, not edited source.

## P01: logarithmic derivative

`paper/paper4.tex`, lines 260–272.

```text
0260  \Dfun_{N,j}(z)
0261  =
0262  \sum_{n\geq0}(-1)^n\frac{z^{Nn+j}}{(Nn+j)!}
0263  \]
0264  is the signed basis for $y^{(N)}=-y$.  The section $\Dfun_N=\Dfun_{N,0}$ is the denominator used in the reciprocal family
0265  \[
0266  \Sfun_N^{(r)}=\Dfun_N^{-r}.
0267  \]
0268  Its logarithmic derivative is $\Tfun_N$.
0269  
0270  A different reciprocal family comes from normalizing each exponential section at the origin.  The function
0271  \[
0272  \Cfun_{N,j}(z)
```

## P01: actual reciprocal derivative

`formalization/lean/KomorebiPaperIV/AnalyticReciprocalLaws.lean`, lines 45–70.

```text
0045  theorem hasDerivAt_logarithmPower {f L : ℂ → ℂ} {s : Set ℂ}
0046      (hs : IsOpen s) (hL : IsLogarithmOn f L s) (r : ℂ) {z : ℂ} (hz : z ∈ s) :
0047      HasDerivAt (logarithmPower L r)
0048        (r * (-logDeriv f z) * logarithmPower L r z) z := by
0049    change HasDerivAt (fun w => Complex.exp (-r * L w))
0050      (r * (-logDeriv f z) * Complex.exp (-r * L z)) z
0051    have hd := (hL.1 z hz).differentiableAt (hs.mem_nhds hz)
0052    have h := (hd.hasDerivAt.const_mul (-r)).cexp
0053    rw [hL.deriv hs hz] at h
0054    simpa only [logarithmPower, neg_mul, mul_neg, mul_assoc, mul_left_comm, mul_comm] using h
0055  
0056  theorem reciprocal_fixed_log_derivative {N : ℕ} {L : ℂ → ℂ} {s : Set ℂ}
0057      (hs : IsOpen s) (hL : IsLogarithmOn (canonicalSignedDenominator N) L s)
0058      (r : ℂ) {z : ℂ} (hz : z ∈ s) :
0059      deriv (logarithmPower L r) z =
0060        r * analyticTransferTangent N z * logarithmPower L r z :=
0061    (hasDerivAt_logarithmPower hs hL r hz).deriv
0062  
0063  /-- Evaluation of the complete differential Bell polynomial on successive
0064  derivatives of a function. Its defining recurrence is Y_(n+1)=Y_n'+gY_n. -/
0065  def analyticDifferentialBell (g : ℂ → ℂ) : ℕ → ℂ → ℂ
0066    | 0 => fun _ => 1
0067    | n + 1 => fun z => deriv (analyticDifferentialBell g n) z + g z * analyticDifferentialBell g n z
0068  
0069  theorem analyticOnNhd_differentialBell {g : ℂ → ℂ} {s : Set ℂ}
0070      (hg : AnalyticOnNhd ℂ g s) (n : ℕ) : AnalyticOnNhd ℂ (analyticDifferentialBell g n) s := by
```

## P02: global power convention

`paper/paper4.tex`, lines 286–295.

```text
0286  \text{logarithmic coefficients}.
0287  \]
0288  This equality is the bridge between the first and second halves of the paper.
0289  
0290  All powers with a complex parameter are first defined as formal series at the origin.  An analytic interpretation requires a simply connected zero-free region and one fixed logarithm.  Integer reciprocal powers are globally meromorphic and do not require a branch choice.
0291  
0292  The main statements fall into five groups.  The finite algebra model in \cref{sec:finite_algebra} explains the derivative cycles and addition laws through one exponential identity.  The coefficient theory in \cref{sec:reciprocal_powers} gives two complementary recurrences, one from the original denominator and one from its logarithm.  The Appell theory in \cref{sec:residue_section} supplies both formal differential-operator formulas and a convolution law in the space and order parameters.  The zero analysis in \cref{sec:zero_geometry} specializes classical two-term exponential-sum theory, uses symmetry to place the uniquely localized large zeros on the rays, and computes a leading correction.  The product theory in \cref{sec:hadamard} gives the standard diagonal Fredholm encoding of the genus-zero product.
0293  
0294  The article keeps formal and analytic statements separate.  A formal identity needs only the unit constant term of the relevant series.  A holomorphic complex power also needs a zero-free domain and a chosen logarithm.  A meromorphic coefficient asymptotic is stated only for positive integral reciprocal order unless an additional branch domain is specified.
0295  
```

## P02: residue power definition

`paper/paper4.tex`, lines 1349–1358.

```text
1349  \begin{definition}\label{def:residue_section_power}
1350  For $r\in\CC$, define formal coefficients $C_{N,j,n}(r)$ by
1351  \[
1352  \Cfun_{N,j}(z)^r
1353  =
1354  \sum_{n\geq0}C_{N,j,n}(r)\frac{z^{Nn}}{(Nn)!}.
1355  \]
1356  On a simply connected region that avoids the zeros of $\Phi_{N,j}(z^N)$, the same definition uses the holomorphic and nonvanishing function $\Cfun_{N,j}$ together with one fixed logarithm.
1357  \end{definition}
1358  
```

## P02: normalized analytic germ and Taylor theorem

`formalization/lean/KomorebiPaperIV/NormalizedAnalyticPowers.lean`, lines 61–85.

```text
0061  /-- Principal logarithm gives the normalized analytic germ at zero. The
0062  Taylor identity proves the full complex-parameter coefficient normalization. -/
0063  def normalizedAnalyticPower (N j : ℕ) (r : ℂ) (w : ℂ) : ℂ :=
0064    Complex.exp (-r * Complex.log (entireNormalizedSection N j w))
0065  
0066  theorem normalizedAnalyticPower_taylor {N : ℕ} (hN : 0 < N) (j : ℕ) (r : ℂ) :
0067      analyticTaylorSeries (normalizedAnalyticPower N j r) = residuePowerSeries N j r := by
0068    have hf : Differentiable ℂ (entireNormalizedSection N j) := fun z => (analyticAt_entireNormalizedSection hN j z).differentiableAt
0069    have hL : AnalyticAt ℂ (fun z => Complex.log (entireNormalizedSection N j z)) 0 :=
0070      (analyticAt_clog (by rw [entireNormalizedSection_zero]; simp)).comp (hf.analyticAt 0)
0071    have hG : AnalyticAt ℂ (fun z => -r * Complex.log (entireNormalizedSection N j z)) 0 := analyticAt_const.fun_mul hL
0072    change analyticTaylorSeries (fun w => Complex.exp (-r * Complex.log (entireNormalizedSection N j w))) = _
0073    rw [analyticTaylorSeries_exp hG (by simp [entireNormalizedSection_zero]),
0074      analyticTaylorSeries_mul analyticAt_const hL, analyticTaylorSeries_const,
0075      analyticTaylorSeries_log hf (entireNormalizedSection_zero N j),
0076      analyticTaylorSeries_entireNormalizedSection hN, ← normalizedResidueSectionAlg_eq_normalizedResidueSection]
0077    rw [residuePowerSeries, formalExpFamily_eq_exp_subst
0078        (by simp [PowerSeries.constantCoeff_logOf (constantCoeff_normalizedResidueSectionAlg (R := ℂ) N j)]),
0079      formalExpFamily_eq_exp_subst (constantCoeff_normalizedResidueNegativeLog N j)]
0080    simp [normalizedResidueNegativeLog]
0081  
0082  theorem normalizedAnalyticPower_zero_sum_bell {N : ℕ} (hN : 2 ≤ N) (j n : ℕ) (r : ℂ) :
0083      analyticTaylorCoefficient (normalizedAnalyticPower N j r) n =
0084        completeExponentialBell n (fun m => r * ((m-1).factorial : ℂ) *
0085          zeroPowerSum (entireNormalizedSection N j) m) / (n.factorial : ℂ) := by
```

## P03: determinant proof

`paper/paper4.tex`, lines 1088–1098.

```text
1088  Let $D_n$ denote the displayed determinant and put $D_0=1$.  Expansion of this lower Hessenberg determinant gives
1089  \[
1090  D_n
1091  =
1092  \sum_{k=1}^{n}
1093  \frac{(n-1)!}{(n-k)!}p_kD_{n-k}.
1094  \]
1095  Here the cofactor sign is cancelled by the product of the negative
1096  superdiagonal entries $-1,-2,\ldots,-(k-1)$.
1097  Thus $D_n/n!$ satisfies the same recurrence and initial value as $b_{N,n}(r)$.
1098  \end{proof}
```

## P03: literal Hessenberg matrix

`formalization/lean/KomorebiPaperIV/NewtonDeterminant.lean`, lines 10–20.

```text
0010  noncomputable section
0011  open Matrix Finset
0012  variable {K : Type*} [Field K] [CharZero K]
0013  
0014  /-- Newton's lower Hessenberg matrix, including its negative superdiagonal. -/
0015  def newtonHessenberg (p : ℕ → K) (n : ℕ) : Matrix (Fin n) (Fin n) K :=
0016    fun i j => (if j.val ≤ i.val then p (i.val+1-j.val) else 0) -
0017      (if j.val = i.val+1 then (i.val+1 : K) else 0)
0018  
0019  omit [CharZero K] in
0020  private theorem newton_column_sum (p b : ℕ → K) (n : ℕ)
```

## P03: general determinant theorem

`formalization/lean/KomorebiPaperIV/NewtonDeterminant.lean`, lines 57–68.

```text
0057  
0058  /-- The exact determinant solution of Newton's recurrence. -/
0059  theorem newtonHessenberg_det (p b : ℕ → K) (hb0 : b 0 = 1)
0060      (hb : ∀ i, ∑ j ∈ range (i+1), b j*p (i+1-j) = (i+1 : K)*b (i+1))
0061      (n : ℕ) : (newtonHessenberg p n).det = (n.factorial : K)*b n := by
0062    classical
0063    cases n with
0064    | zero => simp [hb0, Matrix.det_isEmpty]
0065    | succ n =>
0066      let H := newtonHessenberg p (n+1)
0067      let C := H.updateCol 0 (fun i => if i = Fin.last n then (n+1 : K)*b (n+1) else 0)
0068      have hc : C.det = H.det := by
```

## P03: reciprocal specialization

`formalization/lean/KomorebiPaperIV/NewtonDeterminant.lean`, lines 109–128.

```text
0109      · simp
0110  
0111  /-- The Newton determinant printed in Theorem 7.6. -/
0112  theorem reciprocalOrdCoeff_newton_determinant (N n : ℕ) (r : K) :
0113      reciprocalOrdCoeff N n r = (n.factorial : K)⁻¹ *
0114        (newtonHessenberg (fun k => r*kappaCoeff N k) n).det := by
0115    have hb0 : reciprocalOrdCoeff N 0 r = 1 := by simp [reciprocalOrdCoeff]
0116    have hb (i : ℕ) : ∑ j ∈ range (i+1), reciprocalOrdCoeff N j r *
0117        (r*kappaCoeff N (i+1-j)) = (i+1 : K)*reciprocalOrdCoeff N (i+1) r := by
0118      have h := reciprocalOrdCoeff_newton N r i
0119      rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at h
0120      rw [h, mul_sum]
0121      apply sum_congr rfl
0122      intro j hj
0123      have he : i-j+1=i+1-j := by have := mem_range.mp hj; omega
0124      rw [he]
0125      ring
0126    rw [newtonHessenberg_det _ _ hb0 hb]
0127    have hf : (n.factorial : K) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
0128    field_simp
```

## P04: tangent expansion

`paper/paper4.tex`, lines 1170–1189.

```text
1170  
1171  \begin{definition}\label{def:transfer_tangent}
1172  Define the transfer tangent
1173  \[
1174  \Tfun_N(z)
1175  =-\frac{\Dfun_N'(z)}{\Dfun_N(z)}.
1176  \]
1177  Its block expansion has the form
1178  \[
1179  \Tfun_N(z)
1180  =
1181  \sum_{n\geq0}T_N(n)
1182  \frac{z^{Nn+N-1}}{(Nn+N-1)!}.
1183  \]
1184  \end{definition}
1185  
1186  \begin{proposition}[Logarithmic coefficient formula]\label{prop:tangent_kappa}
1187  The transfer tangent satisfies
1188  \[
1189  \Tfun_N(z)
```

## P04: analytic tangent series hypotheses

`formalization/lean/KomorebiPaperIV/TangentBoundary.lean`, lines 58–70.

```text
0058  theorem analyticTransferTangent_hasSum_all_orders {N : ℕ} (hN : 0 < N) {R : ℝ}
0059      (hn : ∀ w ∈ Metric.ball (0 : ℂ) R, entireReducedDenominator N w ≠ 0)
0060      {z : ℂ} (hz : z ^ N ∈ Metric.ball (0 : ℂ) R) :
0061      HasSum (fun n => transferTangentCoeff (R := ℂ) N n /
0062        ((N * n + N - 1).factorial : ℂ) * z ^ (N * n + N - 1))
0063        (analyticTransferTangent N z) := by
0064    by_cases h : N = 1
0065    · subst N
0066      exact analyticTransferTangent_one_hasSum z
0067    · exact analyticTransferTangent_coefficient_hasSum (by omega) hn hz
0068  
0069  end
0070  end Komorebi.PaperIV
```

## P05: notation in indicator proof

`paper/paper4.tex`, lines 1746–1762.

```text
1746  At a tie direction exactly two adjacent vertices attain the maximum.  After rotation it is enough to take $\theta=0$.  The two dominant terms give
1747  \[
1748  \frac2N e^{c_Nr}\cos(s_Nr)
1749  \]
1750  and every other term is exponentially smaller.  Along a sequence on which $|\cos(s_Nr)|\geq1/2$, the lower indicator bound is $c_N=h_N(0)$.  Rotational symmetry treats every tie direction.
1751  \end{proof}
1752  
1753  The zero strings are governed by two adjacent exponents.  Put
1754  \[
1755  a_N=\frac\pi N,
1756  \qquad
1757  s_N=\sin a_N,
1758  \qquad
1759  c_N=\cos a_N,
1760  \]
1761  and
1762  \[
```

## P06: inherited order restriction

`paper/paper4.tex`, lines 1644–1651.

```text
1644  \section{Growth and the geometry of the large zeros}\label{sec:zero_geometry}
1645  
1646  We now assume $N\geq2$.  Write
1647  \[
1648  \eta_k=e^{(2k+1)\pi i/N},
1649  \qquad 0\leq k<N.
1650  \]
1651  These are the vertices of a regular polygon and
```

## P06: zero-zeta section opening

`paper/paper4.tex`, lines 2634–2644.

```text
2634  \section{Zero zeta functions}\label{sec:zero_zeta}
2635  
2636  The zero counting theorem gives the exact abscissae of absolute convergence.  The exponentially accurate zero locations give more.  They compare the zero zeta with a Hurwitz zeta function.
2637  
2638  \begin{definition}\label{def:absolute_zero_zetas}
2639  Define
2640  \[
2641  \mathfrak Z_N^{\mathrm{abs}}(s)
2642  =
2643  \sum_{\rho\in\Zcal(\Dfun_N)}|\rho|^{-s}
2644  \]
```

## P06: exact convergence theorem hypotheses

`formalization/lean/KomorebiPaperIV/ZeroZetaConvergence.lean`, lines 112–146.

```text
0112      DifferentiableOn ℂ (absoluteZeroZeta f) {s : ℂ | c < s.re} :=
0113    weightedDirichlet_differentiableOn _ _ (zero_norm_pos_of_value_at_zero hf) c hs
0114  
0115  /-- Exact absolute abscissa, including divergence on and to the left of the boundary. -/
0116  theorem canonicalSignedDenominator_zeta_absolute_convergence {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
0117      Summable (fun z => ‖absoluteZeroZetaTerm (canonicalSignedDenominator N) z s‖) ↔ 1 < s.re := by
0118    rw [absoluteZeroZeta_summable_norm_iff (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)]
0119    exact canonicalSignedDenominator_zero_power_summable_iff hN s.re
0120  
0121  theorem canonicalSignedDenominator_zeta_locally_uniform {N : ℕ} (hN : 2 ≤ N) :
0122      HasSumLocallyUniformlyOn (absoluteZeroZetaTerm (canonicalSignedDenominator N))
0123        (absoluteZeroZeta (canonicalSignedDenominator N)) {s : ℂ | 1 < s.re} := by
0124    apply absoluteZeroZeta_locally_uniform (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)
0125    intro t ht
0126    exact (canonicalSignedDenominator_zero_power_summable_iff hN t).mpr ht
0127  
0128  theorem canonicalSignedDenominator_zeta_holomorphic {N : ℕ} (hN : 2 ≤ N) :
0129      DifferentiableOn ℂ (absoluteZeroZeta (canonicalSignedDenominator N)) {s : ℂ | 1 < s.re} := by
0130    apply absoluteZeroZeta_differentiableOn (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)
0131    intro t ht
0132    exact (canonicalSignedDenominator_zero_power_summable_iff hN t).mpr ht
0133  
0134  theorem entireReducedDenominator_zeta_absolute_convergence {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
0135      Summable (fun z => ‖absoluteZeroZetaTerm (entireReducedDenominator N) z s‖) ↔ 1 / (N : ℝ) < s.re := by
0136    rw [absoluteZeroZeta_summable_norm_iff (by rw [entireReducedDenominator_zero]; exact one_ne_zero)]
0137    exact entireReducedDenominator_zero_power_summable_iff hN s.re
0138  
0139  theorem entireReducedDenominator_zeta_locally_uniform {N : ℕ} (hN : 2 ≤ N) :
0140      HasSumLocallyUniformlyOn (absoluteZeroZetaTerm (entireReducedDenominator N))
0141        (absoluteZeroZeta (entireReducedDenominator N)) {s : ℂ | 1 / (N : ℝ) < s.re} := by
0142    apply absoluteZeroZeta_locally_uniform (by rw [entireReducedDenominator_zero]; exact one_ne_zero)
0143    intro t ht
0144    exact (entireReducedDenominator_zero_power_summable_iff hN t).mpr ht
0145  
0146  theorem entireReducedDenominator_zeta_holomorphic {N : ℕ} (hN : 2 ≤ N) :
```

## P07: ledger indicator wording

`paper/paper4.tex`, lines 2947–2954.

```text
2947  recurrence with its first coefficient. \\
2948  11.2, 11.4--11.11 & Two-sided maximum-modulus bounds prove exact order
2949  and type. The indicator limit holds in every direction, including ties;
2950  dominant-exponential errors and zero-freeness are uniform on compact sets
2951  avoiding ties. Near cancellation and the order-two zero set are checked.
2952  For $N\geq3$, gap and remainder bounds, sector confinement, global exhaustion
2953  and multiplicity identities give the full large-zero-string theorem.
2954  The real leading correction, quadratic exponential error, signed derivative
```

## P07: indicator limsup with zero radii excluded

`formalization/lean/KomorebiPaperIV/IndicatorLimit.lean`, lines 104–116.

```text
0104  theorem canonicalSignedDenominator_indicator {N : ℕ} (hN : 2 ≤ N) (θ : ℝ) :
0105      limsup (fun r : ℝ => Real.log ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ / r) atTop =
0106        signedIndicator N (by omega) θ := by
0107    obtain ⟨r, hr, hf, _⟩ := canonicalSignedDenominator_indicator_sequence (show 0 < N by omega) θ
0108    exact limsup_eq_of_upper_and_sequence
0109      ((eventually_gt_atTop (0 : ℝ)).mono (fun r hr => canonicalSignedDenominator_log_indicator_upper hN θ hr)) hr hf
0110  
0111  /-- The same indicator on the classical logarithm domain. This avoids relying
0112  on Lean's totalized value of log(0) at zeros along a ray. -/
0113  theorem canonicalSignedDenominator_indicator_nonzero_radii {N : ℕ} (hN : 2 ≤ N) (θ : ℝ) :
0114      limsup (fun r : ℝ => Real.log ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ / r)
0115        (atTop ⊓ principal {r : ℝ | canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) ≠ 0}) =
0116        signedIndicator N (by omega) θ := by
```

## P08: ledger denominator notation

`paper/paper4.tex`, lines 2962–2967.

```text
2962  12.1 & For every $N\geq2$, the complete multiplicity-indexed product
2963  converges uniformly on compact sets and equals $\Delta_N$. Jensen and Poisson
2964  estimates prove rigidity of the actual quotient from derived growth bounds;
2965  no growth certificate remains. The original-variable product for $D_N$
2966  is also checked. \\
2967  12.2--12.4 & The actual diagonal operator is trace class, with a
```

## P09: unused source macro

`paper/paper4.tex`, lines 110–123.

```text
0110    \begingroup\small\raggedright\leanname{#1}\par\endgroup\smallskip}
0111  \newcommand{\statusleanprior}[1]{%
0112    \par\smallskip\noindent
0113    {\color{leanblue}\textbf{Formal status: inherited Lean-backed result.}}\par
0114    \begingroup\small\raggedright\leanname{#1}\par\endgroup\smallskip}
0115  \newcommand{\statusarticle}{%
0116    \par\smallskip\noindent
0117    {\color{statusgray}\textbf{Formal status: article proof; Lean formalization pending.}}%
0118    \par\smallskip}
0119  
0120  \title{\textbf{Projector-Resolved Seed Calculus IV}\\[0.45em]
0121  \large Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data}
0122  \author{Komorebi P.}
0123  \date{Version 1.0.0 --- September 5, 2026}
```

## Original evidence boundary

`paper/paper4.tex`, lines 168–185.

```text
0168  \begin{center}
0169  \fbox{\begin{minipage}{0.93\textwidth}
0170  \textbf{Formalization and evidence boundary.}
0171  The released Paper IV Lean contract covers all 68 theorem-like manuscript
0172  results under their stated hypotheses. The accompanying v1.0.0 theorem map
0173  and formalization ledger identify the declarations and their scopes.
0174  Imported standard fact 11.1 remains explicitly imported and is not needed by
0175  the checked growth-order proofs. Open problems remain open. Complex powers
0176  retain their specified logarithms and domains; conditional asymptotic
0177  statements retain their assumptions. Finite computations are regression
0178  evidence. Formal verification checks the encoded specifications and does
0179  not establish historical priority or replace independent mathematical review.
0180  \end{minipage}}
0181  \end{center}
0182  
0183  \clearpage
0184  \tableofcontents
0185  \clearpage
```

## Original completion ledger conclusion

`paper/paper4.tex`, lines 2990–3012.

```text
2990  choices on the finite exceptional part change the continuation by an entire
2991  function and preserve its pole and residue. \\
2992  14.8 & The derivative-weighted series uses every actual simple zero and genuine
2993  logarithms with bounded arguments. Absolute and local uniform convergence and
2994  an entire sum are proved for $N\geq3$; for $N=2$, absolute/local uniform
2995  convergence and holomorphy hold on $\Re s>1$. \\
2996  \bottomrule
2997  \end{longtable}
2998  \endgroup
2999  
3000  The declaration-level theorem map is authoritative. All 68 theorem-like
3001  records have their full scoped statements covered: 68 full, zero partial,
3002  and zero unmapped. Rows 143--151 close the final fifteen partial records
3003  without altering their statements or assumptions. Imported standard fact
3004  11.1 remains imported. Formal identities, normalized analytic germs, and
3005  fixed-logarithm domain identities retain their respective stated meanings.
3006  Finite computations do not change these proof boundaries.
3007  
3008  \section{Conclusion}\label{sec:conclusion}
3009  
3010  Cyclic projection turns the exponential into a finite differential basis, and
3011  the signed cycle produces the distinguished denominator $\Dfun_N$. Its
3012  reciprocal powers yield Bell and Newton recurrences, an additive parameter
```
