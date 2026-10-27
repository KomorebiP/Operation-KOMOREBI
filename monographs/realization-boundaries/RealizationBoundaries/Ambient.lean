import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.Order.BigOperators.GroupWithZero.Finset
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Data.Set.Finite.Basic

/-!
# The actual squarefree product and its finite-support subgroup

The index type contains every natural prime exactly once. The product below is
an unrestricted dependent function space, not a finite truncation.
-/

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace RealizationBoundaries

abbrev Prime := Nat.Primes
abbrev Coordinate (p : Prime) := ZMod p.val
abbrev Ambient := (p : Prime) → Coordinate p

instance primeFact (p : Prime) : Fact p.val.Prime := ⟨p.property⟩

def support (x : Ambient) : Set Prime := {p | x p ≠ 0}

@[simp] theorem mem_support (x : Ambient) (p : Prime) :
    p ∈ support x ↔ x p ≠ 0 := Iff.rfl

def finiteSupport : AddSubgroup Ambient where
  carrier := {x | (support x).Finite}
  zero_mem' := by simp [support]
  add_mem' := by
    intro x y hx hy
    apply (hx.union hy).subset
    intro p hp
    by_contra hn
    have hxy : x p = 0 ∧ y p = 0 := by simpa [support] using hn
    exact hp (by simp [hxy.1, hxy.2])
  neg_mem' := by
    intro x hx
    simpa [support] using hx

@[simp] theorem mem_finiteSupport (x : Ambient) :
    x ∈ finiteSupport ↔ (support x).Finite := Iff.rfl

/-- A finite pattern interpreted as an actual infinite vector. -/
def cut (s : Finset Prime) (x : Ambient) : Ambient :=
  fun p => if p ∈ s then x p else 0

theorem cut_mem_finiteSupport (s : Finset Prime) (x : Ambient) :
    cut s x ∈ finiteSupport := by
  apply s.finite_toSet.subset
  intro p hp
  by_contra hn
  have hn' : p ∉ s := hn
  exact hp (by simp [cut, hn'])

@[simp] theorem cut_apply_mem (s : Finset Prime) (x : Ambient) (p : Prime)
    (hp : p ∈ s) : cut s x p = x p := by simp [cut, hp]

@[simp] theorem cut_apply_not_mem (s : Finset Prime) (x : Ambient) (p : Prime)
    (hp : p ∉ s) : cut s x p = 0 := by simp [cut, hp]

/-- All prime coordinates at which multiplication by `m` can fail to be a unit. -/
def exceptional (m : ℕ) : Set Prime := {p | p.val ∣ m}

theorem exceptional_finite {m : ℕ} (hm : 0 < m) : (exceptional m).Finite := by
  have hfinite : {p : Prime | p.val ≤ m}.Finite :=
    (Set.finite_Iic m).preimage Subtype.val_injective.injOn
  exact hfinite.subset (fun p hp => Nat.le_of_dvd hm hp)

@[simp] theorem coordinate_nsmul (m : ℕ) (x : Ambient) (p : Prime) :
    (m • x) p = (m : Coordinate p) * x p := by
  simp [nsmul_eq_mul]

/-- Exact obstruction to multiplication by an integer in one prime coordinate. -/
theorem coordinate_cast_eq_zero (m : ℕ) (p : Prime) :
    (m : Coordinate p) = 0 ↔ p.val ∣ m := by
  exact CharP.cast_eq_zero_iff (Coordinate p) p.val m

/-- A nonexceptional coordinate cannot disappear under multiplication. -/
theorem coordinate_eq_zero_of_nsmul_eq_zero {m : ℕ} {x : Ambient} (p : Prime)
    (hp : ¬ p.val ∣ m) (hx : (m • x) p = 0) : x p = 0 := by
  have hm : (m : Coordinate p) ≠ 0 := (coordinate_cast_eq_zero m p).not.mpr hp
  exact (mul_eq_zero.mp ((coordinate_nsmul m x p) ▸ hx)).resolve_left hm

/-- Integer multiplication cannot turn an infinitely supported vector into a finite one. -/
theorem finiteSupport_of_nsmul {m : ℕ} (hm : 0 < m) (x : Ambient)
    (hx : m • x ∈ finiteSupport) : x ∈ finiteSupport := by
  apply ((show (support (m • x)).Finite from hx).union (exceptional_finite hm)).subset
  intro p hp
  by_contra hn
  have hn' : (m • x) p = 0 ∧ ¬p.val ∣ m := by
    simpa only [Set.mem_union, mem_support, exceptional, Set.mem_ofPred_eq, not_or, not_not] using hn
  exact hp (coordinate_eq_zero_of_nsmul_eq_zero p hn'.2 hn'.1)

/-- Every finitely supported vector is killed by a positive integer. -/
theorem exists_annihilator_of_finiteSupport (x : Ambient) (hx : x ∈ finiteSupport) :
    ∃ m : ℕ, 0 < m ∧ m • x = 0 := by
  classical
  let s := (show (support x).Finite from hx).toFinset
  refine ⟨∏ p ∈ s, p.val, ?_, ?_⟩
  · exact Finset.prod_pos (fun p _ => p.property.pos)
  · funext p
    by_cases hp : p ∈ s
    · have hd : p.val ∣ ∏ q ∈ s, q.val := Finset.dvd_prod_of_mem (fun q : Prime => q.val) hp
      simp [(coordinate_cast_eq_zero _ p).mpr hd]
    · have hxp : x p = 0 := by simpa [s, support] using hp
      simp [hxp]

/-- Monograph Theorem 2.1, algebraic torsion assertion. -/
theorem torsion_iff_finiteSupport (x : Ambient) :
    (∃ m : ℕ, 0 < m ∧ m • x = 0) ↔ x ∈ finiteSupport := by
  constructor
  · rintro ⟨m, hm, hmx⟩
    exact finiteSupport_of_nsmul hm x (hmx ▸ finiteSupport.zero_mem)
  · exact exists_annihilator_of_finiteSupport x

end RealizationBoundaries
