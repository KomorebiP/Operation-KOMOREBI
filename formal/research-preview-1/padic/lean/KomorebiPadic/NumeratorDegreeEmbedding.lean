import KomorebiPadic.DegreePrunedMaskCertificate

/-! # Exact coordinate simulation under an increased numerator capacity
This is an injective embedding, not an equivalence onto the larger state space.
It applies to unchanged layer/branch types, target routing and polynomial kernels.
-/
namespace KomorebiPadic
open Polynomial
variable {R : Type*} [CommRing R] {p L J D₁ D₂ : ℕ}

noncomputable def raiseNumeratorDegree (D₁ D₂ : ℕ)
    (s : CartierCoefficientState R L D₁) : CartierCoefficientState R L D₂ :=
  fun i => numeratorCoordinates D₂ (numeratorPolynomial D₁ (s i))

/-- Re-encoding at a larger bound loses no polynomial coefficient. -/
theorem raiseNumeratorDegree_decode (hD : D₁ ≤ D₂)
    (s : CartierCoefficientState R L D₁) (i : Fin L) :
    numeratorPolynomial D₂ (raiseNumeratorDegree D₁ D₂ s i) = numeratorPolynomial D₁ (s i) :=
  numeratorPolynomial_coordinates _ ((numeratorPolynomial_degree D₁ (s i)).trans hD)

/-- Zero-padding cannot identify two distinct small coordinate states. -/
theorem raiseNumeratorDegree_injective (hD : D₁ ≤ D₂) :
    Function.Injective (raiseNumeratorDegree (R := R) (L := L) D₁ D₂) := by
  intro s t heq
  funext i
  have he := congrArg (fun u => numeratorPolynomial D₂ (u i)) heq
  rw [raiseNumeratorDegree_decode hD, raiseNumeratorDegree_decode hD] at he
  have hc := congrArg (numeratorCoordinates D₁) he
  simpa only [numeratorCoordinates_polynomial] using hc

theorem machineSeries_raiseNumeratorDegree (hD : D₁ ≤ D₂)
    (g : Fin L → PowerSeries R) (s : CartierCoefficientState R L D₁) :
    machineSeries g (raiseNumeratorDegree D₁ D₂ s) = machineSeries g s := by
  simp only [machineSeries, raiseNumeratorDegree_decode hD]

/-- Same kernels and targets make the complete routed transition commute with the embedding. -/
theorem machineTransition_raiseNumeratorDegree (hD : D₁ ≤ D₂)
    (M₁ : PolynomialCartierMachine R p L J D₁) (M₂ : PolynomialCartierMachine R p L J D₂)
    (ht : M₁.target = M₂.target) (hk : M₁.kernel = M₂.kernel)
    (d : ℕ) (s : CartierCoefficientState R L D₁) :
    raiseNumeratorDegree D₁ D₂ (machineTransition M₁ d s) =
      machineTransition M₂ d (raiseNumeratorDegree D₁ D₂ s) := by
  have hb (i : Fin L) (k : Fin J) :
      machineBranchNumerator M₂ d (raiseNumeratorDegree D₁ D₂ s) i k =
        machineBranchNumerator M₁ d s i k := by
    simp only [machineBranchNumerator, raiseNumeratorDegree_decode hD, hk]
  have hn (j : Fin L) :
      machineNextNumerator M₂ d (raiseNumeratorDegree D₁ D₂ s) j =
        machineNextNumerator M₁ d s j := by
    simp only [machineNextNumerator, hb, ht]
  funext j
  change numeratorCoordinates D₂ (numeratorPolynomial D₁ (machineTransition M₁ d s j)) = _
  rw [machineTransition_decode]
  exact congrArg (numeratorCoordinates D₂) (hn j).symm

/-- Ordered state iteration commutes for every word, without a digit-range hypothesis. -/
theorem iterateMachine_raiseNumeratorDegree (hD : D₁ ≤ D₂)
    (M₁ : PolynomialCartierMachine R p L J D₁) (M₂ : PolynomialCartierMachine R p L J D₂)
    (ht : M₁.target = M₂.target) (hk : M₁.kernel = M₂.kernel)
    (ds : List ℕ) (s : CartierCoefficientState R L D₁) :
    raiseNumeratorDegree D₁ D₂ (iterateMachine M₁ ds s) =
      iterateMachine M₂ ds (raiseNumeratorDegree D₁ D₂ s) := by
  induction ds generalizing s with
  | nil => rfl
  | cons d ds ih =>
    simp only [iterateMachine]
    rw [ih, machineTransition_raiseNumeratorDegree hD M₁ M₂ ht hk]

/-- The new mask machine embeds in Block25's larger numerator space for arbitrary states. -/
theorem degreePrunedMask_transition_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : ℕ) (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) :
    raiseNumeratorDegree _ (cartierNumeratorBound p r A B)
      (machineTransition (degreePrunedMaskMachine p r A B hp) d s) =
    machineTransition (prunedMaskMachine p r A B hp) d
      (raiseNumeratorDegree _ (cartierNumeratorBound p r A B) s) :=
  machineTransition_raiseNumeratorDegree (degreePrunedNumeratorBound_le_original p r A B)
    _ _ rfl rfl d s

theorem degreePrunedMask_initial_embedding (p r : ℕ) (A B : ℤ[X]) :
    raiseNumeratorDegree _ (cartierNumeratorBound p r A B) (degreePrunedMaskInitial p r A B) =
      prunedMaskInitial p r A B := by
  classical
  funext i
  by_cases hi : i.val = 0
  · simp only [raiseNumeratorDegree, degreePrunedMaskInitial, prunedMaskInitial, hi, ↓reduceIte]
    rw [numeratorPolynomial_coordinates _
      (Polynomial.natDegree_map_le.trans (degreePrunedNumeratorBound_initial p r A B))]
  · simp [raiseNumeratorDegree, degreePrunedMaskInitial, prunedMaskInitial, hi,
      numeratorPolynomial, numeratorCoordinates]

/-- Exact coordinate equality along the entire initial orbit, not just equality of outputs. -/
theorem degreePrunedMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List ℕ) :
    raiseNumeratorDegree _ (cartierNumeratorBound p r A B)
      (iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B)) =
    iterateMachine (prunedMaskMachine p r A B hp) ds (prunedMaskInitial p r A B) := by
  rw [iterateMachine_raiseNumeratorDegree (degreePrunedNumeratorBound_le_original p r A B)
    (degreePrunedMaskMachine p r A B hp) (prunedMaskMachine p r A B hp)
    rfl rfl, degreePrunedMask_initial_embedding]

/-- The finite output commutes with zero-padding for every small state. -/
theorem degreePrunedMask_output_embedding (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) :
    prunedMaskOutput p r A B hp hr hB
      (raiseNumeratorDegree _ (cartierNumeratorBound p r A B) s) =
      degreePrunedMaskOutput p r A B hp hr hB s := by
  rw [prunedMaskOutput_series p r A B hp hr hB _ (canonicalMaskSeries_constant p r A B hp hr hB),
    degreePrunedMaskOutput_series p r A B hp hr hB _ (canonicalMaskSeries_constant p r A B hp hr hB),
    machineSeries_raiseNumeratorDegree (degreePrunedNumeratorBound_le_original p r A B)]

end KomorebiPadic
