import ReleaseGluing
import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.Algebra.GroupWithZero.Divisibility

/-!
# Smith inclusion data and exact quotient exponent

The input is an actual basis of a submodule S and an actual basis of W,
related by the diagonal inclusion equation.  No quotient isomorphism or
annihilator formula is assumed.  This is the precise input supplied by a
Smith normal form of a full-rank lattice inclusion.  The proof works over
any domain with a nonzero nonunit pi; a DVR uniformizer satisfies these
conditions.  Zero exponents and empty bases are included.
-/

set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {W : Type v} {I : Type w}
variable [CommRing O] [IsDomain O] [AddCommGroup W] [Module O W]
variable [Fintype I] [DecidableEq I]

theorem mem_submodule_iff_smith_coordinates
    (S : Submodule O W) (b : Module.Basis I O W) (c : Module.Basis I O S)
    (pi : O) (a : I → ℕ)
    (hdiag : ∀ i, (c i : W) = (pi ^ a i) • b i) (x : W) :
    x ∈ S ↔ ∀ i, pi ^ a i ∣ b.repr x i := by
  constructor
  · intro hx i
    let y : S := ⟨x, hx⟩
    have hsum : (∑ j, c.repr y j • (c j : W)) = x := by
      simpa only [Submodule.coe_sum, Submodule.coe_smul] using
        congrArg (fun z : S => (z : W)) (c.sum_repr y)
    refine ⟨c.repr y i, ?_⟩
    rw [← hsum]
    simp [hdiag, mul_comm, Finsupp.single_apply]
  · intro hx
    rw [← b.sum_repr x]
    apply S.sum_mem
    intro i _hi
    obtain ⟨k, hk⟩ := hx i
    rw [hk, mul_comm, mul_smul, ← hdiag i]
    exact S.smul_mem k (c i).property

theorem quotient_annihilated_iff_smith_weights_le
    (S : Submodule O W) (b : Module.Basis I O W) (c : Module.Basis I O S)
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (hdiag : ∀ i, (c i : W) = (pi ^ a i) • b i) (s : ℕ) :
    (∀ z : W ⧸ S, (pi ^ s) • z = 0) ↔ ∀ i, a i ≤ s := by
  constructor
  · intro h i
    have hk := h (S.mkQ (b i))
    rw [← map_smul, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero] at hk
    have hdvd := (mem_submodule_iff_smith_coordinates S b c pi a hdiag _).mp hk i
    simp only [map_smul, Finsupp.smul_apply, b.repr_self_apply, ite_true,
      smul_eq_mul, mul_one] at hdvd
    exact (pow_dvd_pow_iff hpi hunit).mp hdvd
  · intro h z
    obtain ⟨x, rfl⟩ := S.mkQ_surjective z
    rw [← map_smul, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
    apply (mem_submodule_iff_smith_coordinates S b c pi a hdiag _).mpr
    intro i
    simp only [map_smul, Finsupp.smul_apply, smul_eq_mul]
    exact dvd_mul_of_dvd_left ((pow_dvd_pow_iff hpi hunit).mpr (h i)) _

theorem quotient_annihilated_iff_smith_max_le
    (S : Submodule O W) (b : Module.Basis I O W) (c : Module.Basis I O S)
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (hdiag : ∀ i, (c i : W) = (pi ^ a i) • b i) (s : ℕ) :
    (∀ z : W ⧸ S, (pi ^ s) • z = 0) ↔ Finset.univ.sup a ≤ s := by
  rw [quotient_annihilated_iff_smith_weights_le S b c pi hpi hunit a hdiag]
  simp only [Finset.sup_le_iff, Finset.mem_univ, true_implies]

/-- Given a Smith basis of the actual split-lattice inclusion, its maximum weight
is exactly the maximum of the least projector denominator weights. -/
theorem globalWeight_eq_smith_max
    {V : Type*} [AddCommGroup V] [Module O V]
    {J : Type*} [Fintype J] (P : Projectors O V J) (Λ : Submodule O V)
    (b : Module.Basis I O Λ) (c : Module.Basis I O (splitInside P Λ))
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (hdiag : ∀ i, (c i : Λ) = (pi ^ a i) • b i)
    (finite : ∀ j, ∃ s, ClearsPacket P Λ pi j s) :
    globalWeight P Λ pi finite = Finset.univ.sup a := by
  apply le_antisymm
  · apply (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mp
    exact (quotient_annihilated_iff_smith_max_le
      (splitInside P Λ) b c pi hpi hunit a hdiag _).mpr le_rfl
  · apply (quotient_annihilated_iff_smith_max_le
      (splitInside P Λ) b c pi hpi hunit a hdiag _).mp
    exact (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mpr le_rfl

end Komorebi.PaperII.ReleaseGluing
