module
public import EchelonNormalize

@[expose] public section
namespace Komorebi.Echelon

/-- The complete modular kernel, not merely its rational span, is retained. -/
def ContainsModulus {n : Nat} (m : ℤ) (B : Basis n) : Prop :=
  ∀ x : Fin n → ℤ, Represents B (m • x)

theorem containsModulus_normalize {n : Nat} (m : ℤ) (B : Basis n) :
    ContainsModulus m (normalize B) ↔ ContainsModulus m B := by
  simp only [ContainsModulus, represents_normalize]

theorem containsModulus_tail {n : Nat} (m q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B : Basis n) (hB : ContainsModulus m (.cons q hq b B)) :
    ContainsModulus m B := by
  intro x
  obtain ⟨a,ha,ht⟩ := (represents_cons_iff q hq b B _).mp (hB (Fin.cons 0 x))
  have haz : a=0 := by
    have hmul : a*q=0 := by simpa using ha.symm
    exact (mul_eq_zero.mp hmul).resolve_right (ne_of_gt hq)
  simpa only [haz, zero_smul, sub_zero, tailV_smul, tailV_cons] using ht

theorem containsModulus_head_dvd {n : Nat} (m q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B : Basis n) (hB : ContainsModulus m (.cons q hq b B)) :
    q ∣ m := by
  obtain ⟨a,ha,_⟩ := (represents_cons_iff q hq b B _).mp (hB (Fin.cons 1 0))
  refine ⟨a,?_⟩
  simpa [mul_comm] using ha

/-- Every pivot divides the actual modulus, even for non-prime moduli. -/
theorem pivots_dvd_modulus {n : Nat} (m : ℤ) (B : Basis n)
    (hB : ContainsModulus m B) (i : Fin n) : pivots B i ∣ m := by
  induction B with
  | nil => exact Fin.elim0 i
  | cons q hq b B ih =>
    refine Fin.cases ?_ (fun j => ?_) i
    · exact containsModulus_head_dvd m q hq b B hB
    · exact ih (containsModulus_tail m q hq b B hB) j

theorem pivots_positive {n : Nat} (B : Basis n) (i : Fin n) : 0<pivots B i := by
  induction B with
  | nil => exact Fin.elim0 i
  | cons q hq b B ih => exact Fin.cases hq (fun j => ih j) i

theorem pivots_le_modulus {n : Nat} (m : ℤ) (hm : 0<m) (B : Basis n)
    (hB : ContainsModulus m B) (i : Fin n) : pivots B i ≤ m :=
  Int.le_of_dvd hm (pivots_dvd_modulus m B hB i)

theorem inBox_bounds {n : Nat} (B : Basis n) (x : Fin n → ℤ)
    (hx : InBox B x) (i : Fin n) : 0≤x i ∧ x i<pivots B i := by
  induction B with
  | nil => exact Fin.elim0 i
  | cons q hq b B ih =>
    exact Fin.cases ⟨hx.1,hx.2.1⟩ (fun j => ih _ hx.2.2 j) i

/-- All stored row entries, including the zero lower triangle. -/
def entries : {n : Nat} → Basis n → (Fin n → Fin n → ℤ)
  | 0, .nil => fun i => Fin.elim0 i
  | _+1, .cons q _ b B =>
    fun i => Fin.cases (Fin.cons q b) (fun j => Fin.cons 0 (entries B j)) i

/-- A reduced modular preimage basis has uniformly bounded stored integers. -/
theorem reduced_entry_bounds {n : Nat} (m : ℤ) (hm : 0<m) (B : Basis n)
    (hB : ContainsModulus m B) (hred : Reduced B) (i j : Fin n) :
    0 ≤ entries B i j ∧ entries B i j ≤ m := by
  induction B with
  | nil => exact Fin.elim0 i
  | cons q hq b B ih =>
    have ht := containsModulus_tail m q hq b B hB
    refine Fin.cases ?_ (fun a => ?_) i
    · refine Fin.cases ?_ (fun bidx => ?_) j
      · exact ⟨le_of_lt hq, Int.le_of_dvd hm (containsModulus_head_dvd m q hq b B hB)⟩
      · have hb := inBox_bounds B b hred.1 bidx
        exact ⟨hb.1, le_trans (le_of_lt hb.2) (pivots_le_modulus m hm B ht bidx)⟩
    · refine Fin.cases ?_ (fun bidx => ?_) j
      · exact ⟨le_rfl,le_of_lt hm⟩
      · exact ih ht hred.2 a bidx

theorem normalized_entry_bounds {n : Nat} (m : ℤ) (hm : 0<m) (B : Basis n)
    (hB : ContainsModulus m B) (i j : Fin n) :
    0 ≤ entries (normalize B) i j ∧ entries (normalize B) i j ≤ m :=
  reduced_entry_bounds m hm (normalize B)
    ((containsModulus_normalize m B).mpr hB) (normalize_reduced B) i j

/-- One exact insertion followed by the proved lattice-preserving normalizer. -/
def normalizedInsert {n : Nat} (B : Basis n) (v : Fin n → ℤ) : Basis n :=
  normalize (insert B v)

theorem normalizedInsert_correct {n : Nat} (B : Basis n) (v x : Fin n → ℤ) :
    Represents (normalizedInsert B v) x ↔ ∃ c : ℤ, Represents B (x-c • v) := by
  rw [normalizedInsert, represents_normalize, insert_correct]

theorem containsModulus_normalizedInsert {n : Nat} (m : ℤ) (B : Basis n)
    (hB : ContainsModulus m B) (v : Fin n → ℤ) :
    ContainsModulus m (normalizedInsert B v) := by
  intro x
  exact (normalizedInsert_correct B v _).mpr ⟨0,by simpa using hB x⟩

theorem normalizedInsert_entry_bounds {n : Nat} (m : ℤ) (hm : 0<m) (B : Basis n)
    (hB : ContainsModulus m B) (v : Fin n → ℤ) (i j : Fin n) :
    0 ≤ entries (normalizedInsert B v) i j ∧ entries (normalizedInsert B v) i j ≤ m := by
  exact reduced_entry_bounds m hm _ (containsModulus_normalizedInsert m B hB v)
    (normalize_reduced _) i j

end Komorebi.Echelon
