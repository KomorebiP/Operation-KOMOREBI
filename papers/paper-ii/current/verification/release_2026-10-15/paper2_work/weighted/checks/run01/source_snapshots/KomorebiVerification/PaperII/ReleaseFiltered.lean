import KomorebiVerification.PaperII.WeightedTransfer

/-!
# Complete filtered inversion at inverse-limit scope

The quotient at depth `n` is the additive quotient by the relation
`x - y ∈ Fⁿ`.  Its transition maps are induced by the identity.  Thus the
`Complete` hypothesis below is exactly bijectivity of the canonical map to
compatible residue families, rather than an assumed Neumann-series result.
No norm, metrizability hypothesis or finite-dimensional hypothesis is used.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseFiltered

open scoped BigOperators
open Komorebi.PaperII.WeightedTransfer

universe u v

/-- An exhaustive multiplicative ideal filtration. The two ideal actions follow
from multiplicativity and `all_mem`. -/
structure IdealFiltration (R : Type u) [Ring R] extends MultiplicativeFiltration R where
  all_mem : ∀ x : R, Mem 0 x

namespace IdealFiltration

variable {R : Type u} [Ring R] (F : IdealFiltration R)

theorem sub_mem {n : ℕ} {x y : R} (hx : F.Mem n x) (hy : F.Mem n y) :
    F.Mem n (x - y) := by
  simpa only [sub_eq_add_neg] using F.add_mem hx (F.neg_mem hy)

theorem left_mem (x : R) {n : ℕ} {y : R} (hy : F.Mem n y) :
    F.Mem n (x * y) := by
  simpa only [Nat.zero_add] using F.mul_mem (F.all_mem x) hy

theorem right_mem {n : ℕ} {x : R} (hx : F.Mem n x) (y : R) :
    F.Mem n (x * y) := by
  simpa only [Nat.add_zero] using F.mul_mem hx (F.all_mem y)

/-- The usual residue equivalence modulo the filtration ideal. -/
def residueSetoid (n : ℕ) : Setoid R where
  r x y := F.Mem n (x - y)
  iseqv := ⟨by intro x; simpa using F.zero_mem n,
    by intro x y h; simpa only [neg_sub] using F.neg_mem h,
    by
      intro x y z hxy hyz
      have h := F.add_mem hxy hyz
      simpa only [sub_add_sub_cancel] using h⟩

/-- The residue set underlying the quotient ring `R/Fⁿ`. -/
def Residue (n : ℕ) := Quotient (F.residueSetoid n)

def residue (n : ℕ) (x : R) : F.Residue n := Quotient.mk _ x

theorem residue_eq_iff (n : ℕ) (x y : R) :
    F.residue n x = F.residue n y ↔ F.Mem n (x - y) :=
  ⟨Quotient.exact, Quotient.sound⟩

/-- Transition from a finer quotient to a coarser quotient. -/
def reduce {m n : ℕ} (h : m ≤ n) : F.Residue n → F.Residue m :=
  Quotient.map id (by intro x y hxy; exact F.antitone h hxy)

/-- Compatible residue families: the underlying set of the inverse limit. -/
def ResidueLimit :=
  {x : ∀ n : ℕ, F.Residue n // ∀ m n (h : m ≤ n), F.reduce h (x n) = x m}

/-- The canonical map from the ring to its inverse limit of residues. -/
def toResidueLimit (x : R) : F.ResidueLimit :=
  ⟨fun n ↦ F.residue n x, by intro m n h; rfl⟩

/-- Exact inverse-limit completeness and separation. -/
def Complete : Prop := Function.Bijective F.toResidueLimit

/-- Injectivity of the canonical inverse-limit map is separation. -/
theorem separated (hF : F.Complete) {x : R} (hx : ∀ n, F.Mem n x) : x = 0 := by
  apply hF.1
  apply Subtype.ext
  funext n
  apply Quotient.sound
  simpa only [sub_zero] using hx n

/-- Every coherent sequence of representatives lifts to an element at all depths. -/
theorem lift_coherent (hF : F.Complete) (s : ℕ → R)
    (hs : ∀ m n, m ≤ n → F.Mem m (s n - s m)) :
    ∃ x : R, ∀ n, F.Mem n (x - s n) := by
  let z : F.ResidueLimit := ⟨fun n ↦ F.residue n (s n), by
    intro m n h
    apply Quotient.sound
    exact hs m n h⟩
  obtain ⟨x, hx⟩ := hF.2 z
  refine ⟨x, ?_⟩
  intro n
  apply Quotient.exact
  exact congrFun (congrArg Subtype.val hx) n

/-- Powers of a filtration-one element gain one degree at each multiplication. -/
theorem pow_mem {a : R} (ha : F.Mem 1 a) (n : ℕ) : F.Mem n (a ^ n) := by
  induction n with
  | zero => simpa only [pow_zero] using F.one_mem
  | succ n ih =>
      simpa only [pow_succ, Nat.succ_eq_add_one] using F.mul_mem ih ha

/-- The finite geometric candidates form a coherent family of approximations. -/
theorem geometric_coherent {a : R} (ha : F.Mem 1 a) :
    ∀ m n, m ≤ n →
      F.Mem m (finiteGeometricInverse a n - finiteGeometricInverse a m) := by
  intro m n hmn
  obtain ⟨k, rfl⟩ := Nat.exists_eq_add_of_le hmn
  induction k with
  | zero => simpa using F.zero_mem m
  | succ k ih =>
      have hp : F.Mem m ((-a) ^ (m + k)) :=
        F.antitone (Nat.le_add_right m k) (F.pow_mem (F.neg_mem ha) (m + k))
      have hs := F.add_mem ih hp
      simpa only [finiteGeometricInverse, Nat.add_succ, Finset.sum_range_succ,
        add_sub_right_comm] using hs

/-- The two finite geometric residual identities, with no commutativity assumption. -/
theorem geometric_residual (a : R) (n : ℕ) :
    finiteGeometricInverse a n * (1 + a) = 1 - (-a) ^ n ∧
      (1 + a) * finiteGeometricInverse a n = 1 - (-a) ^ n := by
  constructor
  · simpa only [finiteGeometricInverse, sub_neg_eq_add] using geom_sum_mul_neg (-a) n
  · simpa only [finiteGeometricInverse, sub_neg_eq_add] using mul_neg_geom_sum (-a) n

/-- A filtration-convergent Neumann inverse in the full inverse-limit-complete ring.
The congruences are the definition of convergence for the filtration topology. -/
theorem exists_geometric_inverse (hF : F.Complete) {a : R} (ha : F.Mem 1 a) :
    ∃ S : R, TwoSidedInverse (1 + a) S ∧
      ∀ n, F.Mem n (S - finiteGeometricInverse a n) := by
  obtain ⟨S, hS⟩ := F.lift_coherent hF (finiteGeometricInverse a) (F.geometric_coherent ha)
  refine ⟨S, ⟨?_, ?_⟩, hS⟩
  · apply sub_eq_zero.mp
    apply F.separated hF
    intro n
    have hh := F.sub_mem (F.right_mem (hS n) (1 + a)) (F.pow_mem (F.neg_mem ha) n)
    have he := (F.geometric_residual a n).1
    have hid : (S - finiteGeometricInverse a n) * (1 + a) - (-a) ^ n =
        S * (1 + a) - 1 := by
      rw [sub_mul, he]
      abel
    simpa only [hid] using hh
  · apply sub_eq_zero.mp
    apply F.separated hF
    intro n
    have hh := F.sub_mem (F.left_mem (1 + a) (hS n)) (F.pow_mem (F.neg_mem ha) n)
    have he := (F.geometric_residual a n).2
    have hid : (1 + a) * (S - finiteGeometricInverse a n) - (-a) ^ n =
        (1 + a) * S - 1 := by
      rw [mul_sub, he]
      abel
    simpa only [hid] using hh

end IdealFiltration
end Komorebi.PaperII.ReleaseFiltered
