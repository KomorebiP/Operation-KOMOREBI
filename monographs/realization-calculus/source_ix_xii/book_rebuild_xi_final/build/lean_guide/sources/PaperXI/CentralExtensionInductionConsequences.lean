import PaperXI.CentralExtensionInducing
import PaperXI.CentralCharacterInduction

/-!
# Actual induced candidates with prescribed central scalar

The central extension constructs nonzero smooth induced representations with
an arbitrary unit scalar on the adjoined central element.  Different scalars
give no nonzero ambient intertwiner.  These statements do not assert that the
induced representations are irreducible, admissible, or realizations of a
specified supercuspidal parameter.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtensionInductionConsequences

open Representation CentralExtensionInducing

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]

/-- The actual induced action, with its literal Mathlib coinvariant module. -/
def inducedRepresentation (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c : kˣ) :
    Representation k G (IndV (extendedSubgroup J z hz).subtype
      (extendedRepresentation J z hz hfree σ c)) :=
  ind (extendedSubgroup J z hz).subtype (extendedRepresentation J z hz hfree σ c)

/-- The prescribed scalar survives genuine induction to the ambient group. -/
theorem induced_central_scalar (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c : kˣ) :
    inducedRepresentation J z hz hfree σ c z = (c : k) • LinearMap.id :=
  CentralCharacterInduction.ind_central_scalar (extendedSubgroup J z hz)
    (extendedRepresentation J z hz hfree σ c) (centralElement J z hz) hz c
    (extendedRepresentation_central J z hz hfree σ c)

/-- The construction retains nonzero vectors; no finite-index premise is needed. -/
theorem induced_nontrivial (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c : kˣ) [Nontrivial V] :
    Nontrivial (IndV (extendedSubgroup J z hz).subtype
      (extendedRepresentation J z hz hfree σ c)) :=
  OpenSubgroupSmoothInduction.ind_nontrivial _ _

/-- Unequal chosen central scalars preclude every nonzero ambient intertwiner. -/
theorem induced_intertwiner_eq_zero (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c d : kˣ) (hne : c ≠ d)
    (T : IntertwiningMap (inducedRepresentation J z hz hfree σ c)
      (inducedRepresentation J z hz hfree σ d)) : T.toLinearMap = 0 :=
  CentralCharacterInduction.intertwiner_eq_zero_of_scalar_ne _ _ z (c : k) (d : k)
    (induced_central_scalar J z hz hfree σ c)
    (induced_central_scalar J z hz hfree σ d)
    (fun h => hne (Units.ext h)) T

/-- Consequently the nonzero induced candidates for different scalars are inequivalent. -/
theorem induced_not_equiv (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c d : kˣ) (hne : c ≠ d) [Nontrivial V] :
    ¬ Nonempty (Representation.Equiv (inducedRepresentation J z hz hfree σ c)
      (inducedRepresentation J z hz hfree σ d)) := by
  rintro ⟨e⟩
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  let w := IndV.mk (extendedSubgroup J z hz).subtype
    (extendedRepresentation J z hz hfree σ c) 1 v
  have hw : w ≠ 0 := OpenSubgroupSmoothInduction.mk_ne_zero _ _ 1 hv
  have he := induced_intertwiner_eq_zero J z hz hfree σ c d hne e.toIntertwiningMap
  have hew : e.toLinearEquiv w = e.toLinearEquiv 0 := by
    change e.toIntertwiningMap.toLinearMap w = e.toIntertwiningMap.toLinearMap 0
    rw [he]
    rfl
  exact hw (e.toLinearEquiv.injective hew)

section Topology
variable [TopologicalSpace G] [IsTopologicalGroup G]

/-- Smooth inducing data on an open subgroup yield a smooth actual induced candidate. -/
theorem induced_isSmooth (J : Subgroup G) (z : G)
    (hz : ∀ g : G, Commute z g)
    (hfree : ∀ n : ℤ, z ^ n ∈ J → n = 0)
    (σ : Representation k J V) (c : kˣ)
    (hJ : IsOpen (J : Set G)) (hσ : SmoothDegreeQuotient.IsSmooth σ) :
    SmoothDegreeQuotient.IsSmooth (inducedRepresentation J z hz hfree σ c) :=
  OpenSubgroupSmoothInduction.ind_isSmooth _ _
    (extendedSubgroup_isOpen J z hz hJ)
    (extendedRepresentation_smooth J z hz hfree σ c hJ hσ)

end Topology
end PaperXI.CentralExtensionInductionConsequences
