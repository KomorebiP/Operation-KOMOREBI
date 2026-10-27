theorem bad (multiplicity : Nat) : multiplicity ≠ 0 := by
  intro h
  exact Nat.noConfusion h
