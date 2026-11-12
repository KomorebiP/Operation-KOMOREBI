import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-! Actual weighted resistor-node elimination, not a scalar substitute.
Author: Komorebi P. Retained vertices form any finite type; parallel
conductances have already been added. Zero-degree nodes are covered separately.
-/
namespace SmithStarMesh
open scoped BigOperators
variable {V : Type*} [Fintype V]

noncomputable def degree (g : V → ℝ) : ℝ := ∑ v, g v
noncomputable def moment (g u : V → ℝ) : ℝ := ∑ v, g v*u v
noncomputable def eliminatedPotential (g u : V → ℝ) : ℝ := moment g u / degree g
noncomputable def mesh (g : V → ℝ) (i j : V) : ℝ := g i*g j/degree g

theorem star_kcl (g u : V → ℝ) (v : ℝ) :
    (∑ j, g j*(v-u j)) = v*degree g-moment g u := by
  simp_rw [mul_sub]
  rw [Finset.sum_sub_distrib]
  simp [degree,moment,Finset.mul_sum,mul_comm]

theorem extends_kcl (g u : V → ℝ) (h : degree g ≠ 0) :
    (∑ j, g j*(eliminatedPotential g u-u j)) = 0 := by
  rw [star_kcl]
  unfold eliminatedPotential
  field_simp [h]
  ring

theorem kcl_forces_potential (g u : V → ℝ) (v : ℝ) (h : degree g ≠ 0)
    (hkcl : (∑ j, g j*(v-u j)) = 0) : v=eliminatedPotential g u := by
  rw [star_kcl] at hkcl
  unfold eliminatedPotential
  apply (eq_div_iff h).2
  linarith

theorem current_identity (g u : V → ℝ) (h : degree g ≠ 0) (i : V) :
    (∑ j, mesh g i j*(u i-u j)) = g i*(u i-eliminatedPotential g u) := by
  calc
    _ = ∑ j, (g i/degree g)*(u i*g j-g j*u j) := by
      apply Finset.sum_congr rfl
      intro j hj
      unfold mesh
      ring
    _ = (g i/degree g)*(∑ j, (u i*g j-g j*u j)) := by rw [Finset.mul_sum]
    _ = (g i/degree g)*(u i*degree g-moment g u) := by
      rw [Finset.sum_sub_distrib,← Finset.mul_sum]
      rfl
    _ = _ := by unfold eliminatedPotential; field_simp [h]

theorem mesh_symmetric (g : V → ℝ) (i j : V) : mesh g i j=mesh g j i := by
  unfold mesh
  ring

theorem mesh_nonnegative (g : V → ℝ) (hg : ∀ i, 0 ≤ g i) (hG : 0 < degree g)
    (i j : V) : 0 ≤ mesh g i j :=
  div_nonneg (mul_nonneg (hg i) (hg j)) hG.le

theorem retained_current (h : V → V → ℝ) (g u : V → ℝ) (hG : degree g ≠ 0)
    (i : V) :
    (∑ j, (h i j+mesh g i j)*(u i-u j)) =
      (∑ j, h i j*(u i-u j))+g i*(u i-eliminatedPotential g u) := by
  simp_rw [add_mul]
  rw [Finset.sum_add_distrib,current_identity g u hG i]

theorem zero_degree (g : V → ℝ) (hg : ∀ i, 0 ≤ g i) (hG : degree g=0)
    (i : V) : g i=0 := by
  have hle : g i ≤ degree g := by
    exact Finset.single_le_sum (fun j hj => hg j) (Finset.mem_univ i)
  rw [hG] at hle
  exact le_antisymm hle (hg i)

end SmithStarMesh
