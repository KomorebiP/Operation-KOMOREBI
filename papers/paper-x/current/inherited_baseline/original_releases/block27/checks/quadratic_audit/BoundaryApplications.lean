import PaperX.QuadraticCharacters
import PaperX.QuadraticRootCompletion
import PaperX.QuadraticPacketBoundary
import PaperX.QuadraticGalois
import PaperX.QuadraticArithmeticCompletion

/-! Independent applications to exceptional coefficient rings and actual
Galois descent. These checks supplement the raw-source audit. -/
set_option autoImplicit false
noncomputable section
namespace QuadraticAudit
open PaperX.QuadraticAlgebra PaperX.QuadraticCharacters
open PaperX.QuadraticGalois PaperX.CompletionExamples

def zeroRoot : Root (ZMod 1) := ⟨0, by decide⟩

theorem zeroRingPoint :
    pointEquiv ℤ (rootPoint ℤ zeroRoot) = zeroRoot :=
  (pointEquiv ℤ).apply_symm_apply zeroRoot

theorem zeroRingCharacter :
    toRoot (ofRoot zeroRoot) = zeroRoot :=
  characterEquiv.symm_apply_apply zeroRoot

theorem characteristicTwoUniqueRoot (x : Root (ZMod 2)) : x.val = 1 := by
  have h : ∀ a : ZMod 2, a ^ 2 = 1 → a = 1 := by decide +kernel
  exact h x.val x.property

def extraRoot : Root (ZMod 8) := ⟨3, by decide⟩

theorem nonreducedNonSignCharacter :
    ((ofRoot extraRoot generator : (ZMod 8)ˣ) : ZMod 8) ≠ 1 ∧
    ((ofRoot extraRoot generator : (ZMod 8)ˣ) : ZMod 8) ≠ -1 := by
  rw [ofRoot_generator]
  decide +kernel

theorem coefficientRingNotReduced :
    (4 : ZMod 8) ≠ 0 ∧ (4 : ZMod 8) ^ 2 = 0 := by decide +kernel

def zeroGaloisPacket : Packet (ZMod 1) := descentEquiv.symm (ofRoot zeroRoot)

theorem zeroGaloisFinite : Set.Finite (Set.range zeroGaloisPacket.val) :=
  packet_finite_image zeroGaloisPacket

theorem zeroGaloisContinuous [TopologicalSpace (ZMod 1)] :
    Continuous zeroGaloisPacket.val := by
  exact packet_continuous zeroGaloisPacket

theorem realKernel (σ : Field.absoluteGaloisGroup ℚ) :
    σ ∈ quotientMap.ker ↔
      (show PaperX.ArithmeticCertificateExample.GQ from σ)
        PaperX.ArithmeticCertificateExample.imaginary =
        PaperX.ArithmeticCertificateExample.imaginary :=
  quotientMap_eq_one_iff σ

theorem ontoDescent (ψ : C2 →* (ZMod 8)ˣ) :
    descentEquiv (descentEquiv.symm ψ) = ψ := descentEquiv.apply_symm_apply ψ

theorem emptyAdmissibilityObstructs {R : Type} [CommRing R] (I : Ideal R)
    (C : PaperX.QuadraticRootCompletion.Conditions I) (k : ℕ)
    (empty : ∀ y, ¬ C.allowed k y) :
    ¬ ∃ x, PaperX.QuadraticRootCompletion.Realizes I C x := by
  rintro ⟨x, hx⟩
  exact empty _ (hx k)

theorem genuineDyadicCompletion :
    ∃ χ : Packet ℤ_[2], Continuous χ.val := by
  let C : PaperX.QuadraticArithmeticCompletion.Conditions
      (IsLocalRing.maximalIdeal ℤ_[2]) :=
    { allowed := fun _ _ => True
      downward := fun _ _ _ => trivial }
  have occupied : ∀ k, ∃ χ, C.allowed k χ := by
    intro k
    exact ⟨PaperX.QuadraticGaloisPackets.ofRoot
      (PaperX.QuadraticGaloisPackets.oneRoot _), trivial⟩
  obtain ⟨χ, hc, _, _⟩ :=
    PaperX.QuadraticArithmeticCompletion.dyadic_completion C occupied
  exact ⟨χ, hc⟩

theorem finitePacketObstruction :
    ¬ ∃ χ : Packet (ZMod 16),
      mapPacket PaperX.QuadraticPacketBoundary.reduceSixteen χ =
        PaperX.QuadraticGaloisPackets.threePacket :=
  PaperX.QuadraticGaloisPackets.threePacket_no_lift

#print axioms zeroRingPoint
#print axioms zeroRingCharacter
#print axioms characteristicTwoUniqueRoot
#print axioms nonreducedNonSignCharacter
#print axioms zeroGaloisFinite
#print axioms zeroGaloisContinuous
#print axioms realKernel
#print axioms emptyAdmissibilityObstructs
#print axioms genuineDyadicCompletion
#print axioms finitePacketObstruction
end QuadraticAudit
