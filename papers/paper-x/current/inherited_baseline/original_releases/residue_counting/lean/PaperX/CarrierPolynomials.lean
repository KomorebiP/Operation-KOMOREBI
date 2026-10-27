import PaperX.CarrierSummands
import PaperX.TraceRecovery
import Mathlib.LinearAlgebra.Charpoly.ToMatrix
import Mathlib.LinearAlgebra.Trace
import Mathlib.Data.Fintype.Option

set_option autoImplicit false
noncomputable section
namespace PaperX.CarrierPolynomials
open scoped BigOperators
open PaperX.CarrierSummands

variable {K : Type*} [Field K]

def piEnd {I : Type*} {V : I → Type*}
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
    (f : ∀ i, Module.End K (V i)) : Module.End K (∀ i, V i) :=
  LinearMap.pi (fun i => (f i).comp (LinearMap.proj i))

@[simp] theorem piEnd_apply {I : Type*} {V : I → Type*}
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
    (f : ∀ i, Module.End K (V i)) (x : ∀ i, V i) (i : I) :
    piEnd f x i = f i (x i) := rfl

/-- Determinant polynomial of an actual finite dependent product of maps. -/
theorem charpoly_piEnd (I : Type*) [Fintype I] (V : I → Type*)
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)] [∀ i, FiniteDimensional K (V i)]
    (f : ∀ i, Module.End K (V i)) :
    (piEnd f).charpoly = ∏ i, (f i).charpoly := by
  classical
  revert V
  refine Fintype.induction_empty_option (P := fun J _ =>
    ∀ (U : J → Type _) [∀ j, AddCommGroup (U j)] [∀ j, Module K (U j)]
      [∀ j, FiniteDimensional K (U j)] (f : ∀ j, Module.End K (U j)),
      (piEnd f).charpoly = ∏ j, (f j).charpoly) ?_ ?_ ?_ I
  · intro A B _ e ih V _ _ _ f
    let : Fintype A := Fintype.ofEquiv B e.symm
    let D := LinearEquiv.piCongrLeft K V e
    have hD : D.conj (piEnd (fun i => f (e i))) = piEnd f := by
      apply LinearMap.ext
      intro x
      change D (piEnd (fun i => f (e i)) (D.symm x)) = piEnd f x
      apply D.symm.injective
      rw [LinearEquiv.symm_apply_apply]
      rfl
    rw [← hD, LinearEquiv.charpoly_conj, ih]
    exact Fintype.prod_equiv e _ _ (fun _ => rfl)
  · intro V _ _ _ f
    have hf : piEnd f = 0 := Subsingleton.elim _ _
    simp [hf, Module.finrank_zero_of_subsingleton]
  · intro A _ ih V _ _ _ f
    let D := LinearEquiv.piOptionEquivProd K (M := V)
    have hD : D.conj (piEnd f) = (f none).prodMap (piEnd (fun i => f (some i))) := by
      apply LinearMap.ext
      intro x
      apply Prod.ext <;> rfl
    rw [← LinearEquiv.charpoly_conj D (piEnd f), hD,
      LinearMap.charpoly_prodMap, ih, Fintype.prod_option]

/-- Actual traces add under the same dependent product construction. -/
theorem trace_piEnd (I : Type*) [Fintype I] (V : I → Type*)
    [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)] [∀ i, FiniteDimensional K (V i)]
    (f : ∀ i, Module.End K (V i)) :
    LinearMap.trace K _ (piEnd f) = ∑ i, LinearMap.trace K _ (f i) := by
  classical
  revert V
  refine Fintype.induction_empty_option (P := fun J _ =>
    ∀ (U : J → Type _) [∀ j, AddCommGroup (U j)] [∀ j, Module K (U j)]
      [∀ j, FiniteDimensional K (U j)] (f : ∀ j, Module.End K (U j)),
      LinearMap.trace K _ (piEnd f) = ∑ j, LinearMap.trace K _ (f j)) ?_ ?_ ?_ I
  · intro A B _ e ih V _ _ _ f
    let : Fintype A := Fintype.ofEquiv B e.symm
    let D := LinearEquiv.piCongrLeft K V e
    have hD : D.conj (piEnd (fun i => f (e i))) = piEnd f := by
      apply LinearMap.ext
      intro x
      change D (piEnd (fun i => f (e i)) (D.symm x)) = piEnd f x
      apply D.symm.injective
      rw [LinearEquiv.symm_apply_apply]
      rfl
    rw [← hD, LinearMap.trace_conj', ih]
    exact Fintype.sum_equiv e _ _ (fun _ => rfl)
  · intro V _ _ _ f
    have hf : piEnd f = 0 := Subsingleton.elim _ _
    simp [hf]
  · intro A _ ih V _ _ _ f
    let D := LinearEquiv.piOptionEquivProd K (M := V)
    have hD : D.conj (piEnd f) = (f none).prodMap (piEnd (fun i => f (some i))) := by
      apply LinearMap.ext
      intro x
      apply Prod.ext <;> rfl
    rw [← LinearMap.trace_conj' (piEnd f) D, hD,
      LinearMap.trace_prodMap', ih, Fintype.sum_option]

variable {G I : Type*} [Monoid G] [Fintype I]
variable {V : I → Type*} [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
variable [∀ i, FiniteDimensional K (V i)]

theorem copies_charpoly (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ) (g : G) :
    (copiesRep ρ m g).charpoly = ∏ i, (ρ i g).charpoly ^ m i := by
  change (piEnd (fun i => piEnd (fun _ : Fin (m i) => ρ i g))).charpoly = _
  rw [charpoly_piEnd]
  apply Finset.prod_congr rfl
  intro i _
  rw [charpoly_piEnd]
  simp

theorem copies_trace (ρ : ∀ i, Representation K G (V i)) (m : I → ℕ) (g : G) :
    LinearMap.trace K _ (copiesRep ρ m g) = ∑ i, (m i : K) * LinearMap.trace K _ (ρ i g) := by
  change LinearMap.trace K _ (piEnd (fun i => piEnd (fun _ : Fin (m i) => ρ i g))) = _
  rw [trace_piEnd]
  apply Finset.sum_congr rfl
  intro i _
  rw [trace_piEnd]
  simp

theorem copies_finrank (m : I → ℕ) :
    Module.finrank K (Copies V m) = ∑ i, m i * Module.finrank K (V i) := by
  simp [Copies, Module.finrank_pi_fintype]

end PaperX.CarrierPolynomials
