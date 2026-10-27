module

public import KomorebiPhysics.Relativistic3DDiscreteBoost
public import KomorebiPhysics.Relativistic3DPathInversion

/-!
Uniform shell control along an order-`ε²` moving momentum.  This is the
load-bearing step that cannot be obtained by substituting a moving point into a
fixed-momentum asymptotic theorem.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DMovingShell

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Dispersion3D
open KomorebiPhysics.Relativistic1DContinuumLimit
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic3DLorentzKinematics
open KomorebiPhysics.Relativistic3DDiscreteBoost
open KomorebiPhysics.Relativistic3DPathInversion

/-- Exact shell evaluated along a scalar momentum displacement. -/
def movingShell (m : ℝ) (q v : Vec3) (t : ℝ → ℝ) (ε : ℝ) : ℝ :=
  shell m (q.x + t ε * v.x) (q.y + t ε * v.y) (q.z + t ε * v.z) ε

/-- Fixed shell at the base momentum. -/
def fixedShell (m : ℝ) (q : Vec3) (ε : ℝ) : ℝ :=
  shell m q.x q.y q.z ε

/-- Fourth-order coefficient of the moving shell. -/
def movingShellQuartic (m a : ℝ) (q v : Vec3) : ℝ :=
  shellQuarticCoeffSource3 m q.x q.y q.z - a * dot v q

/-- Linear scaling is `O(ε)`. -/
theorem const_mul_id_isBigO (c : ℝ) :
    (fun ε : ℝ => c * ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
  (isBigO_refl (fun ε : ℝ => ε) (𝓝[>] 0)).const_mul_left c

/-- Linear scaling tends to zero on the positive-side filter. -/
theorem tendsto_const_mul_id (c : ℝ) :
    Tendsto (fun ε : ℝ => c * ε) (𝓝[>] 0) (𝓝 0) := by
  have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
    tendsto_id.mono_left nhdsWithin_le_nhds
  simpa using tendsto_const_nhds.mul hid

/-- A fixed scaled sine differs from its linearization by `O(ε³)`. -/
theorem sin_scaled_sub_linear_isBigO_cube (k : ℝ) :
    (fun ε => Real.sin (k*ε) - k*ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^3) := by
  have hcomp := sin_sub_id_isBigO_cube.comp_tendsto (tendsto_const_mul_id k)
  have hk3 := (const_mul_id_isBigO k).pow 3
  have h := hcomp.trans hk3
  exact h.congr_right (by intro ε; ring)

/-- A fixed scaled cosine differs from one by `O(ε²)`. -/
theorem cos_scaled_sub_one_isBigO_sq (k : ℝ) :
    (fun ε => Real.cos (k*ε) - 1) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hcomp := cos_sub_one_isBigO_sq.comp_tendsto (tendsto_const_mul_id k)
  have hk2 := (const_mul_id_isBigO k).pow 2
  have h := hcomp.trans hk2
  exact h.congr_right (by intro ε; ring)

/-- A fixed scaled sine is `O(ε)`. -/
theorem sin_scaled_isBigO_linear (k : ℝ) :
    (fun ε => Real.sin (k*ε)) =O[𝓝[>] 0] (fun ε : ℝ => ε) := by
  have hres0 := (sin_scaled_sub_linear_isBigO_cube k).trans
    ((isLittleO_pow_pow (by omega : 1 < 3)).isBigO.mono nhdsWithin_le_nhds)
  have hres : (fun ε => Real.sin (k*ε) - k*ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε) := hres0.congr_right (by intro ε; ring)
  exact (hres.add (const_mul_id_isBigO k)).congr_left (by intro ε; ring)

/-- A fixed scaled cosine is bounded near zero. -/
theorem cos_scaled_isBigO_one (k : ℝ) :
    (fun ε => Real.cos (k*ε)) =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) := by
  have hT : Tendsto (fun ε => Real.cos (k*ε)) (𝓝[>] 0) (𝓝 1) := by
    simpa [Function.comp_def] using Real.continuous_cos.continuousAt.tendsto.comp
      (tendsto_const_mul_id k)
  exact hT.isBigO_one ℝ

/-- Ninth order is dominated by sixth order near positive zero. -/
theorem pow9_isBigO_pow6_positive :
    (fun ε : ℝ => ε^9) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
  (isLittleO_pow_pow (by omega : 6 < 9)).isBigO.mono nhdsWithin_le_nhds

/-- Tenth order is dominated by sixth order near positive zero. -/
theorem pow10_isBigO_pow6_positive :
    (fun ε : ℝ => ε^10) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
  (isLittleO_pow_pow (by omega : 6 < 10)).isBigO.mono nhdsWithin_le_nhds

/-- Sixth order is dominated by fourth order near positive zero. -/
theorem pow6_isBigO_pow4_positive :
    (fun ε : ℝ => ε^6) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) :=
  (isLittleO_pow_pow (by omega : 4 < 6)).isBigO.mono nhdsWithin_le_nhds

/-- A moving cosine acquires the exact quartic transport term. -/
theorem movingCos_expansion_isBigO
    {t : ℝ → ℝ} {a k w : ℝ}
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => Real.cos ((k + t ε*w)*ε) - Real.cos (k*ε) +
      a*w*k*ε^4) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  let δ : ℝ → ℝ := fun ε => t ε * w * ε
  have ht2 : t =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := path_isBigO_sq ht
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    isBigO_refl _ _
  have hδ : δ =O[𝓝[>] 0] (fun ε : ℝ => ε^3) := by
    have h := (ht2.mul he).const_mul_left w
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by
        dsimp [δ]
        ring)) (Filter.Eventually.of_forall (fun ε => by ring))
  have hδres :
      (fun ε => δ ε - a*w*ε^3) =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
    have h := (ht.mul he).const_mul_left w
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by
        dsimp [δ]
        ring)) (Filter.Eventually.of_forall (fun ε => by ring))
  have hδT : Tendsto δ (𝓝[>] 0) (𝓝 0) :=
    hδ.trans_tendsto (by
      have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
        tendsto_id.mono_left nhdsWithin_le_nhds
      simpa using hid.pow 3)
  have hcosδ :
      (fun ε => Real.cos (δ ε) - 1) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
    have hc := cos_sub_one_isBigO_sq.comp_tendsto hδT
    have h := hc.trans (hδ.pow 2)
    exact h.congr_right (by intro ε; ring)
  have hsinδres9 :
      (fun ε => Real.sin (δ ε) - δ ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^9) := by
    have hs := sin_sub_id_isBigO_cube.comp_tendsto hδT
    have h := hs.trans (hδ.pow 3)
    exact h.congr_right (by intro ε; ring)
  have hsinδ :
      (fun ε => Real.sin (δ ε)) =O[𝓝[>] 0] (fun ε : ℝ => ε^3) := by
    have hres := hsinδres9.trans
      ((isLittleO_pow_pow (by omega : 3 < 9)).isBigO.mono nhdsWithin_le_nhds)
    exact (hres.add hδ).congr_left (by intro ε; ring)
  have hcosx := cos_scaled_isBigO_one k
  have hsinxres := sin_scaled_sub_linear_isBigO_cube k
  have hx := const_mul_id_isBigO k
  have h1 :
      (fun ε => Real.cos (k*ε) * (Real.cos (δ ε)-1)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    exact (hcosx.mul hcosδ).congr_right (by intro ε; ring)
  have h2 :
      (fun ε => -(Real.sin (k*ε)-k*ε) * Real.sin (δ ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have h := (hsinxres.mul hsinδ).const_mul_left (-1 : ℝ)
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have h3 :
      (fun ε => -(k*ε) * (Real.sin (δ ε)-δ ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have h10 := (hx.mul hsinδres9).const_mul_left (-1 : ℝ)
    have h10' :
        (fun ε => -(k*ε) * (Real.sin (δ ε)-δ ε)) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^10) := by
      exact h10.congr' (Filter.Eventually.of_forall (fun ε => by ring))
        (Filter.Eventually.of_forall (fun ε => by ring))
    exact h10'.trans pow10_isBigO_pow6_positive
  have h4 :
      (fun ε => -(k*ε) * (δ ε-a*w*ε^3)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have h := (hx.mul hδres).const_mul_left (-1 : ℝ)
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have hsum := ((h1.add h2).add h3).add h4
  exact hsum.congr_left (by
    intro ε
    have harg : (k + t ε*w)*ε = k*ε + δ ε := by
      dsimp [δ]
      ring
    rw [harg, Real.cos_add]
    dsimp [δ]
    ring)

/-- The moving cosine itself differs from one by `O(ε²)`. -/
theorem movingCos_sub_one_isBigO_sq
    {t : ℝ → ℝ} {a k w : ℝ}
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => Real.cos ((k+t ε*w)*ε) - 1) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hmove6 := movingCos_expansion_isBigO (t := t) (a := a) (k := k) (w := w) ht
  have hmove2 := hmove6.trans
    ((isLittleO_pow_pow (by omega : 2 < 6)).isBigO.mono nhdsWithin_le_nhds)
  have hp42 : (fun ε : ℝ => ε^4) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    (isLittleO_pow_pow (by omega : 2 < 4)).isBigO.mono nhdsWithin_le_nhds
  have hquartic2 := hp42.const_mul_left (-a*w*k)
  have hfixed := cos_scaled_sub_one_isBigO_sq k
  exact ((hmove2.add hquartic2).add hfixed).congr_left (by intro ε; ring)

/-- A moving cosine is bounded near zero. -/
theorem movingCos_isBigO_one
    {t : ℝ → ℝ} {a k w : ℝ}
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => Real.cos ((k+t ε*w)*ε)) =O[𝓝[>] 0]
      (fun _ : ℝ => (1 : ℝ)) := by
  have h2 := movingCos_sub_one_isBigO_sq (t := t) (a := a) (k := k) (w := w) ht
  have hto1 : (fun ε : ℝ => ε^2) =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) := by
    have hT : Tendsto (fun ε : ℝ => ε^2) (𝓝[>] 0) (𝓝 0) := by
      have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
        tendsto_id.mono_left nhdsWithin_le_nhds
      simpa using hid.pow 2
    exact hT.isBigO_one ℝ
  have hres := h2.trans hto1
  have hone : (fun _ : ℝ => (1 : ℝ)) =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) :=
    isBigO_refl _ _
  exact (hres.add hone).congr_left (by intro ε; ring)

/-- The moving spatial cosine product has the transported quartic coefficient. -/
theorem movingSpatialProduct_expansion_isBigO
    {t : ℝ → ℝ} {a : ℝ} (q v : Vec3)
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε =>
      Real.cos ((q.x+t ε*v.x)*ε) * Real.cos ((q.y+t ε*v.y)*ε) *
          Real.cos ((q.z+t ε*v.z)*ε) -
        Real.cos (q.x*ε) * Real.cos (q.y*ε) * Real.cos (q.z*ε) +
        a * dot v q * ε^4) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  let X : ℝ → ℝ := fun ε => Real.cos (q.x*ε)
  let Y : ℝ → ℝ := fun ε => Real.cos (q.y*ε)
  let Z : ℝ → ℝ := fun ε => Real.cos (q.z*ε)
  let Xp : ℝ → ℝ := fun ε => Real.cos ((q.x+t ε*v.x)*ε)
  let Yp : ℝ → ℝ := fun ε => Real.cos ((q.y+t ε*v.y)*ε)
  let Zp : ℝ → ℝ := fun ε => Real.cos ((q.z+t ε*v.z)*ε)
  let cx := a*v.x*q.x
  let cy := a*v.y*q.y
  let cz := a*v.z*q.z
  have hx6 : (fun ε => Xp ε - X ε + cx*ε^4) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    simpa [Xp, X, cx, mul_assoc] using
      movingCos_expansion_isBigO (t := t) (a := a) (k := q.x) (w := v.x) ht
  have hy6 : (fun ε => Yp ε - Y ε + cy*ε^4) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    simpa [Yp, Y, cy, mul_assoc] using
      movingCos_expansion_isBigO (t := t) (a := a) (k := q.y) (w := v.y) ht
  have hz6 : (fun ε => Zp ε - Z ε + cz*ε^4) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    simpa [Zp, Z, cz, mul_assoc] using
      movingCos_expansion_isBigO (t := t) (a := a) (k := q.z) (w := v.z) ht
  have hx4 : (fun ε => Xp ε-X ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have hr := hx6.trans pow6_isBigO_pow4_positive
    have hp := (isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left (-cx)
    exact (hr.add hp).congr_left (by intro ε; ring)
  have hy4 : (fun ε => Yp ε-Y ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have hr := hy6.trans pow6_isBigO_pow4_positive
    have hp := (isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left (-cy)
    exact (hr.add hp).congr_left (by intro ε; ring)
  have hz4 : (fun ε => Zp ε-Z ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have hr := hz6.trans pow6_isBigO_pow4_positive
    have hp := (isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left (-cz)
    exact (hr.add hp).congr_left (by intro ε; ring)
  have hXp1 : (fun ε => Xp ε-1) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [Xp] using movingCos_sub_one_isBigO_sq
      (t := t) (a := a) (k := q.x) (w := v.x) ht
  have hYp1 : (fun ε => Yp ε-1) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [Yp] using movingCos_sub_one_isBigO_sq
      (t := t) (a := a) (k := q.y) (w := v.y) ht
  have hZp1 : (fun ε => Zp ε-1) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [Zp] using movingCos_sub_one_isBigO_sq
      (t := t) (a := a) (k := q.z) (w := v.z) ht
  have hXp := movingCos_isBigO_one (t := t) (a := a) (k := q.x) (w := v.x) ht
  have hYp := movingCos_isBigO_one (t := t) (a := a) (k := q.y) (w := v.y) ht
  have hZp := movingCos_isBigO_one (t := t) (a := a) (k := q.z) (w := v.z) ht
  have hX := cos_scaled_isBigO_one q.x
  have hY := cos_scaled_isBigO_one q.y
  have hZ := cos_scaled_isBigO_one q.z
  have hYpZp1 : (fun ε => Yp ε*Zp ε-1) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
    have hpart := hYp1.mul hZp
    have hpart2 : (fun ε => (Yp ε-1)*Zp ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := hpart.congr_right (by intro ε; simp)
    exact (hpart2.add hZp1).congr_left (by intro ε; ring)
  have hZp1' := hZp1
  have hleadX :
      (fun ε => (Xp ε-X ε)*Yp ε*Zp ε + cx*ε^4) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have hmain := (hx6.mul hYp).mul hZp
    have hmain6 :
        (fun ε => (Xp ε-X ε+cx*ε^4)*Yp ε*Zp ε) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^6) := by
      exact hmain.congr_right (by intro ε; simp)
    have hcross0 := ((isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left cx).mul hYpZp1
    have hcross : (fun ε => cx*ε^4*(1-Yp ε*Zp ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
      have h := hcross0.const_mul_left (-1 : ℝ)
      exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
        (Filter.Eventually.of_forall (fun ε => by ring))
    exact (hmain6.add hcross).congr_left (by intro ε; ring)
  have hleadY :
      (fun ε => X ε*(Yp ε-Y ε)*Zp ε + cy*ε^4) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have hmain := (hX.mul hy6).mul hZp
    have hmain6 :
        (fun ε => X ε*(Yp ε-Y ε+cy*ε^4)*Zp ε) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^6) := by
      exact hmain.congr_right (by intro ε; simp)
    have hXZp1 : (fun ε => X ε*Zp ε-1) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
      have hX1 := cos_scaled_sub_one_isBigO_sq q.x
      have hpart := hX1.mul hZp
      have hpart2 : (fun ε => (X ε-1)*Zp ε) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^2) := by
        simpa [X] using hpart.congr_right (by intro ε; simp)
      exact (hpart2.add hZp1').congr_left (by intro ε; ring)
    have hcross0 := ((isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left cy).mul hXZp1
    have hcross : (fun ε => cy*ε^4*(1-X ε*Zp ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
      have h := hcross0.const_mul_left (-1 : ℝ)
      exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
        (Filter.Eventually.of_forall (fun ε => by ring))
    exact (hmain6.add hcross).congr_left (by intro ε; ring)
  have hleadZ :
      (fun ε => X ε*Y ε*(Zp ε-Z ε) + cz*ε^4) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    have hmain := (hX.mul hY).mul hz6
    have hmain6 :
        (fun ε => X ε*Y ε*(Zp ε-Z ε+cz*ε^4)) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^6) := by
      exact hmain.congr_right (by intro ε; simp)
    have hXY1 : (fun ε => X ε*Y ε-1) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
      have hX1 := cos_scaled_sub_one_isBigO_sq q.x
      have hY1 := cos_scaled_sub_one_isBigO_sq q.y
      have hpart := hX1.mul hY
      have hpart2 : (fun ε => (X ε-1)*Y ε) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^2) := by
        simpa [X, Y] using hpart.congr_right (by intro ε; simp)
      exact (hpart2.add hY1).congr_left (by intro ε; ring)
    have hcross0 := ((isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left cz).mul hXY1
    have hcross : (fun ε => cz*ε^4*(1-X ε*Y ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
      have h := hcross0.const_mul_left (-1 : ℝ)
      exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
        (Filter.Eventually.of_forall (fun ε => by ring))
    exact (hmain6.add hcross).congr_left (by intro ε; ring)
  have hsum := (hleadX.add hleadY).add hleadZ
  exact hsum.congr_left (by
    intro ε
    dsimp [X, Y, Z, Xp, Yp, Zp, cx, cy, cz]
    simp only [dot]
    ring)

/-- The full moving shell changes the quartic coefficient by `-a v·q`. -/
theorem movingShell_expansion_isBigO
    {t : ℝ → ℝ} {a m : ℝ} (q v : Vec3)
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => movingShell m q v t ε -
      pathShellPoly4 (energyVec m q) (movingShellQuartic m a q v) ε)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  let M : ℝ → ℝ := fun ε => Real.cos (m*ε)
  let P : ℝ → ℝ := fun ε =>
    Real.cos ((q.x+t ε*v.x)*ε) * Real.cos ((q.y+t ε*v.y)*ε) *
      Real.cos ((q.z+t ε*v.z)*ε)
  let P0 : ℝ → ℝ := fun ε =>
    Real.cos (q.x*ε) * Real.cos (q.y*ε) * Real.cos (q.z*ε)
  let c := a * dot v q
  have hP : (fun ε => P ε-P0 ε+c*ε^4) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    simpa [P, P0, c] using movingSpatialProduct_expansion_isBigO q v ht
  have hM := cos_scaled_isBigO_one m
  have hM1 := cos_scaled_sub_one_isBigO_sq m
  have hmain := hM.mul hP
  have hmain6 : (fun ε => M ε*(P ε-P0 ε+c*ε^4)) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    simpa [M] using hmain.congr_right (by intro ε; simp)
  have hcross0 := ((isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left c).mul hM1
  have hcross : (fun ε => c*ε^4*(1-M ε)) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    have h := hcross0.const_mul_left (-1 : ℝ)
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have hdiff : (fun ε => movingShell m q v t ε-fixedShell m q ε+c*ε^4)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
    exact (hmain6.add hcross).congr_left (by
      intro ε
      dsimp [movingShell, fixedShell, shell, M, P, P0, c]
      ring)
  have hfixed :
      (fun ε => fixedShell m q ε -
        pathShellPoly4 (energyVec m q)
          (shellQuarticCoeffSource3 m q.x q.y q.z) ε)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
    simpa [fixedShell, energyVec, pathShellPoly4, shellPoly4_3] using
      (shell3_expansion_isBigO m q.x q.y q.z).mono nhdsWithin_le_nhds
  exact (hdiff.add hfixed).congr_left (by
    intro ε
    simp only [movingShellQuartic, pathShellPoly4]
    dsimp [c]
    ring)

end KomorebiPhysics.Relativistic3DMovingShell
