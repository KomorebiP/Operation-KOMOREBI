import PaperXI.ElementaryEnvelope

/-! The actual alternating prime-field form on the commutator radical quotient.
The logarithm equivalence is explicit: the standard character supplies one,
and all alternative choices have a proved scalar comparison. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ElementaryEnvelope
open CocycleCommutator

variable {A : Type*} [CommGroup A] {p : ℕ} [Fact p.Prime]
variable (c : Cocycle A ℂˣ) [Fact (∀ a : A, a ^ p = 1)]

/-- Apply the actual root logarithm in both additive quotient variables. -/
def logarithmicPairing (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    Space c →+ (Space c →+ ZMod p) where
  toFun x := e.symm.toAddMonoidHom.comp (rootPairing c Fact.out x.toMul).toAdditive
  map_zero' := by
    apply AddMonoidHom.ext
    intro y
    change e.symm (Additive.ofMul (rootPairing c Fact.out 1 y.toMul)) = 0
    have h : rootPairing c Fact.out 1 y.toMul = 1 :=
      congrArg (fun f : (A ⧸ radical c) →* rootsOfUnity p ℂ => f y.toMul)
        (map_one (rootPairing c Fact.out))
    rw [h]
    exact map_zero e.symm
  map_add' x y := by
    apply AddMonoidHom.ext
    intro z
    change e.symm (Additive.ofMul (rootPairing c Fact.out (x.toMul * y.toMul) z.toMul)) = _
    have h := congrArg (fun f : (A ⧸ radical c) →* rootsOfUnity p ℂ => f z.toMul)
      (map_mul (rootPairing c Fact.out) x.toMul y.toMul)
    rw [h]
    exact map_add e.symm _ _

/-- Any chosen identification Fp ≃ μp gives a bilinear form, by construction. -/
def formWith (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    LinearMap.BilinForm (ZMod p) (Space c) :=
  ((AddMonoidHom.toZModLinearMapEquiv p).toAddMonoidHom.comp
    (logarithmicPairing c e)).toZModLinearMap p

@[simp] theorem formWith_apply (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ))
    (x y : Space c) : formWith c e x y =
      e.symm (Additive.ofMul (rootPairing c Fact.out x.toMul y.toMul)) := rfl

/-- Exponentiating the form recovers the original quotient commutator. -/
theorem formWith_character (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ))
    (x y : Space c) :
    ((e (formWith c e x y)).toMul : ℂˣ) = quotientPairing c x.toMul y.toMul := by
  rw [formWith_apply, e.apply_symm_apply]
  rfl

/-- Both scalar laws are those of the actual constructed bilinear map. -/
theorem formWith_smul_left (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ))
    (r : ZMod p) (x y : Space c) :
    formWith c e (r • x) y = r * formWith c e x y := by
  exact LinearMap.BilinForm.smul_left _ _ _

theorem formWith_smul_right (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ))
    (r : ZMod p) (x y : Space c) :
    formWith c e x (r • y) = r * formWith c e x y := by
  exact LinearMap.BilinForm.smul_right _ _ _

theorem formWith_isAlt (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    (formWith c e).IsAlt := by
  intro x
  rw [formWith_apply]
  have h : rootPairing (p := p) c Fact.out x.toMul x.toMul = 1 :=
    Subtype.ext (quotientPairing_self c x.toMul)
  rw [h]
  exact map_zero e.symm

theorem formWith_eq_zero_iff (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ))
    (x y : Space c) :
    formWith c e x y = 0 ↔ quotientPairing c x.toMul y.toMul = 1 := by
  rw [formWith_apply, e.symm.map_eq_zero_iff]
  change rootPairing c Fact.out x.toMul y.toMul = 1 ↔ _
  exact Subtype.ext_iff

theorem formWith_nondegenerate (e : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    (formWith c e).Nondegenerate := by
  constructor
  · intro x hx
    have h : x.toMul = 1 := (quotientPairing_nondegenerate_left c x.toMul).mp
      (fun y => (formWith_eq_zero_iff c e x (Additive.ofMul y)).mp (hx (Additive.ofMul y)))
    exact congrArg Additive.ofMul h
  · intro y hy
    have h : y.toMul = 1 := (quotientPairing_nondegenerate_right c y.toMul).mp
      (fun x => (formWith_eq_zero_iff c e (Additive.ofMul x) y).mp (hy (Additive.ofMul x)))
    exact congrArg Additive.ofMul h

/-- The form for the fixed standard additive character. -/
def form : LinearMap.BilinForm (ZMod p) (Space c) := formWith c (rootEquiv p)

theorem form_isAlt : (form (p := p) c).IsAlt := formWith_isAlt c (rootEquiv p)

theorem form_nondegenerate : (form (p := p) c).Nondegenerate :=
  formWith_nondegenerate c (rootEquiv p)

/-- The standard character/logarithm roundtrip lands in the literal scalar pairing. -/
theorem form_stdAddChar (x y : Space c) :
    ZMod.stdAddChar (form (p := p) c x y) =
      (quotientPairing c x.toMul y.toMul : ℂ) := by
  rw [← rootEquiv_coe]
  exact congrArg Units.val (formWith_character c (rootEquiv p) x y)

/-- Changing the identification of μp changes the field coordinate by this
nonzero scalar, rather than giving an identical form. -/
theorem choice_scalar_ne_zero
    (e e' : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    (e.trans e'.symm) 1 ≠ 0 := by
  intro h
  exact one_ne_zero ((e.trans e'.symm).injective (h.trans (map_zero _).symm))

theorem choice_map_eq_mul
    (e e' : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) (t : ZMod p) :
    (e.trans e'.symm) t = (e.trans e'.symm) 1 * t := by
  let L := (e.trans e'.symm).toAddMonoidHom.toZModLinearMap p
  have h := L.map_smul t (1 : ZMod p)
  change (e.trans e'.symm) (t * 1) = t * (e.trans e'.symm) 1 at h
  simpa only [mul_one, mul_comm] using h

/-- Exact choice comparison, with scalar determined by the two characters. -/
theorem formWith_choice
    (e e' : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) (x y : Space c) :
    formWith c e' x y = (e.trans e'.symm) 1 * formWith c e x y := by
  rw [← choice_map_eq_mul e e']
  simp only [formWith_apply, AddEquiv.trans_apply, e.apply_symm_apply]

/-- Any two primitive character choices produce a nonzero scalar multiple. -/
theorem exists_choice_scalar
    (e e' : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) :
    ∃ u : (ZMod p)ˣ, ∀ x y : Space c,
      formWith c e' x y = (u : ZMod p) * formWith c e x y := by
  exact ⟨Units.mk0 _ (choice_scalar_ne_zero e e'), formWith_choice c e e'⟩

end PaperXI.ElementaryEnvelope
