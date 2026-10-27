module
public import KnillLaflammeNecessity
import all KnillLaflammeNecessity
import all KnillLaflammeSufficiency
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
State-space versus operator-space exact correction: polarization and normalization.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix
variable {n : Type*} [Fintype n] [DecidableEq n]

def pure (x : n → ℂ) : Matrix n n ℂ := Matrix.vecMulVec x (star x)

theorem outer_polarization (x y : n → ℂ) :
    (4 : ℂ) • Matrix.vecMulVec x (star y) =
      pure (x+y) - pure (x-y) + Complex.I • (pure (x+Complex.I • y) - pure (x-Complex.I • y)) := by
  ext i j
  simp [pure, Matrix.vecMulVec, star_add, star_sub]
  ring_nf
  simp [Complex.I_sq]
  ring

theorem linearMap_eq_of_pure (f g : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ)
    (h : ∀ x, f (pure x)=g (pure x)) : f=g := by
  have outer (x y : n → ℂ) : f (Matrix.vecMulVec x (star y))=g (Matrix.vecMulVec x (star y)) := by
    apply (smul_right_injective (M := Matrix n n ℂ) (by norm_num : (4 : ℂ) ≠ 0))
    change (4 : ℂ) • f (Matrix.vecMulVec x (star y)) = (4 : ℂ) • g (Matrix.vecMulVec x (star y))
    rw [← map_smul, ← map_smul, outer_polarization]
    simp only [map_add, map_sub, map_smul, h]
  have single (i j : n) (c : ℂ) : f (Matrix.single i j c)=g (Matrix.single i j c) := by
    have hh := outer (Pi.single i c) (Pi.single j 1)
    have hs : Matrix.vecMulVec (Pi.single i c) (star (Pi.single j (1 : ℂ))) = Matrix.single i j c := by
      ext a b
      by_cases ha : i=a <;> by_cases hb : j=b <;>
        simp [Matrix.vecMulVec, Pi.single_apply, ha, hb, eq_comm]
    rwa [hs] at hh
  ext rho i j
  have heq : f rho=g rho := by
    conv_lhs => rw [Matrix.matrix_eq_sum_single rho]
    conv_rhs => rw [Matrix.matrix_eq_sum_single rho]
    simp only [map_sum, single]
  exact congrArg (fun M : Matrix n n ℂ => M i j) heq


/-- Finite Kraus sums as an actual complex-linear map. -/
def noiseLinear {I : Type*} [Fintype I] (E : I → Matrix n n ℂ) :
    Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ where
  toFun := noise E
  map_add' x y := by simp [noise, mul_add, add_mul, Finset.sum_add_distrib]
  map_smul' c x := by simp [noise, Finset.smul_sum]

def sandwichLinear (P : Matrix n n ℂ) : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ where
  toFun := fun rho => P*rho*star P
  map_add' x y := by simp [mul_add, add_mul]
  map_smul' c x := by simp

theorem sandwich_pure (P : Matrix n n ℂ) (x : n → ℂ) :
    sandwichLinear P (pure x)=pure (P *ᵥ x) := by
  simp only [sandwichLinear, LinearMap.coe_mk, AddHom.coe_mk, pure, Matrix.mul_vecMulVec, Matrix.vecMulVec_mul, star_mulVec]
  rfl

/-- Normalization is removed by linearity, including the zero positive matrix. -/
theorem fixes_positive_of_density (P : Matrix n n ℂ)
    (L : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ)
    (hfix : ∀ rho : Matrix n n ℂ, rho.PosSemidef → Matrix.trace rho=1 → P*rho*P=rho → L rho=rho)
    (rho : Matrix n n ℂ) (hpos : rho.PosSemidef) (hsupport : P*rho*P=rho) : L rho=rho := by
  by_cases hz : rho=0
  · simp [hz]
  have htr : Matrix.trace rho ≠ 0 := (hpos.trace_eq_zero_iff).not.mpr hz
  have hreal : ((Matrix.trace rho).re : ℂ)=Matrix.trace rho := by
    apply Complex.ext
    · simp
    · simpa using (RCLike.nonneg_iff.mp hpos.trace_nonneg).2.symm
  have ht : (Matrix.trace rho).re ≠ 0 := by
    intro hh
    apply htr
    rw [← hreal, hh, Complex.ofReal_zero]
  have hc : (((Matrix.trace rho).re)⁻¹ : ℂ) ≠ 0 := by exact_mod_cast inv_ne_zero ht
  let c : ℂ := ((Matrix.trace rho).re)⁻¹
  have hcpos : 0 ≤ c := by
    change 0 ≤ (((Matrix.trace rho).re)⁻¹ : ℂ)
    exact_mod_cast inv_nonneg.mpr (RCLike.nonneg_iff.mp hpos.trace_nonneg).1
  have hct : Matrix.trace (c • rho)=1 := by
    rw [Matrix.trace_smul, ← hreal]
    change (((Matrix.trace rho).re)⁻¹ : ℂ) * ((Matrix.trace rho).re : ℂ) = 1
    exact_mod_cast inv_mul_cancel₀ ht
  have hcs : P*(c • rho)*P=c • rho := by simp [hsupport]
  have hh := hfix (c • rho) (hpos.smul hcpos) hct hcs
  rw [map_smul] at hh
  exact smul_right_injective (M := Matrix n n ℂ) hc hh

/-- Agreement on normalized code density matrices implies agreement on every code operator. -/
theorem fixes_operators_of_density (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (L : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ)
    (hfix : ∀ rho : Matrix n n ℂ, rho.PosSemidef → Matrix.trace rho=1 → P*rho*P=rho → L rho=rho)
    (rho : Matrix n n ℂ) (hsupport : P*rho*P=rho) : L rho=rho := by
  have heq : L.comp (sandwichLinear P)=sandwichLinear P := by
    apply linearMap_eq_of_pure
    intro x
    change L (sandwichLinear P (pure x)) = sandwichLinear P (pure x)
    apply fixes_positive_of_density P L hfix
    · rw [sandwich_pure]
      exact Matrix.posSemidef_vecMulVec_self_star _
    · change P*(P*pure x*star P)*P=P*pure x*star P
      rw [hP.isSelfAdjoint.star_eq]
      simp only [← mul_assoc, hP.isIdempotentElem.eq]
      rw [mul_assoc (P*pure x), hP.isIdempotentElem.eq]
  have hh := congrArg (fun f : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ => f rho) heq
  simpa [sandwichLinear, hP.isSelfAdjoint.star_eq, hsupport] using hh

/-- Physical density-state correctness and code-operator correctness are equivalent. -/
theorem density_corrects_iff_operators {I J : Type*} [Fintype I] [Fintype J]
    (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ) :
    (∀ rho : Matrix n n ℂ, rho.PosSemidef → Matrix.trace rho=1 → P*rho*P=rho →
      noise R (noise E rho)=rho) ↔
    (∀ rho : Matrix n n ℂ, P*rho*P=rho → noise R (noise E rho)=rho) := by
  constructor
  · intro hh rho hs
    exact fixes_operators_of_density P hP ((noiseLinear R).comp (noiseLinear E)) hh rho hs
  · intro hh rho _ _ hs
    exact hh rho hs


def StateCorrectable {I : Type*} [Fintype I] (P : Matrix n n ℂ) (E : I → Matrix n n ℂ) : Prop :=
  ∃ m : ℕ, ∃ R : Fin m → Matrix n n ℂ,
    (∑ r, star (R r)*R r)=1 ∧
    ∀ rho : Matrix n n ℂ, rho.PosSemidef → Matrix.trace rho=1 → P*rho*P=rho →
      noise R (noise E rho)=rho

/-- The physical-state formulation of the full finite channel criterion. -/
theorem state_correctable_iff_gram {I : Type*} [Fintype I] [DecidableEq I]
    (P : Matrix n n ℂ) (hP : IsStarProjection P) (E : I → Matrix n n ℂ)
    (hE : (∑ a, star (E a)*E a)=1) :
    StateCorrectable P E ↔ ∃ C : Matrix I I ℂ, C.PosSemidef ∧
      ∀ a b, P*star (E a)*E b*P=C a b • P := by
  rw [← correctable_iff_gram P hP E hE]
  constructor
  · rintro ⟨m,R,hR,hcorrect⟩
    exact ⟨m,R,hR,(density_corrects_iff_operators P hP E R).mp hcorrect⟩
  · rintro ⟨m,R,hR,hcorrect⟩
    exact ⟨m,R,hR,(density_corrects_iff_operators P hP E R).mpr hcorrect⟩

open scoped Kronecker

def amplifiedNoise {I J : Type*} [Fintype I] [Fintype J] [DecidableEq J]
    (E : I → Matrix n n ℂ) (rho : Matrix (J × n) (J × n) ℂ) : Matrix (J × n) (J × n) ℂ :=
  noise (fun a => (1 : Matrix J J ℂ) ⊗ₖ E a) rho

theorem amplifiedNoise_block {I J : Type*} [Fintype I] [Fintype J] [DecidableEq J]
    (E : I → Matrix n n ℂ) (rho : Matrix (J × n) (J × n) ℂ) (i j : J) (u v : n) :
    amplifiedNoise E rho (i,u) (j,v) = noise E (fun a b => rho (i,a) (j,b)) u v := by
  simp [amplifiedNoise, noise, Matrix.sum_apply, Matrix.mul_apply, Matrix.star_apply,
    Matrix.kroneckerMap_apply, Fintype.sum_prod_type, Matrix.one_apply, apply_ite]

/-- Exact correction persists for arbitrary finite reference systems, including entangled states. -/
theorem recovery_with_reference {I J A : Type*} [Fintype I] [Fintype J] [Fintype A] [DecidableEq A]
    (P : Matrix n n ℂ) (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ)
    (hcorrect : ∀ rho, P*rho*P=rho → noise R (noise E rho)=rho)
    (rho : Matrix (A × n) (A × n) ℂ)
    (hs : ((1 : Matrix A A ℂ) ⊗ₖ P)*rho*((1 : Matrix A A ℂ) ⊗ₖ P)=rho) :
    amplifiedNoise R (amplifiedNoise E rho)=rho := by
  have hblock (i j : A) :
      P*(Matrix.of fun a b => rho (i,a) (j,b))*P=(Matrix.of fun a b => rho (i,a) (j,b)) := by
    ext u v
    have hh := congrArg (fun M : Matrix (A × n) (A × n) ℂ => M (i,u) (j,v)) hs
    simpa [Matrix.mul_apply, Matrix.kroneckerMap_apply, Fintype.sum_prod_type, Matrix.one_apply] using hh
  ext ⟨i,u⟩ ⟨j,v⟩
  rw [amplifiedNoise_block]
  have hin : (fun a b => amplifiedNoise E rho (i,a) (j,b)) =
      noise E (fun a b => rho (i,a) (j,b)) := by
    ext a b
    exact amplifiedNoise_block E rho i j a b
  rw [hin, hcorrect _ (hblock i j)]

end KomorebiPaperVII.KnillLaflamme
