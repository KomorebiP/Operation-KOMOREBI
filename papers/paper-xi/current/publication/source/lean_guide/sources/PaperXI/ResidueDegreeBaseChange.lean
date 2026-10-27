import PaperXI.ResidueWeil
import Mathlib.Data.ZMod.Basic

/-! Integer-degree base change for residue-action pullbacks.
The map (g,m) ↦ (g,n*m) is constructed; neither subgroup equality nor index is
assumed. This does not identify a pullback with an absolute local Weil group. -/
set_option autoImplicit false
noncomputable section
open scoped Classical
namespace PaperXI.ResidueDegreeBaseChange
open PaperXI.ResidueWeil
variable {D C : Type*} [Group D] [Group C]

/-- Residue degree modulo n, with the additive quotient written multiplicatively. -/
def degreeMod (r : D →* C) (F : C) (n : ℕ) :
    Pullback r F →* Multiplicative (ZMod n) where
  toFun w := Multiplicative.ofAdd ((Multiplicative.toAdd (degree r F w) : ℤ) : ZMod n)
  map_one' := by simp
  map_mul' a b := by
    change Multiplicative.ofAdd (((Multiplicative.toAdd a.val.2 + Multiplicative.toAdd b.val.2 : ℤ)) : ZMod n) = _
    simp

/-- The actual degree-divisible subgroup. -/
def periodSubgroup (r : D →* C) (F : C) (n : ℕ) : Subgroup (Pullback r F) :=
  (degreeMod r F n).ker

instance period_normal (r : D →* C) (F : C) (n : ℕ) : (periodSubgroup r F n).Normal :=
  inferInstanceAs ((degreeMod r F n).ker.Normal)

@[simp] theorem mem_periodSubgroup (r : D →* C) (F : C) (n : ℕ) (w : Pullback r F) :
    w ∈ periodSubgroup r F n ↔ (n : ℤ) ∣ Multiplicative.toAdd (degree r F w) := by
  change (((Multiplicative.toAdd (degree r F w) : ℤ) : ZMod n) = 0) ↔ _
  exact ZMod.intCast_zmod_eq_zero_iff_dvd _ _

/-- Change residue Frobenius from F to F^n without reducing the integer degree. -/
def inclusion (r : D →* C) (F : C) (n : ℕ) :
    Pullback r (F^n) →* Pullback r F where
  toFun w := ⟨(w.val.1, Multiplicative.ofAdd ((n : ℤ) * Multiplicative.toAdd w.val.2)), by
    change r w.val.1 = F ^ ((n : ℤ) * Multiplicative.toAdd w.val.2)
    rw [zpow_mul, zpow_natCast]
    exact w.property⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' a b := by
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · change Multiplicative.ofAdd ((n : ℤ) * (Multiplicative.toAdd a.val.2 + Multiplicative.toAdd b.val.2)) = _
      simp [mul_add]

@[simp] theorem inclusion_projection (r : D →* C) (F : C) (n : ℕ)
    (w : Pullback r (F^n)) : projection r F (inclusion r F n w) = projection r (F^n) w := rfl

@[simp] theorem inclusion_degree (r : D →* C) (F : C) (n : ℕ)
    (w : Pullback r (F^n)) : Multiplicative.toAdd (degree r F (inclusion r F n w)) =
      (n : ℤ) * Multiplicative.toAdd (degree r (F^n) w) := rfl

theorem inclusion_injective (r : D →* C) (F : C) {n : ℕ} (hn : n ≠ 0) :
    Function.Injective (inclusion r F n) := by
  intro a b hab
  have h1 := congrArg (fun x : Pullback r F => x.val.1) hab
  have h2 := congrArg (fun x : Pullback r F => Multiplicative.toAdd x.val.2) hab
  have hnz : (n : ℤ) ≠ 0 := by exact_mod_cast hn
  apply Subtype.ext
  apply Prod.ext
  · exact h1
  · exact Multiplicative.toAdd.injective (mul_left_cancel₀ hnz h2)

/-- Surjectivity onto the degree subgroup needs no residue-surjectivity assumption. -/
theorem inclusion_range (r : D →* C) (F : C) (n : ℕ) :
    (inclusion r F n).range = periodSubgroup r F n := by
  ext w
  constructor
  · rintro ⟨v, rfl⟩
    rw [mem_periodSubgroup, inclusion_degree]
    exact dvd_mul_right _ _
  · intro hw
    obtain ⟨m, hm⟩ := (mem_periodSubgroup r F n w).mp hw
    let v : Pullback r (F^n) := ⟨(w.val.1, Multiplicative.ofAdd m), by
      change r w.val.1 = (F^n)^m
      rw [← zpow_natCast F n, ← zpow_mul, ← hm]
      exact w.property⟩
    refine ⟨v, ?_⟩
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · exact Multiplicative.toAdd.injective hm.symm

/-- An actual multiplicative equivalence onto the period subgroup. -/
def periodEquiv (r : D →* C) (F : C) {n : ℕ} (hn : n ≠ 0) :
    Pullback r (F^n) ≃* periodSubgroup r F n :=
  (MonoidHom.ofInjective (inclusion_injective r F hn)).trans
    (MulEquiv.subgroupCongr (inclusion_range r F n))

/-- A degree-one lift provides all integer degrees, not just residue powers. -/
theorem degree_surjective (r : D →* C) (F : C) (hF : F ∈ r.range) :
    Function.Surjective (degree r F) := by
  obtain ⟨w, hw⟩ := (exists_degree_one_iff r F).mpr hF
  intro m
  refine ⟨w ^ Multiplicative.toAdd m, ?_⟩
  rw [map_zpow, hw]
  apply Multiplicative.toAdd.injective
  simp

/-- Reduction modulo n is onto once a degree-one lift exists. -/
theorem degreeMod_surjective (r : D →* C) (F : C) (n : ℕ) (hF : F ∈ r.range) :
    Function.Surjective (degreeMod r F n) := by
  intro z
  obtain ⟨m, hm⟩ := ZMod.intCast_surjective (Multiplicative.toAdd z)
  obtain ⟨w, hw⟩ := degree_surjective r F hF (Multiplicative.ofAdd m)
  refine ⟨w, ?_⟩
  change Multiplicative.ofAdd (((Multiplicative.toAdd (degree r F w) : ℤ)) : ZMod n) = z
  rw [hw]
  exact Multiplicative.toAdd.injective hm

/-- The quotient is the actual cyclic degree quotient. -/
def quotientEquiv (r : D →* C) (F : C) (n : ℕ) (hF : F ∈ r.range) :
    Pullback r F ⧸ periodSubgroup r F n ≃* Multiplicative (ZMod n) :=
  QuotientGroup.quotientKerEquivOfSurjective (degreeMod r F n)
    (degreeMod_surjective r F n hF)

theorem quotient_card (r : D →* C) (F : C) (n : ℕ) [NeZero n] (hF : F ∈ r.range) :
    Nat.card (Pullback r F ⧸ periodSubgroup r F n) = n := by
  rw [Nat.card_congr (quotientEquiv r F n hF).toEquiv]
  simp

/-- Inertia is unaffected by nonzero degree dilation. -/
theorem inertia_preimage (r : D →* C) (F : C) {n : ℕ} (hn : n ≠ 0) :
    ((degree r F).ker).comap (inclusion r F n) = (degree r (F^n)).ker := by
  ext w
  change (Multiplicative.ofAdd ((n : ℤ) * Multiplicative.toAdd w.val.2) = 1) ↔ w.val.2 = 1
  have hnz : (n : ℤ) ≠ 0 := by exact_mod_cast hn
  constructor
  · intro hw
    apply Multiplicative.toAdd.injective
    have hz := congrArg Multiplicative.toAdd hw
    exact (mul_eq_zero.mp hz).resolve_left hnz
  · intro hw
    simp [hw]

/-- The integer degree map composes multiplicatively along an unramified tower. -/
theorem tower_degree (r : D →* C) (F : C) (m n : ℕ)
    (w : Pullback r ((F^m)^n)) :
    Multiplicative.toAdd (degree r F
      (inclusion r F m (inclusion r (F^m) n w))) =
      ((m*n : ℕ) : ℤ) * Multiplicative.toAdd (degree r ((F^m)^n) w) := by
  simp only [inclusion_degree, Nat.cast_mul, mul_assoc]

end PaperXI.ResidueDegreeBaseChange
