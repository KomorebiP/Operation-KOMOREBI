import PaperXI.MoritaActualCartan110

/-! The same actual Cartan witnesses compare two actual lattices. This is an
additive assertion; no canonical H1/J1 or multiplicative attachment is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaPairIndex110
open Matrix Module ValuativeRel
open PaperXI.MoritaLattice110 PaperXI.MoritaCornerRank110
open PaperXI.MoritaActualCartan110

variable (F E : Type*) [Field F] [Field E] [Algebra F E]
  [Module.Finite F E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E]
variable (m : Type*) [Fintype m] [DecidableEq m] [Nonempty m]

/-- The additive index is independent of the choice of finite full maximal-order
bimodule commuting with the scalar radical. Both sides use one factorization
of the same y, rather than independent existential exponent witnesses. -/
theorem actual_pair_index
    (L₁ L₂ : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL₁ : IsMatrixBimodule (coefficientMap F E) L₁.toAddSubgroup)
    (hL₂ : IsMatrixBimodule (coefficientMap F E) L₂.toAddSubgroup)
    (hfg₁ : L₁.FG) (hfg₂ : L₂.FG)
    (hfull₁ : Submodule.span F (L₁ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hfull₂ : Submodule.span F (L₂ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm₁ : RadicalCommutes F E m L₁.toAddSubgroup)
    (hcomm₂ : RadicalCommutes F E m L₂.toAddSubgroup) (y : GL m E) :
    (L₁.toAddSubgroup ⊓ L₁.toAddSubgroup.map
      (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
        L₁.toAddSubgroup =
    (L₂.toAddSubgroup ⊓ L₂.toAddSubgroup.map
      (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
        L₂.toAddSubgroup := by
  obtain ⟨c, l, r, a, _, hy⟩ := PaperXI.ActualLocalCartan106.hasCartan E m y
  rw [relIndex_of_actual_cartan F E m L₁ hL₁ hfg₁ hfull₁ hcomm₁ y c l r a hy,
    relIndex_of_actual_cartan F E m L₂ hL₂ hfg₂ hfull₂ hcomm₂ y c l r a hy]

end PaperXI.MoritaPairIndex110
