module
public import PolynomialAnalyticInverse
public import PolynomialJointSystem
public import PolynomialAnalyticBlocks

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialAnalyticImplicit
open Filter Set
open scoped Topology
open Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialAnalyticInverse

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜]
variable {e k : ℕ}

/-- The solved-coordinate projection as a continuous linear map. -/
def solvedPartCLM : (Fin (e + k) → 𝕜) →L[𝕜] (Fin e → 𝕜) :=
  ContinuousLinearMap.pi fun i => ContinuousLinearMap.proj (Fin.castAdd k i)

@[simp] theorem solvedPartCLM_apply (z : Fin (e + k) → 𝕜) :
    solvedPartCLM z = solvedPart z := rfl

/-- Insert a parameter displacement and zero solved-coordinate displacement. -/
def parameterInjectionCLM : (Fin k → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜) :=
  ContinuousLinearMap.pi fun i => Fin.addCases (fun _ => 0)
    (fun j => ContinuousLinearMap.proj j) i

@[simp] theorem parameterInjectionCLM_apply (v : Fin k → 𝕜) :
    parameterInjectionCLM (e := e) v = join 0 v := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [parameterInjectionCLM]

variable [CompleteSpace 𝕜]

/-- An analytic inverse of an augmented map supplies an exact open local graph.
This helper retains the inverse derivative explicitly for the polynomial specialization. -/
theorem exists_analytic_graph
    (P : (Fin (e + k) → 𝕜) → (Fin e → 𝕜))
    (a : Fin (e + k) → 𝕜) (hP : P a = 0)
    (A : (Fin (e + k) → 𝕜) ≃L[𝕜] (Fin (e + k) → 𝕜))
    (ha : AnalyticAt 𝕜 (fun z => join (P z) (freePart z)) a)
    (hd : HasStrictFDerivAt (fun z => join (P z) (freePart z))
      (A : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)) a) :
    ∃ (ψ : (Fin k → 𝕜) → (Fin e → 𝕜)) (U : Set (Fin k → 𝕜))
      (V : Set (Fin e → 𝕜)),
      IsOpen U ∧ IsOpen V ∧ freePart a ∈ U ∧ solvedPart a ∈ V ∧
      ψ (freePart a) = solvedPart a ∧ AnalyticOnNhd 𝕜 ψ U ∧
      (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V, P (join y t) = 0 ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ
        ((solvedPartCLM (e := e) (k := k)).comp
        ((A.symm : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)).comp
          (parameterInjectionCLM (e := e) (k := k))))
        (freePart a) := by
  let f := fun z => join (P z) (freePart z)
  let g := hd.localInverse f A a
  let ψ := fun t => solvedPart (g (join 0 t))
  have hfa : f a = join 0 (freePart a) := by simp [f, hP]
  have hga : g (join 0 (freePart a)) = a := by
    rw [← hfa]
    exact hd.localInverse_apply_image
  have hψa : ψ (freePart a) = solvedPart a := by simp [ψ, hga]
  have hag : AnalyticAt 𝕜 g (join 0 (freePart a)) := by
    rw [← hfa]
    exact analyticAt_inverse ha hd
  have hag' : AnalyticAt 𝕜 g
      (parameterInjectionCLM (e := e) (k := k) (freePart a)) := by
    simpa only [parameterInjectionCLM_apply] using hag
  have haψ : AnalyticAt 𝕜 ψ (freePart a) := by
    have hi := (parameterInjectionCLM (𝕜 := 𝕜) (e := e) (k := k)).analyticAt
      (freePart a)
    have hg := hag'.comp hi
    have h := ((solvedPartCLM (𝕜 := 𝕜) (e := e) (k := k)).analyticAt _).comp hg
    simpa only [Function.comp_def, solvedPartCLM_apply, parameterInjectionCLM_apply] using h
  have hdg : HasStrictFDerivAt g (A.symm : _ →L[𝕜] _)
      (parameterInjectionCLM (e := e) (k := k) (freePart a)) := by
    simpa only [parameterInjectionCLM_apply, ← hfa] using hd.to_localInverse
  have hdψ : HasStrictFDerivAt ψ
      ((solvedPartCLM (e := e) (k := k)).comp
        ((A.symm : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)).comp
          (parameterInjectionCLM (e := e) (k := k))))
      (freePart a) := by
    have hi := (parameterInjectionCLM (𝕜 := 𝕜) (e := e) (k := k)).hasStrictFDerivAt
      (x := freePart a)
    have hg := hdg.comp (freePart a) hi
    have h := (solvedPartCLM (𝕜 := 𝕜) (e := e) (k := k)).hasStrictFDerivAt.comp
      (freePart a) hg
    simpa only [Function.comp_def, solvedPartCLM_apply, parameterInjectionCLM_apply] using h
  let R := hd.toOpenPartialHomeomorph f
  have hopen : IsOpen {yt : (Fin e → 𝕜) × (Fin k → 𝕜) |
      join yt.1 yt.2 ∈ R.source} := R.open_source.preimage continuous_join
  have hbase : (solvedPart a, freePart a) ∈
      {yt : (Fin e → 𝕜) × (Fin k → 𝕜) | join yt.1 yt.2 ∈ R.source} := by
    simpa using hd.mem_toOpenPartialHomeomorph_source
  obtain ⟨V, U₀, hV, hU₀, hy₀, ht₀, hrect⟩ :=
    isOpen_prod_iff.mp hopen (solvedPart a) (freePart a) hbase
  obtain ⟨W, hW, haW, hanalyticW, hrightW⟩ := exists_open_analytic_inverse ha hd
  let U := U₀ ∩ (parameterInjectionCLM (𝕜 := 𝕜) (e := e) ⁻¹' W) ∩
    {t | AnalyticAt 𝕜 ψ t} ∩ interior (ψ ⁻¹' V)
  have hU : IsOpen U := ((hU₀.inter
    (hW.preimage parameterInjectionCLM.continuous)).inter
    (isOpen_analyticAt 𝕜 ψ)).inter isOpen_interior
  have htU : freePart a ∈ U := by
    refine ⟨⟨⟨ht₀, ?_⟩, haψ⟩, ?_⟩
    · simpa only [Set.mem_preimage, parameterInjectionCLM_apply, hP] using haW
    · rw [mem_interior_iff_mem_nhds]
      exact haψ.continuousAt.preimage_mem_nhds (hV.mem_nhds (hψa ▸ hy₀))
  refine ⟨ψ, U, V, hU, hV, htU, hy₀, hψa, ?_, ?_, ?_, hdψ⟩
  · intro t ht
    exact ht.1.2
  · intro t ht
    exact (interior_subset (s := ψ ⁻¹' V)) ht.2
  · intro t ht y hy
    constructor
    · intro hroot
      have hz : join y t ∈ R.source := hrect (show (y, t) ∈ V ×ˢ U₀ from ⟨hy, ht.1.1.1⟩)
      have hfz : f (join y t) = join 0 t := by simp [f, hroot]
      have hg : g (join 0 t) = join y t := by
        rw [← hfz]
        exact R.left_inv hz
      simp [ψ, hg]
    · intro hsol
      subst y
      have hr : f (g (join 0 t)) = join 0 t := by
        exact hrightW (join 0 t) (by
          simpa only [Set.mem_preimage, parameterInjectionCLM_apply] using ht.1.1.2)
      have hparam : freePart (g (join 0 t)) = t := by
        have := congrArg (freePart (e := e) (q := k)) hr
        simpa [f] using this
      have hroot : P (g (join 0 t)) = 0 := by
        have := congrArg (solvedPart (e := e) (q := k)) hr
        simpa [f] using this
      have hz : join (ψ t) t = g (join 0 t) := by
        change join (solvedPart (g (join 0 t))) t = g (join 0 t)
        calc
          _ = join (solvedPart (g (join 0 t))) (freePart (g (join 0 t))) :=
            congrArg (join (solvedPart (g (join 0 t)))) hparam.symm
          _ = _ := join_parts _
      rw [hz]
      exact hroot

open Komorebi.PolynomialAnalyticEvaluation
open Komorebi.PolynomialAnalyticBlocks

/-- The actual polynomial implicit function theorem: open local graph, analyticity,
and the strict derivative obtained from the actual solved and parameter Jacobians. -/
theorem exists_analytic_implicit
    (F : Fin e → MvPolynomial (Fin (e + k)) 𝕜)
    (a : Fin (e + k) → 𝕜) (hF : evalSystem F a = 0)
    (hJ : IsUnit (Komorebi.PolynomialJointSystem.solvedJacobian F a)) :
    ∃ (ψ : (Fin k → 𝕜) → (Fin e → 𝕜)) (U : Set (Fin k → 𝕜))
      (V : Set (Fin e → 𝕜)),
      IsOpen U ∧ IsOpen V ∧ freePart a ∈ U ∧ solvedPart a ∈ V ∧
      ψ (freePart a) = solvedPart a ∧ AnalyticOnNhd 𝕜 ψ U ∧
      (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V, evalSystem F (join y t) = 0 ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ
        (matrixCLM (-((Komorebi.PolynomialJointSystem.solvedJacobian F a)⁻¹ *
          Komorebi.PolynomialJointSystem.parameterJacobian F a))) (freePart a) := by
  let J := Komorebi.PolynomialJointSystem.solvedJacobian F a
  let K := Komorebi.PolynomialJointSystem.parameterJacobian F a
  let A := upperEquiv J K hJ
  have hshape : evalSystem (Komorebi.PolynomialJointSystem.augmented F 0) =
      fun z => join (evalSystem F z) (freePart z) := by
    funext z
    change (fun i => MvPolynomial.eval z
      (Komorebi.PolynomialJointSystem.augmented F 0 i)) =
        join (fun i => MvPolynomial.eval z (F i)) (freePart z)
    simpa only [sub_zero] using
      Komorebi.PolynomialJointSystem.eval_augmented F (0 : Fin k → 𝕜) z
  have ha := analyticAt_evalSystem (Komorebi.PolynomialJointSystem.augmented F 0) a
  have hd : HasStrictFDerivAt
      (evalSystem (Komorebi.PolynomialJointSystem.augmented F 0))
      (A : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)) a := by
    rw [show (A : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)) =
      matrixCLM (Komorebi.PolynomialBlockInverse.upperBlock J K 1) from
      upperEquiv_toCLM J K hJ]
    simpa only [Komorebi.PolynomialJointSystem.jacobian_augmented] using
      hasStrictFDerivAt_evalSystem (Komorebi.PolynomialJointSystem.augmented F 0) a
  rw [hshape] at ha hd
  obtain ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, hgraph, hder⟩ :=
    exists_analytic_graph (evalSystem F) a hF A ha hd
  refine ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, hgraph, ?_⟩
  have heq : (solvedPartCLM (𝕜 := 𝕜) (e := e) (k := k)).comp
      ((A.symm : (Fin (e + k) → 𝕜) →L[𝕜] (Fin (e + k) → 𝕜)).comp
        (parameterInjectionCLM (e := e) (k := k))) = matrixCLM (-(J⁻¹ * K)) := by
    apply ContinuousLinearMap.ext
    intro v
    simp only [ContinuousLinearMap.comp_apply, solvedPartCLM_apply,
      parameterInjectionCLM_apply]
    exact inverse_solved_zero J K hJ v
  simpa only [heq] using hder

omit [CompleteSpace 𝕜] in
/-- Analyticity supplied by the local graph theorem includes differentiability
at every parameter in its open domain. -/
theorem differentiableOn_of_analytic_graph
    {ψ : (Fin k → 𝕜) → (Fin e → 𝕜)} {U : Set (Fin k → 𝕜)}
    (hψ : AnalyticOnNhd 𝕜 ψ U) : DifferentiableOn 𝕜 ψ U :=
  hψ.differentiableOn

end Komorebi.PolynomialAnalyticImplicit
