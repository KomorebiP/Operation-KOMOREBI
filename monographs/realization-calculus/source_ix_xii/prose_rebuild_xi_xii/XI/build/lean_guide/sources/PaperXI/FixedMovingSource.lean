import PaperXI.FixedMoving
import PaperXI.FiniteFieldAverage
import PaperXI.OddPhase
import Mathlib.RingTheory.Finiteness.Cardinality

/-! The source fixed/moving theorem, with the decomposition and restricted
invertibility derived from the actual finite order prime to the characteristic. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FixedMoving

variable {F V : Type*} [Field F] [AddCommGroup V] [Module F V]

/-- Finite order with invertible order scalar gives the actual complementary subspaces. -/
theorem isCompl_of_period (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) (hm : (m : F) ≠ 0) :
    IsCompl (fixed g) (moving g) := FiniteFieldAverage.isCompl g m hpow hm

/-- The constructed decomposition equivalence has the literal sum as its forward map. -/
def decomposition (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) (hm : (m : F) ≠ 0) :
    (fixed g × moving g) ≃ₗ[F] V := FiniteFieldAverage.decomposition g m hpow hm

@[simp] theorem decomposition_apply (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (v : fixed g × moving g) :
    decomposition g m hpow hm v = (v.1 : V) + (v.2 : V) := rfl

/-- The fixed projection is the actual finite average. -/
theorem decomposition_fixed (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (v : V) :
    (((decomposition g m hpow hm).symm v).1 : V) = FiniteFieldAverage.average g m v :=
  FiniteFieldAverage.decomposition_symm_fst g m hpow hm v

/-- The moving projection is the remainder after the actual finite average. -/
theorem decomposition_moving (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (v : V) :
    (((decomposition g m hpow hm).symm v).2 : V) = v - FiniteFieldAverage.average g m v :=
  FiniteFieldAverage.decomposition_symm_snd g m hpow hm v

theorem movingForm_nondegenerate (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (b : LinearMap.BilinForm F V) (hb : b.IsAlt)
    (hbn : b.Nondegenerate) (hg : ∀ x y, b (g x) (g y) = b x y) :
    (movingForm g b).Nondegenerate :=
  movingForm_nondegenerate_of_isCompl g b hb hbn hg (isCompl_of_period g m hpow hm)

theorem fixedForm_nondegenerate (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (b : LinearMap.BilinForm F V) (hb : b.IsAlt)
    (hbn : b.Nondegenerate) (hg : ∀ x y, b (g x) (g y) = b x y) :
    (fixedForm g b).Nondegenerate :=
  fixedForm_nondegenerate_of_isCompl g b hb hbn hg (isCompl_of_period g m hpow hm)

section PrimeField
variable {p : ℕ} [Fact p.Prime]
variable {U : Type*} [AddCommGroup U] [Module (ZMod p) U]

/-- Finite dimension over the actual finite field makes the automorphism order positive. -/
theorem source_order_pos [FiniteDimensional (ZMod p) U] (g : U ≃ₗ[ZMod p] U) : 0 < orderOf g := by
  let : Finite U := Module.finite_of_finite (ZMod p)
  let : Finite (U ≃ₗ[ZMod p] U) :=
    Finite.of_injective (fun e : U ≃ₗ[ZMod p] U => (e : U → U))
      (fun _ _ he => LinearEquiv.ext (congrFun he))
  exact orderOf_pos g

/-- The source prime-to-characteristic order condition supplies an invertible field scalar. -/
theorem source_order_ne_zero (g : U ≃ₗ[ZMod p] U) (horder : Nat.Coprime (orderOf g) p) :
    (orderOf g : ZMod p) ≠ 0 := by
  rw [Ne, ZMod.natCast_eq_zero_iff]
  exact (Fact.out : p.Prime).coprime_iff_not_dvd.mp horder.symm

theorem source_isCompl (g : U ≃ₗ[ZMod p] U) (horder : Nat.Coprime (orderOf g) p) :
    IsCompl (fixed g) (moving g) :=
  isCompl_of_period g (orderOf g) (pow_orderOf_eq_one g) (source_order_ne_zero g horder)

/-- The source decomposition, constructed from the actual order of the automorphism. -/
def sourceDecomposition (g : U ≃ₗ[ZMod p] U) (horder : Nat.Coprime (orderOf g) p) :
    (fixed g × moving g) ≃ₗ[ZMod p] U :=
  decomposition g (orderOf g) (pow_orderOf_eq_one g) (source_order_ne_zero g horder)

@[simp] theorem sourceDecomposition_apply (g : U ≃ₗ[ZMod p] U)
    (horder : Nat.Coprime (orderOf g) p) (v : fixed g × moving g) :
    sourceDecomposition g horder v = (v.1 : U) + (v.2 : U) := rfl

theorem source_moving_fixedPointFree (g : U ≃ₗ[ZMod p] U)
    (horder : Nat.Coprime (orderOf g) p) : OddPhase.FixedPointFree (movingAction g) :=
  movingAction_fixedPointFree_of_isCompl g (source_isCompl g horder)

/-- The source's actual restricted difference as a linear equivalence. -/
def sourceMovingDifference [FiniteDimensional (ZMod p) U] (g : U ≃ₗ[ZMod p] U) (horder : Nat.Coprime (orderOf g) p) :
    moving g ≃ₗ[ZMod p] moving g := movingDifferenceEquiv g (source_isCompl g horder)

@[simp] theorem sourceMovingDifference_apply [FiniteDimensional (ZMod p) U] (g : U ≃ₗ[ZMod p] U)
    (horder : Nat.Coprime (orderOf g) p) (v : moving g) :
    sourceMovingDifference g horder v = movingAction g v - v := rfl

/-- Source 12.6: the actual orthogonal decomposition, nondegenerate restrictions,
and invertibility of the actual moving difference all follow from the source hypotheses. -/
theorem source [FiniteDimensional (ZMod p) U] (g : U ≃ₗ[ZMod p] U) (horder : Nat.Coprime (orderOf g) p)
    (b : LinearMap.BilinForm (ZMod p) U) (hb : b.IsAlt) (hbn : b.Nondegenerate)
    (hg : ∀ x y, b (g x) (g y) = b x y) :
    0 < orderOf g ∧ IsCompl (fixed g) (moving g) ∧
      (∀ x ∈ fixed g, ∀ y ∈ moving g, b x y = 0) ∧
      (fixedForm g b).Nondegenerate ∧ (movingForm g b).Nondegenerate ∧
      OddPhase.FixedPointFree (movingAction g) ∧
      Function.Bijective (OddPhase.difference (movingAction g)) := by
  have hc := source_isCompl g horder
  have hfree := source_moving_fixedPointFree g horder
  exact ⟨source_order_pos g, hc, fun _ hx _ hy => orthogonal g b hg hx hy,
    fixedForm_nondegenerate_of_isCompl g b hb hbn hg hc,
    movingForm_nondegenerate_of_isCompl g b hb hbn hg hc,
    hfree, (OddPhase.fixedPointFree_iff_bijective (movingAction g)).mp hfree⟩

end PrimeField
end PaperXI.FixedMoving
