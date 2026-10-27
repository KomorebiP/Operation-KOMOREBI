import RealizationBoundaries.EndomorphismScalars

/-!
# Inverses and automorphisms of the original groups

An everywhere nonzero diagonal is invertible on the product. For a source with
an infinite selector, its inverse also preserves the appropriate original
rational-line preimages. This last step is proved; product invertibility alone
is not silently identified with invertibility on an arbitrary subspace.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

def inverseDiagonal (c : Ambient) : Ambient := fun p => (c p)⁻¹

@[simp] theorem inverseDiagonal_apply (c : Ambient) (p : Prime) :
    inverseDiagonal c p = (c p)⁻¹ := rfl

theorem diagonal_inverse_left (c : Ambient) (hc : ∀ p, c p ≠ 0) (x : Ambient) :
    diagonal (inverseDiagonal c) (diagonal c x) = x := by
  funext p
  exact inv_mul_cancel_left₀ (hc p) (x p)

theorem diagonal_inverse_right (c : Ambient) (hc : ∀ p, c p ≠ 0) (x : Ambient) :
    diagonal c (diagonal (inverseDiagonal c) x) = x := by
  funext p
  exact mul_inv_cancel_left₀ (hc p) (x p)

/-- A topological additive equivalence on the actual infinite product. -/
def diagonalAmbientEquiv (c : Ambient) (hc : ∀ p, c p ≠ 0) : Ambient ≃ₜ+ Ambient where
  toFun := diagonal c
  invFun := diagonal (inverseDiagonal c)
  left_inv := diagonal_inverse_left c hc
  right_inv := diagonal_inverse_right c hc
  map_add' := map_add (diagonal c)
  continuous_toFun := diagonal_continuous c
  continuous_invFun := diagonal_continuous (inverseDiagonal c)

theorem diagonalTail_inverse_left (c : Ambient) (hc : ∀ p, c p ≠ 0) (v : TailSpace) :
    diagonalTail (inverseDiagonal c) (diagonalTail c v) = v := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  simp only [diagonalTail_quotient, diagonal_inverse_left c hc]

theorem diagonalTail_inverse_right (c : Ambient) (hc : ∀ p, c p ≠ 0) (v : TailSpace) :
    diagonalTail c (diagonalTail (inverseDiagonal c) v) = v := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  simp only [diagonalTail_quotient, diagonal_inverse_right c hc]

/-- A zero coordinate of the diagonal kills an actual nonzero prime seed. -/
theorem hom_injective_iff_diagonal_nonzero (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) :
    Function.Injective f ↔ ∀ p, homDiagonal U V f p ≠ 0 := by
  constructor
  · intro hf p hp
    have hz : f (preimageSeed U p) = 0 := by
      apply Subtype.ext
      funext q
      rw [hom_coordinate_formula U V f]
      by_cases hq : q = p
      · subst q
        simp [hp]
      · classical
        simp [preimageSeed, primeSeed, cut, hq]
    have he : preimageSeed U p = 0 := hf (hz.trans (map_zero f).symm)
    have he' := congrArg (fun x : preimage U => x.val p) he
    simp at he'
  · intro hc x y hxy
    apply Subtype.ext
    funext p
    have he := congrArg (fun z : preimage V => z.val p) hxy
    rw [hom_coordinate_formula U V f, hom_coordinate_formula U V f] at he
    exact mul_left_cancel₀ (hc p) he

/-- Surjectivity also forces every diagonal coefficient to be nonzero. -/
theorem hom_surjective_diagonal_nonzero (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (hf : Function.Surjective f) :
    ∀ p, homDiagonal U V f p ≠ 0 := by
  intro p hp
  obtain ⟨x, hx⟩ := hf (preimageSeed V p)
  have he := congrArg (fun z : preimage V => z.val p) hx
  rw [hom_coordinate_formula U V f, hp, zero_mul, preimageSeed_apply] at he
  exact zero_ne_one he

/-- Nonzero coordinate scalars cannot annihilate the source's nonzero rational line. -/
theorem diagonalSlope_ne_zero (S T : Set Prime) (hS : S.Infinite) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c)
    (hn : ∀ p, c p ≠ 0) : diagonalSlope S T c hc ≠ 0 := by
  intro hz
  have hs := diagonalSlope_spec S T c hc
  rw [hz, zero_smul] at hs
  have hi := congrArg (diagonalTail (inverseDiagonal c)) hs
  rw [diagonalTail_inverse_left c hn, map_zero] at hi
  exact indicator_tail_ne_zero hS hi

/-- The inverse multiplier maps the target line back to the source line.
The nonzero slope and the inverse line equation are derived explicitly. -/
theorem inverseDiagonal_admissible (S T : Set Prime) (hS : S.Infinite) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c)
    (hn : ∀ p, c p ≠ 0) :
    DiagonalAdmissible (selectorLine T) (selectorLine S) (inverseDiagonal c) := by
  let r := diagonalSlope S T c hc
  have hr : r ≠ 0 := diagonalSlope_ne_zero S T hS c hc hn
  have he : quotientMap (indicator S) =
      r • diagonalTail (inverseDiagonal c) (quotientMap (indicator T)) := by
    have h := congrArg (diagonalTail (inverseDiagonal c)) (diagonalSlope_spec S T c hc)
    rw [diagonalTail_inverse_left c hn, map_smul] at h
    exact h
  apply (diagonalAdmissible_selector_iff T S _).mpr
  apply (mem_selectorGroup_iff S _).mpr
  refine ⟨r⁻¹, ?_⟩
  rw [he, smul_smul, inv_mul_cancel₀ hr, one_smul]
  rfl

/-- Exact inverse on the original subgroups, not only on their completion. -/
def selectorEquivOfNonzeroDiagonal (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T)
    (hn : ∀ p, homDiagonal (selectorLine S) (selectorLine T) f p ≠ 0) :
    selectorGroup S ≃+ selectorGroup T where
  toFun := f
  invFun := diagonalRestriction (selectorLine T) (selectorLine S)
    (inverseDiagonal (homDiagonal (selectorLine S) (selectorLine T) f))
    (inverseDiagonal_admissible S T hS _ (homDiagonal_admissible _ _ f) hn)
  left_inv x := by
    apply Subtype.ext
    change diagonal (inverseDiagonal (homDiagonal (selectorLine S) (selectorLine T) f))
      (f x).val = x.val
    exact (congrArg (diagonal (inverseDiagonal
      (homDiagonal (selectorLine S) (selectorLine T) f)))
      (hom_eq_diagonal (selectorLine S) (selectorLine T) f x)).trans
        (diagonal_inverse_left _ hn x.val)
  right_inv y := by
    apply Subtype.ext
    exact (hom_eq_diagonal (selectorLine S) (selectorLine T) f _).trans
      (diagonal_inverse_right _ hn y.val)
  map_add' := map_add f

@[simp] theorem selectorEquivOfNonzeroDiagonal_apply (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T)
    (hn : ∀ p, homDiagonal (selectorLine S) (selectorLine T) f p ≠ 0)
    (x : selectorGroup S) : selectorEquivOfNonzeroDiagonal S T hS f hn x = f x := rfl

/-- The inverse formula is the reciprocal diagonal at every prime, with no tail exceptions. -/
theorem selectorEquiv_inverse_coordinate (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T)
    (hn : ∀ p, homDiagonal (selectorLine S) (selectorLine T) f p ≠ 0)
    (y : selectorGroup T) (p : Prime) :
    ((selectorEquivOfNonzeroDiagonal S T hS f hn).symm y).val p =
      (homDiagonal (selectorLine S) (selectorLine T) f p)⁻¹ * y.val p := rfl

/-- The rank-one line argument is essential to this converse. -/
theorem selector_hom_bijective_iff (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T) :
    Function.Bijective f ↔ ∀ p, homDiagonal (selectorLine S) (selectorLine T) f p ≠ 0 := by
  constructor
  · intro hf
    exact (hom_injective_iff_diagonal_nonzero _ _ f).mp hf.1
  · intro hn
    exact (selectorEquivOfNonzeroDiagonal S T hS f hn).bijective

/-- In this rank-one family an injective supplied map is automatically an isomorphism. -/
theorem selector_hom_injective_iff_bijective (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T) :
    Function.Injective f ↔ Function.Bijective f := by
  rw [selector_hom_bijective_iff S T hS]
  exact hom_injective_iff_diagonal_nonzero _ _ f

theorem selector_hom_surjective_iff_bijective (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T) :
    Function.Surjective f ↔ Function.Bijective f := by
  constructor
  · intro hf
    exact (selector_hom_bijective_iff S T hS f).mpr
      (hom_surjective_diagonal_nonzero _ _ f hf)
  · exact fun hf => hf.2

/-- Corollary 7.8, including the existence of an actual additive automorphism. -/
theorem selector_endomorphism_automorphism_iff (S : Set Prime) (hS : S.Infinite)
    (f : AddMonoid.End (selectorGroup S)) :
    (∃ e : selectorGroup S ≃+ selectorGroup S, e.toAddMonoidHom = f) ↔
      ∀ p, homDiagonal (selectorLine S) (selectorLine S) f p ≠ 0 := by
  constructor
  · rintro ⟨e, rfl⟩
    exact (hom_injective_iff_diagonal_nonzero _ _ _).mp e.injective
  · intro hn
    exact ⟨selectorEquivOfNonzeroDiagonal S S hS f hn, rfl⟩

end RealizationBoundaries
