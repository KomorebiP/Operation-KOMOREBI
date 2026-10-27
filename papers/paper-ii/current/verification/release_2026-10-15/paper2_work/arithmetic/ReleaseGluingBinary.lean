import ReleaseGluing
import Mathlib.Tactic.FinCases
import Mathlib.Algebra.BigOperators.Fin

set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseGluing

universe u v
variable {O : Type u} {V : Type v}
variable [CommRing O] [AddCommGroup V] [Module O V]

/-- With two complementary packets, either coordinate already detects the gluing class. -/
theorem gluingCoordinate_injective_binary
    (P : Projectors O V (Fin 2)) (Λ : Submodule O V) (i : Fin 2) :
    Function.Injective (gluingCoordinate P Λ i) := by
  apply LinearMap.ker_eq_bot.mp
  apply le_antisymm
  · intro z hz
    obtain ⟨x, rfl⟩ := (splitInside P Λ).mkQ_surjective z
    have hi : P.proj i x ∈ Λ := (rawCoordinate_eq_zero_iff P Λ i x).mp hz
    have hsum : P.proj 0 x + P.proj 1 x = x := by
      simpa only [Fin.sum_univ_two] using reconstruct P x
    have hall : ∀ j, P.proj j x ∈ Λ := by
      intro j
      fin_cases i <;> fin_cases j
      · exact hi
      · have heq : P.proj 1 x = x - P.proj 0 x := by
          apply eq_sub_iff_add_eq.mpr
          simpa only [add_comm] using hsum
        change P.proj 1 x ∈ Λ
        rw [heq]
        exact Λ.sub_mem x.property hi
      · have heq : P.proj 0 x = x - P.proj 1 x :=
          eq_sub_iff_add_eq.mpr hsum
        change P.proj 0 x ∈ Λ
        rw [heq]
        exact Λ.sub_mem x.property hi
      · exact hi
    have hx : x ∈ splitInside P Λ := (mem_splitLattice_iff P Λ x).mpr hall
    simpa only [Submodule.mem_bot, Submodule.mkQ_apply,
      Submodule.Quotient.mk_eq_zero] using hx
  · exact bot_le

/-- The actual binary gluing quotient is isomorphic to either packet quotient. -/
noncomputable def binaryGluingEquivCoordinate
    (P : Projectors O V (Fin 2)) (Λ : Submodule O V) (i : Fin 2) :
    GluingModule P Λ ≃ₗ[O] CoordinateQuotient P Λ i :=
  LinearEquiv.ofBijective (gluingCoordinate P Λ i)
    ⟨gluingCoordinate_injective_binary P Λ i, gluingCoordinate_surjective P Λ i⟩

/-- In the binary case, either least packet weight equals the global gluing weight. -/
theorem binary_packetWeight_eq_globalWeight
    (P : Projectors O V (Fin 2)) (Λ : Submodule O V) (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) (i : Fin 2) :
    packetWeight P Λ pi i (finite i) = globalWeight P Λ pi finite := by
  have hequiv (s : ℕ) : ClearsPacket P Λ pi i s ↔
      ∀ z : GluingModule P Λ, (pi ^ s) • z = 0 := by
    rw [← annihilates_coordinate_iff_clears P Λ pi i s]
    constructor
    · intro h z
      apply gluingCoordinate_injective_binary P Λ i
      rw [map_smul, h _, map_zero]
    · intro h z
      obtain ⟨x, rfl⟩ := gluingCoordinate_surjective P Λ i z
      rw [← map_smul, h _, map_zero]
  apply le_antisymm
  · apply (clearsPacket_iff_weight_le P Λ pi i (finite i) _).mp
    exact (hequiv _).mpr ((gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mpr le_rfl)
  · apply (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mp
    exact (hequiv _).mp ((clearsPacket_iff_weight_le P Λ pi i (finite i) _).mpr le_rfl)

/-- Complementary binary projectors have exactly the same least separation weight. -/
theorem binary_packetWeights_equal
    (P : Projectors O V (Fin 2)) (Λ : Submodule O V) (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) :
    packetWeight P Λ pi 0 (finite 0) = packetWeight P Λ pi 1 (finite 1) := by
  rw [binary_packetWeight_eq_globalWeight, binary_packetWeight_eq_globalWeight]

end Komorebi.PaperII.ReleaseGluing
