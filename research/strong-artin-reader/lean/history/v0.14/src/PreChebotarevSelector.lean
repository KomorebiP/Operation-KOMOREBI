import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree

namespace Komorebi.StrongArtin.PreChebotarevSelector

noncomputable section

universe u w r c

variable {k G : Type u} {R : Type r} {C : Type c}
  [Field k] [Group G] [Monoid R] [Monoid C]

/-- A one-cocycle adds along a left product whenever the first factor acts
trivially on the coefficient module. -/
theorem cocycle_mul_of_action_eq_one
    (A : Rep.{w} k G)
    (f : groupCohomology.cocycles₁ A)
    (σ g : G)
    (hσ : A.ρ σ = 1) :
    f (σ * g) = f σ + f g := by
  rw [(groupCohomology.mem_cocycles₁_iff f).1 f.2]
  rw [hσ]
  simp [add_comm]

/-- If a probe detects a cocycle on a residual-kernel element `σ`, then it
must detect either a prescribed element `g` or the adjusted element `σ * g`. -/
theorem probe_detects_base_or_adjusted
    (A : Rep.{w} k G)
    (f : groupCohomology.cocycles₁ A)
    (L : A →ₗ[k] k)
    (σ g : G)
    (hσ : A.ρ σ = 1)
    (hdetect : L (f σ) ≠ 0) :
    L (f g) ≠ 0 ∨ L (f (σ * g)) ≠ 0 := by
  by_cases hg : L (f g) = 0
  · right
    rw [cocycle_mul_of_action_eq_one A f σ g hσ]
    simp only [map_add, hg, add_zero]
    exact hdetect
  · exact Or.inl hg

/-- **Pre-Chebotarev two-point selector.** Suppose `σ` acts trivially on the
cocycle coefficients and is invisible to both a prescribed residual label and
a cyclotomic label. If a linear probe detects `f σ`, then one can choose either
`g` or `σ * g` so that the residual label is unchanged, the cyclotomic label
remains trivial, and the cocycle is detected by the chosen probe. -/
theorem exists_label_preserving_detected_element
    (A : Rep.{w} k G)
    (f : groupCohomology.cocycles₁ A)
    (L : A →ₗ[k] k)
    (res : G →* R)
    (cyc : G →* C)
    (σ g : G)
    (hact : A.ρ σ = 1)
    (hres : res σ = 1)
    (hcycσ : cyc σ = 1)
    (hcycg : cyc g = 1)
    (hdetect : L (f σ) ≠ 0) :
    ∃ γ : G,
      (γ = g ∨ γ = σ * g) ∧
      res γ = res g ∧
      cyc γ = 1 ∧
      L (f γ) ≠ 0 := by
  rcases probe_detects_base_or_adjusted A f L σ g hact hdetect with hg | hσg
  · exact ⟨g, Or.inl rfl, rfl, hcycg, hg⟩
  · refine ⟨σ * g, Or.inr rfl, ?_, ?_, hσg⟩
    · simp [hres]
    · simp [hcycσ, hcycg]

end
end Komorebi.StrongArtin.PreChebotarevSelector

#print axioms Komorebi.StrongArtin.PreChebotarevSelector.cocycle_mul_of_action_eq_one
#print axioms Komorebi.StrongArtin.PreChebotarevSelector.probe_detects_base_or_adjusted
#print axioms Komorebi.StrongArtin.PreChebotarevSelector.exists_label_preserving_detected_element
