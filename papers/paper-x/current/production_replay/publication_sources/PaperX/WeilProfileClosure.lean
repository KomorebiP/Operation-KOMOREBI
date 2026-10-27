import PaperX.WeilSmooth
import PaperX.WeilEuler
import PaperX.WeilMorphisms

/-!
Paper X Claim 9.2: finite-sum local Weil-profile closure.

This file does not construct the arithmetic Galois-to-Weil--Deligne attachment.
It proves that once constituent attached data are supplied, every algebraic and
smooth-inertia property used by the selected finite-copy summand is preserved by
the already constructed Paper X direct-sum datum.  A separate reduction theorem
shows that identifying an actual arithmetic attachment with this constructed datum
is enough to inherit all local polynomial/dimension/trace conclusions.
-/
set_option autoImplicit false
noncomputable section

namespace PaperX.WeilProfileClosure

open scoped BigOperators
open PaperX.CarrierSummands
open PaperX.WeilData
open PaperX.WeilCopies
open PaperX.WeilSmooth
open PaperX.WeilEuler

variable {K G I : Type*} [Field K] [Group G] [Fintype I]
variable {ν : G →* Kˣ} [TopologicalSpace G]
variable {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
variable [∀ i, FiniteDimensional K (W i)]

/-- The selected finite-copy datum simultaneously carries smooth inertia and
all exact local polynomial, dimension, and trace formulas already proved in
Paper X.  This is the algebraic/smooth local-profile half of Claim 9.2. -/
theorem copies_local_profile
    (H : Subgroup G) [H.Normal]
    (D : ∀ i, InertialDatum (ν := ν) H (W i))
    (m : I → ℕ) (φ : G) :
    let S := copiesInertialDatum H D m
    S.toDatum = copiesDatum (fun i => (D i).toDatum) m ∧
    localCharpoly S.toDatum H φ =
      ∏ i, localCharpoly (D i).toDatum H φ ^ m i ∧
    eulerPolynomial S.toDatum H φ =
      ∏ i, eulerPolynomial (D i).toDatum H φ ^ m i ∧
    Module.finrank K (fixedKernel S.toDatum H) =
      ∑ i, m i * Module.finrank K (fixedKernel (D i).toDatum H) ∧
    LinearMap.trace K _ (fixedRep S.toDatum H φ) =
      ∑ i, (m i : K) * LinearMap.trace K _ (fixedRep (D i).toDatum H φ) := by
  dsimp only
  refine ⟨rfl, ?_, ?_, ?_, ?_⟩
  · exact local_charpoly_product (fun i => (D i).toDatum) H m φ
  · exact euler_product (fun i => (D i).toDatum) H m φ
  · exact fixed_dimension_sum (fun i => (D i).toDatum) H m
  · exact fixed_trace_sum (fun i => (D i).toDatum) H m φ

/-- Common coefficient-field local characteristic polynomials survive the
selected finite-copy construction with the expected multiplicities. -/
theorem copies_common_local_polynomial
    {E : Type*} [CommRing E] (σ : E →+* K)
    (H : Subgroup G) [H.Normal]
    (D : ∀ i, InertialDatum (ν := ν) H (W i))
    (m : I → ℕ) (φ : G)
    (P : I → Polynomial E)
    (hP : ∀ i, localCharpoly (D i).toDatum H φ = (P i).map σ) :
    localCharpoly (copiesInertialDatum H D m).toDatum H φ =
      (∏ i, P i ^ m i).map σ := by
  exact common_local_polynomial σ (fun i => (D i).toDatum) H m φ P hP

/-- The same statement for the reversed local Euler denominator. -/
theorem copies_common_euler_polynomial
    {E : Type*} [CommRing E] (σ : E →+* K)
    (H : Subgroup G) [H.Normal]
    (D : ∀ i, InertialDatum (ν := ν) H (W i))
    (m : I → ℕ) (φ : G)
    (P : I → Polynomial E)
    (hP : ∀ i, eulerPolynomial (D i).toDatum H φ = (P i).map σ) :
    eulerPolynomial (copiesInertialDatum H D m).toDatum H φ =
      (∏ i, P i ^ m i).map σ := by
  exact common_euler_polynomial σ (fun i => (D i).toDatum) H m φ P hP

/-- Exact reduction of the remaining WD-attachment problem.  If an independently
constructed arithmetic attachment is identified with the Paper X finite-copy
Weil datum, all local polynomial/dimension/trace formulas follow immediately.
The hypothesis `hA` is precisely the substantive arithmetic attachment/naturality
bridge; this theorem does not manufacture it. -/
theorem actual_attachment_reduction
    (H : Subgroup G) [H.Normal]
    (D : ∀ i, InertialDatum (ν := ν) H (W i))
    (m : I → ℕ) (φ : G)
    (A : Datum ν (Copies W m))
    (hA : A = copiesDatum (fun i => (D i).toDatum) m) :
    localCharpoly A H φ =
      ∏ i, localCharpoly (D i).toDatum H φ ^ m i ∧
    eulerPolynomial A H φ =
      ∏ i, eulerPolynomial (D i).toDatum H φ ^ m i ∧
    Module.finrank K (fixedKernel A H) =
      ∑ i, m i * Module.finrank K (fixedKernel (D i).toDatum H) ∧
    LinearMap.trace K _ (fixedRep A H φ) =
      ∑ i, (m i : K) * LinearMap.trace K _ (fixedRep (D i).toDatum H φ) := by
  subst A
  exact ⟨local_charpoly_product (fun i => (D i).toDatum) H m φ,
    euler_product (fun i => (D i).toDatum) H m φ,
    fixed_dimension_sum (fun i => (D i).toDatum) H m,
    fixed_trace_sum (fun i => (D i).toDatum) H m φ⟩

/-- If the actual attachment is itself packaged with the intended smooth-inertia
conditions, equality of its underlying datum with the finite-copy construction
upgrades the previous reduction without adding any new local hypotheses. -/
theorem actual_inertial_attachment_reduction
    (H : Subgroup G) [H.Normal]
    (D : ∀ i, InertialDatum (ν := ν) H (W i))
    (m : I → ℕ) (φ : G)
    (A : InertialDatum (ν := ν) H (Copies W m))
    (hA : A.toDatum = copiesDatum (fun i => (D i).toDatum) m) :
    localCharpoly A.toDatum H φ =
      ∏ i, localCharpoly (D i).toDatum H φ ^ m i ∧
    eulerPolynomial A.toDatum H φ =
      ∏ i, eulerPolynomial (D i).toDatum H φ ^ m i ∧
    Module.finrank K (fixedKernel A.toDatum H) =
      ∑ i, m i * Module.finrank K (fixedKernel (D i).toDatum H) ∧
    LinearMap.trace K _ (fixedRep A.toDatum H φ) =
      ∑ i, (m i : K) * LinearMap.trace K _ (fixedRep (D i).toDatum H φ) := by
  exact actual_attachment_reduction H D m φ A.toDatum hA

end PaperX.WeilProfileClosure
