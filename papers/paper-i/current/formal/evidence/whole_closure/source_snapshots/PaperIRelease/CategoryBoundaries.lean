import PaperIRelease.CategoryPackets
import PaperIRelease.CategoryExport
import PaperIRelease.GrammarIdeal
import PaperIRelease.GrammarPaths
import PaperIRelease.GrammarFactorization
import KomorebiVerification.FibreRefinement

set_option autoImplicit false
set_option linter.unnecessarySimpa false
set_option linter.unusedSimpArgs false

noncomputable section

namespace Komorebi.PaperIRelease.CategoryBoundaries

open CategoryPackets GrammarAlgebra

/-- Two actual nonzero coordinate packets over Q. -/
abbrev twoPackets : PacketObject ℚ where
  carrier := Fin 2 → ℚ
  index := Fin 2
  algebra := ⊤
  packets := Packet.fibreLinearProjectorFamily id
  packet_nonzero i hi := by
    have h := congrArg (fun T : Module.End ℚ (Fin 2 → ℚ) => T (fun _ => 1) i) hi
    simpa [Packet.fibreLinearProjectorFamily, Packet.fibreLinearProj, Packet.fibreProj] using h

/-- The same vector space viewed as one nonzero packet. -/
abbrev onePacket : PacketObject ℚ where
  carrier := Fin 2 → ℚ
  index := Unit
  algebra := ⊤
  packets := Packet.fibreLinearProjectorFamily (fun _ => ())
  packet_nonzero i hi := by
    cases i
    have h := congrArg (fun T : Module.End ℚ (Fin 2 → ℚ) => T (fun _ => 1) 0) hi
    simpa [Packet.fibreLinearProjectorFamily, Packet.fibreLinearProj, Packet.fibreProj] using h

/-- A real label-merging morphism.  Injective-label formalizations cannot instantiate this. -/
def mergeTwoPackets : PacketMorphism twoPackets onePacket where
  linearMap := LinearMap.id
  algebraMap := AlgHom.id ℚ _
  packetMap := fun _ => ()
  operator_natural _ := by simp
  packet_natural j := by
    cases j
    apply LinearMap.ext
    intro x
    change x = fiberProjector twoPackets (fun _ => ()) () x
    rw [fiberProjector_apply twoPackets (fun _ => ()) () x]
    simp only [↓reduceIte]
    exact (twoPackets.packets.complete x).symm

theorem merge_is_not_injective : ¬ Function.Injective mergeTwoPackets.packetMap := by
  intro h
  have hh : (0 : Fin 2) = 1 := h rfl
  exact (by decide : (0 : Fin 2) ≠ 1) hh

theorem merge_block_naturality (T : twoPackets.algebra) :
    (Foundation.transferBlock onePacket.packets onePacket.packets
      (mergeTwoPackets.algebraMap T).1 () ()).comp mergeTwoPackets.linearMap =
      ∑ b, ∑ a, mergeTwoPackets.linearMap.comp
        (Foundation.transferBlock twoPackets.packets twoPackets.packets T.1 b a) := by
  simpa [mergeTwoPackets] using transferBlock_naturality mergeTwoPackets T () ()

def emptySource : Fin 0 → Fin 0 := Fin.elim0

/-- No vertices forces the presented path algebra to be the zero ring. -/
theorem empty_vertex_algebra (a : PathAlgebra (K := ℚ) emptySource emptySource) : a = 0 := by
  have h : (0 : PathAlgebra (K := ℚ) emptySource emptySource) = 1 := by
    simpa using vertex_complete (freeGrammar (K := ℚ) emptySource emptySource)
  calc
    a = a * 1 := (mul_one a).symm
    _ = a * 0 := congrArg (a * ·) h.symm
    _ = 0 := mul_zero a

end Komorebi.PaperIRelease.CategoryBoundaries

#print axioms Komorebi.PaperIRelease.GrammarAlgebra.typedModuleEquivalence
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.typedIdealModuleEquivalence
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.TypedData.path_action
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.CollapsedRealization.seedRank_imageAlgebra_eq
#print axioms Komorebi.PaperIRelease.CategoryPackets.transferBlock_naturality
#print axioms Komorebi.PaperIRelease.CategoryPackets.seedCategory
#print axioms Komorebi.PaperIRelease.CategoryExport.equation_transport
