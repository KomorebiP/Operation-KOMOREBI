import Mathlib.LinearAlgebra.Dual.Lemmas

/-! The compatible equation target is the annihilator of the remaining dual
syzygies. Algebraic dual separation proves the image theorem over any field,
without a finite-dimensional hypothesis. -/

namespace Komorebi.StrongArtin.SyzygyCompatibleTarget

noncomputable section

variable {k U W : Type*} [Field k]
  [AddCommGroup U] [Module k U] [AddCommGroup W] [Module k W]

/-- Equations invisible to all remaining dual syzygies. -/
def compatibleTarget (S : Submodule k (Module.Dual k W)) : Submodule k W :=
  S.dualCoannihilator

@[simp] theorem mem_compatibleTarget (S : Submodule k (Module.Dual k W)) (w : W) :
    w ∈ compatibleTarget S ↔ ∀ phi ∈ S, phi w = 0 :=
  Submodule.mem_dualCoannihilator w

/-- The algebraic dual detects exactly the failure to lie in a linear image. -/
theorem range_eq_compatibleTarget_dualKernel (J : U →ₗ[k] W) :
    LinearMap.range J = compatibleTarget (LinearMap.ker J.dualMap) := by
  rw [compatibleTarget, LinearMap.ker_dualMap_eq_dualAnnihilator_range,
    Subspace.dualAnnihilator_dualCoannihilator_eq]

/-- This is the exact target requested by the v0.23 handoff. -/
theorem range_eq_compatibleTarget_of_dualKernel_eq
    (J : U →ₗ[k] W) (S : Submodule k (Module.Dual k W))
    (hS : LinearMap.ker J.dualMap = S) :
    LinearMap.range J = compatibleTarget S := by
  rw [← hS]
  exact range_eq_compatibleTarget_dualKernel J

/-- An affine correction exists precisely when its error satisfies all syzygies. -/
theorem correction_exists_iff_compatible
    (J : U →ₗ[k] W) (S : Submodule k (Module.Dual k W))
    (hS : LinearMap.ker J.dualMap = S) (e : W) :
    (∃ u : U, J u + e = 0) ↔ e ∈ compatibleTarget S := by
  rw [← range_eq_compatibleTarget_of_dualKernel_eq J S hS]
  constructor
  · rintro ⟨u, hu⟩
    refine ⟨-u, ?_⟩
    rw [map_neg, eq_neg_of_add_eq_zero_left hu, neg_neg]
  · rintro ⟨u, rfl⟩
    exact ⟨-u, by simp⟩

/-- Corestriction does not alter the equation; it removes the unreachable codomain. -/
def toCompatibleTarget
    (J : U →ₗ[k] W) (S : Submodule k (Module.Dual k W))
    (hS : LinearMap.ker J.dualMap = S) : U →ₗ[k] compatibleTarget S :=
  J.codRestrict (compatibleTarget S) (fun u => by
    rw [← range_eq_compatibleTarget_of_dualKernel_eq J S hS]
    exact ⟨u, rfl⟩)

theorem toCompatibleTarget_surjective
    (J : U →ₗ[k] W) (S : Submodule k (Module.Dual k W))
    (hS : LinearMap.ker J.dualMap = S) :
    Function.Surjective (toCompatibleTarget J S hS) := by
  intro w
  have hw : (w : W) ∈ LinearMap.range J := by
    rw [range_eq_compatibleTarget_of_dualKernel_eq J S hS]
    exact w.property
  obtain ⟨u, hu⟩ := hw
  exact ⟨u, Subtype.ext hu⟩

/-- A violated syzygy certifies that no correction is possible. -/
theorem no_correction_of_syzygy_witness
    (J : U →ₗ[k] W) (phi : Module.Dual k W)
    (hphi : phi ∈ LinearMap.ker J.dualMap) (e : W) (hne : phi e ≠ 0) :
    ¬ ∃ u : U, J u + e = 0 := by
  intro h
  have he := (correction_exists_iff_compatible J (LinearMap.ker J.dualMap) rfl e).mp h
  exact hne ((mem_compatibleTarget _ _).mp he phi hphi)

end
end Komorebi.StrongArtin.SyzygyCompatibleTarget

#print axioms Komorebi.StrongArtin.SyzygyCompatibleTarget.range_eq_compatibleTarget_dualKernel
#print axioms Komorebi.StrongArtin.SyzygyCompatibleTarget.correction_exists_iff_compatible
#print axioms Komorebi.StrongArtin.SyzygyCompatibleTarget.toCompatibleTarget_surjective
#print axioms Komorebi.StrongArtin.SyzygyCompatibleTarget.no_correction_of_syzygy_witness
