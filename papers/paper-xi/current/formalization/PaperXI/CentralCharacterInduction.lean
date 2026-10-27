import PaperXI.OpenSubgroupSmoothInduction

/-!
# The central action of actual induction

The scalar on a central element of the inducing subgroup remains the scalar on
the actual induced representation. Consequently, two different such scalars
cannot be related by a nonzero ambient intertwiner. No irreducibility hypothesis
or finite-index hypothesis is used.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralCharacterInduction

open Representation PaperXI.OpenSubgroupSmoothInduction

variable {k G V W : Type*} [Field k] [Group G]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]

/-- The action of a central inducing element on genuine induction is its
prescribed scalar. This checks the right-translation convention explicitly. -/
theorem ind_central_scalar (H : Subgroup G) (σ : Representation k H V)
    (z : H) (hz : ∀ g : G, Commute (z : G) g) (c : k)
    (hσ : σ z = c • LinearMap.id) :
    ind H.subtype σ (z : G) = c • LinearMap.id := by
  apply IndV.hom_ext
  intro g
  ext v
  rw [LinearMap.comp_apply, ind_mk]
  have hcomm : g * (z : G)⁻¹ = (z : G)⁻¹ * g :=
    ((hz g).inv_left).eq.symm
  rw [hcomm, mk_subgroup, hσ]
  simp

/-- An intertwiner between two actions with different central scalars is zero.
The conclusion concerns the actual linear map, without any Schur shortcut. -/
theorem intertwiner_eq_zero_of_scalar_ne
    (ρ : Representation k G V) (τ : Representation k G W) (z : G)
    (c d : k) (hc : ρ z = c • LinearMap.id)
    (hd : τ z = d • LinearMap.id) (hne : c ≠ d)
    (T : IntertwiningMap ρ τ) : T.toLinearMap = 0 := by
  ext v
  have h := LinearMap.congr_fun (T.isIntertwining' z) v
  have he : c • T v = d • T v := by
    simpa [hc, hd] using h
  have hzero : (c - d) • T v = 0 := by
    rw [sub_smul, he, sub_self]
  exact (smul_eq_zero.mp hzero).resolve_left (sub_ne_zero.mpr hne)

/-- The scalar distinction applies directly to actual induced representations. -/
theorem ind_intertwiner_eq_zero
    (H : Subgroup G) (σ : Representation k H V) (τ : Representation k H W)
    (z : H) (hz : ∀ g : G, Commute (z : G) g) (c d : k)
    (hc : σ z = c • LinearMap.id) (hd : τ z = d • LinearMap.id)
    (hne : c ≠ d)
    (T : IntertwiningMap (ind H.subtype σ) (ind H.subtype τ)) :
    T.toLinearMap = 0 :=
  intertwiner_eq_zero_of_scalar_ne _ _ (z : G) c d
    (ind_central_scalar H σ z hz c hc)
    (ind_central_scalar H τ z hz d hd) hne T

end PaperXI.CentralCharacterInduction
