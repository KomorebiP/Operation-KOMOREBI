import KomorebiLSM.RationalTransform
import Mathlib.Topology.Compactness.Compact

set_option autoImplicit false
namespace Komorebi.LSM.StrictRationalGeometry
open scoped Topology
open Filter LorentzCylinder RobustOrientedMargin RationalTransform
noncomputable section
variable {n : ℕ}

/-- Joint output continuity uses the literal inverse-conjugated density. -/
theorem continuousAt_conjugated_slack (G : Fin n → RationalMatrix) (T : RealMatrix)
    (hT : IsUnit T.det) (y : ℝ × ℂ) :
    ContinuousAt (fun Ty : RealMatrix × (ℝ × ℂ) => slack (conjugated Ty.1 G Ty.2.1 (1,Ty.2.2))) (T,y) := by
  have hcoords : Continuous (fun Ty : RealMatrix × (ℝ × ℂ) => (Ty.1,Ty.2.1)) :=
    continuous_fst.prodMk continuous_snd.fst
  have hc : ContinuousAt (fun Ty : RealMatrix × (ℝ × ℂ) => conjugated Ty.1 G Ty.2.1) (T,y) :=
    ContinuousAt.comp (f := fun Ty : RealMatrix × (ℝ × ℂ) => (Ty.1,Ty.2.1))
      (x := (T,y)) (continuousAt_conjugated G T hT y.1) (hcoords.continuousAt (x := (T,y)))
  have hz : Continuous (fun Ty : RealMatrix × (ℝ × ℂ) => ((1 : ℝ),Ty.2.2)) :=
    continuous_const.prodMk continuous_snd.snd
  exact continuous_slack.continuousAt.comp (hc.clm_apply (hz.continuousAt (x := (T,y))))

/-- Compact observation and input sets turn pointwise continuity into one transform neighborhood. -/
theorem eventually_margin (G : Fin n → RationalMatrix) (T : RealMatrix)
    (hT : IsUnit T.det) (kappa : ℝ)
    (hmargin : ∀ u∈Set.Icc (-1 : ℝ) 1, kappa<sigma (conjugated T G u)) :
    ∀ᶠ S in 𝓝 T, ∀ u∈Set.Icc (-1 : ℝ) 1, kappa<sigma (conjugated S G u) := by
  let K : Set (ℝ × ℂ) := Set.Icc (-1 : ℝ) 1  ×ˢ Metric.closedBall 0 1
  have hK : IsCompact K := isCompact_Icc.prod (isCompact_closedBall (0 : ℂ) 1)
  have hpoint : ∀ y∈K, ∀ᶠ Ty : RealMatrix × (ℝ × ℂ) in 𝓝 (T,y),
      kappa<slack (conjugated Ty.1 G Ty.2.1 (1,Ty.2.2)) := by
    intro y hy
    have hv : ‖y.2‖≤1 := by simpa using hy.2
    have hm := (hmargin y.1 hy.1).trans_le (sigma_le (conjugated T G y.1) y.2 hv)
    exact (continuousAt_conjugated_slack G T hT y).eventually (Ioi_mem_nhds hm)
  have he := hK.eventually_forall_of_forall_eventually (x₀ := T)
    (P := fun S y => kappa<slack (conjugated S G y.1 (1,y.2))) hpoint
  filter_upwards [he] with S hS
  intro u hu
  apply hS (u,worstInput (conjugated S G u))
  exact ⟨hu,by simpa using worstInput_mem (conjugated S G u)⟩

theorem eventually_initial (T : RealMatrix) (z : State ℂ) (hz : 0<slack (operator T z)) :
    ∀ᶠ S in 𝓝 T, 0<slack (operator S z) := by
  have hc : Continuous (fun S : RealMatrix => slack (operator S z)) :=
    continuous_slack.comp (continuous_operator.clm_apply continuous_const)
  exact hc.continuousAt.eventually (Ioi_mem_nhds hz)

/-- A real strict finite sector contains an actual rational mass-preserving invertible transform. -/
theorem rational_strict_sector {I A J : Type*} [Fintype I] [Fintype A] [Fintype J]
    (G : I → A → Fin n → RationalMatrix) (z : J → State ℂ)
    (T : RealMatrix) (hT : IsUnit T.det) (hmass : MassPreserving T)
    (hinit : ∀ j, 0<slack (operator T (z j))) (eta : ℝ) (heta : 0<eta)
    (hmargin : ∀ i a u, u∈Set.Icc (-1 : ℝ) 1 → eta≤sigma (conjugated T (G i a) u)) :
    ∃ q : Parameters ℚ, ∃ kappa : ℚ, 0<kappa ∧ IsUnit (affineMatrix q).det ∧
      (∀ j, 0<slack (operator (castMatrix (affineMatrix q)) (z j))) ∧
      ∀ i a u, u∈Set.Icc (-1 : ℝ) 1 →
        (kappa : ℝ)<sigma (PolynomialGram.operatorPolynomial
          (fun k => RationalBernsteinMargin.matrixOperator
            (rationalConjugated (affineMatrix q) (G i a) k)) u) := by
  obtain ⟨kappa,hk0,hketa⟩ := exists_rat_btwn heta
  have hi : ∀ᶠ S in 𝓝 T, ∀ j,0<slack (operator S (z j)) :=
    Filter.eventually_all.mpr (fun j => eventually_initial T (z j) (hinit j))
  have hf : ∀ᶠ S in 𝓝 T, ∀ i a u,u∈Set.Icc (-1 : ℝ) 1 →
      (kappa : ℝ)<sigma (conjugated S (G i a) u) := by
    apply Filter.eventually_all.mpr
    intro i
    apply Filter.eventually_all.mpr
    intro a
    exact eventually_margin (G i a) T hT kappa (fun u hu => hketa.trans_le (hmargin i a u hu))
  have hd : ∀ᶠ S in 𝓝 T, IsUnit S.det := by
    have hne : T.det≠0 := isUnit_iff_ne_zero.mp hT
    have he := continuous_id.matrix_det.continuousAt.eventually
      (isOpen_ne.mem_nhds hne)
    simpa [isUnit_iff_ne_zero] using he
  have hall : ∀ᶠ S in 𝓝 T, IsUnit S.det ∧ (∀ j,0<slack (operator S (z j))) ∧
      ∀ i a u,u∈Set.Icc (-1 : ℝ) 1 → (kappa : ℝ)<sigma (conjugated S (G i a) u) := by
    filter_upwards [hd,hi,hf] with S hS hI hF
    exact ⟨hS,hI,hF⟩
  have hc : Tendsto (affineMatrix (R := ℝ)) (𝓝 (parametersOf T)) (𝓝 T) := by
    have hcont : Tendsto (affineMatrix (R := ℝ)) (𝓝 (parametersOf T))
        (𝓝 (affineMatrix (parametersOf T))) := continuous_affineMatrix.continuousAt
    rwa [affineMatrix_parametersOf T hmass] at hcont
  obtain ⟨q,hq⟩ := dense_castParameters.mem_nhds (hc.eventually hall)
  change IsUnit (affineMatrix (castParameters q)).det ∧
    (∀ j, 0<slack (operator (affineMatrix (castParameters q)) (z j))) ∧
    (∀ i a u, u∈Set.Icc (-1 : ℝ) 1 →
      (kappa : ℝ)<sigma (conjugated (affineMatrix (castParameters q)) (G i a) u)) at hq
  rw [affineMatrix_cast] at hq
  have hqdet := unit_of_castMatrix (affineMatrix q) hq.1
  refine ⟨q,kappa,by exact_mod_cast hk0,hqdet,hq.2.1,?_⟩
  intro i a u hu
  rw [rational_conjugated_operator (affineMatrix q) hqdet]
  exact hq.2.2 i a u hu

end
end Komorebi.LSM.StrictRationalGeometry
