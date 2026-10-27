import CoprimeKernelSurjectivity
import MatrixCocycleConjugacy

namespace Komorebi.StrongArtin.ChebotarevReadySpectralClass

open Komorebi.StrongArtin.CoprimeKernelSurjectivity
open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.MatrixCocycleConjugacy

noncomputable section

variable {k n G Γ C : Type*}
  [Field k] [Fintype n] [DecidableEq n]
  [Group G] [Group Γ] [Group C]

/-- **Chebotarev-ready spectral element.** Let the residual quotient have
prime-to-`p` order and let all splitting/cyclotomic constraints be packaged in
a finite `p`-group label. Every desired residual element can first be lifted
inside the label kernel. If a deeper common-kernel cocycle value is detected by
a projector commuting with that residual block, then one of two candidates has
all desired labels and nonzero detector value. -/
theorem exists_splitting_kernel_spectral_detector
    {p : ℕ} [Fact p.Prime]
    [Finite Γ] [Finite C]
    (hC : IsPGroup p C)
    (q : G →* Γ) (hq : Function.Surjective q)
    (cyc : G →* C)
    (hpΓ : ¬ p ∣ Nat.card Γ)
    (ρ : Γ →* (Matrix n n k)ˣ)
    (f : MatrixCocycleData (ρ.comp q))
    (γ₀ : Γ) (t : G)
    (htq : q t = 1) (htcyc : cyc t = 1)
    (P : Matrix n n k)
    (htdet : traceProbe P (f.value t) ≠ 0) :
    ∃ g : G,
      q g = γ₀ ∧
      cyc g = 1 ∧
      traceProbe P (f.value g) ≠ 0 := by
  obtain ⟨g, hqg, hcycg⟩ :=
    exists_lift_in_pGroup_kernel hC q cyc hq hpΓ γ₀
  by_cases hgdet : traceProbe P (f.value g) ≠ 0
  · exact ⟨g, hqg, hcycg, hgdet⟩
  · have hρt : (ρ.comp q) t = 1 := by simp [htq]
    have htg : f.value (t * g) = f.value t + f.value g := by
      rw [f.map_mul]
      simp [hρt]
    have htgd : traceProbe P (f.value (t * g)) ≠ 0 := by
      rw [htg]
      intro hzero
      have hsum :
          traceProbe P (f.value t + f.value g) =
            traceProbe P (f.value t) + traceProbe P (f.value g) := by
        simp [traceProbe, Matrix.mul_add, Matrix.trace_add]
      rw [hsum, not_ne_iff.mp hgdet, add_zero] at hzero
      exact htdet hzero
    refine ⟨t * g, ?_, ?_, htgd⟩
    · simp [htq, hqg]
    · simp [htcyc, hcycg]

/-- The selected detector is stable on the complete conjugacy class in the
finite affine quotient: after conjugating the residual block, transport the
projector by the same conjugating matrix. -/
theorem exists_chebotarev_ready_conjugacy_class
    {p : ℕ} [Fact p.Prime]
    [Finite Γ] [Finite C]
    (hC : IsPGroup p C)
    (q : G →* Γ) (hq : Function.Surjective q)
    (cyc : G →* C)
    (hpΓ : ¬ p ∣ Nat.card Γ)
    (ρ : Γ →* (Matrix n n k)ˣ)
    (f : MatrixCocycleData (ρ.comp q))
    (γ₀ : Γ) (t : G)
    (htq : q t = 1) (htcyc : cyc t = 1)
    (P : Matrix n n k)
    (hcomm : Commute P (ρ γ₀ : Matrix n n k))
    (htdet : traceProbe P (f.value t) ≠ 0) :
    ∃ g : G,
      q g = γ₀ ∧
      cyc g = 1 ∧
      traceProbe P (f.value g) ≠ 0 ∧
      ∀ h : G,
        q (h * g * h⁻¹) = q h * γ₀ * (q h)⁻¹ ∧
        cyc (h * g * h⁻¹) = 1 ∧
        traceProbe
          ((ρ (q h) : Matrix n n k) * P *
            (↑(ρ (q h))⁻¹ : Matrix n n k))
          (f.value (h * g * h⁻¹)) ≠ 0 := by
  obtain ⟨g, hqg, hcycg, hgdet⟩ :=
    exists_splitting_kernel_spectral_detector
      hC q hq cyc hpΓ ρ f γ₀ t htq htcyc P htdet
  refine ⟨g, hqg, hcycg, hgdet, ?_⟩
  intro h
  have hqmatg : (ρ.comp q) g = ρ γ₀ := by simp [hqg]
  have hcommg : Commute P ((ρ.comp q) g : Matrix n n k) := by
    simpa [hqmatg] using hcomm
  refine ⟨?_, ?_, ?_⟩
  · simp [hqg]
  · simp [hcycg]
  · simpa using MatrixCocycleData.traceProbe_value_conj_ne_zero
      (ρ.comp q) f h g P hcommg hgdet


/-- Indexed version used by relative spectral detection: first choose an actual
projector detecting the deeper cocycle value, then use the residual element
attached to that same projector as the desired Frobenius class. This removes
the mismatch between an arbitrary detector and an unrelated residual element. -/
theorem exists_indexed_chebotarev_ready_conjugacy_class
    {p : ℕ} [Fact p.Prime]
    {ι : Type*}
    [Finite Γ] [Finite C]
    (hC : IsPGroup p C)
    (q : G →* Γ) (hq : Function.Surjective q)
    (cyc : G →* C)
    (hpΓ : ¬ p ∣ Nat.card Γ)
    (ρ : Γ →* (Matrix n n k)ˣ)
    (f : MatrixCocycleData (ρ.comp q))
    (t : G) (htq : q t = 1) (htcyc : cyc t = 1)
    (base : ι → Γ) (P : ι → Matrix n n k)
    (hcomm : ∀ i : ι, Commute (P i) (ρ (base i) : Matrix n n k))
    (hdetect : ∃ i : ι, traceProbe (P i) (f.value t) ≠ 0) :
    ∃ i : ι, ∃ g : G,
      q g = base i ∧
      cyc g = 1 ∧
      traceProbe (P i) (f.value g) ≠ 0 ∧
      ∀ h : G,
        q (h * g * h⁻¹) = q h * base i * (q h)⁻¹ ∧
        cyc (h * g * h⁻¹) = 1 ∧
        traceProbe
          ((ρ (q h) : Matrix n n k) * P i *
            (↑(ρ (q h))⁻¹ : Matrix n n k))
          (f.value (h * g * h⁻¹)) ≠ 0 := by
  obtain ⟨i, hi⟩ := hdetect
  obtain ⟨g, hqg, hcycg, hgdet, hclass⟩ :=
    exists_chebotarev_ready_conjugacy_class
      hC q hq cyc hpΓ ρ f (base i) t htq htcyc (P i) (hcomm i) hi
  exact ⟨i, g, hqg, hcycg, hgdet, hclass⟩


end
end Komorebi.StrongArtin.ChebotarevReadySpectralClass

#print axioms Komorebi.StrongArtin.ChebotarevReadySpectralClass.exists_splitting_kernel_spectral_detector
#print axioms Komorebi.StrongArtin.ChebotarevReadySpectralClass.exists_chebotarev_ready_conjugacy_class
#print axioms Komorebi.StrongArtin.ChebotarevReadySpectralClass.exists_indexed_chebotarev_ready_conjugacy_class
