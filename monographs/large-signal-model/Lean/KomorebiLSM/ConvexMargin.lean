import KomorebiLSM.RobustOrientedMargin
import Mathlib.Analysis.Convex.Combination

/-! P76: convexity of the actual oriented margin, exact mass and covered
initial states in a fixed geometry. No convexity of geometry search is asserted. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConvexMargin
open LorentzCylinder RobustOrientedMargin
open scoped BigOperators
variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

theorem slack_combination (x y : State V) (a b : ℝ) (ha : 0≤a) (hb : 0≤b) :
    a*slack x+b*slack y≤slack (a • x+b • y) := by
  have hn := norm_add_le (a • x.2) (b • y.2)
  rw [norm_smul,norm_smul,Real.norm_eq_abs,Real.norm_eq_abs,
    abs_of_nonneg ha,abs_of_nonneg hb] at hn
  change a*(x.1-‖x.2‖)+b*(y.1-‖y.2‖)≤a*x.1+b*y.1-‖a • x.2+b • y.2‖
  nlinarith

variable [FiniteDimensional ℝ V]

/-- The minimum over the entire normalized ball is concave in the operator. -/
theorem sigma_combination (F G : State V →L[ℝ] State V) (a b : ℝ)
    (ha : 0≤a) (hb : 0≤b) :
    a*sigma F+b*sigma G≤sigma (a • F+b • G) := by
  apply (le_sigma_iff _ _).mpr
  intro v hv
  have hf := mul_le_mul_of_nonneg_left (sigma_le F v hv) ha
  have hg := mul_le_mul_of_nonneg_left (sigma_le G v hv) hb
  exact (add_le_add hf hg).trans (slack_combination (F (1,v)) (G (1,v)) a b ha hb)

theorem convex_margin_set (kappa : ℝ) :
    Convex ℝ {F : State V →L[ℝ] State V | kappa≤sigma F} := by
  intro F hF G hG a b ha hb hab
  have hf := mul_le_mul_of_nonneg_left hF ha
  have hg := mul_le_mul_of_nonneg_left hG hb
  have hs := sigma_combination F G a b ha hb
  change kappa≤sigma (a • F+b • G)
  have he : a*kappa+b*kappa=kappa := by rw [← add_mul,hab,one_mul]
  linarith

/-- Every finite convex combination of complete branch operators retains the margin. -/
theorem finite_margin {J : Type*} [Fintype J]
    (F : J → State V →L[ℝ] State V) (w : J → ℝ) (kappa : ℝ)
    (hw : ∀ j,0≤w j) (hs : ∑ j,w j=1) (hF : ∀ j,kappa≤sigma (F j)) :
    kappa≤sigma (∑ j,w j • F j) := by
  change (∑ j,w j • F j)∈{F : State V →L[ℝ] State V | kappa≤sigma F}
  exact (convex_margin_set kappa).sum_mem (fun j _ => hw j) hs (fun j _ => hF j)

omit [FiniteDimensional ℝ V] in
/-- Initial coverage is convex in this same fixed probability domain. -/
theorem convex_initial_base : Convex ℝ (probabilityCone (V := V)).base := by
  intro x hx y hy a b ha hb hab
  refine ⟨probabilityCone.add_mem (probabilityCone.smul_mem ha hx.1)
    (probabilityCone.smul_mem hb hy.1),?_⟩
  rw [map_add,map_smul,map_smul,hx.2,hy.2]
  simpa using hab

omit [FiniteDimensional ℝ V] in
theorem finite_initial {J : Type*} [Fintype J]
    (z : J → State V) (w : J → ℝ) (hw : ∀ j,0≤w j) (hs : ∑ j,w j=1)
    (hz : ∀ j,z j∈(probabilityCone (V := V)).base) :
    (∑ j,w j • z j)∈(probabilityCone (V := V)).base :=
  convex_initial_base.sum_mem (fun j _ => hw j) hs (fun j _ => hz j)

abbrev Family (A : Type*) (n : ℕ) (V : Type*) [NormedAddCommGroup V] [NormedSpace ℝ V] :=
  A → Fin n → State V →L[ℝ] State V

variable {A : Type*} {n : ℕ}

/-- Polynomial evaluation is linear in the complete operator family. -/
noncomputable def evaluate (a : A) (u : ℝ) : Family A n V →ₗ[ℝ] (State V →L[ℝ] State V) where
  toFun F := PolynomialGram.operatorPolynomial (F a) u
  map_add' F G := by
    simp [PolynomialGram.operatorPolynomial,smul_add,Finset.sum_add_distrib]
  map_smul' c F := by
    simp only [PolynomialGram.operatorPolynomial,Pi.smul_apply,RingHom.id_apply,
      Finset.smul_sum,smul_smul]
    congr 1
    funext k
    rw [mul_comm]

/-- Exact integrated mass is a linear coefficient constraint, using the
actual uniform-reference polynomial moments. -/
noncomputable def integratedMass (a : A) (z : State V) : Family A n V →ₗ[ℝ] ℝ where
  toFun F := probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • F a k) z)
  map_add' F G := by
    simp [smul_add,Finset.sum_add_distrib,map_add]
  map_smul' c F := by
    have he : (∑ k : Fin n,UniformIntervalMoments.moment k • (c • F a k))=
        c • ∑ k : Fin n,UniformIntervalMoments.moment k • F a k := by
      simp only [Finset.smul_sum,smul_smul]
      congr 1
      funext k
      rw [mul_comm]
    change probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (c • F a k)) z)= _
    rw [he,smul_apply,map_smul]
    rfl

/-- The actual fixed-geometry feasible coefficient set. -/
def feasible (kappa : A → ℝ → ℝ) : Set (Family A n V) :=
  {F | (∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa a u≤sigma (evaluate a u F)) ∧
    ∀ a z,integratedMass a z F=probabilityCone.mass z}

theorem convex_feasible (kappa : A → ℝ → ℝ) : Convex ℝ (feasible (n := n) (V := V) kappa) := by
  intro F hF G hG a b ha hb hab
  constructor
  · intro action u hu
    rw [map_add,map_smul,map_smul]
    exact convex_margin_set (kappa action u) (hF.1 action u hu) (hG.1 action u hu) ha hb hab
  · intro action z
    rw [map_add,map_smul,map_smul,hF.2 action z,hG.2 action z]
    change a*probabilityCone.mass z+b*probabilityCone.mass z=probabilityCone.mass z
    rw [← add_mul,hab,one_mul]

/-- A convex data-consistency set can be intersected with the actual margin,
mass and initial constraints. Geometry is fixed throughout. -/
theorem convex_data_feasible (kappa : A → ℝ → ℝ)
    (U : Set (Family A n V × State V)) (hU : Convex ℝ U) :
    Convex ℝ {p : Family A n V × State V |
      p.1∈feasible kappa ∧ p.2∈probabilityCone.base ∧ p∈U} := by
  intro x hx y hy a b ha hb hab
  exact ⟨convex_feasible kappa hx.1 hy.1 ha hb hab,
    convex_initial_base hx.2.1 hy.2.1 ha hb hab,hU hx.2.2 hy.2.2 ha hb hab⟩

theorem finite_feasible {J : Type*} [Fintype J]
    (F : J → Family A n V) (w : J → ℝ) (kappa : A → ℝ → ℝ)
    (hw : ∀ j,0≤w j) (hs : ∑ j,w j=1) (hF : ∀ j,F j∈feasible kappa) :
    (∑ j,w j • F j)∈feasible kappa := by
  have hc : Convex ℝ (feasible (A := A) (n := n) (V := V) kappa) := convex_feasible kappa
  exact hc.sum_mem (t := Finset.univ) (w := w) (z := F)
    (fun j _ => hw j) hs (fun j _ => hF j)

theorem hull_feasible {J : Type*} (F : J → Family A n V) (kappa : A → ℝ → ℝ)
    (hF : ∀ j,F j∈feasible kappa) :
    convexHull ℝ (Set.range F)⊆feasible kappa := by
  apply convexHull_min
  · rintro _ ⟨j,rfl⟩
    exact hF j
  · exact convex_feasible kappa

omit [FiniteDimensional ℝ V] in
theorem hull_initial {J : Type*} (z : J → State V)
    (hz : ∀ j,z j∈(probabilityCone (V := V)).base) :
    convexHull ℝ (Set.range z)⊆(probabilityCone (V := V)).base :=
  convexHull_min (Set.range_subset_iff.mpr hz) convex_initial_base

variable [MeasurableSpace V] [BorelSpace V]

open MeasureTheory in
/-- Actual feasible coefficients with a nonnegative common margin construct
the literal polynomial probability instrument. -/
noncomputable def instrument (kappa : A → ℝ → ℝ) (F : Family A n V)
    (hF : F∈feasible kappa) (hk : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → 0≤kappa a u) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone (V := V)) UniformIntervalMoments.measure where
  op a := PolynomialGram.operatorPolynomial (F a)
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  positive a := PolynomialGram.uniform_ae_interval.mono fun u hu z hz => by
    apply preserves_of_normalized _ _ hz
    intro v hv
    have hs := ((hk a u hu).trans (hF.1 a u hu)).trans (sigma_le _ v hv)
    change ‖(PolynomialGram.operatorPolynomial (F a) u (1,v)).2‖≤
      (PolynomialGram.operatorPolynomial (F a) u (1,v)).1
    unfold slack at hs
    change 0≤(PolynomialGram.operatorPolynomial (F a) u (1,v)).1-
      ‖(PolynomialGram.operatorPolynomial (F a) u (1,v)).2‖ at hs
    linarith
  mass_preserving a z := by
    rw [PolynomialGram.operatorPolynomial_integral]
    exact hF.2 a z

open MeasureTheory in
/-- The complete-family and initial hulls may use independent coefficients.
Every selected pair has actual normalized record laws at every horizon. -/
theorem hull_record_probability [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    {J K : Type*} (families : J → Family A n V) (initials : K → State V)
    (kappa : A → ℝ → ℝ) (hF : ∀ j,families j∈feasible kappa)
    (hz : ∀ k,initials k∈(probabilityCone (V := V)).base)
    (hk : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → 0≤kappa a u)
    (F : Family A n V) (hFh : F∈convexHull ℝ (Set.range families))
    (z : State V) (hzh : z∈convexHull ℝ (Set.range initials))
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw
      (instrument kappa F (hull_feasible families kappa hF hFh) hk) π z N) :=
  ContinuousRecords.recordLaw_probability _ π ⟨z,hull_initial initials hz hzh⟩ N

end Komorebi.LSM.ConvexMargin
