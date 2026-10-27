import PaperX.AbsoluteGaloisRestriction
import Mathlib.FieldTheory.Galois.IsGaloisGroup
import Mathlib.FieldTheory.Galois.Profinite
import Mathlib.RingTheory.Invariant.Profinite
import Mathlib.RingTheory.Localization.Integral
import Mathlib.FieldTheory.Perfect
import Mathlib.Topology.Algebra.MulAction
import Mathlib.NumberTheory.NumberField.Basic
import Mathlib.RingTheory.Ideal.Int

/-! Actual arithmetic Frobenius elements in decomposition groups of the algebraic
integers in the fixed algebraic closure of Q. The prime ideal and the absolute
Galois automorphism are constructed. No Frobenius lift or residue-surjectivity
hypothesis is supplied. The residue convention is the arithmetic p-power map. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AbsoluteIntegralFrobenius
open scoped Pointwise

abbrev Qbar := AlgebraicClosure ℚ
abbrev GQ := Gal(Qbar/ℚ)
abbrev IntegralClosure := integralClosure ℤ Qbar

instance algebraic_int : Algebra.IsAlgebraic ℤ Qbar :=
  IsFractionRing.comap_isAlgebraic_iff.mpr (inferInstance : Algebra.IsAlgebraic ℚ Qbar)

instance fractionRing : IsFractionRing IntegralClosure Qbar :=
  integralClosure.isFractionRing_of_algebraic (A := ℤ)
    (fun _ hx => (FaithfulSMul.algebraMap_injective ℤ Qbar) (hx.trans (map_zero _).symm))

instance galoisGroup_integral : IsGaloisGroup GQ ℤ IntegralClosure :=
  IsGaloisGroup.of_isFractionRing GQ ℤ IntegralClosure ℚ Qbar

local instance : TopologicalSpace IntegralClosure := ⊥
local instance : DiscreteTopology IntegralClosure := ⟨rfl⟩

/-- The actual absolute Galois action on the algebraic integers is continuous
when the algebraic integers carry the discrete topology. -/
theorem continuous_integral_action : ContinuousSMul GQ IntegralClosure := by
  apply continuousSMul_iff_stabilizer_isOpen.mpr
  intro x
  convert stabilizer_isOpen_of_isIntegral (K := ℚ) (x : Qbar) using 1
  ext σ
  simp only [SetLike.mem_coe, MulAction.mem_stabilizer_iff, Subtype.ext_iff]
  rfl

attribute [local instance] continuous_integral_action

variable (p : ℕ) [hp : Fact p.Prime]
  (Q : Ideal IntegralClosure) [Q.IsMaximal] [Q.LiesOver (Ideal.span {(p : ℤ)})]

attribute [local instance] Ideal.Quotient.field

/-- A prime ideal of the algebraic integers above p has residue characteristic p. -/
theorem residue_charP : CharP (IntegralClosure ⧸ Q) p := by
  apply (CharP.charP_iff_prime_eq_zero hp.out).mpr
  have hm : (p : IntegralClosure) ∈ Q := by
    change algebraMap ℤ IntegralClosure (p : ℤ) ∈ Q
    rw [← Ideal.mem_under, ← Ideal.over_def Q (Ideal.span {(p : ℤ)})]
    exact Ideal.subset_span (Set.mem_singleton _)
  simpa only [map_natCast] using (Ideal.Quotient.eq_zero_iff_mem.mpr hm)


/-- The p-power map on this actual residue field is bijective. Roots in Qbar
remain integral because their p-th powers are integral. -/
theorem residue_perfect : PerfectRing (IntegralClosure ⧸ Q) p := by
  let : CharP (IntegralClosure ⧸ Q) p := residue_charP p Q
  refine ⟨⟨frobenius_inj (IntegralClosure ⧸ Q) p, ?_⟩⟩
  intro x
  obtain ⟨b, rfl⟩ := Ideal.Quotient.mk_surjective x
  obtain ⟨y, hy⟩ := IsAlgClosed.exists_pow_nat_eq (b : Qbar) hp.out.pos
  have hi : IsIntegral ℤ y := IsIntegral.of_pow hp.out.pos (by rw [hy]; exact b.property)
  let c : IntegralClosure := ⟨y, (mem_integralClosure_iff ℤ Qbar).mpr hi⟩
  refine ⟨Ideal.Quotient.mk Q c, ?_⟩
  change Ideal.Quotient.mk Q c ^ p = Ideal.Quotient.mk Q b
  rw [← map_pow]
  apply congrArg (Ideal.Quotient.mk Q)
  exact Subtype.ext hy


/-- Arithmetic Frobenius as an automorphism of the actual residue extension. -/
def residueFrobenius :
    (IntegralClosure ⧸ Q) ≃ₐ[ℤ ⧸ Ideal.span {(p : ℤ)}] (IntegralClosure ⧸ Q) := by
  let : CharP (IntegralClosure ⧸ Q) p := residue_charP p Q
  let : PerfectRing (IntegralClosure ⧸ Q) p := residue_perfect p Q
  exact
    { __ := frobeniusEquiv (IntegralClosure ⧸ Q) p
      commutes' := by
        intro x
        obtain ⟨z, rfl⟩ := Ideal.Quotient.mk_surjective x
        change frobeniusEquiv (IntegralClosure ⧸ Q) p (z : IntegralClosure ⧸ Q) =
          (z : IntegralClosure ⧸ Q)
        exact map_intCast (frobeniusEquiv (IntegralClosure ⧸ Q) p) z }

/-- The chosen residue automorphism is exactly the p-power map. -/
theorem residueFrobenius_apply (x : IntegralClosure ⧸ Q) :
    residueFrobenius p Q x = x ^ p := rfl

/-- Every actual prime ideal above p admits an arithmetic Frobenius lift in its
actual absolute Galois decomposition group. -/
theorem exists_frobenius_at :
    ∃ σ : MulAction.stabilizer GQ Q, ∀ x : IntegralClosure,
      Ideal.Quotient.mk Q (σ.val • x) = (Ideal.Quotient.mk Q x) ^ p := by
  obtain ⟨σ, hσ⟩ := Ideal.Quotient.stabilizerHom_surjective_of_profinite
    (G := GQ) (Ideal.span {(p : ℤ)}) Q (residueFrobenius p Q)
  refine ⟨σ, fun x => ?_⟩
  exact DFunLike.congr_fun hσ (Ideal.Quotient.mk Q x)

/-- For each rational prime, an actual maximal ideal of the algebraic integers
and an actual absolute Frobenius element above it exist. -/
theorem exists_frobenius :
    ∃ Q : Ideal IntegralClosure, Q.IsMaximal ∧ Q.LiesOver (Ideal.span {(p : ℤ)}) ∧
      ∃ σ : MulAction.stabilizer GQ Q, ∀ x : IntegralClosure,
        Ideal.Quotient.mk Q (σ.val • x) = (Ideal.Quotient.mk Q x) ^ p := by
  let : (Ideal.span {(p : ℤ)}).IsMaximal := Int.ideal_span_isMaximal_of_prime p
  obtain ⟨Q, hQ, hQP⟩ := Ideal.exists_maximal_ideal_liesOver_of_isIntegral
    (S := IntegralClosure) (Ideal.span {(p : ℤ)})
  let : Q.IsMaximal := hQ
  let : Q.LiesOver (Ideal.span {(p : ℤ)}) := hQP
  exact ⟨Q, hQ, hQP, exists_frobenius_at p Q⟩

end PaperX.AbsoluteIntegralFrobenius
