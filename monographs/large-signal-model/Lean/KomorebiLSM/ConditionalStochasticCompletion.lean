import KomorebiLSM.CanonicalCone
import KomorebiLSM.PositivePackets
import KomorebiLSM.CoreStability
import KomorebiLSM.FilteringStability
import KomorebiLSM.FiniteTableP32
import KomorebiLSM.ResetCertificate

/-! P37: population-table reconstruction, its actual probability cone,
coordinate transport, full packet synthesis and conditional perturbation bounds.
Causality and global rank coverage are explicit population assumptions. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConditionalStochasticCompletion
open scoped BigOperators
open FiniteInstruments Behavior

section Exact
variable {A O I : Type*} [Fintype O] [Fintype I] [DecidableEq I]
variable (f : List (A × O) → ℝ) [FiniteDimensional ℝ (space f)]
variable (tests histories : I → List (A × O))
variable (hH : IsUnit (core f tests histories).det)
variable (hr : Module.finrank ℝ (space f) ≤ Fintype.card I)

/-- The canonical cone transported by the constructed population-core isomorphism. -/
noncomputable def coreCone : Set (I → ℝ) :=
  (coreEquiv f tests histories hH hr).symm ⁻¹' probabilityCone f

omit [Fintype O] in
theorem coreCone_image : coreCone f tests histories hH hr =
    (coreEquiv f tests histories hH hr) '' probabilityCone f := by
  ext z
  constructor
  · intro hz
    exact ⟨(coreEquiv f tests histories hH hr).symm z, hz,
      (coreEquiv f tests histories hH hr).apply_symm_apply z⟩
  · rintro ⟨v, hv, rfl⟩
    simpa [coreCone] using hv

omit [Fintype O] in
theorem coreCone_closed : IsClosed (coreCone f tests histories hH hr) :=
  probabilityCone_closed.preimage
    (coreEquiv f tests histories hH hr).symm.toContinuousLinearEquiv.continuous

omit [Fintype O] in
theorem coreCone_convex : Convex ℝ (coreCone f tests histories hH hr) :=
  probabilityCone_convex.linear_preimage
    (coreEquiv f tests histories hH hr).symm.toLinearMap

omit [Fintype O] in
theorem coreCone_pointed {z : I → ℝ}
    (hz : z ∈ coreCone f tests histories hH hr)
    (hn : -z ∈ coreCone f tests histories hH hr) : z = 0 := by
  apply (coreEquiv f tests histories hH hr).symm.injective
  rw [map_zero]
  exact probabilityCone_pointed hz (by simpa [coreCone] using hn)

theorem coreCone_spans (hf : CausalLaw f) :
    Submodule.span ℝ (coreCone f tests histories hH hr) = ⊤ := by
  rw [coreCone_image, Submodule.span_image_linearEquiv, probabilityCone_spans hf]
  rw [Submodule.map_top]
  exact LinearMap.range_eq_top.mpr (coreEquiv f tests histories hH hr).surjective

omit [Fintype O] in
/-- The actual inferred symbol operator, not a supplied candidate, preserves the cone. -/
theorem coreCone_invariant (s : A × O) {z : I → ℝ}
    (hz : z ∈ coreCone f tests histories hH hr) :
    (reconstructed f tests histories s).mulVecLin z ∈ coreCone f tests histories hH hr := by
  let e := coreEquiv f tests histories hH hr
  have he : (reconstructed f tests histories s).mulVecLin z =
      e (branch f s (e.symm z)) := by
    have h := reconstructed_intertwines f tests histories hH hr s (e.symm z)
    simpa only [show evaluate f tests = e.toLinearMap from rfl,
      LinearEquiv.coe_coe, LinearEquiv.apply_symm_apply, Matrix.mulVecLin_apply] using h
  rw [he]
  change e.symm (e (branch f s (e.symm z))) ∈ probabilityCone f
  rw [e.symm_apply_apply]
  exact probabilityCone_invariant s hz

omit [Fintype O] in
theorem core_mass (i₀ : I) (hi : tests i₀ = []) (z : I → ℝ) :
    mass f ((coreEquiv f tests histories hH hr).symm z) = z i₀ := by
  let e := coreEquiv f tests histories hH hr
  have he := congrFun (e.apply_symm_apply z) i₀
  change (e.symm z : List (A × O) → ℝ) (tests i₀) = z i₀ at he
  simpa only [hi, Behavior.mass_apply] using he

theorem coreCone_strict_mass (hf : CausalLaw f) (i₀ : I) (hi : tests i₀ = [])
    {z : I → ℝ} (hz : z ∈ coreCone f tests histories hH hr) (hne : z ≠ 0) :
    0 < z i₀ := by
  rw [← core_mass f tests histories hH hr i₀ hi z]
  apply probabilityCone_strict_mass hf hz
  intro he
  apply hne
  exact (coreEquiv f tests histories hH hr).symm.injective (by simpa using he)

theorem initial_coreCone (hf : CausalLaw f) :
    tableState f tests [] ∈ coreCone f tests histories hH hr := by
  change (coreEquiv f tests histories hH hr).symm
    ((coreEquiv f tests histories hH hr) (history f [])) ∈ probabilityCone f
  rw [LinearEquiv.symm_apply_apply]
  exact history_mem_probabilityCone hf []

include hH hr in
theorem core_instrument_mass (hf : CausalLaw f) (i₀ : I) (hi : tests i₀ = [])
    (a : A) (z : I → ℝ) :
    ∑ o, ((reconstructed f tests histories (a,o)).mulVecLin z) i₀ = z i₀ := by
  let e := coreEquiv f tests histories hH hr
  have he (s : A × O) :
      (reconstructed f tests histories s).mulVecLin z =
        e (branch f s (e.symm z)) := by
    simpa only [show evaluate f tests = e.toLinearMap from rfl,
      LinearEquiv.coe_coe, LinearEquiv.apply_symm_apply, Matrix.mulVecLin_apply] using
      reconstructed_intertwines f tests histories hH hr s (e.symm z)
  simp only [he]
  change (∑ o, (branch f (a,o) (e.symm z) : List (A × O) → ℝ) (tests i₀)) = z i₀
  rw [hi]
  exact (hf.behavior_mass (e.symm z) a).trans (core_mass f tests histories hH hr i₀ hi z)

/-- Every positive history is a normalized point of the transported cone,
with all future experiment probabilities given by the chronological ratio. -/
theorem conditional_core_history (hf : CausalLaw f) (i₀ : I) (hi : tests i₀ = [])
    (h : List (A × O)) (hh : 0 < f h) :
    ((f h)⁻¹ • tableState f tests h) ∈ coreCone f tests histories hH hr ∧
    (((f h)⁻¹ • tableState f tests h) i₀ = 1) ∧
    ∀ t, (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) t
      ((f h)⁻¹ • tableState f tests h)) i₀ = f (h ++ t) / f h ∧
      0 ≤ f (h ++ t) / f h ∧ f (h ++ t) / f h ≤ 1 := by
  refine ⟨?_, ?_, ?_⟩
  · change (coreEquiv f tests histories hH hr).symm
      ((f h)⁻¹ • (coreEquiv f tests histories hH hr) (history f h)) ∈ probabilityCone f
    rw [map_smul, LinearEquiv.symm_apply_apply]
    exact probabilityCone_smul (inv_nonneg.mpr hh.le) (history_mem_probabilityCone hf h)
  · simp [Pi.smul_apply, tableState_mass f tests i₀ hi h, ne_of_gt hh]
  · intro t
    refine ⟨?_, hf.conditional_bounds h t hh⟩
    rw [map_smul]
    have he := core_test_readout f tests histories hH hr i₀ hi t (history f h)
    change (f h)⁻¹ * (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) t
      (evaluate f tests (history f h))) i₀ = _
    rw [he]
    simp only [history_apply, div_eq_mul_inv, mul_comm]

/-- P37's exact learned realization is minimal and correct on all finite words;
its normalized state and likelihood are recursively obtained from table matrices. -/
theorem exact_stochastic_completion (hf : CausalLaw f) (i₀ : I) (hi : tests i₀ = []) :
    Module.finrank ℝ (space f) = Fintype.card I ∧
    (tableModel f tests histories hH hr i₀ hi).IsReachable ∧
    (tableModel f tests histories hH hr i₀ hi).IsObservable ∧
    (∀ w, (wordAction (fun s => (reconstructed f tests histories s).mulVecLin) w
      (tableState f tests [])) i₀ = f w) ∧
    (∀ h s, 0 < f h → 0 < f (h ++ [s]) →
      0 < ((reconstructed f tests histories s).mulVecLin
        ((f h)⁻¹ • tableState f tests h)) i₀ ∧
      normalize (LinearMap.proj i₀)
        ((reconstructed f tests histories s).mulVecLin
          ((f h)⁻¹ • tableState f tests h)) =
          (f (h ++ [s]))⁻¹ • tableState f tests (h ++ [s])) ∧
    tableState f tests [] ∈ coreCone f tests histories hH hr ∧
    (∀ s z, z ∈ coreCone f tests histories hH hr →
      (reconstructed f tests histories s).mulVecLin z ∈ coreCone f tests histories hH hr) ∧
    (∀ a z, ∑ o, ((reconstructed f tests histories (a,o)).mulVecLin z) i₀ = z i₀) := by
  refine ⟨core_rank_exact f tests histories hH hr,
    tableModel_reachable f tests histories hH hr i₀ hi,
    tableModel_observable f tests histories hH hr i₀ hi,
    reconstructed_probability f tests histories hH hr i₀ hi, ?_,
    initial_coreCone f tests histories hH hr hf,
    fun s _ => coreCone_invariant f tests histories hH hr s,
    core_instrument_mass f tests histories hH hr hf i₀ hi⟩
  intro h s hh hs
  exact ⟨reconstructed_likelihood_pos f tests histories hH hr i₀ hi h s hh hs,
    reconstructed_conditional_update f tests histories hH hr i₀ hi h s (ne_of_gt hh)⟩

end Exact

section Atlas
variable {S E F : Type*} [AddCommGroup E] [Module ℝ E]
variable [AddCommGroup F] [Module ℝ F]

/-- All symbol maps are conjugated using the same invertible atlas. -/
def atlasOperator (T : E ≃ₗ[ℝ] F) (B : S → E →ₗ[ℝ] E) (s : S) : F →ₗ[ℝ] F :=
  T.toLinearMap.comp ((B s).comp T.symm.toLinearMap)

def atlasMass (T : E ≃ₗ[ℝ] F) (lam : E →ₗ[ℝ] ℝ) : F →ₗ[ℝ] ℝ :=
  lam.comp T.symm.toLinearMap

theorem atlas_word (T : E ≃ₗ[ℝ] F) (B : S → E →ₗ[ℝ] E)
    (w : List S) (z : E) :
    wordAction (atlasOperator T B) w (T z) = T (wordAction B w z) := by
  induction w generalizing z with
  | nil => rfl
  | cons s w ih =>
    simpa only [wordAction_cons, LinearMap.comp_apply, atlasOperator,
      LinearEquiv.coe_coe, LinearEquiv.symm_apply_apply] using ih (B s z)

theorem atlas_likelihood (T : E ≃ₗ[ℝ] F) (B : S → E →ₗ[ℝ] E)
    (lam : E →ₗ[ℝ] ℝ) (w : List S) (z : E) :
    atlasMass T lam (wordAction (atlasOperator T B) w (T z)) =
      lam (wordAction B w z) := by
  rw [atlas_word]
  simp [atlasMass]

theorem atlas_posterior (T : E ≃ₗ[ℝ] F) (lam : E →ₗ[ℝ] ℝ) (z : E) :
    normalize (atlasMass T lam) (T z) = T (normalize lam z) := by
  simp [FiniteInstruments.normalize, atlasMass]

theorem atlas_cone_invariant (T : E ≃ₗ[ℝ] F) (B : S → E →ₗ[ℝ] E)
    (C : Set E) (hc : ∀ s z, z ∈ C → B s z ∈ C) (s : S) {z : F}
    (hz : z ∈ T '' C) : atlasOperator T B s z ∈ T '' C := by
  obtain ⟨x, hx, rfl⟩ := hz
  exact ⟨B s x, hc s x hx, by simp [atlasOperator]⟩

/-- Completeness preserves the synthesized state before any probability readout. -/
theorem full_packet_prediction {J : Type*} [Fintype J]
    (P : J → E →ₗ[ℝ] E) (hP : ∑ j, P j = LinearMap.id)
    (B : S → E →ₗ[ℝ] E) (lam : E →ₗ[ℝ] ℝ) (w : List S) (z : E) :
    lam (wordAction B w (∑ j, P j z)) = lam (wordAction B w z) := by
  have he := congrArg (fun F : E →ₗ[ℝ] E => F z) hP
  have hs : ∑ j, P j z = z := by
    simpa only [LinearMap.sum_apply, LinearMap.id_apply] using he
  rw [hs]

end Atlas
section Perturbation
variable {r : ℕ}

/-- Matrices act on the declared Euclidean core coordinates. -/
noncomputable def matrixOperator (M : Matrix (Fin r) (Fin r) ℝ) :
    EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r) :=
  M.toEuclideanLin.toContinuousLinearMap

theorem matrixOperator_add (M N : Matrix (Fin r) (Fin r) ℝ) :
    matrixOperator (M+N) = matrixOperator M + matrixOperator N := by
  change LinearMap.toContinuousLinearMap (Matrix.toEuclideanLin (M+N)) = _
  rw [map_add, map_add]
  rfl

theorem matrixOperator_mul (M N : Matrix (Fin r) (Fin r) ℝ) :
    matrixOperator (M*N) = (matrixOperator M).comp (matrixOperator N) := by
  ext x i
  change ((M*N).mulVec x) i = (M.mulVec (N.mulVec x)) i
  rw [Matrix.mulVec_mulVec]

variable {A O : Type*} (f : List (A × O) → ℝ)
variable (tests histories : Fin r → List (A × O))

/-- The fit uses the observed shifted block and observed core, without a hidden operator. -/
noncomputable def tableFit (s : A × O) (E F : Matrix (Fin r) (Fin r) ℝ) :
    EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r) :=
  (matrixOperator (shiftedCore f tests histories s + F)).comp
    (Identification.pinvL (matrixOperator (core f tests histories + E)))

theorem tableFit_eq_coreFit (hH : IsUnit (core f tests histories).det)
    (s : A × O) (E F : Matrix (Fin r) (Fin r) ℝ) :
    tableFit f tests histories s E F =
      Identification.coreFit (matrixOperator (core f tests histories))
        (matrixOperator E) (matrixOperator F)
        (matrixOperator (reconstructed f tests histories s)) := by
  unfold tableFit Identification.coreFit
  rw [matrixOperator_add, matrixOperator_add, ← matrixOperator_mul,
    reconstructed_core_equation f tests histories hH s]

theorem tableFit_error (hH : IsUnit (core f tests histories).det)
    (s : A × O) (E F : Matrix (Fin r) (Fin r) ℝ)
    (hE : ‖matrixOperator E‖ < Identification.rowGain (matrixOperator (core f tests histories))) :
    ‖tableFit f tests histories s E F - matrixOperator (reconstructed f tests histories s)‖ ≤
      (‖matrixOperator F‖ + ‖matrixOperator (reconstructed f tests histories s)‖ * ‖matrixOperator E‖) /
        (Identification.rowGain (matrixOperator (core f tests histories)) - ‖matrixOperator E‖) := by
  rw [tableFit_eq_coreFit f tests histories hH s E F]
  exact Identification.core_error_bound _ _ _ _ hE

/-- The actual table fit supplies the operator defects in the normalized
recursion. State bounds and branch likelihood margins remain explicit. -/
theorem tableFit_filtering_path (hH : IsUnit (core f tests histories).det)
    (s : ℕ → A × O) (E F : ℕ → Matrix (Fin r) (Fin r) ℝ)
    (z zhat : ℕ → EuclideanSpace ℝ (Fin r)) (i₀ : Fin r)
    (R : ℝ) (ηhat : ℕ → ℝ)
    (hE : ∀ t, ‖matrixOperator (E t)‖ <
      Identification.rowGain (matrixOperator (core f tests histories)))
    (true_step : ∀ t, z (t+1) = Filtering.normalize (EuclideanSpace.proj i₀)
      (matrixOperator (reconstructed f tests histories (s t)) (z t)))
    (fit_step : ∀ t, zhat (t+1) = Filtering.normalize (EuclideanSpace.proj i₀)
      (tableFit f tests histories (s t) (E t) (F t) (zhat t)))
    (hz : ∀ t, ‖z t‖ ≤ R)
    (hp : ∀ t, (matrixOperator (reconstructed f tests histories (s t)) (z t)) i₀ ≠ 0)
    (hq : ∀ t, ηhat t ≤ (tableFit f tests histories (s t) (E t) (F t) (zhat t)) i₀)
    (hη : ∀ t, 0 < ηhat t) (T : ℕ) :
    ‖zhat T-z T‖ ≤ Stability.errorEnvelope
      (fun t => (1+R*‖(EuclideanSpace.proj i₀ : EuclideanSpace ℝ (Fin r) →L[ℝ] ℝ)‖) *
        ‖tableFit f tests histories (s t) (E t) (F t)‖ / ηhat t)
      (fun t => (1+R*‖(EuclideanSpace.proj i₀ : EuclideanSpace ℝ (Fin r) →L[ℝ] ℝ)‖) *
        ((‖matrixOperator (F t)‖ + ‖matrixOperator (reconstructed f tests histories (s t))‖ *
            ‖matrixOperator (E t)‖) /
          (Identification.rowGain (matrixOperator (core f tests histories)) - ‖matrixOperator (E t)‖)) *
          R / ηhat t) ‖zhat 0-z 0‖ T := by
  exact Filtering.filtering_path (EuclideanSpace.proj i₀)
    (fun t => matrixOperator (reconstructed f tests histories (s t)))
    (fun t => tableFit f tests histories (s t) (E t) (F t)) z zhat R
    (fun t => ‖tableFit f tests histories (s t) (E t) (F t)‖)
    (fun t => (‖matrixOperator (F t)‖ + ‖matrixOperator (reconstructed f tests histories (s t))‖ *
        ‖matrixOperator (E t)‖) /
      (Identification.rowGain (matrixOperator (core f tests histories)) - ‖matrixOperator (E t)‖))
    ηhat true_step fit_step (fun _ => le_rfl)
    (fun t => tableFit_error f tests histories hH (s t) (E t) (F t) (hE t))
    hz hp hq hη T

end Perturbation
section ResetData
open MeasureTheory ProbabilityTheory
variable {A O Ω : Type*} [Fintype A] [Fintype O] [MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ] {r N : ℕ}

/-- One prospectively declared experiment set includes the core, all shifted
blocks and the initial vector. Repeated words may appear under different indices. -/
abbrev DataIndex (A O : Type*) (r : ℕ) :=
  Sum (Fin r × Fin r) (Sum ((A × O) × Fin r × Fin r) (Fin r))

def experimentWord (tests histories : Fin r → List (A × O)) :
    DataIndex A O r → List (A × O)
  | .inl (i,j) => histories j ++ tests i
  | .inr (.inl (s,i,j)) => histories j ++ s :: tests i
  | .inr (.inr i) => tests i

noncomputable def estimatedCore
    (X : DataIndex A O r → Fin N → Ω → ℝ) (ω : Ω) : Matrix (Fin r) (Fin r) ℝ :=
  fun i j => ResetCertificate.sampleMean (X (.inl (i,j))) ω

noncomputable def estimatedShift
    (X : DataIndex A O r → Fin N → Ω → ℝ) (s : A × O) (ω : Ω) :
    Matrix (Fin r) (Fin r) ℝ :=
  fun i j => ResetCertificate.sampleMean (X (.inr (.inl (s,i,j)))) ω

noncomputable def estimatedInitial
    (X : DataIndex A O r → Fin N → Ω → ℝ) (ω : Ω) : EuclideanSpace ℝ (Fin r) :=
  WithLp.toLp 2 (fun i => ResetCertificate.sampleMean (X (.inr (.inr i))) ω)

/-- The sample event controls every matrix entry, hence actual operator norms,
and also the initial Euclidean state. It does not infer population rank. -/
theorem reset_table_event
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O)) (i₀ : Fin r)
    (hN : 0 < N) (X : DataIndex A O r → Fin N → Ω → ℝ) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = f (experimentWord tests histories w)) :
    1-δ ≤ μ.real {ω |
      (∀ w, |ResetCertificate.sampleMean (X w) ω - f (experimentWord tests histories w)| ≤
        ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ) ∧
      ‖matrixOperator (estimatedCore X ω - core f tests histories)‖ ≤
        r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ ∧
      (∀ s, ‖matrixOperator (estimatedShift X s ω - shiftedCore f tests histories s)‖ ≤
        r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ) ∧
      ‖estimatedInitial X ω - WithLp.toLp 2 (fun i => f (tests i))‖ ≤
        Real.sqrt r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ} := by
  let : Nonempty (DataIndex A O r) := ⟨.inr (.inr i₀)⟩
  have he := ResetCertificate.reset_probability_certificate hN X
    (fun w => f (experimentWord tests histories w)) hδ hδ1 hind hm hb hp
  apply he.trans (measureReal_mono ?_)
  intro ω hω
  refine ⟨hω, ?_, ?_, ?_⟩
  · apply ResetCertificate.matrix_opNorm_le _ _ (Real.sqrt_nonneg _)
    intro i j
    exact hω (.inl (i,j))
  · intro s
    apply ResetCertificate.matrix_opNorm_le _ _ (Real.sqrt_nonneg _)
    intro i j
    exact hω (.inr (.inl (s,i,j)))
  · apply ResetCertificate.vector_norm_le _ _ (Real.sqrt_nonneg _)
    intro i
    exact hω (.inr (.inr i))

omit [Fintype A] [Fintype O] [MeasurableSpace Ω] in
/-- Substitution shows the inferred matrices use the sampled blocks themselves. -/
theorem sampled_tableFit
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O))
    (X : DataIndex A O r → Fin N → Ω → ℝ) (s : A × O) (ω : Ω) :
    tableFit f tests histories s (estimatedCore X ω - core f tests histories)
      (estimatedShift X s ω - shiftedCore f tests histories s) =
      (matrixOperator (estimatedShift X s ω)).comp
        (Identification.pinvL (matrixOperator (estimatedCore X ω))) := by
  simp [tableFit]

/-- The same reset event also bounds every reconstructed symbol operator.
The positive core gap is separate from statistical coverage. -/
theorem reset_operator_event
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O)) (i₀ : Fin r)
    (hH : IsUnit (core f tests histories).det)
    (hN : 0 < N) (X : DataIndex A O r → Fin N → Ω → ℝ) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = f (experimentWord tests histories w))
    (hgap : r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ <
      Identification.rowGain (matrixOperator (core f tests histories))) :
    1-δ ≤ μ.real {ω | ∀ s,
      ‖(matrixOperator (estimatedShift X s ω)).comp
          (Identification.pinvL (matrixOperator (estimatedCore X ω))) -
          matrixOperator (reconstructed f tests histories s)‖ ≤
        ((r:ℝ) * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ +
          ‖matrixOperator (reconstructed f tests histories s)‖ *
          ((r:ℝ) * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ)) /
          (Identification.rowGain (matrixOperator (core f tests histories)) -
            (r:ℝ) * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ)} := by
  have he := reset_table_event f tests histories i₀ hN X hδ hδ1 hind hm hb hp
  apply he.trans (measureReal_mono ?_)
  intro ω hω s
  rw [← sampled_tableFit f tests histories X s ω]
  have hE := hω.2.1.trans_lt hgap
  apply (tableFit_error f tests histories hH s _ _ hE).trans
  have hnum := add_le_add (hω.2.2.1 s)
    (mul_le_mul_of_nonneg_left hω.2.1
      (norm_nonneg (matrixOperator (reconstructed f tests histories s))))
  have hε : 0 ≤ (r:ℝ) * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ :=
    (norm_nonneg _).trans hω.2.1
  apply (div_le_div_of_nonneg_right hnum (sub_pos.mpr hE).le).trans
  apply div_le_div_of_nonneg_left (by positivity) (sub_pos.mpr hgap)
  exact sub_le_sub_left hω.2.1 _

/-- On the very same simultaneous reset event, a separated population table
has the data-selected singular-subspace certificate. -/
theorem reset_spectral_event
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O)) (i₀ : Fin r)
    (hN : 0 < N) (X : DataIndex A O r → Fin N → Ω → ℝ) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = f (experimentWord tests histories w))
    (hrank : 0 < Module.finrank ℝ (matrixOperator (core f tests histories)).toLinearMap.range)
    (hsmall : r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ <
      Spectral.leastPositive (matrixOperator (core f tests histories)).toLinearMap / 2) :
    1-δ ≤ μ.real {ω |
      let M := matrixOperator (core f tests histories)
      let E := matrixOperator (estimatedCore X ω - core f tests histories)
      let ε := (r:ℝ) * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ
      Spectral.leastPositive M.toLinearMap - ε ≤
        (M+E).toLinearMap.singularValues (Module.finrank ℝ M.toLinearMap.range-1) ∧
      (M+E).toLinearMap.singularValues (Module.finrank ℝ M.toLinearMap.range) ≤ ε ∧
      ‖M.toLinearMap.range.starProjection - (Spectral.learnedLeft M E).starProjection‖ ≤
        2*ε/Spectral.leastPositive M.toLinearMap ∧
      2*ε/Spectral.leastPositive M.toLinearMap < 1} := by
  have he := reset_table_event f tests histories i₀ hN X hδ hδ1 hind hm hb hp
  apply he.trans (measureReal_mono ?_)
  intro ω hω
  exact Spectral.finite_table_stability _ _ hrank _ hω.2.1 hsmall

/-- The four quantitative conclusions of the constructed finite-table subspace theorem. -/
def SpectralCertificate (M E : EuclideanSpace ℝ (Fin r) →L[ℝ] EuclideanSpace ℝ (Fin r))
    (ε : ℝ) : Prop :=
  Spectral.leastPositive M.toLinearMap - ε ≤
      (M+E).toLinearMap.singularValues (Module.finrank ℝ M.toLinearMap.range-1) ∧
  (M+E).toLinearMap.singularValues (Module.finrank ℝ M.toLinearMap.range) ≤ ε ∧
  ‖M.toLinearMap.range.starProjection - (Spectral.learnedLeft M E).starProjection‖ ≤
    2*ε/Spectral.leastPositive M.toLinearMap ∧
  2*ε/Spectral.leastPositive M.toLinearMap < 1

/-- Joint conclusions indexed by one sample outcome, with one common entry budget. -/
def JointCertificate
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O))
    (X : DataIndex A O r → Fin N → Ω → ℝ) (ω : Ω) (ε : ℝ) : Prop :=
  ‖estimatedInitial X ω - WithLp.toLp 2 (fun i => f (tests i))‖ ≤ Real.sqrt r*ε ∧
  ‖matrixOperator (estimatedCore X ω-core f tests histories)‖ ≤ r*ε ∧
  (∀ s, ‖(matrixOperator (estimatedShift X s ω)).comp
      (Identification.pinvL (matrixOperator (estimatedCore X ω))) -
      matrixOperator (reconstructed f tests histories s)‖ ≤
    ((r:ℝ)*ε + ‖matrixOperator (reconstructed f tests histories s)‖*((r:ℝ)*ε)) /
      (Identification.rowGain (matrixOperator (core f tests histories))-(r:ℝ)*ε)) ∧
  SpectralCertificate (matrixOperator (core f tests histories))
    (matrixOperator (estimatedCore X ω-core f tests histories)) ((r:ℝ)*ε)

omit [Fintype A] [Fintype O] [MeasurableSpace Ω] in
/-- One entry event implies all certificates together. No probability budgets
are added when the operator and spectral conclusions use the same data. -/
theorem simultaneous_certificates_of_entries
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O))
    (hH : IsUnit (core f tests histories).det)
    (X : DataIndex A O r → Fin N → Ω → ℝ) (ω : Ω) (ε : ℝ) (hε : 0 ≤ ε)
    (hω : ∀ w, |ResetCertificate.sampleMean (X w) ω - f (experimentWord tests histories w)| ≤ ε)
    (hgap : (r:ℝ)*ε < Identification.rowGain (matrixOperator (core f tests histories)))
    (hrank : 0 < Module.finrank ℝ (matrixOperator (core f tests histories)).toLinearMap.range)
    (hsmall : (r:ℝ)*ε < Spectral.leastPositive (matrixOperator (core f tests histories)).toLinearMap / 2) :
    JointCertificate f tests histories X ω ε := by
  have hcore : ‖matrixOperator (estimatedCore X ω-core f tests histories)‖ ≤ (r:ℝ)*ε := by
    apply ResetCertificate.matrix_opNorm_le _ ε hε
    intro i j
    exact hω (.inl (i,j))
  have hshift : ∀ s, ‖matrixOperator (estimatedShift X s ω-shiftedCore f tests histories s)‖ ≤ (r:ℝ)*ε := by
    intro s
    apply ResetCertificate.matrix_opNorm_le _ ε hε
    intro i j
    exact hω (.inr (.inl (s,i,j)))
  refine ⟨?_, hcore, ?_, ?_⟩
  · apply ResetCertificate.vector_norm_le _ ε hε
    intro i
    exact hω (.inr (.inr i))
  · intro s
    rw [← sampled_tableFit f tests histories X s ω]
    have hE := hcore.trans_lt hgap
    apply (tableFit_error f tests histories hH s _ _ hE).trans
    have hnum := add_le_add (hshift s)
      (mul_le_mul_of_nonneg_left hcore (norm_nonneg (matrixOperator (reconstructed f tests histories s))))
    apply (div_le_div_of_nonneg_right hnum (sub_pos.mpr hE).le).trans
    apply div_le_div_of_nonneg_left (by positivity) (sub_pos.mpr hgap)
    exact sub_le_sub_left hcore _
  · exact Spectral.finite_table_stability _ _ hrank _ hcore hsmall

/-- P37's joint statistical event retains P35's original failure budget. -/
theorem reset_joint_event
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O)) (i₀ : Fin r)
    (hH : IsUnit (core f tests histories).det)
    (hN : 0 < N) (X : DataIndex A O r → Fin N → Ω → ℝ) {δ : ℝ}
    (hδ : 0 < δ) (hδ1 : δ < 1)
    (hind : ∀ w, iIndepFun (X w) μ) (hm : ∀ w i, Measurable (X w i))
    (hb : ∀ w i, ∀ᵐ ω ∂μ, X w i ω ∈ Set.Icc (0:ℝ) 1)
    (hp : ∀ w i, ∫ ω, X w i ω ∂μ = f (experimentWord tests histories w))
    (hgap : r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ <
      Identification.rowGain (matrixOperator (core f tests histories)))
    (hrank : 0 < Module.finrank ℝ (matrixOperator (core f tests histories)).toLinearMap.range)
    (hsmall : r * ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ <
      Spectral.leastPositive (matrixOperator (core f tests histories)).toLinearMap / 2) :
    1-δ ≤ μ.real {ω | JointCertificate f tests histories X ω
      (ResetCertificate.radius (Fintype.card (DataIndex A O r)) N δ)} := by
  let : Nonempty (DataIndex A O r) := ⟨.inr (.inr i₀)⟩
  have he := ResetCertificate.reset_probability_certificate hN X
    (fun w => f (experimentWord tests histories w)) hδ hδ1 hind hm hb hp
  apply he.trans (measureReal_mono ?_)
  intro ω hω
  exact simultaneous_certificates_of_entries f tests histories hH X ω _
    (Real.sqrt_nonneg _) hω hgap hrank hsmall

omit [Fintype A] [Fintype O] [MeasurableSpace Ω] in
/-- Filtering is conditional on branch margins and state bounds on the very
same joint event. It spends no new statistical error budget. -/
theorem filtering_on_joint_event
    (f : List (A × O) → ℝ) (tests histories : Fin r → List (A × O))
    (X : DataIndex A O r → Fin N → Ω → ℝ) (ω : Ω) (ε : ℝ)
    (hc : JointCertificate f tests histories X ω ε)
    (s : ℕ → A × O) (z zhat : ℕ → EuclideanSpace ℝ (Fin r)) (i₀ : Fin r)
    (R : ℝ) (ηhat : ℕ → ℝ)
    (true_step : ∀ t, z (t+1) = Filtering.normalize (EuclideanSpace.proj i₀)
      (matrixOperator (reconstructed f tests histories (s t)) (z t)))
    (fit_step : ∀ t, zhat (t+1) = Filtering.normalize (EuclideanSpace.proj i₀)
      ((matrixOperator (estimatedShift X (s t) ω)).comp
        (Identification.pinvL (matrixOperator (estimatedCore X ω))) (zhat t)))
    (hz : ∀ t, ‖z t‖ ≤ R)
    (hp : ∀ t, (matrixOperator (reconstructed f tests histories (s t)) (z t)) i₀ ≠ 0)
    (hq : ∀ t, ηhat t ≤ ((matrixOperator (estimatedShift X (s t) ω)).comp
      (Identification.pinvL (matrixOperator (estimatedCore X ω))) (zhat t)) i₀)
    (hη : ∀ t, 0 < ηhat t) (T : ℕ) :
    ‖zhat T-z T‖ ≤ Stability.errorEnvelope
      (fun t => (1+R*‖(EuclideanSpace.proj i₀ : EuclideanSpace ℝ (Fin r) →L[ℝ] ℝ)‖) *
        ‖(matrixOperator (estimatedShift X (s t) ω)).comp
          (Identification.pinvL (matrixOperator (estimatedCore X ω)))‖ / ηhat t)
      (fun t => (1+R*‖(EuclideanSpace.proj i₀ : EuclideanSpace ℝ (Fin r) →L[ℝ] ℝ)‖) *
        (((r:ℝ)*ε + ‖matrixOperator (reconstructed f tests histories (s t))‖*((r:ℝ)*ε)) /
          (Identification.rowGain (matrixOperator (core f tests histories))-(r:ℝ)*ε)) *
          R / ηhat t) ‖zhat 0-z 0‖ T := by
  exact Filtering.filtering_path (EuclideanSpace.proj i₀)
    (fun t => matrixOperator (reconstructed f tests histories (s t)))
    (fun t => (matrixOperator (estimatedShift X (s t) ω)).comp
      (Identification.pinvL (matrixOperator (estimatedCore X ω)))) z zhat R
    (fun t => ‖(matrixOperator (estimatedShift X (s t) ω)).comp
      (Identification.pinvL (matrixOperator (estimatedCore X ω)))‖)
    (fun t => ((r:ℝ)*ε + ‖matrixOperator (reconstructed f tests histories (s t))‖*((r:ℝ)*ε)) /
      (Identification.rowGain (matrixOperator (core f tests histories))-(r:ℝ)*ε))
    ηhat true_step fit_step (fun _ => le_rfl) (fun t => hc.2.2.1 (s t)) hz hp hq hη T

end ResetData
end Komorebi.LSM.ConditionalStochasticCompletion
