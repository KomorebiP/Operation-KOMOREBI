import KomorebiQCOS.FiniteGram
import KomorebiQCOS.Certificates
import Mathlib.MeasureTheory.Measure.Real
import Mathlib.MeasureTheory.Constructions.BorelSpace.Order
import Mathlib.MeasureTheory.Group.Arithmetic

/-!
# From exact forms to actual tail probabilities

The probability is the real value of an actual measure, not a supplied scalar.
Finite measure is required when passing extended measure inequalities to reals.
Measurability of every statistic used as a probability law is proved explicitly.
No Gaussian reduction or numerical integration is assumed by this module.
-/

namespace KomorebiQCOS
open MeasureTheory
open scoped BigOperators

variable {Ω I : Type*} [MeasurableSpace Ω]

/-- The closed upper-tail event. Atoms at the threshold are included. -/
def tailEvent (X : Ω → ℝ) (q : ℝ) : Set Ω := {ω | q ≤ X ω}

/-- Real-valued upper-tail mass. Theorems use a finite or probability measure. -/
noncomputable def tailProbability (μ : Measure Ω) (X : Ω → ℝ) (q : ℝ) : ℝ :=
  μ.real (tailEvent X q)

theorem measurableSet_tailEvent {X : Ω → ℝ} (hX : Measurable X) (q : ℝ) :
    MeasurableSet (tailEvent X q) :=
  measurableSet_le measurable_const hX

theorem tailProbability_nonneg (μ : Measure Ω) (X : Ω → ℝ) (q : ℝ) :
    0 ≤ tailProbability μ X q := measureReal_nonneg

theorem tailProbability_le_one (μ : Measure Ω) [IsProbabilityMeasure μ]
    (X : Ω → ℝ) (q : ℝ) : tailProbability μ X q ≤ 1 := measureReal_le_one

theorem tailProbability_congr_ae (μ : Measure Ω) {X Y : Ω → ℝ}
    (h : X =ᵐ[μ] Y) (q : ℝ) : tailProbability μ X q = tailProbability μ Y q := by
  apply measureReal_congr
  filter_upwards [h] with ω hω
  simp only [tailEvent, Set.mem_ofPred_eq, hω]

theorem tailProbability_mono (μ : Measure Ω) [IsFiniteMeasure μ]
    {X Y : Ω → ℝ} (h : ∀ ω, X ω ≤ Y ω) (q : ℝ) :
    tailProbability μ X q ≤ tailProbability μ Y q := by
  refine measureReal_mono ?_ (measure_ne_top μ _)
  intro ω hω
  exact hω.trans (h ω)

theorem tailProbability_mono_ae (μ : Measure Ω) [IsFiniteMeasure μ]
    {X Y : Ω → ℝ} (h : ∀ᵐ ω ∂μ, X ω ≤ Y ω) (q : ℝ) :
    tailProbability μ X q ≤ tailProbability μ Y q := by
  apply ENNReal.toReal_mono (measure_ne_top μ _)
  apply measure_mono_ae
  filter_upwards [h] with ω hω
  exact fun htail => htail.trans hω

theorem tailProbability_antitone_threshold (μ : Measure Ω) [IsFiniteMeasure μ]
    (X : Ω → ℝ) : Antitone (tailProbability μ X) := by
  intro q₁ q₂ hq
  refine measureReal_mono ?_ (measure_ne_top μ _)
  intro ω hω
  exact hq.trans hω

/-- A measurable statistic has exactly this tail under its pushforward law. -/
theorem tailProbability_eq_map (μ : Measure Ω) {X : Ω → ℝ}
    (hX : Measurable X) (q : ℝ) :
    tailProbability μ X q = (μ.map X).real (Set.Ici q) := by
  rw [map_measureReal_apply hX measurableSet_Ici]
  rfl

theorem measurable_weightedSquares (s : Finset I) (coeff : I → ℝ)
    (Z : Ω → I → ℝ) (hZ : ∀ i ∈ s, Measurable (fun ω => Z ω i)) :
    Measurable (fun ω => weightedSquares s coeff (Z ω)) := by
  unfold weightedSquares
  exact Finset.measurable_sum s (fun i hi => measurable_const.mul ((hZ i hi).pow_const 2))

/-- Actual measure monotonicity, strengthening the baseline event implication. -/
theorem weightedSquares_tailProbability_mono (μ : Measure Ω) [IsFiniteMeasure μ]
    (s : Finset I) (lower upper : I → ℝ) (Z : Ω → I → ℝ)
    (h : ∀ i ∈ s, lower i ≤ upper i) (q : ℝ) :
    tailProbability μ (fun ω => weightedSquares s lower (Z ω)) q ≤
      tailProbability μ (fun ω => weightedSquares s upper (Z ω)) q :=
  tailProbability_mono μ (fun ω => weightedSquares_mono s lower upper (Z ω) h) q

/-- Three forms are coupled using the same random coordinates. -/
theorem weightedSquares_tailProbability_enclosed (μ : Measure Ω) [IsFiniteMeasure μ]
    (s : Finset I) (lower coeff upper : I → ℝ) (Z : Ω → I → ℝ)
    (hl : ∀ i ∈ s, lower i ≤ coeff i) (hu : ∀ i ∈ s, coeff i ≤ upper i) (q : ℝ) :
    Enclosed (tailProbability μ (fun ω => weightedSquares s coeff (Z ω)) q)
      (tailProbability μ (fun ω => weightedSquares s lower (Z ω)) q)
      (tailProbability μ (fun ω => weightedSquares s upper (Z ω)) q) :=
  ⟨weightedSquares_tailProbability_mono μ s lower coeff Z hl q,
   weightedSquares_tailProbability_mono μ s coeff upper Z hu q⟩

/-- Endpoint solver enclosures compose with the actual stochastic bracket. -/
theorem weightedSquares_tailProbability_endpoint_enclosure
    (μ : Measure Ω) [IsFiniteMeasure μ] (s : Finset I)
    (lower coeff upper : I → ℝ) (Z : Ω → I → ℝ)
    (hl : ∀ i ∈ s, lower i ≤ coeff i) (hu : ∀ i ∈ s, coeff i ≤ upper i)
    (q L U : ℝ)
    (hL : L ≤ tailProbability μ (fun ω => weightedSquares s lower (Z ω)) q)
    (hU : tailProbability μ (fun ω => weightedSquares s upper (Z ω)) q ≤ U) :
    Enclosed (tailProbability μ (fun ω => weightedSquares s coeff (Z ω)) q) L U := by
  exact enclosed_widen
    (weightedSquares_tailProbability_enclosed μ s lower coeff upper Z hl hu q) hL hU

/-- The Gram and streamed-energy statistics induce the same tail for every input law. -/
theorem gram_tailProbability_eq_energy {Row Variant : Type*} [Fintype Row]
    (μ : Measure Ω) (s : Finset Variant) (A : Row → Variant → ℝ)
    (V : Ω → Row → ℝ) (q : ℝ) :
    tailProbability μ (fun ω => quadraticForm (gramEntry s A) (V ω)) q =
      tailProbability μ (fun ω => factorEnergy s A (V ω)) q := by
  have h : (fun ω => quadraticForm (gramEntry s A) (V ω)) =
      (fun ω => factorEnergy s A (V ω)) := by
    funext ω
    exact quadraticForm_gram_eq_energy s A (V ω)
  rw [h]

/-- A measurable input vector gives a measurable factor-energy statistic. -/
theorem measurable_factorEnergy {Row Variant : Type*} [Fintype Row]
    (s : Finset Variant) (A : Row → Variant → ℝ) (V : Ω → Row → ℝ)
    (hV : ∀ i, Measurable (fun ω => V ω i)) :
    Measurable (fun ω => factorEnergy s A (V ω)) := by
  unfold factorEnergy
  apply Finset.measurable_sum
  intro k _
  apply Measurable.pow_const
  exact Finset.measurable_sum Finset.univ (fun i _ => measurable_const.mul (hV i))

theorem measurable_quadraticForm_gram {Row Variant : Type*} [Fintype Row]
    (s : Finset Variant) (A : Row → Variant → ℝ) (V : Ω → Row → ℝ)
    (hV : ∀ i, Measurable (fun ω => V ω i)) :
    Measurable (fun ω => quadraticForm (gramEntry s A) (V ω)) := by
  simpa only [quadraticForm_gram_eq_energy] using measurable_factorEnergy s A V hV

/-- The identity is an equality of whole pushforward laws, not only one tail. -/
theorem gram_law_eq_energy {Row Variant : Type*} [Fintype Row]
    (μ : Measure Ω) (s : Finset Variant) (A : Row → Variant → ℝ)
    (V : Ω → Row → ℝ) :
    μ.map (fun ω => quadraticForm (gramEntry s A) (V ω)) =
      μ.map (fun ω => factorEnergy s A (V ω)) := by
  congr 1
  funext ω
  exact quadraticForm_gram_eq_energy s A (V ω)

end KomorebiQCOS
