import KomorebiPadic.PolynomialCartier
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Data.Fintype.Card

/-! # Finite coefficient states and exact polynomial transitions
The coordinate space is finite over every finite commutative coefficient ring.
Degree closure proves that the coordinate encoder loses no numerator information.
-/
namespace KomorebiPadic
open Polynomial

abbrev CartierCoefficientState (R : Type*) (L D : ℕ) := Fin L → Fin (D+1) → R

structure PolynomialCartierMachine (R : Type*) [CommRing R] (p L J D : ℕ) where
  radix_pos : 0 < p
  target : Fin L → Fin J → Fin L
  kernel : Fin L → Fin J → R[X]
  kernel_degree : ∀ i k, (kernel i k).natDegree ≤ (p-1)*D

variable {R : Type*} [CommRing R] {p L J D : ℕ}

noncomputable def machineBranchNumerator (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) (i : Fin L) (k : Fin J) : R[X] :=
  polynomialCartier p d (numeratorPolynomial D (s i) * M.kernel i k)

noncomputable def machineNextNumerator (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) (j : Fin L) : R[X] :=
  ∑ i : Fin L, ∑ k : Fin J, if M.target i k = j then machineBranchNumerator M d s i k else 0

noncomputable def machineTransition (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) : CartierCoefficientState R L D :=
  fun j => numeratorCoordinates D (machineNextNumerator M d s j)

theorem machineBranchNumerator_degree (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) (i : Fin L) (k : Fin J) :
    (machineBranchNumerator M d s i k).natDegree ≤ D := by
  exact polynomialCartier_mul_degree_le M.radix_pos d _ _
    (numeratorPolynomial_degree D (s i)) (M.kernel_degree i k)

theorem machineNextNumerator_degree (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) (j : Fin L) :
    (machineNextNumerator M d s j).natDegree ≤ D := by
  apply Polynomial.natDegree_sum_le_of_forall_le
  intro i _
  apply Polynomial.natDegree_sum_le_of_forall_le
  intro k _
  split_ifs
  · exact machineBranchNumerator_degree M d s i k
  · simp

/-- Coordinate truncation is proved lossless at every outgoing layer. -/
theorem machineTransition_decode (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s : CartierCoefficientState R L D) (j : Fin L) :
    numeratorPolynomial D (machineTransition M d s j) = machineNextNumerator M d s j :=
  numeratorPolynomial_coordinates _ (machineNextNumerator_degree M d s j)

noncomputable def machineSeries (g : Fin L → PowerSeries R)
    (s : CartierCoefficientState R L D) : PowerSeries R :=
  ∑ i : Fin L, (numeratorPolynomial D (s i) : PowerSeries R) * g i

/-- Routing and summation preserve every branch, including coincident destinations. -/
theorem sum_routed_products (target : Fin L → Fin J → Fin L)
    (x : Fin L → Fin J → PowerSeries R) (g : Fin L → PowerSeries R) :
    (∑ j : Fin L, (∑ i : Fin L, ∑ k : Fin J, if target i k = j then x i k else 0) * g j) =
      ∑ i : Fin L, ∑ k : Fin J, x i k * g (target i k) := by
  simp only [Finset.sum_mul, ite_mul, zero_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  rw [Finset.sum_comm]
  simp

/-- A proved branch law transports to the whole finite coordinate state. -/
theorem machineTransition_series (M : PolynomialCartierMachine R p L J D)
    (g : Fin L → PowerSeries R) (d : ℕ)
    (hstep : ∀ i (P : R[X]), cartierSection p d ((P : PowerSeries R)*g i) =
      ∑ k : Fin J, (polynomialCartier p d (P*M.kernel i k) : PowerSeries R)*g (M.target i k))
    (s : CartierCoefficientState R L D) :
    machineSeries g (machineTransition M d s) = cartierSection p d (machineSeries g s) := by
  have hcoe (j : Fin L) : (machineNextNumerator M d s j : PowerSeries R) =
      ∑ i : Fin L, ∑ k : Fin J,
        if M.target i k = j then (machineBranchNumerator M d s i k : PowerSeries R) else 0 := by
    change Polynomial.coeToPowerSeries.ringHom (∑ i : Fin L, ∑ k : Fin J,
      if M.target i k = j then machineBranchNumerator M d s i k else 0) = _
    simp only [map_sum, apply_ite, map_zero]
    rfl
  unfold machineSeries
  simp only [machineTransition_decode, hcoe]
  rw [sum_routed_products, map_sum]
  apply Finset.sum_congr rfl
  intro i _
  exact (hstep i (numeratorPolynomial D (s i))).symm

omit [CommRing R] in
/-- Exact size of the coordinate state space; it is not a minimal-orbit claim. -/
theorem cartierCoefficientState_card [Fintype R] (L D : ℕ) :
    Fintype.card (CartierCoefficientState R L D) = (Fintype.card R)^(L*(D+1)) := by
  simp [CartierCoefficientState, ← pow_mul, Nat.mul_comm]

/-- Digits are consumed least-significant first. -/
noncomputable def iterateMachine (M : PolynomialCartierMachine R p L J D) :
    List ℕ → CartierCoefficientState R L D → CartierCoefficientState R L D
  | [], s => s
  | d :: ds, s => iterateMachine M ds (machineTransition M d s)

noncomputable def iterateCartier (p : ℕ) : List ℕ → PowerSeries R → PowerSeries R
  | [], F => F
  | d :: ds, F => iterateCartier p ds (cartierSection p d F)

/-- The coefficient index encoded by a least-significant-first word. -/
def cartierWordValue (p : ℕ) : List ℕ → ℕ
  | [] => 0
  | d :: ds => d + p * cartierWordValue p ds

/-- Full coefficient law, including the word length and arbitrary remaining index. -/
theorem coeff_iterateCartier (p : ℕ) (ds : List ℕ) (F : PowerSeries R) (n : ℕ) :
    PowerSeries.coeff n (iterateCartier p ds F) =
      PowerSeries.coeff (p^ds.length*n+cartierWordValue p ds) F := by
  induction ds generalizing F with
  | nil => simp [iterateCartier, cartierWordValue]
  | cons d ds ih =>
    rw [iterateCartier, ih, coeff_cartierSection]
    apply congrArg (fun m => PowerSeries.coeff m F)
    simp only [List.length_cons, cartierWordValue, pow_succ]
    ring

/-- Polynomial state iteration and formal-series iteration commute. -/
theorem iterateMachine_series (M : PolynomialCartierMachine R p L J D)
    (g : Fin L → PowerSeries R)
    (hstep : ∀ d, d < p → ∀ i (P : R[X]),
      cartierSection p d ((P : PowerSeries R)*g i) =
        ∑ k : Fin J, (polynomialCartier p d (P*M.kernel i k) : PowerSeries R)*g (M.target i k))
    (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) (s : CartierCoefficientState R L D) :
    machineSeries g (iterateMachine M ds s) = iterateCartier p ds (machineSeries g s) := by
  induction ds generalizing s with
  | nil => rfl
  | cons d ds ih =>
    rw [iterateMachine, ih (fun e he => hd e (List.mem_cons_of_mem d he)),
      machineTransition_series M g d (hstep d (hd d (by simp))), iterateCartier]

/-- Constant output after a word gives the original coefficient indexed by that word. -/
theorem iterateMachine_output (M : PolynomialCartierMachine R p L J D)
    (g : Fin L → PowerSeries R)
    (hstep : ∀ d, d < p → ∀ i (P : R[X]),
      cartierSection p d ((P : PowerSeries R)*g i) =
        ∑ k : Fin J, (polynomialCartier p d (P*M.kernel i k) : PowerSeries R)*g (M.target i k))
    (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) (s : CartierCoefficientState R L D) :
    PowerSeries.constantCoeff (machineSeries g (iterateMachine M ds s)) =
      PowerSeries.coeff (cartierWordValue p ds) (machineSeries g s) := by
  rw [iterateMachine_series M g hstep ds hd,
    ← PowerSeries.coeff_zero_eq_constantCoeff, coeff_iterateCartier]
  simp

/-- The finite transition is additive even when branch destinations coincide. -/
theorem machineTransition_add (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (s t : CartierCoefficientState R L D) :
    machineTransition M d (s+t) = machineTransition M d s + machineTransition M d t := by
  classical
  have hb (i : Fin L) (k : Fin J) :
      machineBranchNumerator M d (s+t) i k =
        machineBranchNumerator M d s i k + machineBranchNumerator M d t i k := by
    unfold machineBranchNumerator
    have hp : numeratorPolynomial D ((s+t) i) = numeratorPolynomial D (s i)+numeratorPolynomial D (t i) :=
      (Polynomial.ofFn (D+1)).map_add (s i) (t i)
    rw [hp, add_mul]
    exact (polynomialCartierLinear p d M.radix_pos).map_add _ _
  have hn (j : Fin L) : machineNextNumerator M d (s+t) j =
      machineNextNumerator M d s j + machineNextNumerator M d t j := by
    unfold machineNextNumerator
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i _
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro k _
    split_ifs <;> simp [hb]
  funext j
  change numeratorCoordinates D (machineNextNumerator M d (s+t) j) = _
  rw [hn]
  exact (Polynomial.toFn (D+1)).map_add _ _

/-- Scalar linearity is proved over the coefficient ring, including zero divisors. -/
theorem machineTransition_smul (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) (a : R) (s : CartierCoefficientState R L D) :
    machineTransition M d (a • s) = a • machineTransition M d s := by
  classical
  have hb (i : Fin L) (k : Fin J) :
      machineBranchNumerator M d (a • s) i k = a • machineBranchNumerator M d s i k := by
    unfold machineBranchNumerator
    have hp : numeratorPolynomial D ((a • s) i) = a • numeratorPolynomial D (s i) :=
      (Polynomial.ofFn (D+1)).map_smul a (s i)
    rw [hp, smul_mul_assoc]
    exact (polynomialCartierLinear p d M.radix_pos).map_smul a _
  have hn (j : Fin L) : machineNextNumerator M d (a • s) j = a • machineNextNumerator M d s j := by
    unfold machineNextNumerator
    rw [Finset.smul_sum]
    apply Finset.sum_congr rfl
    intro i _
    rw [Finset.smul_sum]
    apply Finset.sum_congr rfl
    intro k _
    split_ifs <;> simp [hb]
  funext j
  change numeratorCoordinates D (machineNextNumerator M d (a • s) j) = _
  rw [hn]
  exact (Polynomial.toFn (D+1)).map_smul a _

noncomputable def machineTransitionLinear (M : PolynomialCartierMachine R p L J D)
    (d : ℕ) : CartierCoefficientState R L D →ₗ[R] CartierCoefficientState R L D where
  toFun := machineTransition M d
  map_add' := machineTransition_add M d
  map_smul' := machineTransition_smul M d

end KomorebiPadic
