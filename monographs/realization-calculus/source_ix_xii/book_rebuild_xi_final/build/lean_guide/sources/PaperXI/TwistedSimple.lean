import PaperXI.CocycleBasis
import PaperXI.TwistedAlgebra
import PaperXI.SchrodingerFourier
import Mathlib.RingTheory.SimpleRing.Basic
import Mathlib.RingTheory.TwoSidedIdeal.Operations

/-! Nondegenerate scalar commutators force simplicity of the actual twisted
algebra. Coordinate elimination is applied to two-sided ideals, so no
semisimplicity or matrix-algebra hypothesis enters the argument. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedSimple
open Module
open PaperXI.CocycleCommutator

variable {A : Type*} [CommGroup A]

/-- The commutator characters separate basis indices under nondegeneracy. -/
theorem commutator_separates (c : Cocycle A ℂˣ) (hnd : radical c = ⊥) :
    ∀ u v : A, u ≠ v → ∃ i : A,
      (↑(commutator c i u) : ℂ) ≠ (↑(commutator c i v) : ℂ) := by
  intro u v huv
  by_contra h
  push Not at h
  apply huv
  apply (MonoidHom.ker_eq_bot_iff (characterMap c)).mp hnd
  apply MonoidHom.ext
  intro i
  have hi : commutator c i u = commutator c i v := Units.ext (h i)
  change commutator c u i = commutator c v i
  rw [commutator_swap c i u, commutator_swap c i v, hi]

/-- The multiplication law itself yields the scalar commutation law. -/
theorem basis_commute {B : Type*} [Ring B] [Algebra ℂ B]
    (c : Cocycle A ℂˣ) (b : Basis A ℂ B)
    (hmul : ∀ a d, b a * b d = (c.coeff a d : ℂ) • b (a * d)) (a d : A) :
    b a * b d = (↑(commutator c a d) : ℂ) • (b d * b a) := by
  rw [hmul, hmul, mul_comm d a, smul_smul]
  congr 1
  change (c.coeff a d : ℂ) = ((c.coeff a d / c.coeff d a : ℂˣ) : ℂ) * _
  exact congrArg (fun z : ℂˣ => (z : ℂ)) (div_mul_cancel (c.coeff a d) (c.coeff d a)).symm

/-- A two-sided ideal is closed under the scalar action from the algebra. -/
theorem ideal_smul_mem {B : Type*} [Ring B] [Algebra ℂ B]
    (J : TwoSidedIdeal B) (z : ℂ) {x : B} (hx : x ∈ J) : z • x ∈ J := by
  rw [Algebra.smul_def]
  exact J.mul_mem_left _ _ hx

omit [CommGroup A] in
/-- For a basis of units, separating scalar commutators imply that every
nonzero two-sided ideal contains a unit basis element. -/
theorem simple_of_basis {B : Type*} [Ring B] [Algebra ℂ B] [Nontrivial B]
    [Fintype A] (b : Basis A ℂ B) (χ : A → A → ℂ)
    (hsep : ∀ u v : A, u ≠ v → ∃ i : A, χ i u ≠ χ i v)
    (hcomm : ∀ i a, b i * b a = χ i a • (b a * b i))
    (hunit : ∀ i, IsUnit (b i)) : IsSimpleRing B := by
  classical
  apply IsSimpleRing.of_eq_bot_or_eq_top
  intro J
  by_cases hJ : J = ⊥
  · exact Or.inl hJ
  right
  obtain ⟨x, hxJ, hx0 : x ≠ 0⟩ :=
    SetLike.exists_of_lt (bot_lt_iff_ne_bot.mpr hJ : ⊥ < J)
  let S : Submodule ℂ (A → ℂ) :=
    { carrier := {f | b.equivFun.symm f ∈ J}
      zero_mem' := by simpa only [Set.mem_ofPred_eq, map_zero] using J.zero_mem
      add_mem' := by
        intro f g hf hg
        simpa only [Set.mem_ofPred_eq, map_add] using J.add_mem hf hg
      smul_mem' := by
        intro z f hf
        simpa only [Set.mem_ofPred_eq, map_smul] using ideal_smul_mem J z hf }
  have hstable : ∀ i f, f ∈ S → (fun a => χ i a * f a) ∈ S := by
    intro i f hf
    change b.equivFun.symm (fun a => χ i a * f a) ∈ J
    have heq : b.equivFun.symm (fun a => χ i a * f a) * b i =
        b i * b.equivFun.symm f := by
      rw [Basis.equivFun_symm_apply, Basis.equivFun_symm_apply,
        Finset.sum_mul, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro a _
      rw [mul_smul_comm, hcomm]
      simp only [smul_mul_assoc, smul_smul]
      rw [mul_comm]
    obtain ⟨v, hv⟩ := hunit i
    have hmem := J.mul_mem_right _ (↑(v⁻¹) : B)
      (heq.symm ▸ J.mul_mem_left (b i) _ hf)
    simpa only [← hv, mul_assoc, Units.mul_inv,
      mul_one] using hmem
  have hxcoord : ∃ u, b.equivFun x u ≠ 0 := by
    by_contra h
    push Not at h
    apply hx0
    apply b.equivFun.injective
    ext a
    simpa using h a
  obtain ⟨u, hu⟩ := hxcoord
  have hxu : b.equivFun x ∈ S := by
    change b.equivFun.symm (b.equivFun x) ∈ J
    simpa using hxJ
  have hdelta := SchrodingerFourier.coordinate_unit_mem χ hsep S hstable u
    (b.equivFun x) hxu hu
  have hbJ : b u ∈ J := by
    change b.equivFun.symm (fun a => if a = u then (1 : ℂ) else 0) ∈ J at hdelta
    have hd : (fun a => if a = u then (1 : ℂ) else 0) = b.equivFun (b u) := by
      ext a
      simp [Basis.equivFun_self, eq_comm]
    simpa only [hd, LinearEquiv.symm_apply_apply] using hdelta
  obtain ⟨v, hv⟩ := hunit u
  apply J.eq_top
  have h := J.mul_mem_left (↑(v⁻¹) : B) (b u) hbJ
  simpa only [← hv, Units.inv_mul] using h

/-- Simplicity of the constructed twisted algebra, without an assumed
semisimplicity, center, multiplication table, or matrix equivalence. -/
theorem isSimpleRing [Fintype A] (c : Cocycle A ℂˣ) (hc : Normalized c)
    (hnd : radical c = ⊥) : IsSimpleRing (TwistedAlgebra.Algebra c hc) := by
  apply simple_of_basis (TwistedAlgebra.basis c hc) (fun i a => ↑(commutator c i a))
    (commutator_separates c hnd) _ (TwistedAlgebra.basis_isUnit c hc)
  intro a d
  rw [TwistedAlgebra.basis_mul, TwistedAlgebra.basis_mul, mul_comm d a, smul_smul]
  congr 1
  change (c.coeff a d : ℂ) = ((c.coeff a d / c.coeff d a : ℂˣ) : ℂ) * _
  exact congrArg (fun z : ℂˣ => (z : ℂ))
    (div_mul_cancel (c.coeff a d) (c.coeff d a)).symm

/-- Elementwise nondegeneracy is equivalent to a trivial radical. -/
theorem radical_eq_bot_iff (c : Cocycle A ℂˣ) : radical c = ⊥ ↔
    ∀ a : A, (∀ x : A, commutator c a x = 1) → a = 1 := by
  rw [eq_bot_iff]
  simp only [SetLike.le_def, mem_radical_iff, Subgroup.mem_bot]

/-- The source-facing form of the simplicity result. -/
theorem isSimpleRing_of_nondegenerate [Fintype A] (c : Cocycle A ℂˣ)
    (hc : Normalized c)
    (hnd : ∀ a : A, (∀ x : A, commutator c a x = 1) → a = 1) :
    IsSimpleRing (TwistedAlgebra.Algebra c hc) :=
  isSimpleRing c hc ((radical_eq_bot_iff c).2 hnd)

omit [CommGroup A] in
/-- The diagonal coordinate action is conjugation by a basis unit. This form
avoids choosing its inverse. -/
theorem diagonal_mul_basis {B : Type*} [Ring B] [Algebra ℂ B] [Fintype A]
    (b : Basis A ℂ B) (χ : A → A → ℂ)
    (hcomm : ∀ i a, b i * b a = χ i a • (b a * b i)) (i : A) (z : B) :
    b.equivFun.symm (fun a => χ i a * b.equivFun z a) * b i = b i * z := by
  conv_rhs => rw [← b.sum_equivFun z]
  rw [Basis.equivFun_symm_apply, Finset.sum_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a _
  rw [mul_smul_comm, hcomm]
  simp only [smul_mul_assoc, smul_smul]
  rw [mul_comm]

/-- A central element has only its identity coefficient under nondegeneracy. -/
theorem center_scalar_of_basis {B : Type*} [Ring B] [Algebra ℂ B] [Fintype A]
    (c : Cocycle A ℂˣ) (hnd : radical c = ⊥) (b : Basis A ℂ B)
    (hmul : ∀ a d, b a * b d = (c.coeff a d : ℂ) • b (a * d))
    (hunit : ∀ i, IsUnit (b i)) (hone : b 1 = 1)
    (z : B) (hz : ∀ y : B, y * z = z * y) :
    z = b.equivFun z 1 • (1 : B) := by
  classical
  let χ : A → A → ℂ := fun i a => ↑(commutator c i a)
  have hcomm : ∀ i a, b i * b a = χ i a • (b a * b i) := basis_commute c b hmul
  have hdiag (i : A) : b.equivFun.symm (fun a => χ i a * b.equivFun z a) = z :=
    (hunit i).mul_right_cancel ((diagonal_mul_basis b χ hcomm i z).trans (hz (b i)))
  have hcoeff (i a : A) : χ i a * b.equivFun z a = b.equivFun z a := by
    have h := congrArg (fun w => b.equivFun w a) (hdiag i)
    simpa only [LinearEquiv.apply_symm_apply] using h
  have hzero (a : A) (ha : a ≠ 1) : b.equivFun z a = 0 := by
    obtain ⟨i, hi⟩ := commutator_separates c hnd a 1 ha
    have hi' : χ i a ≠ 1 := by simpa [χ] using hi
    have heq : (χ i a - 1) * b.equivFun z a = 0 := by
      rw [sub_mul, one_mul, hcoeff, sub_self]
    exact (mul_eq_zero.mp heq).resolve_left (sub_ne_zero.mpr hi')
  calc
    z = ∑ a, b.equivFun z a • b a := (b.sum_equivFun z).symm
    _ = b.equivFun z 1 • b 1 := by
      apply Finset.sum_eq_single 1
      · intro a _ ha
        rw [hzero a ha, zero_smul]
      · simp
    _ = _ := by rw [hone]


set_option backward.isDefEq.respectTransparency false in
/-- The center of the actual algebra consists of unique complex scalars. -/
theorem center_eq_scalars [Fintype A] (c : Cocycle A ℂˣ) (hc : Normalized c)
    (hnd : radical c = ⊥) (z : TwistedAlgebra.Algebra c hc)
    (hz : ∀ y : TwistedAlgebra.Algebra c hc, y * z = z * y) :
    ∃! s : ℂ, z = s • (1 : TwistedAlgebra.Algebra c hc) := by
  have hzscalar : z = (TwistedAlgebra.basis c hc).equivFun z 1 •
      (1 : TwistedAlgebra.Algebra c hc) := by
    apply center_scalar_of_basis (B := TwistedAlgebra.Algebra c hc) c hnd (TwistedAlgebra.basis c hc)
    · exact TwistedAlgebra.basis_mul c hc
    · exact TwistedAlgebra.basis_isUnit c hc
    · exact TwistedAlgebra.basis_one c hc
    · exact hz
  refine ⟨(TwistedAlgebra.basis c hc).equivFun z 1, hzscalar, ?_⟩
  intro s hs
  exact smul_left_injective ℂ (m := (1 : TwistedAlgebra.Algebra c hc)) (one_ne_zero : (1 : TwistedAlgebra.Algebra c hc) ≠ 0)
    (hs.symm.trans hzscalar)

end PaperXI.TwistedSimple
