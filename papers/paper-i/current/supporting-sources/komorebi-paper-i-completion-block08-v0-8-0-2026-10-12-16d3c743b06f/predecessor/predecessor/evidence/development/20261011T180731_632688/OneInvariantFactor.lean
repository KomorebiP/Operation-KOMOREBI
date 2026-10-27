import PaperICompletion5
import Mathlib.RingTheory.PowerBasis

/-! # One invariant factor with an actual companion-matrix basis
An actual polynomial-module equivalence yields a basis of the given vector
space in which its operator is the usual companion matrix. This is a
mathematical construction, not an executable rational-canonical algorithm.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperICompletion6.OneInvariantFactor
open Polynomial
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.PaperICompletion5.CyclicGeometricCriterion
universe u v
variable {k : Type u} [Field k] {V : Type v} [AddCommGroup V] [Module k V]

/-- The standard companion matrix, including its empty degree-zero convention. -/
def companionMatrix (p : k[X]) : Matrix (Fin p.natDegree) (Fin p.natDegree) k :=
  fun i j => if (j : ℕ) + 1 = p.natDegree then -p.coeff i
    else if (i : ℕ) = (j : ℕ) + 1 then 1 else 0

/-- Forget only the polynomial scalars in an actual one-factor presentation. -/
def quotientVectorEquiv (T : Module.End k V) (p : k[X])
    (E : Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p}) : AdjoinRoot p ≃ₗ[k] V :=
  (E.symm.restrictScalars k).trans (Module.AEval'.of T).symm

/-- The intertwining relation retains the actual operator action. -/
theorem quotientVectorEquiv_intertwines (T : Module.End k V) (p : k[X])
    (E : Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p}) (x : AdjoinRoot p) :
    T (quotientVectorEquiv T p E x) =
      quotientVectorEquiv T p E (AdjoinRoot.root p * x) := by
  apply (Module.AEval'.of T).injective
  change X • E.symm x = E.symm (AdjoinRoot.root p * x)
  rw [← E.symm.map_smul]
  rfl

/-- The quotient power basis transported to the original space. -/
def quotientCompanionBasis (T : Module.End k V) (p : k[X]) (hp : p.Monic)
    (E : Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p}) :
    Module.Basis (Fin p.natDegree) k V :=
  (AdjoinRoot.powerBasis' hp).basis.map (quotientVectorEquiv T p E)

/-- The matrix in the constructed basis is literally the standard companion matrix. -/
theorem toMatrix_quotientCompanionBasis (T : Module.End k V) (p : k[X]) (hp : p.Monic)
    (E : Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p}) :
    LinearMap.toMatrix (quotientCompanionBasis T p hp E)
      (quotientCompanionBasis T p hp E) T = companionMatrix p := by
  let pb := AdjoinRoot.powerBasis' hp
  let e := quotientVectorEquiv T p E
  have hconj : (e.symm.toLinearMap ∘ₗ T) ∘ₗ e.toLinearMap =
      Algebra.lmul k (AdjoinRoot p) pb.gen := by
    apply LinearMap.ext
    intro x
    change e.symm (T (e x)) = AdjoinRoot.root p * x
    rw [quotientVectorEquiv_intertwines, e.symm_apply_apply]
  have hpoly : pb.minpolyGen = p := by
    rw [PowerBasis.minpolyGen_eq]
    change minpoly k (AdjoinRoot.root p) = p
    rw [AdjoinRoot.minpoly_root hp.ne_zero]
    simp [hp.leadingCoeff]
  change LinearMap.toMatrix (pb.basis.map e) (pb.basis.map e) T = _
  rw [LinearMap.toMatrix_map_left, LinearMap.toMatrix_map_right, hconj,
    ← Algebra.leftMulMatrix_apply, PowerBasis.leftMulMatrix]
  simpa only [hpoly] using (rfl :
    (fun i j : Fin p.natDegree => if (j : ℕ) + 1 = p.natDegree then -p.coeff i
      else if (i : ℕ) = (j : ℕ) + 1 then (1 : k) else 0) = companionMatrix p)

/-- An actual one-factor invariant-factor presentation, not a numerical certificate. -/
def HasOneInvariantFactor (T : Module.End k V) : Prop :=
  ∃ p : k[X], p.Monic ∧ 0 < p.natDegree ∧
    Nonempty (Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p})

/-- The factor in a monic one-factor presentation is forced to be the minimal polynomial. -/
theorem factor_eq_minpoly [FiniteDimensional k V] (T : Module.End k V)
    (p : k[X]) (hp : p.Monic)
    (E : Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {p}) : p = minpoly k T := by
  have hs : Ideal.span {minpoly k T} = Ideal.span {p} :=
    (Polynomial.span_minpoly_eq_annihilator k T).trans
      (E.annihilator_eq.trans Ideal.annihilator_quotient)
  exact Polynomial.dvd_antisymm hp (minpoly.monic (LinearMap.isIntegral T))
    (Ideal.span_singleton_le_span_singleton.mp hs.le)
    (Ideal.span_singleton_le_span_singleton.mp hs.ge)

/-- One invariant factor is equivalent to cyclicity of the actual operator. -/
theorem hasCyclicVector_iff_oneInvariantFactor [FiniteDimensional k V] [Nontrivial V]
    (T : Module.End k V) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T ↔ HasOneInvariantFactor T := by
  constructor
  · intro h
    refine ⟨minpoly k T, minpoly.monic (LinearMap.isIntegral T), ?_,
      (hasCyclicVector_iff_minpoly_quotient_presentation T).mp h⟩
    rw [(hasCyclicVector_iff_minpoly_eq_charpoly T).mp h, LinearMap.charpoly_natDegree]
    exact Module.finrank_pos
  · rintro ⟨p, hp, _hd, ⟨E⟩⟩
    apply (hasCyclicVector_iff_minpoly_quotient_presentation T).mpr
    rwa [factor_eq_minpoly T p hp E] at E

/-- A cyclic operator admits a genuine companion-matrix basis for its minimal polynomial. -/
theorem exists_companion_basis_of_cyclic [FiniteDimensional k V]
    (T : Module.End k V) (h : Komorebi.SingleOperatorGraph.HasCyclicVector T) :
    ∃ b : Module.Basis (Fin (minpoly k T).natDegree) k V,
      LinearMap.toMatrix b b T = companionMatrix (minpoly k T) := by
  obtain ⟨E⟩ := (hasCyclicVector_iff_minpoly_quotient_presentation T).mp h
  exact ⟨quotientCompanionBasis T _ (minpoly.monic (LinearMap.isIntegral T)) E,
    toMatrix_quotientCompanionBasis T _ (minpoly.monic (LinearMap.isIntegral T)) E⟩

end Komorebi.PaperICompletion6.OneInvariantFactor
