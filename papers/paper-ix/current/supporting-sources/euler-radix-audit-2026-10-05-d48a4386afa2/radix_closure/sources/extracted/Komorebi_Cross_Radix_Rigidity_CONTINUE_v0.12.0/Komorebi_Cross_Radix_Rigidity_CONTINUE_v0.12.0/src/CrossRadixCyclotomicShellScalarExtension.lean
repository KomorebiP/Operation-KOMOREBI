import CrossRadixCyclotomicShellIntegralLattice
import CrossRadixDFTShellAgreement

noncomputable section
open scoped BigOperators ArithmeticFunction.Moebius

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Coordinatewise embedding of an integral residue packet into the complex residue space. -/
def intPacketToComplex (x : IntResiduePacket T) : ResidueProfile T :=
  fun t => (x t : ℂ)

/-- The complex scalar extension of an unnormalized subgroup Reynolds numerator.
It is deliberately written as `width * average`; the next theorem identifies this
with the literal cast of the integral subgroup sum. -/
def complexSubgroupReynoldsNumerator (hT : 0 < T) (g : DivIdx T) :
    Module.End ℂ (ResidueProfile T) := by
  letI : NeZero T := ⟨hT.ne'⟩
  exact (g.1 : ℂ) • subgroupReynoldsAverage g

/-- On integral packets, the complex subgroup numerator is exactly the coordinatewise
cast of the integral subgroup numerator. -/
@[simp] theorem complexSubgroupReynoldsNumerator_apply
    (hT : 0 < T) [NeZero T] (g : DivIdx T) (x : ResidueProfile T) (t : ZMod T) :
    complexSubgroupReynoldsNumerator hT g x t =
      ∑ z : ZMod g.1, x (t - subgroupShift g z) := by
  have hgT : g.1 ∣ T := (Nat.mem_divisors.mp g.2).1
  have hgpos : 0 < g.1 := Nat.pos_of_dvd_of_pos hgT hT
  have hgc : (g.1 : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr hgpos.ne'
  simp only [complexSubgroupReynoldsNumerator, LinearMap.smul_apply,
    Pi.smul_apply, smul_eq_mul, subgroupReynoldsAverage]
  change (g.1 : ℂ) * ((g.1 : ℂ)⁻¹ * ∑ z : ZMod g.1, x (t - subgroupShift g z)) = _
  rw [← mul_assoc, mul_inv_cancel₀ hgc, one_mul]

/-- On integral packets, the complex subgroup numerator is exactly the coordinatewise
cast of the integral subgroup numerator. -/
theorem complexSubgroupReynoldsNumerator_int_cast
    (hT : 0 < T) [NeZero T] (g : DivIdx T) (x : IntResiduePacket T) :
    complexSubgroupReynoldsNumerator hT g (intPacketToComplex x) =
      intPacketToComplex (intSubgroupReynoldsNumerator hT g x) := by
  funext t
  rw [complexSubgroupReynoldsNumerator_apply]
  simp only [intPacketToComplex, intSubgroupReynoldsNumerator]
  exact (Int.cast_sum (R := ℂ) _ _).symm


/-- DFT of the complex subgroup numerator: the unnormalized subgroup sum contributes its
width times the exact Reynolds `0/1` mask. -/
theorem dft_complexSubgroupReynoldsNumerator
    (hT : 0 < T) [NeZero T] (g : DivIdx T) (x : ResidueProfile T) (k : ZMod T) :
    ZMod.dft (N := T) (E := ℂ) (complexSubgroupReynoldsNumerator hT g x) k =
      (g.1 : ℂ) * rawWidthMask g k * ZMod.dft (N := T) (E := ℂ) x k := by
  simp only [complexSubgroupReynoldsNumerator, LinearMap.smul_apply]
  rw [map_smul]
  simp only [Pi.smul_apply, smul_eq_mul]
  rw [dft_subgroupReynoldsAverage hT]
  ring

/-- Every active Möbius width cancels exactly against its share of the least common
shell denominator after passage to `ℂ`. -/
theorem shellCommonDenom_div_width_mul_complex
    (c : DivIdx T) (r : MobiusShellIndex c) :
    (((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ) *
      (MobiusShellWidth c r.1 : ℂ)) = (shellCommonDenom c : ℂ) := by
  exact_mod_cast Nat.div_mul_cancel (mobiusWidth_dvd_shellCommonDenom c r)


/-- One cleared Möbius term: the denominator share cancels the unnormalized subgroup width. -/
theorem clearedMobiusWidthTerm
    (c : DivIdx T) (r : MobiusShellIndex c) (A B : ℂ) :
    ((((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
        ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ)) *
      ((MobiusShellWidth c r.1 : ℂ) * A * B)) =
      (shellCommonDenom c : ℂ) *
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) * A) * B := by
  have hden := shellCommonDenom_div_width_mul_complex c r
  calc
    ((((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
        ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ)) *
      ((MobiusShellWidth c r.1 : ℂ) * A * B)) =
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
          (((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ) *
            (MobiusShellWidth c r.1 : ℂ))) * A * B := by ring
    _ = (shellCommonDenom c : ℂ) *
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) * A) * B := by rw [hden]; ring

/-- The primitive Fourier shell mask is the active (zero-trimmed) Möbius sum of
literal Reynolds width masks. -/
theorem rawShellMask_eq_active_mobius_width_sum
    (hT : 0 < T) (c : DivIdx T) (k : ZMod T) :
    rawShellMask hT c k =
      ∑ r : MobiusShellIndex c,
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
          rawWidthMask (mobiusWidthIdx hT c r) k) := by
  have hcert := rawShellMask_mobius_agrees_with_certified hT c k
  rw [Finset.sum_apply] at hcert
  simp only [Pi.smul_apply, smul_eq_mul] at hcert
  rw [hcert]
  let F : ℕ → ℂ := fun r =>
    (((ArithmeticFunction.moebius r : ℤ) : ℂ) *
      rawWidthVec (T := T) (c.1 * r) (frequencyShellIdx hT k))
  have hsupp :
      (∑ r ∈ (shellConductor c).divisors, F r) =
        ∑ r ∈ mobiusShellSupport c, F r := by
    symm
    apply Finset.sum_subset
    · intro r hr
      exact (mem_mobiusShellSupport.mp hr).1
    · intro r hrdiv hrnot
      have hmu : ArithmeticFunction.moebius r = 0 := by
        by_contra hne
        exact hrnot (mem_mobiusShellSupport.mpr ⟨hrdiv, hne⟩)
      simp [F, hmu]
  change (∑ r ∈ (shellConductor c).divisors, F r) = _
  rw [hsupp]
  rw [Finset.sum_subtype (mobiusShellSupport c) (by intro r; rfl) F]
  apply Finset.sum_congr rfl
  intro r hr
  change F r.1 =
    (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
      rawWidthMask (mobiusWidthIdx hT c r) k)
  rw [rawWidthMask_eq_widthVec_frequencyShell hT]
  have hraw := rawWidthVec_dividx (mobiusWidthIdx hT c r)
  have hval := congrFun hraw (frequencyShellIdx hT k)
  simp only [F]
  rw [← hval]
  simp only [mobiusWidthIdx_val, MobiusShellWidth]

/-- Complex scalar extension of the actual integral primitive-shell numerator. -/
def complexCyclotomicShellNumerator (hT : 0 < T) (c : DivIdx T) :
    Module.End ℂ (ResidueProfile T) :=
  ∑ r : MobiusShellIndex c,
    (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
      ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ)) •
      complexSubgroupReynoldsNumerator hT (mobiusWidthIdx hT c r)

/-- The complex shell numerator genuinely extends the saved integral numerator:
on every integral packet, applying the complex operator after scalar embedding equals
coordinatewise scalar extension of the integral output. -/
theorem complexCyclotomicShellNumerator_int_cast
    (hT : 0 < T) [NeZero T] (c : DivIdx T) (x : IntResiduePacket T) :
    complexCyclotomicShellNumerator hT c (intPacketToComplex x) =
      intPacketToComplex (cyclotomicShellNumerator hT c x) := by
  funext t
  simp only [complexCyclotomicShellNumerator, LinearMap.sum_apply, LinearMap.smul_apply,
    Pi.smul_apply, smul_eq_mul, cyclotomicShellNumerator, intPacketToComplex,
    Finset.sum_apply]
  change _ = ((Int.castRingHom ℂ) (∑ r : MobiusShellIndex c,
    (ArithmeticFunction.moebius r.1 : ℤ) *
      ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℤ) *
      intSubgroupReynoldsNumerator hT (mobiusWidthIdx hT c r) x t))
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro r hr
  rw [complexSubgroupReynoldsNumerator_int_cast]
  simp only [intPacketToComplex, map_mul]
  norm_cast

/-- Main scalar-extension bridge: after extension from `ℤ` to `ℂ`, the cleared integral
Möbius/Reynolds numerator is exactly the least common shell denominator times the
already-certified primitive DFT shell projector. -/
theorem complexCyclotomicShellNumerator_eq_shellProjector
    (hT : 0 < T) [NeZero T] (c : DivIdx T) :
    complexCyclotomicShellNumerator hT c =
      (shellCommonDenom c : ℂ) • dftShellProjector hT c := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  funext k
  simp only [LinearMap.smul_apply]
  rw [map_smul, dft_dftShellProjector]
  simp only [Pi.smul_apply, smul_eq_mul, rawShellFreqEnd]
  rw [show ZMod.dft (N := T) (E := ℂ) (complexCyclotomicShellNumerator hT c x) k =
      ∑ r : MobiusShellIndex c,
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
          ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℂ)) *
          ((MobiusShellWidth c r.1 : ℂ) *
            rawWidthMask (mobiusWidthIdx hT c r) k *
            ZMod.dft (N := T) (E := ℂ) x k) by
      simp [complexCyclotomicShellNumerator, map_sum, map_smul,
        dft_complexSubgroupReynoldsNumerator, mobiusWidthIdx_val]]
  simp_rw [clearedMobiusWidthTerm]
  rw [← Finset.sum_mul]
  rw [← Finset.mul_sum]
  change ((shellCommonDenom c : ℂ) *
      (∑ r : MobiusShellIndex c,
        (((ArithmeticFunction.moebius r.1 : ℤ) : ℂ) *
          rawWidthMask (mobiusWidthIdx hT c r) k))) *
        ZMod.dft (N := T) (E := ℂ) x k =
      (shellCommonDenom c : ℂ) *
        (rawShellMask hT c k * ZMod.dft (N := T) (E := ℂ) x k)
  rw [← rawShellMask_eq_active_mobius_width_sum hT c k]
  ring


/-- Integer-input form of the scalar-extension theorem: the cast of the saved integral
shell numerator is exactly `D_c` times the complex primitive shell projector. -/
theorem int_cast_cyclotomicShellNumerator_eq_denom_shellProjector
    (hT : 0 < T) [NeZero T] (c : DivIdx T) (x : IntResiduePacket T) :
    intPacketToComplex (cyclotomicShellNumerator hT c x) =
      (shellCommonDenom c : ℂ) •
        dftShellProjector hT c (intPacketToComplex x) := by
  calc
    intPacketToComplex (cyclotomicShellNumerator hT c x) =
        complexCyclotomicShellNumerator hT c (intPacketToComplex x) :=
      (complexCyclotomicShellNumerator_int_cast hT c x).symm
    _ = ((shellCommonDenom c : ℂ) • dftShellProjector hT c)
        (intPacketToComplex x) :=
      LinearMap.congr_fun (complexCyclotomicShellNumerator_eq_shellProjector hT c)
        (intPacketToComplex x)
    _ = (shellCommonDenom c : ℂ) •
        dftShellProjector hT c (intPacketToComplex x) := by rfl

/-- Rational reconstruction formula on the integral lattice: the primitive shell projector
is obtained by dividing the saved integral numerator by its exact shell denominator. -/
theorem dftShellProjector_int_cast_eq_inv_smul_numerator
    (hT : 0 < T) [NeZero T] (c : DivIdx T) (x : IntResiduePacket T) :
    dftShellProjector hT c (intPacketToComplex x) =
      (shellCommonDenom c : ℂ)⁻¹ •
        intPacketToComplex (cyclotomicShellNumerator hT c x) := by
  have hD : (shellCommonDenom c : ℂ) ≠ 0 := by
    exact Nat.cast_ne_zero.mpr (shellCommonDenom_ne_zero hT c)
  have h := int_cast_cyclotomicShellNumerator_eq_denom_shellProjector hT c x
  rw [h]
  simp only [smul_smul]
  rw [inv_mul_cancel₀ hD, one_smul]


/-- Exact integral-preservation characterization: the v0.11 shell good lattice is precisely
the set of integer packets whose primitive complex shell projection is again integral. -/
theorem mem_CyclotomicShellGoodLattice_iff_projector_integral
    (hT : 0 < T) [NeZero T] (c : DivIdx T) (x : IntResiduePacket T) :
    x ∈ CyclotomicShellGoodLattice hT c ↔
      ∃ y : IntResiduePacket T,
        dftShellProjector hT c (intPacketToComplex x) = intPacketToComplex y := by
  constructor
  · intro hx
    have hxdiv := (mem_CyclotomicShellGoodLattice_iff hT c x).1 hx
    choose y hy using hxdiv
    let ypacket : IntResiduePacket T := fun t => y t
    refine ⟨ypacket, ?_⟩
    rw [dftShellProjector_int_cast_eq_inv_smul_numerator hT c x]
    funext t
    have hD : (shellCommonDenom c : ℂ) ≠ 0 := by
      exact Nat.cast_ne_zero.mpr (shellCommonDenom_ne_zero hT c)
    have hyt := hy t
    simp only [Pi.smul_apply, smul_eq_mul, intPacketToComplex, ypacket]
    rw [hyt]
    push_cast
    field_simp
  · rintro ⟨y, hy⟩
    apply (mem_CyclotomicShellGoodLattice_iff hT c x).2
    intro t
    have hcast := congrFun (int_cast_cyclotomicShellNumerator_eq_denom_shellProjector hT c x) t
    rw [hy] at hcast
    simp only [Pi.smul_apply, smul_eq_mul, intPacketToComplex] at hcast
    have hint : cyclotomicShellNumerator hT c x t =
        (shellCommonDenom c : ℤ) * y t := by
      exact_mod_cast hcast
    exact ⟨y t, hint⟩

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.complexSubgroupReynoldsNumerator_int_cast
#print axioms KomorebiCrossRadix.rawShellMask_eq_active_mobius_width_sum
#print axioms KomorebiCrossRadix.complexCyclotomicShellNumerator_int_cast
#print axioms KomorebiCrossRadix.complexCyclotomicShellNumerator_eq_shellProjector
#print axioms KomorebiCrossRadix.int_cast_cyclotomicShellNumerator_eq_denom_shellProjector
#print axioms KomorebiCrossRadix.dftShellProjector_int_cast_eq_inv_smul_numerator
#print axioms KomorebiCrossRadix.mem_CyclotomicShellGoodLattice_iff_projector_integral
