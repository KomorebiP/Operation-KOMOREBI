import BealLaneCertificate

/-! Exact counterexamples to losing candidate labels or paired coordinates. -/

namespace KomorebiBeal.Block47

/-- Separate tests can each pass after choosing a different label. -/
theorem each_test_has_candidate :
    ∀ test : Bool, ∃ candidate : Bool, candidate = test := by
  intro test
  exact ⟨test, rfl⟩

/-- No single label passes both tests. -/
theorem no_candidate_passes_every_test :
    ¬∃ candidate : Bool, ∀ test : Bool, candidate = test := by
  rintro ⟨candidate, h⟩
  have impossible : (false : Bool) = true := (h false).symm.trans (h true)
  cases impossible

/-- The two tests become incompatible only when their labels are intersected. -/
theorem correlated_tests_have_empty_intersection :
    survivors (fun (_ : Unit) (candidate test : Bool) => candidate = test)
      Set.univ () = ∅ := by
  apply Set.eq_empty_iff_forall_notMem.mpr
  intro candidate h
  exact no_candidate_passes_every_test ⟨candidate, fun test => h test (Set.mem_univ test)⟩

/-- Every coordinate separately occurs in the diagonal relation. -/
theorem diagonal_coordinate_projections_are_full :
    (∀ left : Bool, ∃ right : Bool, left = right) ∧
    (∀ right : Bool, ∃ left : Bool, left = right) := by
  exact ⟨fun left => ⟨left, rfl⟩, fun right => ⟨right, rfl⟩⟩

/-- Passing both marginal membership tests does not imply paired membership. -/
theorem diagonal_marginals_lose_correlation :
    (∃ right : Bool, false = right) ∧
    (∃ left : Bool, left = true) ∧ ¬((false : Bool) = true) := by
  exact ⟨⟨false, rfl⟩, ⟨true, rfl⟩, Bool.false_ne_true⟩

end KomorebiBeal.Block47
