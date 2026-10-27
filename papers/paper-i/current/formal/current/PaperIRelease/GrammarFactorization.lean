import PaperIRelease.GrammarAlgebra
import KomorebiVerification.SeedRankOperations

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unnecessarySimpa false
set_option linter.style.haveILetI false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

universe u
variable {K V E M : Type u} [Field K] [Fintype V]
variable [AddCommGroup M] [Module K M]
variable {G : Grammar K V E}

/-- The algebraic hull is unchanged when the constructed grammar action is replaced by its image. -/
theorem CollapsedRealization.span_imageAlgebra_eq (X : CollapsedRealization G M) (S : Set M) :
    letI : Module (Algebra G) M := Module.compHom M X.action.toRingHom
    letI : Module X.action.range M := Module.compHom M X.action.range.val.toRingHom
    (Submodule.span (Algebra G) S : Set M) = Submodule.span X.action.range S := by
  letI : Module (Algebra G) M := Module.compHom M X.action.toRingHom
  letI : Module X.action.range M := Module.compHom M X.action.range.val.toRingHom
  ext x
  constructor
  · intro hx
    induction hx using Submodule.span_induction with
    | mem x hx => exact Submodule.subset_span hx
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul a x hx ih =>
        exact Submodule.smul_mem _ (X.action.rangeRestrict a) ih
  · intro hx
    induction hx using Submodule.span_induction with
    | mem x hx => exact Submodule.subset_span hx
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul a x hx ih =>
        obtain ⟨b, hb⟩ := a.property
        have h := Submodule.smul_mem (Submodule.span (Algebra G) S) b ih
        change (X.action b) x ∈ Submodule.span (Algebra G) S at h
        change (a : Module.End K M) x ∈ Submodule.span (Algebra G) S
        have he : X.action b = (a : Module.End K M) := hb
        rw [he] at h
        exact h

/-- PSC-I-P-ACTION-FACTORIZATION: seed rank is preserved by passage to the realized image algebra. -/
theorem CollapsedRealization.seedRank_imageAlgebra_eq (X : CollapsedRealization G M) :
    letI : Module (Algebra G) M := Module.compHom M X.action.toRingHom
    letI : Module X.action.range M := Module.compHom M X.action.range.val.toRingHom
    SeedRankBasics.seedRank (Algebra G) M = SeedRankBasics.seedRank X.action.range M := by
  letI : Module (Algebra G) M := Module.compHom M X.action.toRingHom
  let f : M →ₛₗ[X.action.toRingHom] M :=
    { toFun := id
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }
  exact SeedRankOperations.seedRank_imageAlgebra_eq X.action f Function.bijective_id

end Komorebi.PaperIRelease.GrammarAlgebra
