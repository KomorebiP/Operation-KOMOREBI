import PaperXI.InductionIrreducibility
import PaperXI.NormalizerExtensionInducing58
import PaperXI.MonomialInduction

/-!
# Actual intersection intertwining at a normalizer

The intertwining locus is defined by nonzero maps on the literal intersection
subgroup. At a normalizing element such a map is a whole-subgroup intertwiner.
An inclusion of the actual character intertwining locus in that of a prescribed
representation supplies the required map, without a determinant or residue-size
condition. The inclusion is an input; no simple-character theorem is asserted.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.NormalizerIntertwining60

open Representation InductionIrreducibility NormalizerExtensionInducing58

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]

/-- Intertwining on the actual subgroup intersection, with its actual conjugation. -/
def IntertwinedAt (J : Subgroup G) (κ : Representation k J V) (g : G) : Prop :=
  ∃ T : IntertwiningMap (κ.comp (intersectionSubgroup J g).subtype)
      (κ.comp (intersectionConjugation J g)), T ≠ 0

variable (J : Subgroup G) (κ : Representation k J V) (t : G)
  (ht : t ∈ Subgroup.normalizer (J : Set G))

/-- Normalization makes every subgroup element belong to the intersection. -/
def intersectionInclusion : J →* intersectionSubgroup J t where
  toFun j := ⟨j, (conjugation J t ht j).property⟩
  map_one' := rfl
  map_mul' _ _ := rfl

/-- The same linear operator now intertwines on the whole original subgroup. -/
def normalizerIntertwiner
    (T : IntertwiningMap (κ.comp (intersectionSubgroup J t).subtype)
      (κ.comp (intersectionConjugation J t))) :
    IntertwiningMap κ (κ.comp (conjugation J t ht).toMonoidHom) where
  toLinearMap := T.toLinearMap
  isIntertwining' j := T.isIntertwining' (intersectionInclusion J t ht j)

@[simp] theorem normalizerIntertwiner_apply
    (T : IntertwiningMap (κ.comp (intersectionSubgroup J t).subtype)
      (κ.comp (intersectionConjugation J t))) (v : V) :
    normalizerIntertwiner J κ t ht T v = T v := rfl

theorem normalizerIntertwiner_ne_zero
    (T : IntertwiningMap (κ.comp (intersectionSubgroup J t).subtype)
      (κ.comp (intersectionConjugation J t))) (hT : T ≠ 0) :
    normalizerIntertwiner J κ t ht T ≠ 0 := by
  intro hz
  apply hT
  ext v
  exact congrArg (fun A : IntertwiningMap κ
    (κ.comp (conjugation J t ht).toMonoidHom) => A v) hz

/-- Existential intertwining data gives a genuine normalizer map, not a scalar label. -/
theorem exists_normalizerIntertwiner (h : IntertwinedAt J κ t) :
    ∃ T : IntertwiningMap κ (κ.comp (conjugation J t ht).toMonoidHom), T ≠ 0 := by
  obtain ⟨T, hT⟩ := h
  exact ⟨normalizerIntertwiner J κ t ht T,
    normalizerIntertwiner_ne_zero J κ t ht T hT⟩

/-- Irreducibility turns this actual nonzero normalizer map into an equivalence. -/
theorem exists_normalizerEquiv [IsIrreducible κ] (h : IntertwinedAt J κ t) :
    Nonempty (Representation.Equiv κ (κ.comp (conjugation J t ht).toMonoidHom)) := by
  obtain ⟨T, hT⟩ := exists_normalizerIntertwiner J κ t ht h
  exact ⟨T.ofBijective (intertwiner_bijective J t ht κ T hT)⟩

section Character
variable (H : Subgroup G) (θ : H →* ℂˣ)

/-- Covariance of a character on the actual intersection supplies the identity map. -/
theorem character_intertwinedAt
    (hθ : ∀ h : intersectionSubgroup H t,
      θ (h : H) = θ (intersectionConjugation H t h)) :
    IntertwinedAt H (MonomialInduction.scalarRepresentation θ) t := by
  let T : IntertwiningMap
      ((MonomialInduction.scalarRepresentation θ).comp (intersectionSubgroup H t).subtype)
      ((MonomialInduction.scalarRepresentation θ).comp (intersectionConjugation H t)) :=
    { toLinearMap := LinearMap.id
      isIntertwining' := fun h => by
        apply LinearMap.ext
        intro z
        change (θ (h : H) : ℂ) * z = (θ (intersectionConjugation H t h) : ℂ) * z
        rw [hθ h] }
  refine ⟨T, ?_⟩
  intro hz
  have he := congrArg (fun A => (A : IntertwiningMap
    ((MonomialInduction.scalarRepresentation θ).comp (intersectionSubgroup H t).subtype)
    ((MonomialInduction.scalarRepresentation θ).comp (intersectionConjugation H t))) 1) hz
  exact one_ne_zero he

variable {W : Type*} [AddCommGroup W] [Module ℂ W]
variable (κc : Representation ℂ J W)

/-- The actual intertwining-locus property of a supplied extension gives its
normalizer operator from character covariance. There is no q>2 restriction. -/
theorem exists_normalizerIntertwiner_of_character
    (hβ : ∀ g : G, IntertwinedAt H (MonomialInduction.scalarRepresentation θ) g →
      IntertwinedAt J κc g)
    (hθ : ∀ h : intersectionSubgroup H t,
      θ (h : H) = θ (intersectionConjugation H t h)) :
    ∃ T : IntertwiningMap κc (κc.comp (conjugation J t ht).toMonoidHom), T ≠ 0 :=
  exists_normalizerIntertwiner J κc t ht
    (hβ t (character_intertwinedAt t H θ hθ))

end Character
end PaperXI.NormalizerIntertwining60
