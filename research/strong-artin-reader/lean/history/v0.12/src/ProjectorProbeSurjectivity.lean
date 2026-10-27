import Mathlib.LinearAlgebra.Dual.Lemmas

namespace Komorebi.StrongArtin.ProjectorProbeSurjectivity

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- Evaluation against a finite family of residual projector/Frobenius probes. -/
def probeEvalMap (probe : ι → Module.Dual k V) : V →ₗ[k] (ι → k) where
  toFun v := fun i => probe i v
  map_add' x y := by
    ext i
    simp
  map_smul' a x := by
    ext i
    simp

@[simp] theorem probeEvalMap_apply (probe : ι → Module.Dual k V) (v : V) (i : ι) :
    probeEvalMap probe v i = probe i v := rfl

/-- A family of linear probes separates deformation directions exactly when the
associated evaluation map is injective. The direction used here is the one
needed for adequacy/projector detection. -/
theorem probeEvalMap_injective_of_separates
    (probe : ι → Module.Dual k V)
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0) :
    Function.Injective (probeEvalMap probe) := by
  intro x y hxy
  have hz : probeEvalMap probe (x - y) = 0 := by
    rw [map_sub, hxy, sub_self]
  have hxy0 : x - y = 0 := hsep (x - y) (by
    intro i
    have hi := congrFun hz i
    simpa using hi)
  exact sub_eq_zero.mp hxy0

/-- **Detection-to-surjectivity bridge.** If a finite family of projector or
Frobenius functionals separates every nonzero deformation direction, then the
dual of the evaluation map is surjective onto the complete dual deformation
space.

This is the finite-dimensional linear-algebra bridge used in the Strong Artin
program: once global auxiliary primes realize a separating probe family, there
is no additional linear-algebra obstruction to spanning/killing all transverse
dual directions. -/
theorem dual_probeMap_surjective_of_separates
    (probe : ι → Module.Dual k V)
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0) :
    Function.Surjective (probeEvalMap probe).dualMap := by
  exact LinearMap.dualMap_surjective_of_injective
    (probeEvalMap_injective_of_separates probe hsep)

/-- Elementwise form: every dual deformation functional is pulled back from a
linear functional on the finite coordinate space of probe values. -/
theorem every_dual_functional_factors_through_probes
    (probe : ι → Module.Dual k V)
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0)
    (ell : Module.Dual k V) :
    ∃ L : Module.Dual k (ι → k), (probeEvalMap probe).dualMap L = ell := by
  exact dual_probeMap_surjective_of_separates probe hsep ell

/-- A weaker and often easier hypothesis suffices: if the only vector killed by
all probes is zero, the same dual-surjectivity conclusion follows. -/
theorem dual_probeMap_surjective_of_joint_kernel_zero
    (probe : ι → Module.Dual k V)
    (hker : {v : V | ∀ i : ι, probe i v = 0} = {0}) :
    Function.Surjective (probeEvalMap probe).dualMap := by
  apply dual_probeMap_surjective_of_separates probe
  intro v hv
  have hm : v ∈ {v : V | ∀ i : ι, probe i v = 0} := hv
  rw [hker] at hm
  simpa using hm

/-- Descend a probe family to the quotient by a deliberately retained defect
subspace, assuming every probe vanishes on that defect. -/
def quotientProbe (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i)) :
    ι → Module.Dual k (V ⧸ D) :=
  fun i => D.liftQ (probe i) (hvan i)

@[simp] theorem quotientProbe_mk (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i)) (i : ι) (v : V) :
    quotientProbe D probe hvan i (D.mkQ v) = probe i v := by
  rfl

/-- **Relative/transverse separation.** If the common kernel of the probes is
contained in the deliberately retained defect subspace `D`, then the descended
probes separate the quotient `V ⧸ D`. The probes need not see the defect itself. -/
theorem quotientProbe_separates_of_kernel_le_defect
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D) :
    ∀ q : V ⧸ D, (∀ i : ι, quotientProbe D probe hvan i q = 0) → q = 0 := by
  intro q hq
  rcases D.mkQ_surjective q with ⟨v, rfl⟩
  rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
  apply hsep v
  intro i
  simpa [quotientProbe] using hq i

/-- **Transverse adequacy bridge.** A probe family that is blind exactly on a
retained defect subspace but separates every class modulo that defect induces a
surjective dual probe map on the quotient deformation space.

For the Strong Artin application, `D` is intended to be the known cyclic
quotient-character defect. Thus full adequacy at the quotient prime can be
replaced, at the linear-algebra level, by adequacy transverse to `D`. -/
theorem dual_quotientProbe_surjective_of_kernel_le_defect
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D) :
    Function.Surjective (probeEvalMap (quotientProbe D probe hvan)).dualMap := by
  apply dual_probeMap_surjective_of_separates (quotientProbe D probe hvan)
  exact quotientProbe_separates_of_kernel_le_defect D probe hvan hsep

/-- Elementwise transverse form: every dual functional on the quotient by the
retained defect is generated through the descended probe coordinate map. -/
theorem every_transverse_dual_factors_through_probes
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D)
    (ell : Module.Dual k (V ⧸ D)) :
    ∃ L : Module.Dual k (ι → k),
      (probeEvalMap (quotientProbe D probe hvan)).dualMap L = ell := by
  exact dual_quotientProbe_surjective_of_kernel_le_defect D probe hvan hsep ell

end
end Komorebi.StrongArtin.ProjectorProbeSurjectivity

#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.probeEvalMap_injective_of_separates
#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.dual_probeMap_surjective_of_separates
#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.every_dual_functional_factors_through_probes
#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.dual_probeMap_surjective_of_joint_kernel_zero

#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.quotientProbe_separates_of_kernel_le_defect
#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.dual_quotientProbe_surjective_of_kernel_le_defect
#print axioms Komorebi.StrongArtin.ProjectorProbeSurjectivity.every_transverse_dual_factors_through_probes
