import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open scoped BigOperators

noncomputable section

variable {V I : Type*} [AddCommGroup V] [Module ℝ V] [Fintype I]

-- Raw source-facing hypotheses, rather than an assumed mixture certificate.
example (C : ConvexCone ℝ V) (m : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V)
    (hm : ∀ x ∈ C, x ≠ 0 → 0 < m x)
    (hp : ∀ i x, x ∈ C → P i x ∈ C)
    (hc : ∑ i, P i = LinearMap.id) (v : V) (hv : v ∈ C) (hunit : m v = 1) :
    (∀ i, 0 ≤ m (P i v)) ∧ (∑ i, m (P i v)) = 1 ∧
    (∀ i, m (P i v) = 0 ↔ P i v = 0) ∧
    (∀ i : {i : I // 0 < m (P i v)},
      ((m (P i.val v))⁻¹ • P i.val v) ∈ C ∧
        m ((m (P i.val v))⁻¹ • P i.val v) = 1) ∧
    (∑ i : {i : I // 0 < m (P i v)},
      m (P i.val v) • ((m (P i.val v))⁻¹ • P i.val v)) = v :=
  source_core25 C m hm P hp hc ⟨hv, hunit⟩

-- Actual finite real linear maps, with no assumed diagonal form or disjointness.
example {N : Type*} [Fintype N] (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i v, (∀ r, 0 ≤ v r) → ∀ r, 0 ≤ P i v r)
    (hc : ∑ i, P i = LinearMap.id)
    (hi : ∀ i, (P i).comp (P i) = P i) :
    (∃ owner : N → I, ∀ i, P i = Coordinate.selector owner i) ∧
    (∀ r, ∃! i, Coordinate.coefficient (P i) r r = 1) ∧
    (∀ i k, i ≠ k → (P i).comp (P k) = 0) :=
  Coordinate.source_core25_coordinate P hp hc hi

-- The general theorem applies without idempotence.
example :
    (∀ b : Bool, Preserves Examples.quadrant (fun _ : Bool => Examples.halfIdentity) b) := by
  intro b
  exact Examples.half_identity_preserves

#check source_core25
#check sum_positive_weights_one
#check Coordinate.classification_iff
#check Coordinate.source_core25_coordinate
#check Transport.source_coordinate_change
#check Transport.normalized_eq
#check Examples.haar_detail_zero_mass_nonzero
#check Examples.transported_signed_state
#check Examples.empty_coordinate_family

end
