import RealizationBoundaries.ComputablePresentations

/-!
# All group operations in a genuinely coded oracle copy

Inversion is not silently omitted from the computable-copy contract. Given the
proved bijective Nat naming and actual computable addition, search for a right
inverse terminates and returns the literal inverse under the naming map.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries
namespace OracleGroupCopy
variable {X : ℕ → Bool} {H : Type*} [AddGroup H]

/-- Zero is a finite natural constant, hence requires no extra oracle. -/
theorem zero_computable (c : OracleGroupCopy X H) :
    OracleComputable X (fun _ => c.zero) := OracleComputable.const c.zero

/-- Ordinary equality of natural names is the actual equality of named elements. -/
theorem names_equal_iff (c : OracleGroupCopy X H) (i j : ℕ) :
    c.names i = c.names j ↔ i = j := c.names.injective.eq_iff

/-- A zero-valued test for a candidate right inverse. -/
def inverseTest (c : OracleGroupCopy X H) (k : ℕ) : ℕ :=
  if c.add k.unpair.1 k.unpair.2 = c.zero then 0 else 1

theorem inverseTest_correct (c : OracleGroupCopy X H) (n t : ℕ) :
    c.inverseTest (Nat.pair n t) = 0 ↔ c.names t = -c.names n := by
  have he : c.add n t = c.zero ↔ c.names n + c.names t = 0 := by
    rw [← c.add_spec, ← c.zero_spec, c.names.injective.eq_iff]
  simp only [inverseTest, Nat.unpair_pair, ite_eq_left_iff, one_ne_zero,
    imp_false, not_not]
  exact he.trans ⟨eq_neg_of_add_eq_zero_right, fun h => by rw [h, add_neg_cancel]⟩

theorem inverseTest_computable (c : OracleGroupCopy X H) :
    OracleComputable X c.inverseTest := by
  have ht : Computable (fun m : ℕ => if m = c.zero then 0 else 1) :=
    (Primrec.ite (Primrec.eq.comp Primrec.id (Primrec.const c.zero))
      (Primrec.const 0) (Primrec.const 1)).to_comp
  exact (OracleComputable.of_computable ht).comp c.add_computable

/-- Termination is justified by actual group inversion and surjectivity of the
names, without assuming that the inverse naming function is computable. -/
theorem inverseTest_total (c : OracleGroupCopy X H) (n : ℕ) :
    ∃ t, c.inverseTest (Nat.pair n t) = 0 := by
  refine ⟨c.names.symm (-c.names n), (c.inverseTest_correct n _).mpr ?_⟩
  exact c.names.apply_symm_apply _

/-- The actual terminating inverse algorithm on Nat names. -/
def inverse (c : OracleGroupCopy X H) (n : ℕ) : ℕ :=
  Nat.find (c.inverseTest_total n)

theorem inverse_spec (c : OracleGroupCopy X H) (n : ℕ) :
    c.names (c.inverse n) = -c.names n :=
  (c.inverseTest_correct n _).mp (Nat.find_spec (c.inverseTest_total n))

/-- Native relative inversion follows from native addition by proved total
minimization; it is not an additional assumption on the copy. -/
theorem inverse_computable (c : OracleGroupCopy X H) :
    OracleComputable X c.inverse :=
  OracleComputable.find c.inverseTest_computable c.inverseTest_total

@[simp] theorem inverse_inverse (c : OracleGroupCopy X H) (n : ℕ) :
    c.inverse (c.inverse n) = n := by
  apply c.names.injective
  rw [c.inverse_spec, c.inverse_spec, neg_neg]

@[simp] theorem inverse_zero (c : OracleGroupCopy X H) : c.inverse c.zero = c.zero := by
  apply c.names.injective
  rw [c.inverse_spec, c.zero_spec, neg_zero]

theorem add_inverse (c : OracleGroupCopy X H) (n : ℕ) :
    c.add n (c.inverse n) = c.zero := by
  apply c.names.injective
  rw [c.add_spec, c.inverse_spec, c.zero_spec, add_neg_cancel]

theorem inverse_add (c : OracleGroupCopy X H) (n : ℕ) :
    c.add (c.inverse n) n = c.zero := by
  apply c.names.injective
  rw [c.add_spec, c.inverse_spec, c.zero_spec, neg_add_cancel]

/-- Subtraction is then also a genuine relative computation on names. -/
def subtract (c : OracleGroupCopy X H) (i j : ℕ) : ℕ := c.add i (c.inverse j)

theorem subtract_spec (c : OracleGroupCopy X H) (i j : ℕ) :
    c.names (c.subtract i j) = c.names i - c.names j := by
  rw [subtract, c.add_spec, c.inverse_spec, sub_eq_add_neg]

theorem subtract_computable (c : OracleGroupCopy X H) :
    OracleComputable X (fun k => c.subtract k.unpair.1 k.unpair.2) :=
  c.add_computable.comp
    (OracleComputable.left.pair (c.inverse_computable.comp OracleComputable.right))
    |>.of_eq (fun k => by simp [subtract])

end OracleGroupCopy
end RealizationBoundaries
