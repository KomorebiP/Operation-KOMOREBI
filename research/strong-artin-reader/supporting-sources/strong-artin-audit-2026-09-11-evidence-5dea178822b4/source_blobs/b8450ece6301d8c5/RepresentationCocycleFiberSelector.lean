import FiniteGroupCocycleAveraging

namespace Komorebi.StrongArtin.RepresentationCocycleFiberSelector

open Komorebi.StrongArtin.FiniteGroupCocycleAveraging

noncomputable section

variable {k G Γ V ι : Type*}
  [Field k] [Group G] [Group Γ]
  [AddCommGroup V] [Module k V]

/-- **Representation-valued two-candidate selector.** If `sigma` lies in the
kernel of a finite quotient, acts trivially on the cocycle coefficients, and a
probe detects `f sigma`, then either `g` or `sigma * g` has the same quotient
image as `g` and is detected by the same probe. -/
theorem exists_detecting_same_quotient_fiber
    (ρG : Representation k G V)
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (probe : Module.Dual k V)
    (q : G →* Γ)
    (sigma g : G)
    (hactionSigma : ρG sigma = 1)
    (hqSigma : q sigma = 1)
    (hdetect : probe (f sigma) ≠ 0) :
    ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      q gamma = q g ∧
      probe (f gamma) ≠ 0 := by
  by_cases hg : probe (f g) = 0
  · refine ⟨sigma * g, Or.inr rfl, ?_, ?_⟩
    · simp [hqSigma]
    · have hc := hf sigma g
      rw [hactionSigma] at hc
      simp only [Module.End.one_apply] at hc
      rw [hc, map_add, hg, add_zero]
      exact hdetect
  · exact ⟨g, Or.inl rfl, rfl, hg⟩

/-- Family form: joint separation chooses an actual probe and the two-candidate
selector chooses an element in the prescribed quotient fibre. -/
theorem exists_probe_and_detecting_same_quotient_fiber
    (ρG : Representation k G V)
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (probe : ι → Module.Dual k V)
    (hsep : ∀ x : V, x ≠ 0 → ∃ i : ι, probe i x ≠ 0)
    (q : G →* Γ)
    (sigma g : G)
    (hactionSigma : ρG sigma = 1)
    (hqSigma : q sigma = 1)
    (hsigma : f sigma ≠ 0) :
    ∃ i : ι, ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      q gamma = q g ∧
      probe i (f gamma) ≠ 0 := by
  obtain ⟨i, hi⟩ := hsep (f sigma) hsigma
  obtain ⟨gamma, hchoice, hq, hp⟩ :=
    exists_detecting_same_quotient_fiber
      ρG f hf (probe i) q sigma g hactionSigma hqSigma hi
  exact ⟨i, gamma, hchoice, hq, hp⟩

end

end Komorebi.StrongArtin.RepresentationCocycleFiberSelector
