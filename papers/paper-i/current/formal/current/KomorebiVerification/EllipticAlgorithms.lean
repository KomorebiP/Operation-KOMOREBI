import KomorebiVerification.PaperIBlockCompletion
import KomorebiVerification.SeedRankBasics
import KomorebiVerification.SingleOperatorGraph

/-!
# Paper I: elliptic coordinates and finite algorithm specifications

This module checks the displayed two-packet model of
`k[x,y] / (y^2 - x^3 + x)`.  The normal form is represented by Mathlib's
quadratic algebra over `k[x]`: an element is exactly a pair `a + y b`, and
the defining multiplication law makes `y^2 = x^3 - x` hold definitionally.

It also gives mathematical specifications and correctness theorems for the
three finite algorithms stated in Paper I.  The orbit-closure construction is
an ascending chain of subspaces and is proved to terminate in finite
dimension.  The transfer-block construction is an actual finite table whose
sum is proved to reconstruct the input map.  The graph routine is specified as
the maximum exact eigenspace dimension over the finite spectrum; evaluation
and performance of a concrete symbolic backend are deliberately outside the
scope of these declarations.
-/

set_option autoImplicit false

-- Suppress only style/unused lints in the frozen completion proofs; warnings remain fatal.
set_option linter.unnecessarySeqFocus false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace Komorebi

/-! ## The elliptic coordinate algebra -/

namespace EllipticCoordinates

open Polynomial

noncomputable section

universe u

variable (k : Type u) [Field k]

/-- The coefficient `x^3 - x` in the elliptic relation. -/
def curveWeight : Polynomial k := X ^ 3 - X

/-- The relation polynomial in the outer variable `y`. -/
def relationPolynomial : Polynomial (Polynomial k) :=
  X ^ 2 - C (curveWeight k)

/-- The literal quotient presentation `k[x][y] / (y^2 - (x^3 - x))`. -/
abbrev QuotientModel := AdjoinRoot (relationPolynomial k)

/--
The unique-normal-form model.  An element is exactly `a + y b`, stored as the
two fields `re = a` and `im = b`; the quadratic generator squares to
`curveWeight k`.
-/
abbrev NormalForm :=
  QuadraticAlgebra (Polynomial k) (curveWeight k) 0

/-- The distinguished normal-form generator `y = 0 + y * 1`. -/
def y : NormalForm k := QuadraticAlgebra.omega

/-- Coefficient coordinates `(a + y b) \mapsto (a,b)`, explicitly `k`-linear. -/
def coefficientCoordinates :
    NormalForm k ≃ₗ[k] Polynomial k × Polynomial k where
  toFun z := (z.re, z.im)
  invFun p := ⟨p.1, p.2⟩
  left_inv z := by cases z <;> rfl
  right_inv p := by cases p <;> rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

@[simp] theorem coefficientCoordinates_apply (z : NormalForm k) :
    coefficientCoordinates k z = (z.re, z.im) := rfl

@[simp] theorem coefficientCoordinates_symm_apply
    (p : Polynomial k × Polynomial k) :
    (coefficientCoordinates k).symm p = ⟨p.1, p.2⟩ := rfl

/-- The even packet projector `P₀(a + yb) = a`. -/
def P0 : Module.End k (NormalForm k) where
  toFun z := ⟨z.re, 0⟩
  map_add' _ _ := by apply QuadraticAlgebra.ext <;> simp
  map_smul' _ _ := by ext <;> simp

/-- The odd packet projector `P₁(a + yb) = yb`. -/
def P1 : Module.End k (NormalForm k) where
  toFun z := ⟨0, z.im⟩
  map_add' _ _ := by apply QuadraticAlgebra.ext <;> simp
  map_smul' _ _ := by ext <;> simp

@[simp] theorem P0_apply (z : NormalForm k) : P0 k z = ⟨z.re, 0⟩ := by
  simp [P0]

@[simp] theorem P1_apply (z : NormalForm k) : P1 k z = ⟨0, z.im⟩ := by
  simp [P1]

theorem P0_idempotent : (P0 k).comp (P0 k) = P0 k := by
  apply LinearMap.ext
  intro z
  apply QuadraticAlgebra.ext <;> simp [P0]

theorem P1_idempotent : (P1 k).comp (P1 k) = P1 k := by
  apply LinearMap.ext
  intro z
  apply QuadraticAlgebra.ext <;> simp [P1]

theorem P0_P1_orthogonal : (P0 k).comp (P1 k) = 0 := by
  apply LinearMap.ext
  intro z
  apply QuadraticAlgebra.ext <;> simp [P0, P1]

theorem P1_P0_orthogonal : (P1 k).comp (P0 k) = 0 := by
  apply LinearMap.ext
  intro z
  apply QuadraticAlgebra.ext <;> simp [P0, P1]

theorem P0_add_P1 : P0 k + P1 k = LinearMap.id := by
  apply LinearMap.ext
  intro z
  apply QuadraticAlgebra.ext <;> simp

/-- The two coefficient packets as a complete finite projector family. -/
def packetProjectors :
    Foundation.LinearProjectorFamily k (NormalForm k) Bool where
  proj i := if i then P1 k else P0 k
  idempotent i z := by
    cases i <;> simp [P0, P1]
  orthogonal {i j} hij z := by
    cases i <;> cases j
    · exact (hij rfl).elim
    · apply QuadraticAlgebra.ext <;> simp [P0, P1]
    · apply QuadraticAlgebra.ext <;> simp [P0, P1]
    · exact (hij rfl).elim
  complete z := by
    apply QuadraticAlgebra.ext <;> simp [P0, P1]

/-- Multiplication by the coefficient variable `x`, in normal-form coordinates. -/
def Mx : Module.End k (NormalForm k) where
  toFun z := ⟨X * z.re, X * z.im⟩
  map_add' z w := by ext <;> simp [mul_add]
  map_smul' c z := by ext <;> simp [mul_smul_comm]

/-- Multiplication by `y`, in normal-form coordinates. -/
def My : Module.End k (NormalForm k) where
  toFun z := ⟨curveWeight k * z.im, z.re⟩
  map_add' z w := by ext <;> simp [mul_add]
  map_smul' c z := by ext <;> simp [mul_smul_comm]

@[simp] theorem Mx_apply (z : NormalForm k) :
    Mx k z = ⟨X * z.re, X * z.im⟩ := rfl

@[simp] theorem My_apply (z : NormalForm k) :
    My k z = ⟨curveWeight k * z.im, z.re⟩ := rfl

/-- `M_x` really is multiplication by the class of the coefficient variable. -/
theorem Mx_eq_multiplication (z : NormalForm k) :
    Mx k z =
      (algebraMap (Polynomial k) (NormalForm k) X) * z := by
  apply QuadraticAlgebra.ext <;> simp [Mx]

/-- `M_y` really is multiplication by the quadratic generator. -/
theorem My_eq_multiplication (z : NormalForm k) :
    My k z = y k * z := by
  apply QuadraticAlgebra.ext <;> simp [My, y]

/-- Multiplication by `y` sends the odd coefficient packet into the even one. -/
theorem P0_My (z : NormalForm k) :
    P0 k (My k z) = ⟨curveWeight k * z.im, 0⟩ := by
  simp

/-- Multiplication by `y` sends the even coefficient packet into the odd one. -/
theorem P1_My (z : NormalForm k) :
    P1 k (My k z) = ⟨0, z.re⟩ := by
  simp

/-- A concrete witness that `P₀` is not linear over the full coordinate algebra. -/
theorem P0_not_full_algebra_linear :
    P0 k (y k * 1) ≠ y k * P0 k 1 := by
  intro h
  have him := congrArg QuadraticAlgebra.im h
  simp only [P0, y, LinearMap.coe_mk, AddHom.coe_mk,
    QuadraticAlgebra.im_mul, QuadraticAlgebra.im_one,
    QuadraticAlgebra.re_one, QuadraticAlgebra.im_omega,
    QuadraticAlgebra.re_omega, mul_zero, zero_mul, one_mul, add_zero, zero_add] at him
  exact zero_ne_one him

/-- A concrete witness that `P₁` is not linear over the full coordinate algebra. -/
theorem P1_not_full_algebra_linear :
    P1 k (y k * 1) ≠ y k * P1 k 1 := by
  intro h
  have him := congrArg QuadraticAlgebra.im h
  simp only [P1, y, LinearMap.coe_mk, AddHom.coe_mk,
    QuadraticAlgebra.im_mul, QuadraticAlgebra.im_one,
    QuadraticAlgebra.re_one, QuadraticAlgebra.im_omega,
    QuadraticAlgebra.re_omega, mul_zero, zero_mul, one_mul, add_zero, zero_add] at him
  exact one_ne_zero him

/--
The unit is a genuine one-element module seed when the coordinate algebra acts
on itself by multiplication.
-/
theorem unitSeed_generates :
    SeedRankBasics.Generates (NormalForm k) (NormalForm k)
      ({1} : Set (NormalForm k)) := by
  rw [SeedRankBasics.Generates,
    Submodule.span_singleton_eq_top_iff]
  intro z
  exact ⟨z, by simp⟩

/-- Iterating `M_x` is exactly multiplication by the corresponding power of `x`. -/
theorem Mx_pow_apply (i : ℕ) (z : NormalForm k) :
    (Mx k ^ i) z =
      (algebraMap (Polynomial k) (NormalForm k) X) ^ i * z := by
  induction i generalizing z with
  | zero => simp
  | succ i ih =>
      rw [pow_succ, Module.End.mul_apply, ih, Mx_eq_multiplication]
      simp only [pow_succ, mul_assoc]

/-- Iterating `M_y` is exactly multiplication by the corresponding power of `y`. -/
theorem My_pow_apply (j : ℕ) (z : NormalForm k) :
    (My k ^ j) z = (y k) ^ j * z := by
  induction j generalizing z with
  | zero => simp
  | succ j ih =>
      rw [pow_succ, Module.End.mul_apply, ih, My_eq_multiplication]
      simp only [pow_succ, mul_assoc]

/--
The displayed address formula: applying `M_x^i M_y^j` to the unit seed gives
the quotient-ring monomial `x^i y^j`.
-/
theorem Mx_pow_My_pow_unitSeed (i j : ℕ) :
    ((Mx k ^ i) * (My k ^ j)) (1 : NormalForm k) =
      (algebraMap (Polynomial k) (NormalForm k) X) ^ i * (y k) ^ j := by
  rw [Module.End.mul_apply, Mx_pow_apply, My_pow_apply]
  simp only [mul_one]

/-- The displayed block-diagonal coefficient formula for `M_x`. -/
@[simp] theorem coefficientCoordinates_Mx (z : NormalForm k) :
    coefficientCoordinates k (Mx k z) =
      (X * z.re, X * z.im) := rfl

/-- The displayed off-diagonal coefficient formula for `M_y`. -/
@[simp] theorem coefficientCoordinates_My (z : NormalForm k) :
    coefficientCoordinates k (My k z) =
      (curveWeight k * z.im, z.re) := rfl

/-- The exact two-packet product law from the paper. -/
theorem product_normal_form
    (a0 a1 b0 b1 : Polynomial k) :
    (⟨a0, a1⟩ : NormalForm k) * ⟨b0, b1⟩ =
      ⟨a0 * b0 + curveWeight k * a1 * b1,
        a0 * b1 + a1 * b0⟩ := by
  apply QuadraticAlgebra.ext <;> simp

/-- The normal-form generator obeys `y^2 = x^3 - x`. -/
theorem y_sq :
    y k ^ 2 =
      (algebraMap (Polynomial k) (NormalForm k)) (curveWeight k) := by
  simpa [y, Algebra.smul_def] using
    (QuadraticAlgebra.omega_pow_two_eq_add
      (R := Polynomial k) (a := curveWeight k) (b := 0))

/-- The normal-form generator is a root of the quotient relation polynomial. -/
theorem relationPolynomial_eval_y :
    (relationPolynomial k).eval₂
      (algebraMap (Polynomial k) (NormalForm k)) (y k) = 0 := by
  rw [relationPolynomial, Polynomial.eval₂_sub, Polynomial.eval₂_pow,
    Polynomial.eval₂_X, Polynomial.eval₂_C, y_sq]
  exact sub_self _

/-- The quotient generator has square `x^3 - x`. -/
theorem quotient_root_sq :
    (AdjoinRoot.root (relationPolynomial k)) ^ 2 =
      (algebraMap (Polynomial k) (QuotientModel k)) (curveWeight k) := by
  have h := AdjoinRoot.eval₂_root (relationPolynomial k)
  rw [relationPolynomial, Polynomial.eval₂_sub, Polynomial.eval₂_pow,
    Polynomial.eval₂_X, Polynomial.eval₂_C] at h
  exact sub_eq_zero.mp h

/-- The quotient map sending its class of `y` to the normal-form generator. -/
def quotientToNormalForm :
    QuotientModel k →ₐ[Polynomial k] NormalForm k :=
  AdjoinRoot.liftAlgHom (relationPolynomial k)
    (Algebra.ofId (Polynomial k) (NormalForm k)) (y k)
    (relationPolynomial_eval_y k)

/-- The normal-form map sending its generator to the quotient class of `y`. -/
def normalFormToQuotient :
    NormalForm k →ₐ[Polynomial k] QuotientModel k :=
  QuadraticAlgebra.lift
    ⟨AdjoinRoot.root (relationPolynomial k), by
      rw [← pow_two, quotient_root_sq]
      simp [Algebra.smul_def]⟩

@[simp] theorem quotientToNormalForm_root :
    quotientToNormalForm k (AdjoinRoot.root (relationPolynomial k)) = y k := by
  exact AdjoinRoot.liftAlgHom_root _ _ _ _

@[simp] theorem normalFormToQuotient_y :
    normalFormToQuotient k (y k) =
      AdjoinRoot.root (relationPolynomial k) := by
  simp [normalFormToQuotient, y]

/--
The quotient presentation and the unique coefficient normal form are exactly
isomorphic as `k[x]`-algebras.
-/
def quotientNormalFormEquiv :
    QuotientModel k ≃ₐ[Polynomial k] NormalForm k where
  __ := quotientToNormalForm k
  invFun := normalFormToQuotient k
  left_inv q := by
    have hcomp :
        (normalFormToQuotient k).comp (quotientToNormalForm k) =
          AlgHom.id (Polynomial k) (QuotientModel k) := by
      apply AdjoinRoot.algHom_ext
      simp
    exact DFunLike.congr_fun hcomp q
  right_inv z := by
    have hcomp :
        (quotientToNormalForm k).comp (normalFormToQuotient k) =
          AlgHom.id (Polynomial k) (NormalForm k) := by
      apply QuadraticAlgebra.algHom_ext
      change quotientToNormalForm k (normalFormToQuotient k (y k)) = y k
      rw [normalFormToQuotient_y, quotientToNormalForm_root]
    exact DFunLike.congr_fun hcomp z

/--
The operator relation from the displayed elliptic example.  The characteristic
assumption is the paper's elliptic-curve hypothesis; the quotient identity
itself is valid more generally.
-/
theorem My_sq_eq_Mx_cube_sub_Mx
    (_hchar : (2 : k) ≠ 0) :
    My k ^ 2 = Mx k ^ 3 - Mx k := by
  apply LinearMap.ext
  intro z
  have hMy : (My k ^ 2) z =
      (⟨curveWeight k * z.re, curveWeight k * z.im⟩ : NormalForm k) := by
    rw [pow_two, Module.End.mul_apply]
    apply QuadraticAlgebra.ext <;> simp [My]
  have hMx : (Mx k ^ 3) z =
      (⟨X ^ 3 * z.re, X ^ 3 * z.im⟩ : NormalForm k) := by
    rw [show (3 : ℕ) = 2 + 1 by omega, pow_succ, pow_two,
      Module.End.mul_apply, Module.End.mul_apply]
    apply QuadraticAlgebra.ext <;> simp [Mx] <;> ring
  rw [hMy, LinearMap.sub_apply, hMx, Mx_apply]
  apply QuadraticAlgebra.ext
  · rw [QuadraticAlgebra.re_sub]
    simp [curveWeight]
    ring
  · rw [QuadraticAlgebra.im_sub]
    simp [curveWeight]
    ring

/-- In characteristic different from two, the displayed discriminant is nonzero. -/
theorem discriminant_ne_zero (hchar : (2 : k) ≠ 0) : (64 : k) ≠ 0 := by
  rw [show (64 : k) = (2 : k) ^ 6 by norm_num]
  exact pow_ne_zero 6 hchar

end

end EllipticCoordinates

/-! ## Orbit-hull closure algorithm -/

namespace FiniteAlgorithms

universe u v w x y

section OrbitHull

variable {k : Type u} {V : Type v} {ι : Type w}
variable [Field k] [AddCommGroup V] [Module k V] [Fintype ι]

/-- A subspace is invariant under every operator in the finite input family. -/
def InvariantUnder (operators : ι → Module.End k V) (W : Submodule k V) : Prop :=
  ∀ i, ∀ x ∈ W, operators i x ∈ W

/-- The least invariant subspace containing the input seed set. -/
def orbitHull (operators : ι → Module.End k V) (seeds : Set V) : Submodule k V :=
  sInf {W : Submodule k V | seeds ⊆ W ∧ InvariantUnder operators W}

theorem seeds_subset_orbitHull
    (operators : ι → Module.End k V) (seeds : Set V) :
    seeds ⊆ orbitHull operators seeds := by
  intro x hx
  apply (Submodule.mem_sInf).2
  intro W hW
  exact hW.1 hx

theorem orbitHull_invariant
    (operators : ι → Module.End k V) (seeds : Set V) :
    InvariantUnder operators (orbitHull operators seeds) := by
  intro i x hx
  apply (Submodule.mem_sInf).2
  intro W hW
  exact hW.2 i x ((sInf_le hW) hx)

theorem orbitHull_le
    (operators : ι → Module.End k V) (seeds : Set V)
    {W : Submodule k V} (hSeeds : seeds ⊆ W)
    (hInvariant : InvariantUnder operators W) :
    orbitHull operators seeds ≤ W := by
  exact sInf_le ⟨hSeeds, hInvariant⟩

/-- One closure pass: retain the old subspace and add all operator images. -/
def orbitClosureStep (operators : ι → Module.End k V)
    (W : Submodule k V) : Submodule k V :=
  W ⊔ ⨆ i, W.map (operators i)

theorem le_orbitClosureStep
    (operators : ι → Module.End k V) (W : Submodule k V) :
    W ≤ orbitClosureStep operators W :=
  le_sup_left

theorem orbitClosureStep_mono
    (operators : ι → Module.End k V) :
    Monotone (orbitClosureStep operators) := by
  intro W Z hWZ
  apply sup_le_sup hWZ
  exact iSup_mono fun i => Submodule.map_mono hWZ

/-- The successive finite closure passes, starting from the span of the seeds. -/
def orbitClosureIter (operators : ι → Module.End k V)
    (seeds : Set V) : ℕ → Submodule k V
  | 0 => Submodule.span k seeds
  | n + 1 => orbitClosureStep operators (orbitClosureIter operators seeds n)

theorem orbitClosureIter_le_succ
    (operators : ι → Module.End k V) (seeds : Set V) (n : ℕ) :
    orbitClosureIter operators seeds n ≤
      orbitClosureIter operators seeds (n + 1) := by
  exact le_orbitClosureStep operators _

theorem orbitClosureIter_monotone
    (operators : ι → Module.End k V) (seeds : Set V) :
    Monotone (orbitClosureIter operators seeds) := by
  exact monotone_nat_of_le_succ (orbitClosureIter_le_succ operators seeds)

/-- The closure iterates bundled as an ascending chain. -/
def orbitClosureChain (operators : ι → Module.End k V)
    (seeds : Set V) : ℕ →o Submodule k V where
  toFun := orbitClosureIter operators seeds
  monotone' := orbitClosureIter_monotone operators seeds

theorem seeds_subset_orbitClosureIter
    (operators : ι → Module.End k V) (seeds : Set V) (n : ℕ) :
    seeds ⊆ orbitClosureIter operators seeds n := by
  intro x hx
  exact (orbitClosureIter_monotone operators seeds (Nat.zero_le n))
    (Submodule.subset_span hx)

theorem orbitClosureIter_le_orbitHull
    (operators : ι → Module.End k V) (seeds : Set V) (n : ℕ) :
    orbitClosureIter operators seeds n ≤ orbitHull operators seeds := by
  induction n with
  | zero =>
      exact Submodule.span_le.mpr (seeds_subset_orbitHull operators seeds)
  | succ n ih =>
      rw [orbitClosureIter]
      apply sup_le ih
      refine iSup_le fun i => ?_
      rw [Submodule.map_le_iff_le_comap]
      intro x hx
      exact orbitHull_invariant operators seeds i x (ih hx)

theorem invariant_of_orbitClosureStep_eq
    (operators : ι → Module.End k V) {W : Submodule k V}
    (hStop : orbitClosureStep operators W = W) :
    InvariantUnder operators W := by
  intro i x hx
  rw [← hStop]
  exact ((le_iSup (fun j => W.map (operators j)) i).trans le_sup_right)
    ⟨x, hx, rfl⟩

/-- A stopped closure pass is exactly the operator hull. -/
theorem orbitClosureIter_eq_orbitHull_of_stop
    (operators : ι → Module.End k V) (seeds : Set V) (n : ℕ)
    (hStop : orbitClosureIter operators seeds (n + 1) =
      orbitClosureIter operators seeds n) :
    orbitClosureIter operators seeds n = orbitHull operators seeds := by
  apply le_antisymm
  · exact orbitClosureIter_le_orbitHull operators seeds n
  · apply orbitHull_le operators seeds
    · exact seeds_subset_orbitClosureIter operators seeds n
    · apply invariant_of_orbitClosureStep_eq operators
      simpa [orbitClosureIter] using hStop

/--
In finite dimension the ascending closure algorithm stops after finitely many
passes, and its stopped output is exactly the least invariant seed hull.
-/
theorem orbitHull_algorithm_terminates_and_correct
    [FiniteDimensional k V]
    (operators : ι → Module.End k V) (seeds : Set V) :
    ∃ n : ℕ,
      orbitClosureIter operators seeds (n + 1) =
        orbitClosureIter operators seeds n ∧
      orbitClosureIter operators seeds n = orbitHull operators seeds := by
  have hEventually := eventuallyConst_of_isNoetherian
    (orbitClosureChain operators seeds)
  rw [Filter.eventuallyConst_atTop] at hEventually
  obtain ⟨n, hn⟩ := hEventually
  have hStop : orbitClosureIter operators seeds (n + 1) =
      orbitClosureIter operators seeds n := by
    exact hn (n + 1) (Nat.le_succ n)
  exact ⟨n, hStop,
    orbitClosureIter_eq_orbitHull_of_stop operators seeds n hStop⟩

end OrbitHull

/-! ## Transfer-block algorithm -/

section TransferBlocks

variable {R : Type u} {M : Type v} {N : Type w}
variable {ι : Type x} {κ : Type y}
variable [Semiring R]
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable [Fintype ι] [Fintype κ]

/-- The finite table produced by the transfer-block algorithm. -/
def transferBlockTable
    (P : Foundation.LinearProjectorFamily R M ι)
    (Q : Foundation.LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) : κ → ι → (M →ₗ[R] N) :=
  fun j i => Foundation.transferBlock P Q T j i

/-- Reassemble a finite transfer-block table by summing every entry. -/
def assembleTransferBlockTable
    (B : κ → ι → (M →ₗ[R] N)) : M →ₗ[R] N :=
  ∑ j, ∑ i, B j i

/-- Correctness of the transfer-block algorithm: its table reconstructs `T`. -/
theorem transferBlock_algorithm_correct
    (P : Foundation.LinearProjectorFamily R M ι)
    (Q : Foundation.LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) :
    assembleTransferBlockTable (transferBlockTable P Q T) = T := by
  exact Foundation.transferBlock_reconstruction_linearMap P Q T

/-- The computed zero pattern is exactly the transfer graph by construction. -/
def transferGraph
    (P : Foundation.LinearProjectorFamily R M ι)
    (Q : Foundation.LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) : κ → ι → Prop :=
  fun j i => transferBlockTable P Q T j i ≠ 0

theorem transferGraph_iff_block_ne_zero
    (P : Foundation.LinearProjectorFamily R M ι)
    (Q : Foundation.LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) (j : κ) (i : ι) :
    transferGraph P Q T j i ↔
      Foundation.transferBlock P Q T j i ≠ 0 :=
  Iff.rfl

end TransferBlocks

/-! ## Exact graph spectral-rank algorithm -/

section GraphRank

open scoped Matrix
open Polynomial

variable {K : Type u} {ν : Type v}
variable [Field K] [Fintype ν] [DecidableEq ν]

/-- The exact finite spectrum of a square matrix. -/
noncomputable def graphSpectrum (A : Matrix ν ν K) : Finset K :=
  (Matrix.finite_spectrum A).toFinset

@[simp] theorem mem_graphSpectrum_iff (A : Matrix ν ν K) (μ : K) :
    μ ∈ graphSpectrum A ↔ μ ∈ spectrum K A := by
  classical
  simp [graphSpectrum]

/-- Exact geometric multiplicity of an eigenvalue. -/
noncomputable def graphEigenMultiplicity
    (A : Matrix ν ν K) (μ : K) : ℕ :=
  Module.finrank K (Module.End.eigenspace (Matrix.toLin' A) μ)

/--
The spectral computation in Paper I: take the maximum exact eigenspace
dimension over the finite spectrum, with value zero for the empty graph.
-/
noncomputable def exactGraphSeedRank (A : Matrix ν ν K) : ℕ :=
  (graphSpectrum A).sup (graphEigenMultiplicity A)

theorem graphEigenMultiplicity_le_exactGraphSeedRank
    (A : Matrix ν ν K) {μ : K} (hμ : μ ∈ spectrum K A) :
    graphEigenMultiplicity A μ ≤ exactGraphSeedRank A := by
  classical
  exact Finset.le_sup (s := graphSpectrum A)
    (f := graphEigenMultiplicity A) ((mem_graphSpectrum_iff A μ).2 hμ)

/--
End-to-end correctness from exact spectral certificates.  The eigenbasis and
Lagrange-projector data prove that `R` is the least number of operator seeds;
the coverage and dimension certificates prove that the finite-spectrum
maximum computed above is exactly that same `R`.
-/
theorem exactGraphSeedRank_isLeast
    {Λ : Type w} [Fintype Λ]
    (A : Matrix ν ν K) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → K)
    (eigenbasis :
      Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) K (ν → K))
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      Matrix.toLin' A (eigenbasis z) = eigenvalue z.1 • eigenbasis z)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (projectorPolynomial : Λ → K[X])
    (hproject : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      aeval (Matrix.toLin' A) (projectorPolynomial eigen)
        (SingleOperatorGraph.paddedBlockSum R multiplicity
          (fun e j ↦ eigenbasis ⟨e, j⟩)
          ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
        eigenbasis ⟨eigen, j⟩)
    (hSpectrumCover : ∀ μ ∈ spectrum K A, ∃ eigen, eigenvalue eigen = μ)
    (hMultiplicity : ∀ eigen,
      graphEigenMultiplicity A (eigenvalue eigen) = multiplicity eigen)
    (hMaxSpectrum : eigenvalue maxEigen ∈ spectrum K A) :
    IsLeast
      {r : ℕ | SingleOperatorGraph.SeedNumberLE (Matrix.toLin' A) r}
      (exactGraphSeedRank A) := by
  classical
  have hLeast :
      IsLeast
        {r : ℕ | SingleOperatorGraph.SeedNumberLE (Matrix.toLin' A) r} R :=
    SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity
      (Matrix.toLin' A) R multiplicity eigenvalue eigenbasis hEigen
      hbound maxEigen hmax projectorPolynomial hproject
  have hComputed : exactGraphSeedRank A = R := by
    apply Nat.le_antisymm
    · apply Finset.sup_le
      intro μ hμ
      have hμSpectrum : μ ∈ spectrum K A :=
        (mem_graphSpectrum_iff A μ).1 hμ
      obtain ⟨eigen, heigen⟩ := hSpectrumCover μ hμSpectrum
      rw [← heigen, hMultiplicity]
      exact hbound eigen
    · rw [← hmax, ← hMultiplicity maxEigen]
      exact Finset.le_sup
        ((mem_graphSpectrum_iff A (eigenvalue maxEigen)).2 hMaxSpectrum)
  rw [hComputed]
  exact hLeast

end GraphRank

end FiniteAlgorithms

end Komorebi

#print axioms Komorebi.EllipticCoordinates.My_sq_eq_Mx_cube_sub_Mx
#print axioms Komorebi.EllipticCoordinates.unitSeed_generates
#print axioms Komorebi.EllipticCoordinates.Mx_pow_My_pow_unitSeed
#print axioms Komorebi.FiniteAlgorithms.orbitHull_algorithm_terminates_and_correct
#print axioms Komorebi.FiniteAlgorithms.transferBlock_algorithm_correct
#print axioms Komorebi.FiniteAlgorithms.exactGraphSeedRank_isLeast
