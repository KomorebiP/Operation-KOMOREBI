module

public import KomorebiPhysics.CornerCurvature
public import QuantumPacketCore
public import TensorRefinement
import all TensorRefinement

/-!
Full physics master, Chapter 7.5, equations (7.31)--(7.37).
Every differentiated matrix corner is reconstructed exactly from two-step paths
through one intermediate packet, and the same identity is stable under finite
coarsening.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
set_option linter.unusedSectionVars false
namespace KomorebiPhysics.CornerReconstruction

open scoped BigOperators
open KomorebiPaperVII
open CornerDerivation

variable {n I : Type*} [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]
local notation "Mat" => Matrix n n ℂ

/-- Matrix corner `P_a X P_b`. -/
def corner (P : PacketFamily Mat I) (X : Mat) (a b : I) : Mat :=
  P.proj a * X * P.proj b

@[simp] theorem corner_zero (P : PacketFamily Mat I) (a b : I) : corner P 0 a b = 0 := by
  simp [corner]

theorem corner_add (P : PacketFamily Mat I) (X Y : Mat) (a b : I) :
    corner P (X + Y) a b = corner P X a b + corner P Y a b := by
  unfold corner
  noncomm_ring

/-- Full projector-corner reconstruction, equation (7.32) without differentiation. -/
theorem reconstruct (P : PacketFamily Mat I) (X : Mat) :
    (∑ a, ∑ b, corner P X a b) = X := by
  unfold corner
  simp only [← Finset.sum_mul, ← Finset.mul_sum, P.sum_proj, mul_one, one_mul]

/-- Equation (7.32) for the actual finite derivation. -/
theorem reconstruct_delta (P : PacketFamily Mat I) (K X : Mat) :
    (∑ a, ∑ b, corner P (delta K X) a b) = delta K X :=
  reconstruct P _

/-- Insert the packet resolution between `K` and `X`, equation (7.34). -/
theorem insert_resolution_left (P : PacketFamily Mat I) (K X : Mat) (a b : I) :
    P.proj a * K * X * P.proj b =
      ∑ c, P.proj a * K * P.proj c * X * P.proj b := by
  calc
    P.proj a * K * X * P.proj b =
        P.proj a * K * (∑ c, P.proj c) * X * P.proj b := by rw [P.sum_proj, mul_one]
    _ = ∑ c, P.proj a * K * P.proj c * X * P.proj b := by
      simp only [Finset.mul_sum, Finset.sum_mul]

/-- Insert the packet resolution between `X` and `K`, equation (7.35). -/
theorem insert_resolution_right (P : PacketFamily Mat I) (K X : Mat) (a b : I) :
    P.proj a * X * K * P.proj b =
      ∑ c, P.proj a * X * P.proj c * K * P.proj b := by
  calc
    P.proj a * X * K * P.proj b =
        P.proj a * X * (∑ c, P.proj c) * K * P.proj b := by rw [P.sum_proj, mul_one]
    _ = ∑ c, P.proj a * X * P.proj c * K * P.proj b := by
      simp only [Finset.mul_sum, Finset.sum_mul]

/-- The two-step path through packet `c`. -/
def pathTerm (P : PacketFamily Mat I) (K X : Mat) (a c b : I) : Mat :=
  P.proj a * K * P.proj c * X * P.proj b -
    P.proj a * X * P.proj c * K * P.proj b

/-- Literal differentiated-corner path expansion, equation (7.33). -/
theorem corner_delta_path (P : PacketFamily Mat I) (K X : Mat) (a b : I) :
    corner P (delta K X) a b = Complex.I • (∑ c, pathTerm P K X a c b) := by
  have hL := insert_resolution_left P K X a b
  have hR := insert_resolution_right P K X a b
  calc
    corner P (delta K X) a b =
        Complex.I • (P.proj a * K * X * P.proj b - P.proj a * X * K * P.proj b) := by
          unfold corner CornerDerivation.delta
          rw [mul_smul_comm, smul_mul_assoc]
          congr 1
          noncomm_ring
    _ = Complex.I • ((∑ c, P.proj a * K * P.proj c * X * P.proj b) -
        (∑ c, P.proj a * X * P.proj c * K * P.proj b)) := by rw [← hL, ← hR]
    _ = Complex.I • (∑ c, pathTerm P K X a c b) := by
          congr 1
          simp only [pathTerm, Finset.sum_sub_distrib]

/-- Each path term is the difference of two genuine two-step corner products. -/
theorem pathTerm_as_corner_products (P : PacketFamily Mat I) (K X : Mat) (a c b : I) :
    pathTerm P K X a c b =
      corner P K a c * corner P X c b - corner P X a c * corner P K c b := by
  have h1 : corner P K a c * corner P X c b =
      P.proj a * K * P.proj c * X * P.proj b := by
    unfold corner
    calc
      _ = P.proj a * K * (P.proj c * P.proj c) * X * P.proj b := by noncomm_ring
      _ = _ := by rw [P.idempotent]
  have h2 : corner P X a c * corner P K c b =
      P.proj a * X * P.proj c * K * P.proj b := by
    unfold corner
    calc
      _ = P.proj a * X * (P.proj c * P.proj c) * K * P.proj b := by noncomm_ring
      _ = _ := by rw [P.idempotent]
  rw [h1, h2]
  rfl

/-- Path expansion written entirely in corner-product notation. -/
theorem corner_delta_path_products (P : PacketFamily Mat I) (K X : Mat) (a b : I) :
    corner P (delta K X) a b =
      Complex.I • (∑ c, (corner P K a c * corner P X c b -
        corner P X a c * corner P K c b)) := by
  rw [corner_delta_path]
  congr 1
  apply Finset.sum_congr rfl
  intro c _
  exact pathTerm_as_corner_products P K X a c b

section Coarse
variable {J : Type*} [Fintype J] [DecidableEq J]

/-- Finite coarse projector from an address map. -/
def coarseProjector (P : PacketFamily Mat I) (address : I → J) (A : J) : Mat :=
  KomorebiPaperVII.TensorRefinement.coarse P.proj address A

/-- Coarse projectors still resolve the identity. -/
theorem coarse_complete (P : PacketFamily Mat I) (address : I → J) :
    ∑ A, coarseProjector P address A = 1 := by
  exact KomorebiPaperVII.TensorRefinement.coarse_complete P.proj address P.sum_proj

/-- Coarse projectors inherit the exact projector multiplication law. -/
theorem coarse_mul (P : PacketFamily Mat I) (address : I → J) (A B : J) :
    coarseProjector P address A * coarseProjector P address B =
      if A = B then coarseProjector P address A else 0 := by
  exact KomorebiPaperVII.TensorRefinement.coarse_mul P.proj address P.mul_proj A B

/-- Equation (7.37): coarse differentiated corners are exact sums of fine corners. -/
theorem coarse_corner (P : PacketFamily Mat I) (address : I → J)
    (X : Mat) (A B : J) :
    coarseProjector P address A * X * coarseProjector P address B =
      ∑ a, ∑ b,
        if address a = A ∧ address b = B then corner P X a b else 0 := by
  calc
    coarseProjector P address A * X * coarseProjector P address B =
        ∑ b, ∑ a, if address a = A ∧ address b = B then corner P X a b else 0 := by
      unfold coarseProjector KomorebiPaperVII.TensorRefinement.coarse corner
      simp only [Finset.sum_mul, Finset.mul_sum, ite_mul, mul_ite, zero_mul, mul_zero]
      apply Finset.sum_congr rfl
      intro b _
      by_cases hb : address b = B
      · simp only [hb, ite_true]
        apply Finset.sum_congr rfl
        intro a _
        by_cases ha : address a = A <;> simp [ha]
      · simp [hb]
    _ = ∑ a, ∑ b, if address a = A ∧ address b = B then corner P X a b else 0 := by
      rw [Finset.sum_comm]

/-- The literal coarse differentiated corner is the fine-corner sum. -/
theorem coarse_delta_corner (P : PacketFamily Mat I) (address : I → J)
    (K X : Mat) (A B : J) :
    coarseProjector P address A * delta K X * coarseProjector P address B =
      ∑ a, ∑ b,
        if address a = A ∧ address b = B then corner P (delta K X) a b else 0 :=
  coarse_corner P address _ A B

/-- Coarse corners reconstruct the entire differentiated matrix. -/
theorem coarse_reconstruct_delta (P : PacketFamily Mat I) (address : I → J) (K X : Mat) :
    (∑ A, ∑ B,
      coarseProjector P address A * delta K X * coarseProjector P address B) = delta K X := by
  simp only [← Finset.sum_mul, ← Finset.mul_sum, coarse_complete, mul_one, one_mul]

end Coarse

end KomorebiPhysics.CornerReconstruction
