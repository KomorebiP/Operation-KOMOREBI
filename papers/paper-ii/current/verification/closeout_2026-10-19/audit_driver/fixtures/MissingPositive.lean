theorem requires_positive (n : Nat) (h : 0 < n) : 0 < n := h
example : 0 < (0 : Nat) := requires_positive 0 (by decide)
