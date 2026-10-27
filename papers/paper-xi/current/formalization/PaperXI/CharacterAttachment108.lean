import PaperXI.TypeSideDescent
import PaperXI.CharacterNormalizer61
import PaperXI.RepresentationStability
import PaperXI.IntertwiningAlong105

/-! Attach the actual character to the prescribed carrier. A single character
vector and character normalization imply scalar action, by irreducibility. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterAttachment108
open Representation IntertwiningAlong105
variable {G K W : Type*} [Group G] [Group K] [AddCommGroup W] [Module ℂ W]

theorem irreducible_of_restriction (N : Subgroup K) (κ : Representation ℂ K W)
    [IsIrreducible (κ.comp N.subtype)] : IsIrreducible κ := by
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space (κ.comp N.subtype)
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  exact RepresentationStability.eq_bot_or_top (κ.comp N.subtype) S
    (fun n w hw => hS n w hw)

/-- Original subgroup and character, carried into the prescribed compact group. -/
def insideCharacter (D J : Subgroup G) (hDJ : D ≤ J) (θ : D →* ℂˣ) :
    D.subgroupOf J →* ℂˣ :=
  θ.comp (Subgroup.subgroupOfEquivOfLe hDJ).toMonoidHom

theorem scalar_of_contains (D J : Subgroup G) (hDJ : D ≤ J) (θ : D →* ℂˣ)
    (hJ : J ≤ CharacterNormalizer61.normalizer D θ)
    (κ : Representation ℂ J W) [IsIrreducible κ]
    (hv : ∃ v : W, v ≠ 0 ∧ ∀ d : D, κ (Subgroup.inclusion hDJ d) v = (θ d : ℂ) • v)
    (d : D) : κ (Subgroup.inclusion hDJ d) = (θ d : ℂ) • LinearMap.id := by
  let : (D.subgroupOf J).Normal :=
    Subgroup.normal_subgroupOf_of_le_normalizer
      (hJ.trans (CharacterNormalizer61.normalizes_domain D θ))
  have hi : TypeSideDescent.Invariant (D.subgroupOf J) (insideCharacter D J hDJ θ) := by
    intro j x
    exact CharacterNormalizer61.character_covariance D θ (hJ j.property)
      ((Subgroup.subgroupOfEquivOfLe hDJ) x)
      ((Subgroup.subgroupOfEquivOfLe hDJ) (TypeSideDescent.conjugate (D.subgroupOf J) j x)) rfl
  have hc : TypeSideDescent.Contains (D.subgroupOf J) (insideCharacter D J hDJ θ) κ := by
    obtain ⟨v, hn, hv⟩ := hv
    refine ⟨v, hn, ?_⟩
    intro x
    exact hv ((Subgroup.subgroupOfEquivOfLe hDJ) x)
  exact TypeSideDescent.scalar_restriction (D.subgroupOf J) (insideCharacter D J hDJ θ)
    hi κ hc ⟨Subgroup.inclusion hDJ d, d.property⟩

/-- Nonzero intertwining of a representation with scalar character restriction
forces equality of the original character on its literal intersection. -/
theorem character_of_scalar (ι : K →* G) (ρ : Representation ℂ K W)
    (D : Subgroup G) (θ : D →* ℂˣ) (j : D →* K)
    (hj : ∀ d : D, ι (j d) = (d : G))
    (hscalar : ∀ d : D, ρ (j d) = (θ d : ℂ) • LinearMap.id)
    (g : G) (hg : ExistsAt ι ρ g) :
    NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g := by
  obtain ⟨T, hn, ht⟩ := hg
  obtain ⟨w, hw⟩ : ∃ w : W, T w ≠ 0 := by
    by_contra h
    push Not at h
    exact hn (LinearMap.ext h)
  apply NormalizerIntertwining60.character_intertwinedAt
  intro x
  let y := InductionIrreducibility.intersectionConjugation D g x
  have he : ι (j y) = g * ι (j (x : D)) * g⁻¹ := by
    rw [hj, hj]
    rfl
  have h := ht (j (x : D)) (j y) he w
  rw [hscalar, hscalar] at h
  simp only [LinearMap.smul_apply, LinearMap.id_apply, map_smul] at h
  apply Units.ext
  exact (smul_left_injective ℂ hw) h

end PaperXI.CharacterAttachment108
