module

public import KomorebiPhysics.Relativistic3DCliffordTransportU1
public import KomorebiPhysics.LocalDiscreteGlobalContinuum
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Data.Fintype.BigOperators
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Tactic.Ring

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Hilbert-unitary Clifford transport and dyadic refinement

This module supplies the concrete finite-volume Hilbert certificate and the
adjacent-resolution intertwining theorem required by the local-discrete /
global-continuous Komorebi Physics programme.  Link and mass phases lie in the
genuine complex unit circle `Circle`.  The spatial transport channels are the
complementary spectral projectors of the Hermitian Dirac involutions.

The dyadic refinement used here is an exact cylinder refinement: every coarse
cell is replicated into two child cells, translations and links are pulled back,
and the child-cell measure is halved.  It proves exact dynamical compatibility
and Hilbert isometry for this refinement architecture.  It does not by itself
identify the completed tower with a continuum manifold or the continuum Dirac
operator.
-/

open scoped BigOperators ComplexConjugate
namespace KomorebiPhysics
namespace Relativistic3DCliffordHilbertRefinement

open Relativistic3DCliffordTransportU1

def ip (ψ φ : Spinor) : ℂ := ∑ j : Fin 4, (starRingEnd ℂ) (ψ j) * φ j

/-- The spinor self-inner-product is the real sum of coordinate norm squares. -/
@[simp] theorem ip_self_eq_normSq_sum (ψ : Spinor) :
    ip ψ ψ = ((∑ j : Fin 4, Complex.normSq (ψ j) : ℝ) : ℂ) := by
  simp [ip, mul_comm, Complex.mul_conj]

/-- Positivity of the finite four-spinor inner product. -/
theorem ip_self_re_nonneg (ψ : Spinor) : 0 ≤ (ip ψ ψ).re := by
  rw [ip_self_eq_normSq_sum]
  simp only [Complex.ofReal_re]
  exact Finset.sum_nonneg (fun j _ => Complex.normSq_nonneg (ψ j))

/-- Positive definiteness of the finite four-spinor inner product. -/
@[simp] theorem ip_self_eq_zero_iff (ψ : Spinor) : ip ψ ψ = 0 ↔ ψ = 0 := by
  rw [ip_self_eq_normSq_sum]
  constructor
  · intro h
    have hs : ∑ j : Fin 4, Complex.normSq (ψ j) = 0 := by
      exact_mod_cast h
    have hz : ∀ j : Fin 4, Complex.normSq (ψ j) = 0 := by
      rw [Finset.sum_eq_zero_iff_of_nonneg] at hs
      · intro j
        exact hs j (Finset.mem_univ j)
      · intro j hj
        exact Complex.normSq_nonneg (ψ j)
    funext j
    exact Complex.normSq_eq_zero.mp (hz j)
  · rintro rfl
    simp

@[simp] theorem star_two : (starRingEnd ℂ) (2 : ℂ) = 2 :=
  map_ofNat (starRingEnd ℂ) 2

@[simp] theorem ip_zero_left (φ : Spinor) : ip 0 φ = 0 := by simp [ip]
@[simp] theorem ip_zero_right (ψ : Spinor) : ip ψ 0 = 0 := by simp [ip]
@[simp] theorem ip_add_left (ψ φ χ : Spinor) : ip (ψ+φ) χ = ip ψ χ + ip φ χ := by
  simp [ip, Finset.sum_add_distrib, add_mul]
@[simp] theorem ip_add_right (ψ φ χ : Spinor) : ip ψ (φ+χ) = ip ψ φ + ip ψ χ := by
  simp [ip, Finset.sum_add_distrib, mul_add]
@[simp] theorem ip_neg_left (ψ φ : Spinor) : ip (-ψ) φ = -ip ψ φ := by
  simp [ip, Finset.sum_neg_distrib]
@[simp] theorem ip_neg_right (ψ φ : Spinor) : ip ψ (-φ) = -ip ψ φ := by
  simp [ip, Finset.sum_neg_distrib]
@[simp] theorem ip_sub_left (ψ φ χ : Spinor) : ip (ψ-φ) χ = ip ψ χ - ip φ χ := by
  rw [sub_eq_add_neg, ip_add_left, ip_neg_left, sub_eq_add_neg]
@[simp] theorem ip_sub_right (ψ φ χ : Spinor) : ip ψ (φ-χ) = ip ψ φ - ip ψ χ := by
  rw [sub_eq_add_neg, ip_add_right, ip_neg_right, sub_eq_add_neg]
@[simp] theorem ip_smul_left (c : ℂ) (ψ φ : Spinor) :
    ip (c • ψ) φ = (starRingEnd ℂ) c * ip ψ φ := by
  simp [ip, Finset.mul_sum, mul_assoc]
@[simp] theorem ip_smul_right (c : ℂ) (ψ φ : Spinor) :
    ip ψ (c • φ) = c * ip ψ φ := by
  simp [ip, Finset.mul_sum, mul_left_comm]

structure HermitianClifford where
  toClifford : CliffordInvolution
  hermitian : ∀ ψ φ, ip (toClifford.act ψ) φ = ip ψ (toClifford.act φ)

namespace HermitianClifford

@[simp] theorem ip_plus_left (H : HermitianClifford) (ψ φ : Spinor) :
    ip (H.toClifford.plus ψ) φ = ip ψ (H.toClifford.plus φ) := by
  simp [CliffordInvolution.plus, H.hermitian]

@[simp] theorem ip_minus_left (H : HermitianClifford) (ψ φ : Spinor) :
    ip (H.toClifford.minus ψ) φ = ip ψ (H.toClifford.minus φ) := by
  simp [CliffordInvolution.minus, H.hermitian]

@[simp] theorem ip_plus_minus (H : HermitianClifford) (ψ φ : Spinor) :
    ip (H.toClifford.plus ψ) (H.toClifford.minus φ) = 0 := by
  rw [H.ip_plus_left]
  simp

@[simp] theorem ip_minus_plus (H : HermitianClifford) (ψ φ : Spinor) :
    ip (H.toClifford.minus ψ) (H.toClifford.plus φ) = 0 := by
  rw [H.ip_minus_left]
  simp

@[simp] theorem ip_split (H : HermitianClifford) (ψ φ : Spinor) :
    ip (H.toClifford.plus ψ) (H.toClifford.plus φ) +
      ip (H.toClifford.minus ψ) (H.toClifford.minus φ) = ip ψ φ := by
  rw [H.ip_plus_left, H.ip_minus_left]
  calc
    ip ψ (H.toClifford.plus (H.toClifford.plus φ)) +
        ip ψ (H.toClifford.minus (H.toClifford.minus φ)) =
      ip ψ (H.toClifford.plus φ) + ip ψ (H.toClifford.minus φ) := by simp
    _ = ip ψ (H.toClifford.plus φ + H.toClifford.minus φ) :=
      (ip_add_right ψ (H.toClifford.plus φ) (H.toClifford.minus φ)).symm
    _ = ip ψ φ := by rw [H.toClifford.plus_add_minus]

end HermitianClifford

def hermitianX : HermitianClifford where
  toClifford := cliffordX
  hermitian := by
    intro ψ φ
    simp [ip, cliffordX, alphaX, Fin.sum_univ_succ]
    ring

def hermitianY : HermitianClifford where
  toClifford := cliffordY
  hermitian := by
    intro ψ φ
    simp [ip, cliffordY, alphaY, Fin.sum_univ_succ]
    ring

def hermitianZ : HermitianClifford where
  toClifford := cliffordZ
  hermitian := by
    intro ψ φ
    simp [ip, cliffordZ, alphaZ, Fin.sum_univ_succ]
    ring


@[simp] theorem ip_phase_same (z : Circle) (ψ φ : Spinor) :
    ip (phaseMul z ψ) (phaseMul z φ) = ip ψ φ := by
  rw [show phaseMul z ψ = (z : ℂ) • ψ by rfl]
  rw [show phaseMul z φ = (z : ℂ) • φ by rfl]
  rw [ip_smul_left, ip_smul_right]
  have hz : (starRingEnd ℂ) (z : ℂ) * (z : ℂ) = 1 := by
    calc
      (starRingEnd ℂ) (z : ℂ) * (z : ℂ) = ((z⁻¹ : Circle) : ℂ) * (z : ℂ) := by
        rw [Circle.coe_inv_eq_conj]
      _ = 1 := by simp
  rw [← mul_assoc, hz]
  simp

@[simp] theorem ip_phase_plus_minus (H : HermitianClifford)
    (z w : Circle) (ψ φ : Spinor) :
    ip (phaseMul z (H.toClifford.plus ψ))
      (phaseMul w (H.toClifford.minus φ)) = 0 := by
  change ip ((z : ℂ) • H.toClifford.plus ψ)
      ((w : ℂ) • H.toClifford.minus φ) = 0
  rw [ip_smul_left, ip_smul_right, H.ip_plus_minus]
  simp

@[simp] theorem ip_phase_minus_plus (H : HermitianClifford)
    (z w : Circle) (ψ φ : Spinor) :
    ip (phaseMul z (H.toClifford.minus ψ))
      (phaseMul w (H.toClifford.plus φ)) = 0 := by
  change ip ((z : ℂ) • H.toClifford.minus ψ)
      ((w : ℂ) • H.toClifford.plus φ) = 0
  rw [ip_smul_left, ip_smul_right, H.ip_minus_plus]
  simp

@[simp] theorem directionalShift_ip_pointwise {Site : Type*}
    (H : HermitianClifford) (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ φ : State (Site := Site)) (x : Site) :
    ip (directionalShift H.toClifford τ u ψ x)
      (directionalShift H.toClifford τ u φ x) =
    ip (H.toClifford.plus (ψ (τ.symm x)))
      (H.toClifford.plus (φ (τ.symm x))) +
    ip (H.toClifford.minus (ψ (τ x)))
      (H.toClifford.minus (φ (τ x))) := by
  simp [directionalShift]

variable {Site : Type*} [Fintype Site]

def stateIP (ψ φ : State (Site := Site)) : ℂ := ∑ x, ip (ψ x) (φ x)

@[simp] theorem directionalShift_stateIP (H : HermitianClifford)
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ φ : State (Site := Site)) :
    stateIP (directionalShift H.toClifford τ u ψ)
      (directionalShift H.toClifford τ u φ) = stateIP ψ φ := by
  let fp : Site → ℂ := fun x =>
    ip (H.toClifford.plus (ψ x)) (H.toClifford.plus (φ x))
  let fm : Site → ℂ := fun x =>
    ip (H.toClifford.minus (ψ x)) (H.toClifford.minus (φ x))
  calc
    stateIP (directionalShift H.toClifford τ u ψ)
        (directionalShift H.toClifford τ u φ) =
      ∑ x, (fp (τ.symm x) + fm (τ x)) := by
        simp [stateIP, fp, fm, directionalShift_ip_pointwise]
    _ = (∑ x, fp (τ.symm x)) + ∑ x, fm (τ x) :=
      Finset.sum_add_distrib
    _ = (∑ x, fp x) + ∑ x, fm x := by
      rw [τ.symm.sum_comp fp, τ.sum_comp fm]
    _ = ∑ x, (fp x + fm x) := Finset.sum_add_distrib.symm
    _ = stateIP ψ φ := by
      simp only [fp, fm, stateIP]
      apply Finset.sum_congr rfl
      intro x hx
      exact H.ip_split (ψ x) (φ x)

/-- The Dirac beta involution in the same algebraic form as the spatial generators. -/
def cliffordBeta : CliffordInvolution where
  act := beta
  map_add := by
    intro ψ φ
    ext j
    fin_cases j <;> simp [beta, add_comm]
  map_smul := by
    intro c ψ
    ext j
    fin_cases j <;> simp [beta]
  square := by
    intro ψ
    ext j
    fin_cases j <;> simp [beta]

def hermitianBeta : HermitianClifford where
  toClifford := cliffordBeta
  hermitian := by
    intro ψ φ
    simp [ip, cliffordBeta, beta, Fin.sum_univ_succ]

/-- A local spectral phase split along an orthogonal Clifford decomposition. -/
def spectralPhase (H : HermitianClifford) (zp zm : Circle) (ψ : Spinor) : Spinor :=
  phaseMul zp (H.toClifford.plus ψ) +
    phaseMul zm (H.toClifford.minus ψ)

/-- The inverse local spectral phase split. -/
def spectralPhaseInv (H : HermitianClifford) (zp zm : Circle) (ψ : Spinor) : Spinor :=
  phaseMul zp⁻¹ (H.toClifford.plus ψ) +
    phaseMul zm⁻¹ (H.toClifford.minus ψ)

@[simp] theorem spectralPhaseInv_phase (H : HermitianClifford)
    (zp zm : Circle) (ψ : Spinor) :
    spectralPhaseInv H zp zm (spectralPhase H zp zm ψ) = ψ := by
  simp [spectralPhaseInv, spectralPhase]

@[simp] theorem spectralPhase_phaseInv (H : HermitianClifford)
    (zp zm : Circle) (ψ : Spinor) :
    spectralPhase H zp zm (spectralPhaseInv H zp zm ψ) = ψ := by
  simp [spectralPhaseInv, spectralPhase]

@[simp] theorem spectralPhase_ip (H : HermitianClifford)
    (zp zm : Circle) (ψ φ : Spinor) :
    ip (spectralPhase H zp zm ψ) (spectralPhase H zp zm φ) = ip ψ φ := by
  simp only [spectralPhase, ip_add_left, ip_add_right,
    ip_phase_same, ip_phase_plus_minus, ip_phase_minus_plus, add_zero, zero_add]
  exact H.ip_split ψ φ

/-- The local reversible step generated by two unit-circle spectral phases. -/
def spectralPhaseLocalStep (H : HermitianClifford) (zp zm : Circle) : LocalStep where
  toFun := spectralPhase H zp zm
  invFun := spectralPhaseInv H zp zm
  left_inv := spectralPhaseInv_phase H zp zm
  right_inv := spectralPhase_phaseInv H zp zm
  phase_commutes := by
    intro z ψ
    simp [spectralPhase, phaseMul_add, mul_comm]
  inv_phase_commutes := by
    intro z ψ
    simp [spectralPhaseInv, phaseMul_add, mul_comm]


@[simp] theorem directionalShiftX_stateIP
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ φ : State (Site := Site)) :
    stateIP (directionalShift cliffordX τ u ψ)
      (directionalShift cliffordX τ u φ) = stateIP ψ φ := by
  simpa [hermitianX] using directionalShift_stateIP hermitianX τ u ψ φ

@[simp] theorem directionalShiftY_stateIP
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ φ : State (Site := Site)) :
    stateIP (directionalShift cliffordY τ u ψ)
      (directionalShift cliffordY τ u φ) = stateIP ψ φ := by
  simpa [hermitianY] using directionalShift_stateIP hermitianY τ u ψ φ

@[simp] theorem directionalShiftZ_stateIP
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ φ : State (Site := Site)) :
    stateIP (directionalShift cliffordZ τ u ψ)
      (directionalShift cliffordZ τ u φ) = stateIP ψ φ := by
  simpa [hermitianZ] using directionalShift_stateIP hermitianZ τ u ψ φ

/-- A reversible local step together with its finite-spinor Hilbert certificate. -/
structure HilbertLocalStep where
  toLocalStep : LocalStep
  preserves_ip : ∀ ψ φ, ip (toLocalStep.toFun ψ) (toLocalStep.toFun φ) = ip ψ φ

/-- The beta mass split is a Hilbert-preserving local step. -/
def betaHilbertStep (zp zm : Circle) : HilbertLocalStep where
  toLocalStep := spectralPhaseLocalStep hermitianBeta zp zm
  preserves_ip := spectralPhase_ip hermitianBeta zp zm

@[simp] theorem HilbertLocalStep.apply_stateIP (M : HilbertLocalStep)
    (ψ φ : State (Site := Site)) :
    stateIP (M.toLocalStep.apply ψ) (M.toLocalStep.apply φ) = stateIP ψ φ := by
  simp [stateIP, LocalStep.apply, M.preserves_ip]

@[simp] theorem sevenFactorWalk_stateIP (M : HilbertLocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ φ : State (Site := Site)) :
    stateIP
      (sevenFactorWalk M.toLocalStep τx τy τz ux uy uz ψ)
      (sevenFactorWalk M.toLocalStep τx τy τz ux uy uz φ) = stateIP ψ φ := by
  simp only [sevenFactorWalk]
  rw [M.apply_stateIP]
  rw [directionalShiftX_stateIP]
  rw [directionalShiftY_stateIP]
  rw [directionalShiftZ_stateIP]
  rw [directionalShiftY_stateIP]
  rw [directionalShiftX_stateIP]
  rw [M.apply_stateIP]


/-! ## One-step dyadic refinement -/

abbrev FineSite (Site : Type*) := Site × Fin 2

/-- Lift a coarse translation without mixing the two child cells. -/
def liftEquiv {Site : Type*} (τ : Site ≃ Site) :
    FineSite Site ≃ FineSite Site :=
  Equiv.prodCongr τ (Equiv.refl (Fin 2))

/-- Pull a coarse link back to both child cells. -/
def liftLink {Site : Type*} (u : Link (Site := Site)) :
    Link (Site := FineSite Site) := fun p => u p.1

/-- Pull a coarse gauge transformation back to both child cells. -/
def liftGauge {Site : Type*} (g : Gauge (Site := Site)) :
    Gauge (Site := FineSite Site) := fun p => g p.1

/-- Replicate each coarse spinor into the two child cells. -/
def replicateState {Site : Type*} (ψ : State (Site := Site)) :
    State (Site := FineSite Site) := fun p => ψ p.1

@[simp] theorem liftEquiv_apply {Site : Type*} (τ : Site ≃ Site)
    (x : Site) (b : Fin 2) : liftEquiv τ (x, b) = (τ x, b) := rfl

@[simp] theorem liftEquiv_symm_apply {Site : Type*} (τ : Site ≃ Site)
    (x : Site) (b : Fin 2) : (liftEquiv τ).symm (x, b) = (τ.symm x, b) := rfl

@[simp] theorem gaugeState_replicate {Site : Type*}
    (g : Gauge (Site := Site)) (ψ : State (Site := Site)) :
    gaugeState (liftGauge g) (replicateState ψ) =
      replicateState (gaugeState g ψ) := by
  rfl

@[simp] theorem gaugeLink_lift {Site : Type*} (τ : Site ≃ Site)
    (g : Gauge (Site := Site)) (u : Link (Site := Site)) :
    gaugeLink (liftEquiv τ) (liftGauge g) (liftLink u) =
      liftLink (gaugeLink τ g u) := by
  rfl

/-- Each directional Clifford transport exactly intertwines child replication. -/
@[simp] theorem directionalShift_replicate {Site : Type*}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    directionalShift A (liftEquiv τ) (liftLink u) (replicateState ψ) =
      replicateState (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨x, b⟩
  rfl

/-- A site-local step exactly intertwines child replication. -/
@[simp] theorem localStep_replicate {Site : Type*} (M : LocalStep)
    (ψ : State (Site := Site)) :
    M.apply (replicateState ψ) = replicateState (M.apply ψ) := by
  rfl

/-- The full seven-factor Clifford walk exactly intertwines one dyadic refinement. -/
@[simp] theorem sevenFactorWalk_replicate {Site : Type*} (M : LocalStep)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (ψ : State (Site := Site)) :
    sevenFactorWalk M (liftEquiv τx) (liftEquiv τy) (liftEquiv τz)
      (liftLink ux) (liftLink uy) (liftLink uz) (replicateState ψ) =
    replicateState (sevenFactorWalk M τx τy τz ux uy uz ψ) := by
  simp [sevenFactorWalk]

variable {CoarseSite : Type*} [Fintype CoarseSite]

/-- Replication doubles the unweighted counting-measure inner product. -/
theorem replicateState_stateIP
    (ψ φ : State (Site := CoarseSite)) :
    stateIP (Site := FineSite CoarseSite) (replicateState ψ) (replicateState φ) =
      2 * stateIP ψ φ := by
  rw [show stateIP (Site := FineSite CoarseSite) (replicateState ψ) (replicateState φ) =
      ∑ x : CoarseSite, ∑ b : Fin 2, ip (ψ x) (φ x) by
        simp [stateIP, replicateState, Fintype.sum_prod_type]]
  simp [stateIP]
  rw [Finset.mul_sum]

/-- The physical child-cell measure is half the coarse measure. -/
def fineCellWeightedIP
    (ψ φ : State (Site := FineSite CoarseSite)) : ℂ :=
  (2 : ℂ)⁻¹ * stateIP ψ φ

/-- With halved cell measure, dyadic replication is exactly Hilbert-isometric. -/
@[simp] theorem replicateState_weighted_isometry
    (ψ φ : State (Site := CoarseSite)) :
    fineCellWeightedIP (replicateState ψ) (replicateState φ) = stateIP ψ φ := by
  rw [fineCellWeightedIP, replicateState_stateIP]
  ring

/-- The lifted walk is unitary for the halved child-cell measure. -/
@[simp] theorem liftedSevenFactorWalk_weightedIP (M : HilbertLocalStep)
    (τx τy τz : CoarseSite ≃ CoarseSite)
    (ux uy uz : Link (Site := CoarseSite))
    (Ψ Φ : State (Site := FineSite CoarseSite)) :
    fineCellWeightedIP
      (sevenFactorWalk M.toLocalStep
        (liftEquiv τx) (liftEquiv τy) (liftEquiv τz)
        (liftLink ux) (liftLink uy) (liftLink uz) Ψ)
      (sevenFactorWalk M.toLocalStep
        (liftEquiv τx) (liftEquiv τy) (liftEquiv τz)
        (liftLink ux) (liftLink uy) (liftLink uz) Φ) =
    fineCellWeightedIP Ψ Φ := by
  unfold fineCellWeightedIP
  rw [sevenFactorWalk_stateIP]


/-! ## Exact dyadic refinement tower and Block 24 instantiation -/

universe u

/-- Iterated dyadic cylinder sites. -/
def DyadicSite (Base : Type u) : ℕ → Type u
  | 0 => Base
  | Nat.succ n => FineSite (DyadicSite Base n)

@[instance_reducible] def dyadicSiteFintype (Base : Type u) [Fintype Base] :
    (n : ℕ) → Fintype (DyadicSite Base n)
  | 0 => inferInstanceAs (Fintype Base)
  | Nat.succ n => by
      letI : Fintype (DyadicSite Base n) := dyadicSiteFintype Base n
      exact inferInstanceAs (Fintype (FineSite (DyadicSite Base n)))

instance (Base : Type u) [Fintype Base] (n : ℕ) :
    Fintype (DyadicSite Base n) := dyadicSiteFintype Base n

/-- Lift a base translation through all dyadic levels. -/
def dyadicEquiv {Base : Type u} (τ : Base ≃ Base) :
    (n : ℕ) → DyadicSite Base n ≃ DyadicSite Base n
  | 0 => τ
  | Nat.succ n => liftEquiv (dyadicEquiv τ n)

/-- Pull a base link through all dyadic levels. -/
def dyadicLink {Base : Type u} (u : Link (Site := Base)) :
    (n : ℕ) → Link (Site := DyadicSite Base n)
  | 0 => u
  | Nat.succ n => liftLink (dyadicLink u n)

/-- Pull a base gauge through all dyadic levels. -/
def dyadicGauge {Base : Type u} (g : Gauge (Site := Base)) :
    (n : ℕ) → Gauge (Site := DyadicSite Base n)
  | 0 => g
  | Nat.succ n => liftGauge (dyadicGauge g n)

/-- Adjacent dyadic embedding by child replication. -/
def dyadicEmbed {Base : Type u} (n : ℕ)
    (ψ : State (Site := DyadicSite Base n)) :
    State (Site := DyadicSite Base n.succ) :=
  replicateState ψ

/-- The same local walk at every lifted resolution. -/
def dyadicWalk {Base : Type u} (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base))
    (n : ℕ) : State (Site := DyadicSite Base n) →
      State (Site := DyadicSite Base n) :=
  sevenFactorWalk M (dyadicEquiv τx n) (dyadicEquiv τy n)
    (dyadicEquiv τz n) (dyadicLink ux n) (dyadicLink uy n)
    (dyadicLink uz n)

@[simp] theorem dyadicWalk_embed {Base : Type u} (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base))
    (n : ℕ) (ψ : State (Site := DyadicSite Base n)) :
    dyadicWalk M τx τy τz ux uy uz n.succ (dyadicEmbed n ψ) =
      dyadicEmbed n (dyadicWalk M τx τy τz ux uy uz n ψ) := by
  exact sevenFactorWalk_replicate M (dyadicEquiv τx n)
    (dyadicEquiv τy n) (dyadicEquiv τz n) (dyadicLink ux n)
    (dyadicLink uy n) (dyadicLink uz n) ψ

/-- Concrete exact refinement tower for the Clifford walk. -/
def exactDyadicTower {Base : Type u} (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base)) :
    KomorebiPhysics.LocalDiscreteGlobalContinuum.ExactRefinementTower
      (fun n => State (Site := DyadicSite Base n)) where
  embed := dyadicEmbed
  evolve := dyadicWalk M τx τy τz ux uy uz
  compatible := dyadicWalk_embed M τx τy τz ux uy uz

/-- The weighted inner product at dyadic depth `n`. -/
def dyadicWeightedIP {Base : Type u} [Fintype Base] (n : ℕ)
    (ψ φ : State (Site := DyadicSite Base n)) : ℂ :=
  ((2 : ℂ)⁻¹) ^ n * stateIP ψ φ

@[simp] theorem dyadicEmbed_weighted_isometry {Base : Type u} [Fintype Base]
    (n : ℕ) (ψ φ : State (Site := DyadicSite Base n)) :
    dyadicWeightedIP n.succ (dyadicEmbed n ψ) (dyadicEmbed n φ) =
      dyadicWeightedIP n ψ φ := by
  change ((2 : ℂ)⁻¹) ^ n.succ *
      stateIP (Site := FineSite (DyadicSite Base n))
        (replicateState ψ) (replicateState φ) =
    ((2 : ℂ)⁻¹) ^ n * stateIP ψ φ
  rw [replicateState_stateIP]
  simp [pow_succ]
  ring

@[simp] theorem dyadicWalk_weightedIP {Base : Type u} [Fintype Base]
    (M : HilbertLocalStep) (τx τy τz : Base ≃ Base)
    (ux uy uz : Link (Site := Base)) (n : ℕ)
    (ψ φ : State (Site := DyadicSite Base n)) :
    dyadicWeightedIP n
      (dyadicWalk M.toLocalStep τx τy τz ux uy uz n ψ)
      (dyadicWalk M.toLocalStep τx τy τz ux uy uz n φ) =
    dyadicWeightedIP n ψ φ := by
  unfold dyadicWeightedIP dyadicWalk
  rw [sevenFactorWalk_stateIP]


/-- The coherent state obtained by repeatedly replicating one base state. -/
def dyadicRefineState {Base : Type u} (ψ₀ : State (Site := Base)) :
    (n : ℕ) → State (Site := DyadicSite Base n)
  | 0 => ψ₀
  | Nat.succ n => dyadicEmbed n (dyadicRefineState ψ₀ n)

/-- A concrete coherent state in the exact dyadic Clifford tower. -/
def dyadicCoherentState {Base : Type u} (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base))
    (ψ₀ : State (Site := Base)) :
    KomorebiPhysics.LocalDiscreteGlobalContinuum.CoherentState
      (exactDyadicTower M τx τy τz ux uy uz) where
  state := dyadicRefineState ψ₀
  coherent := by
    intro n
    rfl

/-- Select the zero child from one dyadic refinement. -/
def firstChild {Site : Type u} (Ψ : State (Site := FineSite Site)) :
    State (Site := Site) := fun x => Ψ (x, 0)

@[simp] theorem firstChild_replicate {Site : Type u}
    (ψ : State (Site := Site)) : firstChild (replicateState ψ) = ψ := by
  rfl

/-- Reconstruct a dyadic cylinder state on the base lattice by following the
zero-child branch. -/
def dyadicReconstruct {Base : Type u} :
    (n : ℕ) → State (Site := DyadicSite Base n) → State (Site := Base)
  | 0 => fun ψ => ψ
  | Nat.succ n => fun Ψ => dyadicReconstruct n (firstChild Ψ)

@[simp] theorem dyadicReconstruct_embed {Base : Type u} (n : ℕ)
    (ψ : State (Site := DyadicSite Base n)) :
    dyadicReconstruct n.succ (dyadicEmbed n ψ) =
      dyadicReconstruct n ψ := by
  rfl

/-- Exact reconstruction compatibility specializes the generic Block 24 bridge
to this concrete dyadic Clifford tower. -/
theorem dyadic_reconstructedSequence_eq_base {Base : Type u}
    (M : LocalStep) (τx τy τz : Base ≃ Base)
    (ux uy uz : Link (Site := Base))
    (ψ : KomorebiPhysics.LocalDiscreteGlobalContinuum.CoherentState
      (exactDyadicTower M τx τy τz ux uy uz)) (n : ℕ) :
    (exactDyadicTower M τx τy τz ux uy uz).reconstructedSequence
      (fun k => dyadicReconstruct (Base := Base) k) ψ n = ψ.state 0 := by
  exact (exactDyadicTower M τx τy τz ux uy uz).reconstructedSequence_eq_zero
    (fun k => dyadicReconstruct (Base := Base) k)
    (fun k x => dyadicReconstruct_embed k x) ψ n

/-- The evolved coherent hierarchy reconstructs exactly to the base evolution.
This is the zero-defect concrete instance of the Block 24 global-dynamics
architecture. -/
theorem dyadic_evolved_reconstructedSequence_eq_base {Base : Type u}
    (M : LocalStep) (τx τy τz : Base ≃ Base)
    (ux uy uz : Link (Site := Base))
    (ψ : KomorebiPhysics.LocalDiscreteGlobalContinuum.CoherentState
      (exactDyadicTower M τx τy τz ux uy uz)) (n : ℕ) :
    (exactDyadicTower M τx τy τz ux uy uz).reconstructedSequence
      (fun k => dyadicReconstruct (Base := Base) k)
      ((exactDyadicTower M τx τy τz ux uy uz).evolveState ψ) n =
    dyadicWalk M τx τy τz ux uy uz 0 (ψ.state 0) := by
  exact (exactDyadicTower M τx τy τz ux uy uz).evolved_reconstructedSequence_eq_zero
    (fun k => dyadicReconstruct (Base := Base) k)
    (fun k x => dyadicReconstruct_embed k x) ψ n


section ExactCylinderLimit

variable {Base : Type u} [Fintype Base]

/-- Exact zero-defect continuum-realization object for the dyadic cylinder
reconstruction.  Its target is the complete finite-volume base-state Hilbert
space, not yet a continuum manifold. -/
def exactDyadicCylinderRealization (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base)) :
    KomorebiPhysics.LocalDiscreteGlobalContinuum.ExactRefinementTower.ContinuumRealization
      (exactDyadicTower M τx τy τz ux uy uz)
      (Y := State (Site := Base)) :=
  (exactDyadicTower M τx τy τz ux uy uz).exactContinuumRealization
    (fun k => dyadicReconstruct (Base := Base) k)
    (fun k x => dyadicReconstruct_embed k x)

/-- The canonical global state of the exact cylinder realization is the
level-zero reconstruction. -/
theorem exactDyadicCylinder_globalState_eq_base (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base))
    (ψ : KomorebiPhysics.LocalDiscreteGlobalContinuum.CoherentState
      (exactDyadicTower M τx τy τz ux uy uz)) :
    KomorebiPhysics.LocalDiscreteGlobalContinuum.ExactRefinementTower.ContinuumRealization.globalState
      (exactDyadicTower M τx τy τz ux uy uz)
      (exactDyadicCylinderRealization M τx τy τz ux uy uz) ψ =
    ψ.state 0 := by
  exact (exactDyadicTower M τx τy τz ux uy uz).exact_globalState_eq_zero
    (fun k => dyadicReconstruct (Base := Base) k)
    (fun k x => dyadicReconstruct_embed k x) ψ

/-- The canonical global evolution of the exact cylinder realization is exactly
the base-level Clifford walk. -/
theorem exactDyadicCylinder_globalEvolution_eq_base (M : LocalStep)
    (τx τy τz : Base ≃ Base) (ux uy uz : Link (Site := Base))
    (ψ : KomorebiPhysics.LocalDiscreteGlobalContinuum.CoherentState
      (exactDyadicTower M τx τy τz ux uy uz)) :
    KomorebiPhysics.LocalDiscreteGlobalContinuum.ExactRefinementTower.ContinuumRealization.globalEvolution
      (exactDyadicTower M τx τy τz ux uy uz)
      (exactDyadicCylinderRealization M τx τy τz ux uy uz) ψ =
    dyadicWalk M τx τy τz ux uy uz 0 (ψ.state 0) := by
  exact (exactDyadicTower M τx τy τz ux uy uz).exact_globalEvolution_eq_zero
    (fun k => dyadicReconstruct (Base := Base) k)
    (fun k x => dyadicReconstruct_embed k x) ψ

end ExactCylinderLimit



end Relativistic3DCliffordHilbertRefinement
end KomorebiPhysics
