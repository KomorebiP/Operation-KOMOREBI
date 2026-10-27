import KomorebiLSM.ObservableCore

/-! P28 packaged as a population-table model, with full-law reconstruction,
minimal dimension and normalized history updates. -/
set_option autoImplicit false
namespace Komorebi.LSM.Behavior
open scoped BigOperators
open FiniteInstruments
variable {S I : Type*} [Fintype I] [DecidableEq I]

noncomputable def tableModel (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = []) :
    Realization f (I → ℝ) where
  initial := tableState f tests []
  operator s := (reconstructed f tests histories s).mulVecLin
  readout := LinearMap.proj i0
  correct := reconstructed_probability f tests histories hH hr i0 hi

/-- State-space dimension is minimal among all finite linear realizations. -/
theorem tableModel_minimal (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I)
    {E : Type*} [AddCommGroup E] [Module ℝ E] [FiniteDimensional ℝ E]
    (r : Realization f E) : Fintype.card I ≤ Module.finrank ℝ E := by
  rw [← core_rank_exact f tests histories hH hr]
  exact r.behavior_dimension_le

/-- In core coordinates the initial state really is the vector f(t_i). -/
theorem tableModel_initial (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = []) :
    (tableModel f tests histories hH hr i0 hi).initial = fun i => f (tests i) := by
  funext i
  simp [tableModel,tableState]

/-- All history columns are reachable in the inferred coordinate space. -/
theorem tableModel_reachable (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = []) :
    (tableModel f tests histories hH hr i0 hi).IsReachable := by
  let r := tableModel f tests histories hH hr i0 hi
  apply top_unique
  intro z _
  obtain ⟨v,hv⟩ := evaluate_surjective f tests histories hH z
  obtain ⟨c,rfl⟩ := synthesize_surjective f tests histories hH hr v
  rw [← hv,synthesize_apply,map_sum]
  apply Submodule.sum_mem
  intro j _
  rw [map_smul]
  apply Submodule.smul_mem
  have hstate : evaluate f tests (history f (histories j)) = r.state (histories j) :=
    (reconstructed_state f tests histories hH hr (histories j)).symm
  rw [hstate]
  exact Submodule.subset_span ⟨histories j,rfl⟩

/-- Core evaluation is the same change of coordinates for every future test. -/
theorem core_test_readout (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = [])
    (w : List S) (v : space f) :
    (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) w
      (evaluate f tests v)) i0 = (v : List S → ℝ) w := by
  have hcomm : ∀ s,
      ((reconstructed f tests histories s).mulVecLin).comp (evaluate f tests) =
        (evaluate f tests).comp (branch f s) := by
    intro s
    ext v i
    exact congrFun (reconstructed_intertwines f tests histories hH hr s v) i
  have hw := word_intertwining (branch f)
    (fun s => (reconstructed f tests histories s).mulVecLin) (evaluate f tests) hcomm w
  have he := congrArg (fun L : space f →ₗ[ℝ] (I → ℝ) => L v i0) hw
  simpa only [LinearMap.comp_apply,evaluate_apply,hi,← mass_apply,test_evaluation] using he

theorem tableModel_observable (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = []) :
    (tableModel f tests histories hH hr i0 hi).IsObservable := by
  intro x y h
  obtain ⟨v,rfl⟩ := evaluate_surjective f tests histories hH x
  obtain ⟨w,rfl⟩ := evaluate_surjective f tests histories hH y
  apply congrArg (evaluate f tests)
  apply Subtype.ext
  funext t
  have ht := congrFun h t
  change (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) t
    (evaluate f tests v)) i0 =
    (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) t
    (evaluate f tests w)) i0 at ht
  simpa only [core_test_readout f tests histories hH hr i0 hi] using ht

/-- Branch probability is the chronological joint/history ratio. -/
theorem reconstructed_likelihood (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = [])
    (h : List S) (s : S) :
    ((reconstructed f tests histories s).mulVecLin ((f h)⁻¹ • tableState f tests h)) i0 =
      f (h ++ [s]) / f h := by
  have hb : (reconstructed f tests histories s).mulVecLin (tableState f tests h) =
      tableState f tests (h ++ [s]) := by
    simpa only [Matrix.mulVecLin_apply,tableState_eq_evaluate,branch_history] using
      reconstructed_intertwines f tests histories hH hr s (history f h)
  rw [map_smul,hb]
  simp only [Pi.smul_apply,smul_eq_mul,tableState_mass f tests i0 hi,div_eq_mul_inv,mul_comm]

/-- Positive history and joint evidence give a positive conditioning denominator. -/
theorem reconstructed_likelihood_pos (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = [])
    (h : List S) (s : S) (hh : 0 < f h) (hs : 0 < f (h ++ [s])) :
    0 < ((reconstructed f tests histories s).mulVecLin
      ((f h)⁻¹ • tableState f tests h)) i0 := by
  rw [reconstructed_likelihood f tests histories hH hr i0 hi]
  exact div_pos hs hh

/-- P28: the matrices are explicitly G_s H^{-1}, with minimality, mass,
reachability, observability and correctness for every future word. -/
theorem observable_table_reconstruction (f : List S → ℝ) [FiniteDimensional ℝ (space f)]
    (tests histories : I → List S) (hH : IsUnit (core f tests histories).det)
    (hr : Module.finrank ℝ (space f) ≤ Fintype.card I) (i0 : I) (hi : tests i0 = []) :
    Module.finrank ℝ (space f) = Fintype.card I ∧
    (tableModel f tests histories hH hr i0 hi).IsReachable ∧
    (tableModel f tests histories hH hr i0 hi).IsObservable ∧
    (∀ s, (tableModel f tests histories hH hr i0 hi).operator s =
      (shiftedCore f tests histories s * (core f tests histories)⁻¹).mulVecLin) ∧
    (∀ w, (tableModel f tests histories hH hr i0 hi).state w = tableState f tests w) := by
  exact ⟨core_rank_exact f tests histories hH hr,
    tableModel_reachable f tests histories hH hr i0 hi,
    tableModel_observable f tests histories hH hr i0 hi,
    fun _ => rfl,reconstructed_state f tests histories hH hr⟩

end Komorebi.LSM.Behavior
