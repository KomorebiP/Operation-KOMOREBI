import KomorebiLSM.TestTopology
import KomorebiLSM.BehaviorProbability

/-! P29: the probability cone is the actual all-test cone of the behavior span.
Finite-dimensional compactness is derived in its inherited function-space topology. -/
set_option autoImplicit false
namespace Komorebi.LSM.Behavior
open scoped BigOperators
open FiniteInstruments
variable {A O : Type*} [Fintype O]
variable {f : List (A × O) → ℝ}

noncomputable def probabilityCone (f : List (A × O) → ℝ) : Set (space f) :=
  {v | ∀ w, 0 ≤ (v : List (A × O) → ℝ) w}

noncomputable def probabilityBase (f : List (A × O) → ℝ) : Set (space f) :=
  {v | v ∈ probabilityCone f ∧ mass f v = 1}

theorem probabilityCone_eq_tests :
    probabilityCone f = TestDomains.allTests (branch f) (mass f) := by
  ext v
  simp only [probabilityCone,TestDomains.allTests,Set.mem_ofPred_eq,
    TestDomains.observe_apply,test_evaluation]

theorem probabilityBase_eq_tests :
    probabilityBase f = TestDomains.base (branch f) (mass f) := by
  unfold probabilityBase TestDomains.base
  rw [probabilityCone_eq_tests]

theorem probability_observe_injective :
    Function.Injective (TestDomains.observe (branch f) (mass f)) := by
  intro x y h
  apply Subtype.ext
  funext w
  have he := congrFun h w
  simpa only [TestDomains.observe_apply,test_evaluation] using he

theorem probabilityCone_convex : Convex ℝ (probabilityCone f) := by
  rw [probabilityCone_eq_tests]
  exact TestDomains.allTests_convex _ _

theorem probabilityCone_pointed {v : space f}
    (hv : v ∈ probabilityCone f) (hn : -v ∈ probabilityCone f) : v = 0 := by
  rw [probabilityCone_eq_tests] at hv hn
  exact TestDomains.allTests_pointed _ _ probability_observe_injective hv hn

theorem probabilityCone_closed [FiniteDimensional ℝ (space f)] :
    IsClosed (probabilityCone f) := by
  rw [probabilityCone_eq_tests]
  exact TestDomains.allTests_closed _ _

theorem probabilityCone_invariant (s : A × O) {v : space f}
    (hv : v ∈ probabilityCone f) : branch f s v ∈ probabilityCone f := by
  intro w; exact hv (s::w)

theorem probabilityCone_smul {c : ℝ} (hc : 0 ≤ c) {v : space f}
    (hv : v ∈ probabilityCone f) : c • v ∈ probabilityCone f := by
  rw [probabilityCone_eq_tests] at hv ⊢
  exact TestDomains.allTests_smul _ _ hc hv

theorem probabilityCone_add {v w : space f}
    (hv : v ∈ probabilityCone f) (hw : w ∈ probabilityCone f) :
    v+w ∈ probabilityCone f := by
  rw [probabilityCone_eq_tests] at hv hw ⊢
  exact TestDomains.allTests_add _ _ hv hw

theorem history_mem_probabilityCone (hf : CausalLaw f) (h : List (A × O)) :
    history f h ∈ probabilityCone f := by
  intro w; exact hf.nonneg (h ++ w)

theorem probabilityCone_spans (hf : CausalLaw f) :
    Submodule.span ℝ (probabilityCone f) = ⊤ := by
  apply top_unique
  rw [← history_span (f := f)]
  apply Submodule.span_mono
  rintro _ ⟨h,rfl⟩
  exact history_mem_probabilityCone hf h

theorem probabilityCone_strict_mass (hf : CausalLaw f) {v : space f}
    (hv : v ∈ probabilityCone f) (hne : v ≠ 0) : 0 < mass f v := by
  rw [probabilityCone_eq_tests] at hv
  exact TestDomains.allTests_strict_mass _ _ (fun a x => hf.behavior_mass x a)
    probability_observe_injective hv hne

theorem probabilityBase_test_bounds (hf : CausalLaw f) {v : space f}
    (hv : v ∈ probabilityBase f) (w : List (A × O)) :
    0 ≤ (v : List (A × O) → ℝ) w ∧ (v : List (A × O) → ℝ) w ≤ 1 := by
  rw [probabilityBase_eq_tests] at hv
  simpa only [TestDomains.observe_apply,test_evaluation] using
    TestDomains.base_test_bounds _ _ (fun a x => hf.behavior_mass x a) hv w

theorem probabilityBase_compact (hf : CausalLaw f) [FiniteDimensional ℝ (space f)] :
    IsCompact (probabilityBase f) := by
  rw [probabilityBase_eq_tests]
  exact TestDomains.base_compact _ _ (fun a x => hf.behavior_mass x a)
    probability_observe_injective

theorem probabilityBase_convex : Convex ℝ (probabilityBase f) := by
  rw [probabilityBase_eq_tests]
  exact TestDomains.base_convex _ _

theorem initial_mem_probabilityBase (hf : CausalLaw f) :
    history f [] ∈ probabilityBase f :=
  ⟨history_mem_probabilityCone hf [], by simpa using hf.initial⟩

theorem probabilityBase_posterior {v : space f} (hv : v ∈ probabilityBase f)
    (s : A × O) (hp : 0 < mass f (branch f s v)) :
    normalize (mass f) (branch f s v) ∈ probabilityBase f := by
  rw [probabilityBase_eq_tests] at hv ⊢
  exact TestDomains.base_posterior _ _ hv.1 s hp

/-- In test coordinates every component lies in [0,1] and the empty test is one. -/
theorem probabilityBase_core_bounds {I : Type*} (hf : CausalLaw f)
    (tests : I → List (A × O)) (i₀ : I) (hi : tests i₀ = [])
    {v : space f} (hv : v ∈ probabilityBase f) :
    (evaluate f tests v) i₀ = 1 ∧ ∀ i, (evaluate f tests v) i ∈ Set.Icc (0 : ℝ) 1 := by
  refine ⟨?_,fun i => probabilityBase_test_bounds hf hv (tests i)⟩
  simpa only [evaluate_apply,hi,mass_apply] using hv.2

/-- Collected P29 conclusions for the actual canonical behavior space. -/
theorem canonical_probability_cone (hf : CausalLaw f) [FiniteDimensional ℝ (space f)] :
    IsClosed (probabilityCone f) ∧ Convex ℝ (probabilityCone f) ∧
    (∀ v, v ∈ probabilityCone f → -v ∈ probabilityCone f → v = 0) ∧
    Submodule.span ℝ (probabilityCone f) = ⊤ ∧
    (∀ s v, v ∈ probabilityCone f → branch f s v ∈ probabilityCone f) ∧
    (∀ v, v ∈ probabilityCone f → v ≠ 0 → 0 < mass f v) ∧
    (∀ a v, ∑ o, mass f (branch f (a,o) v) = mass f v) ∧
    IsCompact (probabilityBase f) ∧ Convex ℝ (probabilityBase f) ∧
    (probabilityBase f).Nonempty :=
  ⟨probabilityCone_closed,probabilityCone_convex,
   fun _ => probabilityCone_pointed,probabilityCone_spans hf,
   fun s _ => probabilityCone_invariant s,fun _ => probabilityCone_strict_mass hf,
   fun a v => hf.behavior_mass v a,probabilityBase_compact hf,probabilityBase_convex,
   ⟨history f [],initial_mem_probabilityBase hf⟩⟩

end Komorebi.LSM.Behavior
