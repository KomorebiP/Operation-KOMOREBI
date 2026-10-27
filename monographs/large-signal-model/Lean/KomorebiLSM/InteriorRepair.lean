import KomorebiLSM.RobustOrientedMargin
import KomorebiLSM.ContinuousTV

/-! P73: a literal center-reset repair buys oriented margin and retains its
separate integrated prediction cost in the actual Lorentz base norm. -/
set_option autoImplicit false
namespace Komorebi.LSM.InteriorRepair
open LorentzCylinder RobustOrientedMargin MeasureTheory ContinuousInstrument
open scoped BigOperators
variable {V A : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

noncomputable def centerReset : State V →L[ℝ] State V :=
  (ContinuousLinearMap.fst ℝ ℝ V).smulRight (1,0)

@[simp] theorem centerReset_apply (z : State V) : centerReset z=(z.1,0) := by
  change z.1 • (1,(0 : V))=(z.1,0)
  simp

noncomputable def resetOperator (g : ℝ) : State V →L[ℝ] State V := g • centerReset

@[simp] theorem resetOperator_normalized (g : ℝ) (v : V) : resetOperator g (1,v)=(g,0) := by
  simp [resetOperator]

@[simp] theorem centerReset_mass (z : State V) : probabilityCone.mass (centerReset z)=probabilityCone.mass z := by
  rw [centerReset_apply]
  rfl

theorem resetOperator_positive (g : ℝ) (hg : 0≤g) {z : State V} (hz : z∈cone) :
    resetOperator g z∈cone := by
  simp only [resetOperator,smul_apply,centerReset_apply]
  change ‖g • (0 : V)‖≤g*z.1
  rw [smul_zero,norm_zero]
  exact mul_nonneg hg ((norm_nonneg _).trans hz)

/-- The estimate is not presumed positive. The change is a genuine model mixture. -/
noncomputable def repair (Fhat : State V →L[ℝ] State V) (g eta : ℝ) : State V →L[ℝ] State V :=
  (1-eta) • Fhat+eta • resetOperator g

/-- The reset modifies only output mass on normalized inputs. -/
theorem repair_slack (Fhat : State V →L[ℝ] State V) (g eta : ℝ)
    (heta1 : eta≤1) (v : V) :
    slack (repair Fhat g eta (1,v))=(1-eta)*slack (Fhat (1,v))+eta*g := by
  simp only [repair,add_apply,smul_apply,resetOperator_normalized]
  change ((1-eta)*(Fhat (1,v)).1+eta*g)-‖(1-eta) • (Fhat (1,v)).2+eta • (0 : V)‖=
    (1-eta)*((Fhat (1,v)).1-‖(Fhat (1,v)).2‖)+eta*g
  rw [smul_zero,add_zero,norm_smul,Real.norm_eq_abs,abs_of_nonneg (sub_nonneg.mpr heta1)]
  ring

theorem estimate_slack_lower (Fstar Fhat : State V →L[ℝ] State V) (d : ℝ)
    (hstar : ∀ z∈cone,Fstar z∈cone)
    (herror : ∀ v : V,‖v‖≤1 → |((Fhat-Fstar) (1,v)).1|+‖((Fhat-Fstar) (1,v)).2‖≤d)
    (v : V) (hv : ‖v‖≤1) : -d≤slack (Fhat (1,v)) := by
  have hp : 0≤slack (Fstar (1,v)) := sub_nonneg.mpr (hstar (1,v) hv)
  have he := herror v hv
  have ha := slack_add_lower (Fstar (1,v)) ((Fhat-Fstar) (1,v))
  have hid : Fstar (1,v)+(Fhat-Fstar) (1,v)=Fhat (1,v) := by
    simp only [sub_apply]
    abel
  rw [hid] at ha
  linarith

variable [FiniteDimensional ℝ V]

/-- The actual repaired minimum has the exact P73 lower bound. -/
theorem repair_margin (Fstar Fhat : State V →L[ℝ] State V) (d g eta : ℝ)
    (heta1 : eta≤1) (hstar : ∀ z∈cone,Fstar z∈cone)
    (herror : ∀ v : V,‖v‖≤1 → |((Fhat-Fstar) (1,v)).1|+‖((Fhat-Fstar) (1,v)).2‖≤d) :
    eta*g-(1-eta)*d≤sigma (repair Fhat g eta) := by
  apply (le_sigma_iff _ _).mpr
  intro v hv
  rw [repair_slack Fhat g eta heta1]
  have h := mul_le_mul_of_nonneg_left (estimate_slack_lower Fstar Fhat d hstar herror v hv)
    (sub_nonneg.mpr heta1)
  nlinarith

/-- An extra combined output uncertainty is charged against the repaired slack. -/
theorem robust_repair_preserves (Fstar Fhat Delta : State V →L[ℝ] State V)
    (d g eta nu : ℝ) (heta1 : eta≤1) (hstar : ∀ z∈cone,Fstar z∈cone)
    (herror : ∀ v : V,‖v‖≤1 → |((Fhat-Fstar) (1,v)).1|+‖((Fhat-Fstar) (1,v)).2‖≤d)
    (hnu : ∀ v : V,‖v‖≤1 → |(Delta (1,v)).1|+‖(Delta (1,v)).2‖≤nu)
    (hcover : (1-eta)*d+nu≤eta*g) {z : State V} (hz : z∈cone) :
    (repair Fhat g eta+Delta) z∈cone := by
  apply preserves_of_normalized _ _ hz
  intro v hv
  have hm := (repair_margin Fstar Fhat d g eta heta1 hstar herror).trans
    (sigma_le (repair Fhat g eta) v hv)
  have he := hnu v hv
  have ha := slack_add_lower (repair Fhat g eta (1,v)) (Delta (1,v))
  have hs : 0≤slack (repair Fhat g eta (1,v)+Delta (1,v)) := by linarith
  unfold slack at hs
  change ‖(repair Fhat g eta (1,v)+Delta (1,v)).2‖≤(repair Fhat g eta (1,v)+Delta (1,v)).1
  exact sub_nonneg.mp hs

/-- Raw estimates retain exact integrated mass without presuming cone positivity. -/
structure EstimateFamily where
  op : A → ℝ → State V →L[ℝ] State V
  measurable_op : ∀ a,Measurable (op a)
  integrable_op : ∀ a,Integrable (op a) UniformIntervalMoments.measure
  mass_preserving : ∀ a z,probabilityCone.mass ((∫ u,op a u∂UniformIntervalMoments.measure) z)=probabilityCone.mass z

/-- The declared strictly positive normalized scalar reset density. -/
structure ResetProfile where
  density : A → ℝ → ℝ
  measurable_density : ∀ a,Measurable (density a)
  integrable_density : ∀ a,Integrable (density a) UniformIntervalMoments.measure
  minimum : ℝ
  minimum_positive : 0<minimum
  lower : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → minimum≤density a u
  integral_one : ∀ a,(∫ u,density a u∂UniformIntervalMoments.measure)=1

variable [MeasurableSpace V] [BorelSpace V]

/-- The reference instrument has exactly the declared reset density and center state. -/
noncomputable def ResetProfile.instrument (g : ResetProfile (A := A)) :
    DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure where
  op a u := resetOperator (g.density a u)
  measurable_op a := (g.measurable_density a).smul measurable_const
  integrable_op a := (g.integrable_density a).smul_const (centerReset (V := V))
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    intro z hz
    exact resetOperator_positive _ (g.minimum_positive.le.trans (g.lower a u hu)) hz
  mass_preserving a z := by
    change probabilityCone.mass ((∫ u,g.density a u • (centerReset (V := V))∂UniformIntervalMoments.measure) z)=_
    rw [integral_smul_const,g.integral_one,one_smul]
    exact centerReset_mass z

/-- Mixing keeps the estimate's exact integrated mass even before proving positivity. -/
noncomputable def mixedFamily (H : EstimateFamily (V := V) (A := A))
    (g : ResetProfile (A := A)) (eta : ℝ) : EstimateFamily (V := V) (A := A) where
  op a u := repair (H.op a u) (g.density a u) eta
  measurable_op a := ((H.measurable_op a).const_smul (1-eta)).add
    (((g.instrument (V := V)).measurable_op a).const_smul eta)
  integrable_op a := ((H.integrable_op a).smul (1-eta)).add
    (((g.instrument (V := V)).integrable_op a).smul eta)
  mass_preserving a z := by
    change probabilityCone.mass ((∫ u,(1-eta) • H.op a u+eta • (g.instrument (V := V)).op a u
      ∂UniformIntervalMoments.measure) z)=_
    have hH : Integrable (fun u => (1-eta) • H.op a u) UniformIntervalMoments.measure :=
      (H.integrable_op a).smul (1-eta)
    have hN : Integrable (fun u => eta • (g.instrument (V := V)).op a u) UniformIntervalMoments.measure :=
      ((g.instrument (V := V)).integrable_op a).smul eta
    rw [integral_add hH hN,integral_smul,integral_smul]
    simp only [add_apply,smul_apply,map_add,map_smul,smul_eq_mul,H.mass_preserving,
      (g.instrument (V := V)).mass_preserving]
    ring

/-- A full interval repair witness constructs a true model; positivity is derived. -/
noncomputable def repairedInstrument (D : DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure)
    (H : EstimateFamily (V := V) (A := A)) (g : ResetProfile (A := A))
    (eta : ℝ) (heta1 : eta≤1) (d : A → ℝ → ℝ)
    (hstar : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ z∈cone,D.op a u z∈cone)
    (herror : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : V,‖v‖≤1 →
      |((H.op a u-D.op a u) (1,v)).1|+‖((H.op a u-D.op a u) (1,v)).2‖≤d a u)
    (hcover : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → (1-eta)*d a u≤eta*g.density a u) :
    DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure where
  op := (mixedFamily H g eta).op
  measurable_op := (mixedFamily H g eta).measurable_op
  integrable_op := (mixedFamily H g eta).integrable_op
  mass_preserving := (mixedFamily H g eta).mass_preserving
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    intro z hz
    change repair (H.op a u) (g.density a u) eta z∈cone
    have hr := robust_repair_preserves (D.op a u) (H.op a u) 0 (d a u) (g.density a u)
      eta 0 heta1 (hstar a u hu) (herror a u hu) (fun _ _ => by simp) (by simpa using hcover a u hu) hz
    simpa only [add_zero] using hr

/-- Polynomial estimates acquire measurability, Bochner integrability and exact mass from their actual coefficients. -/
noncomputable def EstimateFamily.ofPolynomial {n : ℕ}
    (B : A → Fin n → State V →L[ℝ] State V)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • B a k) z)=probabilityCone.mass z) :
    EstimateFamily (V := V) (A := A) where
  op a := PolynomialGram.operatorPolynomial (B a)
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  mass_preserving a z := by rw [PolynomialGram.operatorPolynomial_integral]; exact hm a z

/-- A genuine finite scalar polynomial reset profile, normalized by exact power moments. -/
noncomputable def ResetProfile.ofPolynomial {n : ℕ} (c : A → Fin n → ℝ)
    (gmin : ℝ) (hgmin : 0<gmin)
    (hlower : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → gmin≤(Polynomial.ofFn n (c a)).eval u)
    (hm : ∀ a,∑ k : Fin n,c a k*UniformIntervalMoments.moment k=1) : ResetProfile (A := A) where
  density a u := (Polynomial.ofFn n (c a)).eval u
  measurable_density a := (Polynomial.continuous _).measurable
  integrable_density a := UniformIntervalMoments.continuous_integrable (Polynomial.continuous _)
  minimum := gmin
  minimum_positive := hgmin
  lower := hlower
  integral_one a := by
    simp_rw [UniformIntervalMoments.eval_ofFn]
    rw [UniformIntervalMoments.integral_power_sum]
    exact hm a

omit [FiniteDimensional ℝ V] [MeasurableSpace V] [BorelSpace V] in
theorem EstimateFamily.applied_integrable (H : EstimateFamily (V := V) (A := A)) (a : A) (z : State V) :
    Integrable (fun u => H.op a u z) UniformIntervalMoments.measure :=
  (ContinuousLinearMap.apply ℝ (State V) z).integrable_comp (H.integrable_op a)

omit [MeasurableSpace V] [BorelSpace V] in
/-- The reset's comparison cost is integrated: point densities are not bounded by one. -/
theorem ResetProfile.integrated_cost_le_two (g : ResetProfile (A := A))
    (D : DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure)
    (a : A) (z : State V) (hz : z∈probabilityCone.base) :
    (∫ u,probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z)∂UniformIntervalMoments.measure)≤2 := by
  have hi := probabilityCone.integrable_value
    (((g.instrument (V := V)).applied_integrable a z).sub (D.applied_integrable a z))
  have hj := ((g.instrument (V := V)).density_integrable a z).add (D.density_integrable a z)
  have hp : ∀ᵐ u∂UniformIntervalMoments.measure,
      probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z)≤
        (g.instrument (V := V)).density a u z+D.density a u z := by
    filter_upwards [(g.instrument (V := V)).positive a,D.positive a] with u hN hD
    exact (probabilityCone.value_sub_le _ _).trans_eq (by
      rw [probabilityCone.value_on_cone (hN z hz.1),probabilityCone.value_on_cone (hD z hz.1)]
      rfl)
  calc
    _≤∫ u,(g.instrument (V := V)).density a u z+D.density a u z∂UniformIntervalMoments.measure :=
      integral_mono_ae hi hj hp
    _=2 := by
      rw [integral_add ((g.instrument (V := V)).density_integrable a z) (D.density_integrable a z),
        (g.instrument (V := V)).integral_density,D.integral_density,hz.2]
      norm_num

omit [FiniteDimensional ℝ V] [MeasurableSpace V] [BorelSpace V] in
theorem repair_difference (Fhat Fstar : State V →L[ℝ] State V) (g eta : ℝ) (z : State V) :
    repair Fhat g eta z-Fstar z=(1-eta) • (Fhat z-Fstar z)+eta • (resetOperator g z-Fstar z) := by
  simp only [repair,add_apply,smul_apply,smul_sub]
  module

omit [MeasurableSpace V] [BorelSpace V] in
/-- The repair charge 2 eta is retained separately from the estimate error. -/
theorem repair_integrated_error
    (D : DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure)
    (H : EstimateFamily (V := V) (A := A)) (g : ResetProfile (A := A))
    (eta : ℝ) (heta0 : 0≤eta) (heta1 : eta≤1) (epsilon : ℝ) (a : A) (z : State V)
    (hz : z∈probabilityCone.base)
    (herror : (∫ u,probabilityCone.value (H.op a u z-D.op a u z)∂UniformIntervalMoments.measure)≤epsilon) :
    (∫ u,probabilityCone.value (repair (H.op a u) (g.density a u) eta z-D.op a u z)
      ∂UniformIntervalMoments.measure)≤(1-eta)*epsilon+2*eta := by
  have hi := probabilityCone.integrable_value
    (((mixedFamily H g eta).applied_integrable a z).sub (D.applied_integrable a z))
  have hH : Integrable (fun u => probabilityCone.value (H.op a u z-D.op a u z)) UniformIntervalMoments.measure :=
    probabilityCone.integrable_value ((H.applied_integrable a z).sub (D.applied_integrable a z))
  have hN : Integrable (fun u => probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z))
      UniformIntervalMoments.measure := probabilityCone.integrable_value
        (((g.instrument (V := V)).applied_integrable a z).sub (D.applied_integrable a z))
  have hp (u : ℝ) : probabilityCone.value (repair (H.op a u) (g.density a u) eta z-D.op a u z)≤
      (1-eta)*probabilityCone.value (H.op a u z-D.op a u z)+
        eta*probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z) := by
    rw [repair_difference]
    exact (probabilityCone.value_add_le _ _).trans_eq (by
      rw [probabilityCone.value_smul_of_nonneg (sub_nonneg.mpr heta1),
        probabilityCone.value_smul_of_nonneg heta0]
      rfl)
  calc
    _≤∫ u,(1-eta)*probabilityCone.value (H.op a u z-D.op a u z)+
        eta*probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z)∂UniformIntervalMoments.measure :=
      integral_mono hi ((hH.const_mul (1-eta)).add (hN.const_mul eta)) hp
    _=(1-eta)*(∫ u,probabilityCone.value (H.op a u z-D.op a u z)∂UniformIntervalMoments.measure)+
        eta*(∫ u,probabilityCone.value ((g.instrument (V := V)).op a u z-D.op a u z)∂UniformIntervalMoments.measure) := by
      rw [integral_add (hH.const_mul (1-eta)) (hN.const_mul eta),integral_const_mul,integral_const_mul]
    _≤(1-eta)*epsilon+2*eta := by
      have hreset := mul_le_mul_of_nonneg_left (g.integrated_cost_le_two D a z hz) heta0
      nlinarith [mul_le_mul_of_nonneg_left herror (sub_nonneg.mpr heta1)]

/-- The actual complete common-policy laws satisfy P73's probability-convention TV budget. -/
theorem common_policy_law_error [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (D G : DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure)
    (H : EstimateFamily (V := V) (A := A)) (g : ResetProfile (A := A))
    (eta : ℝ) (heta0 : 0≤eta) (heta1 : eta≤1) (epsilon : ℝ)
    (hG : ∀ a u,G.op a u=repair (H.op a u) (g.density a u) eta)
    (herror : ∀ a z,z∈probabilityCone.base →
      (∫ u,probabilityCone.value (H.op a u z-D.op a u z)∂UniformIntervalMoments.measure)≤epsilon)
    (policy : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : DensityInstrument.State (probabilityCone (V := V))) (horizon : ℕ) :
    SequentialLowerCertificate.lawTV (TimeRecords.recordLaw (fun _ => G) policy z.1 horizon)
      (TimeRecords.recordLaw (fun _ => D) policy z.1 horizon)≤
      min 1 (((horizon : ℝ)/2)*((1-eta)*epsilon+2*eta)) := by
  have hb0 : 0≤(1-eta)*epsilon+2*eta := by
    rcases isEmpty_or_nonempty A with hA | hA
    · let := hA
      have hc := policy.sum_one 0 PUnit.unit
      simp at hc
    · let := hA
      let a : A := Classical.choice hA
      have he0 : 0≤epsilon := (integral_nonneg (fun u => probabilityCone.value_nonneg _)).trans (herror a z.1 z.2)
      exact add_nonneg (mul_nonneg (sub_nonneg.mpr heta1) he0) (mul_nonneg (by norm_num) heta0)
  have hd : ∀ a w,w∈probabilityCone.base →
      (∫ u,probabilityCone.value (G.op a u w-D.op a u w)∂UniformIntervalMoments.measure)≤(1-eta)*epsilon+2*eta := by
    intro a w hw
    simpa only [hG] using repair_integrated_error D H g eta heta0 heta1 epsilon a w hw (herror a w hw)
  have ht := ContinuousTV.record_lawTV_le (fun _ => G) (fun _ => D) policy z z
    (fun _ => (1-eta)*epsilon+2*eta) (fun _ => hb0) (fun _ a w hw => hd a w hw) 0 (by simp) horizon
  convert ht using 1
  congr 1
  simp only [Finset.sum_const,Finset.card_range,nsmul_eq_mul,zero_add]
  ring

end Komorebi.LSM.InteriorRepair
