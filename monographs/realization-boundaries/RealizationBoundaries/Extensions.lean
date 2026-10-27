import RealizationBoundaries.Preimages

/-! # Exact rational quotients and nonsplitting inside the actual ambient product -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Any homomorphism from a divisible additive group into the prime product is zero.
No linearity or continuity of the homomorphism is assumed. -/
theorem hom_zero_of_divisible (E : Type*) [AddGroup E]
    (hdiv : ∀ m : ℕ, 0 < m → ∀ x : E, ∃ y : E, m • y = x)
    (f : E →+ Ambient) : f = 0 := by
  ext x p
  obtain ⟨y, hy⟩ := hdiv p.val p.property.pos x
  rw [← hy, map_nsmul]
  change (p.val • f y) p = 0
  rw [coordinate_nsmul]
  simp

/-- The ambient product has no embedded nonzero divisible group. -/
theorem not_injective_hom_of_divisible (E : Type*) [AddGroup E] [Nontrivial E]
    (hdiv : ∀ m : ℕ, 0 < m → ∀ x : E, ∃ y : E, m • y = x)
    (f : E →+ Ambient) : ¬ Function.Injective f := by
  intro hf
  have hzero := hom_zero_of_divisible E hdiv f
  obtain ⟨x, hx⟩ := exists_ne (0 : E)
  apply hx
  apply hf
  simp [hzero]

theorem rational_hom_zero (E : Type*) [AddCommGroup E] [Module ℚ E]
    (f : E →+ Ambient) : f = 0 := by
  apply hom_zero_of_divisible E _ f
  intro m hm x
  refine ⟨(m : ℚ)⁻¹ • x, ?_⟩
  rw [← Nat.cast_smul_eq_nsmul ℚ, smul_smul]
  simp [Nat.ne_of_gt hm]

/-- Restriction of the actual quotient map to the selected rational subspace. -/
def preimageProjection (W : Submodule ℚ TailSpace) : preimage W →+ W where
  toFun x := ⟨quotientMap x.val, x.property⟩
  map_zero' := Subtype.ext (map_zero quotientMap)
  map_add' x y := Subtype.ext (map_add quotientMap x.val y.val)

theorem preimageProjection_surjective (W : Submodule ℚ TailSpace) :
    Function.Surjective (preimageProjection W) := by
  intro w
  obtain ⟨x, hx⟩ := quotientMap_surjective w.val
  refine ⟨⟨x, ?_⟩, Subtype.ext hx⟩
  change quotientMap x ∈ W
  rw [hx]
  exact w.property

/-- The finite-support kernel, as a subgroup of the original preimage group. -/
def finiteKernel (W : Submodule ℚ TailSpace) : AddSubgroup (preimage W) :=
  finiteSupport.comap (preimage W).subtype

theorem preimageProjection_ker (W : Submodule ℚ TailSpace) :
    (preimageProjection W).ker = finiteKernel W := by
  ext x
  change (⟨quotientMap x.val, x.property⟩ : W) = 0 ↔ x.val ∈ finiteSupport
  rw [Subtype.ext_iff]
  exact quotientMap_eq_zero_iff x.val

/-- The quotient by the actual finite-support subgroup is the selected rational subspace. -/
def preimageQuotientEquiv (W : Submodule ℚ TailSpace) :
    (preimage W ⧸ finiteKernel W) ≃+ W :=
  (QuotientAddGroup.quotientAddEquivOfEq (preimageProjection_ker W).symm).trans
    (QuotientAddGroup.quotientKerEquivOfSurjective (preimageProjection W)
      (preimageProjection_surjective W))

/-- No homomorphic section exists when the rational quotient contains a nonzero point. -/
theorem no_section (W : Submodule ℚ TailSpace) (w : W) (hw : w ≠ 0)
    (s : W →+ preimage W) : (preimageProjection W).comp s ≠ AddMonoidHom.id W := by
  intro hs
  have hz : (preimage W).subtype.comp s = 0 :=
    rational_hom_zero W ((preimage W).subtype.comp s)
  have hsw : s w = 0 := by
    apply Subtype.ext
    exact DFunLike.congr_fun hz w
  have h := DFunLike.congr_fun hs w
  apply hw
  simpa [hsw] using h.symm

/-- A nonsplitting statement with no selected witness in its public hypotheses. -/
theorem no_section_of_nontrivial (W : Submodule ℚ TailSpace) [Nontrivial W] :
    ¬ ∃ s : W →+ preimage W, (preimageProjection W).comp s = AddMonoidHom.id W := by
  obtain ⟨w, hw⟩ := exists_ne (0 : W)
  rintro ⟨s, hs⟩
  exact no_section W w hw s hs

end RealizationBoundaries
