import PaperX.QuadraticGaloisPackets
import PaperX.QuadraticRootCompletion

/-! Completion of actual quadratic Galois packets.  The finite objects are
characters of the absolute Galois group, with a fixed arithmetic kernel.
The coordinate interpretation, compatibility, and continuity are proved. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticArithmeticCompletion

open PaperX.QuadraticAlgebra PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
variable {R : Type} [CommRing R] (I : Ideal R)

@[ext] structure Family where
  values : (n : ℕ) → Packet (R ⧸ I ^ n)
  compatible : ∀ {m n : ℕ} (h : m ≤ n),
    mapPacket (Ideal.Quotient.factorPow I h) (values n) = values m

def reduce (χ : Packet R) : Family I where
  values n := mapPacket (Ideal.Quotient.mk (I ^ n)) χ
  compatible := by
    intro m n h
    apply Subtype.ext
    ext σ
    change Ideal.Quotient.factorPow I h (Ideal.Quotient.mk (I ^ n) (χ.val σ)) =
      Ideal.Quotient.mk (I ^ m) (χ.val σ)
    simp

def rootFamily (x : Family I) : QuadraticRootCompletion.Family I where
  values n := rootOf (x.values n)
  compatible := by
    intro m n h
    rw [← rootOf_natural, x.compatible h]

def reconstruct [IsAdicComplete I R] (x : Family I) : Packet R :=
  ofRoot (QuadraticRootCompletion.reconstruct I (rootFamily I x))

theorem reconstruct_reduces [IsAdicComplete I R] (x : Family I) (n : ℕ) :
    mapPacket (Ideal.Quotient.mk (I ^ n)) (reconstruct I x) = x.values n := by
  rw [reconstruct, ofRoot_natural, QuadraticRootCompletion.reconstruct_reduces]
  exact ofRoot_rootOf (x.values n)

theorem packet_ext [IsHausdorff I R] {χ ψ : Packet R}
    (h : ∀ n, mapPacket (Ideal.Quotient.mk (I ^ n)) χ =
      mapPacket (Ideal.Quotient.mk (I ^ n)) ψ) : χ = ψ := by
  have H : rootOf χ = rootOf ψ := by
    apply QuadraticRootCompletion.root_ext I
    intro n
    simpa only [rootOf_natural] using congrArg rootOf (h n)
  simpa only [ofRoot_rootOf] using congrArg ofRoot H

theorem reconstruct_unique [IsAdicComplete I R] (x : Family I) (χ : Packet R)
    (h : ∀ n, mapPacket (Ideal.Quotient.mk (I ^ n)) χ = x.values n) :
    χ = reconstruct I x := by
  apply packet_ext I
  intro n
  rw [h n, reconstruct_reduces]

theorem reconstruct_reduce [IsAdicComplete I R] (χ : Packet R) :
    reconstruct I (reduce I χ) = χ :=
  (reconstruct_unique I (reduce I χ) χ (fun _ => rfl)).symm

theorem reduce_reconstruct [IsAdicComplete I R] (x : Family I) :
    reduce I (reconstruct I x) = x := by
  apply Family.ext
  funext n
  exact reconstruct_reduces I x n

/-- The inverse-limit equivalence is about actual arithmetic characters. -/
def reconstructionEquiv [IsAdicComplete I R] : Packet R ≃ Family I where
  toFun := reduce I
  invFun := reconstruct I
  left_inv := reconstruct_reduce I
  right_inv := reduce_reconstruct I

/-- The coefficient-preserving coordinate-ring interpretation is retained. -/
def pointReconstructionEquiv [IsAdicComplete I R] :
    (CoordinateRing R →ₐ[R] R) ≃ Family I :=
  (pointPacketEquiv R).trans (reconstructionEquiv I)

theorem reconstructed_continuous [IsAdicComplete I R] [TopologicalSpace R]
    (x : Family I) : Continuous (reconstruct I x).val :=
  packet_continuous (reconstruct I x)

/-- Allowed objects at precision k+1 are actual Galois characters. -/
structure Conditions where
  allowed : (k : ℕ) → Packet (R ⧸ I ^ (k + 1)) → Prop
  downward : ∀ {j k : ℕ} (h : j ≤ k) χ, allowed k χ →
    allowed j (mapPacket (Ideal.Quotient.factorPow I (Nat.add_le_add_right h 1)) χ)

def rootConditions (C : Conditions I) : QuadraticRootCompletion.Conditions I where
  allowed k x := C.allowed k (ofRoot x)
  downward := by
    intro j k h x hx
    have H := C.downward h (ofRoot x) hx
    rwa [ofRoot_natural] at H

def Realizes (C : Conditions I) (χ : Packet R) : Prop :=
  ∀ k, C.allowed k (mapPacket (Ideal.Quotient.mk (I ^ (k + 1))) χ)

/-- No coherent choices of finite characters and no surjective transitions are assumed. -/
theorem exists_realization [IsAdicComplete I R] [TopologicalSpace R]
    (C : Conditions I) (finite : ∀ k, Finite (R ⧸ I ^ (k + 1)))
    (occupied : ∀ k, ∃ χ, C.allowed k χ) :
    ∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ := by
  have ho : ∀ k, ∃ x, (rootConditions I C).allowed k x := by
    intro k
    obtain ⟨χ, hχ⟩ := occupied k
    refine ⟨rootOf χ, ?_⟩
    change C.allowed k (ofRoot (rootOf χ))
    rwa [ofRoot_rootOf]
  obtain ⟨x, hx⟩ := (QuadraticRootCompletion.realization_iff_of_finite_quotients I
    (rootConditions I C) finite).mpr ho
  refine ⟨ofRoot x, packet_continuous _, ?_⟩
  intro k
  have h := hx k
  change C.allowed k (ofRoot (mapRoot (Ideal.Quotient.mk (I ^ (k + 1))) x)) at h
  rwa [← ofRoot_natural] at h

theorem arithmetic_completion_iff [IsAdicComplete I R] [TopologicalSpace R]
    (C : Conditions I) (finite : ∀ k, Finite (R ⧸ I ^ (k + 1))) :
    (∃ χ : Packet R, Continuous χ.val ∧ Realizes I C χ) ↔
      ∀ k, ∃ χ, C.allowed k χ := by
  constructor
  · rintro ⟨χ, _, hχ⟩ k
    exact ⟨mapPacket (Ideal.Quotient.mk (I ^ (k + 1))) χ, hχ k⟩
  · exact exists_realization I C finite

/-- In the actual dyadic coefficient ring the arithmetic completion is one of two packets. -/
theorem dyadic_completion (C : Conditions (R := ℤ_[2]) (IsLocalRing.maximalIdeal ℤ_[2]))
    (occupied : ∀ k, ∃ χ, C.allowed k χ) :
    ∃ χ : Packet ℤ_[2], Continuous χ.val ∧
      Realizes (IsLocalRing.maximalIdeal ℤ_[2]) C χ ∧
      (χ = ofRoot (oneRoot ℤ_[2]) ∨ χ = ofRoot (negativeRoot ℤ_[2])) := by
  let I := IsLocalRing.maximalIdeal ℤ_[2]
  have hfinite : ∀ k, Finite (ℤ_[2] ⧸ I ^ (k + 1)) := by
    intro k
    let : Finite (ℤ_[2] ⧸ I) :=
      Finite.of_equiv (ZMod 2) (PadicInt.residueField (p := 2)).symm.toEquiv
    exact Ideal.finite_quotient_pow (IsNoetherian.noetherian I) (k + 1)
  obtain ⟨χ, hc, hχ⟩ := exists_realization I C hfinite occupied
  exact ⟨χ, hc, hχ, dyadic_packet_classification χ⟩

end PaperX.QuadraticArithmeticCompletion
