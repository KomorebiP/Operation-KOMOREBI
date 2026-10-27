import PaperXII.DyadicProjectors
import PaperXII.ResidualAugmentation
import Mathlib.RingTheory.Ideal.Quotient.Operations

set_option autoImplicit false

/-! Paper XII, Proposition 11.1: the actual residual dual-number algebra. -/
namespace PaperXII.DyadicProjectors.Residual

abbrev k := ZMod 2

noncomputable def squareIdeal : Ideal (Polynomial k) :=
  Ideal.span {Polynomial.X ^ 2}

abbrev Dual := Polynomial k ⧸ squareIdeal

noncomputable def X : Dual := Ideal.Quotient.mk squareIdeal Polynomial.X

theorem X_sq : X * X = 0 := by
  change Ideal.Quotient.mk squareIdeal Polynomial.X *
    Ideal.Quotient.mk squareIdeal Polynomial.X = 0
  rw [← map_mul, ← pow_two, Ideal.Quotient.eq_zero_iff_mem]
  exact Ideal.subset_span (Set.mem_singleton _)

theorem one_add_X_sq : (1 + X) * (1 + X) = 1 := by
  have htwo : (2 : Dual) = 0 := by
    have hz : (2 : k) = 0 := by decide
    calc
      (2 : Dual) = (algebraMap k Dual) (2 : k) := (map_ofNat _ _).symm
      _ = (algebraMap k Dual) 0 := congrArg _ hz
      _ = 0 := map_zero _
  calc
    (1 + X) * (1 + X) = 1 + 2 * X + X * X := by ring
    _ = 1 := by rw [htwo, X_sq]; ring

noncomputable def cyclicMap : G →* Dual where
  toFun h := if h = 1 then 1 else 1 + X
  map_one' := by simp
  map_mul' a b := by
    rcases group_cases a with rfl | rfl <;> rcases group_cases b with rfl | rfl <;>
      simp [g_mul_g, g_ne_one, one_add_X_sq]

/-- The group generator is sent to 1+X. -/
noncomputable def toDual : MonoidAlgebra k G →ₐ[k] Dual :=
  MonoidAlgebra.lift k Dual G cyclicMap

theorem generator_toDual : toDual (generator (K := k)) = 1 + X := by
  simp [toDual, generator, cyclicMap, g_ne_one]

theorem augmentation_generator_sq :
    (generator (K := k) - 1) * (generator - 1) = 0 := by
  have hgen : generator (K := k) * generator = 1 := by
    simp [generator, MonoidAlgebra.single_mul_single, g_mul_g, MonoidAlgebra.one_def]
  have htwo : (2 : MonoidAlgebra k G) = 0 := by
    have hz : (2 : k) = 0 := by decide
    calc
      (2 : MonoidAlgebra k G) = (algebraMap k (MonoidAlgebra k G)) (2 : k) :=
        (map_ofNat _ _).symm
      _ = (algebraMap k (MonoidAlgebra k G)) 0 := congrArg _ hz
      _ = 0 := map_zero _
  calc
    (generator (K := k) - 1) * (generator - 1) =
      generator * generator - 2 * generator + 1 := by ring
    _ = 0 := by rw [hgen, htwo]; simpa only [zero_mul, sub_zero, one_add_one_eq_two] using htwo

noncomputable def fromDual : Dual →ₐ[k] MonoidAlgebra k G :=
  Ideal.Quotient.liftₐ squareIdeal (Polynomial.aeval (generator - 1)) (by
    change squareIdeal ≤ RingHom.ker (Polynomial.aeval (generator - 1)).toRingHom
    apply Ideal.span_le.mpr
    rintro _ rfl
    change (Polynomial.aeval (generator (K := k) - 1)) (Polynomial.X ^ 2) = 0
    simp [pow_two, augmentation_generator_sq])

theorem X_fromDual : fromDual X = generator - 1 := by
  change (Polynomial.aeval (generator (K := k) - 1)) Polynomial.X = _
  exact Polynomial.aeval_X _

theorem fromDual_comp_toDual : fromDual.comp toDual = AlgHom.id k (MonoidAlgebra k G) := by
  apply MonoidAlgebra.algHom_ext
  · intro h
    rcases group_cases h with rfl | rfl
    · simp [toDual, cyclicMap, MonoidAlgebra.one_def]
    · change fromDual (toDual (generator (K := k))) = generator
      rw [generator_toDual, map_add, map_one, X_fromDual]
      ring
  · exact Subsingleton.elim _ _

theorem toDual_comp_fromDual : toDual.comp fromDual = AlgHom.id k Dual := by
  apply Ideal.Quotient.algHom_ext
  apply Polynomial.algHom_ext
  change toDual (fromDual X) = X
  rw [X_fromDual, map_sub, map_one, generator_toDual]
  ring

/-- The residual algebra is exactly the dual-number quotient, via X=g−1. -/
noncomputable def dualNumberEquiv : MonoidAlgebra k G ≃ₐ[k] Dual :=
  AlgEquiv.ofAlgHom toDual fromDual toDual_comp_fromDual fromDual_comp_toDual

theorem dualNumberEquiv_generator : dualNumberEquiv (generator (K := k) - 1) = X := by
  change toDual (generator (K := k) - 1) = X
  rw [map_sub, map_one, generator_toDual]
  ring

theorem cyclic_is_two_group : IsPGroup 2 G := by
  intro h
  refine ⟨1, ?_⟩
  rcases group_cases h with rfl | rfl <;> simp [pow_two, g_mul_g]

theorem groupAlgebra_isLocalRing : IsLocalRing (MonoidAlgebra k G) :=
  PaperXII.ResidualAugmentation.isLocalRing (k := k) cyclic_is_two_group

theorem groupAlgebra_idempotent (e : MonoidAlgebra k G) (he : e * e = e) :
    e = 0 ∨ e = 1 :=
  PaperXII.ResidualAugmentation.idempotent_eq_zero_or_one cyclic_is_two_group e he

theorem dual_isLocalRing : IsLocalRing Dual := by
  let := groupAlgebra_isLocalRing
  exact dualNumberEquiv.toRingEquiv.isLocalRing

theorem dual_idempotent (e : Dual) (he : e * e = e) : e = 0 ∨ e = 1 := by
  let := dual_isLocalRing
  exact PaperXII.LocalIdempotents.eq_zero_or_one e he

end PaperXII.DyadicProjectors.Residual
