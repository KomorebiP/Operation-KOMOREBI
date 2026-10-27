import KomorebiLSM.MarkovMinorization
import KomorebiLSM.MarkovMarginals
import Mathlib.Probability.Distributions.Bernoulli
import Mathlib.Probability.Moments.SubGaussian
import Mathlib.Probability.Independence.Basic
import Mathlib.MeasureTheory.Constructions.Pi

/-! Actual nondegenerate Bernoulli full-record laws separate in total variation,
even though every one-time marginal has a fixed small gap and the constant
transition kernels share a strictly positive minorization. -/
set_option autoImplicit false
namespace Komorebi.LSM.MarkovStability.BernoulliSeparation
open MeasureTheory ProbabilityTheory Matrix SequentialLowerCertificate MeasureTVCalculus Filter
open scoped BigOperators ENNReal NNReal Topology

/-- The actual two-point law, with true meaning value one. -/
noncomputable def coin (p : unitInterval) : Measure Bool := bernoulliMeasure true false p
instance coin_probability (p : unitInterval) : IsProbabilityMeasure (coin p) := by
  unfold coin
  infer_instance

def bit (b : Bool) : ℝ := if b then 1 else 0

theorem bit_measurable : Measurable bit := measurable_of_countable _
theorem bit_mem_unit (b : Bool) : bit b∈Set.Icc (0:ℝ) 1 := by cases b <;> norm_num [bit]

theorem integral_bit (p : unitInterval) : (∫ b,bit b∂coin p)=(p:ℝ) := by
  rw [coin,integral_bernoulliMeasure]
  simp [bit,smul_eq_mul]

/-- A complete record of n transitions contains n+1 independent observations. -/
noncomputable def iidLaw (p : unitInterval) (n : ℕ) : Measure (Fin (n+1) → Bool) :=
  Measure.pi (fun _ => coin p)
instance iidLaw_probability (p : unitInterval) (n : ℕ) : IsProbabilityMeasure (iidLaw p n) := by
  unfold iidLaw
  infer_instance

/-- Every actual coordinate marginal equals the declared Bernoulli law. -/
theorem iidLaw_coordinate (p : unitInterval) (n : ℕ) (i : Fin (n+1)) :
    (iidLaw p n).map (fun w => w i)=coin p :=
  (measurePreserving_eval (fun _ : Fin (n+1) => coin p) i).map_eq

theorem coordinate_mean (p : unitInterval) (n : ℕ) (i : Fin (n+1)) :
    (∫ w,bit (w i)∂iidLaw p n)=(p:ℝ) := by
  rw [← integral_map (measurable_pi_apply i).aemeasurable bit_measurable.aestronglyMeasurable,
    iidLaw_coordinate,integral_bit]

/-- Independence is derived from the literal finite product measure. -/
theorem centered_coordinates_independent (p : unitInterval) (n : ℕ) :
    iIndepFun (fun i (w : Fin (n+1) → Bool) => bit (w i)-(p:ℝ)) (iidLaw p n) := by
  exact iIndepFun_pi (μ := fun _ : Fin (n+1) => coin p)
    (X := fun _ b => bit b-(p:ℝ)) (fun _ => (bit_measurable.sub_const _).aemeasurable)

/-- Ordinary bounded-variable Hoeffding applies to the actual coordinate mean. -/
theorem centered_coordinate_subgaussian (p : unitInterval) (n : ℕ) (i : Fin (n+1)) :
    HasSubgaussianMGF (fun w => bit (w i)-(p:ℝ)) (1/4) (iidLaw p n) := by
  have hm : Measurable (fun w : Fin (n+1) → Bool => bit (w i)) :=
    bit_measurable.comp (measurable_pi_apply i)
  have hb : ∀ᵐ w∂iidLaw p n,bit (w i)∈Set.Icc (0:ℝ) 1 :=
    ae_of_all _ (fun w => bit_mem_unit (w i))
  have h := hasSubgaussianMGF_of_mem_Icc hm.aemeasurable hb
  rw [coordinate_mean p n i] at h
  convert h using 1; norm_num

noncomputable def sumBits (n : ℕ) (w : Fin (n+1) → Bool) : ℝ := ∑ i,bit (w i)
noncomputable def centeredSum (p : unitInterval) (n : ℕ) (w : Fin (n+1) → Bool) : ℝ :=
  ∑ i,(bit (w i)-(p:ℝ))

theorem centeredSum_eq (p : unitInterval) (n : ℕ) (w : Fin (n+1) → Bool) :
    centeredSum p n w=sumBits n w-((n:ℝ)+1)*(p:ℝ) := by
  simp [centeredSum,sumBits,Finset.sum_sub_distrib]

theorem centeredSum_subgaussian (p : unitInterval) (n : ℕ) :
    HasSubgaussianMGF (centeredSum p n) (((n:NNReal)+1)/4) (iidLaw p n) := by
  unfold centeredSum
  have h := HasSubgaussianMGF.sum_of_iIndepFun (centered_coordinates_independent p n)
    (s := Finset.univ) (c := fun _ => (1/4:NNReal))
    (fun i _ => centered_coordinate_subgaussian p n i)
  simpa [div_eq_mul_inv] using h

/-- Exponential error bound for a fixed positive empirical-mean gap. -/
theorem centered_upper_tail (p : unitInterval) (n : ℕ) (d : ℝ) (hd : 0≤d) :
    (iidLaw p n).real {w | (((n:ℝ)+1)*d)≤centeredSum p n w}≤
      Real.exp (-2*((n:ℝ)+1)*d^2) := by
  have h := (centeredSum_subgaussian p n).measure_ge_le
    (mul_nonneg (by positivity : 0≤(n:ℝ)+1) hd)
  have hn : (n:ℝ)+1≠0 := ne_of_gt (by positivity)
  push_cast at h
  have he : -((((n:ℝ)+1)*d)^2)/(2*(((n:ℝ)+1)/4)) = -2*((n:ℝ)+1)*d^2 := by
    field_simp [hn]
    ring
  simpa only [he] using h

/-- The opposite tail uses the actual negative centered sum. -/
theorem centered_lower_tail (p : unitInterval) (n : ℕ) (d : ℝ) (hd : 0≤d) :
    (iidLaw p n).real {w | (((n:ℝ)+1)*d)≤-centeredSum p n w}≤
      Real.exp (-2*((n:ℝ)+1)*d^2) := by
  have h := (centeredSum_subgaussian p n).neg.measure_ge_le
    (mul_nonneg (by positivity : 0≤(n:ℝ)+1) hd)
  have hn : (n:ℝ)+1≠0 := ne_of_gt (by positivity)
  push_cast at h
  have he : -((((n:ℝ)+1)*d)^2)/(2*(((n:ℝ)+1)/4)) = -2*((n:ℝ)+1)*d^2 := by
    field_simp [hn]
    ring
  simpa only [he,Pi.neg_apply] using h

noncomputable def empiricalMean (n : ℕ) (w : Fin (n+1) → Bool) : ℝ :=
  sumBits n w/((n:ℝ)+1)

/-- The actual midpoint empirical-mean test of the source. -/
def aboveMidpoint (p q : unitInterval) (n : ℕ) : Set (Fin (n+1) → Bool) :=
  {w | ((n:ℝ)+1)*((p:ℝ)+(q:ℝ))/2≤sumBits n w}

theorem aboveMidpoint_measurable (p q : unitInterval) (n : ℕ) :
    MeasurableSet (aboveMidpoint p q n) := by
  apply measurableSet_le measurable_const
  exact Finset.measurable_sum _ (fun i _ => bit_measurable.comp (measurable_pi_apply i))

theorem aboveMidpoint_iff (p q : unitInterval) (n : ℕ) (w : Fin (n+1) → Bool) :
    w∈aboveMidpoint p q n ↔ ((p:ℝ)+(q:ℝ))/2≤empiricalMean n w := by
  unfold aboveMidpoint empiricalMean
  rw [le_div_iff₀ (by positivity : 0<(n:ℝ)+1)]
  simp only [Set.mem_ofPred_eq]
  constructor <;> intro h <;> nlinarith

noncomputable def separationError (p q : unitInterval) (n : ℕ) : ℝ :=
  Real.exp (-2*((n:ℝ)+1)*(((q:ℝ)-(p:ℝ))/2)^2)

/-- Both empirical-mean classification errors have a proved exponential bound. -/
theorem midpoint_error_bounds (p q : unitInterval) (hpq : (p:ℝ)<(q:ℝ)) (n : ℕ) :
    (iidLaw p n).real (aboveMidpoint p q n)≤separationError p q n ∧
      (iidLaw q n).real (aboveMidpoint p q n)ᶜ≤separationError p q n := by
  let d : ℝ := ((q:ℝ)-(p:ℝ))/2
  have hd : 0≤d := (div_pos (sub_pos.mpr hpq) (by norm_num)).le
  constructor
  · have hs : aboveMidpoint p q n⊆{w | ((n:ℝ)+1)*d≤centeredSum p n w} := by
      intro w hw
      change ((n:ℝ)+1)*((p:ℝ)+(q:ℝ))/2≤sumBits n w at hw
      change ((n:ℝ)+1)*d≤centeredSum p n w
      rw [centeredSum_eq]
      dsimp [d]
      nlinarith
    exact (ENNReal.toReal_mono (measure_ne_top _ _) (measure_mono hs)).trans
      (centered_upper_tail p n d hd)
  · have hs : (aboveMidpoint p q n)ᶜ⊆{w | ((n:ℝ)+1)*d≤-centeredSum q n w} := by
      intro w hw
      have hl : sumBits n w<((n:ℝ)+1)*((p:ℝ)+(q:ℝ))/2 := lt_of_not_ge hw
      change ((n:ℝ)+1)*d≤-centeredSum q n w
      rw [centeredSum_eq]
      dsimp [d]
      nlinarith
    exact (ENNReal.toReal_mono (measure_ne_top _ _) (measure_mono hs)).trans
      (centered_lower_tail q n d hd)

/-- A literal measurable event gives a lower bound for the actual probability
convention of total variation. -/
theorem event_gap_le {X : Type*} [MeasurableSpace X] (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] (E : Set X) (hE : MeasurableSet E) :
    Q.real E-P.real E≤lawTV P Q := by
  let f : X → ℝ := E.indicator (fun _ => 1)
  have hf : Measurable f := measurable_const.indicator hE
  have h0 : ∀ x,0≤f x := fun x => by by_cases hx : x∈E <;> simp [f,hx]
  have h1 : ∀ x,f x≤1 := fun x => by by_cases hx : x∈E <;> simp [f,hx]
  have h := bounded_test_integral_le_tv P Q f hf h0 h1
  have hi (ν : Measure X) : (∫ x,f x∂ν)=ν.real E := by simp [f,integral_indicator hE]
  rw [hi P,hi Q,abs_sub_comm] at h
  exact (le_abs_self _).trans h

/-- The midpoint test proves actual full-record TV approaches its maximal value. -/
theorem iidLaw_tv_lower (p q : unitInterval) (hpq : (p:ℝ)<(q:ℝ)) (n : ℕ) :
    1-2*separationError p q n≤lawTV (iidLaw p n) (iidLaw q n) := by
  have he := midpoint_error_bounds p q hpq n
  have hq := he.2
  rw [measureReal_compl (aboveMidpoint_measurable p q n)] at hq
  simp only [probReal_univ] at hq
  have hgap := event_gap_le (iidLaw p n) (iidLaw q n) (aboveMidpoint p q n)
    (aboveMidpoint_measurable p q n)
  linarith [he.1]

/-- The explicit record measures are consistent under dropping the last observation. -/
theorem iidLaw_prefix (p : unitInterval) (n : ℕ) :
    (iidLaw p (n+1)).map (fun w (i : Fin (n+1)) => w i.castSucc)=iidLaw p n := by
  have hfull : iIndepFun (fun j (w : Fin (n+1+1) → Bool) => w j) (iidLaw p (n+1)) :=
    iIndepFun_pi (μ := fun _ : Fin (n+1+1) => coin p)
      (X := fun _ b => b) (fun _ => measurable_id.aemeasurable)
  have hsmall := hfull.precomp (Fin.castSucc_injective (n+1))
  have hmap := hsmall.map_fun_eq_pi_map
    (fun i => (measurable_pi_apply i.castSucc).aemeasurable)
  calc
    _ = Measure.pi (fun i : Fin (n+1) =>
        (iidLaw p (n+1)).map (fun w => w i.castSucc)) := hmap
    _ = iidLaw p n := by simp only [iidLaw_coordinate]; rfl

/-- Actual total variation tends to one; the limit is not assumed from a
numerical or asymptotic proxy. -/
theorem iidLaw_tv_tendsto_one (p q : unitInterval) (hpq : (p:ℝ)<(q:ℝ)) :
    Tendsto (fun n => lawTV (iidLaw p n) (iidLaw q n)) atTop (𝓝 1) := by
  let d : ℝ := ((q:ℝ)-(p:ℝ))/2
  have hd : 0<d := div_pos (sub_pos.mpr hpq) (by norm_num)
  have hN : Tendsto (fun n : ℕ => (n:ℝ)+1) atTop atTop := by
    exact tendsto_atTop_add_const_right atTop 1 (tendsto_natCast_atTop_atTop (R := ℝ))
  have hc : -2*d^2<0 := mul_neg_of_neg_of_pos (by norm_num) (sq_pos_of_pos hd)
  have he : Tendsto (separationError p q) atTop (𝓝 0) := by
    have ht := Real.tendsto_exp_atBot.comp (hN.const_mul_atTop_of_neg hc)
    convert ht using 1
    funext n
    unfold separationError
    congr 1
    dsimp [d]
    ring
  have hl : Tendsto (fun n => 1-2*separationError p q n) atTop (𝓝 1) := by
    simpa using tendsto_const_nhds.sub (he.const_mul 2)
  exact tendsto_of_tendsto_of_tendsto_of_le_of_le hl tendsto_const_nhds
    (iidLaw_tv_lower p q hpq) (fun n => lawTV_le_one (iidLaw p n) (iidLaw q n))

/-- The exact one-time distance is the parameter gap. -/
theorem coin_tv (p q : unitInterval) : lawTV (coin p) (coin q)=|(p:ℝ)-(q:ℝ)| := by
  apply le_antisymm
  · apply lawTV_le_of_bounded_tests
    intro f hf h0 h1
    have hi (r : unitInterval) : (∫ b,f b∂coin r)=
        (r:ℝ)*f true+(1-(r:ℝ))*f false := by
      rw [coin,integral_bernoulliMeasure]
      simp [smul_eq_mul]
    rw [hi p,hi q]
    have he : (p:ℝ)*f true+(1-(p:ℝ))*f false-((q:ℝ)*f true+(1-(q:ℝ))*f false)=
        ((p:ℝ)-(q:ℝ))*(f true-f false) := by ring
    rw [he,abs_mul]
    apply mul_le_of_le_one_right (abs_nonneg _)
    exact abs_le.2 ⟨by linarith [h0 true,h1 false],by linarith [h1 true,h0 false]⟩
  · have h := bounded_test_integral_le_tv (coin p) (coin q) bit bit_measurable
      (fun b => (bit_mem_unit b).1) (fun b => (bit_mem_unit b).2)
    simpa only [integral_bit] using h

noncomputable def coinKernel (p : unitInterval) : Kernel Bool Bool := Kernel.const Bool (coin p)
instance coinKernel_markov (p : unitInterval) : IsMarkovKernel (coinKernel p) := by
  unfold coinKernel
  infer_instance

theorem coinKernel_comp (p : unitInterval) (ν : Measure Bool) [IsProbabilityMeasure ν] :
    coinKernel p ∘ₘ ν=coin p := by
  rw [coinKernel,Measure.const_comp,measure_univ,one_smul]

theorem marginal_coin (p : unitInterval) (n : ℕ) :
    marginal (coinKernel p) (coin p) n=coin p := by
  induction n with
  | zero => rfl
  | succ n ih => rw [marginal,ih,coinKernel_comp]

/-- A positive amount of the false atom is an actual common minorization. -/
theorem coinKernel_minorized (p : unitInterval) (ρ : ℝ) (hρ : ρ≤1-(p:ℝ)) :
    Minorized (coinKernel p) ρ (Measure.dirac false) := by
  intro x
  change ENNReal.ofReal ρ • Measure.dirac false≤coin p
  have hfalse : (coin p).real {false}=1-(p:ℝ) := by
    exact bernoulliMeasure_real_apply_of_notMem_of_mem p (measurableSet_singleton false)
      (by simp) (by simp)
  have hcost : ENNReal.ofReal ρ≤coin p {false} := by
    have h := ENNReal.ofReal_le_ofReal hρ
    rwa [← hfalse,Measure.real,ENNReal.ofReal_toReal (measure_ne_top _ _)] at h
  intro E
  have hE : MeasurableSet E := (Set.toFinite E).countable.measurableSet
  by_cases hf : false∈E
  · simpa [Measure.smul_apply,Measure.dirac_apply' _ hE,hf,smul_eq_mul] using
      hcost.trans (measure_mono (Set.singleton_subset_iff.2 hf))
  · simp [Measure.smul_apply,Measure.dirac_apply' _ hE,hf]

/-- The source's counterexample uses two strictly interior Bernoulli
parameters, not a degenerate zero-probability law. -/
theorem interior_bernoulli_record_separation (p q : unitInterval)
    (hp : 0<(p:ℝ)) (hpq : (p:ℝ)<(q:ℝ)) (hq : (q:ℝ)<1) :
    0<1-(q:ℝ) ∧ 1-(q:ℝ)≤1 ∧
    Minorized (coinKernel p) (1-(q:ℝ)) (Measure.dirac false) ∧
    Minorized (coinKernel q) (1-(q:ℝ)) (Measure.dirac false) ∧
    (∀ n,lawTV (marginal (coinKernel p) (coin p) n)
      (marginal (coinKernel q) (coin q) n)=(q:ℝ)-(p:ℝ)) ∧
    (∀ x,lawTV (coinKernel p x) (coinKernel q x)=(q:ℝ)-(p:ℝ)) ∧
    Tendsto (fun n => lawTV (iidLaw p n) (iidLaw q n)) atTop (𝓝 1) := by
  have hgap : |(p:ℝ)-(q:ℝ)|=(q:ℝ)-(p:ℝ) := by rw [abs_of_neg (sub_neg.mpr hpq)]; ring
  refine ⟨by linarith,by linarith,coinKernel_minorized p _ (by linarith),
    coinKernel_minorized q _ le_rfl,?_,?_,iidLaw_tv_tendsto_one p q hpq⟩
  · intro n
    simpa only [marginal_coin] using (coin_tv p q).trans hgap
  · intro x
    change lawTV (coin p) (coin q)=(q:ℝ)-(p:ℝ)
    rw [coin_tv,hgap]

noncomputable def halfParameter : unitInterval := ⟨1/2,by constructor <;> norm_num⟩
noncomputable def closeParameter (ε : ℝ) (hε : 0<ε) (hε1 : ε<1) : unitInterval :=
  ⟨1/2+ε/4,by constructor <;> linarith⟩

/-- The marginal gap can be made arbitrarily small while keeping the same
strictly positive minorization one quarter and full-record TV limit one. -/
theorem arbitrarily_small_marginal_gap (ε : ℝ) (hε : 0<ε) (hε1 : ε<1) :
    let p := halfParameter
    let q := closeParameter ε hε hε1
    (0<(p:ℝ) ∧ (p:ℝ)<(q:ℝ) ∧ (q:ℝ)<1) ∧
    (0<ε/4 ∧ ε/4<ε) ∧
    Minorized (coinKernel p) (1/4) (Measure.dirac false) ∧
    Minorized (coinKernel q) (1/4) (Measure.dirac false) ∧
    (∀ n,lawTV (marginal (coinKernel p) (coin p) n)
      (marginal (coinKernel q) (coin q) n)=ε/4) ∧
    Tendsto (fun n => lawTV (iidLaw p n) (iidLaw q n)) atTop (𝓝 1) := by
  dsimp only
  have hp : 0<(halfParameter:ℝ) := by norm_num [halfParameter]
  have hpq : (halfParameter:ℝ)<(closeParameter ε hε hε1:ℝ) := by
    dsimp [halfParameter,closeParameter]
    linarith
  have hq : (closeParameter ε hε hε1:ℝ)<1 := by dsimp [closeParameter]; linarith
  have hi := interior_bernoulli_record_separation halfParameter (closeParameter ε hε hε1) hp hpq hq
  refine ⟨⟨hp,hpq,hq⟩,⟨by linarith,by linarith⟩,
    coinKernel_minorized _ _ (by norm_num [halfParameter]),
    coinKernel_minorized _ _ (by dsimp [closeParameter]; linarith),?_,hi.2.2.2.2.2.2⟩
  intro n
  have h := hi.2.2.2.2.1 n
  simpa [halfParameter,closeParameter] using h

end Komorebi.LSM.MarkovStability.BernoulliSeparation
