import ReleaseGluingSmith

/-!
# Smith data supplied as an actual module equivalence

These endpoints accept any cyclic-module decomposition of the actual
gluing quotient, as in the manuscript.  Inclusion bases are one source
of such an equivalence, not an additional premise of these statements.
-/

set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {G : Type v} {I : Type w}
variable [CommRing O] [IsDomain O] [AddCommGroup G] [Module O G]
variable [Fintype I]

/-- An arbitrary actual cyclic decomposition determines all uniform annihilators. -/
omit [Fintype I] in
theorem cyclicProduct_annihilated_iff_weights_le
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ) (s : ℕ) :
    (∀ z : ∀ i, O ⧸ Ideal.span {pi ^ a i}, (pi ^ s) • z = 0) ↔
      ∀ i, a i ≤ s := by
  constructor
  · intro h i
    have hi := congrFun (h (fun j => (Ideal.span {pi ^ a j}).mkQ 1)) i
    change (pi ^ s) • (Ideal.span {pi ^ a i}).mkQ 1 = 0 at hi
    rw [← map_smul, smul_eq_mul, mul_one, Submodule.mkQ_apply,
      Submodule.Quotient.mk_eq_zero, Ideal.mem_span_singleton] at hi
    exact (pow_dvd_pow_iff hpi hunit).mp hi
  · intro h z
    ext i
    obtain ⟨r, hr⟩ := (Ideal.span {pi ^ a i}).mkQ_surjective (z i)
    change (pi ^ s) • z i = 0
    rw [← hr, ← map_smul, smul_eq_mul, Submodule.mkQ_apply,
      Submodule.Quotient.mk_eq_zero, Ideal.mem_span_singleton]
    exact dvd_mul_of_dvd_left ((pow_dvd_pow_iff hpi hunit).mpr (h i)) r

/-- Transport of the exact annihilator threshold through any actual module equivalence. -/
theorem annihilated_iff_smith_max_of_equiv
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (e : G ≃ₗ[O] (∀ i, O ⧸ Ideal.span {pi ^ a i})) (s : ℕ) :
    (∀ z : G, (pi ^ s) • z = 0) ↔ Finset.univ.sup a ≤ s := by
  have htransport : (∀ z : G, (pi ^ s) • z = 0) ↔
      ∀ z : ∀ i, O ⧸ Ideal.span {pi ^ a i}, (pi ^ s) • z = 0 := by
    constructor
    · intro h z
      obtain ⟨x, rfl⟩ := e.surjective z
      rw [← map_smul, h x, map_zero]
    · intro h z
      apply e.injective
      rw [map_smul, h (e z), map_zero]
  rw [htransport, cyclicProduct_annihilated_iff_weights_le pi hpi hunit a s]
  simp only [Finset.sup_le_iff, Finset.mem_univ, true_implies]

/-- The length formula only needs the supplied cyclic decomposition. -/
theorem length_eq_smith_sum_of_equiv [IsDiscreteValuationRing O]
    (pi : O) (hpi : Irreducible pi) (a : I → ℕ)
    (e : G ≃ₗ[O] (∀ i, O ⧸ Ideal.span {pi ^ a i})) :
    Module.length O G = ∑ i, (a i : ℕ∞) := by
  rw [e.length_eq, Module.length_pi_of_fintype]
  apply Finset.sum_congr rfl
  intro i _hi
  have heq : Ideal.span {pi ^ a i} = IsLocalRing.maximalIdeal O ^ a i := by
    rw [hpi.maximalIdeal_eq, Ideal.span_singleton_pow]
  rw [(Submodule.quotEquivOfEq _ _ heq).length_eq]
  exact IsDiscreteValuationRing.length_quotient_pow_maximalIdeal (R := O) (a i)

/-- The manuscript's maximum formula for any given Smith decomposition of G. -/
theorem globalWeight_eq_smith_max_of_equiv
    {V : Type*} [AddCommGroup V] [Module O V]
    {J : Type*} [Fintype J] (P : Projectors O V J) (Λ : Submodule O V)
    (pi : O) (hpi : pi ≠ 0) (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (e : GluingModule P Λ ≃ₗ[O] (∀ i, O ⧸ Ideal.span {pi ^ a i}))
    (finite : ∀ j, ∃ s, ClearsPacket P Λ pi j s) :
    globalWeight P Λ pi finite = Finset.univ.sup a := by
  apply le_antisymm
  · apply (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mp
    exact (annihilated_iff_smith_max_of_equiv pi hpi hunit a e _).mpr le_rfl
  · apply (annihilated_iff_smith_max_of_equiv pi hpi hunit a e _).mp
    exact (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mpr le_rfl

end Komorebi.PaperII.ReleaseGluing
