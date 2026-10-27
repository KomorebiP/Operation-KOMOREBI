import PaperXII.AuxiliaryGroupAlgebra
import Mathlib.Algebra.Algebra.ZMod
import Mathlib.Algebra.CharP.Algebra
import Mathlib.GroupTheory.PGroup
import Mathlib.FieldTheory.Finiteness
import Mathlib.Algebra.Field.ZMod
import Mathlib.RingTheory.Idempotents

set_option autoImplicit false

/-! The residual group algebra of a finite p-group has no nontrivial
idempotents, without an abelian hypothesis. The finite prime-field span of
an orbit supplies the fixed vector by p-group fixed-point counting. -/
namespace PaperXII.NonabelianResidual

open scoped MonoidAlgebra
open PaperXII.AuxiliaryGroupAlgebra

variable {k G : Type*} [Field k] [Group G]
variable {p : ℕ}

section PrimeFieldSpan
variable [Algebra (ZMod p) k[G]]

/-- The prime-field span of the left translates of an element. -/
noncomputable def orbitSpan (e : k[G]) : Submodule (ZMod p) k[G] :=
  Submodule.span (ZMod p) (Set.range fun g : G => MonoidAlgebra.single g 1 * e)

theorem self_mem_orbitSpan (e : k[G]) : e ∈ orbitSpan (p := p) e := by
  exact Submodule.subset_span ⟨1, by
    change MonoidAlgebra.single (1 : G) (1 : k) * e = e
    rw [← MonoidAlgebra.one_def, one_mul]⟩

theorem translate_mem_orbitSpan (e : k[G]) (g : G) {v : k[G]}
    (hv : v ∈ orbitSpan (p := p) e) :
    MonoidAlgebra.single g 1 * v ∈ orbitSpan (p := p) e := by
  induction hv using Submodule.span_induction with
  | mem v hv =>
      obtain ⟨h, rfl⟩ := hv
      exact Submodule.subset_span ⟨g * h, by simp [← mul_assoc, MonoidAlgebra.single_mul_single]⟩
  | zero => simp
  | add x y hx hy ihx ihy => simpa [mul_add] using (orbitSpan e).add_mem ihx ihy
  | smul r x hx ih => simpa [mul_smul_comm] using (orbitSpan e).smul_mem r ih

/-- Left multiplication by group elements on the finite orbit span. -/
@[instance_reducible]
noncomputable def orbitAction (e : k[G]) : MulAction G (orbitSpan (p := p) e) where
  smul g v := ⟨MonoidAlgebra.single g 1 * v.1, translate_mem_orbitSpan e g v.2⟩
  one_smul v := by
    apply Subtype.ext
    change MonoidAlgebra.single 1 1 * v.1 = v.1
    rw [← MonoidAlgebra.one_def, one_mul]
  mul_smul g h v := by
    apply Subtype.ext
    change MonoidAlgebra.single (g * h) 1 * v.1 =
      MonoidAlgebra.single g 1 * (MonoidAlgebra.single h 1 * v.1)
    simp [← mul_assoc, MonoidAlgebra.single_mul_single]

theorem orbitSpan_mul_idempotent (e : k[G]) (he : e * e = e)
    {v : k[G]} (hv : v ∈ orbitSpan (p := p) e) : v * e = v := by
  induction hv using Submodule.span_induction with
  | mem v hv => obtain ⟨g, rfl⟩ := hv; simp [mul_assoc, he]
  | zero => simp
  | add x y hx hy ihx ihy => simp [add_mul, ihx, ihy]
  | smul r x hx ih => simp [ih]

/-- Every nonzero orbit span contains a nonzero regular invariant vector. -/
theorem exists_nonzero_invariant [Fact p.Prime] [Finite G] (hG : IsPGroup p G) (e : k[G]) (he : e ≠ 0) :
    ∃ v : k[G], v ∈ orbitSpan (p := p) e ∧ v ≠ 0 ∧
      ∀ g : G, MonoidAlgebra.single g 1 * v = v := by
  classical
  let V := orbitSpan (p := p) e
  let : Module.Finite (ZMod p) V :=
    Module.Finite.span_of_finite (ZMod p) (Set.finite_range _)
  let : Finite V := Module.finite_of_finite (ZMod p)
  let : Fintype V := Fintype.ofFinite V
  let : Nontrivial V := ⟨⟨⟨e, self_mem_orbitSpan e⟩, 0, by
    intro h
    exact he (congrArg Subtype.val h)⟩⟩
  let : MulAction G V := orbitAction e
  have hd : p ∣ Nat.card V := by
    rw [Nat.card_eq_fintype_card, Module.card_eq_pow_finrank (K := ZMod p), ZMod.card]
    exact dvd_pow_self _ (ne_of_gt (Module.finrank_pos (R := ZMod p) (M := V)))
  obtain ⟨v, hv, h0v⟩ := hG.exists_fixed_point_of_prime_dvd_card_of_fixed_point V hd
    (a := 0) (by intro g; apply Subtype.ext; exact mul_zero _)
  refine ⟨v.1, v.2, ?_, ?_⟩
  · intro hv0
    exact h0v (Subtype.ext hv0.symm)
  · intro g
    exact congrArg Subtype.val (hv g)

end PrimeFieldSpan

/-- A vector fixed by every left translation has constant coefficients. -/
theorem invariant_coeff (v : k[G])
    (hv : ∀ g : G, MonoidAlgebra.single g 1 * v = v) (g : G) :
    v.coeff g = v.coeff 1 := by
  have h := congrArg (fun w : k[G] => w.coeff g) (hv g)
  simpa using h.symm

/-- On a regular invariant vector, right multiplication is scalar augmentation. -/
theorem invariant_mul (v e : k[G])
    (hv : ∀ g : G, MonoidAlgebra.single g 1 * v = v) :
    v * e = augmentation e • v := by
  induction e using MonoidAlgebra.induction_on with
  | of g =>
      ext h
      simp [augmentation_single, invariant_coeff v hv]
  | add x y hx hy => simp [mul_add, hx, hy, add_smul]
  | smul r x hx => simp [hx, smul_smul]

/-- An idempotent with zero augmentation is zero, for any finite p-group. -/
theorem idempotent_augmentation_zero [Fact p.Prime] [Finite G] [CharP k p]
    (hG : IsPGroup p G) (e : k[G]) (he : e * e = e) (ha : augmentation e = 0) :
    e = 0 := by
  let : CharP k[G] p := charP_of_injective_algebraMap (algebraMap k k[G]).injective p
  let : Algebra (ZMod p) k[G] := ZMod.algebra k[G] p
  by_contra hne
  obtain ⟨v, hv, hv0, hfixed⟩ := exists_nonzero_invariant hG e hne
  exact hv0 (by
    calc v = v * e := (orbitSpan_mul_idempotent e he hv).symm
         _ = augmentation e • v := invariant_mul v e hfixed
         _ = 0 := by simp [ha])

/-- Corollary 5.3 in full: no nontrivial residual idempotent survives even
for a noncommutative finite p-group. -/
theorem idempotent_eq_zero_or_one [Fact p.Prime] [Finite G] [CharP k p]
    (hG : IsPGroup p G) (e : k[G]) (he : e * e = e) : e = 0 ∨ e = 1 := by
  have ha : augmentation e * augmentation e = augmentation e := by
    simpa only [← map_mul] using congrArg augmentation he
  have hcases : augmentation e = 0 ∨ augmentation e = 1 := by
    by_cases h : augmentation e = 0
    · exact Or.inl h
    · exact Or.inr (mul_left_cancel₀ h (ha.trans (mul_one _).symm))
  rcases hcases with hzero | hone
  · exact Or.inl (idempotent_augmentation_zero hG e he hzero)
  · right
    have h : 1 - e = 0 := idempotent_augmentation_zero hG (1 - e)
      (show IsIdempotentElem (1 - e) from (show IsIdempotentElem e from he).one_sub) (by simp [hone])
    exact (sub_eq_zero.mp h).symm

end PaperXII.NonabelianResidual
