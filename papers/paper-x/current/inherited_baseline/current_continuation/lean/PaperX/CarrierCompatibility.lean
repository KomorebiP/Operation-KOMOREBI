import PaperX.CarrierPolynomials
import Mathlib.Topology.Constructions

/-! Coefficient-independent multiplicities produce common polynomials at the
explicitly permitted samples. This is not the full arithmetic notion of strict
compatibility: no Hodge--Tate or Weil--Deligne realization is postulated here. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CarrierCompatibility
open scoped BigOperators Matrix
open PaperX.CarrierSummands PaperX.CarrierPolynomials PaperX.TraceRecovery

variable {K G I : Type*} [Field K] [Monoid G] [Fintype I]
variable {V : I → Type*} [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
variable [∀ i, FiniteDimensional K (V i)]

theorem common_polynomial {E : Type*} [CommRing E] (σ : E →+* K)
    (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ) (g : G)
    (P : I → Polynomial E) (hP : ∀ i, (ρ i g).charpoly = (P i).map σ) :
    (copiesRep ρ m g).charpoly = (∏ i, P i ^ m i).map σ := by
  rw [copies_charpoly]
  simp only [hP]
  simp [Polynomial.map_prod]

/-- The observed vector is made from traces of the constructed representation. -/
theorem sampled_trace [DecidableEq I] (ρ : ∀ i, Representation K G (V i))
    (m : I → ℕ) (s : I → G) :
    (fun j => LinearMap.trace K _ (copiesRep ρ m (s j))) =
      (fun j i => LinearMap.trace K _ (ρ i (s j))) *ᵥ (fun i => (m i : K)) := by
  funext j
  simp [copies_trace, Matrix.mulVec, dotProduct, mul_comm]

theorem recovery_of_actual_summand [DecidableEq I]
    (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ) (s : I → G)
    (h : Matrix.det (fun j i => LinearMap.trace K _ (ρ i (s j))) ≠ 0) :
    recover (fun j i => LinearMap.trace K _ (ρ i (s j)))
      (fun j => LinearMap.trace K _ (copiesRep ρ m (s j))) = (fun i => (m i : K)) := by
  rw [sampled_trace, recover_trace _ h]

theorem multiplicities_unique_from_actual_traces [DecidableEq I] [CharZero K]
    (ρ : ∀ i, Representation K G (V i)) (m n : I → ℕ) (s : I → G)
    (h : Matrix.det (fun j i => LinearMap.trace K _ (ρ i (s j))) ≠ 0)
    (ht : ∀ j, LinearMap.trace K _ (copiesRep ρ m (s j)) =
      LinearMap.trace K _ (copiesRep ρ n (s j))) : m = n := by
  apply natural_multiplicity_unique (fun j i => LinearMap.trace K _ (ρ i (s j))) h
  rw [← sampled_trace, ← sampled_trace]
  exact funext ht

omit [Fintype I] [∀ i, FiniteDimensional K (V i)] in
/-- Triviality on a supplied subgroup (or set) is preserved by construction. -/
theorem copies_trivial_on (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ)
    (S : Set G) (h : ∀ i g, g ∈ S → ρ i g = 1) (g : G) (hg : g ∈ S) :
    copiesRep ρ m g = 1 := by
  apply LinearMap.ext
  intro x
  funext i k
  simp [h i g hg]

section Topology
variable [TopologicalSpace G] [∀ i, TopologicalSpace (V i)]

omit [Fintype I] [∀ i, FiniteDimensional K (V i)] in
/-- Jointly continuous constituent actions give a jointly continuous sum action. -/
theorem continuous_copies_action (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ)
    (h : ∀ i, Continuous (fun p : G × V i => ρ i p.1 p.2)) :
    Continuous (fun p : G × Copies V m => copiesRep ρ m p.1 p.2) := by
  apply continuous_pi
  intro i
  apply continuous_pi
  intro k
  exact (h i).comp (continuous_fst.prodMk
    ((continuous_apply k).comp ((continuous_apply i).comp continuous_snd)))

omit [Fintype I] [∀ i, FiniteDimensional K (V i)] in
theorem continuous_inclusion {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Continuous (inclusion (R := K) (V := V) h) := by
  apply continuous_pi
  intro i
  apply continuous_pi
  intro k
  by_cases hk : k.val < m i
  · simpa [inclusion, hk, Function.comp_def] using
      (continuous_apply (⟨k.val, hk⟩ : Fin (m i))).comp (continuous_apply i)
  · simpa [inclusion, hk, Function.comp_def] using
      (continuous_const : Continuous (fun _ : Copies V m => (0 : V i)))

omit [Fintype I] [∀ i, FiniteDimensional K (V i)] in
theorem continuous_retraction {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Continuous (retraction (R := K) (V := V) h) := by
  apply continuous_pi
  intro i
  apply continuous_pi
  intro k
  exact (continuous_apply (⟨k.val, lt_of_lt_of_le k.isLt (h i)⟩ : Fin (c i))).comp
    (continuous_apply i)
end Topology

end PaperX.CarrierCompatibility
