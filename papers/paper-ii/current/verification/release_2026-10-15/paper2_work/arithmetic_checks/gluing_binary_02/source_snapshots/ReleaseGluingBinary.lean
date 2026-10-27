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

end Komorebi.PaperII.ReleaseGluing
