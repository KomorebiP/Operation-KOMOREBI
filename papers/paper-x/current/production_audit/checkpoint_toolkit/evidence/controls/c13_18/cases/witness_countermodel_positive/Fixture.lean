namespace Fixture
theorem separated : (∃ n : Nat, n = 0) ∧ (∃ n : Nat, n = 1) ∧ ¬ (∃ n : Nat, n = 0 ∧ n = 1) := by
  refine ⟨⟨0,rfl⟩, ⟨1,rfl⟩, ?_⟩
  rintro ⟨n,h0,h1⟩
  exact Nat.zero_ne_one (h0.symm.trans h1)
end Fixture
