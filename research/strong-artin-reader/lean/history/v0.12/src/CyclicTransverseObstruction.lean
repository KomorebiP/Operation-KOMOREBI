import CyclicDefectAlgebra
import Mathlib.Algebra.Module.LinearMap.Defs
import Mathlib.Algebra.Polynomial.Derivative
import Mathlib.LinearAlgebra.Prod
import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

namespace Komorebi.StrongArtin.CyclicTransverseObstruction

open Polynomial
open Komorebi.StrongArtin.CyclicDefect

noncomputable section

variable {k C T COut TOut : Type*}
  [Field k]
  [AddCommGroup C] [Module k C]
  [AddCommGroup T] [Module k T]
  [AddCommGroup COut] [Module k COut]
  [AddCommGroup TOut] [Module k TOut]

/-- Block-diagonal residual Jacobian after the known cyclic defect direction has
been separated from the transverse deformation directions. -/
def blockJacobian (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut) :
    (C × T) →ₗ[k] (COut × TOut) where
  toFun x := (Jcyc x.1, Jperp x.2)
  map_add' x y := by simp
  map_smul' a x := by simp

@[simp] theorem blockJacobian_apply (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (x : C × T) :
    blockJacobian Jcyc Jperp x = (Jcyc x.1, Jperp x.2) := rfl

/-- If the transverse Jacobian is surjective, solving the complete first-order
correction equation is equivalent to solving only its cyclic component. This is
the exact algebraic form of "kill the transverse obstruction and retain the
known cyclic defect". -/
theorem exists_block_correction_iff_exists_cyclic
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) (b : COut × TOut) :
    (∃ x : C × T, blockJacobian Jcyc Jperp x = b) ↔
      ∃ c : C, Jcyc c = b.1 := by
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨x.1, ?_⟩
    have h := congrArg Prod.fst hx
    simpa [blockJacobian] using h
  · rintro ⟨c, hc⟩
    rcases hperp b.2 with ⟨t, ht⟩
    refine ⟨(c, t), ?_⟩
    exact Prod.ext hc ht

/-- In the quotient-prime special fiber the cyclic relation has zero linearized
Jacobian. Once all transverse directions are surjective, a first-order
correction exists exactly when the cyclic residual component is already zero.
The cyclic direction is therefore retained rather than repaired linearly. -/
theorem exists_block_correction_iff_cyclic_residual_zero
    (Jperp : T →ₗ[k] TOut) (hperp : Function.Surjective Jperp)
    (b : COut × TOut) :
    (∃ x : C × T,
        blockJacobian (0 : C →ₗ[k] COut) Jperp x = b) ↔ b.1 = 0 := by
  rw [exists_block_correction_iff_exists_cyclic
    (Jcyc := (0 : C →ₗ[k] COut)) (Jperp := Jperp) hperp b]
  constructor
  · rintro ⟨c, hc⟩
    simpa using hc.symm
  · intro hb
    exact ⟨0, by simp [hb]⟩

/-- With the transverse block already surjective, the total block Jacobian is
surjective exactly when the cyclic block is. In particular the only possible
first-order failure of smoothness lies in the retained cyclic factor. -/
theorem blockJacobian_surjective_iff_cyclic_surjective
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) :
    Function.Surjective (blockJacobian Jcyc Jperp) ↔
      Function.Surjective Jcyc := by
  constructor
  · intro htot y
    rcases htot (y, 0) with ⟨x, hx⟩
    refine ⟨x.1, ?_⟩
    have h := congrArg Prod.fst hx
    simpa [blockJacobian] using h
  · intro hcyc b
    rcases hcyc b.1 with ⟨c, hc⟩
    rcases hperp b.2 with ⟨t, ht⟩
    exact ⟨(c, t), Prod.ext hc ht⟩


/-- The one-step linearized lifting obstruction attached to a residual vector
`q`: its class in the cokernel of the residual Jacobian. -/
def obstructionClass {U V : Type*} [AddCommGroup U] [Module k U]
    [AddCommGroup V] [Module k V] (J : U →ₗ[k] V) (q : V) :
    V ⧸ LinearMap.range J :=
  (LinearMap.range J).mkQ q

/-- The obstruction class vanishes exactly when the residual vector lies in the
Jacobian image. This is the linear-algebra core of the one-step Hecke lifting
criterion. -/
theorem obstructionClass_eq_zero_iff_mem_range
    {U V : Type*} [AddCommGroup U] [Module k U]
    [AddCommGroup V] [Module k V] (J : U →ₗ[k] V) (q : V) :
    obstructionClass J q = 0 ↔ q ∈ LinearMap.range J := by
  change (LinearMap.range J).mkQ q = 0 ↔ q ∈ LinearMap.range J
  rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]

/-- Equivalently, the obstruction vanishes exactly when a first-order
correction can cancel the residual vector. -/
theorem obstructionClass_eq_zero_iff_exists_correction
    {U V : Type*} [AddCommGroup U] [Module k U]
    [AddCommGroup V] [Module k V] (J : U →ₗ[k] V) (q : V) :
    obstructionClass J q = 0 ↔ ∃ u : U, q + J u = 0 := by
  rw [obstructionClass_eq_zero_iff_mem_range]
  constructor
  · rintro ⟨u, hu⟩
    refine ⟨-u, ?_⟩
    rw [map_neg, hu]
    exact add_neg_cancel q
  · rintro ⟨u, hu⟩
    refine ⟨-u, ?_⟩
    rw [map_neg]
    exact (eq_neg_of_add_eq_zero_left hu).symm

/-- Projection of a full residual equation to the obstruction quotient of the
cyclic block. The transverse coordinate is forgotten. -/
def cyclicCokerProjection (Jcyc : C →ₗ[k] COut) :
    (COut × TOut) →ₗ[k] (COut ⧸ LinearMap.range Jcyc) :=
  (LinearMap.range Jcyc).mkQ.comp (LinearMap.fst k COut TOut)

@[simp] theorem cyclicCokerProjection_apply (Jcyc : C →ₗ[k] COut)
    (b : COut × TOut) :
    cyclicCokerProjection (TOut := TOut) Jcyc b =
      (LinearMap.range Jcyc).mkQ b.1 := rfl

/-- The cyclic-cokernel projection is always surjective. -/
theorem cyclicCokerProjection_surjective (Jcyc : C →ₗ[k] COut) :
    Function.Surjective (cyclicCokerProjection (TOut := TOut) Jcyc) := by
  intro y
  rcases (LinearMap.range Jcyc).mkQ_surjective y with ⟨c, hc⟩
  refine ⟨(c, 0), ?_⟩
  simpa [cyclicCokerProjection] using hc

/-- If the transverse Jacobian is surjective, the kernel of the obstruction
projection is exactly the range of the total block Jacobian. Hence no
transverse obstruction class survives in the cokernel. -/
theorem ker_cyclicCokerProjection_eq_range_blockJacobian
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) :
    LinearMap.ker (cyclicCokerProjection (TOut := TOut) Jcyc) =
      LinearMap.range (blockJacobian Jcyc Jperp) := by
  ext b
  constructor
  · intro hb
    have hb0 : (LinearMap.range Jcyc).mkQ b.1 = 0 := by
      simpa [LinearMap.mem_ker, cyclicCokerProjection] using hb
    have hcyc : b.1 ∈ LinearMap.range Jcyc := by
      simpa [Submodule.Quotient.mk_eq_zero] using hb0
    rcases hcyc with ⟨c, hc⟩
    rcases hperp b.2 with ⟨t, ht⟩
    refine ⟨(c, t), ?_⟩
    exact Prod.ext hc ht
  · rintro ⟨x, rfl⟩
    change cyclicCokerProjection (TOut := TOut) Jcyc
      (blockJacobian Jcyc Jperp x) = 0
    change (LinearMap.range Jcyc).mkQ (Jcyc x.1) = 0
    rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
    exact ⟨x.1, rfl⟩

/-- Under transverse surjectivity, the complete one-step obstruction vanishes
if and only if the cyclic obstruction vanishes. This is the exact obstruction
bookkeeping needed for cyclic-relative finite-depth lifting. -/
theorem blockObstruction_eq_zero_iff_cyclicObstruction_eq_zero
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) (b : COut × TOut) :
    obstructionClass (blockJacobian Jcyc Jperp) b = 0 ↔
      obstructionClass Jcyc b.1 = 0 := by
  rw [obstructionClass_eq_zero_iff_mem_range, obstructionClass_eq_zero_iff_mem_range]
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨x.1, ?_⟩
    have h := congrArg Prod.fst hx
    simpa [blockJacobian] using h
  · rintro ⟨c, hc⟩
    rcases hperp b.2 with ⟨t, ht⟩
    exact ⟨(c, t), Prod.ext hc ht⟩

/-- At the quotient-prime special fiber the cyclic Jacobian is zero. Therefore,
after all transverse directions are made surjective, the complete first-order
obstruction vanishes exactly when the cyclic residual coordinate itself is zero. -/
theorem quotientPrime_blockObstruction_eq_zero_iff_cyclicResidual_zero
    (Jperp : T →ₗ[k] TOut) (hperp : Function.Surjective Jperp)
    (b : COut × TOut) :
    obstructionClass (blockJacobian (0 : C →ₗ[k] COut) Jperp) b = 0 ↔
      b.1 = 0 := by
  rw [blockObstruction_eq_zero_iff_cyclicObstruction_eq_zero
    (Jcyc := (0 : C →ₗ[k] COut)) (Jperp := Jperp) hperp b]
  rw [obstructionClass_eq_zero_iff_mem_range]
  simp

/-- Canonical obstruction-space reduction. If the transverse Jacobian is
surjective, the cokernel of the full block Jacobian is linearly equivalent to
the cokernel of the cyclic block alone. This is the quotient-level version of
`exists_block_correction_iff_exists_cyclic`. -/
noncomputable def blockCokerEquivCyclicCoker
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) :
    ((COut × TOut) ⧸ LinearMap.range (blockJacobian Jcyc Jperp)) ≃ₗ[k]
      (COut ⧸ LinearMap.range Jcyc) :=
  (Submodule.quotEquivOfEq
      (LinearMap.range (blockJacobian Jcyc Jperp))
      (LinearMap.ker (cyclicCokerProjection (TOut := TOut) Jcyc))
      (ker_cyclicCokerProjection_eq_range_blockJacobian Jcyc Jperp hperp).symm).trans
    ((cyclicCokerProjection (TOut := TOut) Jcyc).quotKerEquivOfSurjective
      (cyclicCokerProjection_surjective (TOut := TOut) Jcyc))

/-- In the quotient-prime case, where the cyclic Jacobian is zero, the entire
first-order obstruction space is canonically the cyclic output space itself.
All transverse obstruction classes disappear under transverse surjectivity. -/
noncomputable def blockCokerEquivCyclicOutputOfZero
    (Jperp : T →ₗ[k] TOut) (hperp : Function.Surjective Jperp) :
    ((COut × TOut) ⧸ LinearMap.range
      (blockJacobian (0 : C →ₗ[k] COut) Jperp)) ≃ₗ[k] COut :=
  (blockCokerEquivCyclicCoker (Jcyc := (0 : C →ₗ[k] COut))
      (Jperp := Jperp) hperp).trans
    ((Submodule.quotEquivOfEq
        (LinearMap.range (0 : C →ₗ[k] COut)) (⊥ : Submodule k COut) (by simp)).trans
      ((⊥ : Submodule k COut).quotEquivOfEqBot rfl))


/-- Finite-dimensional form of the obstruction reduction: after transverse
surjectivity, the number of surviving first-order obstruction directions is
exactly the dimension of the cyclic cokernel. -/
theorem finrank_blockCoker_eq_finrank_cyclicCoker
    [FiniteDimensional k COut] [FiniteDimensional k TOut]
    (Jcyc : C →ₗ[k] COut) (Jperp : T →ₗ[k] TOut)
    (hperp : Function.Surjective Jperp) :
    Module.finrank k
        ((COut × TOut) ⧸ LinearMap.range (blockJacobian Jcyc Jperp)) =
      Module.finrank k (COut ⧸ LinearMap.range Jcyc) :=
  LinearEquiv.finrank_eq (blockCokerEquivCyclicCoker Jcyc Jperp hperp)

/-- For one scalar cyclic equation and a surjective transverse Jacobian, the
full first-order obstruction space has dimension exactly one. This is the
formal "one retained cyclic defect direction" statement used by the relative
patching strategy. -/
theorem finrank_blockCoker_eq_one_of_scalar_cyclic
    [FiniteDimensional k TOut]
    (Jperp : T →ₗ[k] TOut) (hperp : Function.Surjective Jperp) :
    Module.finrank k
        ((k × TOut) ⧸ LinearMap.range
          (blockJacobian (0 : k →ₗ[k] k) Jperp)) = 1 := by
  have h := LinearEquiv.finrank_eq
    (blockCokerEquivCyclicOutputOfZero (C := k) (COut := k) Jperp hperp)
  simpa using h

/-- The quotient-prime cyclic defect is maximally singular to first order:
after reduction to `F_p`, the derivative of `(1+X)^p-1 = X^p` vanishes
identically. This is the precise reason ordinary Jacobian smoothness cannot be
asked to remove this direction. -/
theorem derivative_defectPolynomial_zmod_eq_zero (p : ℕ) [Fact p.Prime] :
    derivative (defectPolynomial p (ZMod p)) = 0 := by
  rw [defectPolynomial_zmod_eq_X_pow]
  rw [derivative_X_pow]
  simp

end
end Komorebi.StrongArtin.CyclicTransverseObstruction

#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.exists_block_correction_iff_exists_cyclic
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.exists_block_correction_iff_cyclic_residual_zero
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.blockJacobian_surjective_iff_cyclic_surjective
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.derivative_defectPolynomial_zmod_eq_zero

#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.ker_cyclicCokerProjection_eq_range_blockJacobian
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.blockCokerEquivCyclicCoker
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.blockCokerEquivCyclicOutputOfZero

#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.finrank_blockCoker_eq_finrank_cyclicCoker
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.finrank_blockCoker_eq_one_of_scalar_cyclic

#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.obstructionClass_eq_zero_iff_exists_correction
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.blockObstruction_eq_zero_iff_cyclicObstruction_eq_zero
#print axioms Komorebi.StrongArtin.CyclicTransverseObstruction.quotientPrime_blockObstruction_eq_zero_iff_cyclicResidual_zero
