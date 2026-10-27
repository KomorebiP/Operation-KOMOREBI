import CrossRadixReynoldsDFT
import CrossRadixCyclotomicClosure
import Mathlib.Analysis.Fourier.ZMod

noncomputable section
open Polynomial

namespace KomorebiCrossRadix

/-- Affine polynomial substitution by `X ↦ aX+b` is a linear equivalence over `ℂ`
whenever `a ≠ 0`. The inverse is `X ↦ a⁻¹(X-b)`. -/
def affinePolynomialEquiv (a b : ℂ) (ha : a ≠ 0) : Polynomial ℂ ≃ₗ[ℂ] Polynomial ℂ where
  toFun p := p.comp (C a * X + C b)
  invFun p := p.comp (C a⁻¹ * (X - C b))
  map_add' p q := by simp
  map_smul' c p := by
    simp only [smul_eq_C_mul, mul_comp, C_comp, RingHom.id_apply]
  left_inv p := by
    change (p.comp (C a * X + C b)).comp (C a⁻¹ * (X - C b)) = p
    rw [comp_assoc]
    simp only [add_comp, mul_comp, C_comp, X_comp]
    rw [← mul_assoc, ← C_mul, mul_inv_cancel₀ ha, C_1, one_mul, sub_add_cancel, comp_X]
  right_inv p := by
    change (p.comp (C a⁻¹ * (X - C b))).comp (C a * X + C b) = p
    rw [comp_assoc]
    simp only [sub_comp, mul_comp, C_comp, X_comp]
    rw [add_sub_cancel_right, ← mul_assoc, ← C_mul, inv_mul_cancel₀ ha, C_1, one_mul, comp_X]

@[simp] lemma affinePolynomialEquiv_apply
    (a b : ℂ) (ha : a ≠ 0) (p : Polynomial ℂ) :
    affinePolynomialEquiv a b ha p = p.comp (C a * X + C b) := rfl

abbrev PolynomialResidueProfile (T : ℕ) := ZMod T → Polynomial ℂ

variable {T : ℕ}

/-- The divisor width mask acting on polynomial-valued Fourier coefficients. -/
def polyFreqWidthEnd (g : DivIdx T) : Module.End ℂ (PolynomialResidueProfile T) where
  toFun := fun x k => rawWidthMask g k • x k
  map_add' := by
    intro x y
    funext k
    exact smul_add (rawWidthMask g k) (x k) (y k)
  map_smul' := by
    intro a x
    funext k
    exact smul_comm (rawWidthMask g k) a (x k)

@[simp] lemma polyFreqWidthEnd_apply
    (g : DivIdx T) (x : PolynomialResidueProfile T) (k : ZMod T) :
    polyFreqWidthEnd g x k = rawWidthMask g k • x k := rfl

lemma polyFreqWidthEnd_idempotent (g : DivIdx T) :
    (polyFreqWidthEnd g).comp (polyFreqWidthEnd g) = polyFreqWidthEnd g := by
  apply LinearMap.ext
  intro x
  funext k
  simp only [LinearMap.comp_apply, polyFreqWidthEnd_apply, rawWidthMask]
  split <;> simp

section Fourier
variable [NeZero T]

/-- Polynomial-valued physical width projector, again defined by exact DFT conjugation. -/
def polyReynoldsProjector (g : DivIdx T) : Module.End ℂ (PolynomialResidueProfile T) :=
  (ZMod.dft (N := T) (E := Polynomial ℂ)).symm.toLinearMap.comp
    ((polyFreqWidthEnd g).comp (ZMod.dft (N := T) (E := Polynomial ℂ)).toLinearMap)

lemma dft_polyReynoldsProjector (g : DivIdx T) (x : PolynomialResidueProfile T) :
    ZMod.dft (N := T) (E := Polynomial ℂ) (polyReynoldsProjector g x) =
      polyFreqWidthEnd g (ZMod.dft (N := T) (E := Polynomial ℂ) x) := by
  simp [polyReynoldsProjector]

lemma polyReynoldsProjector_idempotent (g : DivIdx T) :
    (polyReynoldsProjector g).comp (polyReynoldsProjector g) = polyReynoldsProjector g := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := Polynomial ℂ)).injective
  simp only [LinearMap.comp_apply, dft_polyReynoldsProjector]
  exact LinearMap.congr_fun (polyFreqWidthEnd_idempotent g) _

end Fourier

/-- Pointwise affine substitution on a polynomial-valued residue profile. -/
def profileAffineEquiv (T : ℕ) (a b : ℂ) (ha : a ≠ 0) :
    PolynomialResidueProfile T ≃ₗ[ℂ] PolynomialResidueProfile T where
  toFun x k := affinePolynomialEquiv a b ha (x k)
  invFun x k := (affinePolynomialEquiv a b ha).symm (x k)
  left_inv x := by
    funext k
    exact (affinePolynomialEquiv a b ha).left_inv (x k)
  right_inv x := by
    funext k
    exact (affinePolynomialEquiv a b ha).right_inv (x k)
  map_add' x y := by
    funext k
    exact (affinePolynomialEquiv a b ha).map_add (x k) (y k)
  map_smul' c x := by
    funext k
    exact (affinePolynomialEquiv a b ha).map_smul c (x k)

/-- Canonical divisor width induced by a section width `m`: `g = gcd(T,m)`. -/
def gcdDivIdx (hT : 0 < T) (m : ℕ) : DivIdx T :=
  ⟨Nat.gcd T m, Nat.mem_divisors.mpr ⟨Nat.gcd_dvd_left T m, hT.ne'⟩⟩

@[simp] lemma gcdDivIdx_val (hT : 0 < T) (m : ℕ) :
    (gcdDivIdx hT m).1 = Nat.gcd T m := rfl

lemma natCast_complex_ne_zero_of_pos {m : ℕ} (hm : 0 < m) : (m : ℂ) ≠ 0 := by
  exact_mod_cast hm.ne'

/-- The baseline affine substitution is exactly the forward map of the affine polynomial equivalence. -/
lemma affinePolynomialEquiv_nat_apply
    (m r : ℕ) (hm : 0 < m) (p : Polynomial ℂ) :
    affinePolynomialEquiv (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm) p =
      affineSubst p m r := by
  rfl

/-- Normal form `A = P ∘ U`: `U` is reversible affine polynomial bookkeeping and `P`
is the residue-alias projector. -/
def projectorSectionNormalForm
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) : Module.End ℂ V :=
  P.comp U.toLinearMap

/-- Explicit generalized inverse `B = U⁻¹ ∘ P` for an idempotent projector normal form. -/
def projectorDecoder
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) : Module.End ℂ V :=
  U.symm.toLinearMap.comp P

lemma projectorSection_decoder_AB
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) (hP : P.comp P = P) :
    (projectorSectionNormalForm P U).comp (projectorDecoder P U) = P := by
  apply LinearMap.ext
  intro x
  simp [projectorSectionNormalForm, projectorDecoder, LinearMap.comp_apply]
  exact LinearMap.congr_fun hP x

lemma projectorSection_decoder_ABA
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) (hP : P.comp P = P) :
    ((projectorSectionNormalForm P U).comp (projectorDecoder P U)).comp
        (projectorSectionNormalForm P U) = projectorSectionNormalForm P U := by
  rw [projectorSection_decoder_AB P U hP]
  apply LinearMap.ext
  intro x
  change P (P (U x)) = P (U x)
  exact LinearMap.congr_fun hP (U x)

lemma projectorSection_decoder_BAB
    {V : Type*} [AddCommMonoid V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) (hP : P.comp P = P) :
    ((projectorDecoder P U).comp (projectorSectionNormalForm P U)).comp
        (projectorDecoder P U) = projectorDecoder P U := by
  apply LinearMap.ext
  intro x
  simp [projectorSectionNormalForm, projectorDecoder, LinearMap.comp_apply]
  calc
    P (P (P x)) = P (P x) := LinearMap.congr_fun hP (P x)
    _ = P x := LinearMap.congr_fun hP x

section AffineSectionDecoder

variable [NeZero T]

/-- The positive-width affine section normal form on polynomial residue profiles. -/
def affineSectionNormalForm
    (hT : 0 < T) (m r : ℕ) (hm : 0 < m) : Module.End ℂ (PolynomialResidueProfile T) :=
  projectorSectionNormalForm
    (polyReynoldsProjector (gcdDivIdx hT m))
    (profileAffineEquiv T (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm))

/-- Explicit affine decoder for the normal form. -/
def affineSectionDecoder
    (hT : 0 < T) (m r : ℕ) (hm : 0 < m) : Module.End ℂ (PolynomialResidueProfile T) :=
  projectorDecoder
    (polyReynoldsProjector (gcdDivIdx hT m))
    (profileAffineEquiv T (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm))

/-- `A B = P_m`: the decoder isolates all loss in the residue-alias projector. -/
lemma affineSection_decoder_AB
    (hT : 0 < T) (m r : ℕ) (hm : 0 < m) :
    (affineSectionNormalForm hT m r hm).comp (affineSectionDecoder hT m r hm) =
      polyReynoldsProjector (gcdDivIdx hT m) := by
  exact projectorSection_decoder_AB _ _
    (polyReynoldsProjector_idempotent (gcdDivIdx hT m))

lemma affineSection_decoder_ABA
    (hT : 0 < T) (m r : ℕ) (hm : 0 < m) :
    ((affineSectionNormalForm hT m r hm).comp (affineSectionDecoder hT m r hm)).comp
      (affineSectionNormalForm hT m r hm) = affineSectionNormalForm hT m r hm := by
  exact projectorSection_decoder_ABA _ _
    (polyReynoldsProjector_idempotent (gcdDivIdx hT m))

lemma affineSection_decoder_BAB
    (hT : 0 < T) (m r : ℕ) (hm : 0 < m) :
    ((affineSectionDecoder hT m r hm).comp (affineSectionNormalForm hT m r hm)).comp
      (affineSectionDecoder hT m r hm) = affineSectionDecoder hT m r hm := by
  exact projectorSection_decoder_BAB _ _
    (polyReynoldsProjector_idempotent (gcdDivIdx hT m))

end AffineSectionDecoder

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.affinePolynomialEquiv_nat_apply
#print axioms KomorebiCrossRadix.affineSection_decoder_AB
#print axioms KomorebiCrossRadix.affineSection_decoder_ABA
#print axioms KomorebiCrossRadix.affineSection_decoder_BAB
