import KomorebiPaperVI.ComplexMemory
import KomorebiPaperVI.CanonicalJets
import KomorebiPaperVI.ScalarDecay
import Mathlib.Algebra.Algebra.Bilinear

/-! Author: Komorebi P. Spectral half-plane Laplace inversion for arbitrary finite-dimensional
complex algebras. Generalized eigenspaces, including nilpotent Jordan parts, supply the decay. -/
namespace KomorebiPaperVI.NonnormalMemory
open Module Set Filter MeasureTheory NormedSpace
open scoped Topology
open KomorebiPaperVI.Semigroups KomorebiPaperVI.ComplexMemory
set_option backward.isDefEq.respectTransparency false
variable {R : Type*} [CStarAlgebra R] [FiniteDimensional ℂ R]

omit [FiniteDimensional ℂ R] in
theorem left_shift_power (A : R) (μ : ℂ) (k : ℕ) (x : R) :
    ((LinearMap.mulLeft ℂ A-μ • 1)^k) x=(A-μ • 1)^k*x := by
  have he : LinearMap.mulLeft ℂ A-μ • 1=LinearMap.mulLeft ℂ (A-μ • 1) := by
    ext y
    simp [sub_mul,Algebra.smul_mul_assoc]
  rw [he,LinearMap.pow_mulLeft,LinearMap.mulLeft_apply]

omit [FiniteDimensional ℂ R] in
theorem component_spectrum (A : R) (μ : ℂ) (x : R)
    (hx : x ∈ (Module.End.maxGenEigenspace (LinearMap.mulLeft ℂ A)) μ) (hne : x ≠ 0) :
    μ ∈ spectrum ℂ A := by
  have hv : (Module.End.HasUnifEigenvector (LinearMap.mulLeft ℂ A)) μ ⊤ x := ⟨hx,hne⟩
  have he : (Module.End.HasEigenvalue (LinearMap.mulLeft ℂ A)) μ :=
    (Module.End.hasUnifEigenvalue_iff_hasUnifEigenvalue_one (by simp : (0:ℕ∞)<⊤)).mp hv.hasUnifEigenvalue
  obtain ⟨y,hy⟩ := he.exists_hasEigenvector
  rw [spectrum.mem_iff]
  rintro ⟨u,hu⟩
  have hz : (u:R)*y=0 := by
    rw [hu,sub_mul,Algebra.algebraMap_eq_smul_one,Algebra.smul_mul_assoc,one_mul]
    exact sub_eq_zero.mpr hy.apply_eq_smul.symm
  exact hy.2 ((Units.mul_right_eq_zero u).mp hz)

theorem exp_mul_component (A : R) (μ : ℂ) (x : R)
    (hx : x ∈ (Module.End.maxGenEigenspace (LinearMap.mulLeft ℂ A)) μ) (t : ℝ) :
    transfer A t*x=Complex.exp (μ*t) •
      ∑ k ∈ Finset.range (finrank ℂ R),((t:ℂ)^k/(k.factorial:ℂ)) • ((A-μ • 1)^k*x) := by
  classical
  let : NormedAlgebra ℚ R := NormedAlgebra.restrictScalars ℚ ℝ R
  let D := A-μ • 1
  have hkill (k : ℕ) (hk : finrank ℂ R ≤ k) : D^k*x=0 := by
    rw [← left_shift_power]
    exact CanonicalJets.power_kills _ μ x hx k hk
  have hs := (exp_series_hasSum_exp' (𝕂 := ℂ) ((t:ℂ) • D)).mul_right x
  have he : exp ((t:ℂ) • D)*x=
      ∑ k ∈ Finset.range (finrank ℂ R),((t:ℂ)^k/(k.factorial:ℂ)) • (D^k*x) := by
    have hs' : HasSum (fun k : ℕ => ((t:ℂ)^k/(k.factorial:ℂ)) • (D^k*x))
        (exp ((t:ℂ) • D)*x) := by
      simpa only [smul_pow,Algebra.smul_mul_assoc,smul_smul,div_eq_mul_inv,mul_comm] using hs
    exact hs'.unique (hasSum_sum_of_ne_finset_zero (fun k hk => by
      rw [hkill k (by simpa using hk),smul_zero]))
  have ht : t • A=algebraMap ℂ R (μ*t)+(t:ℂ) • D := by
    simp only [D,smul_sub,Algebra.algebraMap_eq_smul_one,smul_smul]
    rw [RCLike.real_smul_eq_coe_smul (K := ℂ),mul_comm μ (t:ℂ)]
    abel
  rw [transfer,ht,exp_add_of_commute (Algebra.commutes _ _),
    ← algebraMap_exp_comm,← Complex.exp_eq_exp_ℂ,Algebra.algebraMap_eq_smul_one,
    Algebra.smul_mul_assoc,one_mul,Algebra.smul_mul_assoc,he]

theorem damped_mul_component (A : R) (z μ : ℂ) (x : R)
    (hx : x ∈ (Module.End.maxGenEigenspace (LinearMap.mulLeft ℂ A)) μ) (t : ℝ) :
    damped A z t*x=∑ k ∈ Finset.range (finrank ℂ R),
      (Complex.exp ((μ-z)*t)*(t:ℂ)^k) • ((k.factorial:ℂ)⁻¹ • ((A-μ • 1)^k*x)) := by
  rw [damped,Algebra.smul_mul_assoc,exp_mul_component A μ x hx,
    smul_smul,Finset.smul_sum]
  apply Finset.sum_congr rfl
  intro k _
  have he : -z*(t:ℂ)+μ*t=(μ-z)*t := by ring
  simp only [smul_smul,div_eq_mul_inv]
  rw [← Complex.exp_add,he,mul_assoc]

theorem component_decay (A : R) (z : ℂ)
    (hz : ∀ μ∈spectrum ℂ A,μ.re < z.re) (μ : ℂ) (x : R)
    (hx : x ∈ (Module.End.maxGenEigenspace (LinearMap.mulLeft ℂ A)) μ) :
    IntegrableOn (fun t => damped A z t*x) (Ioi 0) ∧
    Tendsto (fun t => damped A z t*x) atTop (𝓝 0) := by
  classical
  by_cases hne : x=0
  · subst x
    simp
  have hμ : (μ-z).re < 0 := by
    have hh := hz μ (component_spectrum A μ x hx hne)
    simp only [Complex.sub_re]
    linarith
  have he : (fun t => damped A z t*x)=(fun t : ℝ => ∑ k ∈ Finset.range (finrank ℂ R),
      (Complex.exp ((μ-z)*t)*(t:ℂ)^k) • ((k.factorial:ℂ)⁻¹ • ((A-μ • 1)^k*x))) :=
    funext (damped_mul_component A z μ x hx)
  rw [he]
  constructor
  · exact integrable_finsetSum _ (fun k _ => (ScalarDecay.exp_pow_integrable _ hμ k).smul_const _)
  · simpa using tendsto_finsetSum (Finset.range (finrank ℂ R))
      (fun k _ => (ScalarDecay.exp_pow_tendsto_zero _ hμ k).smul_const
        ((k.factorial:ℂ)⁻¹ • ((A-μ • 1)^k*x)))

theorem spectral_decay (A : R) (z : ℂ) (hz : ∀ μ∈spectrum ℂ A,μ.re < z.re) :
    IntegrableOn (damped A z) (Ioi 0) ∧ Tendsto (damped A z) atTop (𝓝 0) := by
  have h (x : R) : IntegrableOn (fun t => damped A z t*x) (Ioi 0) ∧
      Tendsto (fun t => damped A z t*x) atTop (𝓝 0) := by
    apply Submodule.iSup_induction (Module.End.maxGenEigenspace (LinearMap.mulLeft ℂ A))
      (x := x) (motive := fun x => IntegrableOn (fun t : ℝ => damped A z t*x) (Ioi 0) volume ∧
        Tendsto (fun t => damped A z t*x) atTop (𝓝 0))
      (by rw [Module.End.iSup_maxGenEigenspace_eq_top]; trivial)
    · exact component_decay A z hz
    · simp
    · intro x y hx hy
      simpa only [Pi.add_def,mul_add,add_zero] using And.intro (hx.1.add hy.1) (hx.2.add hy.2)
  simpa using h 1


theorem spectral_laplace_inverse (A : R) (z : ℂ)
    (hz : ∀ μ∈spectrum ℂ A,μ.re < z.re) :
    IntegrableOn (damped A z) (Ioi 0) ∧ IsUnit (algebraMap ℂ R z-A) ∧
      (∫ t in Ioi 0,damped A z t)=Ring.inverse (algebraMap ℂ R z-A) := by
  have hs := spectral_decay A z hz
  let B := A-algebraMap ℂ R z
  have he : damped A z=transfer B := funext (damped_eq_shifted A z)
  rw [he] at hs ⊢
  have hl := integral_Ioi_of_hasDerivAt_of_tendsto'
    (fun t (_ : t∈Ici (0:ℝ)) => transfer_derivative_left B t)
    ((ContinuousLinearMap.mul ℝ R B).integrable_comp hs.1) hs.2
  have hr := integral_Ioi_of_hasDerivAt_of_tendsto'
    (fun t (_ : t∈Ici (0:ℝ)) => transfer_derivative_right B t)
    (((ContinuousLinearMap.mul ℝ R).flip B).integrable_comp hs.1) hs.2
  rw [integral_const_mul_of_integrable hs.1,transfer_zero,zero_sub] at hl
  rw [integral_mul_const_of_integrable hs.1,transfer_zero,zero_sub] at hr
  have hn : algebraMap ℂ R z-A= -B := by dsimp [B]; abel
  have hl' : (algebraMap ℂ R z-A)*(∫ t in Ioi 0,transfer B t)=1 := by
    rw [hn,neg_mul,hl,neg_neg]
  have hr' : (∫ t in Ioi 0,transfer B t)*(algebraMap ℂ R z-A)=1 := by
    rw [hn,mul_neg,hr,neg_neg]
  have hu : IsUnit (algebraMap ℂ R z-A) := ⟨⟨_,_,hl',hr'⟩,rfl⟩
  refine ⟨hs.1,hu,?_⟩
  calc
    _ = Ring.inverse (algebraMap ℂ R z-A)*((algebraMap ℂ R z-A)*(∫ t in Ioi 0,transfer B t)) :=
      (Ring.inverse_mul_cancel_left _ _ hu).symm
    _ = _ := by rw [hl',mul_one]

theorem nonnormal_self_energy (A U V : R) (z : ℂ)
    (hz : ∀ μ∈spectrum ℂ A,μ.re < z.re) :
    IntegrableOn (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V)) (Ioi 0) ∧
    (∫ t : ℝ in Ioi 0,Complex.exp (-z*t) • (U*transfer A t*V))=
      U*Ring.inverse (algebraMap ℂ R z-A)*V := by
  have h := spectral_laplace_inverse A z hz
  have he : (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V))=
      (fun t => U*damped A z t*V) := by
    ext t
    simp [damped,Algebra.mul_smul_comm,Algebra.smul_mul_assoc]
  rw [he]
  have hu : IntegrableOn (fun t => U*damped A z t) (Ioi 0) :=
    (ContinuousLinearMap.mul ℝ R U).integrable_comp h.1
  refine ⟨((ContinuousLinearMap.mul ℝ R).flip V).integrable_comp hu,?_⟩
  rw [integral_mul_const_of_integrable hu,integral_const_mul_of_integrable h.1,h.2.2]

end KomorebiPaperVI.NonnormalMemory
