import KomorebiLSM.MarkovMarginals
import Mathlib.Probability.Kernel.Composition.CompMap
import Mathlib.Probability.Kernel.Composition.Lemmas

/-! Actual chronological Markov records and rolling-window laws. A record with
L transitions contains L+1 consecutive states, including its entry state. -/
set_option autoImplicit false
namespace Komorebi.LSM.MarkovStability
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MeasureTVCalculus
open scoped ENNReal
universe u

def Record (X : Type u) : ℕ → Type u
  | 0 => X
  | n+1 => Record X n × X

instance recordMeasurable {X : Type*} [MeasurableSpace X] :
    (n : ℕ) → MeasurableSpace (Record X n)
  | 0 => inferInstanceAs (MeasurableSpace X)
  | n+1 => by
    letI := recordMeasurable (X := X) n
    exact inferInstanceAs (MeasurableSpace (Record X n × X))
attribute [reducible] Record

def recordLast {X : Type*} : (n : ℕ) → Record X n → X
  | 0,x => x
  | _+1,x => x.2

theorem recordLast_measurable {X : Type*} [MeasurableSpace X] :
    (n : ℕ) → Measurable (recordLast (X := X) n)
  | 0 => measurable_id
  | _+1 => measurable_snd

variable {X : Type*} [MeasurableSpace X]

/-- Literal chronological extension by the row at the most recent state. -/
noncomputable def recordLaw (P : Kernel X X) (ν0 : Measure X) :
    (n : ℕ) → Measure (Record X n)
  | 0 => ν0
  | n+1 => recordLaw P ν0 n ⊗ₘ P.comap (recordLast n) (recordLast_measurable n)

theorem recordLaw_probability_aux (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] :
    (n : ℕ) → IsProbabilityMeasure (recordLaw P ν0 n)
  | 0 => inferInstanceAs (IsProbabilityMeasure ν0)
  | n+1 => by
    have := recordLaw_probability_aux P ν0 n
    exact inferInstanceAs (IsProbabilityMeasure
      (recordLaw P ν0 n ⊗ₘ P.comap (recordLast n) (recordLast_measurable n)))

instance recordLaw_probability (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (n : ℕ) :
    IsProbabilityMeasure (recordLaw P ν0 n) := recordLaw_probability_aux P ν0 n
instance recordLaw_zero_probability (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] :
    IsProbabilityMeasure (recordLaw P ν0 0) := recordLaw_probability_aux P ν0 0
instance recordLaw_succ_probability (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (n : ℕ) :
    IsProbabilityMeasure (recordLaw P ν0 (n+1)) := recordLaw_probability_aux P ν0 (n+1)

/-- The constructed joint laws have the actual prefix consistency property. -/
theorem recordLaw_consistent (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (n : ℕ) :
    (recordLaw P ν0 (n+1)).fst=recordLaw P ν0 n := Measure.fst_compProd _ _

/-- The last coordinate of the actual record is the iterated Markov marginal. -/
theorem recordLaw_last (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] :
    ∀ n,(recordLaw P ν0 n).map (recordLast n)=marginal P ν0 n
  | 0 => by change ν0.map id=ν0; exact Measure.map_id
  | n+1 => by
    change (recordLaw P ν0 n ⊗ₘ P.comap (recordLast n) (recordLast_measurable n)).snd=
      P ∘ₘ marginal P ν0 n
    rw [Measure.snd_compProd,← Kernel.comp_deterministic_eq_comap,
      ← Measure.comp_assoc,Measure.deterministic_comp_eq_map,recordLaw_last P ν0 n]

/-- Full records accumulate one uniform conditional error per transition. -/
theorem recordLaw_step (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (Δ : ℝ) (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (n : ℕ) :
    lawTV (recordLaw P ν0 (n+1)) (recordLaw Q η0 (n+1))≤
      lawTV (recordLaw P ν0 n) (recordLaw Q η0 n)+Δ := by
  let KP := P.comap (recordLast n) (recordLast_measurable n)
  let KQ := Q.comap (recordLast n) (recordLast_measurable n)
  have hcost := compProd_uniform_change (recordLaw P ν0 n) KP KQ Δ (fun r => hΔ (recordLast n r))
  have hcont := lawTV_compProd (recordLaw P ν0 n) (recordLaw Q η0 n) KQ
  have htri := lawTV_triangle (recordLaw P ν0 n ⊗ₘ KP)
    (recordLaw P ν0 n ⊗ₘ KQ) (recordLaw Q η0 n ⊗ₘ KQ)
  exact (htri.trans (add_le_add hcost hcont)).trans_eq (add_comm _ _)

/-- The finite-window telescoping bound is for literal joint record measures. -/
theorem recordLaw_bound (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (Δ : ℝ) (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (n : ℕ) :
    lawTV (recordLaw P ν0 n) (recordLaw Q η0 n)≤min 1 (lawTV ν0 η0+(n:ℝ)*Δ) := by
  apply le_min (lawTV_le_one _ _)
  induction n with
  | zero =>
    simp only [recordLaw,Nat.cast_zero,zero_mul,add_zero]
    exact le_rfl
  | succ n ih =>
    calc lawTV (recordLaw P ν0 (n+1)) (recordLaw Q η0 (n+1))≤
        lawTV (recordLaw P ν0 n) (recordLaw Q η0 n)+Δ := recordLaw_step P Q Δ hΔ ν0 η0 n
      _ ≤ (lawTV ν0 η0+(n:ℝ)*Δ)+Δ := add_le_add ih le_rfl
      _ = lawTV ν0 η0+((n+1:ℕ):ℝ)*Δ := by push_cast; ring

end Komorebi.LSM.MarkovStability
