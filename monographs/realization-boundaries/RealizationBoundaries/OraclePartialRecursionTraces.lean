import RealizationBoundaries.ComputablePresentations

/-! # Finite semantic traces of relative partial primitive recursion -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The literal partial primitive recursion appearing in native `RecursiveIn.prec`. -/
def oraclePartialRec (f h : ℕ →. ℕ) (a : ℕ) : ℕ → Part ℕ :=
  Nat.rec (f a) (fun n r => r.bind (fun z => h (Nat.pair a (Nat.pair n z))))

/-- A terminating primitive-recursion evaluation is exactly a finite sequence
of terminating child evaluations. Values after the final stage carry no data. -/
theorem oraclePartialRec_mem_iff_trace (f h : ℕ →. ℕ) (a n y : ℕ) :
    y ∈ oraclePartialRec f h a n ↔
      ∃ s : ℕ → ℕ, s n = y ∧ s 0 ∈ f a ∧
        ∀ i < n, s (i+1) ∈ h (Nat.pair a (Nat.pair i (s i))) := by
  induction n generalizing y with
  | zero =>
    constructor
    · intro hy
      exact ⟨fun _ => y, rfl, hy, fun _ hi => (Nat.not_lt_zero _ hi).elim⟩
    · rintro ⟨s, hsy, hs, _⟩
      exact hsy ▸ hs
  | succ n ih =>
    change y ∈ (oraclePartialRec f h a n).bind
      (fun z => h (Nat.pair a (Nat.pair n z))) ↔ _
    rw [Part.mem_bind_iff]
    constructor
    · rintro ⟨z, hz, hy⟩
      obtain ⟨s, hsn, hs0, hs⟩ := (ih z).mp hz
      let t := Function.update s (n+1) y
      refine ⟨t, by simp [t], ?_, ?_⟩
      · simpa [t, Nat.succ_ne_zero] using hs0
      · intro i hi
        rcases Nat.lt_succ_iff_lt_or_eq.mp hi with hin | rfl
        · have hi1 : i+1 ≠ n+1 := by omega
          have hi0 : i ≠ n+1 := by omega
          simpa [t, Function.update_of_ne hi1, Function.update_of_ne hi0] using hs i hin
        · simpa [t, hsn] using hy
    · rintro ⟨s, hsn, hs0, hs⟩
      refine ⟨s n, (ih (s n)).mpr ⟨s, rfl, hs0, ?_⟩, ?_⟩
      · exact fun i hi => hs i (Nat.lt_succ_of_lt hi)
      · exact hsn ▸ hs n (Nat.lt_succ_self n)

/-- The native primitive-recursion constructor uses exactly this semantic
recursor after decoding its parameter/count pair. -/
theorem recursiveIn_prec_uses_oraclePartialRec {O : Set (ℕ →. ℕ)}
    {f h : ℕ →. ℕ} (hf : Nat.RecursiveIn O f) (hh : Nat.RecursiveIn O h) :
    Nat.RecursiveIn O (fun k => oraclePartialRec f h k.unpair.1 k.unpair.2) :=
  Nat.RecursiveIn.prec hf hh

end RealizationBoundaries
