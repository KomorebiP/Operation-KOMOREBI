module
public import DensePadicIsometry
public import RationalPadicEmbedding
public import DyadicPacketRational

/-!
# Isometric bijections from the four actual dyadic Euler packets

Author: Komorebi P.
The normalized maps are isometries of the dyadic integers. The original
coefficients instead fill their exact factorial-centered affine images.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicFourIsometry

open Congruential DyadicFourLeastPeriods

def samples (j : ℕ) (hj : j < 4) : ℕ → ℤ_[2] :=
  RationalPadicEmbedding.samples 2 (DyadicPacketRational.packet j)
    (DyadicPacketRational.packet_zero j) (fun m n => DyadicPacketRational.norm_sub j m n hj)

@[simp]
theorem samples_coe (j : ℕ) (hj : j < 4) (n : ℕ) :
    (samples j hj n : ℚ_[2]) = (DyadicPacketRational.packet j n : ℚ_[2]) := rfl

theorem samples_dist (j : ℕ) (hj : j < 4) (m n : ℕ) :
    dist (samples j hj m) (samples j hj n) = dist (m : ℤ_[2]) (n : ℤ_[2]) :=
  RationalPadicEmbedding.samples_dist 2 (DyadicPacketRational.packet j)
    (DyadicPacketRational.packet_zero j) (fun a b => DyadicPacketRational.norm_sub j a b hj) m n

/-- The uniquely determined isometric bijection arising from the actual packet. -/
def isometry (j : ℕ) (hj : j < 4) : ℤ_[2] ≃ᵢ ℤ_[2] :=
  DensePadicIsometry.extensionEquiv 2 (samples j hj) (samples_dist j hj)

@[simp]
theorem isometry_nat (j : ℕ) (hj : j < 4) (n : ℕ) :
    (isometry j hj (n : ℤ_[2]) : ℚ_[2]) = (DyadicPacketRational.packet j n : ℚ_[2]) := by
  change (DensePadicIsometry.extensionEquiv 2 (samples j hj) (samples_dist j hj) n : ℚ_[2]) = _
  rw [DensePadicIsometry.extensionEquiv_nat, samples_coe]

@[simp]
theorem isometry_zero (j : ℕ) (hj : j < 4) : isometry j hj 0 = 0 := by
  apply PadicInt.ext
  simpa using isometry_nat j hj 0

theorem isometry_dist (j : ℕ) (hj : j < 4) (x y : ℤ_[2]) :
    dist (isometry j hj x) (isometry j hj y) = dist x y :=
  (isometry j hj).dist_eq x y

theorem isometry_surjective (j : ℕ) (hj : j < 4) :
    Function.Surjective (isometry j hj) := (isometry j hj).surjective

theorem isometry_continuous (j : ℕ) (hj : j < 4) :
    Continuous (isometry j hj) := (isometry j hj).continuous

/-- Uniqueness is among all continuous maps with the prescribed rational values. -/
theorem unique_continuous (j : ℕ) (hj : j < 4) (g : ℤ_[2] → ℤ_[2])
    (hg : Continuous g)
    (hgnat : ∀ n : ℕ, (g (n : ℤ_[2]) : ℚ_[2]) = (DyadicPacketRational.packet j n : ℚ_[2])) :
    g = isometry j hj := by
  apply DensePadicIsometry.extensionEquiv_unique_continuous 2 (samples j hj) (samples_dist j hj) g hg
  intro n
  exact PadicInt.ext (hgnat n)

/-- Every dyadic target has exactly one input under the normalized map. -/
theorem unique_preimage (j : ℕ) (hj : j < 4) (z : ℤ_[2]) :
    ∃! x : ℤ_[2], isometry j hj x = z := by
  refine ⟨(isometry j hj).symm z, (isometry j hj).apply_symm_apply z, ?_⟩
  intro x hx
  exact (isometry j hj).injective (hx.trans ((isometry j hj).apply_symm_apply z).symm)

/-- A literal existence-and-uniqueness theorem for an isometric bijection
interpolating the normalized actual rational coefficients. -/
theorem existsUnique_isometry (j : ℕ) (hj : j < 4) :
    ∃! e : ℤ_[2] ≃ᵢ ℤ_[2], ∀ n : ℕ,
      (e (n : ℤ_[2]) : ℚ_[2]) = (DyadicPacketRational.packet j n : ℚ_[2]) := by
  refine ⟨isometry j hj, isometry_nat j hj, ?_⟩
  intro e he
  apply IsometryEquiv.ext
  exact congrFun (unique_continuous j hj e e.continuous he)

/-- Undo the normalization to extend the original coefficients themselves. -/
def originalExtension (j : ℕ) (hj : j < 4) (x : ℤ_[2]) : ℤ_[2] :=
  (j.factorial : ℤ_[2]) + (2 : ℤ_[2]) ^ originalBonus j * isometry j hj x

theorem originalExtension_nat (j : ℕ) (hj : j < 4) (n : ℕ) :
    (originalExtension j hj (n : ℤ_[2]) : ℚ_[2]) = (unnormalized 4 j n : ℚ_[2]) := by
  simp only [originalExtension, PadicInt.coe_add, PadicInt.coe_mul, PadicInt.coe_pow,
    PadicInt.coe_natCast, isometry_nat]
  have htwo : ((2 : ℤ_[2]) : ℚ_[2]) = (2 : ℚ_[2]) := rfl
  rw [htwo]
  have he : (j.factorial : ℚ) + (2 : ℚ) ^ originalBonus j * DyadicPacketRational.packet j n =
      unnormalized 4 j n := by
    rw [DyadicPacketRational.packet]
    have hd : (2 : ℚ) ^ originalBonus j ≠ 0 := pow_ne_zero _ (by norm_num)
    field_simp
    ring
  simpa using congrArg (fun q : ℚ => (q : ℚ_[2])) he

theorem originalExtension_continuous (j : ℕ) (hj : j < 4) :
    Continuous (originalExtension j hj) :=
  continuous_const.add (continuous_const.mul (isometry_continuous j hj))

/-- The original continuous coefficients retain their exact displacement scale. -/
theorem originalExtension_dist (j : ℕ) (hj : j < 4) (x y : ℤ_[2]) :
    dist (originalExtension j hj x) (originalExtension j hj y) =
      (2 : ℝ) ^ (-(originalBonus j : ℤ)) * dist x y := by
  have hsub : originalExtension j hj x - originalExtension j hj y =
      (2 : ℤ_[2]) ^ originalBonus j * (isometry j hj x - isometry j hj y) := by
    unfold originalExtension
    ring
  have hn : ‖(2 : ℤ_[2]) ^ originalBonus j‖ = (2 : ℝ) ^ (-(originalBonus j : ℤ)) := by
    simpa using PadicInt.norm_p_pow (p := 2) (originalBonus j)
  rw [dist_eq_norm, hsub, norm_mul, hn, ← dist_eq_norm, isometry_dist]

theorem originalExtension_injective (j : ℕ) (hj : j < 4) :
    Function.Injective (originalExtension j hj) := by
  intro x y h
  have hd : (2 : ℤ_[2]) ^ originalBonus j ≠ 0 := pow_ne_zero _ (by norm_num)
  apply (isometry j hj).injective
  exact (mul_left_cancel₀ hd) (add_left_cancel h)

/-- Every point of the exact affine image has one original-packet preimage. -/
theorem unique_original_preimage (j : ℕ) (hj : j < 4) (z : ℤ_[2]) :
    ∃! x : ℤ_[2], originalExtension j hj x =
      (j.factorial : ℤ_[2]) + (2 : ℤ_[2]) ^ originalBonus j * z := by
  refine ⟨(isometry j hj).symm z, ?_, ?_⟩
  · simp only [originalExtension, (isometry j hj).apply_symm_apply]
  · intro x hx
    apply originalExtension_injective j hj
    simpa only [originalExtension, (isometry j hj).apply_symm_apply] using hx

theorem originalExtension_range (j : ℕ) (hj : j < 4) :
    Set.range (originalExtension j hj) =
      Set.range (fun z : ℤ_[2] => (j.factorial : ℤ_[2]) + (2 : ℤ_[2]) ^ originalBonus j * z) := by
  ext y
  constructor
  · rintro ⟨x, rfl⟩
    exact ⟨isometry j hj x, rfl⟩
  · rintro ⟨z, rfl⟩
    obtain ⟨x, hx, _⟩ := unique_original_preimage j hj z
    exact ⟨x, hx⟩

end KomorebiPaperIX.DyadicFourIsometry
