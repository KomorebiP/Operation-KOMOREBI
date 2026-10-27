import PaperXI.CharacterAttachment108
import PaperXI.FullTypeIntertwining105
import PaperXI.IntertwiningSpace107

/-! Equality of actual intertwining supports after character attachment. The
centralizer beta-intertwining input follows from positive Heisenberg dimension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterSupport108
open Representation IntertwiningAlong105 CharacterAttachment108
variable {G W : Type*} [Group G] [AddCommGroup W] [Module ℂ W]
  (D J : Subgroup G) (hDJ : D ≤ J) (N : Subgroup J)
  (hDN : ∀ d : D, Subgroup.inclusion hDJ d ∈ N)
  (θ : D →* ℂˣ) (κ : Representation ℂ J W)

def intoFirst : D →* N := (Subgroup.inclusion hDJ).codRestrict N hDN

variable (hscalar : ∀ d : D, κ (Subgroup.inclusion hDJ d) = (θ d : ℂ) • LinearMap.id)
  (hβ : ∀ g : G,
    NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
    NormalizerIntertwining60.IntertwinedAt J κ g)

include hscalar hβ hDN in
/-- The reverse inclusion uses the retained beta-extension implication. This is
support equality, not an assertion that the two Hom spaces have equal dimension. -/
theorem restricted_iff_character (g : G) :
    ExistsAt (J.subtype.comp N.subtype) (κ.comp N.subtype) g ↔
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g := by
  constructor
  · exact character_of_scalar (J.subtype.comp N.subtype) (κ.comp N.subtype)
      D θ (intoFirst D J hDJ N hDN) (fun _ => rfl) hscalar g
  · intro hg
    obtain ⟨T, hn, ht⟩ := (FullTypeIntertwining105.existsAt_iff_locus J κ g).mpr (hβ g hg)
    exact ⟨T, hn, fun x y he w => ht x y he w⟩

omit N hDN in
include hscalar hβ in
theorem full_iff_character (g : G) :
    ExistsAt J.subtype κ g ↔
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g := by
  constructor
  · exact character_of_scalar J.subtype κ D θ (Subgroup.inclusion hDJ)
      (fun _ => rfl) hscalar g
  · intro hg
    exact (FullTypeIntertwining105.existsAt_iff_locus J κ g).mpr (hβ g hg)

include hscalar hβ hDN in
theorem full_iff_restricted (g : G) :
    ExistsAt J.subtype κ g ↔ ExistsAt (J.subtype.comp N.subtype) (κ.comp N.subtype) g :=
  (full_iff_character D J hDJ θ κ hscalar hβ g).trans
    (restricted_iff_character D J hDJ N hDN θ κ hscalar hβ g).symm

/-- Positive dimension of the actual Hom space gives a nonzero operator. -/
theorem existsAt_of_dimension_pos {K : Type*} [Group K] (ι : K →* G)
    (ρ : Representation ℂ K W) (g : G)
    (hd : 0 < Module.finrank ℂ (IntertwiningSpace107.space ι ρ g)) : ExistsAt ι ρ g := by
  let : Nontrivial (IntertwiningSpace107.space ι ρ g) := Module.nontrivial_of_finrank_pos hd
  obtain ⟨S, hn⟩ := exists_ne (0 : IntertwiningSpace107.space ι ρ g)
  exact ⟨S, fun h => hn (Subtype.ext h), S.property⟩

include hscalar hβ hDN in
/-- No separate centralizer beta-intertwiner is required once the character is
attached and the Heisenberg intersection dimension is positive. -/
theorem beta_of_dimension_pos (g : G)
    (hd : 0 < Module.finrank ℂ
      (IntertwiningSpace107.space (J.subtype.comp N.subtype) (κ.comp N.subtype) g)) :
    ExistsAt J.subtype κ g :=
  (full_iff_restricted D J hDJ N hDN θ κ hscalar hβ g).mpr
    (existsAt_of_dimension_pos (J.subtype.comp N.subtype) (κ.comp N.subtype) g hd)

end PaperXI.CharacterSupport108
