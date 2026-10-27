/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.ResidueProjectors

/-!
# Residue selectors, finite Fourier averages, and CRT coordinates

This module proves the Paper II residue-selector algebra over arbitrary
semirings, records exact `N → N * k` polyphase refinement, and constructs
coprime CRT packet coordinates.  The Fourier realization is deliberately
separated from the coefficient selector: it is first derived from an explicit
character-orthogonality certificate, and that certificate is then constructed
from a primitive root only over a field.  In particular, no primitive-root
claim is made for arbitrary rings with zero divisors.
-/

set_option autoImplicit false

namespace Komorebi
namespace Residue

universe u v

/-! ## Residue-projector algebra -/

/-- A residue selector is idempotent, over any semiring and module. -/
theorem residueProj_idempotent
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) (r : Fin N) :
    (residueProj (R := R) (A := A) N hN r).comp
        (residueProj (R := R) (A := A) N hN r) =
      residueProj (R := R) (A := A) N hN r := by
  apply LinearMap.ext
  intro x
  exact Packet.fibreProj_idempotent (residueAddress N hN) r x

/-- Distinct residue selectors annihilate one another. -/
theorem residueProj_orthogonal
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) {r s : Fin N} (hrs : r ≠ s) :
    (residueProj (R := R) (A := A) N hN r).comp
        (residueProj (R := R) (A := A) N hN s) = 0 := by
  apply LinearMap.ext
  intro x
  exact Packet.fibreProj_orthogonal (residueAddress N hN) hrs x

/-- The finite family of all residue selectors sums to the identity. -/
theorem residueProj_complete
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) :
    (∑ r : Fin N, residueProj (R := R) (A := A) N hN r) = LinearMap.id := by
  apply LinearMap.ext
  intro x
  simpa only [LinearMap.sum_apply, LinearMap.id_apply, residueProj_apply] using
    Packet.fibreProj_reconstruction (residueAddress N hN) x

/-- Paper II polyphase refinement from modulus `N` to modulus `N * k`. -/
theorem polyphase_refinement
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N k : Nat) (hN : 0 < N) (hk : 0 < k) (r : Fin N) :
    residueProj (R := R) (A := A) N hN r =
      ∑ s : Fin (N * k),
        if mergeAddress N k hN s = r then
          residueProj (R := R) (A := A) (N * k) (Nat.mul_pos hN hk) s
        else 0 :=
  residueProj_refinement N k hN hk r

/-! ## Finite Fourier realization -/

/-- The unnormalized coefficientwise Fourier kernel over a commutative semiring.
The three scalars are deliberately independent: no inverse or division
hypothesis is built into this definition. -/
def ringFourierKernel
    {R : Type u} [CommSemiring R]
    (N : Nat) (omega omegaDual : R) (j : Fin N) (n : Nat) : R :=
  ∑ k : Fin N, (omegaDual ^ (j.val * k.val)) * (omega ^ (n * k.val))

/-- The finite residue-index version of `ringFourierKernel`.  Unlike the
arbitrary-address kernel, both character labels range over the finite type
`Fin N`; consequently its orthogonality table is finite data. -/
def ringFourierResidueKernel
    {R : Type u} [CommSemiring R]
    (N : Nat) (omega omegaDual : R) (j r : Fin N) : R :=
  ∑ k : Fin N, (omegaDual ^ (j.val * k.val)) * (omega ^ (r.val * k.val))

/-- If `omega` is an `N`-th root of unity, the arbitrary-address kernel is
periodic in its coefficient address and is therefore determined by the
finite residue-index kernel. -/
theorem ringFourierKernel_eq_residueKernel
    {R : Type u} [CommSemiring R]
    (N : Nat) (hN : 0 < N) (omega omegaDual : R)
    (homega : omega ^ N = 1) (j : Fin N) (n : Nat) :
    ringFourierKernel N omega omegaDual j n =
      ringFourierResidueKernel N omega omegaDual j
        ⟨n % N, Nat.mod_lt n hN⟩ := by
  apply Finset.sum_congr rfl
  intro k _hk
  congr 1
  calc
    omega ^ (n * k.val) = (omega ^ n) ^ k.val := by rw [pow_mul]
    _ = (omega ^ (n % N)) ^ k.val := by rw [pow_eq_pow_mod n homega]
    _ = omega ^ ((n % N) * k.val) := by rw [pow_mul]

/-- A genuinely finite general-ring Fourier certificate.  Its character
orthogonality premise is a finite `N × N` table; `omega_pow_order` is then
used to extend that table periodically to every coefficient address. -/
structure FiniteRingFourierOrthogonalityCertificate
    (R : Type u) [CommSemiring R] (N : Nat)
    (omega omegaDual eta : R) : Prop where
  omega_pow_order : omega ^ N = 1
  weighted_residue_sum_eq (j r : Fin N) :
    eta * ringFourierResidueKernel N omega omegaDual j r =
      if r = j then 1 else 0

/-- The legacy coefficientwise orthogonality certificate used in Paper II.
It is meaningful over an arbitrary commutative semiring, including rings with
zero divisors, and assumes neither division by `N` nor that `omegaDual` is an
inverse of `omega`.  New proofs should generally use the finite certificate
above and derive this interface through `toRingCertificate`. -/
structure RingFourierOrthogonalityCertificate
    (R : Type u) [CommSemiring R] (N : Nat)
    (omega omegaDual eta : R) : Prop where
  weighted_sum_eq (j : Fin N) (n : Nat) :
    eta * ringFourierKernel N omega omegaDual j n =
      if n % N = j.val then 1 else 0

/-- A finite residue-index certificate supplies the legacy arbitrary-address
certificate by periodic reduction.  This theorem is the substantive bridge
which removes the former infinite family of certificate obligations. -/
theorem FiniteRingFourierOrthogonalityCertificate.toRingCertificate
    {R : Type u} [CommSemiring R]
    (N : Nat) (hN : 0 < N) (omega omegaDual eta : R)
    (certificate :
      FiniteRingFourierOrthogonalityCertificate R N omega omegaDual eta) :
    RingFourierOrthogonalityCertificate R N omega omegaDual eta := by
  refine ⟨?_⟩
  intro j n
  rw [ringFourierKernel_eq_residueKernel N hN omega omegaDual
    certificate.omega_pow_order j n]
  rw [certificate.weighted_residue_sum_eq]
  congr 1
  simp only [Fin.ext_iff]

/-- The division-free coefficientwise Fourier average attached to independent
scalars `omega`, `omegaDual`, and `eta`.  It is the diagonal action of
`eta ∑ₖ (omegaDual)^(j k) U^k` on coefficient sequences. -/
def ringFourierAverage
    {R : Type u} {A : Type v}
    [CommSemiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (omega omegaDual eta : R) (j : Fin N) :
    Module.End R (Nat → A) where
  toFun x n := (eta * ringFourierKernel N omega omegaDual j n) • x n
  map_add' x y := by
    funext n
    exact smul_add _ _ _
  map_smul' c x := by
    funext n
    simp only [Pi.smul_apply, smul_smul, RingHom.id_apply]
    rw [mul_comm]

@[simp] theorem ringFourierAverage_apply
    {R : Type u} {A : Type v}
    [CommSemiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (omega omegaDual eta : R) (j : Fin N)
    (x : Nat → A) (n : Nat) :
    ringFourierAverage (A := A) N omega omegaDual eta j x n =
      (eta * ringFourierKernel N omega omegaDual j n) • x n :=
  rfl

/-- An explicit coefficientwise orthogonality certificate identifies the
division-free Fourier average with the residue selector over any commutative
semiring. -/
theorem ringFourierAverage_eq_residueProj_of_certificate
    {R : Type u} {A : Type v}
    [CommSemiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) (omega omegaDual eta : R)
    (certificate :
      RingFourierOrthogonalityCertificate R N omega omegaDual eta)
    (j : Fin N) :
    ringFourierAverage (A := A) N omega omegaDual eta j =
      residueProj (R := R) (A := A) N hN j := by
  apply LinearMap.ext
  intro x
  funext n
  rw [ringFourierAverage_apply, certificate.weighted_sum_eq]
  change
    (if n % N = j.val then (1 : R) else 0) • x n =
      if residueAddress N hN n = j then x n else 0
  by_cases h : n % N = j.val
  · have haddress : residueAddress N hN n = j := Fin.ext h
    simp [h, haddress]
  · have haddress : residueAddress N hN n ≠ j := by
      intro heq
      exact h (congrArg Fin.val heq)
    simp [h, haddress]

/-- The division-free Fourier average equals the residue selector from only
a finite residue-index orthogonality table and the root-periodicity datum. -/
theorem ringFourierAverage_eq_residueProj_of_finite_certificate
    {R : Type u} {A : Type v}
    [CommSemiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) (omega omegaDual eta : R)
    (certificate :
      FiniteRingFourierOrthogonalityCertificate R N omega omegaDual eta)
    (j : Fin N) :
    ringFourierAverage (A := A) N omega omegaDual eta j =
      residueProj (R := R) (A := A) N hN j :=
  ringFourierAverage_eq_residueProj_of_certificate N hN omega omegaDual eta
    (certificate.toRingCertificate N hN omega omegaDual eta) j

/-- The scalar character sum acting on coefficient address `n` in the
`j`-th finite Fourier average.  Reducing `n` modulo `N` is harmless for a
primitive `N`-th root and makes the exact orthogonality statement explicit. -/
def fourierKernel
    {K : Type u} [Field K]
    (N : Nat) (omega : K) (j : Fin N) (n : Nat) : K :=
  ∑ k : Fin N, ((omega ^ (n % N)) / (omega ^ j.val)) ^ k.val

/-- An explicit finite-character orthogonality certificate.  Besides the
character-sum identity, it records the nonvanishing of the group order needed
to normalize the average. -/
structure FourierOrthogonalityCertificate
    (K : Type u) [Field K] (N : Nat) (omega : K) : Prop where
  order_ne_zero : (N : K) ≠ 0
  sum_eq (j : Fin N) (n : Nat) :
    fourierKernel N omega j n =
      if n % N = j.val then (N : K) else 0

/-- The coefficientwise finite Fourier average.  Its multiplier is exactly
`N⁻¹ ∑ₖ (omega^(n mod N) / omega^j)^k`, the eigenvalue of the operator
average `N⁻¹ ∑ₖ omega^(-jk) U^k` at coefficient address `n`. -/
def fourierAverage
    {K : Type u} {A : Type v}
    [Field K] [AddCommMonoid A] [Module K A]
    (N : Nat) (omega : K) (j : Fin N) : Module.End K (Nat → A) where
  toFun x n := ((N : K)⁻¹ * fourierKernel N omega j n) • x n
  map_add' x y := by
    funext n
    exact smul_add _ _ _
  map_smul' c x := by
    funext n
    simp only [Pi.smul_apply, smul_smul, RingHom.id_apply]
    rw [mul_comm]

@[simp] theorem fourierAverage_apply
    {K : Type u} {A : Type v}
    [Field K] [AddCommMonoid A] [Module K A]
    (N : Nat) (omega : K) (j : Fin N) (x : Nat → A) (n : Nat) :
    fourierAverage (A := A) N omega j x n =
      ((N : K)⁻¹ * fourierKernel N omega j n) • x n :=
  rfl

/-- An explicit orthogonality certificate identifies the finite Fourier
average with the coefficient residue selector. -/
theorem fourierAverage_eq_residueProj_of_certificate
    {K : Type u} {A : Type v}
    [Field K] [AddCommMonoid A] [Module K A]
    (N : Nat) (hN : 0 < N) (omega : K)
    (certificate : FourierOrthogonalityCertificate K N omega)
    (j : Fin N) :
    fourierAverage (A := A) N omega j =
      residueProj (R := K) (A := A) N hN j := by
  apply LinearMap.ext
  intro x
  funext n
  rw [fourierAverage_apply, certificate.sum_eq]
  change
    ((N : K)⁻¹ * (if n % N = j.val then (N : K) else 0)) • x n =
      if residueAddress N hN n = j then x n else 0
  by_cases h : n % N = j.val
  · have haddress : residueAddress N hN n = j := Fin.ext h
    simp [h, haddress, certificate.order_ne_zero]
  · have haddress : residueAddress N hN n ≠ j := by
      intro heq
      exact h (congrArg Fin.val heq)
    simp [h, haddress]

/-- Over a field, a primitive `N`-th root supplies the exact character
orthogonality certificate.  This is intentionally not stated over an
arbitrary zero-divisor ring. -/
theorem primitiveRoot_fourierOrthogonalityCertificate
    {K : Type u} [Field K]
    (N : Nat) (hN : 0 < N) (omega : K)
    (homega : IsPrimitiveRoot omega N) :
    FourierOrthogonalityCertificate K N omega := by
  let _ : NeZero N := ⟨Nat.ne_of_gt hN⟩
  have homega0 : omega ≠ 0 := homega.ne_zero (Nat.ne_of_gt hN)
  refine
    { order_ne_zero := (homega.neZero' : NeZero (N : K)).out
      sum_eq := ?_ }
  intro j n
  by_cases hnj : n % N = j.val
  · simp [fourierKernel, hnj, homega0]
  · rw [ite_eq_right hnj]
    let q : K := (omega ^ (n % N)) / (omega ^ j.val)
    have hpowers : omega ^ (n % N) ≠ omega ^ j.val := by
      intro heq
      exact hnj (homega.pow_inj (Nat.mod_lt n hN) j.isLt heq)
    have hq_ne_one : q ≠ 1 := by
      intro hq
      exact hpowers ((div_eq_one_iff_eq (pow_ne_zero _ homega0)).mp hq)
    have hq_pow : q ^ N = 1 := by
      dsimp only [q]
      rw [div_pow]
      have hnum : (omega ^ (n % N)) ^ N = 1 := by
        rw [← pow_mul, Nat.mul_comm, pow_mul, homega.pow_eq_one, one_pow]
      have hden : (omega ^ j.val) ^ N = 1 := by
        rw [← pow_mul, Nat.mul_comm, pow_mul, homega.pow_eq_one, one_pow]
      rw [hnum, hden, div_one]
    change ∑ k : Fin N, q ^ k.val = 0
    rw [Fin.sum_univ_eq_sum_range, geom_sum_eq hq_ne_one, hq_pow]
    simp

/-- Root-of-unity realization of a residue selector over a field. -/
theorem fourierAverage_eq_residueProj_of_primitiveRoot
    {K : Type u} {A : Type v}
    [Field K] [AddCommMonoid A] [Module K A]
    (N : Nat) (hN : 0 < N) (omega : K)
    (homega : IsPrimitiveRoot omega N) (j : Fin N) :
    fourierAverage (A := A) N omega j =
      residueProj (R := K) (A := A) N hN j :=
  fourierAverage_eq_residueProj_of_certificate N hN omega
    (primitiveRoot_fourierOrthogonalityCertificate N hN omega homega) j

/-! ## Coprime CRT coordinates and product selectors -/

/-- The two residue components of a residue modulo `m * n`. -/
def crtComponents
    (m n : Nat) (hm : 0 < m) (hn : 0 < n) :
    Fin (m * n) → Fin m × Fin n :=
  fun s =>
    (⟨s.val % m, Nat.mod_lt _ hm⟩,
      ⟨s.val % n, Nat.mod_lt _ hn⟩)

/-- The coprime Chinese-remainder bijection on finite residue labels. -/
def crtEquiv
    (m n : Nat) (hm : 0 < m) (hn : 0 < n)
    (hcoprime : m.Coprime n) : Fin (m * n) ≃ Fin m × Fin n where
  toFun := crtComponents m n hm hn
  invFun p :=
    ⟨(Nat.chineseRemainder hcoprime p.1.val p.2.val).val,
      Nat.chineseRemainder_lt_mul hcoprime p.1.val p.2.val
        (Nat.ne_of_gt hm) (Nat.ne_of_gt hn)⟩
  left_inv s := by
    apply Fin.ext
    let c := Nat.chineseRemainder hcoprime (s.val % m) (s.val % n)
    have hs_mod : s.val ≡ c.val [MOD m * n] :=
      Nat.chineseRemainder_modEq_unique hcoprime
        (Nat.mod_modEq s.val m).symm (Nat.mod_modEq s.val n).symm
    change c.val = s.val
    calc
      c.val = c.val % (m * n) :=
        (Nat.mod_eq_of_lt
          (Nat.chineseRemainder_lt_mul hcoprime (s.val % m) (s.val % n)
            (Nat.ne_of_gt hm) (Nat.ne_of_gt hn))).symm
      _ = s.val % (m * n) := hs_mod.symm
      _ = s.val := Nat.mod_eq_of_lt s.isLt
  right_inv p := by
    apply Prod.ext
    · apply Fin.ext
      exact Nat.mod_eq_of_modEq
        (Nat.chineseRemainder hcoprime p.1.val p.2.val).property.1 p.1.isLt
    · apply Fin.ext
      exact Nat.mod_eq_of_modEq
        (Nat.chineseRemainder hcoprime p.1.val p.2.val).property.2 p.2.isLt

/-- The component map itself is bijective for positive coprime moduli. -/
theorem crtComponents_bijective
    (m n : Nat) (hm : 0 < m) (hn : 0 < n)
    (hcoprime : m.Coprime n) :
    Function.Bijective (crtComponents m n hm hn) :=
  (crtEquiv m n hm hn hcoprime).bijective

/-- Reducing an address modulo `m * n` and taking its CRT components agrees
with reducing the address directly modulo `m` and modulo `n`. -/
theorem crtComponents_residueAddress
    (m n : Nat) (hm : 0 < m) (hn : 0 < n) (a : Nat) :
    crtComponents m n hm hn
        (residueAddress (m * n) (Nat.mul_pos hm hn) a) =
      (residueAddress m hm a, residueAddress n hn a) := by
  apply Prod.ext
  · apply Fin.ext
    exact Nat.mod_mod_of_dvd a ⟨n, rfl⟩
  · apply Fin.ext
    exact Nat.mod_mod_of_dvd a ⟨m, Nat.mul_comm m n⟩

/-- Equality of a composite residue address is equivalent to equality of its
two coprime component addresses. -/
theorem residueAddress_eq_iff_crtComponents
    (m n : Nat) (hm : 0 < m) (hn : 0 < n)
    (hcoprime : m.Coprime n) (a : Nat) (s : Fin (m * n)) :
    residueAddress (m * n) (Nat.mul_pos hm hn) a = s ↔
      residueAddress m hm a = (crtComponents m n hm hn s).1 ∧
      residueAddress n hn a = (crtComponents m n hm hn s).2 := by
  constructor
  · intro has
    have hcomponents := congrArg (crtComponents m n hm hn) has
    rw [crtComponents_residueAddress] at hcomponents
    exact Prod.ext_iff.mp hcomponents
  · rintro ⟨hmcomp, hncomp⟩
    apply (crtEquiv m n hm hn hcoprime).injective
    change
      crtComponents m n hm hn
          (residueAddress (m * n) (Nat.mul_pos hm hn) a) =
        crtComponents m n hm hn s
    rw [crtComponents_residueAddress]
    exact Prod.ext hmcomp hncomp

/-- A composite residue selector is the product of its two coprime component
selectors, with the `m`-selector applied last. -/
theorem residueProj_crt
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (m n : Nat) (hm : 0 < m) (hn : 0 < n)
    (hcoprime : m.Coprime n) (s : Fin (m * n)) :
    (residueProj (R := R) (A := A) m hm (crtComponents m n hm hn s).1).comp
        (residueProj (R := R) (A := A) n hn (crtComponents m n hm hn s).2) =
      residueProj (R := R) (A := A) (m * n) (Nat.mul_pos hm hn) s := by
  apply LinearMap.ext
  intro x
  funext a
  simp only [LinearMap.comp_apply, residueProj_apply, Packet.fibreProj]
  by_cases hma : residueAddress m hm a = (crtComponents m n hm hn s).1 <;>
    by_cases hna : residueAddress n hn a = (crtComponents m n hm hn s).2 <;>
    simp [hma, hna,
      residueAddress_eq_iff_crtComponents m n hm hn hcoprime a s]

/-- The two coprime component selectors commute, and their reverse product is
the same composite residue selector. -/
theorem residueProj_crt_comm
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (m n : Nat) (hm : 0 < m) (hn : 0 < n)
    (hcoprime : m.Coprime n) (s : Fin (m * n)) :
    (residueProj (R := R) (A := A) n hn (crtComponents m n hm hn s).2).comp
        (residueProj (R := R) (A := A) m hm (crtComponents m n hm hn s).1) =
      residueProj (R := R) (A := A) (m * n) (Nat.mul_pos hm hn) s := by
  apply LinearMap.ext
  intro x
  funext a
  simp only [LinearMap.comp_apply, residueProj_apply, Packet.fibreProj]
  by_cases hma : residueAddress m hm a = (crtComponents m n hm hn s).1 <;>
    by_cases hna : residueAddress n hn a = (crtComponents m n hm hn s).2 <;>
    simp [hma, hna,
      residueAddress_eq_iff_crtComponents m n hm hn hcoprime a s]

/-! ## Dyadic--odd specialization -/

/-- An odd modulus is coprime to every dyadic power. -/
theorem twoPow_coprime_of_odd
    (a M : Nat) (hodd : Odd M) : (2 ^ a).Coprime M := by
  exact hodd.coprime_two_left.pow_left a

/-- CRT identifies residues modulo `2^a * M` with dyadic and odd residue
labels whenever `M` is positive and odd. -/
def dyadicOddEquiv
    (a M : Nat) (hM : 0 < M) (hodd : Odd M) :
    Fin (2 ^ a * M) ≃ Fin (2 ^ a) × Fin M :=
  crtEquiv (2 ^ a) M (pow_pos (by decide) a) hM
    (twoPow_coprime_of_odd a M hodd)

/-- The dyadic--odd component map is a bijection. -/
theorem dyadicOddComponents_bijective
    (a M : Nat) (hM : 0 < M) (hodd : Odd M) :
    Function.Bijective
      (crtComponents (2 ^ a) M (pow_pos (by decide) a) hM) :=
  (dyadicOddEquiv a M hM hodd).bijective

/-- Dyadic--odd packet factorization, in both composition orders. -/
theorem residueProj_dyadicOdd
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (a M : Nat) (hM : 0 < M) (hodd : Odd M) (s : Fin (2 ^ a * M)) :
    let h2 : 0 < 2 ^ a := pow_pos (by decide) a
    let components := crtComponents (2 ^ a) M h2 hM s
    residueProj (R := R) (A := A) (2 ^ a * M) (Nat.mul_pos h2 hM) s =
        (residueProj (R := R) (A := A) (2 ^ a) h2 components.1).comp
          (residueProj (R := R) (A := A) M hM components.2) ∧
      residueProj (R := R) (A := A) (2 ^ a * M) (Nat.mul_pos h2 hM) s =
        (residueProj (R := R) (A := A) M hM components.2).comp
          (residueProj (R := R) (A := A) (2 ^ a) h2 components.1) := by
  dsimp only
  let h2 : 0 < 2 ^ a := pow_pos (by decide) a
  let hcoprime : (2 ^ a).Coprime M := twoPow_coprime_of_odd a M hodd
  constructor
  · exact (residueProj_crt (R := R) (A := A)
      (2 ^ a) M h2 hM hcoprime s).symm
  · exact (residueProj_crt_comm (R := R) (A := A)
      (2 ^ a) M h2 hM hcoprime s).symm

#print axioms residueProj_idempotent
#print axioms residueProj_orthogonal
#print axioms residueProj_complete
#print axioms polyphase_refinement
#print axioms ringFourierKernel_eq_residueKernel
#print axioms FiniteRingFourierOrthogonalityCertificate.toRingCertificate
#print axioms ringFourierAverage_eq_residueProj_of_certificate
#print axioms ringFourierAverage_eq_residueProj_of_finite_certificate
#print axioms fourierAverage_eq_residueProj_of_certificate
#print axioms primitiveRoot_fourierOrthogonalityCertificate
#print axioms fourierAverage_eq_residueProj_of_primitiveRoot
#print axioms crtEquiv
#print axioms crtComponents_bijective
#print axioms residueProj_crt
#print axioms residueProj_crt_comm
#print axioms dyadicOddComponents_bijective
#print axioms residueProj_dyadicOdd

end Residue
end Komorebi
