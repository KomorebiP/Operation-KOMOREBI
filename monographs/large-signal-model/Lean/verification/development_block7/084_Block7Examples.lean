import KomorebiLSM.BaseNormModels
import KomorebiLSM.PolicyComparison
import KomorebiLSM.SharpConditioning

/-! Exact examples separate whole-record distance, conditioning, and signed coordinates. -/
set_option autoImplicit false
namespace Komorebi.LSM.Block7Examples
open scoped BigOperators
open BaseNorm FiniteTV FiniteBayes FiniteInstruments ObservationTree

noncomputable def bernoulli (p : ℝ) (o : Fin 2) : ℝ →ₗ[ℝ] ℝ :=
  (![1-p,p] o) • LinearMap.id

theorem bernoulli_instrument (p : ℝ) (hp : 0 ≤ p) (h1 : p ≤ 1) :
    scalarCone.Instrument (bernoulli p) := by
  constructor
  · intro o x hx
    change 0 ≤ x at hx
    change 0 ≤ (![1-p,p] o)*x
    apply mul_nonneg _ hx
    fin_cases o <;> simp <;> linarith
  · intro x
    change (∑ o : Fin 2, (![1-p,p] o)*x)=x
    simp only [Fin.sum_univ_two,Matrix.cons_val_zero,Matrix.cons_val_one]
    ring

theorem scalar_initial : (1 : ℝ) ∈ scalarCone.base := by
  constructor
  · change (0 : ℝ) ≤ 1; norm_num
  · rfl

theorem scalar_base_eq_one {x : ℝ} (hx : x ∈ scalarCone.base) : x=1 := hx.2

theorem bernoulli_discrepancy (p q : ℝ) :
    scalarCone.discrepancy (bernoulli p) (bernoulli q) 1=2*|p-q| := by
  unfold ProbabilityCone.discrepancy
  simp only [Fin.sum_univ_two,LinearMap.sub_apply,bernoulli,LinearMap.smul_apply,
    LinearMap.id_apply,smul_eq_mul,mul_one,scalar_value]
  have he : 1-p-(1-q)=-(p-q) := by ring
  simp only [Matrix.cons_val_zero,Matrix.cons_val_one,he,abs_neg]
  ring

theorem bernoulli_instrumentError (p q : ℝ) :
    scalarCone.instrumentError (bernoulli p) (bernoulli q)=2*|p-q| := by
  unfold ProbabilityCone.instrumentError
  have he : scalarCone.discrepancy (bernoulli p) (bernoulli q) '' scalarCone.base =
      {2*|p-q|} := by
    ext r
    constructor
    · rintro ⟨x,hx,rfl⟩
      rw [scalar_base_eq_one hx,bernoulli_discrepancy]
      exact Set.mem_singleton _
    · intro hr
      have hr' : r=2*|p-q| := hr
      exact ⟨1,scalar_initial,(bernoulli_discrepancy p q).trans hr'.symm⟩
  rw [he,csSup_singleton]

/-- The general theorem supplies a bound for every horizon, not a tested maximum length. -/
theorem bernoulli_record_bound (p q : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1)
    (hq : 0 ≤ q) (hq1 : q ≤ 1) (n : ℕ) :
    distance (recordLaw scalarCone (fun _ => bernoulli p) n [] 1)
      (recordLaw scalarCone (fun _ => bernoulli q) n [] 1) ≤ min 1 (n*|p-q|) := by
  have he : ∀ (h : List (Fin 2)) x, x ∈ scalarCone.base →
      scalarCone.discrepancy (bernoulli p) (bernoulli q) x ≤ (fun _ : ℕ => 2*|p-q|) h.length := by
    intro h x hx
    rw [scalar_base_eq_one hx,bernoulli_discrepancy]
  have hb := observation_tree_tv_bound scalarCone (fun _ => bernoulli p) (fun _ => bernoulli q)
    (fun _ => bernoulli_instrument p hp hp1) (fun _ => bernoulli_instrument q hq hq1)
    (fun _ => 2*|p-q|) he n 1 1 scalar_initial scalar_initial
  simpa only [sub_self,ProbabilityCone.value_zero,zero_div,zero_add,Finset.sum_const,
    Finset.card_range,nsmul_eq_mul,mul_div_assoc,mul_div_cancel_left₀ _ (by norm_num : (2:ℝ) ≠ 0)] using hb

theorem bernoulli_quarter_two_step :
    distance (recordLaw scalarCone (fun _ => bernoulli (1/4)) 2 [] 1)
      (recordLaw scalarCone (fun _ => bernoulli (1/2)) 2 [] 1)=5/16 := by
  norm_num [distance,l1,recordLaw,recordState,Record,recordFintype,Fintype.sum_prod_type,
    Fin.sum_univ_two,bernoulli,scalarCone]

theorem bernoulli_zero_half_one_step :
    distance (recordLaw scalarCone (fun _ => bernoulli 0) 1 [] 1)
      (recordLaw scalarCone (fun _ => bernoulli (1/2)) 1 [] 1)=1/2 := by
  norm_num [distance,l1,recordLaw,recordState,Record,recordFintype,Fintype.sum_prod_type,
    Fin.sum_univ_two,bernoulli,scalarCone]

theorem bernoulli_zero_half_two_step :
    distance (recordLaw scalarCone (fun _ => bernoulli 0) 2 [] 1)
      (recordLaw scalarCone (fun _ => bernoulli (1/2)) 2 [] 1)=3/4 := by
  norm_num [distance,l1,recordLaw,recordState,Record,recordFintype,Fintype.sum_prod_type,
    Fin.sum_univ_two,bernoulli,scalarCone]

theorem one_step_error_is_not_full_record_bound :
    ¬ distance (recordLaw scalarCone (fun _ => bernoulli 0) 2 [] 1)
      (recordLaw scalarCone (fun _ => bernoulli (1/2)) 2 [] 1) ≤ 1/2 := by
  rw [bernoulli_zero_half_two_step]; norm_num

/-- Zero-likelihood branches do not obstruct an unnormalized whole-law guarantee. -/
theorem zero_branch_record_is_prior (n : ℕ) :
    IsPrior (recordLaw scalarCone (fun _ => bernoulli 0) n [] 1) :=
  record_prior scalarCone _ (fun _ => bernoulli_instrument 0 (by norm_num) (by norm_num))
    n [] 1 scalar_initial

theorem rare_event_unconditional_distance :
    distance (sharpP (1/100)) (sharpQ (1/100) (1/200))=1/200 :=
  sharp_distance _ _ (by norm_num)

theorem rare_event_conditional_distance :
    distance (conditional (sharpP (1/100)) sharpEvent)
      (conditional (sharpQ (1/100) (1/200)) sharpEvent)=1/2 := by
  rw [sharp_conditional_distance _ _ (by norm_num) (by norm_num)]; norm_num

theorem rare_event_attains_bound :
    distance (conditional (sharpP (1/100)) sharpEvent)
      (conditional (sharpQ (1/100) (1/200)) sharpEvent) =
      distance (sharpP (1/100)) (sharpQ (1/100) (1/200)) /
        eventMass (sharpP (1/100)) sharpEvent := by
  rw [rare_event_conditional_distance,rare_event_unconditional_distance,sharpP_eventMass]
  norm_num

theorem missing_event_is_zero : eventMass (sharpP 0) sharpEvent=0 := sharpP_eventMass 0

theorem missing_event_conditional_not_prior : ¬ IsPrior (conditional (sharpP 0) sharpEvent) := by
  intro h
  have hz : conditional (sharpP 0) sharpEvent=0 := by
    unfold conditional FiniteInstruments.normalize
    rw [restrict_mass,sharpP_eventMass]; simp
  rw [hz] at h
  have ht := h.2
  norm_num at ht

theorem signed_mass_zero : mass (![1,-1] : Fin 2 → ℝ)=0 := by
  norm_num [mass_apply,Fin.sum_univ_two]

theorem signed_base_norm_two : (orthant (Fin 2)).value (![1,-1])=2 := by
  rw [orthant_value]; norm_num [l1,Fin.sum_univ_two]

theorem signed_vector_not_positive : ¬ (![1,-1] : Fin 2 → ℝ) ∈ (orthant (Fin 2)).carrier := by
  rw [orthant_carrier]
  intro h
  have ht := h 1
  norm_num at ht

/-- Aggregation can erase signed contrast without violating its contraction theorem. -/
theorem aggregation_can_strictly_contract :
    l1 (aggregate (fun _ : Fin 2 => ()) (![1,-1] : Fin 2 → ℝ))=0 ∧
    l1 (![1,-1] : Fin 2 → ℝ)=2 := by
  norm_num [l1,aggregate,Fin.sum_univ_two]

end Komorebi.LSM.Block7Examples
