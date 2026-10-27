import KomorebiLSM.Block8Examples
import KomorebiLSM.ReconciliationHilbert
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.SpecificLimits.Normed

/-! Concrete nonlinear, chart and horizon examples. All equalities are exact;
no sampled trajectories establish the general limits or bounds. -/
set_option autoImplicit false
open scoped BigOperators Topology
open Filter
namespace Komorebi.LSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.PacketApproximation
open Komorebi.LSM.Reconciliation Komorebi.LSM.Block8Examples

noncomputable def rate (n : ℕ) : ℝ := (n:ℝ)/((n:ℝ)+1)

theorem rate_bounds (n : ℕ) : 0 ≤ rate n ∧ rate n < 1 := by
  have hn : (0:ℝ) ≤ n := Nat.cast_nonneg n
  constructor
  · exact div_nonneg hn (by linarith)
  · apply (div_lt_one (by positivity : (0:ℝ) < n+1)).mpr
    linarith

theorem rate_tendsto : Tendsto rate atTop (𝓝 1) := tendsto_natCast_div_add_atTop 1

theorem scale_power_apply (r x : ℝ) (k : ℕ) : ((scale r)^k) x=r^k*x := by
  induction k with
  | zero => simp
  | succ k ih => rw [pow_succ',mul_apply_eq_comp,ih,scale_apply,pow_succ']; ring

/-- The general fixed-power theorem applies even though uniform-in-time error
will fail below. These are approximating operators, not projection maps. -/
theorem scalar_fixed_horizon_convergence (x : ℝ) (k : ℕ) :
    Tendsto (fun n => ((scale (rate n))^k) x) atTop (𝓝 x) := by
  have h := strong_fixed_powers (fun n => scale (rate n)) (ContinuousLinearMap.id ℝ ℝ)
    (C:=1) (fun n => by rw [scale_norm,abs_of_nonneg (rate_bounds n).1]; exact (rate_bounds n).2.le)
    (fun y => by simpa only [scale_apply,one_mul] using rate_tendsto.mul_const y) x k
  simpa using h

theorem each_resolution_has_large_late_error (n : ℕ) :
    Tendsto (fun k : ℕ => ‖((scale (rate n))^k) (1:ℝ)-1‖) atTop (𝓝 1) := by
  have h := (tendsto_pow_atTop_nhds_zero_of_lt_one (rate_bounds n).1 (rate_bounds n).2).sub_const 1
  have hn := h.norm
  simpa only [scale_power_apply,mul_one,zero_sub,norm_neg,norm_one] using hn

theorem refinement_horizon_cannot_be_exchanged :
    ‖((scale (rate 1))^1) (1:ℝ)-1‖=1/2 ∧
    ‖((scale (rate 1))^2) (1:ℝ)-1‖=3/4 := by
  norm_num [scale_power_apply,rate]

noncomputable def packet (i : Bool) : (ℝ×ℝ) →L[ℝ] (ℝ×ℝ) :=
  if i then (0 : (ℝ×ℝ) →L[ℝ] ℝ).prod (ContinuousLinearMap.snd ℝ ℝ ℝ)
  else (ContinuousLinearMap.fst ℝ ℝ ℝ).prod 0

noncomputable def sumCoordinate : (ℝ×ℝ) →L[ℝ] ℝ :=
  ContinuousLinearMap.fst ℝ ℝ ℝ+ContinuousLinearMap.snd ℝ ℝ ℝ

noncomputable def powerTerm (m : ℕ) :
    ContinuousMultilinearMap ℝ (fun _ : Fin (m+1) => ℝ×ℝ) ℝ :=
  (ContinuousMultilinearMap.mkPiAlgebra ℝ (Fin (m+1)) ℝ).compContinuousLinearMap
    (fun _ => sumCoordinate)

theorem packet_complete (x : ℝ×ℝ) : ∑ i : Bool, packet i x=x := by
  ext <;> simp [packet]

theorem packet_contractive (i : Bool) : ‖packet i‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro x
  cases i <;> simp [packet,Prod.norm_def]

theorem packet_range_coordinate_norm (i : Bool) (v : ℝ×ℝ)
    (hv : v ∈ LinearMap.range (packet i).toLinearMap) : |v.1+v.2|=‖v‖ := by
  obtain ⟨w,hw⟩ := hv
  rw [← hw]
  cases i <;> simp [packet,Prod.norm_def,Real.norm_eq_abs]

theorem powerTerm_apply (m : ℕ) (v : Fin (m+1) → ℝ×ℝ) :
    powerTerm m v=∏ k, ((v k).1+(v k).2) := by
  simp [powerTerm,sumCoordinate]

theorem powerTerm_packet_bound (m : ℕ) (f : Fin (m+1) → Bool) :
    HasPacketBound packet (powerTerm m) f 1 := by
  intro v hv
  rw [powerTerm_apply,one_mul,Real.norm_eq_abs,Finset.abs_prod]
  apply le_of_eq
  exact Finset.prod_congr rfl (fun k _ => packet_range_coordinate_norm (f k) (v k) (hv k))

noncomputable def diagonalTuples (m : ℕ) : Finset (Fin (m+1) → Bool) :=
  {fun _ => false,fun _ => true}

noncomputable def fullQuadratic : (ℝ×ℝ) → ℝ :=
  fullPolynomial 2 (fun m => powerTerm m.val) 0

noncomputable def diagonalQuadratic : (ℝ×ℝ) → ℝ :=
  retainedPolynomial 2 packet (fun m => powerTerm m.val) (fun m => diagonalTuples m.val) 0

theorem fullQuadratic_formula (x : ℝ×ℝ) :
    fullQuadratic x=x.1+x.2+(x.1+x.2)^2 := by
  simp [fullQuadratic,fullPolynomial,Fin.sum_univ_succ,powerTerm_apply,Fin.prod_univ_succ]
  ring

theorem diagonalQuadratic_formula (x : ℝ×ℝ) :
    diagonalQuadratic x=x.1+x.2+x.1^2+x.2^2 := by
  simp [diagonalQuadratic,retainedPolynomial,Fin.sum_univ_succ,diagonalTuples,
    powerTerm_apply,Fin.prod_univ_succ,packet,funext_iff]
  ring

theorem quadratic_omitted_interaction (x : ℝ×ℝ) :
    fullQuadratic x-diagonalQuadratic x=2*x.1*x.2 := by
  rw [fullQuadratic_formula,diagonalQuadratic_formula]
  ring

theorem quadratic_sharp_error (x : ℝ×ℝ) :
    ‖fullQuadratic x-diagonalQuadratic x‖=2*|x.1|*|x.2| := by
  rw [quadratic_omitted_interaction,Real.norm_eq_abs,abs_mul,abs_mul]
  norm_num

/-- The true block bounds above instantiate the general ordered-tuple theorem. -/
theorem quadratic_general_truncation_bound (x : ℝ×ℝ) :
    ‖fullQuadratic x-diagonalQuadratic x‖ ≤
      ∑ m : Fin 2, ∑ f ∈ Finset.univ \ diagonalTuples m.val,
        (1:ℝ)*∏ k, ‖packet (f k) x‖ := by
  exact packet_interaction_truncation_bound 2 packet packet_complete
    (fun m => powerTerm m.val) (fun m => diagonalTuples m.val) (fun _ _ => 1)
    (fun m f => powerTerm_packet_bound m.val f) 0 x

theorem quadratic_general_lipschitz (x y : ℝ×ℝ) {R : ℝ} (hR : 0 ≤ R)
    (hx : ‖x‖ ≤ R) (hy : ‖y‖ ≤ R) :
    ‖diagonalQuadratic x-diagonalQuadratic y‖ ≤
      (∑ m : Fin 2, ∑ _f ∈ diagonalTuples m.val, (m.val+1:ℕ)*(1:ℝ)*R^m.val)*‖x-y‖ := by
  exact retained_polynomial_lipschitz_bound 2 packet packet_contractive
    (fun m => powerTerm m.val) (fun m => diagonalTuples m.val) (fun _ _ => 1)
    (fun _ _ => zero_le_one) (fun m f => powerTerm_packet_bound m.val f) 0 hR x y hx hy

theorem nonlinear_cross_term_numeric : fullQuadratic (2,3)-diagonalQuadratic (2,3)=12 := by
  rw [quadratic_omitted_interaction]
  norm_num

noncomputable def chartWeights : Fin 2 → ℝ := ![1/4,3/4]
noncomputable def chartFits : Fin 2 → ℝ := ![2,4]

theorem chartWeights_total : ∑ i, chartWeights i=1 := by norm_num [chartWeights,Fin.sum_univ_succ]

theorem chart_mean : weightedMean chartWeights chartFits=7/2 := by
  norm_num [weightedMean,chartWeights,chartFits,Fin.sum_univ_succ]

theorem chart_minimum_cost : weightedCost chartWeights chartFits (7/2)=3/4 := by
  norm_num [weightedCost,chartWeights,chartFits,Fin.sum_univ_succ]

theorem chart_unique_minimum : ∀ x : ℝ,
    weightedCost chartWeights chartFits x=3/4 ↔ x=7/2 := by
  intro x
  have h := weighted_cost_eq_minimum_iff chartWeights chartFits chartWeights_total x
  simpa only [chart_mean,chart_minimum_cost] using h

theorem unanimous_wrong_fit : weightedMean chartWeights (fun _ => (4:ℝ))=4 := by
  norm_num [weightedMean,chartWeights,Fin.sum_univ_succ]

noncomputable def redundantAtlas : LinearAtlas ℝ (ℝ×ℝ) where
  analysis := (LinearMap.id).prod (2 • LinearMap.id)
  synthesis := LinearMap.fst ℝ ℝ ℝ
  reconstruct := fun _ => rfl

noncomputable def scaledAtlas : LinearAtlas ℝ ℝ where
  analysis := 3 • LinearMap.id
  synthesis := (1/3:ℝ) • LinearMap.id
  reconstruct := by intro x; change (1/3:ℝ)*(3*x)=x; ring

theorem chart_transport_exact :
    redundantAtlas.transport scaledAtlas (redundantAtlas.encode 2)=scaledAtlas.encode 2 := by
  simp [LinearAtlas.transport]

theorem chart_transport_isometry :
    letI := redundantAtlas.coeffNormed
    letI := scaledAtlas.coeffNormed
    Isometry (redundantAtlas.transport scaledAtlas) :=
  redundantAtlas.transport_isometry scaledAtlas

theorem invalid_redundant_coefficient : (1,0) ∉ redundantAtlas.analysis.range := by
  rintro ⟨x,h⟩
  have h1 := congrArg Prod.fst h
  have h2 := congrArg Prod.snd h
  change x=1 at h1
  change (2:ℝ)*x=0 at h2
  linarith

theorem repaired_ambient_output_is_realizable (L : ℝ →ₗ[ℝ] ℝ) :
    redundantAtlas.repaired L (1,0) ∈ redundantAtlas.analysis.range :=
  redundantAtlas.repaired_consistent L (1,0)

end Komorebi.LSM.Block8ApproximationExamples
