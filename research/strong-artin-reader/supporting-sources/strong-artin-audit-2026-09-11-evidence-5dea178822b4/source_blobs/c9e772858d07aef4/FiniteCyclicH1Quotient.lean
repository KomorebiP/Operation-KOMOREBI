import Mathlib.RepresentationTheory.Homological.GroupCohomology.FiniteCyclic
import Mathlib.Algebra.Homology.ShortComplex.ModuleCat

namespace Komorebi.StrongArtin.FiniteCyclicH1Quotient

open CategoryTheory

universe u
noncomputable section

variable {k G : Type u} [CommRing k] [CommGroup G] [Fintype G]

/-- H1 of a finite cyclic action with vanishing norm is the quotient by generator minus one. -/
def cyclicH1QuotientEquiv
    (A : Rep k G) (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (hnorm : A.norm.hom.toLinearMap = 0) :
    (groupCohomology A 1 : Type u) ≃ₗ[k]
      A.V ⧸ LinearMap.range (Rep.applyAsHom A g - 𝟙 A).hom.toLinearMap := by
  let S := Rep.FiniteCyclicGroup.subCompNormHom A g
  have hSg : S.g = 0 := by
    change ModuleCat.ofHom A.norm.hom.toLinearMap = 0
    rw [hnorm]
    rfl
  exact
    (Rep.FiniteCyclicGroup.groupCohomologyIsoOdd A g hg 1 (by simp)).toLinearEquiv |>.trans
      (S.asIsoHomologyι hSg).toLinearEquiv |>.trans
      S.moduleCatOpcyclesIso.toLinearEquiv

/-- Any coefficient vector belongs to the norm kernel when the norm is zero. -/
def normKernelOfNormZero
    (A : Rep k G) (hnorm : A.norm.hom.toLinearMap = 0) (x : A.V) :
    LinearMap.ker A.norm.hom.toLinearMap :=
  ⟨x, by rw [hnorm]; rfl⟩

/-- The H1 class represented by a coefficient vector when the cyclic norm is zero. -/
def cyclicH1Class
    (A : Rep k G) (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (hnorm : A.norm.hom.toLinearMap = 0) (x : A.V) :
    groupCohomology A 1 :=
  Rep.FiniteCyclicGroup.groupCohomologyπOdd A g hg 1 (by simp)
    (normKernelOfNormZero A hnorm x)

/-- Two coefficient vectors define the same degree-one class exactly when their
difference lies in the generator-minus-one range. -/
theorem cyclicH1Class_eq_iff
    (A : Rep k G) (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (hnorm : A.norm.hom.toLinearMap = 0) (x y : A.V) :
    cyclicH1Class A g hg hnorm x = cyclicH1Class A g hg hnorm y ↔
      x - y ∈ LinearMap.range
        (Rep.applyAsHom A g - 𝟙 A).hom.toLinearMap := by
  exact Rep.FiniteCyclicGroup.groupCohomologyπOdd_eq_iff
    A g hg 1 (by simp)
      (normKernelOfNormZero A hnorm x)
      (normKernelOfNormZero A hnorm y)

/-- A coefficient vector represents the zero degree-one class exactly when it
lies in the generator-minus-one range. -/
theorem cyclicH1Class_eq_zero_iff
    (A : Rep k G) (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (hnorm : A.norm.hom.toLinearMap = 0) (x : A.V) :
    cyclicH1Class A g hg hnorm x = 0 ↔
      x ∈ LinearMap.range
        (Rep.applyAsHom A g - 𝟙 A).hom.toLinearMap := by
  exact Rep.FiniteCyclicGroup.groupCohomologyπOdd_eq_zero_iff
    A g hg 1 (by simp) (normKernelOfNormZero A hnorm x)

end
end Komorebi.StrongArtin.FiniteCyclicH1Quotient

#print axioms Komorebi.StrongArtin.FiniteCyclicH1Quotient.cyclicH1QuotientEquiv
#print axioms Komorebi.StrongArtin.FiniteCyclicH1Quotient.normKernelOfNormZero
#print axioms Komorebi.StrongArtin.FiniteCyclicH1Quotient.cyclicH1Class
#print axioms Komorebi.StrongArtin.FiniteCyclicH1Quotient.cyclicH1Class_eq_iff
#print axioms Komorebi.StrongArtin.FiniteCyclicH1Quotient.cyclicH1Class_eq_zero_iff
