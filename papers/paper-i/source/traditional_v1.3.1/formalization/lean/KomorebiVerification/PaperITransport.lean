import KomorebiVerification.ProjectorCore

/-!
# Paper I: coordinate transport and block naturality

This module formalizes the algebraic content of Paper I, Section 8.  The
target-side operator is supplied explicitly in the naturality theorem, avoiding
the manuscript's ill-typed expression `φ(T)` when `T` has not been assumed to
belong to the domain of `φ`.
-/

set_option autoImplicit false

namespace Komorebi.Foundation

universe u v w x

variable {R : Type u} {M : Type v} {N : Type w} {ι : Type x}
variable [Semiring R]
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable [Fintype ι]

namespace LinearProjectorFamily

/-- Transport a finite projector family through a linear equivalence. -/
def conjugate
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N) :
    LinearProjectorFamily R N ι where
  proj i := U.toLinearMap.comp ((P.proj i).comp U.symm.toLinearMap)
  idempotent i y := by
    change U (P.proj i (U.symm (U (P.proj i (U.symm y))))) =
      U (P.proj i (U.symm y))
    rw [U.symm_apply_apply, P.idempotent]
  orthogonal hij y := by
    change U (P.proj _ (U.symm (U (P.proj _ (U.symm y))))) = 0
    rw [U.symm_apply_apply, P.orthogonal hij, map_zero]
  complete y := by
    change (∑ i, U (P.proj i (U.symm y))) = y
    rw [← map_sum, P.complete, U.apply_symm_apply]

@[simp] theorem conjugate_proj_apply
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N)
    (i : ι) (y : N) :
    (P.conjugate U).proj i y = U (P.proj i (U.symm y)) :=
  rfl

end LinearProjectorFamily

/-- Conjugate an endomorphism through a linear equivalence. -/
def conjugateEnd (U : M ≃ₗ[R] N) (T : Module.End R M) : Module.End R N :=
  U.toLinearMap.comp (T.comp U.symm.toLinearMap)

@[simp] theorem conjugateEnd_apply
    (U : M ≃ₗ[R] N) (T : Module.End R M) (y : N) :
    conjugateEnd U T y = U (T (U.symm y)) :=
  rfl

/-- Transfer blocks commute exactly with coordinate conjugation. -/
theorem conjugate_transferBlock
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N)
    (T : Module.End R M) (j i : ι) :
    transferBlock (P.conjugate U) (P.conjugate U)
        (conjugateEnd U T) j i =
      conjugateEnd U (transferBlock P P T j i) := by
  apply LinearMap.ext
  intro y
  simp [transferBlock, conjugateEnd]

/--
Packet blocks commute with an intertwiner when both the operator and every
projector intertwine.  This is the type-correct algebraic naturality statement.
-/
theorem transferBlock_natural
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N ι)
    (Φ : M →ₗ[R] N) (T : Module.End R M) (T' : Module.End R N)
    (hT : Φ.comp T = T'.comp Φ)
    (hproj : ∀ i, Φ.comp (P.proj i) = (Q.proj i).comp Φ)
    (j i : ι) :
    Φ.comp (transferBlock P P T j i) =
      (transferBlock Q Q T' j i).comp Φ := by
  apply LinearMap.ext
  intro x
  have hpj (z : M) : Φ (P.proj j z) = Q.proj j (Φ z) := by
    simpa only [LinearMap.comp_apply] using
      congrArg (fun f : M →ₗ[R] N => f z) (hproj j)
  have hTi (z : M) : Φ (T z) = T' (Φ z) := by
    simpa only [LinearMap.comp_apply] using
      congrArg (fun f : M →ₗ[R] N => f z) hT
  have hpi : Φ (P.proj i x) = Q.proj i (Φ x) := by
    simpa only [LinearMap.comp_apply] using
      congrArg (fun f : M →ₗ[R] N => f x) (hproj i)
  change Φ (P.proj j (T (P.proj i x))) =
    Q.proj j (T' (Q.proj i (Φ x)))
  rw [hpj, hTi, hpi]

end Komorebi.Foundation

