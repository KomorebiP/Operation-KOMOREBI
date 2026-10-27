import PaperX.AuxiliaryCyclotomicDisjoint
import PaperX.AuxiliaryCyclotomicDegree

/-! Existence of the cyclic cyclotomic auxiliary field used in field crossing.
No auxiliary field or disjointness witness is assumed in the existence theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AuxiliaryCyclotomicExistence
open IntermediateField AuxiliaryCyclotomicDisjoint AuxiliaryCyclotomicDegree

variable (M : Type*) [Field M] [CharZero M] [IsAlgClosed M]
  [Algebra.IsAlgebraic ℚ M]

/-- For every number field L in an algebraic closure and every positive degree n,
there is a cyclic degree-n field A contained in a prime cyclotomic field and
linearly disjoint from L. Its prime conductor can avoid any supplied finite set
and exceed any supplied bound. -/
theorem exists_cyclic_cyclotomic_disjoint (L : IntermediateField ℚ M) [NumberField L]
    (n : ℕ) [NeZero n] (forbidden : Finset ℕ) (B : ℕ) :
    ∃ p : Nat.Primes, ∃ A : IntermediateField ℚ M,
      B < (p : ℕ) ∧ (p : ℕ) ∉ forbidden ∧
      A ≤ primeCyclotomicPart M p ∧ Module.finrank ℚ A = n ∧
      IsGalois ℚ A ∧ IsCyclic Gal(A/ℚ) ∧ A.LinearDisjoint L := by
  obtain ⟨p, hpB, hpnot, hres, hdis⟩ := exists_prime_conductor M L n forbidden B
  have : Fact (p : ℕ).Prime := ⟨p.property⟩
  have : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  have : IsCyclotomicExtension {(p : ℕ)} ℚ (primeCyclotomicPart M p) :=
    primeCyclotomicPart_isCyclotomic M p
  have hn : n ∣ (p : ℕ) - 1 := by
    apply (ZMod.natCast_eq_zero_iff _ n).mp
    rw [Nat.cast_sub p.property.one_le, hres, Nat.cast_one, sub_self]
  obtain ⟨A, hdegree, hgal, hcyc⟩ := exists_prime_cyclotomic_subfield
    (p : ℕ) (primeCyclotomicPart M p) n hn
  have hgal' : IsGalois ℚ (IntermediateField.lift A) := IsGalois.of_algEquiv (IntermediateField.liftAlgEquiv A)
  have hcyc' : IsCyclic Gal((IntermediateField.lift A)/ℚ) :=
    isCyclic_of_surjective (IntermediateField.liftAlgEquiv A).autCongr
      (IntermediateField.liftAlgEquiv A).autCongr.surjective
  refine ⟨p, IntermediateField.lift A, hpB, hpnot, (IntermediateField.lift_le A), ?_, hgal', hcyc',
    hdis.of_le_left (IntermediateField.lift_le A)⟩
  exact (IntermediateField.liftAlgEquiv A).toLinearEquiv.finrank_eq.symm.trans hdegree

/-- Specialization to the actual algebraic closure of Q. -/
theorem exists_in_algebraicClosure
    (L : IntermediateField ℚ (AlgebraicClosure ℚ)) [NumberField L]
    (n : ℕ) [NeZero n] :
    ∃ p : Nat.Primes, ∃ A : IntermediateField ℚ (AlgebraicClosure ℚ),
      A ≤ primeCyclotomicPart (AlgebraicClosure ℚ) p ∧ Module.finrank ℚ A = n ∧
      IsGalois ℚ A ∧ IsCyclic Gal(A/ℚ) ∧ A.LinearDisjoint L := by
  obtain ⟨p, A, _, _, hle, hdeg, hgal, hcyc, hdis⟩ :=
    exists_cyclic_cyclotomic_disjoint (AlgebraicClosure ℚ) L n ∅ 0
  exact ⟨p, A, hle, hdeg, hgal, hcyc, hdis⟩

end PaperX.AuxiliaryCyclotomicExistence
