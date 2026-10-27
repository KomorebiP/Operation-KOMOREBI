import KomorebiLSM.ContinuousRecords

/-! Time-dependent instruments on the established continuous history and policy
spaces. Actual finite laws, normalization and all prefix marginals are derived. -/
set_option autoImplicit false
namespace Komorebi.LSM.TimeRecords
open MeasureTheory ProbabilityTheory ContinuousRecords
open scoped ENNReal BigOperators

section PolicyBounds
variable {A Y : Type*} [MeasurableSpace A] [MeasurableSpace Y] [Fintype A]

/-- Pointwise normalization bounds each finite-action policy probability. -/
theorem policy_probability_le_one (π : Policy (A := A) (Y := Y))
    (n : ℕ) (h : History (A × Y) n) (a : A) : π.probability n h a ≤ 1 := by
  calc
    _ ≤ ∑ b, π.probability n h b := Finset.single_le_sum (fun _ _ => by positivity) (Finset.mem_univ a)
    _ = 1 := π.sum_one n h

theorem policy_weight_le_one (π : Policy (A := A) (Y := Y)) :
    (n : ℕ) → ∀ h : History (A × Y) n, π.weight n h ≤ 1
  | 0, _ => le_rfl
  | n+1, h => by
    exact (mul_le_mul' (policy_weight_le_one π n h.1)
      (policy_probability_le_one π n h.1 h.2.1)).trans_eq (one_mul 1)

theorem policy_probability_ne_top (π : Policy (A := A) (Y := Y))
    (n : ℕ) (h : History (A × Y) n) (a : A) : π.probability n h a ≠ ⊤ :=
  ne_top_of_le_ne_top ENNReal.one_ne_top (policy_probability_le_one π n h a)

theorem policy_weight_ne_top (π : Policy (A := A) (Y := Y))
    (n : ℕ) (h : History (A × Y) n) : π.weight n h ≠ ⊤ :=
  ne_top_of_le_ne_top ENNReal.one_ne_top (policy_weight_le_one π n h)
end PolicyBounds

variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D : ℕ → ContinuousInstrument.DensityInstrument (A := A) C μ)

/-- The genuine unnormalized operator product on a recorded action/observation history. -/
noncomputable def run (z : E) : (n : ℕ) → History (A × Y) n → E
  | 0, _ => z
  | n+1, h => (D n).op h.2.1 h.2.2 (run z n h.1)

theorem run_measurable (z : E) : (n : ℕ) → Measurable (run D z n)
  | 0 => measurable_const
  | n+1 => by
    exact (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
      (((ContinuousRecords.op_measurable (D n)).comp measurable_snd).prodMk ((run_measurable z n).comp measurable_fst))

/-- Policy factors multiply the mass of the actual operator product. -/
noncomputable def recordDensity (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (h : History (A × Y) n) : ℝ≥0∞ := π.weight n h * ENNReal.ofReal (C.mass (run D z n h))

theorem recordDensity_measurable (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measurable (recordDensity D π z n) :=
  (Policy.weight_measurable π n).mul (((ContinuousInstrument.massCLM C).continuous.measurable.comp
    (run_measurable D z n)).ennreal_ofReal)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSingletonClass A] in
/-- Policy weighting is an exact real scalar representation of the actual
nonnegative record density, because normalized policy weights are finite. -/
theorem recordDensity_eq_ofReal_weightedRun (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (h : History (A × Y) n) :
    recordDensity D π z n h = ENNReal.ofReal (C.mass ((π.weight n h).toReal • run D z n h)) := by
  rw [map_smul, smul_eq_mul, ENNReal.ofReal_mul ENNReal.toReal_nonneg,
    ENNReal.ofReal_toReal (policy_weight_ne_top π n h)]
  rfl

/-- An actual measure on finite action/observation records. -/
noncomputable def recordLaw (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measure (History (A × Y) n) :=
  (reference (stepReference (A := A) μ) n).withDensity (recordDensity D π z n)


variable [IsProbabilityMeasure μ]

theorem run_mem_ae {z : E} (hz : z∈C.carrier) : (n : ℕ) →
    ∀ᵐ h∂reference (stepReference (A := A) μ) n,run D z n h∈C.carrier
  | 0 => by simpa [run] using Filter.Eventually.of_forall (fun _ => hz)
  | n+1 => by
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage (run_measurable D z (n+1)))).mpr
    filter_upwards [run_mem_ae hz n] with h hh
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage
      ((run_measurable D z (n+1)).comp (measurable_const.prodMk measurable_id)))).mpr
    rw [Measure.ae_count_iff]
    intro a
    filter_upwards [(D n).positive a] with y hy
    exact hy _ hh

theorem recordDensity_integrate_last (π : Policy (A := A) (Y := Y))
    (z : E) (n : ℕ) (h : History (A × Y) n) (hh : run D z n h∈C.carrier) :
    (∫⁻ r,recordDensity D π z (n+1) (h,r)∂stepReference (A := A) μ)=
      recordDensity D π z n h := by
  have hm : Measurable (fun r : A × Y => recordDensity D π z (n+1) (h,r)) :=
    (recordDensity_measurable D π z (n+1)).comp (measurable_const.prodMk measurable_id)
  rw [stepReference,lintegral_prod _ hm.aemeasurable]
  change (∫⁻ a,∫⁻ y,(π.weight n h * π.probability n h a) *
    ENNReal.ofReal ((D n).density a y (run D z n h))∂μ∂Measure.count)=recordDensity D π z n h
  have hi (a : A) : (∫⁻ y,(π.weight n h * π.probability n h a) *
      ENNReal.ofReal ((D n).density a y (run D z n h))∂μ)=
      (π.weight n h * π.probability n h a)*ENNReal.ofReal (C.mass (run D z n h)) := by
    have hd : Measurable (fun y : Y => ENNReal.ofReal ((D n).density a y (run D z n h))) :=
      (((D n).density_measurable a).comp (measurable_const.prodMk measurable_id)).ennreal_ofReal
    rw [lintegral_const_mul _ hd,ContinuousRecords.integrated_density_mass (D n) a hh]
  simp_rw [hi,lintegral_count,tsum_fintype]
  rw [← Finset.sum_mul,← Finset.mul_sum,π.sum_one,mul_one]
  rfl



/-- Consistency is the equality of literal prefix marginals. -/
theorem recordLaw_consistent (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    (recordLaw D π z (n+1)).fst=recordLaw D π z n := by
  apply density_first_marginal _ _ _ _ (recordDensity_measurable D π z (n+1))
  filter_upwards [run_mem_ae D hz n] with h hh
  exact recordDensity_integrate_last D π z n h hh

/-- Every finite record law has total probability one. -/
theorem recordLaw_univ (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) :
    (n : ℕ) → recordLaw D π z.1 n Set.univ=1
  | 0 => by simp [recordLaw,reference,recordDensity,Policy.weight,run,z.2.2]
  | n+1 => by
    have hm := congrArg (fun ν : Measure (History (A × Y) n) => ν Set.univ)
      (recordLaw_consistent D π z.2.1 n)
    exact (Measure.fst_univ (ρ := recordLaw D π z.1 (n+1))).symm.trans (hm.trans (recordLaw_univ π z n))

instance recordLaw_probability (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    IsProbabilityMeasure (recordLaw D π z.1 n) := ⟨recordLaw_univ D π z n⟩

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem recordLaw_event (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (S : Set (History (A × Y) n)) (hS : MeasurableSet S) :
    recordLaw D π z n S=∫⁻ h in S,recordDensity D π z n h∂reference (stepReference (A := A) μ) n :=
  withDensity_apply _ hS


/-- Prescribed actions retain the genuine, unnormalized chronological product. -/
noncomputable def observationRun (actions : ℕ → A) (z : E) :
    (n : ℕ) → History Y n → E
  | 0, _ => z
  | n+1,h => (D n).op (actions n) h.2 (observationRun actions z n h.1)

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationRun_measurable (actions : ℕ → A) (z : E) :
    (n : ℕ) → Measurable (observationRun D actions z n)
  | 0 => measurable_const
  | n+1 => by
    exact (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
      ((((D n).measurable_op (actions n)).comp measurable_snd).prodMk
        ((observationRun_measurable actions z n).comp measurable_fst))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationRun_mem_ae (actions : ℕ → A) {z : E} (hz : z∈C.carrier) :
    (n : ℕ) → ∀ᵐ h∂reference μ n,observationRun D actions z n h∈C.carrier
  | 0 => by simpa [observationRun] using Filter.Eventually.of_forall (fun _ => hz)
  | n+1 => by
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage
      (observationRun_measurable D actions z (n+1)))).mpr
    filter_upwards [observationRun_mem_ae actions hz n] with h hh
    filter_upwards [(D n).positive (actions n)] with y hy
    exact hy _ hh

/-- Exact operator-product density with respect to the nested product reference μ^n. -/
noncomputable def observationDensity (actions : ℕ → A) (z : E) (n : ℕ)
    (h : History Y n) : ℝ≥0∞ := ENNReal.ofReal (C.mass (observationRun D actions z n h))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationDensity_measurable (actions : ℕ → A) (z : E) (n : ℕ) :
    Measurable (observationDensity D actions z n) :=
  ((ContinuousInstrument.massCLM C).continuous.measurable.comp
    (observationRun_measurable D actions z n)).ennreal_ofReal

noncomputable def observationLaw (actions : ℕ → A) (z : E) (n : ℕ) :
    Measure (History Y n) := (reference μ n).withDensity (observationDensity D actions z n)

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_consistent (actions : ℕ → A) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    (observationLaw D actions z (n+1)).fst=observationLaw D actions z n := by
  apply density_first_marginal _ _ _ _ (observationDensity_measurable D actions z (n+1))
  filter_upwards [observationRun_mem_ae D actions hz n] with h hh
  exact ContinuousRecords.integrated_density_mass (D n) (actions n) hh

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_univ (actions : ℕ → A)
    (z : ContinuousInstrument.DensityInstrument.State C) :
    (n : ℕ) → observationLaw D actions z.1 n Set.univ=1
  | 0 => by simp [observationLaw,reference,observationDensity,observationRun,z.2.2]
  | n+1 => by
    have hm := congrArg (fun ν : Measure (History Y n) => ν Set.univ)
      (observationLaw_consistent D actions z.2.1 n)
    exact (Measure.fst_univ (ρ := observationLaw D actions z.1 (n+1))).symm.trans
      (hm.trans (observationLaw_univ actions z n))

instance observationLaw_probability (actions : ℕ → A)
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    IsProbabilityMeasure (observationLaw D actions z.1 n) := ⟨observationLaw_univ D actions z n⟩

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationLaw_product_density (actions : ℕ → A) (z : E) (n : ℕ)
    (S : Set (History Y n)) (hS : MeasurableSet S) :
    observationLaw D actions z n S=
      ∫⁻ h in S,ENNReal.ofReal (C.mass (observationRun D actions z n h))∂reference μ n :=
  withDensity_apply _ hS


/-- Consistency holds for every earlier finite horizon. -/
theorem recordLaw_prefix (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) : (k : ℕ) →
    (recordLaw D π z (n+k)).map (truncate n k)=recordLaw D π z n
  | 0 => by simp [truncate]
  | k+1 => by
    change (recordLaw D π z (n+k+1)).map ((truncate n k) ∘ Prod.fst)=_
    exact (Measure.map_map (μ := recordLaw D π z (n+k+1))
      (truncate_measurable (X := A × Y) n k) measurable_fst).symm.trans
      ((congrArg (fun ν : Measure (History (A × Y) (n+k)) => ν.map (truncate n k))
        (recordLaw_consistent D π hz (n+k))).trans (recordLaw_prefix π hz n k))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_prefix (actions : ℕ → A) {z : E}
    (hz : z∈C.carrier) (n : ℕ) : (k : ℕ) →
    (observationLaw D actions z (n+k)).map (truncate n k)=observationLaw D actions z n
  | 0 => by simp [truncate]
  | k+1 => by
    change (observationLaw D actions z (n+k+1)).map ((truncate n k) ∘ Prod.fst)=_
    exact (Measure.map_map (μ := observationLaw D actions z (n+k+1))
      (truncate_measurable (X := Y) n k) measurable_fst).symm.trans
      ((congrArg (fun ν : Measure (History Y (n+k)) => ν.map (truncate n k))
        (observationLaw_consistent D actions hz (n+k))).trans (observationLaw_prefix actions hz n k))



end Komorebi.LSM.TimeRecords
