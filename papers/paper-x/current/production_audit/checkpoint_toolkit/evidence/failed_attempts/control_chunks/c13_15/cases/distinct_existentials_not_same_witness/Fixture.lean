theorem bad (p q : Nat → Prop) (hp : ∃ n, p n) (hq : ∃ n, q n) : ∃ n, p n ∧ q n := by
  rcases hp with ⟨a, ha⟩
  rcases hq with ⟨b, hb⟩
  exact ⟨a, ha, hb⟩
