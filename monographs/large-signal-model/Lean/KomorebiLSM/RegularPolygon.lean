import KomorebiLSM.RegularPolygonAngles
import Mathlib.Analysis.InnerProductSpace.Dual
import Mathlib.Analysis.Convex.Topology
import Mathlib.Analysis.LocallyConvex.Separation
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Tactic

set_option autoImplicit false
namespace Komorebi.LSM.RegularPolygon

theorem ball_subset_convexHull_of_support (s : Set ℂ) (hs : s.Finite) (r : ℝ)
    (hsupport : ∀ v : ℂ, ∃ p ∈ s, ‖v‖*r ≤ inner ℝ v p) :
    {z : ℂ | ‖z‖≤r} ⊆ convexHull ℝ s := by
  intro z hz
  by_contra hnot
  obtain ⟨f,u,hfu,huz⟩ := geometric_hahn_banach_closed_point
    (convex_convexHull ℝ s) (hs.isCompact_convexHull ℝ).isClosed hnot
  let v : ℂ := (InnerProductSpace.toDual ℝ ℂ).symm f
  have hf (x : ℂ) : f x = inner ℝ v x :=
    (InnerProductSpace.toDual_symm_apply (x:=x) (y:=f)).symm
  obtain ⟨p,hp,hvp⟩ := hsupport v
  have hp' := hfu p (subset_convexHull ℝ s hp)
  have hz' : f z ≤ ‖v‖*r := by
    rw [hf]
    exact (real_inner_le_norm v z).trans (mul_le_mul_of_nonneg_left hz (norm_nonneg v))
  rw [hf] at hp'
  linarith

theorem attenuation_cos_of_vertex_bound {η : ℝ} (hη : 0<η) {n : ℕ}
    (hn : 0<n) (hbound : Real.pi/Real.sqrt (2*η) ≤ (n:ℝ)) :
    1-η ≤ Real.cos (Real.pi/(n:ℝ)) := by
  have hs : 0<Real.sqrt (2*η) := Real.sqrt_pos.2 (by positivity)
  have hnR : (0:ℝ)<n := by exact_mod_cast hn
  have hp : Real.pi ≤ (n:ℝ)*Real.sqrt (2*η) := (div_le_iff₀ hs).mp hbound
  have hangle : Real.pi/(n:ℝ) ≤ Real.sqrt (2*η) :=
    (div_le_iff₀ hnR).mpr (by simpa [mul_comm] using hp)
  have hsq : (Real.pi/(n:ℝ))^2 ≤ 2*η := by
    have h0 : 0≤Real.pi/(n:ℝ) := by positivity
    have he := Real.sq_sqrt (by positivity : 0≤2*η)
    nlinarith
  have hc := Real.one_sub_sq_div_two_le_cos (x:=Real.pi/(n:ℝ))
  linarith

noncomputable def polygon (n : ℕ) : Set ℂ := convexHull ℝ (Set.range (vertex n))

theorem polygon_closed (n : ℕ) : IsClosed (polygon n) :=
  ((Set.finite_range (vertex n)).isCompact_convexHull ℝ).isClosed

theorem polygon_convex (n : ℕ) : Convex ℝ (polygon n) := convex_convexHull ℝ _

theorem closedBall_subset_polygon (n : ℕ) (hn : 3≤n) :
    Metric.closedBall (0:ℂ) (Real.cos (Real.pi/(n:ℝ))) ⊆ polygon n := by
  intro z hz
  refine (ball_subset_convexHull_of_support (Set.range (vertex n)) (Set.finite_range _)
    (Real.cos (Real.pi/(n:ℝ))) ?_) ?_
  · intro v
    obtain ⟨j,hj⟩ := support_lower n hn v
    exact ⟨vertex n j,⟨j,rfl⟩,hj⟩
  · change ‖z‖≤Real.cos (Real.pi/(n:ℝ))
    simpa only [Metric.mem_closedBall,dist_zero_right] using hz

theorem polygon_subset_closedBall (n : ℕ) : polygon n ⊆ Metric.closedBall (0:ℂ) 1 := by
  apply convexHull_min ?_ (convex_closedBall (0:ℂ) 1)
  rintro _ ⟨j,rfl⟩
  simp only [Metric.mem_closedBall,dist_zero_right,vertex_norm,le_refl]

theorem cos_radius_nonneg (n : ℕ) (hn : 3≤n) : 0≤Real.cos (Real.pi/(n:ℝ)) := by
  have hnR : (3:ℝ)≤n := by exact_mod_cast hn
  have hp : (0:ℝ)<n := by linarith
  apply Real.cos_nonneg_of_mem_Icc
  constructor
  · have : 0≤Real.pi/(n:ℝ) := by positivity
    linarith [Real.pi_pos]
  · apply (div_le_iff₀ hp).mpr
    nlinarith [Real.pi_pos]

theorem zero_mem_polygon (n : ℕ) (hn : 3≤n) : (0:ℂ) ∈ polygon n :=
  closedBall_subset_polygon n hn (by simpa using cos_radius_nonneg n hn)

theorem one_mem_polygon (n : ℕ) (hn : 0<n) : (1:ℂ) ∈ polygon n := by
  have he : vertex n ⟨0,hn⟩=(1:ℂ) := by simp [vertex]
  rw [← he]
  exact subset_convexHull ℝ _ ⟨_,rfl⟩

theorem scaled_rotation_mem_polygon (n : ℕ) (hn : 3≤n) (q : Circle)
    (α : ℝ) (hα : 0≤α) (hsmall : α≤Real.cos (Real.pi/(n:ℝ)))
    (z : ℂ) (hz : z∈polygon n) : α • ((q:ℂ)*z) ∈ polygon n := by
  apply closedBall_subset_polygon n hn
  have hz1 : ‖z‖≤1 := by simpa only [Metric.mem_closedBall,dist_zero_right] using polygon_subset_closedBall n hz
  simp only [Metric.mem_closedBall,dist_zero_right,norm_smul,Real.norm_eq_abs,abs_of_nonneg hα,norm_mul,Circle.norm_coe,one_mul]
  exact (mul_le_of_le_one_right hα hz1).trans hsmall

noncomputable def sufficientVertexCount (η : ℝ) : ℕ :=
  max 3 ⌈Real.pi/Real.sqrt (2*η)⌉₊

theorem sufficient_vertex_count (η : ℝ) (hη : 0<η) :
    3≤sufficientVertexCount η ∧ 1-η ≤ Real.cos (Real.pi/(sufficientVertexCount η:ℝ)) := by
  have hn : 3≤sufficientVertexCount η := le_max_left _ _
  refine ⟨hn,attenuation_cos_of_vertex_bound hη (by omega) ?_⟩
  exact (Nat.le_ceil _).trans (by exact_mod_cast (le_max_right 3 ⌈Real.pi/Real.sqrt (2*η)⌉₊))

end Komorebi.LSM.RegularPolygon
