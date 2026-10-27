import PaperXI.FiniteResidueBaseChange

/-! A residue-field fixing subgroup, not an abstract subgroup assigned index f.
Its pullback for geometric |k'|-Frobenius is identified with the degree-f subgroup
of the |k|-Frobenius pullback. No local-field lifting theorem is asserted. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteResidueSubgroup
open PaperXI.ResidueWeil PaperXI.ResidueDegreeBaseChange PaperXI.FiniteResidueBaseChange
variable (k k' E : Type*) [Field k] [Fintype k] [Field k'] [Fintype k'] [Field E]
  [Algebra k k'] [Algebra k E] [Algebra k' E] [Algebra.IsAlgebraic k E]

/-- q-power Frobenius commutes with the actual field embedding. -/
theorem arithmetic_map (x : k') :
    arithmetic k E (algebraMap k' E x) = algebraMap k' E (arithmetic k k' x) := by
  simp only [arithmetic_apply, map_pow]

/-- Its inverse commutes with that embedding as well. -/
theorem geometric_map (x : k') :
    geometric k E (algebraMap k' E x) = algebraMap k' E (geometric k k' x) := by
  apply (arithmetic k E).injective
  change arithmetic k E ((arithmetic k E).symm (algebraMap k' E x)) = _
  rw [(arithmetic k E).apply_symm_apply, arithmetic_map]
  exact congrArg (algebraMap k' E) ((arithmetic k k').apply_symm_apply x).symm

theorem geometric_pow_map (n : ℕ) (x : k') :
    (geometric k E ^ n) (algebraMap k' E x) =
      algebraMap k' E ((geometric k k' ^ n) x) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [pow_succ', pow_succ']
    change geometric k E ((geometric k E ^ n) (algebraMap k' E x)) =
      algebraMap k' E (geometric k k' ((geometric k k' ^ n) x))
    rw [ih, geometric_map]

/-- Integer powers preserve the convention even for negative Frobenius degrees. -/
theorem geometric_zpow_map (n : ℤ) (x : k') :
    (geometric k E ^ n) (algebraMap k' E x) =
      algebraMap k' E ((geometric k k' ^ n) x) := by
  cases n with
  | ofNat n =>
    change (geometric k E ^ (n : ℤ)) (algebraMap k' E x) =
      algebraMap k' E ((geometric k k' ^ (n : ℤ)) x)
    simpa only [zpow_natCast] using geometric_pow_map k k' E n x
  | negSucc n =>
    simp only [zpow_negSucc, geometric, inv_pow, inv_inv]
    simp only [arithmetic_pow_apply, map_pow]

/-- Fixing all elements of the finite residue extension detects exact degree divisibility. -/
theorem fixes_subfield_iff (m : ℤ) :
    (∀ x : k', (geometric k E ^ m) (algebraMap k' E x) = algebraMap k' E x) ↔
      (Module.finrank k k' : ℤ) ∣ m := by
  rw [← geometric_zpow_eq_one k k' m]
  constructor
  · intro h
    apply RingEquiv.ext
    intro x
    apply (algebraMap k' E).injective
    rw [← geometric_zpow_map]
    exact h x
  · intro h x
    rw [geometric_zpow_map, h]
    rfl

section Group
variable {D : Type*} [Group D]

/-- The genuine pointwise stabilizer of the embedded residue field. -/
def fixing (r : D →* RingAut E) : Subgroup D where
  carrier := {g | ∀ x : k', r g (algebraMap k' E x) = algebraMap k' E x}
  one_mem' := by intro x; simp
  mul_mem' := by
    intro g h hg hh x
    rw [map_mul]
    change r g (r h (algebraMap k' E x)) = _
    rw [hh, hg]
  inv_mem' := by
    intro g hg x
    rw [map_inv]
    apply (r g).injective
    change r g ((r g).symm (algebraMap k' E x)) = _
    rw [(r g).apply_symm_apply, hg]

omit [Field k] [Fintype k] [Fintype k'] [Algebra k k'] [Algebra k E]
  [Algebra.IsAlgebraic k E] in
theorem kernel_le_fixing (r : D →* RingAut E) : r.ker ≤ fixing k' E r := by
  intro g hg x
  change r g = 1 at hg
  rw [hg]
  rfl

/-- A lift fixes k' exactly when its integer Frobenius degree is divisible by [k':k]. -/
theorem projection_mem_iff (r : D →* RingAut E) (w : Pullback r (geometric k E)) :
    projection r (geometric k E) w ∈ fixing k' E r ↔
      (Module.finrank k k' : ℤ) ∣ Multiplicative.toAdd (degree r (geometric k E) w) := by
  change (∀ x : k', r w.val.1 (algebraMap k' E x) = algebraMap k' E x) ↔ _
  rw [w.property]
  exact fixes_subfield_iff k k' E _

variable [Algebra.IsAlgebraic k' E]

/-- Under its own residue Frobenius, every pullback element fixes the residue base. -/
theorem projection_fixes (r : D →* RingAut E) (w : Pullback r (geometric k' E)) :
    projection r (geometric k' E) w ∈ fixing k' E r := by
  apply (projection_mem_iff k' k' E r w).mpr
  simp

/-- Restricting the decomposition action to the actual field-fixing subgroup loses no
pullback elements for geometric |k'|-Frobenius. -/
def fixingEquiv (r : D →* RingAut E) :
    Pullback (r.comp (fixing k' E r).subtype) (geometric k' E) ≃*
      Pullback r (geometric k' E) where
  toFun w := ⟨(w.val.1.val, w.val.2), w.property⟩
  invFun w := ⟨(⟨w.val.1, projection_fixes k' E r w⟩, w.val.2), w.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_mul' _ _ := rfl

/-- The source-facing residue-extension attachment. The left-hand subgroup is defined
by fixing the actual embedded field, while the right-hand one is a degree kernel. -/
def unramifiedEquiv (r : D →* RingAut E) :
    Pullback (r.comp (fixing k' E r).subtype) (geometric k' E) ≃*
      periodSubgroup r (geometric k E) (Module.finrank k k') :=
  (fixingEquiv k' E r).trans (pullbackEquiv k E k' r)

end Group
end PaperXI.FiniteResidueSubgroup
