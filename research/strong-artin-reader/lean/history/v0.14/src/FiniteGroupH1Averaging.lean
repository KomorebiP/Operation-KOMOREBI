import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree

namespace Komorebi.StrongArtin.FiniteGroupH1Averaging

noncomputable section

universe u

variable {k G : Type u} [Field k] [Group G] [Fintype G]

/-- Every one-cocycle of a finite group is a coboundary when the group order is
nonzero in the coefficient field. -/
theorem cocycle_mem_coboundaries_of_card_ne_zero
    (A : Rep.{u} k G)
    (hcard : (Fintype.card G : k) ≠ 0)
    (f : groupCohomology.cocycles₁ A) :
    (f : G → A) ∈ groupCohomology.coboundaries₁ A := by
  let S : A := ∑ h : G, f h
  let n : k := Fintype.card G
  let x : A := -(n⁻¹) • S
  refine ⟨x, ?_⟩
  funext g
  have hcoc := (groupCohomology.mem_cocycles₁_iff f).1 f.2
  have hperm : (∑ h : G, f (g * h)) = ∑ h : G, f h := by
    exact Fintype.sum_bijective (g * ·) (Group.mulLeft_bijective g)
      (fun h => f (g * h)) (fun h => f h) (fun _ => rfl)
  have hsum : (∑ h : G, f (g * h)) =
      A.ρ g S + (Fintype.card G : k) • f g := by
    simp_rw [hcoc g]
    rw [Finset.sum_add_distrib, map_sum]
    simp [Nat.cast_smul_eq_nsmul]
  have hrel : A.ρ g S + n • f g = S := by
    rw [← hsum]
    simpa [S, n] using hperm
  have hdiff : S - A.ρ g S = n • f g := by
    calc
      S - A.ρ g S = (A.ρ g S + n • f g) - A.ρ g S :=
        congrArg (fun z : A => z - A.ρ g S) hrel.symm
      _ = n • f g := by abel
  change A.ρ g x - x = f g
  calc
    A.ρ g x - x = n⁻¹ • (S - A.ρ g S) := by
      simp [x, map_smul]
      module
    _ = n⁻¹ • (n • f g) := by rw [hdiff]
    _ = f g := by
      rw [smul_smul]
      simp [n, hcard]

/-- Hence the first cohomology group is subsingleton in the prime-to-
characteristic finite-group regime. -/
theorem H1_subsingleton_of_card_ne_zero
    (A : Rep.{u} k G)
    (hcard : (Fintype.card G : k) ≠ 0) :
    Subsingleton (groupCohomology.H1 A) := by
  have hzero : ∀ a : groupCohomology.H1 A, a = 0 := by
    intro a
    refine groupCohomology.H1_induction_on (C := fun z => z = 0) a ?_
    intro x
    exact (groupCohomology.H1π_eq_zero_iff x).2
      (cocycle_mem_coboundaries_of_card_ne_zero A hcard x)
  exact ⟨fun a b => (hzero a).trans (hzero b).symm⟩

end
end Komorebi.StrongArtin.FiniteGroupH1Averaging

#print axioms Komorebi.StrongArtin.FiniteGroupH1Averaging.cocycle_mem_coboundaries_of_card_ne_zero
#print axioms Komorebi.StrongArtin.FiniteGroupH1Averaging.H1_subsingleton_of_card_ne_zero
