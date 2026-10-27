import KomorebiLSM.MarkovRecords

/-! Rolling windows are actual measurable pushforwards of full chronological
Markov records; their restart-at-entry identity is proved from kernel algebra. -/
set_option autoImplicit false
namespace Komorebi.LSM.MarkovStability
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MeasureTVCalculus
open scoped ENNReal

/-- Mapping the retained prefix of a composition product gives the corresponding
mapped-prefix joint law, with the conditional row pulled back along that map. -/
theorem map_compProd_left {A B C : Type*} [MeasurableSpace A] [MeasurableSpace B] [MeasurableSpace C]
    (ν : Measure A) [IsProbabilityMeasure ν] (f : A → B) (hf : Measurable f)
    (K : Kernel B C) [IsMarkovKernel K] :
    (ν ⊗ₘ K.comap f hf).map (Prod.map f id)=ν.map f ⊗ₘ K := by
  have hm : Measurable (Prod.map f (id : C → C)) :=
    (hf.comp measurable_fst).prodMk measurable_snd
  ext s hs
  let g : B × C → ℝ≥0∞ := s.indicator 1
  have hg : Measurable g := measurable_const.indicator hs
  have hrow : Measurable (fun b => ∫⁻ c,g (b,c)∂K b) := hg.lintegral_kernel_prod_right'
  rw [← lintegral_indicator_one (μ := (ν ⊗ₘ K.comap f hf).map (Prod.map f id)) hs,
    ← lintegral_indicator_one (μ := ν.map f ⊗ₘ K) hs]
  change (∫⁻ p,g p∂(ν ⊗ₘ K.comap f hf).map (Prod.map f id))=∫⁻ p,g p∂ν.map f ⊗ₘ K
  rw [lintegral_map hg hm]
  calc (∫⁻ a,g (Prod.map f id a)∂ν ⊗ₘ K.comap f hf)=
      ∫⁻ a,∫⁻ c,g (Prod.map f id (a,c))∂K.comap f hf a∂ν :=
        Measure.lintegral_compProd (hg.comp hm)
    _ = ∫⁻ b,∫⁻ c,g (b,c)∂K b∂ν.map f := by
      rw [lintegral_map hrow hf]
      rfl
    _ = ∫⁻ p,g p∂ν.map f ⊗ₘ K := (Measure.lintegral_compProd hg).symm

/-- Keep the entry state at time t and the following L states. -/
def recordSegment {X : Type*} (t : ℕ) : (L : ℕ) → Record X (t+L) → Record X L
  | 0,r => recordLast t r
  | L+1,r => (recordSegment t L r.1,r.2)

theorem recordSegment_measurable {X : Type*} [MeasurableSpace X] (t : ℕ) :
    (L : ℕ) → Measurable (recordSegment (X := X) t L)
  | 0 => recordLast_measurable t
  | L+1 => (recordSegment_measurable t L |>.comp measurable_fst).prodMk measurable_snd

theorem recordLast_segment {X : Type*} (t L : ℕ) (r : Record X (t+L)) :
    recordLast L (recordSegment t L r)=recordLast (t+L) r := by
  cases L <;> rfl

variable {X : Type*} [MeasurableSpace X]

/-- Restarting the Markov construction at its actual time-t marginal equals
extracting that segment from the actual full record law. -/
theorem recordLaw_segment (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (t : ℕ) :
    ∀ L,(recordLaw P ν0 (t+L)).map (recordSegment t L)=recordLaw P (marginal P ν0 t) L
  | 0 => by
    change (recordLaw P ν0 t).map (recordLast t)=marginal P ν0 t
    exact recordLaw_last P ν0 t
  | L+1 => by
    let f := recordSegment (X := X) t L
    let K := P.comap (recordLast L) (recordLast_measurable L)
    have hk : K.comap f (recordSegment_measurable t L)=
        P.comap (recordLast (t+L)) (recordLast_measurable (t+L)) := by
      ext r s hs
      change P (recordLast L (recordSegment t L r)) s=P (recordLast (t+L) r) s
      rw [recordLast_segment]
    change ((recordLaw P ν0 (t+L)) ⊗ₘ
      P.comap (recordLast (t+L)) (recordLast_measurable (t+L))).map (Prod.map f id)=
        recordLaw P (marginal P ν0 t) L ⊗ₘ K
    rw [← hk,map_compProd_left (recordLaw P ν0 (t+L)) f (recordSegment_measurable t L) K]
    have hi := recordLaw_segment P ν0 t L
    change ((recordLaw P ν0 (t+L)).map (recordSegment t L)) ⊗ₘ K=_
    rw [hi]

/-- The literal rolling-window law is a pushforward from the full record. Its
L transitions contain L+1 observations. -/
noncomputable def rollingWindowLaw (P : Kernel X X) (ν0 : Measure X) (t L : ℕ) : Measure (Record X L) :=
  (recordLaw P ν0 (t+L)).map (recordSegment t L)

instance rollingWindow_probability (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (t L : ℕ) :
    IsProbabilityMeasure (rollingWindowLaw P ν0 t L) := by unfold rollingWindowLaw; infer_instance

/-- Full registered rolling-window bound from the actual marginal entry error. -/
theorem rollingWindow_bound (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (Δ : ℝ) (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (t L : ℕ) :
    lawTV (rollingWindowLaw P ν0 t L) (rollingWindowLaw Q η0 t L)≤
      min 1 (lawTV (marginal P ν0 t) (marginal Q η0 t)+(L:ℝ)*Δ) := by
  simpa only [rollingWindowLaw,recordLaw_segment] using
    recordLaw_bound P Q Δ hΔ (marginal P ν0 t) (marginal Q η0 t) L

/-- Inserting the derived geometric entry bound gives an explicit window budget. -/
theorem rollingWindow_geometric_bound (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (ρ Δ : ℝ)
    (hρ0 : 0<ρ) (hρ1 : ρ≤1) (hmin : Minorized P ρ reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (t L : ℕ) :
    lawTV (rollingWindowLaw P ν0 t L) (rollingWindowLaw Q η0 t L)≤
      min 1 ((1-ρ)^t*lawTV ν0 η0+Δ*(1-(1-ρ)^t)/ρ+(L:ℝ)*Δ) := by
  apply (rollingWindow_bound P Q Δ hΔ ν0 η0 t L).trans
  apply min_le_min le_rfl
  exact add_le_add ((marginal_bound P Q reference ρ Δ hρ0 hρ1 hmin hΔ ν0 η0 t).trans
    (min_le_right _ _)) le_rfl

/-- The common-initial-law window budget is uniform in its start time. -/
theorem rollingWindow_same_initial_uniform (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (ρ Δ : ℝ)
    (hρ0 : 0<ρ) (hρ1 : ρ≤1) (hΔ0 : 0≤Δ) (hmin : Minorized P ρ reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (t L : ℕ) :
    lawTV (rollingWindowLaw P ν0 t L) (rollingWindowLaw Q ν0 t L)≤
      min 1 (Δ/ρ+(L:ℝ)*Δ) := by
  apply (rollingWindow_bound P Q Δ hΔ ν0 ν0 t L).trans
  apply min_le_min le_rfl
  exact add_le_add ((marginal_same_initial_uniform P Q reference ρ Δ hρ0 hρ1 hΔ0 hmin hΔ ν0 t).trans
    (min_le_right _ _)) le_rfl

/-- The source's reference confidence rectangle gives this actual all-time
one-marginal error bound, separate from any complete-record guarantee. -/
theorem reference_marginal_uniform (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference]
    (hmin : Minorized P (31/125) reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤(2437/90000:ℝ))
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (t : ℕ) :
    lawTV (marginal P ν0 t) (marginal Q ν0 t)≤(2437/22320:ℝ) := by
  have hb := (marginal_same_initial_uniform P Q reference (31/125) (2437/90000)
    (by norm_num) (by norm_num) (by norm_num) hmin hΔ ν0 t).trans (min_le_right _ _)
  norm_num at hb ⊢
  exact hb

end Komorebi.LSM.MarkovStability
