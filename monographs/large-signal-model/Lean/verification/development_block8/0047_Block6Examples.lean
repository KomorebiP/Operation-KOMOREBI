import KomorebiLSM.CanonicalCone
import KomorebiLSM.FiniteTestRows
import KomorebiLSM.FacetRobustness
import KomorebiLSM.CertifiedCorrection
import KomorebiLSM.Block5Examples

/-! Exact applications and rejection boundaries for canonical and finite domains.
Finite sampled checks are kept separate from the all-word invariant arguments. -/
set_option autoImplicit false
namespace Komorebi.LSM.Block6Examples
open scoped BigOperators
open FiniteInstruments FiniteBayes Behavior TestDomains PositiveLift RobustDomains

/-- P29 applies to the actual rank-two future-behavior space of the preceding example. -/
theorem canonical_example_compact : IsCompact (probabilityBase Block5Examples.process) :=
  probabilityBase_compact Block5Examples.process_causal

theorem canonical_example_spans :
    Submodule.span ℝ (probabilityCone Block5Examples.process) = ⊤ :=
  probabilityCone_spans Block5Examples.process_causal

theorem canonical_example_initial : history Block5Examples.process [] ∈
    probabilityBase Block5Examples.process := initial_mem_probabilityBase Block5Examples.process_causal

theorem canonical_example_bounds (v : space Block5Examples.process)
    (hv : v ∈ probabilityBase Block5Examples.process) :
    evaluate Block5Examples.process Block5Examples.selected v 0 = 1 ∧
    ∀ i : Fin 2, evaluate Block5Examples.process Block5Examples.selected v i ∈ Set.Icc (0 : ℝ) 1 :=
  probabilityBase_core_bounds Block5Examples.process_causal Block5Examples.selected 0
    Block5Examples.first_test_empty hv

/-- A mass-normalized family can pass every one-step check and fail at length two. -/
noncomputable def delayedMatrix (o : Bool) : Matrix (Fin 2) (Fin 2) ℝ :=
  if o then !![1/2,-1;0,0] else !![1/2,1;0,2]

noncomputable def delayedBranch (s : Unit × Bool) : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) :=
  (delayedMatrix s.2).mulVecLin

noncomputable def delayedState : Fin 2 → ℝ := ![1,1/4]

def firstMass : (Fin 2 → ℝ) →ₗ[ℝ] ℝ := LinearMap.proj 0

theorem delayed_mass_conserved (a : Unit) (x : Fin 2 → ℝ) :
    ∑ o, firstMass (delayedBranch (a,o) x) = firstMass x := by
  simp [firstMass,delayedBranch,delayedMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
  ring

theorem delayed_first_probabilities :
    firstMass (delayedBranch ((),false) delayedState) = 3/4 ∧
    firstMass (delayedBranch ((),true) delayedState) = 1/4 := by
  norm_num [firstMass,delayedBranch,delayedMatrix,delayedState,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem delayed_passes_one : delayedState ∈ testLevel delayedBranch firstMass 1 := by
  intro w hw
  cases w with
  | nil => norm_num [observe_apply,wordAction,firstMass,delayedState]
  | cons s w =>
    have hw0 : w = [] := List.length_eq_zero_iff.mp (by simpa using hw)
    subst w
    rcases s with ⟨a,o⟩
    cases a
    cases o <;> norm_num [observe_apply,wordAction,firstMass,delayedBranch,delayedMatrix,
      delayedState,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem delayed_negative_two :
    firstMass (wordAction delayedBranch [((),false),((),true)] delayedState) = -1/8 := by
  norm_num [wordAction,firstMass,delayedBranch,delayedMatrix,delayedState,Matrix.mulVec,dotProduct,
    Fin.sum_univ_succ]

theorem delayed_not_all_tests : delayedState ∉ allTests delayedBranch firstMass := by
  intro h
  have he := h [((),false),((),true)]
  change 0 ≤ firstMass (wordAction delayedBranch [((),false),((),true)] delayedState) at he
  rw [delayed_negative_two] at he
  norm_num at he

theorem delayed_level_one_not_stable :
    testLevel delayedBranch firstMass 2 ≠ testLevel delayedBranch firstMass 1 := by
  intro he
  have hh := testLevel_stopping delayedBranch firstMass 1 he
  exact delayed_not_all_tests (hh ▸ delayed_passes_one)

/-- Missing observability leaves nonzero mass-zero states in the all-test cone. -/
def hiddenIdentity (_ : Unit × Unit) : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) := LinearMap.id

theorem identity_words (w : List (Unit × Unit)) (x : Fin 2 → ℝ) :
    wordAction hiddenIdentity w x = x := by
  induction w generalizing x with
  | nil => rfl
  | cons s w ih => exact ih x

theorem unobserved_ray_in_cone :
    ![(0 : ℝ),1] ∈ allTests hiddenIdentity firstMass ∧
    -(![(0 : ℝ),1]) ∈ allTests hiddenIdentity firstMass := by
  constructor <;> intro w <;> simp [observe_apply,identity_words,firstMass]

theorem unobserved_ray_nonzero : ![(0 : ℝ),1] ≠ 0 := by
  intro h
  have hh := congrFun h 1
  norm_num at hh

theorem unobserved_cone_mass_zero : firstMass ![(0 : ℝ),1] = 0 := rfl

/-- A redundant synthesis has a closed, generating and strict-mass cone. -/
theorem redundant_summary_domain :
    IsClosed (hull Block4Examples.summary) ∧
    Submodule.span ℝ (hull Block4Examples.summary) = ⊤ ∧
    PositivePackets.StrictMass (hull Block4Examples.summary) Block4Examples.summaryMass :=
  ⟨hull_closed _ _ Block4Examples.summary_preserves_mass,
   hull_spans _ Block4Examples.summary_surjective,
   hull_strict_mass _ _ Block4Examples.summary_preserves_mass⟩

theorem redundant_summary_base_compact :
    IsCompact (normalizedHull Block4Examples.summary Block4Examples.summaryMass) :=
  normalizedHull_compact _ _ Block4Examples.summary_preserves_mass

theorem redundant_summary_lift (s : Unit × Bool) :
    ∀ x ∈ hull Block4Examples.summary, Block4Examples.reducedBranch s x ∈ hull Block4Examples.summary :=
  (positive_lift_iff _ _).mpr ⟨Block4Examples.hiddenMatrix s.2,
    Block4Examples.tinyInstrument.nonneg s.1 s.2,Block4Examples.reduced_intertwining s⟩

theorem redundant_summary_generators_repeat :
    generator Block4Examples.summary (0 : Fin 3) = generator Block4Examples.summary 1 :=
  Block4Examples.same_summary

noncomputable def swapLift : Matrix (Fin 2) (Fin 2) ℝ := !![0,1;1,0]

theorem swap_lift_nonnegative : ∀ i j, 0 ≤ swapLift i j := by
  intro i j
  fin_cases i <;> fin_cases j <;> norm_num [swapLift]

theorem swap_preserves_total :
    (FiniteInstruments.mass : (Fin 2 → ℝ) →ₗ[ℝ] ℝ).comp swapLift.mulVecLin = FiniteInstruments.mass := by
  apply LinearMap.ext
  intro x
  simp [FiniteInstruments.mass_apply,swapLift,dotProduct,Fin.sum_univ_succ,add_comm]

theorem distinct_positive_lifts :
    (1 : Matrix (Fin 2) (Fin 2) ℝ) ≠ swapLift ∧
    (FiniteInstruments.mass : (Fin 2 → ℝ) →ₗ[ℝ] ℝ).comp (1 : Matrix (Fin 2) (Fin 2) ℝ).mulVecLin = FiniteInstruments.mass ∧
    (FiniteInstruments.mass : (Fin 2 → ℝ) →ₗ[ℝ] ℝ).comp swapLift.mulVecLin = FiniteInstruments.mass := by
  refine ⟨?_,?_,swap_preserves_total⟩
  · intro h
    have he := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℝ => M 0 0) h
    norm_num [swapLift] at he
  · apply LinearMap.ext
    intro x
    simp

/-- A complete family of scalar Bernoulli branches. -/
noncomputable def coinFamily (θ : ℝ) (s : Unit × Bool) : ℝ →ₗ[ℝ] ℝ :=
  (if s.2 then θ else 1-θ) • LinearMap.id

theorem coin_mass (θ : ℝ) (a : Unit) (x : ℝ) :
    ∑ o, (LinearMap.id : ℝ →ₗ[ℝ] ℝ) (coinFamily θ (a,o) x) = x := by
  simp [coinFamily]
  ring

theorem coin_valid (θ : ℝ) (h₀ : 0 ≤ θ) (h₁ : θ ≤ 1) :
    ValidFamily (Set.Ici (0 : ℝ)) (LinearMap.id : ℝ →ₗ[ℝ] ℝ) (coinFamily θ) := by
  constructor
  · rintro ⟨a,o⟩ x hx
    change 0 ≤ x at hx
    cases o
    · exact mul_nonneg (sub_nonneg.mpr h₁) hx
    · exact mul_nonneg h₀ hx
  · exact coin_mass θ

noncomputable def coinVertices (b : Bool) : Unit × Bool → ℝ →ₗ[ℝ] ℝ :=
  coinFamily (if b then 3/4 else 1/4)

theorem coin_vertices_valid : ∀ b, ValidFamily (Set.Ici (0 : ℝ)) LinearMap.id (coinVertices b) := by
  intro b
  cases b <;> apply coin_valid <;> norm_num

theorem every_convex_coin_family_valid :
    ∀ B ∈ convexHull ℝ (Set.range coinVertices), ValidFamily (Set.Ici (0 : ℝ)) LinearMap.id B :=
  robust_convex_hull _ (convex_Ici _) _ coinVertices coin_vertices_valid

noncomputable def switchingCoins (h : List (Unit × Bool)) : Unit × Bool → ℝ →ₗ[ℝ] ℝ :=
  coinVertices (h.length % 2 == 0)

theorem switched_tree_normalized (n : ℕ) :
    adaptiveTreeMass switchingCoins LinearMap.id (fun _ => ()) n [] 1 = 1 :=
  adaptiveTreeMass_eq (Set.Ici (0 : ℝ)) LinearMap.id switchingCoins
    (fun _ => coin_vertices_valid _) (fun _ => ()) n [] 1

theorem switched_every_word_valid (w : List (Unit × Bool)) :
    0 ≤ adaptiveWord switchingCoins [] w 1 ∧ adaptiveWord switchingCoins [] w 1 ≤ 1 :=
  ⟨adaptiveWord_nonnegative (Set.Ici (0 : ℝ)) LinearMap.id (fun _ hx => hx)
      switchingCoins (fun _ => coin_vertices_valid _) [] w (by norm_num),
   adaptiveWord_mass_le (Set.Ici (0 : ℝ)) LinearMap.id (fun _ hx => hx)
      switchingCoins (fun _ => coin_vertices_valid _) [] w (by norm_num)⟩

/-- Choosing the larger probability independently from each family breaks normalization. -/
noncomputable def crossedBranches (s : Unit × Bool) : ℝ →ₗ[ℝ] ℝ :=
  if s.2 then coinVertices true s else coinVertices false s

theorem independent_branch_mixing_breaks_mass :
    (∑ o, crossedBranches ((),o) 1) = (3/2 : ℝ) := by
  norm_num [crossedBranches,coinVertices,coinFamily]

theorem bad_coin_has_negative_branch : coinFamily (3/2) ((),false) 1 = (-1/2 : ℝ) := by
  norm_num [coinFamily]

theorem feasible_member_is_not_whole_set_valid :
    ValidFamily (Set.Ici (0 : ℝ)) LinearMap.id (coinFamily (1/2)) ∧
    ¬ ValidFamily (Set.Ici (0 : ℝ)) LinearMap.id (coinFamily (3/2)) := by
  refine ⟨coin_valid _ (by norm_num) (by norm_num), ?_⟩
  intro h
  have hp := h.1 ((),false) 1 (by norm_num)
  change 0 ≤ coinFamily (3/2) ((),false) 1 at hp
  rw [bad_coin_has_negative_branch] at hp
  norm_num at hp

theorem double_radius_can_be_tight :
    ‖(-1 : ℝ)-0‖ = 1 ∧ ‖(1 : ℝ)-0‖ = 1 ∧ ‖(1 : ℝ)-(-1)‖ = 2 := by norm_num

noncomputable def tableBranch (s : Unit × Bool) : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) :=
  (reconstructed Block5Examples.process Block5Examples.selected Block5Examples.selected s).mulVecLin

theorem table_false_coordinates (x : Fin 2 → ℝ) :
    tableBranch ((),false) x = ![x 0-x 1,(x 0-x 1)/2] := by
  change (reconstructed _ _ _ _).mulVec x = _
  rw [Block5Examples.learned_false]
  ext i
  fin_cases i <;> norm_num [Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring

theorem table_true_coordinates (x : Fin 2 → ℝ) :
    tableBranch ((),true) x = ![x 1,3/4*x 1] := by
  change (reconstructed _ _ _ _).mulVec x = _
  rw [Block5Examples.learned_true]
  ext i
  fin_cases i <;> norm_num [Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

noncomputable def outerDomain : Set (Fin 2 → ℝ) := {x | 0 ≤ x 1 ∧ x 1 ≤ x 0}

theorem table_preserves_outer (s : Unit × Bool) (x : Fin 2 → ℝ) (hx : x ∈ outerDomain) :
    tableBranch s x ∈ outerDomain := by
  rcases s with ⟨a,o⟩
  cases a
  change 0 ≤ x 1 ∧ x 1 ≤ x 0 at hx
  cases o
  · rw [table_false_coordinates]
    change 0 ≤ (x 0-x 1)/2 ∧ (x 0-x 1)/2 ≤ x 0-x 1
    constructor <;> linarith [hx.2]
  · rw [table_true_coordinates]
    change 0 ≤ 3/4*x 1 ∧ 3/4*x 1 ≤ x 1
    constructor <;> linarith [hx.1]

theorem table_mass_conserved (a : Unit) (x : Fin 2 → ℝ) :
    ∑ o, firstMass (tableBranch (a,o) x) = firstMass x := by
  cases a
  simp only [Fintype.sum_bool,table_false_coordinates,table_true_coordinates,firstMass,LinearMap.proj_apply]
  simp

theorem table_allTests_outer : allTests tableBranch firstMass = outerDomain := by
  apply Set.Subset.antisymm
  · intro x hx
    have h₁ := hx [((),true)]
    have h₀ := hx [((),false)]
    simp only [observe_apply,wordAction,LinearMap.comp_apply,LinearMap.id_apply,
      table_false_coordinates,table_true_coordinates,firstMass,LinearMap.proj_apply] at h₀ h₁
    exact ⟨h₁,by change 0 ≤ x 0-x 1 at h₀; linarith⟩
  · apply allTests_greatest tableBranch firstMass outerDomain
    · intro x hx; exact hx.1.trans hx.2
    · exact table_preserves_outer

theorem table_level_one_outer : testLevel tableBranch firstMass 1 = outerDomain := by
  apply Set.Subset.antisymm
  · intro x hx
    have h₁ := hx [((),true)] (by simp)
    have h₀ := hx [((),false)] (by simp)
    simp only [observe_apply,wordAction,LinearMap.comp_apply,LinearMap.id_apply,
      table_false_coordinates,table_true_coordinates,firstMass,LinearMap.proj_apply] at h₀ h₁
    exact ⟨h₁,by change 0 ≤ x 0-x 1 at h₀; linarith⟩
  · intro x hx w _
    exact (table_allTests_outer.symm ▸ hx) w

theorem table_finite_stopping : testLevel tableBranch firstMass 2 = testLevel tableBranch firstMass 1 := by
  apply Set.Subset.antisymm (testLevel_antitone tableBranch firstMass (by decide))
  intro x hx w _
  have ho : x ∈ outerDomain := table_level_one_outer ▸ hx
  exact (table_allTests_outer.symm ▸ ho) w

noncomputable def intervalSynthesis : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) :=
  (!![(1 : ℝ),1;1/2,3/4]).mulVecLin

noncomputable def intervalLift (s : Unit × Bool) : Matrix (Fin 2) (Fin 2) ℝ :=
  if s.2 then !![0,0;1/2,3/4] else !![1/2,1/4;0,0]

theorem interval_normalized : firstMass.comp intervalSynthesis = FiniteInstruments.mass := by
  apply LinearMap.ext
  intro a
  simp [firstMass,intervalSynthesis,FiniteInstruments.mass_apply,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem interval_surjective : Function.Surjective intervalSynthesis := by
  intro x
  refine ⟨![3*x 0-4*x 1,4*x 1-2*x 0],?_⟩
  ext i
  fin_cases i <;> norm_num [intervalSynthesis,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring

theorem interval_lift_nonnegative : ∀ s i j, 0 ≤ intervalLift s i j := by
  rintro ⟨a,o⟩ i j
  cases o <;> fin_cases i <;> fin_cases j <;> norm_num [intervalLift]

theorem interval_intertwines (s : Unit × Bool) :
    (tableBranch s).comp intervalSynthesis = intervalSynthesis.comp (intervalLift s).mulVecLin := by
  apply LinearMap.ext
  intro x
  rcases s with ⟨a,o⟩
  cases a
  cases o
  · rw [LinearMap.comp_apply,table_false_coordinates,LinearMap.comp_apply]
    ext i
    fin_cases i <;> norm_num [intervalSynthesis,intervalLift,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring
  · rw [LinearMap.comp_apply,table_true_coordinates,LinearMap.comp_apply]
    ext i
    fin_cases i <;> norm_num [intervalSynthesis,intervalLift,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem interval_initial : intervalSynthesis ![(1/2 : ℝ),1/2] = ![(1 : ℝ),5/8] := by
  ext i
  fin_cases i <;> norm_num [intervalSynthesis,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem interval_prior : IsPrior ![(1/2 : ℝ),1/2] := by
  constructor
  · intro i; fin_cases i <;> norm_num
  · norm_num [Fin.sum_univ_succ]

/-- The witness gives every finite word, not an extrapolation of a word table. -/
theorem interval_certificate_all_words (w : List (Unit × Bool)) :
    0 ≤ firstMass (wordAction tableBranch w ![(1 : ℝ),5/8]) ∧
    firstMass (wordAction tableBranch w ![(1 : ℝ),5/8]) ≤ 1 := by
  rw [← interval_initial]
  exact (finite_positive_lift_certificate tableBranch intervalSynthesis firstMass
    interval_normalized table_mass_conserved intervalLift interval_intertwines
    interval_lift_nonnegative _ interval_prior).2.2 w

/-- The sufficient interval certificate need not equal the canonical all-test domain. -/
theorem certified_subcone_can_be_strict :
    ![(1 : ℝ),0] ∈ allTests tableBranch firstMass ∧ ![(1 : ℝ),0] ∉ hull intervalSynthesis := by
  constructor
  · rw [table_allTests_outer]; constructor <;> norm_num
  · rintro ⟨a,ha,he⟩
    have h₀ := congrFun he 0
    have h₁ := congrFun he 1
    norm_num [intervalSynthesis,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] at h₀ h₁
    linarith [ha 0,ha 1]

end Komorebi.LSM.Block6Examples
