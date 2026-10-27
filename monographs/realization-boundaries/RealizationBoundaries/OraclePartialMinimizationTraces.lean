import RealizationBoundaries.ComputablePresentations

/-! # Exact finite value traces for native partial minimization -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- A successful native minimization has exactly a finite trace of defined,
nonzero earlier outputs followed by a zero output. No behavior after the
successful bound is required. -/
theorem oracle_partial_minimization_trace (f : ℕ →. ℕ) (a y : ℕ) :
    y ∈ Nat.rfind (fun i => (fun m => decide (m = 0)) <$> f (Nat.pair a i)) ↔
      ∃ s : ℕ → ℕ, s y = 0 ∧
        (∀ i ≤ y, s i ∈ f (Nat.pair a i)) ∧ ∀ i < y, s i ≠ 0 := by
  classical
  rw [Nat.mem_rfind]
  constructor
  · rintro ⟨hy, hmin⟩
    have hz : 0 ∈ f (Nat.pair a y) := by
      obtain ⟨v, hv, hzero⟩ := (Part.mem_map_iff _).mp hy
      have hv0 : v = 0 := by simpa using hzero
      exact hv0 ▸ hv
    have hdom : ∀ i ≤ y, (f (Nat.pair a i)).Dom := by
      intro i hi
      rcases lt_or_eq_of_le hi with hlt | rfl
      · obtain ⟨v, hv, _⟩ := (Part.mem_map_iff _).mp (hmin hlt)
        exact Part.dom_iff_mem.mpr ⟨v, hv⟩
      · exact Part.dom_iff_mem.mpr ⟨0, hz⟩
    let s : ℕ → ℕ := fun i => if hi : i ≤ y then (f (Nat.pair a i)).get (hdom i hi) else 0
    have hs : ∀ i ≤ y, s i ∈ f (Nat.pair a i) := by
      intro i hi
      dsimp [s]
      rw [dite_eq_left hi]
      exact Part.get_mem _
    refine ⟨s, Part.mem_unique (hs y le_rfl) hz, hs, ?_⟩
    intro i hi
    obtain ⟨v, hv, hfalse⟩ := (Part.mem_map_iff _).mp (hmin hi)
    have hv0 : v ≠ 0 := by simpa using hfalse
    have he : s i = v := Part.mem_unique (hs i hi.le) hv
    exact he ▸ hv0
  · rintro ⟨s, hy, hs, hn⟩
    constructor
    · apply (Part.mem_map_iff _).mpr
      exact ⟨s y, hs y le_rfl, by simp [hy]⟩
    · intro i hi
      apply (Part.mem_map_iff _).mpr
      exact ⟨s i, hs i hi.le, by simp [hn i hi]⟩

end RealizationBoundaries
