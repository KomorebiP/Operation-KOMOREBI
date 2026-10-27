module

public import Mathlib.Analysis.Complex.Circle
public import Mathlib.Data.Fin.VecNotation
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Group

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Four-spinor Clifford transport with genuine unit-circle phases

This module gives the concrete local transport layer required by the
finite-resolution side of Komorebi Physics.  Spatial channels are the
complementary spectral projectors of the three Dirac `alpha` involutions.
All link and gauge phases live in `Circle`, so scalar transport has modulus
one by construction.
-/

namespace KomorebiPhysics
namespace Relativistic3DCliffordTransportU1

abbrev Spinor := Fin 4 → ℂ

/-- A complex-linear involution on four-spinors. -/
structure CliffordInvolution where
  act : Spinor → Spinor
  map_add : ∀ ψ φ, act (ψ + φ) = act ψ + act φ
  map_smul : ∀ (c : ℂ) ψ, act (c • ψ) = c • act ψ
  square : ∀ ψ, act (act ψ) = ψ

namespace CliffordInvolution

@[simp] theorem map_zero (A : CliffordInvolution) : A.act 0 = 0 := by
  have h : A.act 0 + A.act 0 = A.act 0 + 0 := by
    simpa only [zero_add, add_zero] using
      (A.map_add (0 : Spinor) (0 : Spinor)).symm
  exact add_left_cancel h

@[simp] theorem map_neg (A : CliffordInvolution) (ψ : Spinor) :
    A.act (-ψ) = -A.act ψ := by
  have h : A.act ψ + A.act (-ψ) = 0 := by
    calc
      A.act ψ + A.act (-ψ) = A.act (ψ + -ψ) :=
        (A.map_add ψ (-ψ)).symm
      _ = A.act 0 := by rw [add_neg_cancel]
      _ = 0 := A.map_zero
  exact eq_neg_of_add_eq_zero_right h

@[simp] theorem map_sub (A : CliffordInvolution) (ψ φ : Spinor) :
    A.act (ψ - φ) = A.act ψ - A.act φ := by
  rw [sub_eq_add_neg, A.map_add, A.map_neg, sub_eq_add_neg]

/-- Positive spectral projector `(I + A)/2`. -/
def plus (A : CliffordInvolution) (ψ : Spinor) : Spinor :=
  (2 : ℂ)⁻¹ • (ψ + A.act ψ)

/-- Negative spectral projector `(I - A)/2`. -/
def minus (A : CliffordInvolution) (ψ : Spinor) : Spinor :=
  (2 : ℂ)⁻¹ • (ψ - A.act ψ)

@[simp] theorem plus_add (A : CliffordInvolution) (ψ φ : Spinor) :
    A.plus (ψ + φ) = A.plus ψ + A.plus φ := by
  ext j
  simp [plus, A.map_add]
  ring

@[simp] theorem minus_add (A : CliffordInvolution) (ψ φ : Spinor) :
    A.minus (ψ + φ) = A.minus ψ + A.minus φ := by
  ext j
  simp [minus, A.map_add]
  ring

@[simp] theorem plus_smul (A : CliffordInvolution) (c : ℂ) (ψ : Spinor) :
    A.plus (c • ψ) = c • A.plus ψ := by
  ext j
  simp [plus, A.map_smul]
  ring

@[simp] theorem minus_smul (A : CliffordInvolution) (c : ℂ) (ψ : Spinor) :
    A.minus (c • ψ) = c • A.minus ψ := by
  ext j
  simp [minus, A.map_smul]
  ring

@[simp] theorem plus_add_minus (A : CliffordInvolution) (ψ : Spinor) :
    A.plus ψ + A.minus ψ = ψ := by
  ext j
  simp [plus, minus]
  ring

@[simp] theorem plus_idem (A : CliffordInvolution) (ψ : Spinor) :
    A.plus (A.plus ψ) = A.plus ψ := by
  ext j
  simp [plus, A.map_add, A.map_smul, A.square]
  ring

@[simp] theorem minus_idem (A : CliffordInvolution) (ψ : Spinor) :
    A.minus (A.minus ψ) = A.minus ψ := by
  ext j
  simp [minus, A.map_smul, A.square]
  ring

@[simp] theorem plus_minus (A : CliffordInvolution) (ψ : Spinor) :
    A.plus (A.minus ψ) = 0 := by
  ext j
  simp [plus, minus, A.map_smul, A.square]
  ring

@[simp] theorem minus_plus (A : CliffordInvolution) (ψ : Spinor) :
    A.minus (A.plus ψ) = 0 := by
  ext j
  simp [plus, minus, A.map_add, A.map_smul, A.square]
  ring

end CliffordInvolution

/-- Standard Dirac `α₁`. -/
def alphaX (ψ : Spinor) : Spinor := ![ψ 3, ψ 2, ψ 1, ψ 0]

/-- Standard Dirac `α₂`. -/
def alphaY (ψ : Spinor) : Spinor :=
  ![-Complex.I * ψ 3, Complex.I * ψ 2,
    -Complex.I * ψ 1, Complex.I * ψ 0]

/-- Standard Dirac `α₃`. -/
def alphaZ (ψ : Spinor) : Spinor := ![ψ 2, -ψ 3, ψ 0, -ψ 1]

/-- Standard Dirac `β`. -/
def beta (ψ : Spinor) : Spinor := ![ψ 0, ψ 1, -ψ 2, -ψ 3]

/-- Concrete `x`-direction Clifford involution. -/
def cliffordX : CliffordInvolution where
  act := alphaX
  map_add := by
    intro ψ φ
    ext j
    fin_cases j <;> rfl
  map_smul := by
    intro c ψ
    ext j
    fin_cases j <;> rfl
  square := by
    intro ψ
    ext j
    fin_cases j <;> rfl

/-- Concrete `y`-direction Clifford involution. -/
def cliffordY : CliffordInvolution where
  act := alphaY
  map_add := by
    intro ψ φ
    ext j
    fin_cases j <;> simp [alphaY] <;> ring_nf
  map_smul := by
    intro c ψ
    ext j
    fin_cases j <;> simp [alphaY] <;> ring_nf
  square := by
    intro ψ
    ext j
    fin_cases j <;> simp [alphaY, ← mul_assoc, Complex.I_mul_I]

/-- Concrete `z`-direction Clifford involution. -/
def cliffordZ : CliffordInvolution where
  act := alphaZ
  map_add := by
    intro ψ φ
    ext j
    fin_cases j <;> simp [alphaZ, add_comm]
  map_smul := by
    intro c ψ
    ext j
    fin_cases j <;> simp [alphaZ]
  square := by
    intro ψ
    ext j
    fin_cases j <;> simp [alphaZ]

/-- The concrete spatial Clifford generators anticommute pairwise. -/
theorem alphaX_alphaY_anticommute (ψ : Spinor) :
    alphaX (alphaY ψ) = -alphaY (alphaX ψ) := by
  ext j
  fin_cases j <;> simp [alphaX, alphaY]

theorem alphaX_alphaZ_anticommute (ψ : Spinor) :
    alphaX (alphaZ ψ) = -alphaZ (alphaX ψ) := by
  ext j
  fin_cases j <;> simp [alphaX, alphaZ]

theorem alphaY_alphaZ_anticommute (ψ : Spinor) :
    alphaY (alphaZ ψ) = -alphaZ (alphaY ψ) := by
  ext j
  fin_cases j <;> simp [alphaY, alphaZ]

/-- Every spatial Clifford generator anticommutes with `β`. -/
theorem alphaX_beta_anticommute (ψ : Spinor) :
    alphaX (beta ψ) = -beta (alphaX ψ) := by
  ext j
  fin_cases j <;> simp [alphaX, beta]

theorem alphaY_beta_anticommute (ψ : Spinor) :
    alphaY (beta ψ) = -beta (alphaY ψ) := by
  ext j
  fin_cases j <;> simp [alphaY, beta]

theorem alphaZ_beta_anticommute (ψ : Spinor) :
    alphaZ (beta ψ) = -beta (alphaZ ψ) := by
  ext j
  fin_cases j <;> simp [alphaZ, beta]

/-- Multiplication by a genuine unit-circle phase. -/
def phaseMul (z : Circle) (ψ : Spinor) : Spinor := (z : ℂ) • ψ

@[simp] theorem phaseMul_one (ψ : Spinor) : phaseMul 1 ψ = ψ := by
  simp [phaseMul]

@[simp] theorem phaseMul_zero (z : Circle) : phaseMul z 0 = 0 := by
  simp [phaseMul]

@[simp] theorem phaseMul_mul (z w : Circle) (ψ : Spinor) :
    phaseMul z (phaseMul w ψ) = phaseMul (z * w) ψ := by
  ext j
  simp [phaseMul, mul_assoc]

@[simp] theorem phaseMul_add (z : Circle) (ψ φ : Spinor) :
    phaseMul z (ψ + φ) = phaseMul z ψ + phaseMul z φ := by
  ext j
  simp [phaseMul, mul_add]

@[simp] theorem phaseMul_inv_left (z : Circle) (ψ : Spinor) :
    phaseMul z⁻¹ (phaseMul z ψ) = ψ := by
  rw [phaseMul_mul]
  simp

@[simp] theorem phaseMul_inv_right (z : Circle) (ψ : Spinor) :
    phaseMul z (phaseMul z⁻¹ ψ) = ψ := by
  rw [phaseMul_mul]
  simp

@[simp] theorem plus_phaseMul (A : CliffordInvolution) (z : Circle) (ψ : Spinor) :
    A.plus (phaseMul z ψ) = phaseMul z (A.plus ψ) := by
  exact A.plus_smul (z : ℂ) ψ

@[simp] theorem minus_phaseMul (A : CliffordInvolution) (z : Circle) (ψ : Spinor) :
    A.minus (phaseMul z ψ) = phaseMul z (A.minus ψ) := by
  exact A.minus_smul (z : ℂ) ψ

section Position

variable {Site : Type*}

abbrev State := Site → Spinor
abbrev Link := Site → Circle
abbrev Gauge := Site → Circle

/-- Sitewise gauge action. -/
def gaugeState (g : Gauge (Site := Site)) (ψ : State (Site := Site)) :
    State (Site := Site) := fun x => phaseMul (g x) (ψ x)

/-- Gauge transform of a link oriented from `x` to `τ x`. -/
def gaugeLink (τ : Site ≃ Site) (g : Gauge (Site := Site))
    (u : Link (Site := Site)) : Link (Site := Site) :=
  fun x => g (τ x) * u x * (g x)⁻¹

/-- Positive-channel gauge factor cancellation. -/
theorem gaugeLink_source_mul (τ : Site ≃ Site)
    (g : Gauge (Site := Site)) (u : Link (Site := Site)) (x : Site) :
    gaugeLink τ g u (τ.symm x) * g (τ.symm x) =
      g x * u (τ.symm x) := by
  simp [gaugeLink, mul_assoc]

/-- Negative-channel gauge factor cancellation. -/
theorem gaugeLink_inv_target_mul (τ : Site ≃ Site)
    (g : Gauge (Site := Site)) (u : Link (Site := Site)) (x : Site) :
    (gaugeLink τ g u x)⁻¹ * g (τ x) = g x * (u x)⁻¹ := by
  simp only [gaugeLink]
  group

/-- Directional projector transport. -/
def directionalShift (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    State (Site := Site) := fun x =>
  phaseMul (u (τ.symm x)) (A.plus (ψ (τ.symm x))) +
  phaseMul (u x)⁻¹ (A.minus (ψ (τ x)))

/-- Exact inverse transport. -/
def directionalShiftInv (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    State (Site := Site) := fun x =>
  phaseMul (u x)⁻¹ (A.plus (ψ (τ x))) +
  phaseMul (u (τ.symm x)) (A.minus (ψ (τ.symm x)))

@[simp] theorem directionalShiftInv_shift
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    directionalShiftInv A τ u (directionalShift A τ u ψ) = ψ := by
  funext x
  simp [directionalShiftInv, directionalShift]

@[simp] theorem directionalShift_shiftInv
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    directionalShift A τ u (directionalShiftInv A τ u ψ) = ψ := by
  funext x
  simp [directionalShiftInv, directionalShift]

/-- Exact reversible equivalence. -/
def directionalShiftEquiv (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) : State (Site := Site) ≃ State (Site := Site) where
  toFun := directionalShift A τ u
  invFun := directionalShiftInv A τ u
  left_inv := directionalShiftInv_shift A τ u
  right_inv := directionalShift_shiftInv A τ u

/-- Gauge covariance of one directional shift. -/
theorem directionalShift_gauge_covariant
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (g : Gauge (Site := Site)) (u : Link (Site := Site))
    (ψ : State (Site := Site)) :
    directionalShift A τ (gaugeLink τ g u) (gaugeState g ψ) =
      gaugeState g (directionalShift A τ u ψ) := by
  funext x
  simp only [directionalShift, gaugeState, plus_phaseMul, minus_phaseMul,
    phaseMul_mul, phaseMul_add]
  rw [gaugeLink_source_mul, gaugeLink_inv_target_mul]

/-- A local complex-linear reversible spin step. -/
structure LocalStep where
  toFun : Spinor → Spinor
  invFun : Spinor → Spinor
  left_inv : Function.LeftInverse invFun toFun
  right_inv : Function.RightInverse invFun toFun
  phase_commutes : ∀ z ψ, toFun (phaseMul z ψ) = phaseMul z (toFun ψ)
  inv_phase_commutes : ∀ z ψ, invFun (phaseMul z ψ) = phaseMul z (invFun ψ)

namespace LocalStep

def apply (M : LocalStep) (ψ : State (Site := Site)) : State (Site := Site) :=
  fun x => M.toFun (ψ x)

def applyInv (M : LocalStep) (ψ : State (Site := Site)) : State (Site := Site) :=
  fun x => M.invFun (ψ x)

@[simp] theorem applyInv_apply (M : LocalStep) (ψ : State (Site := Site)) :
    M.applyInv (M.apply ψ) = ψ := by
  funext x
  exact M.left_inv _

@[simp] theorem apply_applyInv (M : LocalStep) (ψ : State (Site := Site)) :
    M.apply (M.applyInv ψ) = ψ := by
  funext x
  exact M.right_inv _

theorem apply_gauge (M : LocalStep) (g : Gauge (Site := Site))
    (ψ : State (Site := Site)) :
    M.apply (gaugeState g ψ) = gaugeState g (M.apply ψ) := by
  funext x
  exact M.phase_commutes _ _

end LocalStep

/-- Concrete opposite `β` phases on upper and lower Dirac components. -/
def betaPhase (z : Circle) : LocalStep where
  toFun := fun ψ => ![(z : ℂ) * ψ 0, (z : ℂ) * ψ 1,
    ((z⁻¹ : Circle) : ℂ) * ψ 2, ((z⁻¹ : Circle) : ℂ) * ψ 3]
  invFun := fun ψ => ![((z⁻¹ : Circle) : ℂ) * ψ 0, ((z⁻¹ : Circle) : ℂ) * ψ 1,
    (z : ℂ) * ψ 2, (z : ℂ) * ψ 3]
  left_inv := by
    intro ψ
    ext j
    fin_cases j <;> simp
  right_inv := by
    intro ψ
    ext j
    fin_cases j <;> simp
  phase_commutes := by
    intro w ψ
    ext j
    fin_cases j <;> simp [phaseMul, mul_left_comm]
  inv_phase_commutes := by
    intro w ψ
    ext j
    fin_cases j <;> simp [phaseMul, mul_left_comm]

/-- Exact local seven-factor walk. -/
def sevenFactorWalk (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ : State (Site := Site)) : State (Site := Site) :=
  M.apply (directionalShift cliffordX τx ux
    (directionalShift cliffordY τy uy
      (directionalShift cliffordZ τz uz
        (directionalShift cliffordY τy uy
          (directionalShift cliffordX τx ux (M.apply ψ))))))

/-- Explicit inverse of the seven-factor walk. -/
def sevenFactorWalkInv (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ : State (Site := Site)) : State (Site := Site) :=
  M.applyInv (directionalShiftInv cliffordX τx ux
    (directionalShiftInv cliffordY τy uy
      (directionalShiftInv cliffordZ τz uz
        (directionalShiftInv cliffordY τy uy
          (directionalShiftInv cliffordX τx ux (M.applyInv ψ))))))

@[simp] theorem sevenFactorWalkInv_walk (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ : State (Site := Site)) :
    sevenFactorWalkInv M τx τy τz ux uy uz
      (sevenFactorWalk M τx τy τz ux uy uz ψ) = ψ := by
  simp [sevenFactorWalkInv, sevenFactorWalk]

@[simp] theorem sevenFactorWalk_walkInv (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ : State (Site := Site)) :
    sevenFactorWalk M τx τy τz ux uy uz
      (sevenFactorWalkInv M τx τy τz ux uy uz ψ) = ψ := by
  simp [sevenFactorWalkInv, sevenFactorWalk]

/-- Exact reversible equivalence of the full local walk. -/
def sevenFactorWalkEquiv (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site)) :
    State (Site := Site) ≃ State (Site := Site) where
  toFun := sevenFactorWalk M τx τy τz ux uy uz
  invFun := sevenFactorWalkInv M τx τy τz ux uy uz
  left_inv := sevenFactorWalkInv_walk M τx τy τz ux uy uz
  right_inv := sevenFactorWalk_walkInv M τx τy τz ux uy uz

/-- Exact gauge covariance of the full local walk. -/
theorem sevenFactorWalk_gauge_covariant (M : LocalStep)
    (τx τy τz : Site ≃ Site) (g : Gauge (Site := Site))
    (ux uy uz : Link (Site := Site)) (ψ : State (Site := Site)) :
    sevenFactorWalk M τx τy τz
      (gaugeLink τx g ux) (gaugeLink τy g uy) (gaugeLink τz g uz)
      (gaugeState g ψ) =
    gaugeState g (sevenFactorWalk M τx τy τz ux uy uz ψ) := by
  simp only [sevenFactorWalk]
  rw [LocalStep.apply_gauge]
  rw [directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant]
  rw [LocalStep.apply_gauge]

/-- One undirected lattice step. -/
def AxisStep (τ : Site ≃ Site) (x y : Site) : Prop := y = τ.symm x ∨ y = τ x

/-- The five translated factors determine a radius-five discrete causal cone. -/
def FiveStepReach (τx τy τz : Site ≃ Site) (x y : Site) : Prop :=
  ∃ x₁ x₂ x₃ x₄,
    AxisStep τx x x₁ ∧ AxisStep τy x₁ x₂ ∧ AxisStep τz x₂ x₃ ∧
    AxisStep τy x₃ x₄ ∧ AxisStep τx x₄ y

/-- A one-axis output vanishes when both source spinors vanish. -/
theorem directionalShift_zero_of_sources (A : CliffordInvolution)
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ : State (Site := Site)) (x : Site)
    (h₁ : ψ (τ.symm x) = 0) (h₂ : ψ (τ x) = 0) :
    directionalShift A τ u ψ x = 0 := by
  simp [directionalShift, h₁, h₂, CliffordInvolution.plus,
    CliffordInvolution.minus, phaseMul]

end Position

end Relativistic3DCliffordTransportU1
end KomorebiPhysics
