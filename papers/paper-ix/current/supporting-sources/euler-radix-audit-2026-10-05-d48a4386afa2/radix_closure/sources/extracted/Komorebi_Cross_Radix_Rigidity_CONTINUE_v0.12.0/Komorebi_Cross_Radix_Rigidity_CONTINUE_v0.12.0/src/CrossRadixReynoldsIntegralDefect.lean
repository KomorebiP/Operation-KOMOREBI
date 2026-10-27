import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Isomorphisms

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

/-- Integral packets on `N` cyclic positions. -/
abbrev IntPacket (N : ℕ) := Fin N → ℤ

/-- Sum the packet and reduce modulo `N`. Its kernel is exactly the locus on
which the denominator `1/N` in the uniform Reynolds average is cancelled. -/
def reynoldsModSum (N : ℕ) : IntPacket N →ₗ[ℤ] ZMod N where
  toFun x := ∑ i, (x i : ZMod N)
  map_add' x y := by simp [Finset.sum_add_distrib]
  map_smul' c x := by
    simp [Finset.mul_sum]

/-- Distinguished integral lattice on which the uniform Reynolds denominator cancels. -/
def ReynoldsGoodLattice (N : ℕ) : Submodule ℤ (IntPacket N) :=
  LinearMap.ker (reynoldsModSum N)

/-- Membership in the good lattice is exactly divisibility of the coordinate sum by `N`. -/
theorem mem_ReynoldsGoodLattice_iff
    {N : ℕ} (x : IntPacket N) :
    x ∈ ReynoldsGoodLattice N ↔ (N : ℤ) ∣ ∑ i, x i := by
  change (∑ i, (x i : ZMod N)) = 0 ↔ _
  rw [← Int.cast_sum]
  exact CharP.intCast_eq_zero_iff (ZMod N) N _

/-- For positive width, every residue modulo `N` is realized by a packet sum. -/
theorem reynoldsModSum_surjective {N : ℕ} (hN : 0 < N) :
    Function.Surjective (reynoldsModSum N) := by
  intro z
  let i0 : Fin N := ⟨0, hN⟩
  let x : IntPacket N := fun i => if i = i0 then (ZMod.cast z : ℤ) else 0
  refine ⟨x, ?_⟩
  change (∑ i, ((x i : ℤ) : ZMod N)) = z
  simp [x, i0]

/-- First-isomorphism description of the Reynolds denominator defect:
`ℤ^N / L_N ≃ ZMod N`, where `L_N` is the good lattice. -/
noncomputable def reynoldsDefectEquiv {N : ℕ} (hN : 0 < N) :
    (IntPacket N ⧸ ReynoldsGoodLattice N) ≃ₗ[ℤ] ZMod N :=
  (reynoldsModSum N).quotKerEquivOfSurjective (reynoldsModSum_surjective hN)

/-- The good-lattice condition can be read as an exact denominator-cancellation witness. -/
theorem reynolds_denominator_cancels_iff
    {N : ℕ} (x : IntPacket N) :
    x ∈ ReynoldsGoodLattice N ↔ ∃ z : ℤ, (∑ i, x i) = N * z := by
  rw [mem_ReynoldsGoodLattice_iff]
  constructor
  · rintro ⟨z, hz⟩
    exact ⟨z, by simpa [mul_comm] using hz⟩
  · rintro ⟨z, hz⟩
    refine ⟨z, ?_⟩
    simpa [mul_comm] using hz


/-- Concrete negative control: the first basis vector at width two does not lie
in the good lattice, so the uniform average produces a genuine denominator. -/
def reynoldsBadPacketTwo : IntPacket 2 := fun i => if i = 0 then 1 else 0

theorem reynoldsBadPacketTwo_not_mem :
    reynoldsBadPacketTwo ∉ ReynoldsGoodLattice 2 := by
  rw [mem_ReynoldsGoodLattice_iff]
  norm_num [reynoldsBadPacketTwo]

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.mem_ReynoldsGoodLattice_iff
#print axioms KomorebiCrossRadix.reynoldsModSum_surjective
#print axioms KomorebiCrossRadix.reynoldsDefectEquiv
#print axioms KomorebiCrossRadix.reynoldsBadPacketTwo_not_mem
