module
public import EchelonBounds

@[expose] public section
namespace Komorebi.Echelon

theorem leadingRow_mem {n : Nat} (q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B : Basis n) :
    Represents (.cons q hq b B) (Fin.cons q b) := by
  apply (represents_cons_iff q hq b B _).mpr
  refine ⟨1, by simp, ?_⟩
  simpa only [tailV_cons, one_smul, sub_self] using (show Represents B 0 from ⟨0,synth_zero B⟩)

theorem zero_head_represents_iff {n : Nat} (q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B : Basis n) (x : Fin n → ℤ) :
    Represents (.cons q hq b B) (Fin.cons 0 x) ↔ Represents B x := by
  rw [represents_cons_iff]
  constructor
  · rintro ⟨a,ha,ht⟩
    have hm : a*q=0 := by simpa using ha.symm
    have hz : a=0 := (mul_eq_zero.mp hm).resolve_right (ne_of_gt hq)
    simpa [hz] using ht
  · intro hx
    exact ⟨0,by simp,by simpa using hx⟩

/-- The lower triangular block is intrinsically the lattice section with first coordinate zero. -/
theorem lattice_tail_eq {n : Nat} (q r : ℤ) (hq : 0<q) (hr : 0<r)
    (b c : Fin n → ℤ) (B C : Basis n)
    (h : lattice (.cons q hq b B)=lattice (.cons r hr c C)) : lattice B=lattice C := by
  ext x
  change Represents B x ↔ Represents C x
  rw [← zero_head_represents_iff q hq b B x, ← zero_head_represents_iff r hr c C x]
  change Fin.cons 0 x ∈ lattice (.cons q hq b B) ↔ Fin.cons 0 x ∈ lattice (.cons r hr c C)
  rw [h]

/-- A reduced full triangular integer basis is unique for its actual lattice. -/
theorem reduced_unique {n : Nat} (B C : Basis n) (hB : Reduced B) (hC : Reduced C)
    (h : lattice B=lattice C) : B=C := by
  induction B with
  | nil => cases C; rfl
  | cons q hq b B ih =>
    cases C with
    | cons r hr c C =>
      have htail := lattice_tail_eq q r hq hr b c B C h
      have hrest : B=C := ih C hB.2 hC.2 htail
      have hqmem : Represents (.cons r hr c C) (Fin.cons q b) := by
        change Fin.cons q b ∈ lattice (.cons r hr c C)
        rw [← h]
        exact leadingRow_mem q hq b B
      have hrmem : Represents (.cons q hq b B) (Fin.cons r c) := by
        change Fin.cons r c ∈ lattice (.cons q hq b B)
        rw [h]
        exact leadingRow_mem r hr c C
      obtain ⟨a,ha,hta⟩ := (represents_cons_iff r hr c C _).mp hqmem
      obtain ⟨e,he,_⟩ := (represents_cons_iff q hq b B _).mp hrmem
      have hqr : q=r := Int.dvd_antisymm (le_of_lt hq) (le_of_lt hr)
        ⟨e,by simpa [mul_comm] using he⟩ ⟨a,by simpa [mul_comm] using ha⟩
      subst r
      subst C
      have ha1 : a=1 := by
        apply mul_right_cancel₀ (ne_of_gt hq)
        simpa using ha.symm
      have hbc : b=c := inBox_unique B b c hB.1 hC.1 (by simpa [ha1] using hta)
      subst c
      rfl

/-- Canonicalization is independent of the supplied triangular presentation. -/
theorem normalize_eq_of_lattice_eq {n : Nat} (B C : Basis n)
    (h : lattice B=lattice C) : normalize B=normalize C := by
  apply reduced_unique _ _ (normalize_reduced B) (normalize_reduced C)
  simpa only [lattice_normalize] using h

theorem normalize_eq_iff_lattice_eq {n : Nat} (B C : Basis n) :
    normalize B=normalize C ↔ lattice B=lattice C := by
  constructor
  · intro h
    rw [← lattice_normalize B, ← lattice_normalize C, h]
  · exact normalize_eq_of_lattice_eq B C

end Komorebi.Echelon
