import KomorebiLSM.RegressionGeometry
import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral
import Mathlib.MeasureTheory.Measure.Haar.NormedSpace
import Mathlib.MeasureTheory.Integral.Pi
import Mathlib.Analysis.Matrix.PosDef
import Mathlib.MeasureTheory.Measure.Lebesgue.EqHaar
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap
import Mathlib.Tactic

/-! Actual Gaussian quadratic integrals for the ridge-mixture argument. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open MeasureTheory
open Matrix
open scoped BigOperators ENNReal ComplexOrder

/-- Completing the square gives the actual one-dimensional Gaussian tilt. -/
theorem integral_exp_quadratic (b c : ℝ) (hb : 0 < b) :
    (∫ x : ℝ,Real.exp (-b*x^2+c*x)) =
      Real.sqrt (Real.pi/b)*Real.exp (c^2/(4*b)) := by
  have hid (x : ℝ) : -b*x^2+c*x = -b*(x+(-c/(2*b)))^2+c^2/(4*b) := by
    field_simp
    ring
  simp_rw [hid,Real.exp_add]
  rw [integral_mul_const,integral_add_right_eq_self (fun x : ℝ => Real.exp (-b*x^2))
    (-c/(2*b)),integral_gaussian]

/-- The completed-square density is genuinely Bochner integrable. -/
theorem integrable_exp_quadratic (b c : ℝ) (hb : 0 < b) :
    Integrable (fun x : ℝ => Real.exp (-b*x^2+c*x)) := by
  have hid (x : ℝ) : -b*x^2+c*x = -b*(x+(-c/(2*b)))^2+c^2/(4*b) := by
    field_simp
    ring
  simp_rw [hid,Real.exp_add]
  exact ((integrable_exp_neg_mul_sq hb).comp_add_right (-c/(2*b))).mul_const _

/-- The actual finite-product quadratic Gaussian integral. -/
theorem integral_exp_diagonal {I : Type*} [Fintype I] (b c : I → ℝ)
    (hb : ∀ i,0 < b i) :
    (∫ x : I → ℝ,Real.exp (-(∑ i,b i*(x i)^2)+∑ i,c i*x i)) =
      ∏ i,Real.sqrt (Real.pi/b i)*Real.exp ((c i)^2/(4*b i)) := by
  simp_rw [← Finset.sum_neg_distrib,← Finset.sum_add_distrib,Real.exp_sum]
  rw [integral_fintype_prod_volume_eq_prod (f := fun i (x : ℝ) =>
    Real.exp (-(b i*x^2)+c i*x))]
  congr with i
  simpa only [neg_mul] using integral_exp_quadratic (b i) (c i) (hb i)

/-- Strict positivity of the computed integral supplies its Bochner integrability. -/
theorem integrable_exp_diagonal {I : Type*} [Fintype I] (b c : I → ℝ)
    (hb : ∀ i,0 < b i) :
    Integrable (fun x : I → ℝ => Real.exp (-(∑ i,b i*(x i)^2)+∑ i,c i*x i)) := by
  have hp : 0 < ∫ x : I → ℝ,Real.exp (-(∑ i,b i*(x i)^2)+∑ i,c i*x i) := by
    rw [integral_exp_diagonal b c hb]
    apply Finset.prod_pos
    intro i _
    exact mul_pos (Real.sqrt_pos.2 (div_pos Real.pi_pos (hb i))) (Real.exp_pos _)
  by_contra hi
  rw [integral_undef hi] at hp
  exact lt_irrefl 0 hp

/-- Real unitary coordinate changes preserve the actual product Lebesgue integral. -/
theorem integral_unitary_mulVec {I : Type*} [Fintype I] [DecidableEq I]
    (U : unitary (Matrix I I ℝ)) (f : (I → ℝ) → ℝ) :
    (∫ x : I → ℝ,f ((U : Matrix I I ℝ) *ᵥ x)) = ∫ x : I → ℝ,f x := by
  let A : Matrix I I ℝ := U
  have hleft : A.transpose*A=1 := by
    simpa only [A,Matrix.star_eq_conjTranspose,Matrix.conjTranspose_eq_transpose_of_trivial]
      using Unitary.coe_star_mul_self U
  have hright : A*A.transpose=1 := by
    have h := Unitary.coe_mul_star_self U
    change (U : Matrix I I ℝ)*star (U : Matrix I I ℝ)=1 at h
    simpa only [A,Matrix.star_eq_conjTranspose,Matrix.conjTranspose_eq_transpose_of_trivial]
      using h
  have hdet : A.det^2=1 := by
    have h := congrArg Matrix.det hleft
    simpa only [Matrix.det_mul,Matrix.det_transpose,Matrix.det_one,pow_two] using h
  have habs : |A.det|=1 := by
    nlinarith [sq_abs A.det,abs_nonneg A.det]
  have hd : LinearMap.det A.toLin' ≠ 0 := by
    rw [LinearMap.det_toLin']
    intro hz
    simp [hz] at hdet
  have hmap := Measure.map_linearMap_addHaar_pi_eq_smul_addHaar hd
    (volume : Measure (I → ℝ))
  simp only [LinearMap.det_toLin',abs_inv,habs,inv_one,ENNReal.ofReal_one,one_smul] at hmap
  have hpres : MeasurePreserving (fun x => A *ᵥ x) (volume : Measure (I → ℝ)) volume :=
    ⟨A.toLin'.continuous_of_finiteDimensional.measurable,hmap⟩
  let e : (I → ℝ) ≃ₗ[ℝ] (I → ℝ) :=
    { A.toLin' with
      invFun := fun x => A.transpose *ᵥ x
      left_inv := fun x => by
        change A.transpose *ᵥ (A *ᵥ x)=x
        rw [mulVec_mulVec,hleft,Matrix.one_mulVec]
      right_inv := fun x => by
        change A *ᵥ (A.transpose *ᵥ x)=x
        rw [mulVec_mulVec,hright,Matrix.one_mulVec] }
  exact hpres.integral_comp e.toContinuousLinearEquiv.toHomeomorph.measurableEmbedding f

/-- The centered positive-definite Gaussian integral is computed from the
actual spectral decomposition, including its determinant factor. -/
theorem integral_exp_posDef {I : Type*} [Fintype I] [DecidableEq I]
    (V : Matrix I I ℝ) (hV : V.PosDef) :
    (∫ x : I → ℝ,Real.exp (-(x ⬝ᵥ (V *ᵥ x))/2)) =
      Real.sqrt ((2*Real.pi)^Fintype.card I / V.det) := by
  let U := hV.isHermitian.eigenvectorUnitary
  let eigen := hV.isHermitian.eigenvalues
  have hd : (U : Matrix I I ℝ).transpose*V*(U : Matrix I I ℝ)=diagonal eigen := by
    simpa only [U,eigen,Unitary.conjStarAlgAut_star_apply,Matrix.star_eq_conjTranspose,
      Matrix.conjTranspose_eq_transpose_of_trivial,RCLike.ofReal_real_eq_id,Function.id_comp]
      using hV.isHermitian.conjStarAlgAut_star_eigenvectorUnitary
  have hq (x : I → ℝ) :
      ((U : Matrix I I ℝ) *ᵥ x) ⬝ᵥ (V *ᵥ ((U : Matrix I I ℝ) *ᵥ x)) =
        ∑ i,eigen i*(x i)^2 := by
    calc
      _ = x ⬝ᵥ ((U : Matrix I I ℝ).transpose *ᵥ
          (V *ᵥ ((U : Matrix I I ℝ) *ᵥ x))) := by
        rw [dotProduct_transpose_mulVec,dotProduct_comm]
      _ = x ⬝ᵥ (((U : Matrix I I ℝ).transpose*V*(U : Matrix I I ℝ)) *ᵥ x) := by
        rw [mulVec_mulVec,mulVec_mulVec]
      _ = _ := by
        rw [hd]
        simp [dotProduct,Matrix.mulVec_diagonal,pow_two,mul_comm,mul_assoc]
  rw [← integral_unitary_mulVec U (fun x => Real.exp (-(x ⬝ᵥ (V *ᵥ x))/2))]
  simp_rw [hq]
  have heigen (i : I) : 0 < eigen i := hV.eigenvalues_pos i
  have hi := integral_exp_diagonal (fun i => eigen i/2) (fun _ => 0)
    (fun i => div_pos (heigen i) (by norm_num))
  have heq (x : I → ℝ) :
      -(∑ i,(eigen i/2)*(x i)^2)+(∑ i,(0:ℝ)*x i) = -(∑ i,eigen i*(x i)^2)/2 := by
    simp only [zero_mul,Finset.sum_const_zero,add_zero,neg_div]
    congr 1
    rw [Finset.sum_div]
    apply Finset.sum_congr rfl
    intro i _
    ring
  simp_rw [heq,zero_pow (by decide : (2:ℕ)≠0),zero_div,Real.exp_zero,mul_one] at hi
  rw [hi]
  calc
    (∏ i,Real.sqrt (Real.pi/(eigen i/2))) = ∏ i,Real.sqrt ((2*Real.pi)/eigen i) := by
      apply Finset.prod_congr rfl
      intro i _
      congr 1
      field_simp
    _ = Real.sqrt (∏ i,(2*Real.pi)/eigen i) :=
      (Real.sqrt_prod Finset.univ (fun i _ => (div_pos (by positivity) (heigen i)).le)).symm
    _ = _ := by
      congr 1
      rw [Finset.prod_div_distrib,Finset.prod_const]
      exact congrArg (fun t : ℝ => (2*Real.pi)^Fintype.card I/t)
        hV.isHermitian.det_eq_prod_eigenvalues.symm

/-- Completing the square uses the actual nonsingular inverse of the
positive-definite matrix. -/
theorem quadratic_complete_square {I : Type*} [Fintype I] [DecidableEq I]
    (V : Matrix I I ℝ) (hV : V.PosDef) (s q : I → ℝ) :
    -(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q =
      -((q-V⁻¹ *ᵥ s) ⬝ᵥ (V *ᵥ (q-V⁻¹ *ᵥ s)))/2+(s ⬝ᵥ (V⁻¹ *ᵥ s))/2 := by
  let a := V⁻¹ *ᵥ s
  have hinv : V *ᵥ a=s := by
    dsimp [a]
    rw [mulVec_mulVec,Matrix.mul_nonsing_inv V (isUnit_iff_ne_zero.mpr (ne_of_gt hV.det_pos)),
      Matrix.one_mulVec]
  have hsymm : V.transpose=V := by
    simpa only [Matrix.IsHermitian,Matrix.conjTranspose_eq_transpose_of_trivial] using hV.isHermitian
  have hcross : a ⬝ᵥ (V *ᵥ q)=s ⬝ᵥ q := by
    have h := dotProduct_transpose_mulVec V a q
    rw [hsymm,hinv] at h
    exact h.trans (dotProduct_comm _ _)
  change -(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q =
    -((q-a) ⬝ᵥ (V *ᵥ (q-a)))/2+(s ⬝ᵥ a)/2
  simp only [Matrix.mulVec_sub,sub_dotProduct,dotProduct_sub]
  rw [hinv,hcross,dotProduct_comm q s,dotProduct_comm a s]
  ring

/-- The actual multivariate Gaussian exponential tilt, with its exact
determinant and inverse-quadratic factors. -/
theorem integral_exp_posDef_tilt {I : Type*} [Fintype I] [DecidableEq I]
    (V : Matrix I I ℝ) (hV : V.PosDef) (s : I → ℝ) :
    (∫ q : I → ℝ,Real.exp (-(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q)) =
      Real.sqrt ((2*Real.pi)^Fintype.card I / V.det)*
        Real.exp ((s ⬝ᵥ (V⁻¹ *ᵥ s))/2) := by
  simp_rw [quadratic_complete_square V hV s,Real.exp_add]
  rw [integral_mul_const]
  have ht := integral_add_right_eq_self (μ := (volume : Measure (I → ℝ)))
    (fun q : I → ℝ => Real.exp (-(q ⬝ᵥ (V *ᵥ q))/2)) (-(V⁻¹ *ᵥ s))
  simp only [← sub_eq_add_neg] at ht
  rw [ht,integral_exp_posDef V hV]

theorem integrable_exp_posDef_tilt {I : Type*} [Fintype I] [DecidableEq I]
    (V : Matrix I I ℝ) (hV : V.PosDef) (s : I → ℝ) :
    Integrable (fun q : I → ℝ => Real.exp (-(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q)) := by
  have hp : 0 < ∫ q : I → ℝ,Real.exp (-(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q) := by
    rw [integral_exp_posDef_tilt V hV s]
    exact mul_pos (Real.sqrt_pos.2 (div_pos (by positivity) hV.det_pos)) (Real.exp_pos _)
  by_contra hi
  rw [integral_undef hi] at hp
  exact lt_irrefl 0 hp

section GaussianPrior
variable {I : Type*} [Fintype I] [DecidableEq I]

/-- The partition function computed by the actual Gaussian integral. -/
noncomputable def gaussianPartition (V : Matrix I I ℝ) : ℝ :=
  Real.sqrt ((2*Real.pi)^Fintype.card I/V.det)

theorem gaussianPartition_pos {V : Matrix I I ℝ} (hV : V.PosDef) :
    0 < gaussianPartition V :=
  Real.sqrt_pos.2 (div_pos (by positivity) hV.det_pos)

/-- The genuine centered Gaussian density with precision gamma times the identity. -/
noncomputable def gaussianDensity (γ : ℝ) (q : I → ℝ) : ℝ :=
  (gaussianPartition (γ • (1 : Matrix I I ℝ)))⁻¹ *
    Real.exp (-(q ⬝ᵥ ((γ • (1 : Matrix I I ℝ)) *ᵥ q))/2)

theorem gaussianDensity_nonneg (γ : ℝ) (q : I → ℝ) : 0 ≤ gaussianDensity γ q :=
  mul_nonneg (inv_nonneg.2 (Real.sqrt_nonneg _)) (Real.exp_nonneg _)

theorem gaussianDensity_measurable (γ : ℝ) : Measurable (gaussianDensity (I := I) γ) := by
  unfold gaussianDensity
  fun_prop

theorem gaussianDensity_integrable (γ : ℝ) (hγ : 0 < γ) :
    Integrable (gaussianDensity (I := I) γ) := by
  unfold gaussianDensity
  have hV : (γ • (1 : Matrix I I ℝ)).PosDef := Matrix.PosDef.one.smul hγ
  have hi := integrable_exp_posDef_tilt (γ • (1 : Matrix I I ℝ)) hV (0 : I → ℝ)
  simpa only [zero_dotProduct,add_zero] using hi.const_mul
    (gaussianPartition (γ • (1 : Matrix I I ℝ)))⁻¹

theorem integral_gaussianDensity (γ : ℝ) (hγ : 0 < γ) :
    (∫ q : I → ℝ,gaussianDensity γ q) = 1 := by
  have hV : (γ • (1 : Matrix I I ℝ)).PosDef := Matrix.PosDef.one.smul hγ
  unfold gaussianDensity
  rw [integral_const_mul,integral_exp_posDef _ hV]
  exact inv_mul_cancel₀ (ne_of_gt (gaussianPartition_pos hV))

/-- The actual normalized Gaussian mixing measure, constructed by density. -/
noncomputable def gaussianPrior (γ : ℝ) : Measure (I → ℝ) :=
  volume.withDensity (fun q => ENNReal.ofReal (gaussianDensity γ q))

theorem gaussianPrior_probability (γ : ℝ) (hγ : 0 < γ) :
    IsProbabilityMeasure (gaussianPrior (I := I) γ) := by
  constructor
  rw [gaussianPrior,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ,
    ← ofReal_integral_eq_lintegral_ofReal (gaussianDensity_integrable γ hγ)
      (ae_of_all _ (gaussianDensity_nonneg γ)),integral_gaussianDensity γ hγ]
  exact ENNReal.ofReal_one

theorem gaussianPrior_integral (γ : ℝ) (g : (I → ℝ) → ℝ) :
    (∫ q,g q∂gaussianPrior γ)=∫ q,gaussianDensity γ q*g q := by
  rw [gaussianPrior,integral_withDensity_eq_integral_toReal_smul
    (gaussianDensity_measurable γ).ennreal_ofReal (ae_of_all _ fun _ => ENNReal.ofReal_lt_top)]
  apply integral_congr_ae
  exact ae_of_all _ (fun q => by
    change (ENNReal.ofReal (gaussianDensity γ q)).toReal • g q = gaussianDensity γ q*g q
    rw [ENNReal.toReal_ofReal (gaussianDensity_nonneg γ q),smul_eq_mul])

theorem gaussianPartition_ratio (V W : Matrix I I ℝ) (hV : V.PosDef) (hW : W.PosDef) :
    gaussianPartition V/gaussianPartition W=Real.sqrt (W.det/V.det) := by
  unfold gaussianPartition
  rw [← Real.sqrt_div (div_nonneg (by positivity) hV.det_pos.le)]
  congr 1
  have hc : (2*Real.pi)^Fintype.card I ≠ 0 := by positivity
  field_simp [hc,ne_of_gt hV.det_pos,ne_of_gt hW.det_pos]

/-- Mixing a quadratic exponential against the constructed Gaussian prior
gives the exact determinant ratio; this is an identity of actual integrals. -/
theorem gaussianPrior_tilt (γ : ℝ) (hγ : 0 < γ) (V : Matrix I I ℝ)
    (hV : V.PosDef) (s : I → ℝ) :
    (∫ q : I → ℝ,Real.exp (s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2)∂gaussianPrior γ) =
      Real.sqrt ((γ • (1 : Matrix I I ℝ)).det/V.det)*
        Real.exp ((s ⬝ᵥ (V⁻¹ *ᵥ s))/2) := by
  rw [gaussianPrior_integral]
  have he (q : I → ℝ) : gaussianDensity γ q*
      Real.exp (s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2) =
      (gaussianPartition (γ • (1 : Matrix I I ℝ)))⁻¹ *
        Real.exp (-(q ⬝ᵥ (V *ᵥ q))/2+s ⬝ᵥ q) := by
    unfold gaussianDensity
    rw [mul_assoc,← Real.exp_add]
    congr 2
    simp only [Matrix.sub_mulVec,dotProduct_sub]
    ring
  simp_rw [he]
  rw [integral_const_mul,integral_exp_posDef_tilt V hV s]
  change (gaussianPartition (γ • (1 : Matrix I I ℝ)))⁻¹*
    (gaussianPartition V*Real.exp ((s ⬝ᵥ (V⁻¹ *ᵥ s))/2)) = _
  calc
    _ = (gaussianPartition V/gaussianPartition (γ • (1 : Matrix I I ℝ)))*
        Real.exp ((s ⬝ᵥ (V⁻¹ *ᵥ s))/2) := by ring
    _ = _ := by rw [gaussianPartition_ratio V _ hV (Matrix.PosDef.one.smul hγ)]

theorem gaussianPrior_tilt_integrable (γ : ℝ) (hγ : 0 < γ) (V : Matrix I I ℝ)
    (hV : V.PosDef) (s : I → ℝ) :
    Integrable (fun q : I → ℝ => Real.exp (s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2))
      (gaussianPrior γ) := by
  have h0 : (γ • (1 : Matrix I I ℝ)).PosDef := Matrix.PosDef.one.smul hγ
  have hp : 0 < ∫ q : I → ℝ,Real.exp (s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2)
      ∂gaussianPrior γ := by
    rw [gaussianPrior_tilt γ hγ V hV s]
    exact mul_pos (Real.sqrt_pos.2 (div_pos h0.det_pos hV.det_pos)) (Real.exp_pos _)
  by_contra hi
  rw [integral_undef hi] at hp
  exact lt_irrefl 0 hp

/-- The exact self-normalized mixture formula for the actual ridge Gram matrix. -/
theorem gaussian_ridge_mixture (γ σ : ℝ) (hγ : 0 < γ) (hσ : 0 < σ)
    (φ : ℕ → I → ℝ) (n : ℕ) (score : I → ℝ) :
    (∫ q : I → ℝ,Real.exp ((q ⬝ᵥ score)/σ-(q ⬝ᵥ (designGram φ n *ᵥ q))/2)
      ∂gaussianPrior γ) =
      Real.sqrt ((γ • (1 : Matrix I I ℝ)).det/(ridgeMatrix γ φ n).det)*
        Real.exp ((weightedNorm (ridgeMatrix γ φ n)⁻¹ score)^2/(2*σ^2)) := by
  let V := ridgeMatrix γ φ n
  let s : I → ℝ := σ⁻¹ • score
  have hV := ridgeMatrix_posDef γ hγ φ n
  have hp (q : I → ℝ) : s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2 =
      (q ⬝ᵥ score)/σ-(q ⬝ᵥ (designGram φ n *ᵥ q))/2 := by
    simp only [V,ridgeMatrix,add_sub_cancel_left,s,smul_dotProduct,smul_eq_mul]
    rw [dotProduct_comm score q]
    ring
  have he : (s ⬝ᵥ (V⁻¹ *ᵥ s))/2 = (weightedNorm V⁻¹ score)^2/(2*σ^2) := by
    rw [weightedNorm_sq hV.inv.posSemidef]
    dsimp [s]
    simp only [Matrix.mulVec_smul,smul_dotProduct,dotProduct_smul,smul_eq_mul]
    field_simp [ne_of_gt hσ]
    ring
  have hi := gaussianPrior_tilt γ hγ V hV s
  simp_rw [hp] at hi
  rw [he] at hi
  exact hi

theorem gaussian_ridge_mixture_integrable (γ σ : ℝ) (hγ : 0 < γ)
    (φ : ℕ → I → ℝ) (n : ℕ) (score : I → ℝ) :
    Integrable (fun q : I → ℝ =>
      Real.exp ((q ⬝ᵥ score)/σ-(q ⬝ᵥ (designGram φ n *ᵥ q))/2)) (gaussianPrior γ) := by
  let V := ridgeMatrix γ φ n
  let s : I → ℝ := σ⁻¹ • score
  have hp (q : I → ℝ) : s ⬝ᵥ q-(q ⬝ᵥ ((V-γ • 1) *ᵥ q))/2 =
      (q ⬝ᵥ score)/σ-(q ⬝ᵥ (designGram φ n *ᵥ q))/2 := by
    simp only [V,ridgeMatrix,add_sub_cancel_left,s,smul_dotProduct,smul_eq_mul]
    rw [dotProduct_comm score q]
    ring
  have hi := gaussianPrior_tilt_integrable γ hγ V (ridgeMatrix_posDef γ hγ φ n) s
  simpa only [hp] using hi

end GaussianPrior

end Komorebi.LSM.RegressionConfidence
