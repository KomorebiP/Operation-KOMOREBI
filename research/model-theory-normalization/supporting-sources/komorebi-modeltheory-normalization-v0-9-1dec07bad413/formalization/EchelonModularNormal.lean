module
public import EchelonCanonical
public import EchelonModular

@[expose] public section
namespace Komorebi.Echelon

def canonicalBasis (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) : Basis n := normalize (build m rows)

theorem canonicalBasis_correct (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (x : Fin n → ℤ) :
    Represents (canonicalBasis m rows) x ↔ reduce m x ∈ rowSpan (ZMod m) rows := by
  rw [canonicalBasis, represents_normalize, build_correct]

theorem canonicalBasis_containsModulus (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) : ContainsModulus (m:ℤ) (canonicalBasis m rows) := by
  intro x
  apply (canonicalBasis_correct m rows _).mpr
  have hz : reduce m ((m:ℤ) • x)=0 := by ext i; simp [reduce]
  rw [hz]
  exact (rowSpan (ZMod m) rows).zero_mem

/-- An exact, ambient-coordinate-relative key for residue submodules. -/
theorem canonicalBasis_eq_iff (m : Nat) [NeZero m] {n : Nat}
    (rows other : List (Fin n → ZMod m)) :
    canonicalBasis m rows=canonicalBasis m other ↔
      rowSpan (ZMod m) rows=rowSpan (ZMod m) other := by
  constructor
  · intro h
    ext x
    rw [← reduce_lift m x]
    rw [← canonicalBasis_correct m rows _, ← canonicalBasis_correct m other _, h]
  · intro h
    apply reduced_unique _ _ (normalize_reduced _) (normalize_reduced _)
    ext x
    change Represents (canonicalBasis m rows) x ↔ Represents (canonicalBasis m other) x
    rw [canonicalBasis_correct, canonicalBasis_correct, h]

theorem canonicalBasis_entry_bounds (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (i j : Fin n) :
    0≤entries (canonicalBasis m rows) i j ∧ entries (canonicalBasis m rows) i j≤(m:ℤ) :=
  reduced_entry_bounds (m:ℤ) (by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)) _
    (canonicalBasis_containsModulus m rows) (normalize_reduced _) i j

end Komorebi.Echelon
