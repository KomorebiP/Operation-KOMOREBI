import KomorebiLSM.InteriorRepair
import Mathlib.Topology.Order.Monotone

/-! P80: the actual full-domain feasible repair weights have a least endpoint,
and genuine cone-positive functionals give lower brackets. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConvexRepairBracketing
open LorentzCylinder RobustOrientedMargin InteriorRepair
open scoped RealInnerProductSpace InnerProductSpace
variable {V A : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V] [FiniteDimensional ℝ V]

/-- Feasibility quantifies the actual minimum sigma at every observation and action. -/
noncomputable def feasibleWeights (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) : Set ℝ :=
  {eta | eta∈Set.Icc 0 1 ∧ ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa≤sigma (repair (H a u) 1 eta)}

/-- On [0,1], the center-reset margin is the literal affine expression in eta. -/
theorem feasible_iff_linear (H : A → ℝ → State V →L[ℝ] State V) (kappa eta : ℝ) :
    eta∈feasibleWeights H kappa ↔ eta∈Set.Icc 0 1 ∧
      ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : V,‖v‖≤1 →
        kappa≤(1-eta)*slack (H a u (1,v))+eta := by
  constructor
  · rintro ⟨heta,hm⟩
    refine ⟨heta,?_⟩
    intro a u hu v hv
    have hp := (le_sigma_iff _ _).mp (hm a u hu) v hv
    simpa only [repair_slack _ _ _ heta.2,mul_one] using hp
  · rintro ⟨heta,hlin⟩
    refine ⟨heta,?_⟩
    intro a u hu
    apply (le_sigma_iff _ _).mpr
    intro v hv
    simpa only [repair_slack _ _ _ heta.2,mul_one] using hlin a u hu v hv

theorem feasible_closed (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) :
    IsClosed (feasibleWeights H kappa) := by
  have he : feasibleWeights H kappa=Set.Icc 0 1 ∩
      {eta | ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : V,‖v‖≤1 →
        kappa≤(1-eta)*slack (H a u (1,v))+eta} := by
    ext eta
    exact feasible_iff_linear H kappa eta
  rw [he]
  apply isClosed_Icc.inter
  have hc (a : A) (u : ℝ) (v : V) :
      IsClosed {eta : ℝ | kappa≤(1-eta)*slack (H a u (1,v))+eta} :=
    isClosed_le continuous_const (((continuous_const.sub continuous_id).mul continuous_const).add continuous_id)
  simpa only [Set.ofPred_forall] using
    (isClosed_iInter fun a => isClosed_iInter fun u => isClosed_iInter fun (_hu : u∈Set.Icc (-1 : ℝ) 1) =>
      isClosed_iInter fun v => isClosed_iInter fun (_hv : ‖v‖≤1) => hc a u v)

theorem feasible_convex (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) :
    Convex ℝ (feasibleWeights H kappa) := by
  intro eta heta xi hxi a b ha hb hab
  apply (feasible_iff_linear H kappa _).mpr
  have hη := (feasible_iff_linear H kappa eta).mp heta
  have hξ := (feasible_iff_linear H kappa xi).mp hxi
  refine ⟨convex_Icc (0 : ℝ) 1 hη.1 hξ.1 ha hb hab,?_⟩
  intro action u hu v hv
  let s := slack (H action u (1,v))
  change kappa≤(1-(a*eta+b*xi))*s+(a*eta+b*xi)
  calc
    kappa=a*kappa+b*kappa := by rw [← add_mul,hab,one_mul]
    _≤a*((1-eta)*s+eta)+b*((1-xi)*s+xi) :=
      add_le_add (mul_le_mul_of_nonneg_left (hη.2 action u hu v hv) ha)
        (mul_le_mul_of_nonneg_left (hξ.2 action u hu v hv) hb)
    _=((a+b)-(a*eta+b*xi))*s+(a*eta+b*xi) := by ring
    _=_ := by rw [hab]

theorem one_feasible (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) (hkappa : kappa≤1) :
    (1 : ℝ)∈feasibleWeights H kappa := by
  apply (feasible_iff_linear H kappa 1).mpr
  refine ⟨by constructor <;> norm_num,?_⟩
  intro a u hu v hv
  simpa using hkappa

theorem feasible_bddBelow (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) :
    BddBelow (feasibleWeights H kappa) := ⟨0,fun _ h => h.1.1⟩

noncomputable def etaStar (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) : ℝ :=
  sInf (feasibleWeights H kappa)

theorem etaStar_feasible (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) (hkappa : kappa≤1) :
    etaStar H kappa∈feasibleWeights H kappa :=
  (feasible_closed H kappa).csInf_mem ⟨1,one_feasible H kappa hkappa⟩ (feasible_bddBelow H kappa)

theorem etaStar_in_unit (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) (hkappa : kappa≤1) :
    etaStar H kappa∈Set.Icc 0 1 := (etaStar_feasible H kappa hkappa).1

/-- The complete feasible set is the actual closed interval ending at the full reset. -/
theorem feasible_interval (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ) (hkappa : kappa≤1) :
    feasibleWeights H kappa=Set.Icc (etaStar H kappa) 1 := by
  ext eta
  constructor
  · intro h
    exact ⟨csInf_le (feasible_bddBelow H kappa) h,h.1.2⟩
  · intro h
    exact (feasible_convex H kappa).ordConnected.out
      (etaStar_feasible H kappa hkappa) (one_feasible H kappa hkappa) h

/-- The actual row functional ell=(1,-q transpose), with the standard real inner product. -/
def separator (q : V) : State V →ₗ[ℝ] ℝ where
  toFun z := z.1-⟪q,z.2⟫_ℝ
  map_add' z w := by
    change z.1+w.1-⟪q,z.2+w.2⟫_ℝ=(z.1-⟪q,z.2⟫_ℝ)+(w.1-⟪q,w.2⟫_ℝ)
    rw [inner_add_right]
    ring
  map_smul' a z := by
    change a*z.1-⟪q,a • z.2⟫_ℝ=a*(z.1-⟪q,z.2⟫_ℝ)
    rw [inner_smul_right]
    ring

omit [FiniteDimensional ℝ V] in
theorem slack_le_separator (q : V) (hq : ‖q‖≤1) (z : State V) : slack z≤separator q z := by
  have hi := (real_inner_le_norm q z.2).trans
    (mul_le_mul_of_nonneg_right hq (norm_nonneg z.2))
  change z.1-‖z.2‖≤z.1-⟪q,z.2⟫_ℝ
  nlinarith

omit [FiniteDimensional ℝ V] in
/-- Cone positivity is derived for this literal functional, not assumed as an abstract field. -/
theorem separator_positive (q : V) (hq : ‖q‖≤1) {z : State V} (hz : z∈cone) :
    0≤separator q z :=
  (sub_nonneg.mpr hz).trans (slack_le_separator q hq z)

omit [FiniteDimensional ℝ V] in
theorem separator_repair_normalized (q : V) (Fhat : State V →L[ℝ] State V)
    (eta : ℝ) (v : V) : separator q (repair Fhat 1 eta (1,v))=
      (1-eta)*separator q (Fhat (1,v))+eta := by
  simp only [repair,add_apply,smul_apply,map_add,map_smul,resetOperator_normalized,smul_eq_mul]
  change (1-eta)*separator q (Fhat (1,v))+eta*(1-⟪q,(0 : V)⟫_ℝ)=_
  simp

/-- Every feasible weight obeys the exact separating-functional ratio lower bound. -/
theorem separator_ratio_lower (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ)
    (hkappa : kappa≤1) (eta : ℝ) (heta : eta∈feasibleWeights H kappa)
    (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) (v q : V) (hv : ‖v‖≤1) (hq : ‖q‖≤1)
    (hbad : separator q (H a u (1,v))<kappa) :
    (kappa-separator q (H a u (1,v)))/(1-separator q (H a u (1,v)))≤eta := by
  have hm := (le_sigma_iff _ _).mp (heta.2 a u hu) v hv
  have hs := hm.trans (slack_le_separator q hq (repair (H a u) 1 eta (1,v)))
  rw [separator_repair_normalized] at hs
  have hden : 0<1-separator q (H a u (1,v)) := sub_pos.mpr (hbad.trans_le hkappa)
  apply (div_le_iff₀ hden).mpr
  nlinarith

theorem separator_lower_endpoint (H : A → ℝ → State V →L[ℝ] State V) (kappa : ℝ)
    (hkappa : kappa≤1) (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (v q : V) (hv : ‖v‖≤1) (hq : ‖q‖≤1) (hbad : separator q (H a u (1,v))<kappa) :
    (kappa-separator q (H a u (1,v)))/(1-separator q (H a u (1,v)))≤etaStar H kappa :=
  separator_ratio_lower H kappa hkappa _ (etaStar_feasible H kappa hkappa) a u hu v q hv hq hbad

/-- A sound complete margin certificate supplies an upper bracket on the true minimum. -/
theorem certificate_upper_bound (H : A → ℝ → State V →L[ℝ] State V) (kappa etaU : ℝ)
    (hetaU : etaU∈Set.Icc 0 1)
    (hcertificate : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa≤sigma (repair (H a u) 1 etaU)) :
    etaStar H kappa≤etaU := csInf_le (feasible_bddBelow H kappa) ⟨hetaU,hcertificate⟩

end Komorebi.LSM.ConvexRepairBracketing
