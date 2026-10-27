import Mathlib.LinearAlgebra.Quotient.Pi
import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.RingTheory.Ideal.Norm.AbsNorm
import Mathlib.RingTheory.Ideal.Operations

/-! Cardinality of ideal quotients of an actual finite free module.
This supplies the numerical lattice leaf once its corner basis is constructed;
it does not assert that an arbitrary additive lattice has that basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FreeLatticeCard110

variable {R M ι : Type*} [CommRing R] [AddCommGroup M] [Module R M]
  [Fintype ι] [DecidableEq ι]

theorem ideal_smul_top_pi (I : Ideal R) :
    I • (⊤ : Submodule R (ι → R)) = Submodule.pi Set.univ (fun _ : ι => I) := by
  apply le_antisymm
  · apply Submodule.smul_le.mpr
    intro r hr f _
    apply Submodule.mem_pi.mpr
    intro i _
    exact I.mul_mem_right (f i) hr
  · intro f hf
    have hfi : ∀ i, f i ∈ I := fun i => Submodule.mem_pi.mp hf i (Set.mem_univ i)
    have he : f = ∑ i : ι, f i • Pi.single i (1 : R) := by
      ext j
      simp [Pi.single_apply, mul_ite]
    rw [he]
    apply Submodule.sum_mem
    intro i _
    exact Submodule.smul_mem_smul (hfi i) Submodule.mem_top

def quotientEquiv (b : Module.Basis ι R M) (I : Ideal R) :
    (M ⧸ (I • (⊤ : Submodule R M))) ≃ₗ[R] (ι → R ⧸ I) :=
  (Submodule.Quotient.equiv _ _ b.equivFun (by
    rw [Submodule.map_smul'', Submodule.map_top,
      LinearMap.range_eq_top.mpr b.equivFun.surjective, ideal_smul_top_pi])).trans
    (Submodule.quotientPi (fun _ : ι => I))

theorem card_quotient (b : Module.Basis ι R M) (I : Ideal R) :
    Nat.card (M ⧸ (I • (⊤ : Submodule R M))) = Nat.card (R ⧸ I) ^ Fintype.card ι := by
  rw [Nat.card_congr (quotientEquiv b I).toEquiv, Nat.card_fun]
  simp only [Nat.card_eq_fintype_card]

theorem card_quotient_prime_pow [IsDedekindDomain R] (b : Module.Basis ι R M)
    (I : Ideal R) [I.IsPrime] (hI : I ≠ ⊥) (a : ℕ) :
    Nat.card (M ⧸ ((I ^ a) • (⊤ : Submodule R M))) =
      Nat.card (R ⧸ I) ^ (a * Fintype.card ι) := by
  rw [card_quotient b (I ^ a)]
  change (Submodule.cardQuot (I ^ a)) ^ Fintype.card ι = _
  rw [cardQuot_pow_of_prime hI, ← pow_mul]
  rfl

end PaperXI.FreeLatticeCard110
