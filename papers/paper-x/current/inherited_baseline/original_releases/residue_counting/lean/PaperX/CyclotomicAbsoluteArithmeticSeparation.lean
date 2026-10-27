import PaperX.CyclotomicAbsoluteSeparation
import PaperX.AbsoluteIntegralFrobenius
import PaperX.CyclotomicIntegralFrobenius

/-! Arithmetic separators with actual absolute-Galois Frobenius witnesses.
The common cyclotomic factorization remains explicit. Prime ideals and
decomposition elements belong to the integral closure of Z in Qbar. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicAbsoluteArithmeticSeparation
open PaperX.CyclotomicPrimeCoverage PaperX.CyclotomicAbsoluteSamples
open PaperX.CompatibleSystemRigidity PaperX.FiniteSeparation
open PaperX.AbsoluteIntegralFrobenius
open scoped Pointwise

variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]

variable {Λ I E : Type*} [Field E] [Fintype I] [DecidableEq I]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) Gal(L/ℚ) (W l i))
variable [∀ l i, Representation.IsIrreducible ((ρ l i).comp (restrictionMap n L))]
variable (emb : (l : Λ) → E →+* K l) (t : I → PermittedPrime n ∅ → E)
variable (good : Λ → PermittedPrime n ∅ → Prop)
variable (hgood : ∀ l, Set.Finite {p | ¬ good l p})
variable (compat : ∀ l i p, good l p →
  Representation.character ((ρ l i).comp (restrictionMap n L)) (liftSample n L p) =
    emb l (t i p))
variable (hne : ∀ i j,
  MemberwiseEquiv (fun l i => (ρ l i).comp (restrictionMap n L)) i j → i = j)

include hgood compat hne in
/-- Actual arithmetic Frobenius witnesses realize a common invertible trace
matrix for absolute-Galois systems factoring through the fixed cyclotomic field.
Neither absolute Frobenius witnesses nor quotient coverage are assumed. -/
theorem finite_arithmetic_system_separator (l₀ : Λ) (forbidden : Finset ℕ) :
    ∃ (v : I → PermittedPrime n ∅)
      (Q : I → Ideal IntegralClosure) (γ : I → GQ),
      Function.Injective (fun i => (v i).val) ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, (v i).val ∉ forbidden) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      (∀ j, (Q j).IsMaximal ∧ (Q j).LiesOver (Ideal.span {((v j).val : ℤ)}) ∧
        γ j ∈ MulAction.stabilizer GQ (Q j) ∧
        ∀ x : IntegralClosure, Ideal.Quotient.mk (Q j) (γ j • x) =
          (Ideal.Quotient.mk (Q j) x) ^ (v j).val) ∧
      (∀ j, restrictionMap n L (γ j) = primeSample n L ∅ (v j)) ∧
      (∀ l i j (δ : GQ), δ ∈ (Q j).inertia GQ →
        ((ρ l i).comp (restrictionMap n L)) δ = 1) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          Representation.character ((ρ l i).comp (restrictionMap n L)) (γ j) := by
  classical
  obtain ⟨v, hv, hg, hb, hd, hdl, ht⟩ :=
    PaperX.CyclotomicAbsoluteSeparation.finite_absolute_system_separator
      n L ρ emb t good hgood compat hne l₀ forbidden
  have witnesses : ∀ j : I, ∃ Q : Ideal IntegralClosure,
      Q.IsMaximal ∧ Q.LiesOver (Ideal.span {((v j).val : ℤ)}) ∧
      ∃ σ : MulAction.stabilizer GQ Q,
        ∀ x : IntegralClosure, Ideal.Quotient.mk Q (σ.val • x) =
          (Ideal.Quotient.mk Q x) ^ (v j).val := by
    intro j
    let : Fact (v j).val.Prime := ⟨(v j).property.1⟩
    exact exists_frobenius (v j).val
  choose Q hQ hQp σ hσ using witnesses
  let γ : I → GQ := fun j => (σ j).val
  have hr : ∀ j, restrictionMap n L (γ j) = primeSample n L ∅ (v j) := by
    intro j
    let : (Q j).IsMaximal := hQ j
    let : (Q j).LiesOver (Ideal.span {((v j).val : ℤ)}) := hQp j
    let : Fact (v j).val.Prime := ⟨(v j).property.1⟩
    exact PaperX.CyclotomicIntegralFrobenius.restriction_eq_primePower_of_residue
      n L (Q j) (v j).val (v j).property.2.1 (γ j) (hσ j)
  refine ⟨v, Q, γ, hv, hg, hb, hd, hdl, ?_, hr, ?_, ?_⟩
  · intro j
    exact ⟨hQ j, hQp j, (σ j).property, hσ j⟩
  · intro l i j δ hδ
    let : (Q j).IsMaximal := hQ j
    let : (Q j).LiesOver (Ideal.span {((v j).val : ℤ)}) := hQp j
    let : Fact (v j).val.Prime := ⟨(v j).property.1⟩
    exact PaperX.CyclotomicIntegralFrobenius.pullback_trivial_on_inertia
      n L (Q j) (v j).val (v j).property.2.1 (ρ l i) δ hδ
  · intro l j i hp
    exact ht l j i (γ j) (hr j) hp

end PaperX.CyclotomicAbsoluteArithmeticSeparation
