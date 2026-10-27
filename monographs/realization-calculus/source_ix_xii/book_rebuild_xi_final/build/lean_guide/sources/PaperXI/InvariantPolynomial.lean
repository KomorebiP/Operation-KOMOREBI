import PaperXI.InertiaFixed
import PaperXI.CyclicPolynomial

/-! The local polynomial is attached to Frobenius restricted to the actual
invariant subspace. Its determinant meaning is proved before its evaluation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InvariantPolynomial
open Polynomial
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.InertiaFixed
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

def operatorPolynomial [FiniteDimensional K V] (F : Module.End K V) : K[X] :=
  F.charpoly.reverse

theorem operatorPolynomial_eq_det [FiniteDimensional K V] (F : Module.End K V)
    {ι : Type*} [Fintype ι] [DecidableEq ι] (b : Module.Basis ι K V) :
    operatorPolynomial F = Matrix.det (1 - (X : K[X]) • (LinearMap.toMatrix b b F).map C) := by
  rw [operatorPolynomial, ← LinearMap.charpoly_toMatrix F b, Matrix.reverse_charpoly]
  rfl

theorem operatorPolynomial_of_subsingleton [FiniteDimensional K V] [Subsingleton V]
    (F : Module.End K V) : operatorPolynomial F = 1 := by
  have hF : F = 0 := Subsingleton.elim _ _
  simp [operatorPolynomial, hF, Module.finrank_zero_of_subsingleton, Polynomial.reverse]

variable {W : Type*} [AddCommGroup W] [Module K W]

theorem operatorPolynomial_conj [FiniteDimensional K V] [FiniteDimensional K W]
    (e : V ≃ₗ[K] W) (F : Module.End K V) :
    operatorPolynomial (e.conj F) = operatorPolynomial F := by
  simp [operatorPolynomial]

variable {U : Type*} [AddCommGroup U] [Module ℂ U]
variable {M : ℕ} [NeZero M]

/-- Frobenius and its inverse act on the actual Mathlib invariant subspace. -/
def fixedFrobenius (ρ : Action (K := ℂ) (V := U) (M := M))
    (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) :
    ρ.invariants ≃ₗ[ℂ] ρ.invariants where
  toFun v := ⟨F v, fixed_forward ρ F q h v.property⟩
  invFun v := ⟨F.symm v, fixed_backward ρ F q h v.property⟩
  left_inv v := by ext; simp
  right_inv v := by ext; simp
  map_add' v w := by ext; simp
  map_smul' c v := by ext; simp

theorem fixedFrobenius_apply (ρ : Action (K := ℂ) (V := U) (M := M))
    (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (v : ρ.invariants) :
    (fixedFrobenius ρ F q h v : U) = F v := rfl

/-- This definition uses the restricted operator, with no case split on a label. -/
def localPolynomial [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) : ℂ[X] :=
  operatorPolynomial (fixedFrobenius ρ F q h).toLinearMap

theorem localPolynomial_eq_det [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {ι : Type*} [Fintype ι] [DecidableEq ι] (b : Module.Basis ι ℂ ρ.invariants) :
    localPolynomial ρ F q h = Matrix.det
      (1 - (X : ℂ[X]) • (LinearMap.toMatrix b b (fixedFrobenius ρ F q h).toLinearMap).map C) :=
  operatorPolynomial_eq_det _ b

theorem fixed_conj_of_top (ρ : Action (K := ℂ) (V := U) (M := M))
    (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (htop : ρ.invariants = ⊤) :
    (LinearEquiv.ofTop ρ.invariants htop).conj (fixedFrobenius ρ F q h).toLinearMap =
      F.toLinearMap := by
  ext v
  simp [LinearEquiv.conj_apply_apply, fixedFrobenius]

theorem localPolynomial_of_top [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (htop : ρ.invariants = ⊤) :
    localPolynomial ρ F q h = operatorPolynomial F.toLinearMap := by
  rw [localPolynomial, ← operatorPolynomial_conj (LinearEquiv.ofTop ρ.invariants htop),
    fixed_conj_of_top]

theorem localPolynomial_of_bot [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (hbot : ρ.invariants = ⊥) :
    localPolynomial ρ F q h = 1 := by
  have : Subsingleton ρ.invariants := Submodule.subsingleton_iff_eq_bot.mpr hbot
  exact operatorPolynomial_of_subsingleton _

end PaperXI.InvariantPolynomial
