import PaperX.QuadraticLocalArithmetic
import PaperX.QuadraticGaloisInertia

/-! Independent applications expose the prime-two boundary, the distinction
between local splitting and inertia triviality, characteristic-two coefficient
collapse, and completion over an infinite set of specified local fields. -/
set_option autoImplicit false
noncomputable section
namespace Block22IndependentAudit
open PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
open PaperX.QuadraticLocalGalois PaperX.QuadraticLocalPackets
open PaperX.QuadraticArithmeticCompletion PaperX.QuadraticLocalCompletion
open PaperX.PadicQuadraticSplitting

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
local instance : Fact (Nat.Prime 7) := ⟨by decide⟩
local instance : Fact (Nat.Prime 13) := ⟨by decide⟩

example : ¬ ∃ x : ℚ_[2], x ^ 2 = -1 := no_root_two
example : ¬ ∃ x : ℚ_[3], x ^ 2 = -1 := no_root_three
example : ∃ x : ℚ_[5], x ^ 2 = -1 := root_five
example : ¬ ∃ x : ℚ_[7], x ^ 2 = -1 := by
  rw [root_iff_mod_four_eq_one]
  decide
example : ∃ x : ℚ_[13], x ^ 2 = -1 := by
  rw [root_iff_mod_four_eq_one]

example : Function.Surjective (localQuotient ℚ) := by
  apply localQuotient_surjective
  rintro ⟨x, hx⟩
  nlinarith [sq_nonneg x]

example : IsUnit (2 : ℤ_[3]) := PaperX.QuadraticPadicInertia.two_isUnit 3 (by decide)
example : ¬ IsUnit (2 : ℤ_[2]) := by
  rw [PadicInt.isUnit_iff]
  have h : ‖(2 : ℤ_[2])‖ < 1 :=
    (PadicInt.norm_natCast_lt_one_iff).mpr (dvd_refl 2)
  exact ne_of_lt h

-- The same coefficient character is trivial locally at 5 and nontrivial at 3.
example : LocallyTrivial ℚ_[5] (ofRoot (negativeRoot (ZMod 4))) :=
  locallyTrivial_of_square ℚ_[5] root_five _
example : ¬ LocallyTrivial ℚ_[3] (ofRoot (negativeRoot (ZMod 4))) := by
  rw [locallyTrivial_iff_oneRoot ℚ_[3] no_root_three]
  intro h
  have hv := congrArg Subtype.val (ofRoot_injective h)
  change (-1 : ZMod 4) = 1 at hv
  exact (by decide : (-1 : ZMod 4) ≠ 1) hv

-- This is a direct witness separating whole-local-group triviality from inertia.
example : ∃ χ : Packet (ZMod 4),
    PaperX.QuadraticGaloisInertia.InertiaTrivial 3 χ ∧ ¬ LocallyTrivial ℚ_[3] χ := by
  refine ⟨ofRoot (negativeRoot (ZMod 4)),
    PaperX.QuadraticGaloisInertia.inertiaTrivial_of_odd 3 (by decide) _, ?_⟩
  rw [locallyTrivial_iff_oneRoot ℚ_[3] no_root_three]
  intro h
  have hv := congrArg Subtype.val (ofRoot_injective h)
  change (-1 : ZMod 4) = 1 at hv
  exact (by decide : (-1 : ZMod 4) ≠ 1) hv

-- In characteristic two, sign and trivial collapse, even at a nonsplit field.
example : LocallyTrivial ℚ_[3] (ofRoot (negativeRoot (ZMod 2))) := by
  apply (locallyTrivial_iff_oneRoot ℚ_[3] no_root_three _).mpr
  apply congrArg ofRoot
  apply Subtype.ext
  decide

-- No nontriviality assumption is hidden on the coefficient ring.
example (χ : Packet (ZMod 1)) : LocallyTrivial ℚ_[3] χ := by
  apply MonoidHom.ext
  intro σ
  exact Subsingleton.elim _ _

-- Inertia uses the genuine residue-action kernel. No claim that the entire
-- absolute local Galois group equals the decomposition subgroup is needed.
example (A : ValuationSubring (AlgebraicClosure ℚ_[3]))
    (h : ∀ x : ℤ_[3], PaperX.QuadraticPadicInertia.integralMap 3 x ∈ A)
    (y : AlgebraicClosure ℚ_[3]) (hy : y ^ 2 = -1)
    (σ : A.decompositionSubgroup ℚ_[3]) (hσ : σ ∈ A.inertiaSubgroup ℚ_[3]) :
    (σ.val : AlgebraicClosure ℚ_[3] ≃ₐ[ℚ_[3]] AlgebraicClosure ℚ_[3]) y = y :=
  PaperX.QuadraticPadicInertia.inertia_fixes_square_neg_one 3 (by decide) A h y hy σ hσ

-- Infinite indexing of the local conditions remains admissible. The only
-- finiteness hypothesis below concerns coefficient quotients.
example {R : Type} [CommRing R] [TopologicalSpace R] (I : Ideal R)
    [IsAdicComplete I R] (C : Conditions I)
    (finite : ∀ k, Finite (R ⧸ I ^ (k + 1)))
    (occupied : ∀ k, ∃ χ, C.allowed k χ ∧ ∀ _n : ℕ, LocallyTrivial ℚ_[3] χ) :
    ∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ ∧
      ∀ _n : ℕ, LocallyTrivial ℚ_[3] χ :=
  exists_local_realization I (fun _ : ℕ => ℚ_[3]) C finite occupied

-- A residual condition may hold even though the actual local character fails it.
example : ∃ χ : Packet ℤ_[2],
    LocallyTrivial ℚ_[3] (mapPacket (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) χ) ∧
      ¬ LocallyTrivial ℚ_[3] χ :=
  ⟨ofRoot (negativeRoot ℤ_[2]),
    PaperX.QuadraticLocalArithmetic.sign_residual_locallyTrivial_three,
    PaperX.QuadraticLocalArithmetic.sign_not_locallyTrivial_three⟩

-- The mod-four detector includes arithmetic prime 2, without asserting
-- that its inertia action is trivial.
example (χ : Packet ℤ_[2]) :
    LocallyTrivial ℚ_[2] χ ↔ LocallyTrivial ℚ_[2]
      (mapPacket (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) χ) :=
  PaperX.QuadraticLocalArithmetic.dyadic_local_detection_mod_four 2 χ

end Block22IndependentAudit
