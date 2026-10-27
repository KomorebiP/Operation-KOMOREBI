module

public import KomorebiPhysics.MixedTransfer
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv
public import Mathlib.Analysis.SpecialFunctions.Pow.Deriv

/-!
Chapter 4.6, equations (4.35)--(4.44). Derivatives of actual Shannon,
real-power moment and Renyi functionals. Finite sums, strict positivity at
the time of differentiation, and q != 1 where the Renyi expression is used.
Antisymmetry implies balance identities, not an entropy-production sign.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.InformationTransport
open scoped BigOperators
variable {I : Type*} [Fintype I]

/-- Packet Shannon entropy with the natural logarithm. -/
def entropy (p : I → ℝ) : ℝ := -(∑ i, p i * Real.log (p i))

/-- Real-order moment, with the actual real power. -/
def powerSum (p : I → ℝ) (q : ℝ) : ℝ := ∑ i, (p i) ^ q

/-- The displayed Renyi expression. The derivative theorem explicitly excludes
q=1; Lean's totalized division is not a definition of its Shannon limit. -/
def renyi (p : I → ℝ) (q : ℝ) : ℝ := Real.log (powerSum p q) / (1-q)

/-- The finite weighted antisymmetric-sum identity underlying all the
information-transport formulas. -/
theorem weighted_current_symmetry (J : I → I → ℝ) (g : I → ℝ)
    (hJ : ∀ i j, J i j = -J j i) :
    (∑ i, g i * ∑ j, J i j) =
      (1/2 : ℝ) * ∑ i, ∑ j, J i j * (g i - g j) := by
  have hswap : (∑ i, ∑ j, J i j * g j) = -(∑ i, ∑ j, J i j * g i) := by
    calc
      _ = ∑ i, ∑ j, J j i * g i := Finset.sum_comm
      _ = ∑ i, ∑ j, -(J i j * g i) := by
        apply Finset.sum_congr rfl
        intro i _
        apply Finset.sum_congr rfl
        intro j _
        rw [hJ j i, neg_mul]
      _ = _ := by simp only [Finset.sum_neg_distrib]
  have hleft : (∑ i, g i * ∑ j, J i j) = ∑ i, ∑ j, J i j * g i := by
    simp only [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i _
    apply Finset.sum_congr rfl
    intro j _
    exact mul_comm _ _
  rw [hleft]
  simp only [mul_sub, Finset.sum_sub_distrib]
  rw [hswap]
  ring

/-- A general differentiable packet functional inherits an exact current
formula. The functional derivative is derived by the chain rule. -/
theorem hasDerivAt_functional {p : ℝ → I → ℝ} {t : ℝ}
    (J : I → I → ℝ) (f : ℝ → ℝ) (g : I → ℝ)
    (hJ : ∀ i j, J i j = -J j i)
    (hp : ∀ i, HasDerivAt (fun s => p s i) (∑ j, J i j) t)
    (hf : ∀ i, HasDerivAt f (g i) (p t i)) :
    HasDerivAt (fun s => ∑ i, f (p s i))
      ((1/2 : ℝ) * ∑ i, ∑ j, J i j * (g i - g j)) t := by
  have h := HasDerivAt.fun_sum (u := Finset.univ)
    (fun i _ => (hf i).comp t (hp i))
  simpa only [Function.comp_def, weighted_current_symmetry J g hJ] using h

/-- The derivative of x log x is established on the positive domain. -/
theorem hasDerivAt_xlogx {x : ℝ} (hx : 0 < x) :
    HasDerivAt (fun y : ℝ => y * Real.log y) (1 + Real.log x) x := by
  have h := (hasDerivAt_id x).mul (Real.hasDerivAt_log (ne_of_gt hx))
  simpa only [id_eq, Pi.mul_apply, one_mul, mul_inv_cancel₀ (ne_of_gt hx), add_comm] using h

/-- Equation (4.37): actual entropy derivative for arbitrary supplied component
slopes. No zero-mass-rate assumption has been inserted here. -/
theorem hasDerivAt_entropy_raw {p : ℝ → I → ℝ} {v : I → ℝ} {t : ℝ}
    (hp : ∀ i, HasDerivAt (fun s => p s i) (v i) t)
    (hpos : ∀ i, 0 < p t i) :
    HasDerivAt (fun s => entropy (p s))
      (-(∑ i, (1 + Real.log (p t i)) * v i)) t := by
  exact (HasDerivAt.fun_sum (u := Finset.univ)
    (fun i _ => (hasDerivAt_xlogx (hpos i)).comp t (hp i))).neg

/-- Equations (4.38)--(4.40): antisymmetric currents produce the exact
log-ratio entropy derivative. No monotonicity conclusion follows by itself. -/
theorem hasDerivAt_entropy_current {p : ℝ → I → ℝ} {t : ℝ}
    (J : I → I → ℝ) (hJ : ∀ i j, J i j = -J j i)
    (hp : ∀ i, HasDerivAt (fun s => p s i) (∑ j, J i j) t)
    (hpos : ∀ i, 0 < p t i) :
    HasDerivAt (fun s => entropy (p s))
      (-(1/2 : ℝ) * ∑ i, ∑ j, J i j * Real.log (p t i / p t j)) t := by
  have h := hasDerivAt_entropy_raw hp hpos
  rw [weighted_current_symmetry J (fun i => 1 + Real.log (p t i)) hJ] at h
  have hlog (i j : I) : (1 + Real.log (p t i)) - (1 + Real.log (p t j)) =
      Real.log (p t i / p t j) := by
    rw [Real.log_div (ne_of_gt (hpos i)) (ne_of_gt (hpos j))]
    ring
  simpa only [hlog, neg_mul] using h

/-- Real-power moments have actual derivatives for every fixed real order q
on the strictly positive packet domain. -/
theorem hasDerivAt_powerSum_raw {p : ℝ → I → ℝ} {v : I → ℝ} {t : ℝ}
    (q : ℝ) (hp : ∀ i, HasDerivAt (fun s => p s i) (v i) t)
    (hpos : ∀ i, 0 < p t i) :
    HasDerivAt (fun s => powerSum (p s) q)
      (∑ i, (q * (p t i) ^ (q-1)) * v i) t := by
  apply HasDerivAt.fun_sum
  intro i _
  exact (Real.hasDerivAt_rpow_const (p := q) (Or.inl (ne_of_gt (hpos i)))).comp t (hp i)

/-- Equation (4.42): the real-order moment transport identity. -/
theorem hasDerivAt_powerSum_current {p : ℝ → I → ℝ} {t : ℝ}
    (q : ℝ) (J : I → I → ℝ) (hJ : ∀ i j, J i j = -J j i)
    (hp : ∀ i, HasDerivAt (fun s => p s i) (∑ j, J i j) t)
    (hpos : ∀ i, 0 < p t i) :
    HasDerivAt (fun s => powerSum (p s) q)
      ((q/2) * ∑ i, ∑ j, J i j * ((p t i) ^ (q-1) - (p t j) ^ (q-1))) t := by
  have h := hasDerivAt_powerSum_raw q hp hpos
  rw [weighted_current_symmetry J (fun i => q * (p t i) ^ (q-1)) hJ] at h
  have hfactor (i j : I) : J i j * (q * (p t i) ^ (q-1) - q * (p t j) ^ (q-1)) =
      q * (J i j * ((p t i) ^ (q-1) - (p t j) ^ (q-1))) := by ring
  simp only [hfactor, ← Finset.mul_sum] at h
  convert h using 1
  ring

/-- A nonempty finite family of positive packets has a positive real-order
moment. This discharges the logarithm denominator, including for q<0. -/
theorem powerSum_pos [Nonempty I] (p : I → ℝ) (q : ℝ) (hp : ∀ i, 0 < p i) :
    0 < powerSum p q := by
  exact Finset.sum_pos (fun i _ => Real.rpow_pos_of_pos (hp i) q) Finset.univ_nonempty

/-- Equation (4.44), with q != 1 and a proved positive moment. The derivative
comes from differentiating the actual logarithm of the actual power sum. -/
theorem hasDerivAt_renyi_current [Nonempty I] {p : ℝ → I → ℝ} {t : ℝ}
    (q : ℝ) (hq : q ≠ 1) (J : I → I → ℝ) (hJ : ∀ i j, J i j = -J j i)
    (hp : ∀ i, HasDerivAt (fun s => p s i) (∑ j, J i j) t)
    (hpos : ∀ i, 0 < p t i) :
    HasDerivAt (fun s => renyi (p s) q)
      (q / (2 * (1-q) * powerSum (p t) q) *
        ∑ i, ∑ j, J i j * ((p t i) ^ (q-1) - (p t j) ^ (q-1))) t := by
  have hM : powerSum (p t) q ≠ 0 := ne_of_gt (powerSum_pos (p t) q hpos)
  have hq0 : 1-q ≠ 0 := sub_ne_zero.mpr (Ne.symm hq)
  have h := ((hasDerivAt_powerSum_current q J hJ hp hpos).log hM).div_const (1-q)
  change HasDerivAt (fun s => renyi (p s) q) _ t at h
  convert h using 1
  field_simp

end KomorebiPhysics.InformationTransport

namespace KomorebiPhysics.MixedTransfer.MatrixAtlas
open scoped BigOperators
open InformationTransport
variable {n I : Type*} [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]
variable (P : MatrixAtlas n I)

/-- The abstract entropy law is discharged from the original matrix flow and
the proved quantum current, not assumed as a new physical evolution law. -/
theorem hasDerivAt_packet_entropy {H : Matrix n n ℂ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t)
    (hpos : ∀ i, 0 < P.probability (ρ t) i) :
    HasDerivAt (fun s => entropy (P.probability (ρ s)))
      (-(1/2 : ℝ) * ∑ i, ∑ j, P.current H (ρ t) i j *
        Real.log (P.probability (ρ t) i / P.probability (ρ t) j)) t :=
  hasDerivAt_entropy_current _ (P.current_antisymm H (ρ t) hH hρt)
    (P.hasDerivAt_probability hH hρt hρ) hpos

/-- Real-order moment transport derived directly from matrix dynamics. -/
theorem hasDerivAt_packet_powerSum {H : Matrix n n ℂ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (q : ℝ) (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t)
    (hpos : ∀ i, 0 < P.probability (ρ t) i) :
    HasDerivAt (fun s => powerSum (P.probability (ρ s)) q)
      ((q/2) * ∑ i, ∑ j, P.current H (ρ t) i j *
        ((P.probability (ρ t) i) ^ (q-1) - (P.probability (ρ t) j) ^ (q-1))) t :=
  hasDerivAt_powerSum_current q _ (P.current_antisymm H (ρ t) hH hρt)
    (P.hasDerivAt_probability hH hρt hρ) hpos

/-- Renyi transport derived directly from matrix dynamics. Strictly positive
packet probabilities are stronger than merely positive-semidefinite rho. -/
theorem hasDerivAt_packet_renyi [Nonempty I]
    {H : Matrix n n ℂ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (q : ℝ) (hq : q ≠ 1) (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t)
    (hpos : ∀ i, 0 < P.probability (ρ t) i) :
    HasDerivAt (fun s => renyi (P.probability (ρ s)) q)
      (q / (2 * (1-q) * powerSum (P.probability (ρ t)) q) *
        ∑ i, ∑ j, P.current H (ρ t) i j *
          ((P.probability (ρ t) i) ^ (q-1) - (P.probability (ρ t) j) ^ (q-1))) t :=
  hasDerivAt_renyi_current q hq _ (P.current_antisymm H (ρ t) hH hρt)
    (P.hasDerivAt_probability hH hρt hρ) hpos

end KomorebiPhysics.MixedTransfer.MatrixAtlas
