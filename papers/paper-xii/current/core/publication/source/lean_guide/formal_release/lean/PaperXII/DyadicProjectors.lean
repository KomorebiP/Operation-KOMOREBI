import Mathlib.Algebra.MonoidAlgebra.Basic
import Mathlib.NumberTheory.Padics.PadicIntegers
import Mathlib.Tactic

set_option autoImplicit false

/-! Paper XII, Proposition 11.1: actual dyadic sign projectors. -/
namespace PaperXII.DyadicProjectors

abbrev G := Multiplicative (ZMod 2)

def g : G := Multiplicative.ofAdd 1

theorem g_ne_one : g ≠ 1 := by decide

theorem g_mul_g : g * g = 1 := by decide

theorem group_cases (h : G) : h = 1 ∨ h = g := by
  change h.toAdd = 0 ∨ h.toAdd = 1
  exact (by decide : ∀ a : ZMod 2, a = 0 ∨ a = 1) h.toAdd

section Field
variable {K : Type*} [Field K]

/-- The actual group-ring basis element corresponding to the nonidentity element. -/
noncomputable def generator : MonoidAlgebra K G := MonoidAlgebra.single g 1

/-- Every group algebra element has exactly its two actual group coefficients. -/
theorem two_coefficients (x : MonoidAlgebra K G) :
    x = MonoidAlgebra.single 1 (x.coeff 1) + MonoidAlgebra.single g (x.coeff g) := by
  ext h
  rcases group_cases h with rfl | rfl <;> simp [g_ne_one, Ne.symm g_ne_one]

/-- The positive sign idempotent, with coefficient 1/2 at each group element. -/
noncomputable def ePlus : MonoidAlgebra K G :=
  MonoidAlgebra.single 1 (1 / 2) + MonoidAlgebra.single g (1 / 2)

/-- The negative sign idempotent. -/
noncomputable def eMinus : MonoidAlgebra K G :=
  MonoidAlgebra.single 1 (1 / 2) + MonoidAlgebra.single g (-(1 / 2))

theorem ePlus_formula : ePlus (K := K) = (1 / 2 : K) • (1 + generator) := by
  simp [ePlus, generator, smul_add, MonoidAlgebra.smul_single, MonoidAlgebra.one_def]

theorem eMinus_formula : eMinus (K := K) = (1 / 2 : K) • (1 - generator) := by
  simp [eMinus, generator, MonoidAlgebra.smul_single, MonoidAlgebra.one_def,
    ← MonoidAlgebra.single_neg, sub_eq_add_neg]

/-- Evaluation at the two characters of the actual cyclic group of order two. -/
noncomputable def characterMap : MonoidAlgebra K G →+* K × K where
  toFun x := (x.coeff 1 + x.coeff g, x.coeff 1 - x.coeff g)
  map_one' := by simp [MonoidAlgebra.one_def, g_ne_one]
  map_zero' := by simp
  map_add' x y := by ext <;> simp <;> ring
  map_mul' x y := by
    rw [two_coefficients x, two_coefficients y]
    ext <;> simp [add_mul, mul_add, MonoidAlgebra.single_mul_single,
      g_mul_g, g_ne_one, Ne.symm g_ne_one] <;> ring

variable [CharZero K]

/-- The inverse two-character transform. -/
noncomputable def inverseCharacters (z : K × K) : MonoidAlgebra K G :=
  MonoidAlgebra.single 1 ((z.1 + z.2) / 2) +
    MonoidAlgebra.single g ((z.1 - z.2) / 2)

theorem characterMap_inverse (z : K × K) : characterMap (inverseCharacters z) = z := by
  ext <;> simp [characterMap, inverseCharacters, g_ne_one, Ne.symm g_ne_one] <;> ring

theorem inverse_characterMap (x : MonoidAlgebra K G) : inverseCharacters (characterMap x) = x := by
  rw [two_coefficients x]
  simp [characterMap, inverseCharacters, g_ne_one, Ne.symm g_ne_one]

/-- The two-character decomposition over any field of characteristic zero. -/
noncomputable def characterEquiv : MonoidAlgebra K G ≃+* K × K :=
  RingEquiv.ofBijective characterMap
    ⟨Function.HasLeftInverse.injective ⟨inverseCharacters, inverse_characterMap⟩,
      Function.HasRightInverse.surjective ⟨inverseCharacters, characterMap_inverse⟩⟩

theorem characters_ePlus : characterMap (ePlus (K := K)) = (1, 0) := by
  ext <;> simp [characterMap, ePlus, g_ne_one, Ne.symm g_ne_one]; ring

theorem characters_eMinus : characterMap (eMinus (K := K)) = (0, 1) := by
  ext <;> simp [characterMap, eMinus, g_ne_one, Ne.symm g_ne_one]; ring

/-- These are complementary, orthogonal idempotents in the actual group algebra. -/
theorem sign_projector_relations :
    ePlus (K := K) * ePlus = ePlus ∧ eMinus (K := K) * eMinus = eMinus ∧
    ePlus (K := K) * eMinus = 0 ∧ ePlus (K := K) + eMinus = 1 := by
  have inj := (characterEquiv (K := K)).injective
  change Function.Injective (characterMap (K := K)) at inj
  refine ⟨inj ?_, inj ?_, inj ?_, inj ?_⟩ <;>
    simp only [map_mul, map_add, map_zero, map_one, characters_ePlus, characters_eMinus] <;>
    ext <;> simp

/-- There are no other idempotents besides 0, 1 and the two sign projectors. -/
theorem idempotent_classification (x : MonoidAlgebra K G) :
    x * x = x ↔ x = 0 ∨ x = 1 ∨ x = ePlus ∨ x = eMinus := by
  constructor
  · intro hx
    have hfield (a : K) (ha : a * a = a) : a = 0 ∨ a = 1 := by
      have hz : a * (a - 1) = 0 := by rw [mul_sub, mul_one, ha, sub_self]
      exact (mul_eq_zero.mp hz).imp_right sub_eq_zero.mp
    have hy := congrArg characterMap hx
    rw [map_mul] at hy
    have h₁ := hfield (characterMap x).1 (congrArg Prod.fst hy)
    have h₂ := hfield (characterMap x).2 (congrArg Prod.snd hy)
    have inj := (characterEquiv (K := K)).injective
    change Function.Injective (characterMap (K := K)) at inj
    rcases h₁ with h₁ | h₁ <;> rcases h₂ with h₂ | h₂
    · left; apply inj; ext <;> simp [h₁, h₂]
    · right; right; right; apply inj; rw [characters_eMinus]; exact Prod.ext h₁ h₂
    · right; right; left; apply inj; rw [characters_ePlus]; exact Prod.ext h₁ h₂
    · right; left; apply inj; ext <;> simp [h₁, h₂]
  · rintro (rfl | rfl | rfl | rfl)
    · simp
    · simp
    · exact sign_projector_relations.1
    · exact sign_projector_relations.2.1

/-- The two nontrivial idempotents are nonzero. -/
theorem sign_projectors_nonzero : ePlus (K := K) ≠ 0 ∧ eMinus (K := K) ≠ 0 := by
  constructor
  · intro h
    have hh := congrArg characterMap h
    rw [characters_ePlus, map_zero] at hh
    have := congrArg Prod.fst hh
    exact one_ne_zero this
  · intro h
    have hh := congrArg characterMap h
    rw [characters_eMinus, map_zero] at hh
    have := congrArg Prod.snd hh
    exact one_ne_zero this

/-- Each sign projector is primitive: it has no proper nonzero idempotent below it. -/
theorem sign_projectors_primitive :
    (∀ e : MonoidAlgebra K G, e * e = e → e * ePlus = e → e = 0 ∨ e = ePlus) ∧
    (∀ e : MonoidAlgebra K G, e * e = e → e * eMinus = e → e = 0 ∨ e = eMinus) := by
  have rel := sign_projector_relations (K := K)
  constructor
  · intro e he hb
    rcases (idempotent_classification e).mp he with rfl | rfl | rfl | rfl
    · exact Or.inl rfl
    · exact Or.inr (by simpa using hb.symm)
    · exact Or.inr rfl
    · left
      rw [mul_comm, rel.2.2.1] at hb
      exact hb.symm
  · intro e he hb
    rcases (idempotent_classification e).mp he with rfl | rfl | rfl | rfl
    · exact Or.inl rfl
    · exact Or.inr (by simpa using hb.symm)
    · left
      rw [rel.2.2.1] at hb
      exact hb.symm
    · exact Or.inr rfl

end Field

/-- The canonical coefficient embedding of the actual dyadic integral group algebra. -/
noncomputable def integralMap : MonoidAlgebra ℤ_[2] G →+* MonoidAlgebra ℚ_[2] G :=
  MonoidAlgebra.mapRingHom G PadicInt.Coe.ringHom

theorem half_norm : ‖(1 / 2 : ℚ_[2])‖ = 2 := by
  have hp : ‖(2 : ℚ_[2])‖ = (2 : ℝ)⁻¹ := by
    exact_mod_cast (Padic.norm_p (p := 2))
  rw [norm_div, norm_one, hp]
  norm_num

/-- The scalar obstruction is actual dyadic integrality, not a formal denominator rule. -/
theorem half_not_integral (a : ℤ_[2]) : (a : ℚ_[2]) ≠ 1 / 2 := by
  intro ha
  have h := a.2
  rw [ha, half_norm] at h
  norm_num at h

/-- Neither actual dyadic character projector belongs to the integral coefficient image. -/
theorem sign_projectors_not_integral :
    ePlus (K := ℚ_[2]) ∉ Set.range integralMap ∧
      eMinus (K := ℚ_[2]) ∉ Set.range integralMap := by
  constructor <;> rintro ⟨a, ha⟩
  · have hc := congrArg (fun x : MonoidAlgebra ℚ_[2] G => x.coeff 1) ha
    have hcoeff : (a.coeff 1 : ℚ_[2]) = 1 / 2 := by
      simp only [integralMap, MonoidAlgebra.coeff_mapRingHom] at hc
      change (a.coeff 1 : ℚ_[2]) = _ at hc
      simpa [ePlus, g_ne_one] using hc
    exact half_not_integral _ hcoeff
  · have hc := congrArg (fun x : MonoidAlgebra ℚ_[2] G => x.coeff 1) ha
    have hcoeff : (a.coeff 1 : ℚ_[2]) = 1 / 2 := by
      simp only [integralMap, MonoidAlgebra.coeff_mapRingHom] at hc
      change (a.coeff 1 : ℚ_[2]) = _ at hc
      simpa [eMinus, g_ne_one] using hc
    exact half_not_integral _ hcoeff

end PaperXII.DyadicProjectors
