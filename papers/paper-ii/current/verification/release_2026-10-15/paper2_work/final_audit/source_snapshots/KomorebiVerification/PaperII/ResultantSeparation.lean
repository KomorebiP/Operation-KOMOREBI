/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Algebra.Order.Floor.Div
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.List.OfFn
import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.Finset.NatAntidiagonal
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.RingTheory.PowerSeries.Inverse
import Mathlib.Analysis.Normed.Ring.Basic
import Mathlib.Tactic.NoncommRing
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Tactic.Abel
import Mathlib.Util.AssertNoSorry
import Mathlib.Analysis.Complex.Exponential
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.RingTheory.RootsOfUnity.PrimitiveRoots
import Mathlib.Data.Nat.ChineseRemainder
import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.NumberTheory.Padics.PadicVal.Basic
import Mathlib.RingTheory.Polynomial.Resultant.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Push
import Mathlib.Tactic.ByContra
import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.FunProp

/-!
# Paper II: evaluated Bezout separation and precision delay

Author: Komorebi P.

This file starts with evaluated endomorphism certificates.  It does not construct polynomial
resultants, and it does not promote nilpotence on a primary summand to exact kernel action.  The
identity and zero actions below follow only from the displayed Bezout and annihilation equations.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.ResultantSeparation

universe u v

variable {K : Type u} {M : Type v}
variable [Field K] [AddCommGroup M] [Module K M]

abbrev End := Module.End K M

/-! ## Evaluated certificate and its numerator -/

/-- The certificate obtained after evaluating a Bezout identity at an operator.

All four supplied endomorphisms are required to commute, `UF + VG = rI` is recorded verbatim,
and `FG = 0` is a separate certificate.  In particular, no resultant construction or
nilpotence-to-kernel inference is hidden in this structure.
-/
structure EvaluatedBezoutCertificate (F G U V : End (K := K) (M := M)) (r : K) : Prop where
  r_ne_zero : r ≠ 0
  commute_FG : Commute F G
  commute_FU : Commute F U
  commute_FV : Commute F V
  commute_GU : Commute G U
  commute_GV : Commute G V
  commute_UV : Commute U V
  bezout : U * F + V * G = r • (1 : End (K := K) (M := M))
  annihilate : F * G = 0

/-- The integral numerator `VG` of the evaluated separator. -/
def separatorNumerator (V G : End (K := K) (M := M)) : End (K := K) (M := M) :=
  V * G

/-- The rational separator `r⁻¹ VG`. -/
def separator (r : K) (V G : End (K := K) (M := M)) : End (K := K) (M := M) :=
  r⁻¹ • separatorNumerator V G

variable {F G U V : End (K := K) (M := M)} {r : K}

/-- Minimal form of the numerator identity: only the evaluated Bezout equality is needed. -/
theorem separatorNumerator_eq_scalar_sub_of_bezout
    (bezout : U * F + V * G = r • (1 : End (K := K) (M := M))) :
    separatorNumerator V G = r • (1 : End (K := K) (M := M)) - U * F := by
  apply (eq_sub_iff_add_eq).2
  simpa only [separatorNumerator, add_comm] using bezout

/-- The numerator is also `rI - UF`, directly from the evaluated Bezout identity. -/
theorem separatorNumerator_eq_scalar_sub
    (certificate : EvaluatedBezoutCertificate F G U V r) :
    separatorNumerator V G = r • (1 : End (K := K) (M := M)) - U * F := by
  exact separatorNumerator_eq_scalar_sub_of_bezout certificate.bezout

/-- Minimal form of cross-term vanishing.  Among the six commutation fields in the bundled
certificate, only `FG = GF` and `GU = UG` enter this calculation. -/
theorem separatorNumerator_mul_complement_eq_zero_of_commute
    (commute_FG : Commute F G) (commute_GU : Commute G U) (annihilate : F * G = 0) :
    separatorNumerator V G * (U * F) = 0 := by
  calc
    separatorNumerator V G * (U * F) = V * (G * U) * F := by
      simp only [separatorNumerator, mul_assoc]
    _ = V * (U * G) * F := by rw [commute_GU.eq]
    _ = (V * U) * (G * F) := by simp only [mul_assoc]
    _ = (V * U) * (F * G) := by rw [← commute_FG.eq]
    _ = 0 := by rw [annihilate, mul_zero]

/-- The cross term which occurs in the numerator-square calculation vanishes. -/
theorem separatorNumerator_mul_complement_eq_zero
    (certificate : EvaluatedBezoutCertificate F G U V r) :
    separatorNumerator V G * (U * F) = 0 := by
  exact separatorNumerator_mul_complement_eq_zero_of_commute
    certificate.commute_FG certificate.commute_GU certificate.annihilate

/-- Minimal denominator-free quasi-idempotence theorem.  It requires neither `r ≠ 0` nor the
four commutation relations unused by the numerator-square calculation. -/
theorem separatorNumerator_mul_self_of_bezout
    (bezout : U * F + V * G = r • (1 : End (K := K) (M := M)))
    (commute_FG : Commute F G) (commute_GU : Commute G U) (annihilate : F * G = 0) :
    separatorNumerator V G * separatorNumerator V G = r • separatorNumerator V G := by
  calc
    separatorNumerator V G * separatorNumerator V G =
        separatorNumerator V G *
          (r • (1 : End (K := K) (M := M)) - U * F) := by
            exact congrArg (separatorNumerator V G * ·)
              (separatorNumerator_eq_scalar_sub_of_bezout bezout)
    _ = separatorNumerator V G * (r • (1 : End (K := K) (M := M))) -
          separatorNumerator V G * (U * F) := by rw [mul_sub]
    _ = r • separatorNumerator V G := by
      rw [separatorNumerator_mul_complement_eq_zero_of_commute
        commute_FG commute_GU annihilate]
      simp only [sub_zero, mul_smul_comm, mul_one]

/-- The denominator-free numerator identity `N² = rN`. -/
theorem separatorNumerator_mul_self
    (certificate : EvaluatedBezoutCertificate F G U V r) :
    separatorNumerator V G * separatorNumerator V G = r • separatorNumerator V G := by
  exact separatorNumerator_mul_self_of_bezout certificate.bezout certificate.commute_FG
    certificate.commute_GU certificate.annihilate

/-- Minimal idempotence theorem for the normalized separator. -/
theorem separator_idempotent_of_bezout
    (r_ne_zero : r ≠ 0)
    (bezout : U * F + V * G = r • (1 : End (K := K) (M := M)))
    (commute_FG : Commute F G) (commute_GU : Commute G U) (annihilate : F * G = 0) :
    separator r V G * separator r V G = separator r V G := by
  rw [separator, smul_mul_smul,
    separatorNumerator_mul_self_of_bezout bezout commute_FG commute_GU annihilate]
  rw [smul_smul]
  apply congrArg (fun a : K => a • separatorNumerator V G)
  field_simp [r_ne_zero]

/-- The evaluated separator is idempotent. -/
theorem separator_idempotent
    (certificate : EvaluatedBezoutCertificate F G U V r) :
    separator r V G * separator r V G = separator r V G := by
  exact separator_idempotent_of_bezout certificate.r_ne_zero certificate.bezout
    certificate.commute_FG certificate.commute_GU certificate.annihilate

/-! ## Exact action on the two certified kernels -/

/-- Minimal kernel-action theorem: evaluated Bezout alone makes the numerator act by `r` on
`ker F`. -/
theorem separatorNumerator_apply_of_mem_ker_F_of_bezout
    (bezout : U * F + V * G = r • (1 : End (K := K) (M := M))) {x : M}
    (hx : x ∈ LinearMap.ker F) :
    separatorNumerator V G x = r • x := by
  change F x = 0 at hx
  have h := LinearMap.congr_fun bezout x
  simpa [separatorNumerator, hx] using h

/-- On the exact kernel of `F`, the numerator acts by the scalar `r`. -/
theorem separatorNumerator_apply_of_mem_ker_F
    (certificate : EvaluatedBezoutCertificate F G U V r) {x : M}
    (hx : x ∈ LinearMap.ker F) :
    separatorNumerator V G x = r • x := by
  exact separatorNumerator_apply_of_mem_ker_F_of_bezout certificate.bezout hx

/-- Minimal normalized kernel-action theorem. -/
theorem separator_apply_of_mem_ker_F_of_bezout
    (r_ne_zero : r ≠ 0)
    (bezout : U * F + V * G = r • (1 : End (K := K) (M := M))) {x : M}
    (hx : x ∈ LinearMap.ker F) :
    separator r V G x = x := by
  rw [separator, LinearMap.smul_apply,
    separatorNumerator_apply_of_mem_ker_F_of_bezout bezout hx]
  simp [smul_smul, r_ne_zero]

/-- The separator is exactly the identity on `ker F`. -/
theorem separator_apply_of_mem_ker_F
    (certificate : EvaluatedBezoutCertificate F G U V r) {x : M}
    (hx : x ∈ LinearMap.ker F) :
    separator r V G x = x := by
  exact separator_apply_of_mem_ker_F_of_bezout certificate.r_ne_zero certificate.bezout hx

/-- The numerator vanishes on `ker G`. -/
theorem separatorNumerator_apply_of_mem_ker_G
    {x : M} (hx : x ∈ LinearMap.ker G) :
    separatorNumerator V G x = 0 := by
  change G x = 0 at hx
  simp [separatorNumerator, hx]

/-- The separator is exactly zero on `ker G`. -/
theorem separator_apply_of_mem_ker_G
    {x : M} (hx : x ∈ LinearMap.ker G) :
    separator r V G x = 0 := by
  simp [separator, separatorNumerator_apply_of_mem_ker_G hx]

/-! ## Lattice preservation and denominator certificates -/

/-- An endomorphism preserves the chosen additive lattice. -/
def PreservesLattice (T : End (K := K) (M := M)) (lattice : AddSubgroup M) : Prop :=
  ∀ x : M, x ∈ lattice → T x ∈ lattice

/-- A scalar preserves the chosen additive lattice.  This is deliberately explicit: when `K` is
a fraction field, algebraic invertibility in `K` alone does not imply preservation of a chosen
valuation lattice. -/
def ScalarPreservesLattice (a : K) (lattice : AddSubgroup M) : Prop :=
  ∀ x : M, x ∈ lattice → a • x ∈ lattice

/-- A field unit acts as an automorphism of the chosen lattice: both it and its inverse preserve
the lattice.  This is the precise lattice condition needed for unit factors in a denominator. -/
def IsLatticeUnit (u : Kˣ) (lattice : AddSubgroup M) : Prop :=
  ScalarPreservesLattice (u : K) lattice ∧ ScalarPreservesLattice (↑(u⁻¹) : K) lattice

/-- Multiplicative closure of lattice preservation under composition. -/
theorem PreservesLattice.mul {S T : End (K := K) (M := M)} {lattice : AddSubgroup M}
    (hS : PreservesLattice S lattice) (hT : PreservesLattice T lattice) :
    PreservesLattice (S * T) lattice := by
  intro x hx
  exact hS (T x) (hT x hx)

/-- Multiplying a lattice-preserving endomorphism by a lattice-preserving scalar preserves the
lattice. -/
theorem ScalarPreservesLattice.smul {a : K} {T : End (K := K) (M := M)}
    {lattice : AddSubgroup M} (ha : ScalarPreservesLattice a lattice)
    (hT : PreservesLattice T lattice) :
    PreservesLattice (a • T) lattice := by
  intro x hx
  rw [LinearMap.smul_apply]
  exact ha (T x) (hT x hx)

/-- Lattice-preserving scalars are closed under multiplication. -/
theorem ScalarPreservesLattice.mul {a b : K} {lattice : AddSubgroup M}
    (ha : ScalarPreservesLattice a lattice)
    (hb : ScalarPreservesLattice b lattice) :
    ScalarPreservesLattice (a * b) lattice := by
  intro x hx
  rw [mul_smul]
  exact ha (b • x) (hb x hx)

/-- Every power of a lattice-preserving scalar preserves the lattice. -/
theorem ScalarPreservesLattice.pow {a : K} {lattice : AddSubgroup M}
    (ha : ScalarPreservesLattice a lattice) :
    ∀ n : ℕ, ScalarPreservesLattice (a ^ n) lattice := by
  intro n
  induction n with
  | zero =>
      intro x hx
      simpa using hx
  | succ n ih =>
      simpa [pow_succ] using ih.mul ha

/-- Lattice units are closed under inversion. -/
theorem IsLatticeUnit.inv {u : Kˣ} {lattice : AddSubgroup M}
    (hu : IsLatticeUnit u lattice) :
    IsLatticeUnit u⁻¹ lattice := by
  constructor
  · exact hu.2
  · simpa using hu.1

/-- If `V` and `G` preserve the lattice, so does the numerator `VG`. -/
theorem separatorNumerator_preservesLattice {lattice : AddSubgroup M}
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    PreservesLattice (separatorNumerator V G) lattice := by
  exact hV.mul hG

/-- Clearing the displayed nonzero denominator recovers the numerator exactly. -/
theorem scalar_mul_separator_of_ne_zero (r_ne_zero : r ≠ 0) :
    r • separator r V G = separatorNumerator V G := by
  simp [separator, smul_smul, r_ne_zero]

/-- Clearing the displayed nonzero denominator recovers the numerator exactly. -/
theorem scalar_mul_separator
    (certificate : EvaluatedBezoutCertificate F G U V r) :
    r • separator r V G = separatorNumerator V G := by
  exact scalar_mul_separator_of_ne_zero certificate.r_ne_zero

/-- Lattice form of denominator clearing: preservation of `V` and `G` certifies preservation of
`rE`. -/
theorem scalar_mul_separator_preservesLattice_of_ne_zero
    (r_ne_zero : r ≠ 0) {lattice : AddSubgroup M}
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    PreservesLattice (r • separator r V G) lattice := by
  rw [scalar_mul_separator_of_ne_zero r_ne_zero]
  exact separatorNumerator_preservesLattice hV hG

/-- Lattice form of denominator clearing, as a wrapper around the minimal nonvanishing theorem. -/
theorem scalar_mul_separator_preservesLattice
    (certificate : EvaluatedBezoutCertificate F G U V r) {lattice : AddSubgroup M}
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    PreservesLattice (r • separator r V G) lattice := by
  exact scalar_mul_separator_preservesLattice_of_ne_zero certificate.r_ne_zero hV hG

/-- If `r = uπ^s`, then clearing only the uniformizer power leaves the inverse unit factor:
`π^s E = u⁻¹ N`.  No lattice hypothesis is needed for this algebraic identity. -/
theorem pow_smul_separator_eq_unit_inv_smul_separatorNumerator_of_ne_zero
    (r_ne_zero : r ≠ 0) {pi : K} {s : ℕ} (u : Kˣ)
    (hr : (u : K) * pi ^ s = r) :
    (pi ^ s) • separator r V G = (↑(u⁻¹) : K) • separatorNumerator V G := by
  have hpow : pi ^ s ≠ 0 := by
    intro h
    apply r_ne_zero
    rw [← hr, h, mul_zero]
  rw [separator, smul_smul]
  apply congrArg (fun a : K ↦ a • separatorNumerator V G)
  rw [← hr]
  field_simp [hpow]
  exact u.mul_inv.symm

/-- Certificate wrapper for unit-aware algebraic denominator clearing. -/
theorem pow_smul_separator_eq_unit_inv_smul_separatorNumerator
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} (u : Kˣ)
    (hr : (u : K) * pi ^ s = r) :
    (pi ^ s) • separator r V G = (↑(u⁻¹) : K) • separatorNumerator V G := by
  exact pow_smul_separator_eq_unit_inv_smul_separatorNumerator_of_ne_zero
    certificate.r_ne_zero u hr

/-- A finite certificate that `s` powers of `pi` clear a projector on a lattice. -/
def IsSeparationWeight (pi : K) (E : End (K := K) (M := M))
    (lattice : AddSubgroup M) (s : ℕ) : Prop :=
  PreservesLattice ((pi ^ s) • E) lattice

/-- Clearing exponents are upward closed whenever the uniformizer scalar preserves the lattice. -/
theorem IsSeparationWeight.mono {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} {s t : ℕ}
    (hs : IsSeparationWeight pi E lattice s) (hst : s ≤ t)
    (hpi : ScalarPreservesLattice pi lattice) :
    IsSeparationWeight pi E lattice t := by
  rw [IsSeparationWeight] at hs ⊢
  have hpow : pi ^ t = pi ^ (t - s) * pi ^ s := by
    rw [← pow_add, Nat.sub_add_cancel hst]
  rw [hpow, mul_smul]
  exact (hpi.pow (t - s)).smul hs

/-- Existence of a finite separation weight is kept as explicit data. -/
structure FiniteSeparationWeight (pi : K) (E : End (K := K) (M := M))
    (lattice : AddSubgroup M) where
  weight : ℕ
  clears : IsSeparationWeight pi E lattice weight

/-- Propositional form of finiteness, used to define the actual least separation weight. -/
def HasFiniteSeparationWeight (pi : K) (E : End (K := K) (M := M))
    (lattice : AddSubgroup M) : Prop :=
  ∃ s : ℕ, IsSeparationWeight pi E lattice s

/-- A bundled finite certificate supplies the corresponding existence proof. -/
theorem FiniteSeparationWeight.exists {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} (certificate : FiniteSeparationWeight pi E lattice) :
    HasFiniteSeparationWeight pi E lattice :=
  ⟨certificate.weight, certificate.clears⟩

/-- The actual separation weight: the least natural exponent which clears the projector on the
lattice.  Its existence proof is explicit and `Nat.find` performs only the well-ordering step. -/
noncomputable def separationWeight {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} (finite : HasFiniteSeparationWeight pi E lattice) : ℕ :=
  by
    classical
    exact Nat.find finite

/-- The least separation weight really clears the projector. -/
theorem separationWeight_clears {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} (finite : HasFiniteSeparationWeight pi E lattice) :
    IsSeparationWeight pi E lattice (separationWeight finite) := by
  classical
  exact Nat.find_spec finite

/-- Minimality, equivalently the abstract upper-bound rule: every supplied clearing exponent bounds
the actual separation weight from above. -/
theorem separationWeight_le_of_clears {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} (finite : HasFiniteSeparationWeight pi E lattice)
    {s : ℕ} (hs : IsSeparationWeight pi E lattice s) :
    separationWeight finite ≤ s := by
  classical
  exact Nat.find_min' finite hs

/-- A certified weight is, tautologically, a finite separation-weight certificate. -/
def finiteSeparationWeightOfCertificate {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} {s : ℕ} (h : IsSeparationWeight pi E lattice s) :
    FiniteSeparationWeight pi E lattice :=
  ⟨s, h⟩

/-- If the evaluated denominator is exactly `pi^s`, preservation of `V` and `G` supplies the
corresponding finite separation-weight certificate. -/
theorem separator_isSeparationWeight_of_pow_eq
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ}
    {lattice : AddSubgroup M} (hr : pi ^ s = r)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    IsSeparationWeight pi (separator r V G) lattice s := by
  rw [IsSeparationWeight, hr]
  exact scalar_mul_separator_preservesLattice certificate hV hG

/-- Minimal unit-aware denominator clearing.  If `r = uπ^s`, only the action of the inverse
unit is needed to transfer preservation of the integral numerator to `π^s E`. -/
theorem separator_isSeparationWeight_of_unit_mul_pow_eq_of_inv_preserves
    (r_ne_zero : r ≠ 0) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : (u : K) * pi ^ s = r)
    (huInv : ScalarPreservesLattice (↑(u⁻¹) : K) lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    IsSeparationWeight pi (separator r V G) lattice s := by
  rw [IsSeparationWeight,
    pow_smul_separator_eq_unit_inv_smul_separatorNumerator_of_ne_zero r_ne_zero u hr]
  exact huInv.smul (separatorNumerator_preservesLattice hV hG)

/-- Bundled valuation-unit wrapper for unit-aware denominator clearing.  Both unit directions
are convenient lattice data, although this implication uses only `u⁻¹`. -/
theorem separator_isSeparationWeight_of_unit_mul_pow_eq_of_ne_zero
    (r_ne_zero : r ≠ 0) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : (u : K) * pi ^ s = r)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    IsSeparationWeight pi (separator r V G) lattice s := by
  exact separator_isSeparationWeight_of_unit_mul_pow_eq_of_inv_preserves
    r_ne_zero hr hu.2 hV hG

/-- Certificate wrapper for unit-aware separation-weight clearing. -/
theorem separator_isSeparationWeight_of_unit_mul_pow_eq
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : (u : K) * pi ^ s = r)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    IsSeparationWeight pi (separator r V G) lattice s := by
  exact separator_isSeparationWeight_of_unit_mul_pow_eq_of_ne_zero
    certificate.r_ne_zero hr hu hV hG

/-- The same unit-aware theorem in the conventional valuation orientation `r = uπ^s`. -/
theorem separator_isSeparationWeight_of_eq_unit_mul_pow
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : r = (u : K) * pi ^ s)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    IsSeparationWeight pi (separator r V G) lattice s :=
  separator_isSeparationWeight_of_unit_mul_pow_eq certificate hr.symm hu hV hG

/-- Unit-aware denominator data supplies finiteness directly, without a redundant external
existence hypothesis. -/
theorem separator_hasFiniteSeparationWeight_of_unit_mul_pow_eq
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : (u : K) * pi ^ s = r)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    HasFiniteSeparationWeight pi (separator r V G) lattice :=
  ⟨s, separator_isSeparationWeight_of_unit_mul_pow_eq certificate hr hu hV hG⟩

/-- Conventional-orientation finiteness theorem for `r = uπ^s`. -/
theorem separator_hasFiniteSeparationWeight_of_eq_unit_mul_pow
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : r = (u : K) * pi ^ s)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    HasFiniteSeparationWeight pi (separator r V G) lattice :=
  ⟨s, separator_isSeparationWeight_of_eq_unit_mul_pow certificate hr hu hV hG⟩

/-- The canonical least weight obtained from unit-aware denominator data is at most its displayed
exponent. -/
theorem separator_separationWeight_le_of_unit_mul_pow_eq
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : (u : K) * pi ^ s = r)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    separationWeight
        (separator_hasFiniteSeparationWeight_of_unit_mul_pow_eq certificate hr hu hV hG) ≤ s := by
  apply separationWeight_le_of_clears
  exact separator_isSeparationWeight_of_unit_mul_pow_eq certificate hr hu hV hG

/-- The canonical least separation weight associated to `r = uπ^s` is at most `s`. -/
theorem separator_separationWeight_le_of_eq_unit_mul_pow
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ} {u : Kˣ}
    {lattice : AddSubgroup M} (hr : r = (u : K) * pi ^ s)
    (hu : IsLatticeUnit u lattice)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    separationWeight
        (separator_hasFiniteSeparationWeight_of_eq_unit_mul_pow certificate hr hu hV hG) ≤ s := by
  apply separationWeight_le_of_clears
  exact separator_isSeparationWeight_of_eq_unit_mul_pow certificate hr hu hV hG

/-- Consequently, any displayed denominator `pi^s = r` gives the manuscript's upper bound on the
actual minimal separation weight. -/
theorem separator_separationWeight_le_of_pow_eq
    (certificate : EvaluatedBezoutCertificate F G U V r) {pi : K} {s : ℕ}
    {lattice : AddSubgroup M}
    (finite : HasFiniteSeparationWeight pi (separator r V G) lattice)
    (hr : pi ^ s = r)
    (hV : PreservesLattice V lattice) (hG : PreservesLattice G lattice) :
    separationWeight finite ≤ s := by
  apply separationWeight_le_of_clears finite
  exact separator_isSeparationWeight_of_pow_eq certificate hr hV hG

/-! ## Precision delay -/

/-- Congruence modulo the scalar lattice `pi^n lattice`, expressed with an explicit witness. -/
def CongruentModLattice (pi : K) (lattice : AddSubgroup M) (n : ℕ) (x y : M) : Prop :=
  ∃ z : M, z ∈ lattice ∧ x - y = (pi ^ n) • z

/-- An `s`-digit denominator certificate turns `m+s` input digits into `m` output digits. -/
theorem projector_precision_delay {pi : K} {E : End (K := K) (M := M)}
    {lattice : AddSubgroup M} {s m : ℕ}
    (hweight : IsSeparationWeight pi E lattice s) {x y : M}
    (hxy : CongruentModLattice pi lattice (m + s) x y) :
    CongruentModLattice pi lattice m (E x) (E y) := by
  rcases hxy with ⟨z, hz, hxy⟩
  refine ⟨((pi ^ s) • E) z, hweight z hz, ?_⟩
  rw [← map_sub, hxy, map_smul]
  simp only [LinearMap.smul_apply, pow_add, smul_smul]

end Komorebi.PaperII.ResultantSeparation
