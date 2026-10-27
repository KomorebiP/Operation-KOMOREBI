import PaperX.ProfiniteSeparation
import PaperX.QuadraticCharacters

/-! Quotient coverage alone need not survive a finite deletion of sample indices.
The actual group is C2 with its discrete topology. Its nonidentity element occurs
only at index zero, while the identity occurs at every positive index. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.FiniteAvoidanceBoundary
open PaperX.CompletionExamples PaperX.QuadraticCharacters
open PaperX.ProfiniteSeparation

/-- A surjective family with only one occurrence of the nonidentity element. -/
def sample (n : ℕ) : C2 := if n = 0 then generator else 1

@[simp] theorem sample_zero : sample 0 = generator := by simp [sample]

@[simp] theorem sample_succ (n : ℕ) : sample (n + 1) = 1 := by simp [sample]

theorem sample_surjective : Function.Surjective sample := by
  intro g
  rcases c2_cases g with rfl | rfl
  · exact ⟨1, sample_succ 0⟩
  · exact ⟨0, sample_zero⟩

theorem sample_dense : DenseRange sample := sample_surjective.denseRange

theorem sample_conjugacy_dense :
    DenseRange (fun p : ℕ × C2 => p.2 * sample p.1 * p.2⁻¹) := by
  apply Function.Surjective.denseRange
  intro g
  obtain ⟨n, hn⟩ := sample_surjective g
  exact ⟨(n, 1), by simpa using hn⟩

/-- Even the original finite-quotient coverage premise holds. -/
theorem sample_quotient_coverage : QuotientCoverage sample := by
  intro H g
  obtain ⟨n, hn⟩ := sample_surjective g
  refine ⟨n, 1, ?_⟩
  simp [hn]

/-- The remaining indices after deleting the finite set `{0}`. -/
abbrev Remaining := {n : ℕ // n ∉ ({0} : Finset ℕ)}

def remainingSample (n : Remaining) : C2 := sample n.val

@[simp] theorem remainingSample_eq_one (n : Remaining) : remainingSample n = 1 := by
  have hn : n.val ≠ 0 := by simpa using n.property
  simp [remainingSample, sample, hn]

theorem remaining_conjugate_eq_one (p : Remaining × C2) :
    p.2 * remainingSample p.1 * p.2⁻¹ = 1 := by simp

theorem remaining_misses_generator :
    ∀ n : Remaining, remainingSample n ≠ generator := by
  intro n
  simpa using generator_ne_one.symm

theorem remaining_not_dense : ¬ DenseRange remainingSample := by
  intro hd
  obtain ⟨n, hn⟩ := denseRange_discrete.mp hd generator
  exact remaining_misses_generator n hn

theorem remaining_conjugacy_not_dense :
    ¬ DenseRange (fun p : Remaining × C2 =>
      p.2 * remainingSample p.1 * p.2⁻¹) := by
  intro hd
  obtain ⟨p, hp⟩ := denseRange_discrete.mp hd generator
  exact generator_ne_one (hp.symm.trans (remaining_conjugate_eq_one p))

theorem remaining_quotient_coverage_fails : ¬ QuotientCoverage remainingSample := by
  intro hc
  exact remaining_conjugacy_not_dense (dense_of_quotient_coverage remainingSample hc)

/-- These are actual unit-valued characters, with different generator values. -/
def signCharacter : C2 →* ℚˣ := ofRoot ⟨-1, by norm_num⟩

def trivialCharacter : C2 →* ℚˣ := 1

theorem characters_agree_after_deletion (n : Remaining) :
    signCharacter (remainingSample n) = trivialCharacter (remainingSample n) := by
  simp

theorem characters_differ : signCharacter ≠ trivialCharacter := by
  intro h
  have hv := congrArg (fun χ : C2 →* ℚˣ => (χ generator : ℚ)) h
  norm_num [signCharacter, trivialCharacter, ofRoot_generator] at hv

end PaperX.FiniteAvoidanceBoundary
