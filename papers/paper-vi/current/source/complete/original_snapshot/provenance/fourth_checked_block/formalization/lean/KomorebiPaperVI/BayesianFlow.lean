import KomorebiPaperVI.FiniteBayes
import Mathlib.Analysis.Calculus.Deriv.Inv

/-! Author: Komorebi P. The normalized exponential flow and its actual derivative. -/
namespace KomorebiPaperVI.BayesianFlow
open KomorebiPaperVI.FiniteBayes
open scoped BigOperators
variable {I : Type*} [Fintype I]

noncomputable def likelihood (g : I → ℝ) (t : ℝ) (i : I) : ℝ := Real.exp (t*g i)
noncomputable def flow (p g : I → ℝ) (t : ℝ) : I → ℝ := update p (likelihood g t)

theorem positive_evidence (p g : I → ℝ) (hp : IsProbability p) (t : ℝ) :
    0 < evidence p (likelihood g t) := by
  have hex : ∃ i, 0 < p i := by
    by_contra h
    push Not at h
    have he : mass p=0 := Finset.sum_eq_zero (fun i _ => le_antisymm (h i) (hp.1 i))
    linarith [hp.2]
  obtain ⟨i, hi⟩ := hex
  apply Finset.sum_pos'
  · intro j _; exact mul_nonneg (Real.exp_pos _).le (hp.1 j)
  · exact ⟨i, Finset.mem_univ i, mul_pos (Real.exp_pos _) hi⟩

theorem flow_probability (p g : I → ℝ) (hp : IsProbability p) (t : ℝ) :
    IsProbability (flow p g t) :=
  posterior_probability p _ hp (fun _ => (Real.exp_pos _).le) (positive_evidence p g hp t)

omit [Fintype I] in
theorem likelihood_add (g : I → ℝ) (s t : ℝ) :
    likelihood g (s+t) = fun i => likelihood g t i*likelihood g s i := by
  funext i
  dsimp [likelihood]
  rw [add_mul, Real.exp_add, mul_comm]

theorem flow_add (p g : I → ℝ) (hp : IsProbability p) (s t : ℝ) :
    flow p g (s+t) = flow (flow p g t) g s := by
  have hz := (positive_evidence p g hp (s+t)).ne'
  rw [likelihood_add] at hz
  dsimp only [flow]
  rw [likelihood_add]
  exact (posterior_composition p (likelihood g t) (likelihood g s)
    (positive_evidence p g hp t).ne' hz).symm

theorem flow_zero (p g : I → ℝ) (hp : IsProbability p) : flow p g 0=p := by
  funext i
  simp only [flow, update, likelihood, zero_mul, Real.exp_zero, one_mul, evidence]
  change p i/mass p=p i
  rw [hp.2, div_one]

omit [Fintype I] in
theorem likelihood_derivative (g : I → ℝ) (t : ℝ) (i : I) :
    HasDerivAt (fun u => likelihood g u i) (g i*likelihood g t i) t := by
  simpa [likelihood, mul_comm] using ((hasDerivAt_id t).mul_const (g i)).exp

theorem evidence_derivative (p g : I → ℝ) (t : ℝ) :
    HasDerivAt (fun u => evidence p (likelihood g u))
      (∑ i, g i*likelihood g t i*p i) t := by
  convert! HasDerivAt.sum (u := Finset.univ)
    (fun i _ => (likelihood_derivative g t i).mul_const (p i)) using 1
  ext u
  simp [evidence]

theorem flow_derivative (p g : I → ℝ) (hp : IsProbability p) (t : ℝ) (i : I) :
    HasDerivAt (fun u => flow p g u i)
      ((g i-(∑ j, g j*flow p g t j))*flow p g t i) t := by
  have hz := (positive_evidence p g hp t).ne'
  have hd := ((likelihood_derivative g t i).mul_const (p i)).div
    (evidence_derivative p g t) hz
  convert! hd using 1
  simp only [flow, update]
  simp only [← mul_div_assoc, ← Finset.sum_div]
  field_simp

end KomorebiPaperVI.BayesianFlow
