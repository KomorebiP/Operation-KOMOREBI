import KomorebiLSM.RotationModel
import KomorebiLSM.LorentzBaseNorm
import KomorebiLSM.RegularPolygon
import KomorebiLSM.PolicyComparison
import KomorebiLSM.PositiveLift
import KomorebiLSM.BehaviorProbability
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-! P47's explicit rational diamond approximation. The four actual generators
are (1,1,0), (1,0,1), (1,-1,0), and (1,0,-1). -/
set_option autoImplicit false
set_option maxHeartbeats 800000
namespace Komorebi.LSM.RotationApproximation
noncomputable section
open scoped BigOperators
open FiniteInstruments

abbrev State := Fin 3 → ℝ

noncomputable def mass : State →ₗ[ℝ] ℝ := LinearMap.proj 0

def initial : State := ![1,1,0]

def synthesisMatrix : Matrix (Fin 3) (Fin 4) ℝ :=
  !![1,1,1,1; 1,0,-1,0; 0,1,0,-1]

noncomputable def synthesis : (Fin 4 → ℝ) →ₗ[ℝ] State := synthesisMatrix.mulVecLin

def rotationMatrix (α : ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  !![1,0,0; 0,3*α/5,-4*α/5; 0,4*α/5,3*α/5]

def probeMatrix (o : Bool) : Matrix (Fin 3) (Fin 3) ℝ :=
  if o then !![1/2,-1/2,0; 1/2,-1/2,0; 0,0,0]
  else !![1/2,1/2,0; 1/2,1/2,0; 0,0,0]

/-- False is the rotate action, true is the probe action. -/
def branchMatrix (α : ℝ) (s : Bool × Bool) : Matrix (Fin 3) (Fin 3) ℝ :=
  if s.1 then probeMatrix s.2 else if s.2 then 0 else rotationMatrix α

noncomputable def operator (α : ℝ) (s : Bool × Bool) : State →ₗ[ℝ] State :=
  (branchMatrix α s).mulVecLin

/-- Unused diamond mass is distributed uniformly over the four vertices. -/
def slack (α : ℝ) : ℝ := (1-7*α/5)/4

def rotationLift (α : ℝ) : Matrix (Fin 4) (Fin 4) ℝ :=
  !![slack α+3*α/5, slack α, slack α, slack α+4*α/5;
     slack α+4*α/5, slack α+3*α/5, slack α, slack α;
     slack α, slack α+4*α/5, slack α+3*α/5, slack α;
     slack α, slack α, slack α+4*α/5, slack α+3*α/5]

def probeLift (o : Bool) : Matrix (Fin 4) (Fin 4) ℝ :=
  if o then !![0,1/2,1,1/2; 0,0,0,0; 0,0,0,0; 0,0,0,0]
  else !![1,1/2,0,1/2; 0,0,0,0; 0,0,0,0; 0,0,0,0]

def liftMatrix (α : ℝ) (s : Bool × Bool) : Matrix (Fin 4) (Fin 4) ℝ :=
  if s.1 then probeLift s.2 else if s.2 then 0 else rotationLift α

/-- The displayed four-generator lift intertwines the actual matrices exactly. -/
theorem matrix_intertwining (α : ℝ) (s : Bool × Bool) :
    branchMatrix α s * synthesisMatrix = synthesisMatrix * liftMatrix α s := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    norm_num [branchMatrix, rotationMatrix, probeMatrix, synthesisMatrix,
      liftMatrix, rotationLift, probeLift, Matrix.mul_apply, Fin.sum_univ_succ, slack] <;> ring

/-- Every lifted entry is nonnegative in the stated diamond attenuation range. -/
theorem lift_nonnegative (α : ℝ) (hα : 0 ≤ α) (hupper : α ≤ 5/7)
    (s : Bool × Bool) (i j : Fin 4) : 0 ≤ liftMatrix α s i j := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> fin_cases i <;> fin_cases j <;>
    norm_num [liftMatrix, rotationLift, probeLift, slack] <;> nlinarith

/-- Column mass is one for each action, including all its observation branches. -/
theorem lift_mass (α : ℝ) (a : Bool) (j : Fin 4) :
    ∑ o : Bool, ∑ i : Fin 4, liftMatrix α (a,o) i j = 1 := by
  cases a <;> fin_cases j <;>
    norm_num [liftMatrix, rotationLift, probeLift, slack, Fin.sum_univ_succ,
      Fintype.sum_bool, Matrix.cons_val_two, Matrix.cons_val_three] <;> ring

/-- The synthesis reads ordinary lifted probability mass in coordinate zero. -/
theorem synthesis_mass : mass.comp synthesis = FiniteInstruments.mass := by
  apply LinearMap.ext
  intro a
  simp [mass, synthesis, synthesisMatrix, Matrix.mulVec, dotProduct,
    Fin.sum_univ_succ, FiniteInstruments.mass_apply]

/-- The initial state is the first diamond generator with a valid point prior. -/
theorem synthesis_initial : synthesis (FiniteBayes.pointMass (0 : Fin 4)) = initial := by
  ext i
  fin_cases i <;>
    norm_num [synthesis, synthesisMatrix, initial, Matrix.mulVec, dotProduct,
      Fin.sum_univ_succ, FiniteBayes.pointMass]

/-- The exact matrix relation also holds as a relation of linear maps. -/
theorem operator_intertwining (α : ℝ) (s : Bool × Bool) :
    (operator α s).comp synthesis = synthesis.comp (liftMatrix α s).mulVecLin := by
  change (branchMatrix α s).mulVecLin.comp synthesisMatrix.mulVecLin =
    synthesisMatrix.mulVecLin.comp (liftMatrix α s).mulVecLin
  rw [← Matrix.mulVecLin_mul, ← Matrix.mulVecLin_mul]
  exact congrArg Matrix.mulVecLin (matrix_intertwining α s)

/-- A concrete finite stochastic instrument, without a supplied positivity witness. -/
noncomputable def diamondInstrument (α : ℝ) (hα : 0 ≤ α) (hupper : α ≤ 5/7) :
    Instrument (Fin 4) Bool Bool where
  matrix a o := liftMatrix α (a,o)
  nonneg a o i j := lift_nonnegative α hα hupper (a,o) i j
  mass_one := lift_mass α

/-- The positive finite lift is correct on every word, not just a test prefix. -/
theorem diamond_word_probability (α : ℝ) (hα : 0 ≤ α) (hupper : α ≤ 5/7)
    (w : List (Bool × Bool)) :
    mass (wordAction (operator α) w initial) =
      FiniteInstruments.mass (wordAction (diamondInstrument α hα hupper).branch w
        (FiniteBayes.pointMass (0 : Fin 4))) := by
  rw [← synthesis_initial]
  exact PositiveLift.lifted_word_probability (operator α) synthesis mass synthesis_mass
    (liftMatrix α) (operator_intertwining α) w (FiniteBayes.pointMass (0 : Fin 4))

/-- The rational approximation is valid at all horizons. -/
theorem diamond_all_word_bounds (α : ℝ) (hα : 0 ≤ α) (hupper : α ≤ 5/7)
    (w : List (Bool × Bool)) :
    0 ≤ mass (wordAction (operator α) w initial) ∧
      mass (wordAction (operator α) w initial) ≤ 1 := by
  rw [diamond_word_probability α hα hupper]
  exact (diamondInstrument α hα hupper).word_probability w _ (FiniteInstruments.point_prior 0)

/-- The stated manuscript example alpha=2/3 is an exact rational certificate. -/
theorem rational_two_thirds_valid (w : List (Bool × Bool)) :
    0 ≤ mass (wordAction (operator (2/3)) w initial) ∧
      mass (wordAction (operator (2/3)) w initial) ≤ 1 :=
  diamond_all_word_bounds (2/3) (by norm_num) (by norm_num) w

/-- Explicit coordinate formula for the four-generator synthesis. -/
theorem synthesis_apply (a : Fin 4 → ℝ) :
    synthesis a = ![a 0+a 1+a 2+a 3, a 0-a 2, a 1-a 3] := by
  ext i
  fin_cases i <;> simp [synthesis, synthesisMatrix, Matrix.mulVec, dotProduct,
    Fin.sum_univ_succ, Matrix.cons_val_two] <;> ring

/-- The actual normalized axes generate precisely the rational diamond cone. -/
theorem diamond_hull : PositiveLift.hull synthesis =
    {z : State | |z 1|+|z 2| ≤ z 0} := by
  ext z
  constructor
  · rintro ⟨a,ha,rfl⟩
    simp only [synthesis_apply, Set.mem_ofPred_eq, Matrix.cons_val_one,
      Matrix.cons_val_two, Matrix.head_cons, Matrix.tail_cons, Matrix.cons_val_zero]
    have hx : |a 0-a 2| ≤ a 0+a 2 := by
      simpa only [abs_of_nonneg (ha 0), abs_of_nonneg (ha 2)] using abs_sub (a 0) (a 2)
    have hy : |a 1-a 3| ≤ a 1+a 3 := by
      simpa only [abs_of_nonneg (ha 1), abs_of_nonneg (ha 3)] using abs_sub (a 1) (a 3)
    linarith
  · intro hz
    change |z 1|+|z 2| ≤ z 0 at hz
    let b : ℝ := (z 0-|z 1|-|z 2|)/2
    let a : Fin 4 → ℝ := ![max (z 1) 0+b, max (z 2) 0,
      max (-z 1) 0+b, max (-z 2) 0]
    have hb : 0 ≤ b := by dsimp [b]; linarith
    have hdiff : ∀ x : ℝ, max x 0-max (-x) 0=x := by
      intro x
      rcases le_total 0 x with h|h
      · rw [max_eq_left h, max_eq_right (neg_nonpos.mpr h)]; ring
      · rw [max_eq_right h, max_eq_left (neg_nonneg.mpr h)]; ring
    have habs : ∀ x : ℝ, max x 0+max (-x) 0=|x| := by
      intro x
      rcases le_total 0 x with h|h
      · rw [max_eq_left h, max_eq_right (neg_nonpos.mpr h),abs_of_nonneg h]; ring
      · rw [max_eq_right h, max_eq_left (neg_nonneg.mpr h),abs_of_nonpos h]; ring
    refine ⟨a, ?_, ?_⟩
    · intro j
      fin_cases j
      · exact add_nonneg (le_max_right _ _) hb
      · exact le_max_right _ _
      · exact add_nonneg (le_max_right _ _) hb
      · exact le_max_right _ _
    · rw [synthesis_apply]
      ext i
      fin_cases i
      · change (max (z 1) 0+b)+max (z 2) 0+(max (-z 1) 0+b)+max (-z 2) 0=z 0
        dsimp [b]
        nlinarith [habs (z 1), habs (z 2)]
      · change (max (z 1) 0+b)-(max (-z 1) 0+b)=z 1
        linarith [hdiff (z 1)]
      · exact hdiff (z 2)

/-- At alpha one these are literally the source model's branch operators. -/
theorem exact_operator (s : Bool × Bool) : operator 1 s = RotationModel.operator s := by
  rw [RotationModel.operator_matrix]
  change (branchMatrix 1 s).mulVecLin = (RotationModel.matrix s).mulVecLin
  congr 1
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    norm_num [branchMatrix, rotationMatrix, probeMatrix, RotationModel.matrix,
      RotationModel.rotationMatrix, RotationModel.probeMatrix0, RotationModel.probeMatrix1]

/-- The attenuation leaves the probability mass unchanged. -/
theorem operator_mass (α : ℝ) (a : Bool) (z : State) :
    ∑ o : Bool, mass (operator α (a,o) z)=mass z := by
  cases a <;> simp [mass, operator, branchMatrix, probeMatrix, rotationMatrix,
    Matrix.mulVec, dotProduct, Fin.sum_univ_succ]
  all_goals ring

/-- The actual attenuated rotation contracts the spatial Euclidean radius. -/
theorem rotation_radius (α : ℝ) (hα : 0 ≤ α) (z : State) :
    Real.sqrt (((operator α (false,false) z) 1)^2+((operator α (false,false) z) 2)^2) =
      α*Real.sqrt ((z 1)^2+(z 2)^2) := by
  have he : ((operator α (false,false) z) 1)^2+((operator α (false,false) z) 2)^2 =
      α^2*((z 1)^2+(z 2)^2) := by
    simp [operator,branchMatrix,rotationMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
    ring
  rw [he, Real.sqrt_mul (sq_nonneg α), Real.sqrt_sq_eq_abs, abs_of_nonneg hα]

/-- Every actual probe is the same reset as in the exact model. -/
theorem probe_reset (α : ℝ) (o : Bool) (z : State) :
    operator α (true,o) z = ((if o then z 0-z 1 else z 0+z 1)/2) • initial := by
  cases o <;> ext i <;> fin_cases i <;>
    simp [operator,branchMatrix,probeMatrix,initial,Matrix.mulVec,dotProduct,
      Fin.sum_univ_succ] <;> ring

/-- Finite normalized vertices plus an actual inscribed ball provide invariant
operators. The regular-polygon geometry is a separate, reusable input. -/
theorem finite_hull_invariant {J : Type*} [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] State) (hn : mass.comp V=FiniteInstruments.mass)
    (hvertices : ∀ j, Real.sqrt ((PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2) ≤ 1)
    (hinit : initial ∈ PositiveLift.hull V)
    (r : ℝ) (hball : ∀ z : State, mass z=1 →
      Real.sqrt ((z 1)^2+(z 2)^2) ≤ r → z ∈ PositiveLift.hull V)
    (α : ℝ) (hα : 0 ≤ α) (hαr : α ≤ r) (s : Bool × Bool) :
    ∀ z ∈ PositiveLift.hull V, operator α s z ∈ PositiveLift.hull V := by
  apply (PositiveLift.invariant_iff_generators V (operator α s)).mpr
  intro j
  have hmass := PositiveLift.mass_generator V mass hn j
  have hm : PositiveLift.generator V j 0=1 := hmass
  rcases s with ⟨a,o⟩
  cases a <;> cases o
  · apply hball
    · simpa [mass,operator,branchMatrix,rotationMatrix,Matrix.mulVec,dotProduct,
        Fin.sum_univ_succ] using hm
    · rw [rotation_radius α hα]
      exact (mul_le_mul_of_nonneg_left (hvertices j) hα).trans (by simpa using hαr)
  · simpa [operator,branchMatrix] using PositiveLift.hull_zero V
  · rw [probe_reset]
    apply PositiveLift.hull_smul V _ hinit
    have hs := Real.sq_sqrt (show 0 ≤ (PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2 by positivity)
    have hn0 := Real.sqrt_nonneg ((PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2)
    have hr0 := hvertices j
    simp only [Bool.false_eq_true, reduceIte, hm]
    nlinarith [sq_nonneg (PositiveLift.generator V j 2)]
  · rw [probe_reset]
    apply PositiveLift.hull_smul V _ hinit
    have hs := Real.sq_sqrt (show 0 ≤ (PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2 by positivity)
    have hn0 := Real.sqrt_nonneg ((PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2)
    have hr0 := hvertices j
    simp only [reduceIte, hm]
    nlinarith [sq_nonneg (PositiveLift.generator V j 2)]

/-- A finite positive stochastic lift is constructed from the vertex geometry,
with exact initial mass and every word probability retained. -/
theorem finite_vertex_certificate {J : Type*} [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] State) (hn : mass.comp V=FiniteInstruments.mass)
    (hvertices : ∀ j, Real.sqrt ((PositiveLift.generator V j 1)^2+
      (PositiveLift.generator V j 2)^2) ≤ 1)
    (hinit : initial ∈ PositiveLift.hull V)
    (r : ℝ) (hball : ∀ z : State, mass z=1 →
      Real.sqrt ((z 1)^2+(z 2)^2) ≤ r → z ∈ PositiveLift.hull V)
    (α : ℝ) (hα : 0 ≤ α) (hαr : α ≤ r) :
    ∃ (M : Bool × Bool → Matrix J J ℝ) (a₀ : J → ℝ),
      (∀ s i j, 0 ≤ M s i j) ∧ FiniteBayes.IsPrior a₀ ∧ V a₀=initial ∧
      (∀ s, (operator α s).comp V=V.comp (M s).mulVecLin) ∧
      (∀ a j, ∑ o : Bool, ∑ i, M (a,o) i j=1) ∧
      (∀ w, mass (wordAction (operator α) w initial)=
        FiniteInstruments.mass (wordAction (fun s => (M s).mulVecLin) w a₀)) := by
  classical
  have hi := finite_hull_invariant V hn hvertices hinit r hball α hα hαr
  choose M hM he using fun s => (PositiveLift.positive_lift_iff V (operator α s)).mp (hi s)
  obtain ⟨a₀,ha₀,hVa⟩ := hinit
  have hp : FiniteBayes.IsPrior a₀ := by
    refine ⟨ha₀, ?_⟩
    have h := congrArg mass hVa
    have hnormal := PositiveLift.normalized_mass V mass hn a₀
    change mass (V a₀)=1 at h
    exact hnormal.symm.trans h
  refine ⟨M,a₀,hM,hp,hVa,he,PositiveLift.lifted_mass (operator α) V mass hn
    (operator_mass α) M he, ?_⟩
  intro w
  rw [← hVa]
  exact PositiveLift.lifted_word_probability (operator α) V mass hn M he w a₀

/-- Both exact and attenuated models preserve the same actual Lorentz cone. -/
theorem cone_invariant (α : ℝ) (hα : 0 ≤ α) (hα1 : α ≤ 1)
    (s : Bool × Bool) {z : State} (hz : z ∈ RotationModel.cone) :
    operator α s z ∈ RotationModel.cone := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o
  · change Real.sqrt (((operator α (false,false) z) 1)^2+
      ((operator α (false,false) z) 2)^2) ≤ (operator α (false,false) z) 0
    rw [rotation_radius α hα]
    have h0 : (operator α (false,false) z) 0=z 0 := by
      simp [operator,branchMatrix,rotationMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
    rw [h0]
    have hmul := mul_le_mul_of_nonneg_right hα1
      (Real.sqrt_nonneg ((z 1)^2+(z 2)^2))
    have hmul' : α*Real.sqrt ((z 1)^2+(z 2)^2) ≤ Real.sqrt ((z 1)^2+(z 2)^2) := by
      simpa only [one_mul] using hmul
    exact hmul'.trans hz
  · have hzero : operator α (false,true) z=0 := by simp [operator,branchMatrix]
    rw [hzero]
    exact RotationModel.cone_zero
  · have he : operator α (true,false)=operator 1 (true,false) := rfl
    rw [he,exact_operator]
    exact RotationModel.operator_cone _ hz
  · have he : operator α (true,true)=operator 1 (true,true) := rfl
    rw [he,exact_operator]
    exact RotationModel.operator_cone _ hz

/-- The change of a rotate branch is purely spatial with exact known radius. -/
theorem rotation_difference_radius (α : ℝ) (hα1 : α ≤ 1) (z : State) :
    Real.sqrt ((((operator 1 (false,false)-operator α (false,false)) z) 1)^2+
      (((operator 1 (false,false)-operator α (false,false)) z) 2)^2) =
      (1-α)*Real.sqrt ((z 1)^2+(z 2)^2) := by
  have he : (((operator 1 (false,false)-operator α (false,false)) z) 1)^2+
      (((operator 1 (false,false)-operator α (false,false)) z) 2)^2 =
      (1-α)^2*((z 1)^2+(z 2)^2) := by
    simp [operator,branchMatrix,rotationMatrix,dotProduct,Fin.sum_univ_succ]
    ring
  rw [he,Real.sqrt_mul (sq_nonneg (1-α)),Real.sqrt_sq_eq_abs,
    abs_of_nonneg (sub_nonneg.mpr hα1)]

/-- The actual finite-dimensional operators have canonical continuous versions. -/
noncomputable def continuousOperator (α : ℝ) (s : Bool × Bool) : State →L[ℝ] State :=
  (operator α s).toContinuousLinearMap

section LawComparison
variable (C : BaseNorm.ProbabilityCone State)
variable (hcarrier : C.carrier=RotationModel.cone) (hmass : C.mass=mass)
variable (hvalue : ∀ z : State, C.value z=max |z 0| (Real.sqrt ((z 1)^2+(z 2)^2)))
include hcarrier hmass

/-- Positivity and exact action mass are established on the common Lorentz cone. -/
theorem common_cone_instrument (α : ℝ) (hα : 0 ≤ α) (hα1 : α ≤ 1) (a : Bool) :
    C.Instrument (fun o => (continuousOperator α (a,o)).toLinearMap) := by
  constructor
  · intro o z hz
    change operator α (a,o) z ∈ C.carrier
    rw [hcarrier] at hz ⊢
    exact cone_invariant α hα hα1 _ hz
  · intro z
    change (∑ o : Bool, C.mass (operator α (a,o) z))=C.mass z
    simpa only [hmass] using operator_mass α a z

include hvalue

/-- Only the rotate action changes. Its summed branch discrepancy is at most
one minus attenuation in the actual Lorentz base norm. -/
theorem action_discrepancy (α : ℝ) (hα1 : α ≤ 1) (a : Bool)
    (z : State) (hz : z ∈ C.base) :
    C.discrepancy (fun o => operator 1 (a,o)) (fun o => operator α (a,o)) z ≤ 1-α := by
  have hzcone : z ∈ RotationModel.cone := by rw [← hcarrier]; exact hz.1
  have h0 : z 0=1 := by simpa only [hmass,mass,LinearMap.proj_apply] using hz.2
  have hr : Real.sqrt ((z 1)^2+(z 2)^2) ≤ 1 := by
    simpa only [RotationModel.cone_iff,h0] using hzcone
  cases a
  · have hz0 : ((operator 1 (false,false)-operator α (false,false)) z) 0=0 := by
      simp [operator,branchMatrix,rotationMatrix,dotProduct,Fin.sum_univ_succ]
    have hz1 : (operator 1 (false,true)-operator α (false,true)) z=0 := by
      simp [operator,branchMatrix]
    rw [BaseNorm.ProbabilityCone.discrepancy,Fintype.sum_bool,hz1,C.value_zero,zero_add,
      hvalue,hz0,abs_zero,max_eq_right (Real.sqrt_nonneg _),rotation_difference_radius α hα1]
    simpa only [mul_one] using mul_le_mul_of_nonneg_left hr (sub_nonneg.mpr hα1)
  · have he : ∀ o : Bool, operator 1 (true,o)=operator α (true,o) := by
      intro o
      cases o <;> rfl
    simp only [BaseNorm.ProbabilityCone.discrepancy,he,sub_self,LinearMap.zero_apply,
      C.value_zero,Finset.sum_const_zero]
    exact sub_nonneg.mpr hα1

/-- P47's error bound holds for actual observation laws under an arbitrary
shared randomized history-dependent policy, including zero policy weights. -/
theorem shared_policy_tv_bound
    (π : List (Bool × Bool) → Bool → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (α : ℝ) (hα : 0 ≤ α) (hα1 : α ≤ 1) (n : ℕ) :
    FiniteTV.distance
      (ObservationTree.observationLaw C π (fun _ s => continuousOperator 1 s) n initial)
      (ObservationTree.observationLaw C π (fun _ s => continuousOperator α s) n initial) ≤
        min 1 ((n:ℝ)*(1-α)/2) := by
  have hi : initial ∈ C.base := by
    refine ⟨?_,?_⟩
    · rw [hcarrier]
      exact RotationModel.initial_mem
    · rw [hmass]
      rfl
  have h := ObservationTree.shared_policy_observation_tv_bound C π hπ
    (fun _ s => continuousOperator 1 s) (fun _ s => continuousOperator α s)
    (fun _ a => common_cone_instrument C hcarrier hmass 1 (by norm_num) (by norm_num) a)
    (fun _ a => common_cone_instrument C hcarrier hmass α hα hα1 a)
    (fun _ => 1-α) (fun _ a z hz => action_discrepancy C hcarrier hmass hvalue α hα1 a z hz)
    n initial initial hi hi
  simpa only [sub_self,C.value_zero,zero_div,Finset.sum_const,Finset.card_range,
    nsmul_eq_mul,zero_add] using h

end LawComparison

/-- The common-policy bound instantiated with the actual, constructed Lorentz
base norm; no norm estimate or discrepancy bound is assumed. -/
theorem model_shared_policy_tv_bound
    (π : List (Bool × Bool) → Bool → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (α : ℝ) (hα : 0 ≤ α) (hα1 : α ≤ 1) (n : ℕ) :
    FiniteTV.distance
      (ObservationTree.observationLaw LorentzBaseNorm.coneInstance π
        (fun _ s => continuousOperator 1 s) n initial)
      (ObservationTree.observationLaw LorentzBaseNorm.coneInstance π
        (fun _ s => continuousOperator α s) n initial) ≤ min 1 ((n:ℝ)*(1-α)/2) := by
  exact shared_policy_tv_bound LorentzBaseNorm.coneInstance
    LorentzBaseNorm.coneInstance_carrier_eq LorentzBaseNorm.coneInstance_mass_eq
    LorentzBaseNorm.value_eq_sqrt π hπ α hα hα1 n

/-- Two exact rational word calculations show that attenuation changes the law. -/
theorem exact_and_two_thirds_probe :
    mass (wordAction (operator 1) [(false,false),(true,false)] initial)=4/5 ∧
    mass (wordAction (operator (2/3)) [(false,false),(true,false)] initial)=7/10 := by
  norm_num [wordAction,operator,branchMatrix,probeMatrix,rotationMatrix,initial,mass,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

/-- Embed the actual regular-polygon vertices at mass one. -/
def vertexMatrix (n : ℕ) : Matrix (Fin 3) (Fin n) ℝ := fun i j =>
  LorentzBaseNorm.point 1 (RegularPolygon.vertex n j) i

noncomputable def vertexSynthesis (n : ℕ) : (Fin n → ℝ) →ₗ[ℝ] State :=
  (vertexMatrix n).mulVecLin

theorem vertex_generator (n : ℕ) (j : Fin n) :
    PositiveLift.generator (vertexSynthesis n) j=
      LorentzBaseNorm.point 1 (RegularPolygon.vertex n j) := by
  ext i
  simp [PositiveLift.generator,vertexSynthesis,vertexMatrix,Matrix.mulVec,dotProduct,
    FiniteBayes.pointMass]

theorem vertex_mass (n : ℕ) : mass.comp (vertexSynthesis n)=FiniteInstruments.mass := by
  ext a
  simp [mass,vertexSynthesis,vertexMatrix,Matrix.mulVec,dotProduct,FiniteInstruments.mass_apply]

/-- Mass-one embedding preserves convex combinations exactly. -/
theorem point_convex_combination (a b : ℝ) (hab : a+b=1) (x y : ℂ) :
    LorentzBaseNorm.point 1 (a • x+b • y)=
      a • LorentzBaseNorm.point 1 x+b • LorentzBaseNorm.point 1 y := by
  ext i
  fin_cases i
  · change 1=a*1+b*1
    linarith
  · simp [LorentzBaseNorm.point]
  · simp [LorentzBaseNorm.point]

/-- Every point of the regular polygon is a positive combination of the
actual normalized synthesis columns. -/
theorem polygon_point_mem_hull (n : ℕ) {w : ℂ} (hw : w ∈ RegularPolygon.polygon n) :
    LorentzBaseNorm.point 1 w ∈ PositiveLift.hull (vertexSynthesis n) := by
  let S : Set ℂ := {w | LorentzBaseNorm.point 1 w ∈ PositiveLift.hull (vertexSynthesis n)}
  have hs : Set.range (RegularPolygon.vertex n) ⊆ S := by
    rintro _ ⟨j,rfl⟩
    change LorentzBaseNorm.point 1 (RegularPolygon.vertex n j) ∈ PositiveLift.hull (vertexSynthesis n)
    rw [← vertex_generator]
    exact PositiveLift.generator_mem (vertexSynthesis n) j
  have hc : Convex ℝ S := by
    intro x hx y hy a b ha hb hab
    change LorentzBaseNorm.point 1 (a • x+b • y) ∈ PositiveLift.hull (vertexSynthesis n)
    rw [point_convex_combination a b hab]
    exact PositiveLift.hull_convex (vertexSynthesis n) hx hy ha hb hab
  exact (convexHull_min hs hc) hw

/-- The finite vertex hull includes the full inscribed Euclidean disk. -/
theorem regular_polygon_inscribed_hull (n : ℕ) (hn : 3 ≤ n) (z : State)
    (hm : mass z=1) (hz : Real.sqrt ((z 1)^2+(z 2)^2) ≤ Real.cos (Real.pi/(n:ℝ))) :
    z ∈ PositiveLift.hull (vertexSynthesis n) := by
  have hball : LorentzBaseNorm.spatial z ∈
      Metric.closedBall (0:ℂ) (Real.cos (Real.pi/(n:ℝ))) := by
    simpa only [Metric.mem_closedBall,dist_zero_right,LorentzBaseNorm.spatial_norm] using hz
  have hp := RegularPolygon.closedBall_subset_polygon n hn hball
  have he : LorentzBaseNorm.point 1 (LorentzBaseNorm.spatial z)=z := by
    have h0 : z 0=1 := hm
    simpa only [h0] using LorentzBaseNorm.point_mass_spatial z
  rw [← he]
  exact polygon_point_mem_hull n hp

/-- P47's general n-vertex positive stochastic lift, constructed from the
proved inscribed-disk geometry of the actual regular polygon. -/
theorem regular_polygon_positive_lift (n : ℕ) (hn : 3 ≤ n)
    (α : ℝ) (hα : 0 ≤ α) (hsmall : α ≤ Real.cos (Real.pi/(n:ℝ))) :
    ∃ (M : Bool × Bool → Matrix (Fin n) (Fin n) ℝ) (a₀ : Fin n → ℝ),
      (∀ s i j, 0 ≤ M s i j) ∧ FiniteBayes.IsPrior a₀ ∧ vertexSynthesis n a₀=initial ∧
      (∀ s, (operator α s).comp (vertexSynthesis n)=(vertexSynthesis n).comp (M s).mulVecLin) ∧
      (∀ a j, ∑ o : Bool, ∑ i, M (a,o) i j=1) ∧
      (∀ w, mass (wordAction (operator α) w initial)=
        FiniteInstruments.mass (wordAction (fun s => (M s).mulVecLin) w a₀)) := by
  apply finite_vertex_certificate (vertexSynthesis n) (vertex_mass n) ?_ ?_
    (Real.cos (Real.pi/(n:ℝ))) (regular_polygon_inscribed_hull n hn) α hα hsmall
  · intro j
    rw [vertex_generator, ← LorentzBaseNorm.spatial_norm,LorentzBaseNorm.spatial_point,
      RegularPolygon.vertex_norm]
  · change LorentzBaseNorm.point 1 (1:ℂ) ∈ PositiveLift.hull (vertexSynthesis n)
    exact polygon_point_mem_hull n (RegularPolygon.one_mem_polygon n (by omega))

/-- The explicit ceiling bound in the manuscript supplies a genuine finite
certificate for every positive attenuation loss no larger than one. -/
theorem sufficient_vertex_positive_lift (η : ℝ) (hη : 0 < η) (hη1 : η ≤ 1) :
    let n := RegularPolygon.sufficientVertexCount η
    ∃ (M : Bool × Bool → Matrix (Fin n) (Fin n) ℝ) (a₀ : Fin n → ℝ),
      (∀ s i j, 0 ≤ M s i j) ∧ FiniteBayes.IsPrior a₀ ∧ vertexSynthesis n a₀=initial ∧
      (∀ s, (operator (1-η) s).comp (vertexSynthesis n)=
        (vertexSynthesis n).comp (M s).mulVecLin) ∧
      (∀ a j, ∑ o : Bool, ∑ i, M (a,o) i j=1) ∧
      (∀ w, mass (wordAction (operator (1-η)) w initial)=
        FiniteInstruments.mass (wordAction (fun s => (M s).mulVecLin) w a₀)) := by
  obtain ⟨hn,hsmall⟩ := RegularPolygon.sufficient_vertex_count η hη
  exact regular_polygon_positive_lift _ hn (1-η) (sub_nonneg.mpr hη1) hsmall

/-- The four rational generators span the actual three-dimensional state. -/
theorem diamond_synthesis_surjective : Function.Surjective synthesis := by
  intro z
  let b : ℝ := (z 0-z 1-z 2)/2
  refine ⟨![z 1+b,z 2,b,0], ?_⟩
  rw [synthesis_apply]
  ext i
  fin_cases i <;> simp [b]
  all_goals ring

/-- A genuine positive inradius forces the regular vertex synthesis to have
full row rank; the finite positive certificate does not assume this rank. -/
theorem regular_vertex_surjective (n : ℕ) (hn : 3 ≤ n) :
    Function.Surjective (vertexSynthesis n) := by
  let r : ℝ := Real.cos (Real.pi/(n:ℝ))
  have hnR : (3:ℝ) ≤ n := by exact_mod_cast hn
  have hn0 : (0:ℝ) < n := by linarith
  have hr : 0 < r := by
    dsimp [r]
    apply Real.cos_pos_of_mem_Ioo
    constructor
    · have hangle : 0 ≤ Real.pi/(n:ℝ) := by positivity
      linarith [Real.pi_pos]
    · apply (div_lt_iff₀ hn0).mpr
      nlinarith [Real.pi_pos]
  have hpoint : ∀ w : ℂ, ‖w‖ ≤ r →
      LorentzBaseNorm.point 1 w ∈ PositiveLift.hull (vertexSynthesis n) := by
    intro w hw
    apply polygon_point_mem_hull
    apply RegularPolygon.closedBall_subset_polygon n hn
    simpa only [Metric.mem_closedBall,dist_zero_right] using hw
  obtain ⟨a₀,_ha₀,he₀⟩ := hpoint 0 (by simp; exact hr.le)
  obtain ⟨a₁,_ha₁,he₁⟩ := hpoint (r:ℂ) (by simp [abs_of_pos hr])
  obtain ⟨a₂,_ha₂,he₂⟩ := hpoint ((r:ℂ)*Complex.I) (by simp [abs_of_pos hr])
  intro z
  refine ⟨(z 0-z 1/r-z 2/r) • a₀+(z 1/r) • a₁+(z 2/r) • a₂, ?_⟩
  rw [map_add,map_add,map_smul,map_smul,map_smul,he₀,he₁,he₂]
  ext i
  fin_cases i <;> simp [LorentzBaseNorm.point]
  all_goals field_simp [ne_of_gt hr]
  all_goals ring

/-- The actual regular-polygon cone is invariant and contains the declared
initial state. This is the geometric component of P47. -/
theorem regular_polygon_invariant (n : ℕ) (hn : 3 ≤ n) (α : ℝ)
    (hα : 0 ≤ α) (hsmall : α ≤ Real.cos (Real.pi/(n:ℝ))) :
    initial ∈ PositiveLift.hull (vertexSynthesis n) ∧
      ∀ s z, z ∈ PositiveLift.hull (vertexSynthesis n) →
        operator α s z ∈ PositiveLift.hull (vertexSynthesis n) := by
  obtain ⟨M,a₀,hM,ha,hVa,he,_hm,_hw⟩ := regular_polygon_positive_lift n hn α hα hsmall
  refine ⟨⟨a₀,ha.1,hVa⟩,?_⟩
  intro s
  exact (PositiveLift.positive_lift_iff (vertexSynthesis n) (operator α s)).mpr
    ⟨M s,hM s,he s⟩

/-- P47's regular-polygon condition and its common-policy error bound refer
to exactly the same attenuation of the rational source model. -/
theorem regular_polygon_policy_error (n : ℕ) (hn : 3 ≤ n) (α : ℝ)
    (hα : 0 ≤ α) (hsmall : α ≤ Real.cos (Real.pi/(n:ℝ)))
    (π : List (Bool × Bool) → Bool → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) (T : ℕ) :
    Function.Surjective (vertexSynthesis n) ∧
    (initial ∈ PositiveLift.hull (vertexSynthesis n) ∧
      ∀ s z, z ∈ PositiveLift.hull (vertexSynthesis n) →
        operator α s z ∈ PositiveLift.hull (vertexSynthesis n)) ∧
    FiniteTV.distance
      (ObservationTree.observationLaw LorentzBaseNorm.coneInstance π
        (fun _ s => continuousOperator 1 s) T initial)
      (ObservationTree.observationLaw LorentzBaseNorm.coneInstance π
        (fun _ s => continuousOperator α s) T initial) ≤ min 1 ((T:ℝ)*(1-α)/2) :=
  ⟨regular_vertex_surjective n hn,regular_polygon_invariant n hn α hα hsmall,
    model_shared_policy_tv_bound π hπ α hα (hsmall.trans (Real.cos_le_one _)) T⟩

/-- The alpha=2/3 lifted matrices are literal casts of rational matrices. -/
theorem rational_lift_matrix (s : Bool × Bool) :
    ∃ M : Matrix (Fin 4) (Fin 4) ℚ, M.map (algebraMap ℚ ℝ)=liftMatrix (2/3) s := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o
  · refine ⟨!![5/12,1/60,1/60,11/20; 11/20,5/12,1/60,1/60;
      1/60,11/20,5/12,1/60; 1/60,1/60,11/20,5/12],?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [liftMatrix,rotationLift,slack,Matrix.cons_val_two,Matrix.cons_val_three]
  · refine ⟨0,?_⟩
    ext i j
    simp [liftMatrix]
  · refine ⟨!![1,1/2,0,1/2; 0,0,0,0; 0,0,0,0; 0,0,0,0],?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [liftMatrix,probeLift,Matrix.cons_val_two,Matrix.cons_val_three]
  · refine ⟨!![0,1/2,1,1/2; 0,0,0,0; 0,0,0,0; 0,0,0,0],?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [liftMatrix,probeLift,Matrix.cons_val_two,Matrix.cons_val_three]

/-- Every datum of the four-generator certificate is rational, including
synthesis columns and the normalized initial lifted state. -/
theorem rational_diamond_certificate_data :
    (∃ V : Matrix (Fin 3) (Fin 4) ℚ, V.map (algebraMap ℚ ℝ)=synthesisMatrix) ∧
    (∀ s, ∃ M : Matrix (Fin 4) (Fin 4) ℚ, M.map (algebraMap ℚ ℝ)=liftMatrix (2/3) s) ∧
    (∃ a : Fin 4 → ℚ, ∀ j, (algebraMap ℚ ℝ) (a j)=FiniteBayes.pointMass (0:Fin 4) j) := by
  refine ⟨?_,rational_lift_matrix,?_⟩
  · refine ⟨!![1,1,1,1; 1,0,-1,0; 0,1,0,-1],?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [synthesisMatrix]
  · refine ⟨fun j => if j=0 then 1 else 0,?_⟩
    intro j
    by_cases hj : j=0 <;> simp [FiniteBayes.pointMass,hj]

end
end Komorebi.LSM.RotationApproximation
