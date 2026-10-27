namespace Fixture
theorem linked (p q : Nat → Prop) (a b : Nat) (hp : p a) (hq : q b) (h : a = b) : ∃ n, p n ∧ q n := by
  subst b
  exact ⟨a, hp, hq⟩
end Fixture
