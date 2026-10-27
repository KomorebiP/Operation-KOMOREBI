module

public import KomorebiPhysics.Relativistic3DContinuumLimit

/-!
Exact three-vector and continuum Lorentz-boost algebra for the observer-shell
calculation.  The spatial boost is written in the regularized form
`γ²/(γ+1)`, which remains defined at zero velocity; its equality to the usual
`(γ-1)/|v|²` coefficient is proved away from zero velocity.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DLorentzKinematics

open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit

/-- Concrete real three-vector used by the observer calculation. -/
structure Vec3 where
  x : ℝ
  y : ℝ
  z : ℝ
  deriving DecidableEq

/-- The zero three-vector. -/
def zero : Vec3 := ⟨0, 0, 0⟩

/-- Vector addition. -/
def add (u w : Vec3) : Vec3 := ⟨u.x + w.x, u.y + w.y, u.z + w.z⟩

/-- Vector subtraction. -/
def sub (u w : Vec3) : Vec3 := ⟨u.x - w.x, u.y - w.y, u.z - w.z⟩

/-- Scalar multiplication. -/
def scale (a : ℝ) (u : Vec3) : Vec3 := ⟨a * u.x, a * u.y, a * u.z⟩

/-- Euclidean dot product. -/
def dot (u w : Vec3) : ℝ := u.x * w.x + u.y * w.y + u.z * w.z

/-- Euclidean squared norm. -/
def normSq (u : Vec3) : ℝ := dot u u

/-- Continuum relativistic energy in vector notation. -/
def energyVec (m : ℝ) (k : Vec3) : ℝ := energy3 m k.x k.y k.z

/-- Quartic lattice anisotropy polynomial in vector notation. -/
def anisotropyVec (m : ℝ) (k : Vec3) : ℝ := anisotropyQ m k.x k.y k.z

/-- Exact positive-spacing lattice frequency in vector notation. -/
def frequencyVec (m : ℝ) (k : Vec3) (ε : ℝ) : ℝ :=
  positiveFrequency3 m k.x k.y k.z ε

/-- Checked quadratic lattice-frequency coefficient in vector notation. -/
def correctionVec (m : ℝ) (k : Vec3) : ℝ := correction3 m k.x k.y k.z

@[simp] theorem zero_x : zero.x = 0 := rfl
@[simp] theorem zero_y : zero.y = 0 := rfl
@[simp] theorem zero_z : zero.z = 0 := rfl
@[simp] theorem add_x (u w : Vec3) : (add u w).x = u.x + w.x := rfl
@[simp] theorem add_y (u w : Vec3) : (add u w).y = u.y + w.y := rfl
@[simp] theorem add_z (u w : Vec3) : (add u w).z = u.z + w.z := rfl
@[simp] theorem sub_x (u w : Vec3) : (sub u w).x = u.x - w.x := rfl
@[simp] theorem sub_y (u w : Vec3) : (sub u w).y = u.y - w.y := rfl
@[simp] theorem sub_z (u w : Vec3) : (sub u w).z = u.z - w.z := rfl
@[simp] theorem scale_x (a : ℝ) (u : Vec3) : (scale a u).x = a * u.x := rfl
@[simp] theorem scale_y (a : ℝ) (u : Vec3) : (scale a u).y = a * u.y := rfl
@[simp] theorem scale_z (a : ℝ) (u : Vec3) : (scale a u).z = a * u.z := rfl

@[ext] theorem Vec3.ext {u w : Vec3}
    (hx : u.x = w.x) (hy : u.y = w.y) (hz : u.z = w.z) : u = w := by
  cases u
  cases w
  simp_all

@[simp] theorem add_zero (u : Vec3) : add u zero = u := by ext <;> simp
@[simp] theorem zero_add (u : Vec3) : add zero u = u := by ext <;> simp
@[simp] theorem sub_self (u : Vec3) : sub u u = zero := by ext <;> simp
@[simp] theorem scale_zero (a : ℝ) : scale a zero = zero := by ext <;> simp
@[simp] theorem zero_scale (u : Vec3) : scale 0 u = zero := by ext <;> simp
@[simp] theorem one_scale (u : Vec3) : scale 1 u = u := by ext <;> simp

/-- Dot-product linearity in the second argument. -/
theorem dot_add (u w q : Vec3) : dot u (add w q) = dot u w + dot u q := by
  simp [dot, add]
  ring

/-- Dot product of a scaled vector. -/
theorem dot_scale (u w : Vec3) (a : ℝ) : dot u (scale a w) = a * dot u w := by
  simp [dot, scale]
  ring

/-- Symmetry of the dot product. -/
theorem dot_comm (u w : Vec3) : dot u w = dot w u := by
  simp [dot]
  ring

/-- Squared norm is the coordinate square sum. -/
theorem normSq_eq (u : Vec3) : normSq u = u.x^2 + u.y^2 + u.z^2 := by
  simp [normSq, dot]
  ring

/-- Squared norm is nonnegative. -/
theorem normSq_nonneg (u : Vec3) : 0 ≤ normSq u := by
  rw [normSq_eq]
  positivity

@[simp] theorem dot_zero_left (u : Vec3) : dot zero u = 0 := by
  simp [dot, zero]

@[simp] theorem dot_zero_right (u : Vec3) : dot u zero = 0 := by
  simp [dot, zero]

@[simp] theorem normSq_zero : normSq zero = 0 := by
  simp [normSq]

/-- Vanishing squared norm forces every coordinate to vanish. -/
theorem eq_zero_of_normSq_eq_zero {u : Vec3} (h : normSq u = 0) : u = zero := by
  rw [normSq_eq] at h
  have hx : u.x = 0 := by
    nlinarith [sq_nonneg u.x, sq_nonneg u.y, sq_nonneg u.z]
  have hy : u.y = 0 := by
    nlinarith [sq_nonneg u.x, sq_nonneg u.y, sq_nonneg u.z]
  have hz : u.z = 0 := by
    nlinarith [sq_nonneg u.x, sq_nonneg u.y, sq_nonneg u.z]
  exact Vec3.ext (by simpa [zero] using hx) (by simpa [zero] using hy)
    (by simpa [zero] using hz)

/-- Three-dimensional Lagrange identity. -/
theorem lagrange_identity (u w : Vec3) :
    normSq u * normSq w - dot u w ^ 2 =
      (u.x*w.y-u.y*w.x)^2 + (u.x*w.z-u.z*w.x)^2 +
        (u.y*w.z-u.z*w.y)^2 := by
  simp [normSq, dot]
  ring

/-- Coordinate Cauchy--Schwarz inequality. -/
theorem dot_sq_le_normSq_mul_normSq (u w : Vec3) :
    dot u w ^ 2 ≤ normSq u * normSq w := by
  rw [← sub_nonneg]
  rw [lagrange_identity]
  positivity

/-- The vector energy obeys the continuum mass shell. -/
theorem energyVec_sq (m : ℝ) (k : Vec3) :
    energyVec m k ^ 2 = m^2 + normSq k := by
  rw [energyVec, energy3_sq, normSq_eq]
  ring

/-- Vector energy is nonnegative. -/
theorem energyVec_nonneg (m : ℝ) (k : Vec3) : 0 ≤ energyVec m k := by
  exact energy3_nonneg _ _ _ _

/-- Subluminal Lorentz factor. -/
def gamma (v : Vec3) : ℝ := (Real.sqrt (1 - normSq v))⁻¹

/-- The radicand defining `γ` is positive for a subluminal velocity. -/
theorem one_sub_normSq_pos {v : Vec3} (hv : normSq v < 1) :
    0 < 1 - normSq v := by linarith

/-- A subluminal Lorentz factor is positive. -/
theorem gamma_pos {v : Vec3} (hv : normSq v < 1) : 0 < gamma v := by
  rw [gamma]
  exact inv_pos.mpr (Real.sqrt_pos.2 (one_sub_normSq_pos hv))

/-- A subluminal Lorentz factor is nonzero. -/
theorem gamma_ne_zero {v : Vec3} (hv : normSq v < 1) : gamma v ≠ 0 :=
  ne_of_gt (gamma_pos hv)

/-- `γ+1` is nonzero on the subluminal region. -/
theorem gamma_add_one_ne_zero {v : Vec3} (hv : normSq v < 1) :
    gamma v + 1 ≠ 0 := by
  have hg := gamma_pos hv
  linarith

/-- Exact identity `γ²(1-|v|²)=1`. -/
theorem gamma_sq_mul_one_sub {v : Vec3} (hv : normSq v < 1) :
    gamma v ^ 2 * (1 - normSq v) = 1 := by
  have hp : 0 < 1 - normSq v := one_sub_normSq_pos hv
  have hrp : 0 < Real.sqrt (1 - normSq v) := Real.sqrt_pos.2 hp
  have hrne : Real.sqrt (1 - normSq v) ≠ 0 := ne_of_gt hrp
  have hrsq : Real.sqrt (1 - normSq v) ^ 2 = 1 - normSq v := by
    rw [Real.sq_sqrt hp.le]
  rw [gamma]
  field_simp [hrne]
  exact hrsq.symm

/-- Regularized longitudinal boost coefficient `γ²/(γ+1)`. -/
def boostAlpha (v : Vec3) : ℝ := gamma v ^ 2 / (gamma v + 1)

/-- Away from zero speed, the regularized coefficient equals `(γ-1)/|v|²`. -/
theorem boostAlpha_eq_source {v : Vec3} (hv : normSq v < 1)
    (hvn : normSq v ≠ 0) :
    boostAlpha v = (gamma v - 1) / normSq v := by
  have hg1 := gamma_add_one_ne_zero hv
  have hrel := gamma_sq_mul_one_sub hv
  rw [boostAlpha]
  field_simp [hvn, hg1]
  nlinarith

/-- Scalar coefficient in the spatial boost. -/
def boostCoeff (v k : Vec3) (E : ℝ) : ℝ :=
  boostAlpha v * dot v k - gamma v * E

/-- Continuum boosted energy. -/
def boostEnergy (v k : Vec3) (E : ℝ) : ℝ := gamma v * (E - dot v k)

/-- Continuum boosted momentum, in a form regular at `v=0`. -/
def boostMomentum (v k : Vec3) (E : ℝ) : Vec3 :=
  add k (scale (boostCoeff v k E) v)

/-- Dot product of the velocity with the boosted momentum. -/
theorem dot_boostMomentum (v k : Vec3) (E : ℝ) :
    dot v (boostMomentum v k E) =
      dot v k + boostCoeff v k E * normSq v := by
  simp [boostMomentum, dot_add, dot_scale, normSq]

/-- Exact squared norm of the boosted momentum. -/
theorem normSq_boostMomentum (v k : Vec3) (E : ℝ) :
    normSq (boostMomentum v k E) =
      normSq k + 2 * boostCoeff v k E * dot v k +
        boostCoeff v k E ^ 2 * normSq v := by
  simp [boostMomentum, normSq_eq, add, scale, dot]
  ring

/-- Zero velocity has unit Lorentz factor. -/
@[simp] theorem gamma_zero : gamma zero = 1 := by
  norm_num [gamma, normSq, dot, zero]

/-- Zero velocity leaves energy unchanged. -/
@[simp] theorem boostEnergy_zero (k : Vec3) (E : ℝ) :
    boostEnergy zero k E = E := by
  rw [boostEnergy, gamma_zero]
  simp

/-- Zero velocity leaves momentum unchanged. -/
@[simp] theorem boostMomentum_zero (k : Vec3) (E : ℝ) :
    boostMomentum zero k E = k := by
  rw [boostMomentum]
  simp

/-- The regularized coefficient satisfies `α |v|² = γ - 1`. -/
theorem boostAlpha_mul_normSq {v : Vec3} (hv : normSq v < 1) :
    boostAlpha v * normSq v = gamma v - 1 := by
  have hg1 := gamma_add_one_ne_zero hv
  have hrel := gamma_sq_mul_one_sub hv
  rw [boostAlpha]
  field_simp [hg1]
  nlinarith

/-- The second coefficient identity needed by the exact norm calculation. -/
theorem two_boostAlpha_add_sq_mul_normSq {v : Vec3} (hv : normSq v < 1) :
    2 * boostAlpha v + boostAlpha v ^ 2 * normSq v = gamma v ^ 2 := by
  have ha := boostAlpha_mul_normSq hv
  have hg1 := gamma_add_one_ne_zero hv
  calc
    2 * boostAlpha v + boostAlpha v ^ 2 * normSq v =
        boostAlpha v * (2 + boostAlpha v * normSq v) := by ring
    _ = boostAlpha v * (gamma v + 1) := by rw [ha]; ring
    _ = gamma v ^ 2 := by
      rw [boostAlpha]
      field_simp [hg1]

/-- A useful nonsingular rewriting of the boost coefficient times `|v|²`. -/
theorem boostCoeff_mul_normSq {v : Vec3} (hv : normSq v < 1)
    (k : Vec3) (E : ℝ) :
    boostCoeff v k E * normSq v =
      (gamma v - 1) * dot v k - gamma v * E * normSq v := by
  rw [boostCoeff]
  have ha := boostAlpha_mul_normSq hv
  calc
    (boostAlpha v * dot v k - gamma v * E) * normSq v =
        (boostAlpha v * normSq v) * dot v k -
          gamma v * E * normSq v := by ring
    _ = (gamma v - 1) * dot v k - gamma v * E * normSq v := by rw [ha]

/-- Exact identity `γ(1-|v|²)=1/γ`. -/
theorem gamma_mul_one_sub {v : Vec3} (hv : normSq v < 1) :
    gamma v * (1 - normSq v) = 1 / gamma v := by
  have hrel := gamma_sq_mul_one_sub hv
  have hg := gamma_ne_zero hv
  field_simp [hg]
  nlinarith

/-- The regularized boost is exactly Minkowski-norm preserving. -/
theorem boost_minkowski_invariant {v : Vec3} (hv : normSq v < 1)
    (k : Vec3) (E : ℝ) :
    boostEnergy v k E ^ 2 - normSq (boostMomentum v k E) =
      E^2 - normSq k := by
  have ha := boostAlpha_mul_normSq hv
  have ha2 := two_boostAlpha_add_sq_mul_normSq hv
  have hrel := gamma_sq_mul_one_sub hv
  have hchange :
      2 * boostCoeff v k E * dot v k +
          boostCoeff v k E ^ 2 * normSq v =
        gamma v ^ 2 * dot v k ^ 2 -
          2 * gamma v ^ 2 * E * dot v k +
          gamma v ^ 2 * normSq v * E ^ 2 := by
    rw [boostCoeff]
    calc
      2 * (boostAlpha v * dot v k - gamma v * E) * dot v k +
          (boostAlpha v * dot v k - gamma v * E) ^ 2 * normSq v =
          (2 * boostAlpha v + boostAlpha v ^ 2 * normSq v) * dot v k ^ 2 -
            2 * gamma v * (1 + boostAlpha v * normSq v) * E * dot v k +
            gamma v ^ 2 * normSq v * E ^ 2 := by ring
      _ = gamma v ^ 2 * dot v k ^ 2 -
            2 * gamma v ^ 2 * E * dot v k +
            gamma v ^ 2 * normSq v * E ^ 2 := by rw [ha2, ha]; ring
  rw [boostEnergy, normSq_boostMomentum]
  calc
    (gamma v * (E - dot v k)) ^ 2 -
        (normSq k + 2 * boostCoeff v k E * dot v k +
          boostCoeff v k E ^ 2 * normSq v) =
        (gamma v * (E - dot v k)) ^ 2 -
          (normSq k +
            (2 * boostCoeff v k E * dot v k +
              boostCoeff v k E ^ 2 * normSq v)) := by ring
    _ = (gamma v * (E - dot v k)) ^ 2 -
          (normSq k +
            (gamma v ^ 2 * dot v k ^ 2 - 2 * gamma v ^ 2 * E * dot v k +
              gamma v ^ 2 * normSq v * E ^ 2)) := by rw [hchange]
    _ = gamma v ^ 2 * (1 - normSq v) * E ^ 2 - normSq k := by ring
    _ = E ^ 2 - normSq k := by rw [hrel]; ring

/-- The inverse-energy identity used by the moving-momentum cancellation. -/
theorem boostEnergy_add_dot_boostMomentum {v : Vec3} (hv : normSq v < 1)
    (k : Vec3) (E : ℝ) :
    boostEnergy v k E + dot v (boostMomentum v k E) = E / gamma v := by
  have hc := boostCoeff_mul_normSq hv k E
  have hg := gamma_mul_one_sub hv
  rw [boostEnergy, dot_boostMomentum, hc]
  calc
    gamma v * (E - dot v k) +
        (dot v k + ((gamma v - 1) * dot v k - gamma v * E * normSq v)) =
      (gamma v * (1 - normSq v)) * E := by ring
    _ = (1 / gamma v) * E := by rw [hg]
    _ = E / gamma v := by ring

/-- A nonzero continuum energy remains strictly positive after a subluminal boost. -/
theorem boostEnergy_pos {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    0 < boostEnergy v k (energyVec m k) := by
  let E := energyVec m k
  let s := normSq v
  let r := normSq k
  let d := dot v k
  have hEp : 0 < E := lt_of_le_of_ne (energyVec_nonneg m k) (Ne.symm hE)
  have hs0 : 0 ≤ s := normSq_nonneg v
  have hr0 : 0 ≤ r := normSq_nonneg k
  have hd2 : d^2 ≤ s*r := by
    simpa [d, s, r] using dot_sq_le_normSq_mul_normSq v k
  have hEsq : E^2 = m^2 + r := by simpa [E, r] using energyVec_sq m k
  have hsr : s*r < E^2 := by
    by_cases hr : r = 0
    · rw [hr]
      nlinarith [sq_pos_of_pos hEp]
    · have hrp : 0 < r := lt_of_le_of_ne hr0 (Ne.symm hr)
      have hmul : s*r < 1*r := mul_lt_mul_of_pos_right hv hrp
      nlinarith [sq_nonneg m]
  have hdlt : d < E := by
    by_contra hnot
    have hEd : E ≤ d := le_of_not_gt hnot
    nlinarith
  exact mul_pos (gamma_pos hv) (sub_pos.mpr hdlt)

/-- The continuum boosted energy equals the positive mass-shell energy of the boosted momentum. -/
theorem energyVec_boostMomentum {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    energyVec m (boostMomentum v k (energyVec m k)) =
      boostEnergy v k (energyVec m k) := by
  have hinv := boost_minkowski_invariant hv k (energyVec m k)
  have hk := energyVec_sq m k
  have hkp := energyVec_sq m (boostMomentum v k (energyVec m k))
  have hpos := boostEnergy_pos hv hE
  have hnon := energyVec_nonneg m (boostMomentum v k (energyVec m k))
  nlinarith

/-- Source-coordinate expression for the spatial boost away from zero velocity. -/
theorem boostMomentum_eq_source {v : Vec3} (hv : normSq v < 1)
    (hvn : normSq v ≠ 0) (k : Vec3) (E : ℝ) :
    boostMomentum v k E =
      add k (scale (((gamma v - 1) / normSq v) * dot v k - gamma v * E) v) := by
  rw [boostMomentum, boostCoeff, boostAlpha_eq_source hv hvn]

end KomorebiPhysics.Relativistic3DLorentzKinematics
